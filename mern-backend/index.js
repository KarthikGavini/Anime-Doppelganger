import express from 'express';
import cors from 'cors';
import multer from 'multer';
import fs from 'fs';
import { Blob } from 'buffer';
import { Client } from '@gradio/client';

// --- 1. INITIALIZE APP & MIDDLEWARE ---
const app = express();
// app.use(cors()); // Enable CORS
app.use(cors({
  origin: "https://anime-doppelganger.vercel.app"
}));

app.use(express.static('public')); // Serve static files from 'public'

// Set up Multer for in-memory file storage
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// --- 2. DEFINE THE API ENDPOINT ---
app.post('/api/find', upload.single('image'), async (req, res) => {
  console.log("Received a request to /api/find");

  if (!req.file) {
    return res.status(400).json({ error: "No image file uploaded." });
  }

  try {
    // Wrap the uploaded buffer in a Blob
    const exampleImage = new Blob([req.file.buffer]);

    // Connect to Hugging Face Space
    const client = await Client.connect("KarthikGavini/anime-doppelganger");

    // Call the /find_lookalike function
    const result = await client.predict("/find_lookalike", {
      user_image_pil: exampleImage
    });

    console.log("Received response from Hugging Face Space.");

    // Return the result to Postman / frontend
    res.json({
      message: result.data[0],       // Text result
      image_url: result.data[1]?.url // Anime twin image URL
    });

  } catch (error) {
    console.error("Error calling Hugging Face API:", error);
    res.status(500).json({ error: "Failed to process the image with Hugging Face." });
  }
});

// --- 3. START THE SERVER ---
const PORT = 5001;
app.listen(PORT, () => {
  console.log(`Node.js server is running on http://localhost:${PORT}`);
});

