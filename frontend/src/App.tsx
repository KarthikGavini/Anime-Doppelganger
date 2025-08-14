// frontend/src/App.tsx
import React, { useState } from 'react';
import axios from 'axios';
import Uploader from './components/Uploader';
import ResultDisplay from './components/ResultDisplay';
import Loader from './components/Loader';

interface ApiResult {
  message: string;     // text result from Hugging Face
  image_url: string;   // URL of generated anime twin image
}


const App: React.FC = () => {
  const [_userImage, setUserImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<ApiResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (file: File) => {
    setUserImage(file);
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result as string);
    reader.readAsDataURL(file);
    handleSubmit(file);
  };

  const handleSubmit = async (file: File) => {
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/find`,
        formData
      );


      setResult(response.data);
    } catch (err) {
      setError("Something went wrong. Please try another image.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTryAgain = () => {
    setUserImage(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  const renderContent = () => {
    if (loading) return <Loader />;
    if (error) return <p className="text-red-400 text-center mt-4 text-xl">{error}</p>;
    if (result && preview) {
      return (
        <ResultDisplay
          userImage={preview}
          // animeFilename={result.lookalike_filename}
          animeImage={result.image_url}
          // score={result.score}
          message={result.message}
          onTryAgain={handleTryAgain}
        />
      );
    }
    return <Uploader onFileSelect={handleFileSelect} />;
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-4">
      <header className="text-center mb-12">
        <h1 className="text-5xl md:text-6xl font-black mb-2 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500">
          Anime Doppelgänger
        </h1>
        <p className="text-lg text-gray-400">
          Uncover Your Anime Alter Ego with AI
        </p>
      </header>

      <main className="w-full">
        {renderContent()}
      </main>

      <footer className="text-center mt-16 text-gray-600">
        <p>An AI Experiment by Karthik Gavini</p>
      </footer>
    </div>
  );
};

export default App;
