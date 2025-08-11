// frontend/src/components/ResultDisplay.tsx
import React from 'react';

interface ResultDisplayProps {
  userImage: string;
  animeFilename: string;
  score: string;
  onTryAgain: () => void;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ userImage, animeFilename, score, onTryAgain }) => {
  const animeImageUrl = `http://localhost:5001/mal_character_images/${animeFilename}`;
  const displayName = animeFilename.replace(/\.(jpg|jpeg|png)$/i, '');

  return (
    <div className="w-full max-w-5xl mx-auto"> {/* Increased max-width for larger layout */}
      <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16">
        {/* User's Photo Card */}
        <div className="flex flex-col items-center animate-slide-in-left">
          <h2 className="text-3xl font-bold mb-4 text-gray-300">You</h2>
          <img 
            src={userImage} 
            alt="Your submission" 
            // ✅ Bigger size and new shape
            className="w-56 h-56 md:w-80 md:h-80 rounded-3xl object-cover border-4 border-gray-600 shadow-lg" 
          />
        </div>

        {/* VS Separator */}
        <div className="text-6xl font-black text-cyan-400 animate-pop-in" style={{ animationDelay: '200ms' }}>VS</div>

        {/* Anime Twin Card */}
        <div className="flex flex-col items-center animate-slide-in-right" style={{ animationDelay: '400ms' }}>
          <h2 className="text-3xl font-bold mb-4 text-cyan-400">Your Twin</h2>
          <img 
            src={animeImageUrl} 
            alt={displayName} 
            // ✅ Bigger size and new shape
            className="w-56 h-56 md:w-80 md:h-80 rounded-3xl object-cover border-4 border-cyan-400 shadow-lg" 
          />
        </div>
      </div>

      <div className="text-center mt-10 animate-pop-in" style={{ animationDelay: '600ms' }}>
        <p className="text-2xl text-gray-400">Match Score</p>
        <p className="text-6xl font-bold text-white my-2">{score}</p>
        <p className="text-3xl font-semibold text-gray-300">{displayName}</p>
        <div className="mt-8 flex justify-center gap-4">
          <button onClick={onTryAgain} className="bg-cyan-500 text-white font-bold py-3 px-8 rounded-xl hover:bg-cyan-600 transition-all text-lg">Try Again</button>
          {/* <button className="bg-gray-700 text-white font-bold py-3 px-8 rounded-xl hover:bg-gray-800 transition-all text-lg">Share</button> */}
        </div>
      </div>
    </div>
  );
};

export default ResultDisplay;