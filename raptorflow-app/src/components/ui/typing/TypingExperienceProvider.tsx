"use client";

import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { usePathname } from 'next/navigation';
import { AudioEngine, AudioConfig, SoundProfile } from './AudioEngine';
import { AnimationEngine, AnimationConfig } from './AnimationEngine';
import { ContextManager, ContextualSettings, TypingContext } from './ContextManager';

interface TypingExperienceContextType {
  // Core functionality
  playKeySound: (options?: { velocity?: number; position?: number }) => void;
  playClickSound: (options?: { velocity?: number; position?: number }) => void;
  playBackspaceSound: (options?: { velocity?: number; position?: number }) => void;
  playCompletionSound: (options?: { velocity?: number; position?: number }) => void;
  animateElement: (element: HTMLElement, context: any) => void;

  // Configuration
  setSoundProfile: (profile: string) => void;
  setAnimationProfile: (profile: string) => void;
  setVolume: (volume: number) => void;
  setIntensity: (intensity: 'subtle' | 'normal' | 'pronounced') => void;
  setAccessibilityMode: (enabled: boolean) => void;

  // State
  isSoundEnabled: boolean;
  isAnimationEnabled: boolean;
  currentSoundProfile: string;
  currentAnimationProfile: string;
  currentContext: TypingContext;

  // Analytics
  getTypingMetrics: () => any;
  getContextInsights: () => any;
  recordFeedback: (feedback: any) => void;

  // Available options
  getAvailableSoundProfiles: () => string[];
  getAvailableAnimationProfiles: () => string[];
}

const TypingExperienceContext = createContext<TypingExperienceContextType | null>(null);

export function useTypingExperience() {
  const context = useContext(TypingExperienceContext);
  if (!context) {
    throw new Error('useTypingExperience must be used within TypingExperienceProvider');
  }
  return context;
}

interface TypingExperienceProviderProps {
  children: React.ReactNode;
  config?: {
    sound?: Partial<AudioConfig>;
    animation?: Partial<AnimationConfig>;
    contextual?: Partial<ContextualSettings>;
  };
}

export function TypingExperienceProvider({ children, config = {} }: TypingExperienceProviderProps) {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isSoundEnabled, setIsSoundEnabled] = useState(true);
  const [isAnimationEnabled, setIsAnimationEnabled] = useState(true);
  const [currentSoundProfile, setCurrentSoundProfile] = useState('professional');
  const [currentAnimationProfile, setCurrentAnimationProfile] = useState('subtle');
  const [currentContext, setCurrentContext] = useState<TypingContext | null>(null);

  // Engine instances
  const audioEngineRef = useRef<AudioEngine | null>(null);
  const animationEngineRef = useRef<AnimationEngine | null>(null);
  const contextManagerRef = useRef<ContextManager | null>(null);

  // Initialize engines
  useEffect(() => {
    const initializeEngines = async () => {
      try {
        // Initialize Audio Engine
        const audioConfig: AudioConfig = {
          volume: 0.15,  // Reduced from 0.3 to 0.15 for much calmer experience
          adaptiveVolume: true,
          spatialAudio: false,
          soundProfile: 'professional',
          sensitivityMode: 'minimal',  // Changed to minimal for less sensitivity
          ...config.sound
        };

        audioEngineRef.current = new AudioEngine(audioConfig);
        await audioEngineRef.current.initialize();

        // Initialize Animation Engine
        const animationConfig: AnimationConfig = {
          enabled: true,
          profile: 'subtle',
          speed: 100,
          intensity: 'subtle',
          accessibilityMode: false,
          ...config.animation
        };

        animationEngineRef.current = new AnimationEngine(animationConfig);

        // Initialize Context Manager
        const contextualSettings: ContextualSettings = {
          soundProfile: 'professional',
          animationProfile: 'subtle',
          volume: 0.3,
          intensity: 'subtle',
          features: {
            completionSounds: true,
            particleEffects: false,
            rippleEffects: true,
            adaptiveVolume: true
          },
          ...config.contextual
        };

        contextManagerRef.current = new ContextManager(contextualSettings);

        setIsInitialized(true);
        console.log('10x Typing Experience initialized successfully');
      } catch (error) {
        console.error('Failed to initialize Typing Experience:', error);
      }
    };

    initializeEngines();

    return () => {
      audioEngineRef.current?.cleanup();
      animationEngineRef.current?.cleanup();
    };
  }, []);

  // Global event listeners
  useEffect(() => {
    if (!isInitialized) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const isInputElement =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target.isContentEditable ||
        target.getAttribute('contenteditable') === 'true';

      if (isInputElement && contextManagerRef.current) {
        // Update context
        const context = contextManagerRef.current.updateContext(target, e);
        setCurrentContext(context);

        // Get adapted settings
        const settings = contextManagerRef.current.getAdaptedSettings();

        // Update engines
        audioEngineRef.current?.updateConfig({
          soundProfile: settings.soundProfile,
          volume: settings.volume
        });

        animationEngineRef.current?.updateConfig({
          profile: settings.animationProfile,
          intensity: settings.intensity,
          accessibilityMode: !isAnimationEnabled
        });

        // Play sounds based on key
        if (isSoundEnabled && settings.features.completionSounds) {
          const velocity = e.key === 'Backspace' || e.key === 'Delete' ? 0.7 : 1;

          if (e.key === 'Backspace' || e.key === 'Delete') {
            playBackspaceSound({ velocity });
          } else if (e.key === 'Enter') {
            playCompletionSound({ velocity });
          } else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
            playKeySound({ velocity });
          }
        }

        // Animate element
        if (isAnimationEnabled) {
          animationEngineRef.current?.animateElement(target, {
            type: 'typing',
            velocity: e.key === 'Backspace' ? 0.7 : 1
          });
        }
      }
    };

    const handleMouseDown = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const isButtonElement =
        target.tagName === 'BUTTON' ||
        target.tagName === 'A' ||
        target.role === 'button' ||
        target.getAttribute('role') === 'button' ||
        target.onclick ||
        target.classList.contains('clickable');

      if (isButtonElement) {
        // Play click sound
        if (isSoundEnabled) {
          playClickSound();
        }

        // Animate button
        if (isAnimationEnabled) {
          animationEngineRef.current?.animateElement(target, {
            type: 'click',
            velocity: 1
          });

          // Add ripple effect
          const rect = target.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          animationEngineRef.current?.createRippleEffect(target, x, y);
        }
      }
    };

    const handleFocus = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      if (isAnimationEnabled && target instanceof HTMLElement) {
        animationEngineRef.current?.animateElement(target, {
          type: 'focus'
        });
      }
    };

    // Add event listeners
    document.addEventListener('keydown', handleKeyDown, true);
    document.addEventListener('mousedown', handleMouseDown, true);
    document.addEventListener('focus', handleFocus, true);

    return () => {
      document.removeEventListener('keydown', handleKeyDown, true);
      document.removeEventListener('mousedown', handleMouseDown, true);
      document.removeEventListener('focus', handleFocus, true);
    };
  }, [isInitialized, isSoundEnabled, isAnimationEnabled]);

  // Sound functions
  const playKeySound = useCallback((options: { velocity?: number; position?: number } = {}) => {
    audioEngineRef.current?.playSound('key', {
      velocity: options.velocity,
      spatialPosition: options.position,
      pitchVariation: (Math.random() - 0.5) * 0.1
    });
  }, []);

  const playClickSound = useCallback((options: { velocity?: number; position?: number } = {}) => {
    audioEngineRef.current?.playSound('click', {
      velocity: options.velocity || 0.8,
      spatialPosition: options.position,
      pitchVariation: (Math.random() - 0.5) * 0.05
    });
  }, []);

  const playBackspaceSound = useCallback((options: { velocity?: number; position?: number } = {}) => {
    audioEngineRef.current?.playSound('backspace', {
      velocity: options.velocity || 0.7,
      spatialPosition: options.position,
      pitchVariation: (Math.random() - 0.5) * 0.08
    });
  }, []);

  const playCompletionSound = useCallback((options: { velocity?: number; position?: number } = {}) => {
    audioEngineRef.current?.playSound('completion', {
      velocity: options.velocity || 1,
      spatialPosition: options.position,
      pitchVariation: (Math.random() - 0.5) * 0.03
    });
  }, []);

  // Animation function
  const animateElement = useCallback((element: HTMLElement, context: any) => {
    animationEngineRef.current?.animateElement(element, context);
  }, []);

  // Configuration functions
  const setSoundProfile = useCallback((profile: string) => {
    audioEngineRef.current?.updateConfig({ soundProfile: profile });
    setCurrentSoundProfile(profile);
    contextManagerRef.current?.updateUserPreferences({ soundProfile: profile });
  }, []);

  const setAnimationProfile = useCallback((profile: string) => {
    animationEngineRef.current?.updateConfig({ profile });
    setCurrentAnimationProfile(profile);
    contextManagerRef.current?.updateUserPreferences({ animationProfile: profile });
  }, []);

  const setVolume = useCallback((volume: number) => {
    audioEngineRef.current?.updateConfig({ volume: volume / 100 });
    contextManagerRef.current?.updateUserPreferences({ volume: volume / 100 });
  }, []);

  const setIntensity = useCallback((intensity: 'subtle' | 'normal' | 'pronounced') => {
    animationEngineRef.current?.updateConfig({ intensity });
    contextManagerRef.current?.updateUserPreferences({ intensity });
  }, []);

  const setAccessibilityMode = useCallback((enabled: boolean) => {
    animationEngineRef.current?.updateConfig({ accessibilityMode: enabled });
  }, []);

  // Analytics functions
  const getTypingMetrics = useCallback(() => {
    return contextManagerRef.current?.getTypingMetrics() || {};
  }, []);

  const getContextInsights = useCallback(() => {
    return contextManagerRef.current?.getContextInsights() || {};
  }, []);

  const recordFeedback = useCallback((feedback: any) => {
    contextManagerRef.current?.recordUserFeedback(feedback);
  }, []);

  // Get available options
  const getAvailableSoundProfiles = useCallback(() => {
    return audioEngineRef.current?.getAvailableProfiles() || [];
  }, []);

  const getAvailableAnimationProfiles = useCallback(() => {
    return animationEngineRef.current?.getAvailableProfiles() || [];
  }, []);

  const contextValue: TypingExperienceContextType = {
    playKeySound,
    playClickSound,
    playBackspaceSound,
    playCompletionSound,
    animateElement,
    setSoundProfile,
    setAnimationProfile,
    setVolume,
    setIntensity,
    setAccessibilityMode,
    isSoundEnabled,
    isAnimationEnabled,
    currentSoundProfile,
    currentAnimationProfile,
    currentContext: currentContext || {} as TypingContext,
    getTypingMetrics,
    getContextInsights,
    recordFeedback,
    getAvailableSoundProfiles,
    getAvailableAnimationProfiles,
  };

  return (
    <TypingExperienceContext.Provider value={contextValue}>
      {children}
    </TypingExperienceContext.Provider>
  );
}
