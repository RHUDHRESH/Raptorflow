"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight01Icon } from "hugeicons-react";
import Link from "next/link";

/**
 * A floating CTA bar that appears after the user has scrolled past the hero section.
 */
export function FloatingCTA() {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            // Show after scrolling 500px (past the hero)
            setIsVisible(window.scrollY > 500);
        };

        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ y: 100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 100, opacity: 0 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
                >
                    <Link
                        href="/signup"
                        className="group flex items-center gap-3 px-6 py-3 bg-[var(--ink)] text-[var(--canvas)] rounded-full shadow-2xl shadow-[var(--ink)]/30 hover:shadow-[var(--ink)]/50 transition-all duration-300 border border-[var(--ink)]"
                    >
                        <span className="text-sm font-semibold tracking-wide">Start Free Trial</span>
                        {React.createElement(ArrowRight01Icon as any, {
                            className: "w-4 h-4 transition-transform group-hover:translate-x-1"
                        })}
                    </Link>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
