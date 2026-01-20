"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion";

// ═══════════════════════════════════════════════════════════════════════════════
// 1. CURSOR SPOTLIGHT - Follows cursor with spotlight effect
// ═══════════════════════════════════════════════════════════════════════════════
export function CursorSpotlight() {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setPosition({ x: e.clientX, y: e.clientY });
            setIsVisible(true);
        };
        const handleMouseLeave = () => setIsVisible(false);

        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseleave", handleMouseLeave);
        return () => {
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseleave", handleMouseLeave);
        };
    }, []);

    return (
        <motion.div
            className="pointer-events-none fixed inset-0 z-30 opacity-20"
            animate={{ opacity: isVisible ? 0.15 : 0 }}
        >
            <div
                className="absolute w-[500px] h-[500px] rounded-full"
                style={{
                    left: position.x - 250,
                    top: position.y - 250,
                    background: "radial-gradient(circle, rgba(224,141,121,0.3) 0%, transparent 70%)",
                }}
            />
        </motion.div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 2. SCROLL REVEAL TEXT - Words highlight as you scroll
// ═══════════════════════════════════════════════════════════════════════════════
export function ScrollRevealText({ text, className = "" }: { text: string; className?: string }) {
    const ref = useRef<HTMLParagraphElement>(null);
    const { scrollYProgress } = useScroll({
        target: ref,
        offset: ["start 0.9", "end 0.5"]
    });

    const words = text.split(" ");

    return (
        <p ref={ref} className={`flex flex-wrap ${className}`}>
            {words.map((word, i) => {
                const start = i / words.length;
                const end = start + 1 / words.length;
                return (
                    <Word key={i} range={[start, end]} progress={scrollYProgress}>
                        {word}
                    </Word>
                );
            })}
        </p>
    );
}

function Word({ children, range, progress }: { children: string; range: [number, number]; progress: any }) {
    const opacity = useTransform(progress, range, [0.2, 1]);
    return (
        <motion.span style={{ opacity }} className="mr-2 mb-1 transition-colors">
            {children}
        </motion.span>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 3. GRADIENT WAVE DIVIDER - Animated section divider
// ═══════════════════════════════════════════════════════════════════════════════
export function GradientWaveDivider({ flip = false }: { flip?: boolean }) {
    return (
        <div className={`relative h-24 overflow-hidden ${flip ? "rotate-180" : ""}`}>
            <svg
                viewBox="0 0 1200 120"
                preserveAspectRatio="none"
                className="absolute w-full h-full"
            >
                <defs>
                    <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="var(--rf-coral)" stopOpacity="0.3" />
                        <stop offset="50%" stopColor="var(--rf-ocean)" stopOpacity="0.3" />
                        <stop offset="100%" stopColor="var(--rf-mint)" stopOpacity="0.3" />
                    </linearGradient>
                </defs>
                <motion.path
                    d="M0,60 C200,100 400,20 600,60 C800,100 1000,20 1200,60 L1200,120 L0,120 Z"
                    fill="url(#waveGradient)"
                    animate={{
                        d: [
                            "M0,60 C200,100 400,20 600,60 C800,100 1000,20 1200,60 L1200,120 L0,120 Z",
                            "M0,60 C200,20 400,100 600,60 C800,20 1000,100 1200,60 L1200,120 L0,120 Z",
                            "M0,60 C200,100 400,20 600,60 C800,100 1000,20 1200,60 L1200,120 L0,120 Z",
                        ]
                    }}
                    transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
                />
            </svg>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 4. STAT WITH HOVER CONTEXT - Shows additional info on hover
// ═══════════════════════════════════════════════════════════════════════════════
export function StatWithContext({
    number,
    label,
    context
}: {
    number: string;
    label: string;
    context: string;
}) {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <motion.div
            className="relative text-center cursor-default"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <motion.div
                animate={{ scale: isHovered ? 1.05 : 1 }}
                transition={{ type: "spring", stiffness: 300 }}
            >
                <p className="text-4xl font-mono font-bold text-[var(--ink)]">{number}</p>
                <p className="text-sm text-[var(--muted)] uppercase tracking-wider">{label}</p>
            </motion.div>

            <AnimatePresence>
                {isHovered && (
                    <motion.p
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 5 }}
                        className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-1.5 bg-[var(--ink)] text-[var(--canvas)] text-xs rounded-lg whitespace-nowrap z-10"
                    >
                        {context}
                    </motion.p>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 5. FUN FACTS TICKER - Scrolling fun facts
// ═══════════════════════════════════════════════════════════════════════════════
const FUN_FACTS = [
    "💡 Founders spend 15+ hours weekly on marketing—we cut that to 5",
    "🎯 Our AI trained on 10,000+ successful campaigns",
    "⚡ Average setup time: 22 minutes",
    "🚀 Users ship 3x more content per week",
    "📈 87% see pipeline growth in 6 weeks",
];

export function FunFactsTicker() {
    return (
        <div className="overflow-hidden bg-[var(--surface)] border-y border-[var(--border)] py-3">
            <motion.div
                className="flex gap-16 whitespace-nowrap"
                animate={{ x: [0, -1000] }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
                {[...FUN_FACTS, ...FUN_FACTS].map((fact, i) => (
                    <span key={i} className="text-sm text-[var(--secondary)]">
                        {fact}
                    </span>
                ))}
            </motion.div>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 6. INTERACTIVE LOGO CLICK - Logo responds to clicks
// ═══════════════════════════════════════════════════════════════════════════════
export function InteractiveLogo({ children }: { children: React.ReactNode }) {
    const [clicks, setClicks] = useState(0);
    const [message, setMessage] = useState("");

    const messages = [
        "", // 0 clicks
        "👀", // 1
        "Hey there!", // 2
        "Curious one, aren't you?", // 3
        "Keep going...", // 4
        "🎉 You found an easter egg!", // 5
    ];

    const handleClick = () => {
        const newClicks = Math.min(clicks + 1, 5);
        setClicks(newClicks);
        setMessage(messages[newClicks]);

        if (newClicks < 5) {
            setTimeout(() => setMessage(""), 2000);
        }
    };

    return (
        <div className="relative">
            <motion.div
                onClick={handleClick}
                whileTap={{ scale: 0.95, rotate: clicks === 4 ? 360 : 0 }}
                transition={{ type: "spring" }}
                className="cursor-pointer"
            >
                {children}
            </motion.div>
            <AnimatePresence>
                {message && (
                    <motion.span
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="absolute left-full ml-3 top-1/2 -translate-y-1/2 text-sm text-[var(--muted)] whitespace-nowrap"
                    >
                        {message}
                    </motion.span>
                )}
            </AnimatePresence>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 7. BREATHING DOT - Calm, breathing status indicator
// ═══════════════════════════════════════════════════════════════════════════════
export function BreathingDot({ color = "green" }: { color?: "green" | "blue" | "coral" }) {
    const colorClasses = {
        green: "bg-green-500",
        blue: "bg-[var(--rf-ocean)]",
        coral: "bg-[var(--rf-coral)]",
    };

    return (
        <span className="relative inline-flex">
            <span className={`w-2 h-2 rounded-full ${colorClasses[color]}`} />
            <motion.span
                className={`absolute inset-0 rounded-full ${colorClasses[color]}`}
                animate={{ scale: [1, 1.8, 1], opacity: [0.6, 0, 0.6] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            />
        </span>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 8. HOVER EXPAND CARD - Card expands with more info on hover
// ═══════════════════════════════════════════════════════════════════════════════
export function HoverExpandCard({
    title,
    preview,
    expanded
}: {
    title: string;
    preview: string;
    expanded: string;
}) {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <motion.div
            className="p-6 border border-[var(--border)] rounded-xl cursor-pointer overflow-hidden"
            onMouseEnter={() => setIsExpanded(true)}
            onMouseLeave={() => setIsExpanded(false)}
            animate={{ height: isExpanded ? "auto" : 120 }}
        >
            <h4 className="text-lg font-bold mb-2">{title}</h4>
            <AnimatePresence mode="wait">
                <motion.p
                    key={isExpanded ? "expanded" : "preview"}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-[var(--secondary)]"
                >
                    {isExpanded ? expanded : preview}
                </motion.p>
            </AnimatePresence>
        </motion.div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 9. KEYBOARD HINT - Shows keyboard shortcut hints
// ═══════════════════════════════════════════════════════════════════════════════
export function KeyboardHint({ keys, action }: { keys: string[]; action: string }) {
    return (
        <div className="inline-flex items-center gap-2 text-sm text-[var(--muted)]">
            <span className="flex gap-1">
                {keys.map((key, i) => (
                    <kbd
                        key={i}
                        className="px-2 py-1 bg-[var(--surface)] border border-[var(--border)] rounded text-xs font-mono"
                    >
                        {key}
                    </kbd>
                ))}
            </span>
            <span>{action}</span>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 10. LIVE ACTIVITY INDICATOR - Shows "live" activity
// ═══════════════════════════════════════════════════════════════════════════════
export function LiveActivityIndicator() {
    const [activity, setActivity] = useState("");
    const activities = [
        "Sarah just joined RaptorFlow",
        "Move #247 shipped by Marcus",
        "3 new Moves queued today",
        "Emma hit 10k impressions",
        "New Foundation completed",
    ];

    useEffect(() => {
        const showActivity = () => {
            const randomActivity = activities[Math.floor(Math.random() * activities.length)];
            setActivity(randomActivity);
            setTimeout(() => setActivity(""), 4000);
        };

        showActivity();
        const interval = setInterval(showActivity, 8000);
        return () => clearInterval(interval);
    }, []);

    return (
        <AnimatePresence>
            {activity && (
                <motion.div
                    initial={{ opacity: 0, y: 20, x: "-50%" }}
                    animate={{ opacity: 1, y: 0, x: "-50%" }}
                    exit={{ opacity: 0, y: -20, x: "-50%" }}
                    className="fixed bottom-24 left-1/2 z-40 flex items-center gap-3 px-4 py-2 bg-white/95 backdrop-blur border border-[var(--border)] rounded-full shadow-lg text-sm"
                >
                    <BreathingDot color="green" />
                    <span>{activity}</span>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
