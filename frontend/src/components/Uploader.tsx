// frontend/src/components/Uploader.tsx
import React, { useRef, useState } from 'react';
import { useWebcam } from '../hooks/useWebcam';

interface UploaderProps {
  onFileSelect: (file: File) => void;
}

const Uploader: React.FC<UploaderProps> = ({ onFileSelect }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { isWebcamOpen, webcamError, videoRef, openWebcam, closeWebcam, takePicture } = useWebcam();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) onFileSelect(file);
  };

  const handleDragEvents = (e: React.DragEvent<HTMLDivElement>, dragging: boolean) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(dragging);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    handleDragEvents(e, false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      onFileSelect(file);
    }
  };

  const handleTakePicture = async () => {
    const file = await takePicture();
    if (file) {
      onFileSelect(file);
      closeWebcam();
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto">
      {isWebcamOpen ? (
        <div className="flex flex-col items-center animate-pop-in">
          <p className="text-lg text-gray-300 mb-2">Align yourself in the frame</p>
          
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-full rounded-3xl mb-4 border-2 border-cyan-400"
          />

          {webcamError && <p className="text-red-400 mb-2">{webcamError}</p>}

          <div className="flex gap-4">
            <button
              onClick={handleTakePicture}
              className="bg-cyan-500 text-white font-bold py-3 px-8 rounded-xl hover:bg-cyan-600 transition-all text-lg"
            >
              📸 Capture
            </button>
            <button
              onClick={closeWebcam}
              className="bg-gray-700 text-white font-bold py-3 px-8 rounded-xl hover:bg-gray-800 transition-all text-lg"
            >
              ❌ Cancel
            </button>
          </div>
        </div>
      ) : (
        <div
          className={`relative w-full h-64 border-4 border-dashed rounded-3xl flex flex-col justify-center items-center text-center p-4 transition-all duration-300 ${isDragging ? 'border-cyan-400 bg-cyan-400/10' : 'border-gray-600'}`}
          onDragOver={(e) => handleDragEvents(e, true)}
          onDragLeave={(e) => handleDragEvents(e, false)}
          onDrop={handleDrop}
        >
          <p className="text-2xl font-bold text-gray-300">Drag & Drop Your Photo</p>
          <p className="text-gray-500 my-2">or</p>

          <input
            type="file"
            accept="image/png, image/jpeg"
            onChange={handleFileChange}
            className="hidden"
            ref={fileInputRef}
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-gray-700 text-white font-bold py-2 px-6 rounded-xl hover:bg-gray-800 transition-all"
          >
            Select File
          </button>

          <button
            onClick={openWebcam}
            className="mt-4 text-cyan-400 font-semibold hover:text-cyan-300 transition-all"
          >
            Take a Picture
          </button>
        </div>
      )}
    </div>
  );
};

export default Uploader;
