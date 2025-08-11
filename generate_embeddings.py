# generate_embeddings_tf.py (Final version with corrected keyword argument)

import os
import numpy as np
import pickle
from tqdm import tqdm

import tensorflow as tf
from transformers import TFCLIPModel, CLIPProcessor
from PIL import Image

# --- Configuration ---
IMAGE_FOLDER = './data'
EMBEDDINGS_FILE = 'anime_embeddings.npy'
FILENAMES_FILE = 'anime_filenames.pkl'
MODEL_NAME = 'openai/clip-vit-base-patch32'

# --- Model Setup ---

def setup_model():
    """Loads the CLIP model and processor using TensorFlow."""
    print("Setting up the CLIP model (TensorFlow)...")
    model = TFCLIPModel.from_pretrained(MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    return model, processor

def get_clip_embedding(img_path, model, processor):
    """Generates a CLIP embedding for a single image using TensorFlow."""
    image = Image.open(img_path).convert("RGB")
    inputs = processor(images=image, return_tensors="tf")

    # Use GPU if available, otherwise CPU. This is the more robust device check.
    device = '/GPU:0' if tf.config.list_physical_devices('GPU') else '/CPU:0'
    
    with tf.device(device):
        # ✅ Correctly using the keyword argument 'pixel_values'
        embedding = model.get_image_features(pixel_values=inputs["pixel_values"])

    return embedding.numpy()[0]

# --- Main Script ---

def generate_anime_embeddings():
    """
    Scans a folder of images, generates CLIP embeddings using TensorFlow,
    and saves the embeddings and corresponding filenames.
    """
    if tf.config.list_physical_devices('GPU'):
        print("GPU detected. Using GPU for processing.")
    else:
        print("No GPU detected. Using CPU.")
        
    model, processor = setup_model()
    
    if not os.path.isdir(IMAGE_FOLDER):
        print(f"\nError: The folder '{IMAGE_FOLDER}' was not found.")
        print("Please update the IMAGE_FOLDER variable in the script.")
        return

    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print(f"\nError: No images found in '{IMAGE_FOLDER}'.")
        return

    print(f"\nFound {len(image_files)} images. Starting embedding generation...")

    all_embeddings = []
    all_filenames = []

    for filename in tqdm(image_files, desc="⚙️  Processing faces"):
        image_path = os.path.join(IMAGE_FOLDER, filename)
        
        try:
            embedding = get_clip_embedding(image_path, model, processor)
            all_embeddings.append(embedding)
            all_filenames.append(filename)
        except Exception as e:
            print(f"\nWarning: Could not process '{filename}'. Skipping. Reason: {e}")
            continue

    all_embeddings_np = np.array(all_embeddings, dtype=np.float32)

    print(f"\nSaving {len(all_embeddings_np)} embeddings to '{EMBEDDINGS_FILE}'...")
    np.save(EMBEDDINGS_FILE, all_embeddings_np)

    print(f"Saving {len(all_filenames)} filenames to '{FILENAMES_FILE}'...")
    with open(FILENAMES_FILE, 'wb') as f:
        pickle.dump(all_filenames, f)

    print("\n✅ Process complete!")
    print(f"Output files created:\n1. {EMBEDDINGS_FILE}\n2. {FILENAMES_FILE}")


if __name__ == "__main__":
    generate_anime_embeddings()