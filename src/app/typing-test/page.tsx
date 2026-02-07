"use client";

import { useState } from 'react';
import { TypingExperienceControls } from '@/components/ui/typing/TypingExperienceControls';
import { useTypingExperience } from '@/components/ui/typing/TypingExperienceProvider';

export default function TypingTestPage() {
  const [text, setText] = useState('');
  const [message, setMessage] = useState('');
  const { playCompletionSound } = useTypingExperience();

  return (
    <div className="min-h-screen bg-[#FAF9F6] p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-serif text-[#1E1E1E] mb-8">10x Typing Experience Test</h1>

        <div className="space-y-6">
          {/* Test Input Fields */}
          <div className="bg-white p-6 rounded-lg border border-[rgba(0,0,0,0.08)]">
            <h2 className="text-xl font-semibold text-[#1E1E1E] mb-4">Test Input Fields</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#6B6B6B] mb-2">
                  Text Input
                </label>
                <input
                  type="text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Type here to test the 10x typing experience..."
                  className="w-full px-4 py-2 border border-[rgba(0,0,0,0.08)] rounded-lg focus:outline-none focus:border-[#1E1E1E]"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[#6B6B6B] mb-2">
                  Textarea
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type longer text here to experience the enhanced sounds..."
                  rows={4}
                  className="w-full px-4 py-2 border border-[rgba(0,0,0,0.08)] rounded-lg focus:outline-none focus:border-[#1E1E1E] resize-none"
                />
              </div>
            </div>
          </div>

          {/* Test Buttons */}
          <div className="bg-white p-6 rounded-lg border border-[rgba(0,0,0,0.08)]">
            <h2 className="text-xl font-semibold text-[#1E1E1E] mb-4">Test Buttons</h2>

            <div className="flex gap-4">
              <button
                onClick={() => playCompletionSound()}
                className="px-6 py-2 bg-[#1E1E1E] text-white rounded-lg hover:bg-[#2E2E2E] transition-colors"
              >
                Play Completion Sound
              </button>

              <button className="px-6 py-2 border border-[#1E1E1E] text-[#1E1E1E] rounded-lg hover:bg-[#1E1E1E] hover:text-white transition-colors">
                Secondary Button
              </button>
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-white p-6 rounded-lg border border-[rgba(0,0,0,0.08)]">
            <h2 className="text-xl font-semibold text-[#1E1E1E] mb-4">What to Test</h2>

            <ul className="space-y-2 text-[#6B6B6B]">
              <li>• Type in the input fields - you should hear enhanced "thocky" sounds</li>
              <li>• Press Backspace/Delete - you should hear a different sound</li>
              <li>• Press Enter - you should hear a satisfying bell sound</li>
              <li>• Click the buttons - you should hear click sounds</li>
              <li>• Watch for smooth cursor animations (60ms speed)</li>
              <li>• Use the controls panel to adjust volume, intensity, and profiles</li>
              <li>• Try different sound profiles (Professional, Creative, Gaming, Minimalist)</li>
              <li>• Test context-aware adaptations</li>
            </ul>
          </div>

          {/* Current Values Display */}
          <div className="bg-white p-6 rounded-lg border border-[rgba(0,0,0,0.08)]">
            <h2 className="text-xl font-semibold text-[#1E1E1E] mb-4">Current Values</h2>

            <div className="space-y-2 text-sm">
              <p><strong>Text Input:</strong> "{text}"</p>
              <p><strong>Message:</strong> "{message}"</p>
              <p><strong>Text Length:</strong> {text.length} characters</p>
              <p><strong>Message Length:</strong> {message.length} characters</p>
            </div>
          </div>
        </div>
      </div>

      {/* 10x Controls */}
      <TypingExperienceControls />
    </div>
  );
}
