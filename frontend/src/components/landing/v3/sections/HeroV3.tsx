"use client";

import React, { useEffect, useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { ArchButton } from "../ui/ArchButton";

export function HeroV3() {
    const containerRef = useRef<HTMLDivElement>(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end start"],
    });

    const yText = useTransform(scrollYProgress, [0, 1], [0, 100]);
    const opacityText = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

    return (
        <section
            ref={containerRef}
            className="relative min-h-[90vh] flex flex-col border-b border-white/10 bg-[#050505] overflow-hidden"
        >
            {/* BACKGROUND GRID (Subtle) */}
            <div className="absolute inset-0 pointer-events-none opacity-[0.05]"
                style={{
                    backgroundImage: `linear-gradient(to right, #333 1px, transparent 1px), linear-gradient(to bottom, #333 1px, transparent 1px)`,
                    backgroundSize: '80px 80px'
                }}
            />

            {/* MAIN CONTENT AREA - Fills available space */}
            <div className="flex-1 flex flex-col items-center justify-center relative z-10 px-4 md:px-0">

                {/* 
                   MASSIVE HEADLINE 
                   Using clamp() to ensure it breaks boundaries on large screens but fits on small.
                   Leading is negative to tighten the block.
                */}
                <motion.h1
                    style={{ y: yText, opacity: opacityText }}
                    className="text-[12vw] md:text-[8rem] lg:text-[10rem] font-bold leading-[0.85] tracking-tighter text-center uppercase mix-blend-difference"
                >
                    <span className="block text-white">System</span>
                    <span className="block text-[#333]">Online</span>
                </motion.h1>

                {/* Floating "Stamp" or Subtext */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5, duration: 0.8 }}
                    className="mt-8 md:mt-12 max-w-xl text-center"
                >
                    <p className="font-mono text-sm md:text-base text-white/70 uppercase tracking-widest">
                        The Operating System for Founder-Led Growth.
                    </p>
                </motion.div>
            </div>

            {/* BOTTOM BAR - 2 Columns */}
            <div className="h-20 md:h-24 w-full border-t border-white/10 flex">

                {/* LEFT: STATUS */}
                <div className="flex-1 flex items-center justify-start px-6 md:px-12 border-r border-white/10 bg-[#0A0A0A]">
                    <div className="flex items-center gap-3">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                        <span className="font-mono text-xs text-white/50 tracking-widest uppercase">
                            Operational
                        </span>
                    </div>
                </div>

                {/* RIGHT: CTA */}
                <div className="flex-1 flex items-center justify-end px-6 md:px-12 bg-white hover:bg-[#FAFAFA] transition-colors cursor-pointer group relative overflow-hidden">
                    <div className="absolute inset-0 bg-black translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />

                    <span className="relative z-10 font-bold text-black group-hover:text-white text-lg md:text-xl uppercase tracking-tight transition-colors duration-300">
                        Start Trial
                    </span>
                    <span className="relative z-10 ml-2 text-black group-hover:text-white transition-colors duration-300">
                        →
                    </span>
                </div>
            </div>
        </section>
    );
}
