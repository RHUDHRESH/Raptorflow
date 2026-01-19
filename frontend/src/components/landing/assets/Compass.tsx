"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";

export function Compass() {
    const ref = useRef<HTMLDivElement>(null);
    const [isHovered, setIsHovered] = useState(false);

    // Mouse position tracking
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!ref.current) return;
        const rect = ref.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        mouseX.set(e.clientX - centerX);
        mouseY.set(e.clientY - centerY);
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
        mouseX.set(0);
        mouseY.set(0);
    };

    // Smooth spring animation for the tilt effect
    const rotateX = useSpring(useTransform(mouseY, [-200, 200], [15, -15]), { stiffness: 150, damping: 20 });
    const rotateY = useSpring(useTransform(mouseX, [-200, 200], [-15, 15]), { stiffness: 150, damping: 20 });

    // Needle rotation acts like a real compass, slightly lagging and pointing to "True North" (up)
    // but influenced by mouse magnetic pull
    const needleRotate = useSpring(useTransform(mouseX, [-300, 300], [-45, 45]), { stiffness: 50, damping: 10 });

    return (
        <motion.div
            ref={ref}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
            style={{
                rotateX,
                rotateY,
                transformStyle: "preserve-3d"
            }}
            className="w-[300px] h-[300px] md:w-[400px] md:h-[400px] relative flex items-center justify-center"
        >
            {/* Outer Ring - Brushed Metal Look */}
            <div className="absolute inset-0 rounded-full border border-[var(--border)] bg-[var(--surface)]/50 backdrop-blur-sm shadow-2xl"
                style={{ transform: "translateZ(-20px)" }}>
                <div className="absolute inset-2 rounded-full border border-[var(--border)] opacity-50" />
            </div>

            {/* Inner Ring with Ticks */}
            <div className="absolute inset-8 rounded-full border border-[var(--border)] bg-[var(--canvas)] flex items-center justify-center shadow-inner"
                style={{ transform: "translateZ(0px)" }}>

                {/* Degree Ticks */}
                {[...Array(12)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute w-1 h-3 bg-[var(--border)] origin-bottom"
                        style={{
                            top: "10px",
                            left: "50%",
                            transform: `translateX(-50%) rotate(${i * 30}deg) translateY(130px)` // Approx radius placement
                        }}
                    />
                ))}

                {/* Cardinal Points */}
                <span className="absolute top-4 font-mono text-[var(--accent)] text-xs font-bold tracking-widest">N</span>
                <span className="absolute bottom-4 font-mono text-[var(--muted)] text-xs tracking-widest">S</span>
                <span className="absolute left-4 font-mono text-[var(--muted)] text-xs tracking-widest">W</span>
                <span className="absolute right-4 font-mono text-[var(--muted)] text-xs tracking-widest">E</span>

                {/* Central Pivot */}
                <div className="w-4 h-4 rounded-full bg-[var(--ink)] z-20 shadow-lg relative">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 bg-[var(--accent)] rounded-full" />
                </div>
            </div>

            {/* The Needle - The Hero */}
            <motion.div
                style={{ rotate: needleRotate, transform: "translateZ(30px)" }}
                className="absolute w-2 h-48 z-10 pointer-events-none"
            >
                {/* North Half */}
                <div className="absolute top-0 left-0 w-full h-1/2 bg-[var(--ink)] clip-path-needle-north"
                    style={{ clipPath: "polygon(50% 0%, 0% 100%, 100% 100%)" }}
                />
                {/* South Half */}
                <div className="absolute bottom-0 left-0 w-full h-1/2 bg-[var(--accent)] clip-path-needle-south"
                    style={{ clipPath: "polygon(50% 100%, 0% 0%, 100% 0%)" }}
                />
            </motion.div>

            {/* Glass Cover Reflection */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-white/10 to-transparent pointer-events-none"
                style={{ transform: "translateZ(40px)" }} />
        </motion.div>
    );
}
