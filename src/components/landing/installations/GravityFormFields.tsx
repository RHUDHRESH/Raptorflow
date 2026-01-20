"use client";

import React, { useState, useRef } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";

interface FormFieldProps {
    label: string;
    type?: string;
    placeholder?: string;
}

function GravityField({ label, type = "text", placeholder }: FormFieldProps) {
    const [isFocused, setIsFocused] = useState(false);
    const [value, setValue] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);

    const isActive = isFocused || value.length > 0;

    return (
        <div className="relative">
            {/* Floating label */}
            <motion.label
                className="absolute left-4 pointer-events-none origin-left text-[var(--muted)]"
                animate={{
                    y: isActive ? -28 : 16,
                    scale: isActive ? 0.85 : 1,
                    color: isFocused ? "var(--rf-coral)" : "var(--muted)",
                }}
                transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 25,
                }}
            >
                {label}
            </motion.label>

            {/* Input field */}
            <motion.input
                ref={inputRef}
                type={type}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                className={`
                    w-full px-4 py-4 bg-[var(--surface)] border-2 rounded-xl
                    text-[var(--ink)] outline-none transition-colors
                    ${isFocused ? "border-[var(--rf-coral)]" : "border-[var(--border)]"}
                `}
                animate={{
                    boxShadow: isFocused
                        ? "0 0 0 4px rgba(224, 141, 121, 0.15)"
                        : "0 0 0 0px rgba(224, 141, 121, 0)",
                }}
            />

            {/* Placeholder that falls away */}
            {!isActive && placeholder && (
                <motion.span
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-sm text-[var(--muted)] opacity-50"
                    initial={{ y: 0, opacity: 0.5 }}
                    animate={{ y: isFocused ? 20 : 0, opacity: isFocused ? 0 : 0.5 }}
                >
                    {placeholder}
                </motion.span>
            )}
        </div>
    );
}

function MagneticButton({ children }: { children: React.ReactNode }) {
    const buttonRef = useRef<HTMLButtonElement>(null);

    const x = useMotionValue(0);
    const y = useMotionValue(0);

    const xSpring = useSpring(x, { stiffness: 300, damping: 20 });
    const ySpring = useSpring(y, { stiffness: 300, damping: 20 });

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!buttonRef.current) return;
        const rect = buttonRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        const deltaX = (e.clientX - centerX) * 0.3;
        const deltaY = (e.clientY - centerY) * 0.3;

        x.set(deltaX);
        y.set(deltaY);
    };

    const handleMouseLeave = () => {
        x.set(0);
        y.set(0);
    };

    return (
        <motion.button
            ref={buttonRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{ x: xSpring, y: ySpring }}
            whileTap={{ scale: 0.95 }}
            className="w-full py-4 bg-[var(--ink)] text-[var(--canvas)] rounded-xl font-semibold text-lg hover:bg-[var(--ink)]/90 transition-colors"
        >
            {children}
        </motion.button>
    );
}

export default function GravityFormFields() {
    const [isSubmitted, setIsSubmitted] = useState(false);

    return (
        <div className="max-w-md mx-auto">
            <motion.div
                className="bg-[var(--canvas)] border border-[var(--border)] rounded-2xl p-8 shadow-xl"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
            >
                <h3 className="text-2xl font-editorial mb-6 text-center">
                    Start your journey
                </h3>

                <div className="space-y-8">
                    <GravityField
                        label="Your name"
                        placeholder="e.g. Priya"
                    />
                    <GravityField
                        label="Email address"
                        type="email"
                        placeholder="e.g. hello@startup.com"
                    />
                    <GravityField
                        label="Company name"
                        placeholder="Your startup"
                    />

                    <MagneticButton>
                        Get Started →
                    </MagneticButton>
                </div>

                <p className="mt-6 text-center text-sm text-[var(--muted)]">
                    No commitment required. Setup takes 20 minutes.
                </p>
            </motion.div>
        </div>
    );
}
