"use client";

import React, { useRef, useEffect, ReactNode } from "react";
import { motion, useInView } from "framer-motion";
import { fadeUp, staggerContainer } from "../animations/presets";

// ═══════════════════════════════════════════════════════════════
// SectionWrapper - Consistent section structure with scroll reveal
// ═══════════════════════════════════════════════════════════════

interface SectionWrapperProps {
    children: ReactNode;
    className?: string;
    id?: string;
    /** Background variant */
    variant?: "default" | "surface" | "dark" | "accent";
    /** Padding variant */
    padding?: "normal" | "large" | "hero";
    /** Whether to add border top/bottom */
    bordered?: boolean;
}

const variantStyles: Record<string, string> = {
    default: "bg-[var(--canvas)]",
    surface: "bg-[var(--surface)]",
    dark: "bg-[var(--ink)] text-[var(--canvas)]",
    accent: "bg-[var(--accent)]/5",
};

const paddingStyles: Record<string, string> = {
    normal: "py-24 md:py-32",
    large: "py-32 md:py-40",
    hero: "min-h-screen flex items-center py-20",
};

export function SectionWrapper({
    children,
    className = "",
    id,
    variant = "default",
    padding = "normal",
    bordered = false,
}: SectionWrapperProps) {
    const ref = useRef<HTMLElement>(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });

    return (
        <section
            ref={ref}
            id={id}
            className={`
        relative overflow-hidden
        ${variantStyles[variant]}
        ${paddingStyles[padding]}
        ${bordered ? "border-y border-[var(--border)]" : ""}
        ${className}
      `}
        >
            <motion.div
                initial="hidden"
                animate={isInView ? "visible" : "hidden"}
                variants={staggerContainer}
                className="relative z-10"
            >
                {children}
            </motion.div>
        </section>
    );
}

// ═══════════════════════════════════════════════════════════════
// SectionHeader - Consistent section headers
// ═══════════════════════════════════════════════════════════════

interface SectionHeaderProps {
    eyebrow?: string;
    title: ReactNode;
    subtitle?: string;
    centered?: boolean;
    className?: string;
}

export function SectionHeader({
    eyebrow,
    title,
    subtitle,
    centered = false,
    className = "",
}: SectionHeaderProps) {
    return (
        <motion.div
            variants={fadeUp}
            className={`
        max-w-3xl mb-16 md:mb-20
        ${centered ? "mx-auto text-center" : ""}
        ${className}
      `}
        >
            {eyebrow && (
                <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">
                    {eyebrow}
                </p>
            )}
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-editorial leading-[1.1] mb-6">
                {title}
            </h2>
            {subtitle && (
                <p className="text-lg md:text-xl text-[var(--secondary)] leading-relaxed">
                    {subtitle}
                </p>
            )}
        </motion.div>
    );
}

// ═══════════════════════════════════════════════════════════════
// ContentContainer - Max-width container
// ═══════════════════════════════════════════════════════════════

interface ContentContainerProps {
    children: ReactNode;
    className?: string;
    size?: "sm" | "md" | "lg" | "xl" | "full";
}

const sizeStyles: Record<string, string> = {
    sm: "max-w-2xl",
    md: "max-w-4xl",
    lg: "max-w-6xl",
    xl: "max-w-7xl",
    full: "max-w-none",
};

export function ContentContainer({
    children,
    className = "",
    size = "xl",
}: ContentContainerProps) {
    return (
        <div className={`mx-auto px-6 ${sizeStyles[size]} ${className}`}>
            {children}
        </div>
    );
}
