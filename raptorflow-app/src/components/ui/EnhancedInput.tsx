'use client';

import React, { forwardRef, useEffect, useRef, useCallback } from 'react';
import { useTypingExperience } from './TypingExperienceProvider';

interface EnhancedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  // Additional props for enhanced typing experience
}

export const EnhancedInput = forwardRef<HTMLInputElement, EnhancedInputProps>(
  ({ className, ...props }, ref) => {
    const { animateCursor, playKeySound, playBackspaceSound } =
      useTypingExperience();
    const lastKeyTime = useRef<number>(0);

    useEffect(() => {
      const input = (ref as React.RefObject<HTMLInputElement>)?.current;
      if (!input) return;
      if (!input) return;

      const handleKeyDown = (e: KeyboardEvent) => {
        const now = Date.now();

        // Animate cursor on any key
        animateCursor(input);

        // Rate limiting for sounds
        if (now - lastKeyTime.current < 30) return;
        lastKeyTime.current = now;

        if (e.key === 'Backspace' || e.key === 'Delete') {
          playBackspaceSound();
        } else if (e.key.length === 1) {
          playKeySound();
        }
      };

      const handleFocus = () => {
        animateCursor(input);
      };

      input.addEventListener('keydown', handleKeyDown);
      input.addEventListener('focus', handleFocus);

      return () => {
        input.removeEventListener('keydown', handleKeyDown);
        input.removeEventListener('focus', handleFocus);
      };
    }, [animateCursor, playKeySound, playBackspaceSound]);

    return (
      <input
        className={className}
        ref={ref}
        {...props}
      />
    );
  }
);

EnhancedInput.displayName = 'EnhancedInput';
