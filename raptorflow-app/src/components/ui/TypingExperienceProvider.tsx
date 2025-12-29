'use client';

import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
} from 'react';
import { usePathname } from 'next/navigation';

interface TypingSound {
  play: () => void;
  setVolume: (volume: number) => void;
  setEnabled: (enabled: boolean) => void;
}

interface CursorAnimation {
  animate: (element: HTMLElement) => void;
  setDuration: (duration: number) => void;
  setEnabled: (enabled: boolean) => void;
}

interface TypingExperienceContextType {
  playKeySound: () => void;
  playClickSound: () => void;
  playBackspaceSound: () => void;
  playBellSound: () => void;
  animateCursor: (element: HTMLElement) => void;
  setSoundEnabled: (enabled: boolean) => void;
  setCursorEnabled: (enabled: boolean) => void;
  setSoundVolume: (volume: number) => void;
  setCursorSpeed: (speed: number) => void;
  isSoundEnabled: boolean;
  isCursorEnabled: boolean;
}

const TypingExperienceContext =
  createContext<TypingExperienceContextType | null>(null);

export function useTypingExperience() {
  const context = useContext(TypingExperienceContext);
  if (!context) {
    throw new Error(
      'useTypingExperience must be used within TypingExperienceProvider'
    );
  }
  return context;
}

export function TypingExperienceProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSoundEnabled, setSoundEnabled] = useState(true);
  const [isCursorEnabled, setCursorEnabled] = useState(true);
  const [soundVolume, setSoundVolume] = useState(0.3);
  const [cursorSpeed, setCursorSpeed] = useState(60); // Faster, more subtle
  const pathname = usePathname();

  const audioContextRef = useRef<AudioContext | null>(null);
  const keySoundBufferRef = useRef<AudioBuffer | null>(null);
  const clickSoundBufferRef = useRef<AudioBuffer | null>(null);
  const backspaceSoundBufferRef = useRef<AudioBuffer | null>(null);
  const bellSoundBufferRef = useRef<AudioBuffer | null>(null);
  const lastKeyTimeRef = useRef<number>(0);
  const cursorAnimationTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize audio context and sounds
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const initAudio = async () => {
      try {
        // Create audio context on first user interaction to avoid browser restrictions
        const createAudioContext = () => {
          const AudioContextClass =
            window.AudioContext || (window as any).webkitAudioContext;
          if (!AudioContextClass) {
            console.warn('Web Audio API not supported');
            return null;
          }
          return new AudioContextClass();
        };

        // Initialize audio context
        let audioContext = audioContextRef.current;
        if (!audioContext) {
          audioContext = createAudioContext();
          if (!audioContext) return;
          audioContextRef.current = audioContext;
        }

        // Resume context if suspended (required by some browsers)
        if (audioContext.state === 'suspended') {
          await audioContext.resume();
        }

        const sampleRate = audioContext.sampleRate;

        // Key press sound - perfect thocky sound based on research
        const keyDuration = 0.12; // Longer for deeper resonance
        const keyFrames = sampleRate * keyDuration;
        const keyBuffer = audioContext.createBuffer(1, keyFrames, sampleRate);
        const keyData = keyBuffer.getChannelData(0);

        for (let i = 0; i < keyFrames; i++) {
          const t = i / sampleRate;

          // Multi-stage envelope for thocky feel
          const attack = Math.min(t * 15, 1); // Quick initial attack
          const sustain = Math.exp(-(t - 0.02) * 15); // Sustain with decay
          const resonance = Math.sin(t * 50) * 0.1 * Math.exp(-t * 20); // Resonance tail
          const envelope = attack * sustain + resonance;

          // Deep bass foundation (150-250Hz) - the "thock"
          const bass = 0.5 * Math.sin(2 * Math.PI * 180 * t);
          // Low-mid body (300-500Hz) - fullness
          const body = 0.3 * Math.sin(2 * Math.PI * 350 * t);
          // Mid presence (800-1200Hz) - clarity without harshness
          const presence = 0.15 * Math.sin(2 * Math.PI * 900 * t);
          // Subtle high sparkle (2000-3000Hz) - crispness
          const sparkle = 0.05 * Math.sin(2 * Math.PI * 2400 * t);

          // Combine for perfect thocky sound
          keyData[i] = envelope * (bass + body + presence + sparkle);
        }
        keySoundBufferRef.current = keyBuffer;

        // Click sound - subtle and cushioned
        const clickDuration = 0.06;
        const clickFrames = sampleRate * clickDuration;
        const clickBuffer = audioContext.createBuffer(
          1,
          clickFrames,
          sampleRate
        );
        const clickData = clickBuffer.getChannelData(0);

        for (let i = 0; i < clickFrames; i++) {
          const t = i / sampleRate;
          // Soft attack and decay for muted feel
          const envelope = Math.min(t * 8, 1) * Math.exp(-t * 40);
          clickData[i] =
            envelope *
            (0.6 * Math.sin(2 * Math.PI * 600 * t) + // Main body
              0.2 * Math.sin(2 * Math.PI * 1200 * t) + // Upper harmonics
              0.1 * Math.sin(2 * Math.PI * 2400 * t)) * // Subtle sparkle
            0.3;
        }
        clickSoundBufferRef.current = clickBuffer;

        // Backspace sound - deeper, more substantial thock
        const backspaceDuration = 0.15; // Even longer for resonance
        const backspaceFrames = sampleRate * backspaceDuration;
        const backspaceBuffer = audioContext.createBuffer(
          1,
          backspaceFrames,
          sampleRate
        );
        const backspaceData = backspaceBuffer.getChannelData(0);

        for (let i = 0; i < backspaceFrames; i++) {
          const t = i / sampleRate;
          // Very slow attack for substantial feel
          const attack = Math.min(t * 5, 1);
          const decay = Math.exp(-(t - 0.05) * 10);
          const resonance = Math.sin(t * 30) * 0.15 * Math.exp(-t * 15);
          const envelope = attack * decay + resonance;

          backspaceData[i] =
            envelope *
            (0.7 * Math.sin(2 * Math.PI * 120 * t) + // Deep sub-bass
              0.4 * Math.sin(2 * Math.PI * 240 * t) + // Low-mid
              0.2 * Math.sin(2 * Math.PI * 480 * t) + // Mid
              0.1 * Math.sin(2 * Math.PI * 960 * t)) * // Upper harmonics
            0.6;
        }
        backspaceSoundBufferRef.current = backspaceBuffer;

        // Enhanced bell sound - satisfying completion reward
        const bellDuration = 0.4;
        const bellFrames = sampleRate * bellDuration;
        const bellBuffer = audioContext.createBuffer(1, bellFrames, sampleRate);
        const bellData = bellBuffer.getChannelData(0);

        for (let i = 0; i < bellFrames; i++) {
          const t = i / sampleRate;
          // Complex envelope for bell-like resonance
          const attack = Math.min(t * 8, 1);
          const decay = Math.exp(-(t - 0.08) * 6);
          const shimmer = Math.sin(t * 80) * 0.2 * Math.exp(-t * 12);
          const envelope = attack * decay + shimmer;

          // Rich harmonic series for bell sound
          const fundamental = Math.sin(2 * Math.PI * 750 * t);
          const octave = 0.4 * Math.sin(2 * Math.PI * 1500 * t);
          const fifth = 0.3 * Math.sin(2 * Math.PI * 1125 * t);
          const third = 0.2 * Math.sin(2 * Math.PI * 1875 * t);
          const sparkle = 0.1 * Math.sin(2 * Math.PI * 3000 * t);

          bellData[i] =
            envelope * (fundamental + octave + fifth + third + sparkle) * 0.25;
        }
        bellSoundBufferRef.current = bellBuffer;

        console.log('Typing sounds initialized successfully');
      } catch (error) {
        console.warn('Failed to initialize typing sounds:', error);
      }
    };

    // Initialize on first user interaction
    const handleFirstInteraction = () => {
      initAudio();
      document.removeEventListener('click', handleFirstInteraction);
      document.removeEventListener('keydown', handleFirstInteraction);
    };

    document.addEventListener('click', handleFirstInteraction);
    document.addEventListener('keydown', handleFirstInteraction);

    return () => {
      document.removeEventListener('click', handleFirstInteraction);
      document.removeEventListener('keydown', handleFirstInteraction);
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  const playSound = useCallback(
    (buffer: AudioBuffer | null) => {
      if (!isSoundEnabled || !buffer) return;

      const now = Date.now();
      // Rate limiting to prevent sound spam
      if (now - lastKeyTimeRef.current < 30) return;
      lastKeyTimeRef.current = now;

      try {
        // Ensure audio context exists and is running
        let audioContext = audioContextRef.current;
        if (!audioContext) {
          const AudioContextClass =
            window.AudioContext || (window as any).webkitAudioContext;
          if (!AudioContextClass) return;
          audioContext = new AudioContextClass();
          audioContextRef.current = audioContext;
        }

        // Resume context if suspended
        if (audioContext.state === 'suspended') {
          audioContext.resume().catch(console.warn);
        }

        const source = audioContext.createBufferSource();
        source.buffer = buffer;

        const gainNode = audioContext.createGain();
        gainNode.gain.value = soundVolume;

        // Add slight randomization to pitch for natural feel
        const playbackRate = 0.95 + Math.random() * 0.1;
        source.playbackRate.value = playbackRate;

        source.connect(gainNode);
        gainNode.connect(audioContext.destination);

        source.start(0);

        // Clean up after sound finishes
        source.onended = () => {
          try {
            source.disconnect();
            gainNode.disconnect();
          } catch (e) {
            // Ignore cleanup errors
          }
        };
      } catch (error) {
        // Silently fail to avoid breaking the app
        console.debug('Sound playback failed:', error);
      }
    },
    [isSoundEnabled, soundVolume]
  );

  const playKeySound = useCallback(() => {
    playSound(keySoundBufferRef.current);
  }, [playSound]);

  const playClickSound = useCallback(() => {
    playSound(clickSoundBufferRef.current);
  }, [playSound]);

  const playBackspaceSound = useCallback(() => {
    playSound(backspaceSoundBufferRef.current);
  }, [playSound]);

  const playBellSound = useCallback(() => {
    playSound(bellSoundBufferRef.current);
  }, [playSound]);

  const animateCursor = useCallback(
    (element: HTMLElement) => {
      if (!isCursorEnabled || !element) return;

      // Clear any existing animation
      if (cursorAnimationTimeoutRef.current) {
        clearTimeout(cursorAnimationTimeoutRef.current);
      }

      // Subtle, elegant cursor animation - no lunging
      element.style.transition = `all ${cursorSpeed}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)`;

      // Gentle scale and subtle glow instead of aggressive transform
      element.style.transform = 'scale(1.02)';
      element.style.boxShadow = '0 0 0 1px rgba(0, 0, 0, 0.05)';

      cursorAnimationTimeoutRef.current = setTimeout(() => {
        element.style.transform = 'scale(1)';
        element.style.boxShadow = '';
      }, cursorSpeed);
    },
    [isCursorEnabled, cursorSpeed]
  );

  // Global keyboard event listener
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Check if we're in an input context
      const target = e.target as HTMLElement;
      const isInputElement =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target.isContentEditable ||
        target.getAttribute('contenteditable') === 'true' ||
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA';

      if (isInputElement) {
        // Animate cursor for any typing activity
        if (target instanceof HTMLElement) {
          animateCursor(target);
        }

        // Play appropriate sounds
        if (e.key === 'Backspace' || e.key === 'Delete') {
          playBackspaceSound();
        } else if (e.key === 'Enter') {
          // Satisfying completion sound for Enter
          playBellSound();
        } else if (
          e.key.length === 1 &&
          !e.ctrlKey &&
          !e.metaKey &&
          !e.altKey
        ) {
          // Only play for actual character input, not modifier keys
          playKeySound();
        }
      }
    };

    const handleMouseDown = (e: MouseEvent) => {
      // Play click sound for button-like elements
      const target = e.target as HTMLElement;
      const isButtonElement =
        target.tagName === 'BUTTON' ||
        target.tagName === 'A' ||
        target.role === 'button' ||
        target.getAttribute('role') === 'button' ||
        target.onclick ||
        target.classList.contains('clickable') ||
        (target as HTMLInputElement).type === 'submit' ||
        (target as HTMLInputElement).type === 'button';

      if (isButtonElement) {
        playClickSound();
        if (target instanceof HTMLElement) {
          animateCursor(target);
        }
      }
    };

    const handleFocus = (e: FocusEvent) => {
      // Animate cursor when input elements get focus
      const target = e.target as HTMLElement;
      if (target instanceof HTMLElement) {
        animateCursor(target);
      }
    };

    // Add event listeners with capture to ensure we get events first
    document.addEventListener('keydown', handleKeyDown, true);
    document.addEventListener('mousedown', handleMouseDown, true);
    document.addEventListener('focus', handleFocus, true);

    return () => {
      document.removeEventListener('keydown', handleKeyDown, true);
      document.removeEventListener('mousedown', handleMouseDown, true);
      document.removeEventListener('focus', handleFocus, true);
    };
  }, [playKeySound, playClickSound, playBackspaceSound, animateCursor]);

  const contextValue: TypingExperienceContextType = {
    playKeySound,
    playClickSound,
    playBackspaceSound,
    playBellSound,
    animateCursor,
    setSoundEnabled,
    setCursorEnabled,
    setSoundVolume,
    setCursorSpeed,
    isSoundEnabled,
    isCursorEnabled,
  };

  return (
    <TypingExperienceContext.Provider value={contextValue}>
      {children}
    </TypingExperienceContext.Provider>
  );
}
