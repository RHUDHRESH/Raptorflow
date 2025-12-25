"use client";

import React, { useState } from 'react';
import { useTypingExperience } from './TypingExperienceProvider';

export function TypingExperienceControls() {
  const {
    isSoundEnabled,
    isAnimationEnabled,
    currentSoundProfile,
    currentAnimationProfile,
    currentContext,
    setSoundProfile,
    setAnimationProfile,
    setVolume,
    setIntensity,
    setAccessibilityMode,
    getTypingMetrics,
    getContextInsights,
    recordFeedback,
    getAvailableSoundProfiles,
    getAvailableAnimationProfiles,
  } = useTypingExperience();

  const [volumeValue, setVolumeValue] = useState(30);
  const [intensityValue, setIntensityValue] = useState<'subtle' | 'normal' | 'pronounced'>('subtle');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  const soundProfiles = getAvailableSoundProfiles();
  const animationProfiles = getAvailableAnimationProfiles();
  const metrics = getTypingMetrics();
  const insights = getContextInsights();

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseInt(e.target.value);
    setVolumeValue(newVolume);
    setVolume(newVolume / 100);
  };

  const handleIntensityChange = (newIntensity: 'subtle' | 'normal' | 'pronounced') => {
    setIntensityValue(newIntensity);
    setIntensity(newIntensity);
  };

  const handleFeedback = (type: 'sound' | 'animation' | 'overall', rating: number) => {
    recordFeedback({
      soundSatisfaction: type === 'sound' ? rating : 5,
      animationSatisfaction: type === 'animation' ? rating : 5,
      overallExperience: type === 'overall' ? rating : 5,
    });
  };

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50 max-w-sm">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">10x Typing Experience</h3>

      {/* Basic Controls */}
      <div className="space-y-3">
        {/* Sound Toggle */}
        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-700">Sound</label>
          <button
            onClick={() => setSoundProfile(isSoundEnabled ? 'minimalist' : 'professional')}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              isSoundEnabled
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isSoundEnabled ? 'ON' : 'OFF'}
          </button>
        </div>

        {/* Animation Toggle */}
        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-700">Animation</label>
          <button
            onClick={() => setAccessibilityMode(!isAnimationEnabled)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              isAnimationEnabled
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isAnimationEnabled ? 'ON' : 'OFF'}
          </button>
        </div>

        {/* Volume Slider */}
        <div className={isSoundEnabled ? '' : 'opacity-50'}>
          <label className="text-sm text-gray-700 block mb-1">
            Volume: {volumeValue}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={volumeValue}
            onChange={handleVolumeChange}
            disabled={!isSoundEnabled}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Sound Profile Selector */}
        <div className={isSoundEnabled ? '' : 'opacity-50'}>
          <label className="text-sm text-gray-700 block mb-1">Sound Profile</label>
          <select
            value={currentSoundProfile}
            onChange={(e) => setSoundProfile(e.target.value)}
            disabled={!isSoundEnabled}
            className="w-full text-xs border border-gray-300 rounded px-2 py-1"
          >
            {soundProfiles.map(profile => (
              <option key={profile} value={profile}>
                {profile.charAt(0).toUpperCase() + profile.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Animation Profile Selector */}
        <div className={isAnimationEnabled ? '' : 'opacity-50'}>
          <label className="text-sm text-gray-700 block mb-1">Animation Profile</label>
          <select
            value={currentAnimationProfile}
            onChange={(e) => setAnimationProfile(e.target.value)}
            disabled={!isAnimationEnabled}
            className="w-full text-xs border border-gray-300 rounded px-2 py-1"
          >
            {animationProfiles.map(profile => (
              <option key={profile} value={profile}>
                {profile.charAt(0).toUpperCase() + profile.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Intensity Selector */}
        <div className={isAnimationEnabled ? '' : 'opacity-50'}>
          <label className="text-sm text-gray-700 block mb-1">Intensity</label>
          <div className="flex gap-1">
            {(['subtle', 'normal', 'pronounced'] as const).map(level => (
              <button
                key={level}
                onClick={() => handleIntensityChange(level)}
                disabled={!isAnimationEnabled}
                className={`flex-1 px-2 py-1 text-xs rounded transition-colors ${
                  level === intensityValue
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Advanced Toggle */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="w-full mt-3 text-xs text-gray-600 hover:text-gray-800 transition-colors"
      >
        {showAdvanced ? 'Hide' : 'Show'} Advanced
      </button>

      {/* Advanced Controls */}
      {showAdvanced && (
        <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
          {/* Current Context Display */}
          <div className="text-xs text-gray-600">
            <div className="font-medium">Current Context:</div>
            <div className="grid grid-cols-2 gap-1 mt-1">
              <div>App: {currentContext?.application}</div>
              <div>Env: {currentContext?.environment}</div>
              <div>Time: {currentContext?.timeOfDay}</div>
              <div>State: {currentContext?.userState}</div>
            </div>
          </div>

          {/* Quick Feedback */}
          <div className="text-xs text-gray-600">
            <div className="font-medium">Quick Feedback:</div>
            <div className="flex gap-1 mt-1">
              {[1, 2, 3, 4, 5].map(rating => (
                <button
                  key={rating}
                  onClick={() => handleFeedback('overall', rating * 2)}
                  className="w-6 h-6 text-xs border border-gray-300 rounded hover:bg-gray-100"
                >
                  {rating}
                </button>
              ))}
            </div>
          </div>

          {/* Analytics Toggle */}
          <button
            onClick={() => setShowAnalytics(!showAnalytics)}
            className="w-full text-xs text-gray-600 hover:text-gray-800 transition-colors"
          >
            {showAnalytics ? 'Hide' : 'Show'} Analytics
          </button>

          {/* Analytics Display */}
          {showAnalytics && (
            <div className="text-xs text-gray-600 bg-gray-50 rounded p-2">
              <div className="font-medium">Typing Metrics:</div>
              <div className="grid grid-cols-3 gap-1 mt-1">
                <div>Speed: {Math.round(metrics.speed || 0)} wpm</div>
                <div>Accuracy: {Math.round((metrics.accuracy || 0) * 100)}%</div>
                <div>Consistency: {Math.round((metrics.consistency || 0) * 100)}%</div>
              </div>

              {Object.keys(insights.dominantContexts || {}).length > 0 && (
                <>
                  <div className="font-medium mt-2">Dominant Contexts:</div>
                  <div className="mt-1">
                    {Object.entries(insights.dominantContexts || {})
                      .sort((a, b) => (b[1] as number) - (a[1] as number))
                      .slice(0, 3)
                      .map(([context, count]) => (
                        <div key={context} className="text-xs">
                          {context}: {count as number}
                        </div>
                      ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
