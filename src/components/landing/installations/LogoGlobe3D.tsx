"use client";

import React, { useRef, useState, useEffect } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

const LOGOS = [
    { name: "PS", color: "from-[var(--rf-coral)] to-orange-400" },
    { name: "MC", color: "from-[var(--rf-ocean)] to-blue-400" },
    { name: "SJ", color: "from-[var(--rf-mint)] to-green-400" },
    { name: "RP", color: "from-[var(--rf-violet)] to-purple-400" },
    { name: "EW", color: "from-yellow-400 to-amber-500" },
    { name: "AK", color: "from-pink-400 to-rose-500" },
    { name: "JL", color: "from-cyan-400 to-teal-500" },
    { name: "DM", color: "from-indigo-400 to-violet-500" },
];

function OrbitingLogo({
    logo,
    index,
    total,
    radius,
    speed,
    tilt
}: {
    logo: typeof LOGOS[0];
    index: number;
    total: number;
    radius: number;
    speed: number;
    tilt: number;
}) {
    const angle = (index / total) * 360;

    return (
        <motion.div
            className="absolute left-1/2 top-1/2"
            style={{
                transformStyle: "preserve-3d",
            }}
            animate={{
                rotateY: [angle, angle + 360],
            }}
            transition={{
                duration: speed,
                repeat: Infinity,
                ease: "linear",
            }}
        >
            <motion.div
                className="absolute"
                style={{
                    transform: `translateX(-50%) translateY(-50%) translateZ(${radius}px) rotateX(${tilt}deg)`,
                }}
            >
                <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${logo.color} flex items-center justify-center text-white font-bold text-sm shadow-lg`}>
                    {logo.name}
                </div>
            </motion.div>
        </motion.div>
    );
}

export default function LogoGlobe3D() {
    const containerRef = useRef<HTMLDivElement>(null);
    const [isDragging, setIsDragging] = useState(false);

    const rotateX = useMotionValue(15);
    const rotateY = useMotionValue(0);

    const springX = useSpring(rotateX, { stiffness: 100, damping: 30 });
    const springY = useSpring(rotateY, { stiffness: 100, damping: 30 });

    // Auto-rotate when not dragging
    useEffect(() => {
        if (isDragging) return;
        const interval = setInterval(() => {
            rotateY.set(rotateY.get() + 0.5);
        }, 50);
        return () => clearInterval(interval);
    }, [isDragging, rotateY]);

    const handleMouseDown = () => setIsDragging(true);
    const handleMouseUp = () => setIsDragging(false);

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isDragging || !containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        rotateY.set((e.clientX - centerX) * 0.5);
        rotateX.set((e.clientY - centerY) * 0.3);
    };

    return (
        <div
            ref={containerRef}
            className="relative w-[400px] h-[400px] mx-auto cursor-grab active:cursor-grabbing"
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onMouseMove={handleMouseMove}
            style={{ perspective: "1000px" }}
        >
            {/* Globe container */}
            <motion.div
                className="relative w-full h-full"
                style={{
                    transformStyle: "preserve-3d",
                    rotateX: springX,
                    rotateY: springY,
                }}
            >
                {/* Center logo */}
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
                    <motion.div
                        animate={{ scale: [1, 1.05, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="w-20 h-20 rounded-2xl bg-[var(--ink)] flex items-center justify-center shadow-2xl"
                    >
                        <span className="text-white font-bold text-xl">RF</span>
                    </motion.div>
                </div>

                {/* Orbital ring visual */}
                <div
                    className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full border border-[var(--border)] opacity-30"
                    style={{ transform: "rotateX(70deg)" }}
                />

                {/* Inner orbit */}
                {LOGOS.slice(0, 4).map((logo, i) => (
                    <OrbitingLogo
                        key={logo.name}
                        logo={logo}
                        index={i}
                        total={4}
                        radius={100}
                        speed={20}
                        tilt={0}
                    />
                ))}

                {/* Outer orbit */}
                {LOGOS.slice(4).map((logo, i) => (
                    <OrbitingLogo
                        key={logo.name}
                        logo={logo}
                        index={i}
                        total={4}
                        radius={150}
                        speed={30}
                        tilt={20}
                    />
                ))}
            </motion.div>

            {/* Drag hint */}
            <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2 }}
                className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-sm text-[var(--muted)]"
            >
                Drag to rotate
            </motion.p>
        </div>
    );
}
