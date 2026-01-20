"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Testimonial {
    quote: string;
    name: string;
    role: string;
    initials: string;
}

const TESTIMONIALS: Testimonial[] = [
    {
        quote: "I went from random posting to a real strategy in one afternoon. This is what founder marketing should feel like.",
        name: "Sarah Chen",
        role: "Founder, ProductLabs",
        initials: "SC"
    },
    {
        quote: "RaptorFlow replaced Notion, Buffer, and ChatGPT for me. The weekly Moves alone save me 5 hours.",
        name: "Marcus Rodriguez",
        role: "CEO, Clarity AI",
        initials: "MR"
    },
    {
        quote: "Finally understand what's driving pipeline vs. what's just vanity metrics. Game changer.",
        name: "Emma Thompson",
        role: "Founder, DesignPro",
        initials: "ET"
    },
    {
        quote: "The cognitive onboarding blew my mind. It understood my positioning better than I did.",
        name: "Alex Kim",
        role: "CEO, DevScale",
        initials: "AK"
    },
    {
        quote: "Marketing finally feels like a system, not chaos. My team actually knows what to do now.",
        name: "Priya Sharma",
        role: "Founder, DataNest",
        initials: "PS"
    }
];

interface CardTransform {
    rotateX: number;
    rotateY: number;
    glowX: number;
    glowY: number;
}

function LiquidCard({
    testimonial,
    isActive
}: {
    testimonial: Testimonial;
    isActive: boolean;
}) {
    const cardRef = useRef<HTMLDivElement>(null);
    const [transform, setTransform] = useState<CardTransform>({
        rotateX: 0,
        rotateY: 0,
        glowX: 50,
        glowY: 50
    });

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!cardRef.current) return;

        const rect = cardRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        // Calculate rotation (max 10 degrees)
        const rotateX = ((y - centerY) / centerY) * -8;
        const rotateY = ((x - centerX) / centerX) * 8;

        // Calculate glow position
        const glowX = (x / rect.width) * 100;
        const glowY = (y / rect.height) * 100;

        setTransform({ rotateX, rotateY, glowX, glowY });
    };

    const handleMouseLeave = () => {
        setTransform({ rotateX: 0, rotateY: 0, glowX: 50, glowY: 50 });
    };

    return (
        <motion.div
            ref={cardRef}
            className="relative cursor-pointer perspective-1000"
            initial={{ opacity: 0, y: 30 }}
            animate={{
                opacity: isActive ? 1 : 0,
                y: isActive ? 0 : 30,
                scale: isActive ? 1 : 0.95,
            }}
            exit={{ opacity: 0, y: -30, scale: 0.95 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{
                transform: `perspective(1000px) rotateX(${transform.rotateX}deg) rotateY(${transform.rotateY}deg)`,
                transformStyle: "preserve-3d",
                transition: "transform 0.1s ease-out",
            }}
        >
            {/* Ambient glow */}
            <div
                className="absolute -inset-1 rounded-3xl opacity-50 blur-xl transition-opacity duration-300"
                style={{
                    background: `radial-gradient(circle at ${transform.glowX}% ${transform.glowY}%, rgba(224, 141, 121, 0.4), rgba(140, 169, 179, 0.2), transparent 60%)`,
                }}
            />

            {/* Card */}
            <div className="relative p-10 md:p-12 rounded-3xl border border-[var(--glass-border)] bg-gradient-to-br from-white/80 via-white/60 to-white/40 backdrop-blur-xl shadow-2xl overflow-hidden">
                {/* Shimmer effect */}
                <div
                    className="absolute inset-0 opacity-30"
                    style={{
                        background: `linear-gradient(135deg, transparent 40%, rgba(255,255,255,0.8) 50%, transparent 60%)`,
                        backgroundPosition: `${transform.glowX * 3}% 50%`,
                        transition: "background-position 0.3s ease-out",
                    }}
                />

                {/* Content */}
                <div className="relative z-10">
                    {/* Quote mark */}
                    <div className="absolute -top-2 -left-2 text-6xl font-editorial text-[var(--rf-coral)] opacity-20">
                        "
                    </div>

                    <p className="text-xl md:text-2xl leading-relaxed text-[var(--ink)] font-medium mb-8 relative z-10">
                        {testimonial.quote}
                    </p>

                    <div className="flex items-center gap-4">
                        {/* Floating avatar with parallax */}
                        <motion.div
                            className="w-14 h-14 rounded-full bg-gradient-to-br from-[var(--rf-coral)] to-[var(--rf-ocean)] flex items-center justify-center text-white font-bold text-lg shadow-lg"
                            style={{
                                transform: `translateX(${transform.rotateY * 0.5}px) translateY(${transform.rotateX * -0.5}px)`,
                                transition: "transform 0.2s ease-out",
                            }}
                        >
                            {testimonial.initials}
                        </motion.div>

                        <div>
                            <p className="font-bold text-[var(--ink)]">{testimonial.name}</p>
                            <p className="text-sm text-[var(--muted)]">{testimonial.role}</p>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

export default function LiquidTestimonials() {
    const [activeIndex, setActiveIndex] = useState(0);
    const [isPaused, setIsPaused] = useState(false);

    // Auto-cycle testimonials
    useEffect(() => {
        if (isPaused) return;

        const interval = setInterval(() => {
            setActiveIndex((prev) => (prev + 1) % TESTIMONIALS.length);
        }, 5000);

        return () => clearInterval(interval);
    }, [isPaused]);

    return (
        <div
            className="relative max-w-3xl mx-auto"
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
        >
            {/* Main card area */}
            <div className="relative min-h-[320px] flex items-center justify-center">
                <AnimatePresence mode="wait">
                    <LiquidCard
                        key={activeIndex}
                        testimonial={TESTIMONIALS[activeIndex]}
                        isActive={true}
                    />
                </AnimatePresence>
            </div>

            {/* Navigation dots */}
            <div className="flex justify-center gap-3 mt-8">
                {TESTIMONIALS.map((_, i) => (
                    <button
                        key={i}
                        onClick={() => setActiveIndex(i)}
                        className="group relative p-2"
                    >
                        <motion.div
                            className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${i === activeIndex
                                    ? "bg-[var(--ink)]"
                                    : "bg-[var(--border)] group-hover:bg-[var(--muted)]"
                                }`}
                            animate={{
                                scale: i === activeIndex ? 1.2 : 1,
                            }}
                        />
                        {i === activeIndex && (
                            <motion.div
                                className="absolute inset-0 rounded-full border-2 border-[var(--rf-coral)]"
                                layoutId="activeIndicator"
                                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                            />
                        )}
                    </button>
                ))}
            </div>

            {/* Progress bar */}
            <div className="mt-4 h-0.5 bg-[var(--border)] rounded-full overflow-hidden max-w-xs mx-auto">
                <motion.div
                    className="h-full bg-gradient-to-r from-[var(--rf-coral)] to-[var(--rf-ocean)]"
                    initial={{ width: "0%" }}
                    animate={{ width: isPaused ? undefined : "100%" }}
                    transition={{
                        duration: isPaused ? 0 : 5,
                        ease: "linear",
                        repeat: isPaused ? 0 : Infinity,
                    }}
                    key={`${activeIndex}-${isPaused}`}
                />
            </div>
        </div>
    );
}
