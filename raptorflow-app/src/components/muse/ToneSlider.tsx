'use client';

import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface ToneSliderProps {
  value?: number;
  onChange?: (value: number, label: string) => void;
  className?: string;
}

const TONE_STOPS = [
  { value: 0, label: 'Casual', description: 'Friendly, conversational' },
  { value: 25, label: 'Balanced', description: 'Clear, approachable' },
  { value: 50, label: 'Professional', description: 'Polished, formal' },
  { value: 75, label: 'Authoritative', description: 'Expert, confident' },
  { value: 100, label: 'Provocative', description: 'Bold, challenging' },
];

function getToneForValue(value: number) {
  // Find the closest tone stop
  let closest = TONE_STOPS[0];
  let minDiff = Math.abs(value - TONE_STOPS[0].value);

  for (const stop of TONE_STOPS) {
    const diff = Math.abs(value - stop.value);
    if (diff < minDiff) {
      minDiff = diff;
      closest = stop;
    }
  }

  return closest;
}

export function ToneSlider({
  value = 50,
  onChange,
  className,
}: ToneSliderProps) {
  const [localValue, setLocalValue] = useState(value);
  const [isDragging, setIsDragging] = useState(false);

  const currentTone = getToneForValue(localValue);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = parseInt(e.target.value, 10);
      setLocalValue(newValue);
      const tone = getToneForValue(newValue);
      onChange?.(newValue, tone.label);
    },
    [onChange]
  );

  return (
    <div className={cn('space-y-3', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-widest text-muted-foreground">
          Tone
        </span>
        <div className="flex items-center gap-2">
          <span
            className={cn(
              'text-sm font-medium transition-all duration-300',
              isDragging && 'text-foreground scale-105'
            )}
          >
            {currentTone.label}
          </span>
        </div>
      </div>

      {/* Slider track */}
      <div className="relative">
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-foreground/80 rounded-full transition-all duration-150 ease-out"
            style={{ width: `${localValue}%` }}
          />
        </div>

        {/* Custom thumb via input range */}
        <input
          type="range"
          min="0"
          max="100"
          value={localValue}
          onChange={handleChange}
          onMouseDown={() => setIsDragging(true)}
          onMouseUp={() => setIsDragging(false)}
          onTouchStart={() => setIsDragging(true)}
          onTouchEnd={() => setIsDragging(false)}
          className={cn(
            'absolute inset-0 w-full h-2 opacity-0 cursor-pointer',
            '[&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4',
            '[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-foreground',
            '[&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4',
            '[&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-foreground'
          )}
        />

        {/* Visual thumb */}
        <div
          className={cn(
            'absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full',
            'bg-foreground shadow-md pointer-events-none',
            'transition-transform duration-150',
            isDragging && 'scale-125'
          )}
          style={{ left: `calc(${localValue}% - 8px)` }}
        />
      </div>

      {/* Stop markers */}
      <div className="flex justify-between px-1">
        {TONE_STOPS.map((stop) => (
          <button
            key={stop.value}
            onClick={() => {
              setLocalValue(stop.value);
              onChange?.(stop.value, stop.label);
            }}
            className={cn(
              'flex flex-col items-center gap-1 group',
              'transition-opacity duration-200',
              Math.abs(localValue - stop.value) <= 12
                ? 'opacity-100'
                : 'opacity-40 hover:opacity-70'
            )}
          >
            <div
              className={cn(
                'w-1 h-1 rounded-full bg-muted-foreground',
                'group-hover:scale-150 transition-transform'
              )}
            />
            <span className="text-[10px] text-muted-foreground hidden sm:block">
              {stop.label}
            </span>
          </button>
        ))}
      </div>

      {/* Description */}
      <p
        className={cn(
          'text-xs text-muted-foreground text-center',
          'transition-all duration-300',
          isDragging && 'opacity-0'
        )}
      >
        {currentTone.description}
      </p>
    </div>
  );
}

// Compact inline version for toolbar
export function ToneSliderCompact({
  value = 50,
  onChange,
  className,
}: ToneSliderProps) {
  const [localValue, setLocalValue] = useState(value);
  const currentTone = getToneForValue(localValue);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = parseInt(e.target.value, 10);
      setLocalValue(newValue);
      const tone = getToneForValue(newValue);
      onChange?.(newValue, tone.label);
    },
    [onChange]
  );

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <span className="text-xs text-muted-foreground whitespace-nowrap">
        {currentTone.label}
      </span>
      <div className="relative flex-1 min-w-[100px]">
        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-foreground/60 rounded-full transition-all duration-150"
            style={{ width: `${localValue}%` }}
          />
        </div>
        <input
          type="range"
          min="0"
          max="100"
          value={localValue}
          onChange={handleChange}
          className="absolute inset-0 w-full opacity-0 cursor-pointer"
        />
      </div>
    </div>
  );
}
