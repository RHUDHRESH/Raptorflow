'use client';

import { useEffect, useRef } from 'react';
import { useTypingExperience } from './TypingExperienceProvider';

/**
 * Hook to automatically add typing sounds to any input/textarea element
 * Usage: const typingRef = useTypingSounds();
 *        <input ref={typingRef} />
 */
export function useTypingSounds() {
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);
  const { playKeySound, playClickSound, playBackspaceSound } =
    useTypingExperience();

  useEffect(() => {
    const element = inputRef.current;
    if (!element) return;

    const handleKeyDown = (e: Event) => {
      const keyboardEvent = e as KeyboardEvent;
      if (keyboardEvent.key === 'Backspace') {
        playBackspaceSound({ velocity: 0.4 });
      } else if (
        keyboardEvent.key.length === 1 &&
        !keyboardEvent.ctrlKey &&
        !keyboardEvent.metaKey
      ) {
        playKeySound({ velocity: 0.3 });
      }
    };

    const handleClick = () => {
      playClickSound({ velocity: 0.5 });
    };

    element.addEventListener('keydown', handleKeyDown);
    element.addEventListener('click', handleClick);

    return () => {
      element.removeEventListener('keydown', handleKeyDown);
      element.removeEventListener('click', handleClick);
    };
  }, [playKeySound, playClickSound, playBackspaceSound]);

  return inputRef;
}
