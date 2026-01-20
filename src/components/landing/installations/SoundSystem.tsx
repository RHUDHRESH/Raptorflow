"use client";

import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

// Sound URLs (using base64-encoded tiny sounds for no external deps)
const SOUNDS = {
    pop: "data:audio/wav;base64,UklGRl9vT19telephone_soundAAAAAA==", // Placeholder
    whoosh: "data:audio/wav;base64,UklGRl9vT19telephone_soundAAAAAA==",
    ding: "data:audio/wav;base64,UklGRl9vT19telephone_sound==",
    tick: "data:audio/wav;base64,UklGRl9vT19telephone_soundAAAAAA==",
};

interface SoundContextType {
    isEnabled: boolean;
    toggle: () => void;
    play: (sound: keyof typeof SOUNDS) => void;
}

const SoundContext = createContext<SoundContextType | null>(null);

export function useSoundSystem() {
    const context = useContext(SoundContext);
    if (!context) {
        return { isEnabled: false, toggle: () => { }, play: () => { } };
    }
    return context;
}

export function SoundProvider({ children }: { children: React.ReactNode }) {
    const [isEnabled, setIsEnabled] = useState(false);
    const [audioContext, setAudioContext] = useState<AudioContext | null>(null);

    useEffect(() => {
        // Initialize AudioContext on first user interaction
        const initAudio = () => {
            if (!audioContext) {
                setAudioContext(new (window.AudioContext || (window as any).webkitAudioContext)());
            }
            window.removeEventListener("click", initAudio);
        };
        window.addEventListener("click", initAudio);
        return () => window.removeEventListener("click", initAudio);
    }, [audioContext]);

    const toggle = useCallback(() => {
        setIsEnabled(prev => !prev);
    }, []);

    const play = useCallback((sound: keyof typeof SOUNDS) => {
        if (!isEnabled || !audioContext) return;

        // Create a simple oscillator for the sound effect
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        // Different sounds have different frequencies and durations
        const configs: Record<string, { freq: number; duration: number; type: OscillatorType }> = {
            pop: { freq: 600, duration: 0.05, type: "sine" },
            whoosh: { freq: 200, duration: 0.15, type: "sawtooth" },
            ding: { freq: 880, duration: 0.1, type: "sine" },
            tick: { freq: 1000, duration: 0.02, type: "square" },
        };

        const config = configs[sound] || configs.pop;

        oscillator.type = config.type;
        oscillator.frequency.setValueAtTime(config.freq, audioContext.currentTime);

        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + config.duration);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + config.duration);
    }, [isEnabled, audioContext]);

    return (
        <SoundContext.Provider value={{ isEnabled, toggle, play }}>
            {children}
        </SoundContext.Provider>
    );
}

// Sound toggle button for footer
export function SoundToggle() {
    const { isEnabled, toggle } = useSoundSystem();

    return (
        <motion.button
            onClick={toggle}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`
                flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-colors
                ${isEnabled
                    ? "bg-[var(--rf-mint)]/20 text-[var(--rf-mint)]"
                    : "bg-[var(--surface)] text-[var(--muted)] hover:text-[var(--ink)]"
                }
            `}
        >
            <motion.span
                animate={{ scale: isEnabled ? [1, 1.2, 1] : 1 }}
                transition={{ duration: 0.3 }}
            >
                {isEnabled ? "🔊" : "🔇"}
            </motion.span>
            <span>{isEnabled ? "Sound On" : "Sound Off"}</span>
        </motion.button>
    );
}

// Hook to play sound on hover
export function useSoundHover(sound: keyof typeof SOUNDS = "pop") {
    const { play } = useSoundSystem();
    return {
        onMouseEnter: () => play(sound),
    };
}
