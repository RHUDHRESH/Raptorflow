'use client';

import React, { useState } from 'react';
import { RefreshCw, ChevronDown, X, Send } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RegenWithFeedbackProps {
  onRegenerate: (feedback?: string) => void;
  variant?: 'button' | 'icon';
  className?: string;
}

const QUICK_FEEDBACK = [
  { label: 'Too vague', value: 'too_vague' },
  { label: 'Too long', value: 'too_long' },
  { label: 'Too formal', value: 'too_formal' },
  { label: 'Not my voice', value: 'not_my_voice' },
  { label: 'Too salesy', value: 'too_salesy' },
  { label: 'Different angle', value: 'different_angle' },
];

export function RegenWithFeedback({
  onRegenerate,
  variant = 'button',
  className,
}: RegenWithFeedbackProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [customFeedback, setCustomFeedback] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleQuickFeedback = async (feedback: string) => {
    setIsProcessing(true);
    await onRegenerate(feedback);
    setIsProcessing(false);
    setIsOpen(false);
  };

  const handleCustomSubmit = async () => {
    if (!customFeedback.trim()) {
      onRegenerate();
      setIsOpen(false);
      return;
    }
    setIsProcessing(true);
    await onRegenerate(customFeedback);
    setIsProcessing(false);
    setCustomFeedback('');
    setIsOpen(false);
  };

  const handleSimpleRegen = () => {
    onRegenerate();
  };

  return (
    <div className="relative">
      {/* Main Button */}
      <div className="flex items-center">
        <button
          onClick={handleSimpleRegen}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-l-lg text-sm transition-colors',
            'hover:bg-[#F3F4EE] text-[#5B5F61]',
            isProcessing && 'opacity-50 pointer-events-none',
            className
          )}
        >
          <RefreshCw
            className={cn('w-3.5 h-3.5', isProcessing && 'animate-spin')}
          />
          {variant === 'button' && 'Regenerate'}
        </button>
        {/* Dropdown Trigger */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'p-2 rounded-r-lg border-l border-[#E5E6E3] transition-colors',
            'hover:bg-[#F3F4EE] text-[#5B5F61]',
            isOpen && 'bg-[#F3F4EE]'
          )}
        >
          <ChevronDown
            className={cn(
              'w-3.5 h-3.5 transition-transform',
              isOpen && 'rotate-180'
            )}
          />
        </button>
      </div>

      {/* Feedback Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-72 bg-white border border-[#E5E6E3] rounded-2xl shadow-lg z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#E5E6E3]">
            <span className="text-xs font-mono uppercase tracking-wider text-[#9D9F9F]">
              What's wrong?
            </span>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-[#F3F4EE] rounded"
            >
              <X className="w-3.5 h-3.5 text-[#9D9F9F]" />
            </button>
          </div>

          {/* Quick Chips */}
          <div className="p-3 flex flex-wrap gap-2">
            {QUICK_FEEDBACK.map((item) => (
              <button
                key={item.value}
                onClick={() => handleQuickFeedback(item.value)}
                disabled={isProcessing}
                className={cn(
                  'px-3 py-1.5 text-xs rounded-full border border-[#E5E6E3] transition-all',
                  'hover:bg-[#2D3538] hover:text-white hover:border-[#2D3538]',
                  'text-[#5B5F61]',
                  isProcessing && 'opacity-50'
                )}
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Custom Input */}
          <div className="p-3 pt-0">
            <div className="flex items-center gap-2 bg-[#FAFAF8] rounded-xl p-2">
              <input
                type="text"
                value={customFeedback}
                onChange={(e) => setCustomFeedback(e.target.value)}
                placeholder="Or type what you want..."
                className="flex-1 bg-transparent text-sm text-[#2D3538] placeholder:text-[#9D9F9F] outline-none px-2"
                onKeyDown={(e) => e.key === 'Enter' && handleCustomSubmit()}
              />
              <button
                onClick={handleCustomSubmit}
                disabled={isProcessing}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  'bg-[#2D3538] text-white hover:bg-[#1A1D1E]',
                  isProcessing && 'opacity-50'
                )}
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
