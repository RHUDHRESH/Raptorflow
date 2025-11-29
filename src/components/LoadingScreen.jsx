import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingScreen = () => {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-white">
      <Loader2 className="h-8 w-8 animate-spin text-neutral-900 mb-4" />
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-neutral-400 animate-pulse">
        Loading Experience
      </p>
    </div>
  );
};

export default LoadingScreen;
