# model/app.py
import os
import time
import urllib.parse
import numpy as np
import pickle
from PIL import Image

import gradio as gr
import tensorflow as tf
from transformers import TFCLIPModel, CLIPProcessor
from sklearn.preprocessing import normalize

# ----------------- Config -----------------
GITHUB_USER = "KarthikGavini"
GITHUB_REPO = "anime-doppelganger-assets"      # GitHub Pages repo
ASSET_SUBDIR = "mal_character_images"          # folder in that repo
NOCACHE = lambda: int(time.time() * 1000)      # ms (like JS Date.now())

# ----------------- TF setup (optional niceties) -----------------
# Prefer GPU if available; otherwise CPU
DEVICE = "/GPU:0" if tf.config.list_physical_devices("GPU") else "/CPU:0"
# Optional: avoid grabbing all GPU memory up front
for gpu in tf.config.list_physical_devices("GPU"):
    try:
        tf.config.experimental.set_memory_growth(gpu, True)
    except Exception:
        pass

# ----------------- Load model & data once -----------------
print("Loading CLIP model and data...")
model = TFCLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Always resolve paths relative to this file
BASE_DIR = os.path.dirname(__file__)
emb_path = os.path.join(BASE_DIR, "anime_embeddings.npy")
names_path = os.path.join(BASE_DIR, "anime_filenames.pkl")

anime_embeddings = np.load(emb_path)
anime_embeddings = normalize(anime_embeddings, axis=1, norm="l2")

with open(names_path, "rb") as f:
    anime_filenames = pickle.load(f)

print(f"Model and data loaded successfully! ({len(anime_filenames)} entries)")

# ----------------- Core logic -----------------
def encode_filename(name: str) -> str:
    """URL-encode filename safely (like encodeURIComponent)."""
    return urllib.parse.quote(name, safe="")  # encode everything that needs it

def make_github_pages_url(filename: str) -> str:
    encoded = encode_filename(filename)
    return (
        f"https://{GITHUB_USER}.github.io/{GITHUB_REPO}/"
        f"{ASSET_SUBDIR}/{encoded}?nocache={NOCACHE()}"
    )

def get_clip_embedding(pil_img: Image.Image) -> np.ndarray:
    with tf.device(DEVICE):
        inputs = processor(images=pil_img, return_tensors="tf")
        feats = model.get_image_features(pixel_values=inputs["pixel_values"])
    return feats.numpy()

def find_lookalike(user_image_pil: Image.Image):
    # Guard: no image provided
    if user_image_pil is None:
        return "Please upload an image.", None

    # Ensure RGB (some uploads can be RGBA/L/P etc.)
    if user_image_pil.mode != "RGB":
        user_image_pil = user_image_pil.convert("RGB")

    # Embed, normalize, and score
    user_embedding = get_clip_embedding(user_image_pil)
    user_embedding = normalize(user_embedding, axis=1, norm="l2")
    scores = np.dot(anime_embeddings, user_embedding.T).flatten()

    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])
    best_name = anime_filenames[best_idx]

    image_url = make_github_pages_url(best_name)
    result_text = f"Match: {best_name}\nScore: {best_score * 100:.2f}%"

    return result_text, image_url

# ----------------- Gradio UI -----------------
with gr.Blocks(css="body { background-color: #1a1a2e; color: #dcdcdc; }") as demo:
    gr.Markdown("# Anime Doppelgänger")
    gr.Markdown("Upload your photo to find your AI-powered anime twin!")

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="Upload Your Image", height=360)
            submit_button = gr.Button("Find My Twin", variant="primary")
        with gr.Column():
            output_text = gr.Textbox(label="Result", lines=3)
            # gr.Image can accept a URL string; Gradio will fetch and display it.
            output_image = gr.Image(label="Your Anime Twin", height=360)

    submit_button.click(
        fn=find_lookalike,
        inputs=input_image,
        outputs=[output_text, output_image],
        api_name="find_lookalike",
    )

if __name__ == "__main__":
    # For local testing; on Spaces just running the file is enough
    demo.launch()
