"use client";

import React, { useState } from 'react';
import { useTypingExperience } from './TypingExperienceProvider';
import { EnhancedButton } from './EnhancedButton';

export function TypingExperienceControls() {
  const {
    isSoundEnabled,
    isCursorEnabled,
    setSoundEnabled,
    setCursorEnabled,
    setSoundVolume,
    setCursorSpeed,
  } = useTypingExperience();

  const [volume, setVolume] = useState(30);
  const [speed, setSpeed] = useState(60);

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseInt(e.target.value);
    setVolume(newVolume);
    setSoundVolume(newVolume / 100);
  };

  const handleSpeedChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newSpeed = parseInt(e.target.value);
    setSpeed(newSpeed);
    setCursorSpeed(newSpeed);
  };

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50 max-w-xs">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Typing Experience</h3>

      <div className="space-y-3">
        {/* Sound Toggle */}
        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-700">Sound Effects</label>
          <EnhancedButton
            onClick={() => setSoundEnabled(!isSoundEnabled)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              isSoundEnabled
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isSoundEnabled ? 'ON' : 'OFF'}
          </EnhancedButton>
        </div>

        {/* Cursor Animation Toggle */}
        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-700">Cursor Animation</label>
          <EnhancedButton
            onClick={() => setCursorEnabled(!isCursorEnabled)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              isCursorEnabled
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isCursorEnabled ? 'ON' : 'OFF'}
          </EnhancedButton>
        </div>

        {/* Volume Slider */}
        <div className={isSoundEnabled ? '' : 'opacity-50'}>
          <label className="text-sm text-gray-700 block mb-1">
            Volume: {volume}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={volume}
            onChange={handleVolumeChange}
            disabled={!isSoundEnabled}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Cursor Speed Slider */}
        <div className={isCursorEnabled ? '' : 'opacity-50'}>
          <label className="text-sm text-gray-700 block mb-1">
            Cursor Speed: {speed}ms
          </label>
          <input
            type="range"
            min="20"
            max="200"
            value={speed}
            onChange={handleSpeedChange}
            disabled={!isCursorEnabled}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>
      </div>
    </div>
  );
}
