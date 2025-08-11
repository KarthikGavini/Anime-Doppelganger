# main.py (Final version with score normalization)

import uvicorn
import numpy as np
import pickle
import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# TensorFlow and Transformers imports for our CLIP model
import tensorflow as tf
from transformers import TFCLIPModel, CLIPProcessor

# ✅ NEW IMPORT for normalization
from sklearn.preprocessing import normalize

# --- 1. INITIALIZE THE APP AND THE CLIP MODEL ---
print("Starting server and initializing model...")
app = FastAPI(title="Anime Doppelgänger API")

def setup_model():
    print("Loading CLIP model from Hugging Face...")
    model = TFCLIPModel.from_pretrained('openai/clip-vit-base-patch32')
    processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
    print("Model loaded successfully.")
    return model, processor

def get_clip_embedding(image: Image.Image, model, processor):
    device = '/GPU:0' if tf.config.list_physical_devices('GPU') else '/CPU:0'
    with tf.device(device):
        inputs = processor(images=image, return_tensors="tf")
        embedding = model.get_image_features(pixel_values=inputs["pixel_values"])
    return embedding.numpy()

model, processor = setup_model()

# --- 2. LOAD AND NORMALIZE YOUR PRE-COMPUTED DATABASE ---
print("Loading pre-computed anime face embeddings...")
try:
    anime_embeddings = np.load('anime_embeddings.npy')
    # ✅ NORMALIZE the database embeddings once on startup
    anime_embeddings = normalize(anime_embeddings, axis=1, norm='l2')

    with open('anime_filenames.pkl', 'rb') as f:
        anime_filenames = pickle.load(f)
    print(f"Successfully loaded and normalized {len(anime_filenames)} anime embeddings!")
except FileNotFoundError:
    print("ERROR: Embedding files not found.")
    anime_embeddings, anime_filenames = None, None

# --- 3. CONFIGURE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. DEFINE THE API ENDPOINT ---
@app.post("/find_lookalike")
async def find_lookalike(file: UploadFile = File(...)):
    if anime_embeddings is None:
        raise HTTPException(status_code=500, detail="Server is not ready. Embeddings not loaded.")

    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert('RGB')
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    user_embedding = get_clip_embedding(image, model, processor)
    
    # ✅ NORMALIZE the user's embedding on the fly
    user_embedding = normalize(user_embedding, axis=1, norm='l2')
    
    # Now, the dot product is the true cosine similarity
    scores = np.dot(anime_embeddings, user_embedding.T).flatten()
    
    best_match_index = np.argmax(scores)
    best_match_score = scores[best_match_index]
    best_match_filename = anime_filenames[best_match_index]
    
    return {
        "lookalike_filename": best_match_filename,
        "score": f"{best_match_score * 100:.2f}%",
        "best_match_index": int(best_match_index)
    }

@app.get("/")
def read_root():
    return {"Hello": "This is the Anime Doppelgänger ML Service. Go to /docs to test the API."}