"use client";

import React, { forwardRef, useRef, useEffect, useCallback } from 'react';
import { useTypingExperience } from './TypingExperienceProvider';

interface EnhancedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  // Additional props for enhanced typing experience
}

export const EnhancedButton = forwardRef<HTMLButtonElement, EnhancedButtonProps>(
  ({ className, children, ...props }, ref) => {
    const buttonRef = useRef<HTMLButtonElement>(null);
    const { playClickSound, animateCursor } = useTypingExperience();

    // Merge refs
    const mergedRef = useCallback((element: HTMLButtonElement | null) => {
      if (typeof ref === 'function') {
        ref(element);
      } else if (ref) {
        ref.current = element;
      }
      buttonRef.current = element;
    }, [ref]);

    useEffect(() => {
      const button = buttonRef.current;
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

      const handleFocus = () => {
        animateCursor(button);
      };

      button.addEventListener('mousedown', handleMouseDown);
      button.addEventListener('keydown', handleKeyDown);
      button.addEventListener('focus', handleFocus);

      return () => {
        button.removeEventListener('mousedown', handleMouseDown);
        button.removeEventListener('keydown', handleKeyDown);
        button.removeEventListener('focus', handleFocus);
      };
    }, [playClickSound, animateCursor]);

    return (
      <button
        ref={mergedRef}
        className={className}
        {...props}
      >
        {children}
      </button>
    );
  }
);

EnhancedButton.displayName = 'EnhancedButton';
