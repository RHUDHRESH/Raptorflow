"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from "framer-motion";

interface Testimonial {
    quote: string;
    author: string;
    role: string;
    avatar: string;
}

const TESTIMONIALS: Testimonial[] = [
    {
        quote: "RaptorFlow replaced our entire marketing stack. One tool, zero chaos.",
        author: "Priya Sharma",
        role: "Founder, CloudScale",
        avatar: "PS"
    },
    {
        quote: "We went from 0 to 10K followers in 8 weeks. The Moves are surgical.",
        author: "Marcus Chen",
        role: "CEO, DataFlow",
        avatar: "MC"
    },
    {
        quote: "Finally, marketing that feels like engineering. Systematic and predictable.",
        author: "Sarah Johnson",
        role: "Founder, TechLabs",
        avatar: "SJ"
    },
    {
        quote: "The Foundation module alone saved us 3 months of positioning work.",
        author: "Raj Patel",
        role: "Co-founder, FinStack",
        avatar: "RP"
    },
    {
        quote: "I actually look forward to marketing Mondays now. That's new.",
        author: "Emma Wilson",
        role: "Solo Founder, Craftly",
        avatar: "EW"
    }
];

function OrbitingTestimonial({
    testimonial,
    index,
    total,
    isCenter,
    onClick
}: {
    testimonial: Testimonial;
    index: number;
    total: number;
    isCenter: boolean;
    onClick: () => void;
}) {
    const angle = (index / total) * 360;
    const radius = 200;

    // Calculate position on orbit
    const x = Math.cos((angle * Math.PI) / 180) * radius;
    const y = Math.sin((angle * Math.PI) / 180) * radius;

    if (isCenter) {
        return (
            <motion.div
                layoutId={`testimonial-${index}`}
                className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 25 }}
            >
                <div className="bg-[var(--canvas)] border-2 border-[var(--ink)] rounded-2xl p-8 shadow-2xl max-w-md text-center">
                    <p className="text-xl font-editorial italic mb-6 leading-relaxed">
                        "{testimonial.quote}"
                    </p>
                    <div className="flex items-center justify-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[var(--rf-coral)] to-[var(--rf-ocean)] flex items-center justify-center text-white font-bold">
                            {testimonial.avatar}
                        </div>
                        <div className="text-left">
                            <p className="font-semibold">{testimonial.author}</p>
                            <p className="text-sm text-[var(--muted)]">{testimonial.role}</p>
                        </div>
                    </div>
                </div>
            </motion.div>
        );
    }

    return (
        <motion.div
            layoutId={`testimonial-${index}`}
            className="absolute cursor-pointer z-10"
            style={{
                left: `calc(50% + ${x}px)`,
                top: `calc(50% + ${y}px)`,
            }}
            animate={{
                x: "-50%",
                y: "-50%",
                rotate: [0, 360],
            }}
            transition={{
                rotate: {
                    duration: 30 + index * 5,
                    repeat: Infinity,
                    ease: "linear"
                }
            }}
            onClick={onClick}
            whileHover={{ scale: 1.1 }}
        >
            <motion.div
                animate={{ rotate: [0, -360] }}
                transition={{
                    duration: 30 + index * 5,
                    repeat: Infinity,
                    ease: "linear"
                }}
                className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-4 shadow-lg hover:border-[var(--ink)] transition-colors max-w-[180px]"
            >
                <p className="text-sm italic line-clamp-2 mb-2">"{testimonial.quote.slice(0, 50)}..."</p>
                <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[var(--rf-coral)] to-[var(--rf-ocean)] flex items-center justify-center text-white text-xs font-bold">
                        {testimonial.avatar}
                    </div>
                    <span className="text-xs text-[var(--muted)]">{testimonial.author.split(' ')[0]}</span>
                </div>
            </motion.div>
        </motion.div>
    );
}

export default function OrbitTestimonials() {
    const [centerIndex, setCenterIndex] = useState(0);
    const containerRef = useRef<HTMLDivElement>(null);

    // Auto-rotate every 6 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            setCenterIndex(prev => (prev + 1) % TESTIMONIALS.length);
        }, 6000);
        return () => clearInterval(interval);
    }, []);

    const orbitingTestimonials = TESTIMONIALS.filter((_, i) => i !== centerIndex);

    return (
        <div ref={containerRef} className="relative h-[600px] w-full flex items-center justify-center">
            {/* Orbital rings */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-[400px] h-[400px] rounded-full border border-[var(--border)] opacity-30" />
                <div className="absolute w-[500px] h-[500px] rounded-full border border-[var(--border)] border-dashed opacity-20" />
            </div>

            {/* Central testimonial */}
            <OrbitingTestimonial
                testimonial={TESTIMONIALS[centerIndex]}
                index={centerIndex}
                total={TESTIMONIALS.length}
                isCenter={true}
                onClick={() => { }}
            />

            {/* Orbiting testimonials */}
            {orbitingTestimonials.map((testimonial, i) => {
                const originalIndex = TESTIMONIALS.findIndex(t => t.author === testimonial.author);
                return (
                    <OrbitingTestimonial
                        key={testimonial.author}
                        testimonial={testimonial}
                        index={i}
                        total={orbitingTestimonials.length}
                        isCenter={false}
                        onClick={() => setCenterIndex(originalIndex)}
                    />
                );
            })}

            {/* Navigation dots */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                {TESTIMONIALS.map((_, i) => (
                    <button
                        key={i}
                        onClick={() => setCenterIndex(i)}
                        className={`w-2 h-2 rounded-full transition-all ${i === centerIndex
                                ? "bg-[var(--ink)] w-6"
                                : "bg-[var(--border)] hover:bg-[var(--muted)]"
                            }`}
                    />
                ))}
            </div>
        </div>
    );
}
