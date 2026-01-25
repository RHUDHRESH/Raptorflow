"use client";

import React, { useState } from "react";
import { motion, AnimatePresence, PanInfo } from "framer-motion";
import {
    Target,
    Mic,
    Calendar,
    TrendingUp,
    Archive
} from "lucide-react";

interface FeatureCard {
    title: string;
    description: string;
    Icon: any;
    gradient: string;
}

const CARDS: FeatureCard[] = [
    {
        title: "Foundation",
        description: "Define your ICP, positioning, and voice in 20 minutes. The strategic bedrock everything else builds on.",
        Icon: Target,
        gradient: "from-[var(--rf-coral)] to-orange-400"
    },
    {
        title: "Muse AI",
        description: "Train the AI on your voice. It learns how you write, what you care about, and generates content that sounds like you.",
        Icon: Mic,
        gradient: "from-[var(--rf-ocean)] to-blue-400"
    },
    {
        title: "Weekly Moves",
        description: "Get ready-to-ship content packets every Monday. LinkedIn posts, tweets, emails—all aligned to your strategy.",
        Icon: Calendar,
        gradient: "from-[var(--rf-mint)] to-green-400"
    },
    {
        title: "Matrix Analytics",
        description: "See what's working. Track impressions, engagement, and pipeline impact across all your channels.",
        Icon: TrendingUp,
        gradient: "from-[var(--rf-violet)] to-purple-400"
    },
    {
        title: "Blackbox Vault",
        description: "Your institutional memory. Every Move, insight, and winning hook stored and searchable forever.",
        Icon: Archive,
        gradient: "from-[var(--rf-sage)] to-yellow-400"
    }
];

export default function StackedDeckCards() {
    const [cards, setCards] = useState(CARDS);
    const [exitDirection, setExitDirection] = useState(1);

    const handleDragEnd = (info: PanInfo) => {
        const threshold = 100;
        if (Math.abs(info.offset.x) > threshold) {
            setExitDirection(info.offset.x > 0 ? 1 : -1);
            // Move top card to bottom
            setCards(prev => {
                const [first, ...rest] = prev;
                return [...rest, first];
            });
        }
    };

    const handleClick = () => {
        setExitDirection(1);
        setCards(prev => {
            const [first, ...rest] = prev;
            return [...rest, first];
        });
    };

    return (
        <div className="relative h-[450px] w-full max-w-md mx-auto">
            {/* Card hint */}
            <div className="absolute -top-10 left-1/2 -translate-x-1/2 text-sm text-[var(--muted)] flex items-center gap-2">
                <span>Swipe or click to explore</span>
                <motion.span
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                >
                    →
                </motion.span>
            </div>

            {/* Stacked cards */}
            <AnimatePresence mode="popLayout">
                {cards.map((card, index) => {
                    const isTop = index === 0;
                    const offset = index * 8;
                    const scale = 1 - index * 0.05;
                    const opacity = 1 - index * 0.15;

                    return (
                        <motion.div
                            key={card.title}
                            layout
                            initial={{ scale: 0.9, y: 50, opacity: 0 }}
                            animate={{
                                scale,
                                y: offset,
                                opacity: Math.max(opacity, 0.4),
                                rotateZ: isTop ? 0 : (index % 2 === 0 ? 2 : -2),
                            }}
                            exit={{
                                x: exitDirection * 300,
                                opacity: 0,
                                rotateZ: exitDirection * 20,
                                scale: 0.8,
                            }}
                            transition={{
                                type: "spring",
                                stiffness: 300,
                                damping: 25,
                            }}
                            drag={isTop ? "x" : false}
                            dragConstraints={{ left: 0, right: 0 }}
                            onDragEnd={(_, info) => isTop && handleDragEnd(info)}
                            onClick={isTop ? handleClick : undefined}
                            className={`
                                absolute inset-0 cursor-${isTop ? "grab" : "default"}
                                active:cursor-grabbing
                            `}
                            style={{ zIndex: CARDS.length - index }}
                        >
                            <div className="h-full bg-[var(--canvas)] border border-[var(--border)] rounded-2xl p-8 shadow-xl flex flex-col">
                                {/* Icon */}
                                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${card.gradient} flex items-center justify-center mb-6`}>
                                    {React.createElement(card.Icon, {
                                        className: "w-8 h-8 text-white"
                                    })}
                                </div>

                                {/* Content */}
                                <h3 className="text-2xl font-bold mb-3">{card.title}</h3>
                                <p className="text-[var(--secondary)] leading-relaxed flex-grow">
                                    {card.description}
                                </p>

                                {/* Card number */}
                                <div className="mt-6 pt-4 border-t border-[var(--border)] flex justify-between items-center">
                                    <span className="text-sm text-[var(--muted)]">
                                        {cards.indexOf(card) + 1} of {CARDS.length}
                                    </span>
                                    {isTop && (
                                        <motion.span
                                            animate={{ x: [0, 3, 0] }}
                                            transition={{ duration: 1, repeat: Infinity }}
                                            className="text-sm text-[var(--muted)]"
                                        >
                                            Swipe →
                                        </motion.span>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </AnimatePresence>

            {/* Navigation dots */}
            <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 flex gap-2">
                {CARDS.map((card, i) => (
                    <div
                        key={card.title}
                        className={`w-2 h-2 rounded-full transition-all ${cards[0].title === card.title
                                ? "bg-[var(--ink)] w-6"
                                : "bg-[var(--border)]"
                            }`}
                    />
                ))}
            </div>
        </div>
    );
}
