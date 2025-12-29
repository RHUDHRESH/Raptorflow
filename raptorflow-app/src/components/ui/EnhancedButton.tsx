'use client';

import React, { forwardRef, useRef, useEffect, useCallback } from 'react';
import { useTypingExperience } from './TypingExperienceProvider';

interface EnhancedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  // Additional props for enhanced typing experience
}

export const EnhancedButton = forwardRef<
  HTMLButtonElement,
  EnhancedButtonProps
>(({ className, children, ...props }, ref) => {
  const { playClickSound, animateCursor } = useTypingExperience();

  useEffect(() => {
    const button = (ref as React.RefObject<HTMLButtonElement>)?.current;
    if (!button) return;

    const handleMouseDown = () => {
      playClickSound();
      animateCursor(button);
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        playClickSound();
        animateCursor(button);
      }
    };

    const handleMouseUp = () => {
      animateCursor(button);
    };

    button.addEventListener('mousedown', handleMouseDown);
    button.addEventListener('keydown', handleKeyDown);
    button.addEventListener('mouseup', handleMouseUp);

    return () => {
      button.removeEventListener('mousedown', handleMouseDown);
      button.removeEventListener('keydown', handleKeyDown);
      button.removeEventListener('mouseup', handleMouseUp);
    };
  }, [ref, playClickSound, animateCursor]);

  return (
    <button
      className={className}
      ref={ref}
      {...props}
    >
      {children}
    </button>
  );
});

EnhancedButton.displayName = 'EnhancedButton';
