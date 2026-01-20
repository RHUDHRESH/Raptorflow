"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

// ═══════════════════════════════════════════════════════════════════════════════
// 1. TYPEWRITER HEADLINE - Types out text character by character
// ═══════════════════════════════════════════════════════════════════════════════
export function TypewriterText({
    text,
    className = "",
    speed = 50,
    delay = 0
}: {
    text: string;
    className?: string;
    speed?: number;
    delay?: number;
}) {
    const [displayText, setDisplayText] = useState("");
    const [isComplete, setIsComplete] = useState(false);

    useEffect(() => {
        const timeout = setTimeout(() => {
            let i = 0;
            const interval = setInterval(() => {
                if (i < text.length) {
                    setDisplayText(text.slice(0, i + 1));
                    i++;
                } else {
                    clearInterval(interval);
                    setIsComplete(true);
                }
            }, speed);
            return () => clearInterval(interval);
        }, delay);
        return () => clearTimeout(timeout);
    }, [text, speed, delay]);

    return (
        <span className={className}>
            {displayText}
            {!isComplete && (
                <motion.span
                    animate={{ opacity: [1, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                    className="inline-block w-[3px] h-[1em] bg-current ml-1 align-middle"
                />
            )}
        </span>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 2. ANIMATED COUNTER - Counts up to a number
// ═══════════════════════════════════════════════════════════════════════════════
export function AnimatedCounter({
    end,
    duration = 2000,
    prefix = "",
    suffix = ""
}: {
    end: number;
    duration?: number;
    prefix?: string;
    suffix?: string;
}) {
    const [count, setCount] = useState(0);
    const ref = useRef<HTMLSpanElement>(null);
    const [hasAnimated, setHasAnimated] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !hasAnimated) {
                    setHasAnimated(true);
                    const startTime = Date.now();
                    const animate = () => {
                        const elapsed = Date.now() - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        // Easing function for smooth finish
                        const eased = 1 - Math.pow(1 - progress, 3);
                        setCount(Math.floor(eased * end));
                        if (progress < 1) requestAnimationFrame(animate);
                    };
                    animate();
                }
            },
            { threshold: 0.5 }
        );
        if (ref.current) observer.observe(ref.current);
        return () => observer.disconnect();
    }, [end, duration, hasAnimated]);

    return <span ref={ref}>{prefix}{count}{suffix}</span>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// 3. FLOATING EMOJI - Randomly floating emojis
// ═══════════════════════════════════════════════════════════════════════════════
export function FloatingEmojis({ emojis = ["🚀", "✨", "💡", "🎯", "⚡"] }: { emojis?: string[] }) {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {emojis.map((emoji, i) => (
                <motion.span
                    key={i}
                    className="absolute text-2xl opacity-20"
                    initial={{
                        x: `${10 + (i * 20)}%`,
                        y: `${20 + (i * 15)}%`,
                    }}
                    animate={{
                        y: [`${20 + (i * 15)}%`, `${15 + (i * 15)}%`, `${20 + (i * 15)}%`],
                        rotate: [0, 10, -10, 0],
                    }}
                    transition={{
                        duration: 4 + i,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                >
                    {emoji}
                </motion.span>
            ))}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 4. CONFETTI BURST - Celebration on click
// ═══════════════════════════════════════════════════════════════════════════════
export function ConfettiBurst({ trigger }: { trigger: boolean }) {
    const colors = ["#E08D79", "#8CA9B3", "#A6C4B9", "#B8A9C9", "#F5D6BA"];
    const particles = Array.from({ length: 30 });

    return (
        <AnimatePresence>
            {trigger && (
                <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
                    {particles.map((_, i) => (
                        <motion.div
                            key={i}
                            initial={{
                                x: "50vw",
                                y: "50vh",
                                scale: 0,
                            }}
                            animate={{
                                x: `${Math.random() * 100}vw`,
                                y: `${Math.random() * 100}vh`,
                                scale: [0, 1, 0],
                                rotate: Math.random() * 720,
                            }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 1.5, ease: "easeOut" }}
                            className="absolute w-3 h-3 rounded-full"
                            style={{ backgroundColor: colors[i % colors.length] }}
                        />
                    ))}
                </div>
            )}
        </AnimatePresence>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 5. WITTY TOOLTIP - Playful tooltips with personality
// ═══════════════════════════════════════════════════════════════════════════════
export function WittyTooltip({
    children,
    message,
    position = "top"
}: {
    children: React.ReactNode;
    message: string;
    position?: "top" | "bottom";
}) {
    const [isVisible, setIsVisible] = useState(false);

    return (
        <div
            className="relative inline-block"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
        >
            {children}
            <AnimatePresence>
                {isVisible && (
                    <motion.div
                        initial={{ opacity: 0, y: position === "top" ? 5 : -5, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: position === "top" ? 5 : -5, scale: 0.95 }}
                        className={`
                            absolute left-1/2 -translate-x-1/2 px-3 py-2 
                            bg-[var(--ink)] text-[var(--canvas)] text-xs rounded-lg
                            whitespace-nowrap z-50 font-medium
                            ${position === "top" ? "bottom-full mb-2" : "top-full mt-2"}
                        `}
                    >
                        {message}
                        <div
                            className={`
                                absolute left-1/2 -translate-x-1/2 w-2 h-2 
                                bg-[var(--ink)] rotate-45
                                ${position === "top" ? "top-full -mt-1" : "bottom-full -mb-1"}
                            `}
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 6. MOOD INDICATOR - Shows time-based greeting
// ═══════════════════════════════════════════════════════════════════════════════
export function MoodGreeting() {
    const [greeting, setGreeting] = useState({ text: "", emoji: "" });

    useEffect(() => {
        const hour = new Date().getHours();
        if (hour < 6) setGreeting({ text: "Burning the midnight oil?", emoji: "🌙" });
        else if (hour < 12) setGreeting({ text: "Good morning, builder", emoji: "☀️" });
        else if (hour < 17) setGreeting({ text: "Afternoon productivity mode", emoji: "🚀" });
        else if (hour < 21) setGreeting({ text: "Evening grind activated", emoji: "✨" });
        else setGreeting({ text: "Late night hustle", emoji: "🌃" });
    }, []);

    return (
        <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-sm text-[var(--muted)] flex items-center gap-2"
        >
            <span>{greeting.emoji}</span>
            <span>{greeting.text}</span>
        </motion.span>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 7. EASTER EGG KONAMI CODE
// ═══════════════════════════════════════════════════════════════════════════════
export function useKonamiCode(callback: () => void) {
    const konamiCode = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a"];
    const [keys, setKeys] = useState<string[]>([]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            setKeys(prev => {
                const newKeys = [...prev, e.key].slice(-10);
                if (newKeys.join(",") === konamiCode.join(",")) {
                    callback();
                }
                return newKeys;
            });
        };
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [callback]);
}

// ═══════════════════════════════════════════════════════════════════════════════
// 8. SPARKLE TEXT - Text with floating sparkles
// ═══════════════════════════════════════════════════════════════════════════════
export function SparkleText({ children, className = "" }: { children: React.ReactNode; className?: string }) {
    return (
        <span className={`relative inline-block ${className}`}>
            {children}
            <motion.span
                className="absolute -top-1 -right-1 text-xs"
                animate={{ scale: [1, 1.2, 1], opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 1.5, repeat: Infinity }}
            >
                ✨
            </motion.span>
        </span>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 9. RANDOM QUOTE ROTATOR - Inspirational quotes
// ═══════════════════════════════════════════════════════════════════════════════
const QUOTES = [
    { text: "Ship it before it's perfect.", author: "Every successful founder" },
    { text: "Marketing is just listening at scale.", author: "The RaptorFlow Way" },
    { text: "Your competitors are posting too.", author: "Friendly reminder" },
    { text: "Done is better than perfect.", author: "Mark Zuckerberg" },
];

export function RotatingQuote() {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setIndex(i => (i + 1) % QUOTES.length);
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-center"
            >
                <p className="text-lg italic text-[var(--secondary)]">"{QUOTES[index].text}"</p>
                <p className="text-sm text-[var(--muted)] mt-1">— {QUOTES[index].author}</p>
            </motion.div>
        </AnimatePresence>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 10. WAVE HAND EMOJI - Animated waving hand
// ═══════════════════════════════════════════════════════════════════════════════
export function WavingHand() {
    return (
        <motion.span
            className="inline-block origin-bottom-right"
            animate={{ rotate: [0, 14, -8, 14, -4, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 2 }}
        >
            👋
        </motion.span>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 11. PROGRESS CELEBRATION - Celebrate milestones
// ═══════════════════════════════════════════════════════════════════════════════
export function CelebrationBadge({ message }: { message: string }) {
    return (
        <motion.div
            initial={{ scale: 0, rotate: -10 }}
            animate={{ scale: 1, rotate: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[var(--rf-coral)] to-[var(--rf-ocean)] text-white rounded-full text-sm font-medium"
        >
            <span>🎉</span>
            <span>{message}</span>
        </motion.div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 12. PERSONALITY PHRASES - Random witty microcopy
// ═══════════════════════════════════════════════════════════════════════════════
export const PERSONALITY_PHRASES = {
    loading: [
        "Brewing something good...",
        "Warming up the engines...",
        "Almost there, promise!",
        "Good things take time...",
    ],
    success: [
        "Nailed it! 🎯",
        "You're on fire! 🔥",
        "That was smooth! ✨",
        "Look at you go! 🚀",
    ],
    cta: [
        "Let's do this →",
        "Ready when you are →",
        "Your move, founder →",
        "Time to ship →",
    ],
    empty: [
        "Crickets... 🦗",
        "Nothing here yet!",
        "The stage is yours",
        "Blank canvas awaits",
    ]
};

export function getRandomPhrase(type: keyof typeof PERSONALITY_PHRASES) {
    const phrases = PERSONALITY_PHRASES[type];
    return phrases[Math.floor(Math.random() * phrases.length)];
}

// ═══════════════════════════════════════════════════════════════════════════════
// 13. SCROLL ENCOURAGEMENT - Shows when user hasn't scrolled
// ═══════════════════════════════════════════════════════════════════════════════
export function ScrollEncouragement() {
    const [show, setShow] = useState(false);
    const [dismissed, setDismissed] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            if (window.scrollY < 100 && !dismissed) setShow(true);
        }, 5000);

        const handleScroll = () => {
            if (window.scrollY > 100) {
                setShow(false);
                setDismissed(true);
            }
        };

        window.addEventListener("scroll", handleScroll);
        return () => {
            clearTimeout(timer);
            window.removeEventListener("scroll", handleScroll);
        };
    }, [dismissed]);

    return (
        <AnimatePresence>
            {show && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 20 }}
                    className="fixed bottom-20 left-1/2 -translate-x-1/2 z-40 bg-[var(--ink)] text-[var(--canvas)] px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2"
                >
                    <span>Psst... there's more below</span>
                    <motion.span animate={{ y: [0, 4, 0] }} transition={{ repeat: Infinity, duration: 1 }}>
                        👇
                    </motion.span>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
