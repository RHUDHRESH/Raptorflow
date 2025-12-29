'use client';

import React, { forwardRef, useEffect, useRef, useCallback } from 'react';
import { useTypingExperience } from './TypingExperienceProvider';

interface EnhancedTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  // Additional props for enhanced typing experience
}

export const EnhancedTextarea = forwardRef<
  HTMLTextAreaElement,
  EnhancedTextareaProps
>(({ className, ...props }, ref) => {
  const { animateCursor, playKeySound, playBackspaceSound } =
    useTypingExperience();
  const lastKeyTime = useRef<number>(0);

  useEffect(() => {
    const textarea = (ref as React.RefObject<HTMLTextAreaElement>)?.current;
    if (!textarea) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const now = Date.now();

      // Animate cursor on any key
      animateCursor(textarea);

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
      animateCursor(textarea);
    };

    textarea.addEventListener('keydown', handleKeyDown);
    textarea.addEventListener('focus', handleFocus);

    return () => {
      textarea.removeEventListener('keydown', handleKeyDown);
      textarea.removeEventListener('focus', handleFocus);
    };
  }, [animateCursor, playKeySound, playBackspaceSound]);

  return (
    <textarea
      className={className}
      ref={ref}
      {...props}
    />
  );
});

EnhancedTextarea.displayName = 'EnhancedTextarea';
