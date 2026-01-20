"use client";

import React, { useState, useEffect } from "react";
import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { ArrowRight01Icon } from "hugeicons-react";

export default function ScrollProgressCTA() {
    const [isVisible, setIsVisible] = useState(false);
    const [hasScrolledPast, setHasScrolledPast] = useState(false);
    const { scrollYProgress } = useScroll();

    const progressWidth = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);

    useEffect(() => {
        const handleScroll = () => {
            const scrollY = window.scrollY;
            const windowHeight = window.innerHeight;

            // Show after scrolling past first viewport
            if (scrollY > windowHeight * 0.8) {
                setIsVisible(true);
            }

            // Hide near the bottom (footer area)
            const documentHeight = document.documentElement.scrollHeight;
            if (scrollY + windowHeight > documentHeight - 400) {
                setHasScrolledPast(true);
            } else {
                setHasScrolledPast(false);
            }
        };

        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const shouldShow = isVisible && !hasScrolledPast;

    return (
        <AnimatePresence>
            {shouldShow && (
                <motion.div
                    initial={{ y: 100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 100, opacity: 0 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
                >
                    {/* Glow effect */}
                    <motion.div
                        className="absolute -inset-2 rounded-full bg-gradient-to-r from-[var(--rf-coral)] via-[var(--rf-ocean)] to-[var(--rf-mint)] opacity-30 blur-xl"
                        animate={{
                            opacity: [0.2, 0.4, 0.2],
                            scale: [1, 1.05, 1],
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                    />

                    {/* Main container */}
                    <div className="relative bg-[var(--ink)] rounded-full px-2 py-2 shadow-2xl flex items-center gap-3">
                        {/* Progress ring */}
                        <div className="relative w-10 h-10 flex-shrink-0">
                            <svg className="w-10 h-10 -rotate-90" viewBox="0 0 40 40">
                                {/* Background circle */}
                                <circle
                                    cx="20"
                                    cy="20"
                                    r="16"
                                    fill="none"
                                    stroke="rgba(255,255,255,0.2)"
                                    strokeWidth="3"
                                />
                                {/* Progress circle */}
                                <motion.circle
                                    cx="20"
                                    cy="20"
                                    r="16"
                                    fill="none"
                                    stroke="url(#progressGradient)"
                                    strokeWidth="3"
                                    strokeLinecap="round"
                                    style={{
                                        pathLength: scrollYProgress,
                                    }}
                                    strokeDasharray="1"
                                    strokeDashoffset="0"
                                />
                                <defs>
                                    <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#E08D79" />
                                        <stop offset="50%" stopColor="#8CA9B3" />
                                        <stop offset="100%" stopColor="#A6C4B9" />
                                    </linearGradient>
                                </defs>
                            </svg>

                            {/* Center percentage */}
                            <motion.div
                                className="absolute inset-0 flex items-center justify-center text-[10px] font-mono font-bold text-white"
                            >
                                <motion.span>
                                    {Math.round(scrollYProgress.get() * 100)}%
                                </motion.span>
                            </motion.div>
                        </div>

                        {/* CTA Button */}
                        <Link
                            href="/signup"
                            className="group flex items-center gap-2 px-5 py-2.5 bg-[var(--canvas)] text-[var(--ink)] rounded-full font-semibold text-sm hover:bg-white transition-colors"
                        >
                            <span>Get Started</span>
                            {React.createElement(ArrowRight01Icon as any, {
                                className: "w-4 h-4 group-hover:translate-x-1 transition-transform"
                            })}
                        </Link>

                        {/* Close button */}
                        <button
                            onClick={() => setIsVisible(false)}
                            className="w-8 h-8 rounded-full flex items-center justify-center text-white/60 hover:text-white hover:bg-white/10 transition-colors"
                        >
                            <span className="text-lg leading-none">×</span>
                        </button>
                    </div>

                    {/* Linear progress bar */}
                    <div className="absolute -bottom-3 left-4 right-4 h-0.5 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                            className="h-full bg-gradient-to-r from-[var(--rf-coral)] via-[var(--rf-ocean)] to-[var(--rf-mint)]"
                            style={{ width: progressWidth }}
                        />
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
