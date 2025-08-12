# crop_faces.py
import cv2
import os
from PIL import Image

# --- SETUP ---
# Point this to the folder with your downloaded full-size character images
SOURCE_FOLDER = "mal_character_images"

# A new folder where the cropped faces will be saved
CROPPED_FOLDER = "mal_character_faces_cropped"

# The pre-trained model for detecting anime faces
# Make sure you download this file and place it in the same directory as your script.
# Download Link: https://github.com/nagadomi/lbpcascade_animeface/raw/master/lbpcascade_animeface.xml
CASCADE_FILE = "lbpcascade_animeface.xml"

# --- SCRIPT ---

# Check if the cascade file exists
if not os.path.exists(CASCADE_FILE):
    print(f"Error: Cascade file not found! Please download '{CASCADE_FILE}' and place it in the same folder as this script.")
    exit()

# Load the face detection model
face_cascade = cv2.CascadeClassifier(CASCADE_FILE)

# Create the output directory if it doesn't exist
if not os.path.exists(CROPPED_FOLDER):
    os.makedirs(CROPPED_FOLDER)

print(f"Starting face detection and cropping for images in '{SOURCE_FOLDER}'...")
print(f"Cropped faces will be saved in '{CROPPED_FOLDER}'.")

# Get a list of all images in the source folder
image_files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

for filename in image_files:
    source_path = os.path.join(SOURCE_FOLDER, filename)
    
    try:
        # Read the image using OpenCV
        image = cv2.imread(source_path)
        if image is None:
            print(f"  - Could not read image: {filename}. Skipping.")
            continue
            
        # Convert the image to grayscale (face detection works better on grayscale)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray,
                                              # detector options
                                              scaleFactor=1.1,
                                              minNeighbors=5,
                                              minSize=(48, 48))
        
        if len(faces) == 0:
            print(f"  - No face found in {filename}. Skipping.")
            continue

        # Assume the largest detected face is the main one
        (x, y, w, h) = faces[0]

        # Add some padding around the face crop for better results
        padding = int(w * 0.2)
        x_pad = max(0, x - padding)
        y_pad = max(0, y - padding)
        w_pad = w + (padding * 2)
        h_pad = h + (padding * 2)

        # Crop the image to the face area with padding
        face_crop = image[y_pad:y_pad + h_pad, x_pad:x_pad + w_pad]
        
        if face_crop.size == 0:
            print(f"  - Created an empty crop for {filename}. Skipping.")
            continue
            
        # Save the new cropped image
        destination_path = os.path.join(CROPPED_FOLDER, filename)
        cv2.imwrite(destination_path, face_crop)
        print(f"  ✔ Cropped and saved: {filename}")

    except Exception as e:
        print(f"  - Error processing {filename}: {e}")

print("\nProcessing complete!")