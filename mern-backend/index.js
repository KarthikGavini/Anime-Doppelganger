import express from 'express';
import cors from 'cors';
import multer from 'multer';
import axios from 'axios';
import FormData from 'form-data';

// --- 1. INITIALIZE APP & MIDDLEWARE ---
const app = express();
app.use(cors()); // Enable Cross-Origin Resource Sharing

// ✅ ADD THIS LINE: Serve static files from the 'public' directory
app.use(express.static('public'));

// Set up Multer for in-memory file storage
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

const PYTHON_API_URL = 'http://127.0.0.1:8000/find_lookalike'; // The URL of your running FastAPI service

// --- 2. DEFINE THE API ENDPOINT ---
app.post('/api/find', upload.single('image'), async (req, res) => {
    console.log("Received a request to /api/find");

    if (!req.file) {
        return res.status(400).json({ error: "No image file uploaded." });
    }

    try {
        // --- 3. FORWARD THE IMAGE TO THE PYTHON SERVICE ---
        const formData = new FormData();
        formData.append('file', req.file.buffer, { filename: req.file.originalname });

        console.log("Forwarding request to Python ML service...");
        const response = await axios.post(PYTHON_API_URL, formData, {
            headers: {
                ...formData.getHeaders()
            }
        });
        
        console.log("Received response from Python service.");
        res.json(response.data);

    } catch (error) {
        if (error.response) {
            console.error("Error from Python API:", error.response.status, error.response.data);
        } else if (error.request) {
            console.error("No response received from Python API:", error.request);
        } else {
            console.error("Error setting up request to Python API:", error.message);
        }
        res.status(500).json({ error: "Failed to process the image." });
    }
});

// --- 4. START THE SERVER ---
const PORT = 5001;
app.listen(PORT, () => {
    console.log(`Node.js server is running on http://localhost:${PORT}`);
});