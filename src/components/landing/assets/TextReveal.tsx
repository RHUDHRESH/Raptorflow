"use client";

import React from "react";
import { motion, type Variants } from "framer-motion";

interface TextRevealProps {
    text: string;
    className?: string;
    delay?: number;
}

/**
 * A component that reveals text character-by-character with a staggered animation.
 * Use for hero headlines that need dramatic impact.
 */
export function TextReveal({ text, className = "", delay = 0 }: TextRevealProps) {
    const words = text.split(" ");

    const container: Variants = {
        hidden: { opacity: 0 },
        visible: (i = 1) => ({
            opacity: 1,
            transition: { staggerChildren: 0.03, delayChildren: delay },
        }),
    };

    const child: Variants = {
        visible: {
            opacity: 1,
            y: 0,
            transition: {
                type: "spring",
                damping: 12,
                stiffness: 100,
            },
        },
        hidden: {
            opacity: 0,
            y: 20,
            transition: {
                type: "spring",
                damping: 12,
                stiffness: 100,
            },
        },
    };

    return (
        <motion.span
            variants={container}
            initial="hidden"
            animate="visible"
            className={`inline-block ${className}`}
        >
            {words.map((word, wordIndex) => (
                <span key={wordIndex} className="inline-block mr-[0.25em] whitespace-nowrap">
                    {word.split("").map((char, charIndex) => (
                        <motion.span
                            key={`${wordIndex}-${charIndex}`}
                            variants={child}
                            className="inline-block"
                        >
                            {char}
                        </motion.span>
                    ))}
                </span>
            ))}
        </motion.span>
    );
}

/**
 * A simpler word-by-word reveal for subtitles.
 */
export function WordReveal({ text, className = "", delay = 0 }: TextRevealProps) {
    const words = text.split(" ");

    return (
        <span className={className}>
            {words.map((word, i) => (
                <motion.span
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: delay + i * 0.05, duration: 0.4 }}
                    className="inline-block mr-[0.25em]"
                >
                    {word}
                </motion.span>
            ))}
        </span>
    );
}
