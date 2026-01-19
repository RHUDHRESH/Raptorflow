"use client";

import React, { useEffect, useState } from "react";
import { motion, useScroll, useSpring } from "framer-motion";

// ═══════════════════════════════════════════════════════════════
// ScrollProgress - Reading progress indicator
// ═══════════════════════════════════════════════════════════════

interface ScrollProgressProps {
    /** Position of the progress bar */
    position?: "top" | "bottom" | "left" | "right";
    /** Color of the progress bar */
    color?: string;
    /** Height (for top/bottom) or width (for left/right) */
    thickness?: number;
    /** Z-index */
    zIndex?: number;
    className?: string;
}

export function ScrollProgress({
    position = "top",
    color = "var(--accent)",
    thickness = 3,
    zIndex = 100,
    className = "",
}: ScrollProgressProps) {
    const { scrollYProgress } = useScroll();
    const scaleX = useSpring(scrollYProgress, {
        stiffness: 100,
        damping: 30,
        restDelta: 0.001,
    });

    const isHorizontal = position === "top" || position === "bottom";

    const positionStyles: Record<string, React.CSSProperties> = {
        top: { top: 0, left: 0, right: 0, height: thickness },
        bottom: { bottom: 0, left: 0, right: 0, height: thickness },
        left: { top: 0, left: 0, bottom: 0, width: thickness },
        right: { top: 0, right: 0, bottom: 0, width: thickness },
    };

    return (
        <motion.div
            className={`fixed ${className}`}
            style={{
                ...positionStyles[position],
                background: color,
                transformOrigin: isHorizontal ? "left" : "top",
                scaleX: isHorizontal ? scaleX : 1,
                scaleY: isHorizontal ? 1 : scaleX,
                zIndex,
            }}
        />
    );
}

// ═══════════════════════════════════════════════════════════════
// ScrollIndicator - Scroll down hint (editorial style)
// ═══════════════════════════════════════════════════════════════

interface ScrollIndicatorProps {
    label?: string;
    className?: string;
    onClick?: () => void;
}

export function ScrollIndicator({
    label = "Scroll to explore",
    className = "",
    onClick,
}: ScrollIndicatorProps) {
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        const handleScroll = () => {
            setIsVisible(window.scrollY < 100);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <motion.button
            onClick={onClick}
            initial={{ opacity: 0 }}
            animate={{ opacity: isVisible ? 1 : 0 }}
            transition={{ duration: 0.3 }}
            className={`
        flex flex-col items-center gap-3 
        text-[var(--muted)] hover:text-[var(--ink)]
        transition-colors cursor-pointer
        ${className}
      `}
        >
            <span className="text-xs uppercase tracking-[0.2em] font-medium">
                {label}
            </span>
            <motion.div
                animate={{ y: [0, 6, 0] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                className="flex flex-col items-center gap-1"
            >
                <div className="w-px h-8 bg-current opacity-30" />
                <div className="w-2 h-2 border-b border-r border-current rotate-45" />
            </motion.div>
        </motion.button>
    );
}

// ═══════════════════════════════════════════════════════════════
// SectionNav - Dot navigation for sections
// ═══════════════════════════════════════════════════════════════

interface SectionNavProps {
    sections: { id: string; label: string }[];
    activeSection?: string;
    className?: string;
}

export function SectionNav({
    sections,
    activeSection,
    className = "",
}: SectionNavProps) {
    const handleClick = (id: string) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: "smooth" });
        }
    };

    return (
        <nav
            className={`fixed right-6 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-3 ${className}`}
        >
            {sections.map((section) => (
                <button
                    key={section.id}
                    onClick={() => handleClick(section.id)}
                    className="group flex items-center gap-3"
                >
                    <span
                        className={`
              text-xs uppercase tracking-wider opacity-0 group-hover:opacity-100
              transition-opacity text-[var(--muted)]
            `}
                    >
                        {section.label}
                    </span>
                    <div
                        className={`
              w-2 h-2 rounded-full border transition-all
              ${activeSection === section.id
                                ? "bg-[var(--ink)] border-[var(--ink)] scale-125"
                                : "border-[var(--muted)] group-hover:border-[var(--ink)]"
                            }
            `}
                    />
                </button>
            ))}
        </nav>
    );
}
