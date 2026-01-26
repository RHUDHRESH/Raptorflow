"use client";

import React, { useRef, useState } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
import { CheckCircle } from "lucide-react";

interface Benefit {
    title: string;
    desc: string;
}

const BENEFITS: Benefit[] = [
    { title: "Save 10+ hours per week", desc: "Stop context-switching between tools. Everything lives in one place." },
    { title: "Ship content that converts", desc: "No more guessing what to post. Every Move is backed by your strategy." },
    { title: "Know what's working", desc: "Real attribution, not vanity metrics. See the full pipeline picture." },
    { title: "Build institutional memory", desc: "Every experiment, every outcome. Never repeat the same mistakes." }
];

function MagneticCard({ benefit, index }: { benefit: Benefit; index: number }) {
    const cardRef = useRef<HTMLDivElement>(null);
    const [isHovered, setIsHovered] = useState(false);

    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    const springConfig = { stiffness: 150, damping: 15, mass: 0.1 };
    const x = useSpring(mouseX, springConfig);
    const y = useSpring(mouseY, springConfig);

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        // Magnetic pull towards cursor (max 15px)
        const deltaX = (e.clientX - centerX) * 0.15;
        const deltaY = (e.clientY - centerY) * 0.15;

        mouseX.set(deltaX);
        mouseY.set(deltaY);
    };

    const handleMouseLeave = () => {
        mouseX.set(0);
        mouseY.set(0);
        setIsHovered(false);
    };

    // Alternating gradient colors
    const gradients = [
        "from-[var(--rf-coral)] to-[var(--rf-peach)]",
        "from-[var(--rf-ocean)] to-[var(--rf-mint)]",
        "from-[var(--rf-mint)] to-[var(--rf-sage)]",
        "from-[var(--rf-violet)] to-[var(--rf-lavender)]"
    ];

    return (
        <motion.div
            ref={cardRef}
            className="relative"
            style={{ x, y }}
            initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1, type: "spring" }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
        >
            {/* Animated background glow */}
            <motion.div
                className={`absolute -inset-1 rounded-2xl bg-gradient-to-r ${gradients[index]} opacity-0 blur-xl transition-opacity duration-500`}
                animate={{ opacity: isHovered ? 0.4 : 0 }}
            />

            <motion.div
                className="relative flex gap-4 p-6 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm overflow-hidden"
                animate={{
                    borderColor: isHovered ? "rgba(255, 255, 255, 0.25)" : "rgba(255, 255, 255, 0.1)",
                    background: isHovered ? "rgba(255, 255, 255, 0.08)" : "rgba(255, 255, 255, 0.05)"
                }}
                transition={{ duration: 0.3 }}
            >
                {/* Animated shine effect */}
                <motion.div
                    className="absolute inset-0 opacity-0"
                    animate={{
                        opacity: isHovered ? 1 : 0,
                        background: isHovered
                            ? "linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.1) 45%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 55%, transparent 60%)"
                            : "none",
                        backgroundPosition: isHovered ? "200% 0" : "-100% 0"
                    }}
                    transition={{ duration: 0.8 }}
                    style={{ backgroundSize: "200% 100%" }}
                />

                {/* Icon */}
                <motion.div
                    className="flex-shrink-0 mt-1"
                    animate={{
                        scale: isHovered ? 1.2 : 1,
                        rotate: isHovered ? 360 : 0
                    }}
                    transition={{ type: "spring", stiffness: 200 }}
                >
                    <CheckCircle className={`w-6 h-6 transition-colors duration-300 ${isHovered ? "text-[var(--rf-coral)]" : "text-[var(--canvas)]"}`} />
                </motion.div>

                {/* Content */}
                <div className="relative z-10">
                    <motion.h3
                        className="text-xl font-bold mb-2 text-[var(--canvas)]"
                        animate={{ x: isHovered ? 4 : 0 }}
                        transition={{ type: "spring", stiffness: 300 }}
                    >
                        {benefit.title}
                    </motion.h3>
                    <motion.p
                        className="text-[var(--canvas)]/70"
                        animate={{ x: isHovered ? 4 : 0 }}
                        transition={{ type: "spring", stiffness: 300, delay: 0.05 }}
                    >
                        {benefit.desc}
                    </motion.p>
                </div>

                {/* Corner accent */}
                <motion.div
                    className={`absolute -bottom-10 -right-10 w-24 h-24 rounded-full bg-gradient-to-r ${gradients[index]} opacity-0`}
                    animate={{
                        opacity: isHovered ? 0.2 : 0,
                        scale: isHovered ? 1.2 : 1
                    }}
                    transition={{ duration: 0.4 }}
                />
            </motion.div>
        </motion.div>
    );
}

export default function MagneticBenefits() {
    return (
        <div className="grid md:grid-cols-2 gap-8">
            {BENEFITS.map((benefit, i) => (
                <MagneticCard key={i} benefit={benefit} index={i} />
            ))}
        </div>
    );
}
