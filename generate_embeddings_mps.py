# generate_embeddings_mps.py
import os
import numpy as np
import pickle
from tqdm import tqdm
from PIL import Image

import torch
from transformers import CLIPModel, CLIPProcessor

# --- Configuration ---
IMAGE_FOLDER = './mal_character_images'
EMBEDDINGS_FILE = 'anime_embeddings.npy'
FILENAMES_FILE = 'anime_filenames.pkl'

# A general-purpose CLIP model that works for diverse images (real + anime)
MODEL_NAME = 'openai/clip-vit-base-patch32'

# --- Device setup ---
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# --- Model setup ---
def setup_model():
    print(f"Loading CLIP model '{MODEL_NAME}'...")
    model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    return model, processor

def get_clip_embedding(img_path, model, processor):
    image = Image.open(img_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        embedding = model.get_image_features(**inputs)
    return embedding.cpu().numpy()[0]

# --- Main script ---
def generate_anime_embeddings():
    model, processor = setup_model()

    if not os.path.isdir(IMAGE_FOLDER):
        print(f"Error: Folder '{IMAGE_FOLDER}' not found.")
        return

    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        print(f"Error: No images found in '{IMAGE_FOLDER}'.")
        return

    print(f"Found {len(image_files)} images. Starting embedding generation...")

    all_embeddings = []
    all_filenames = []

    for filename in tqdm(image_files, desc="⚙️ Processing faces"):
        img_path = os.path.join(IMAGE_FOLDER, filename)
        try:
            embedding = get_clip_embedding(img_path, model, processor)
            all_embeddings.append(embedding)
            all_filenames.append(filename)
        except Exception as e:
            print(f"Warning: Skipping '{filename}' due to error: {e}")

    all_embeddings_np = np.array(all_embeddings, dtype=np.float32)
    np.save(EMBEDDINGS_FILE, all_embeddings_np)

    with open(FILENAMES_FILE, 'wb') as f:
        pickle.dump(all_filenames, f)

    print("\n✅ Process complete!")
    print(f"Embeddings saved to '{EMBEDDINGS_FILE}'")
    print(f"Filenames saved to '{FILENAMES_FILE}'")

if __name__ == "__main__":
    generate_anime_embeddings()
