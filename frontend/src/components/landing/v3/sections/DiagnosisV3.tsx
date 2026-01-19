"use client";

import React from "react";
import { motion } from "framer-motion";

export function DiagnosisV3() {
    return (
        <section className="relative min-h-[80vh] flex flex-col md:flex-row bg-[#050505] border-b border-white/10 overflow-hidden">

            {/* LEFT PANE: THE CHAOS */}
            <div className="flex-1 p-12 md:p-24 border-b md:border-b-0 md:border-r border-white/10 relative">
                <div className="absolute inset-0 bg-white/5 opacity-0 md:opacity-100 mix-blend-overlay pointer-events-none" />

                <h3 className="font-mono text-xs uppercase tracking-widest text-white/50 mb-12">
                    Current_State_Log
                </h3>

                <ul className="space-y-6 font-mono text-sm md:text-base text-white/60">
                    <li className="flex gap-4 items-center">
                        <span className="text-red-500">[FAIL]</span>
                        <span className="line-through opacity-50">Generic ChatGPT Prompts</span>
                    </li>
                    <li className="flex gap-4 items-center">
                        <span className="text-red-500">[FAIL]</span>
                        <span className="line-through opacity-50">Random Buffer Scheduling</span>
                    </li>
                    <li className="flex gap-4 items-center">
                        <span className="text-red-500">[FAIL]</span>
                        <span className="line-through opacity-50">Zero Pipeline Attribution</span>
                    </li>
                    <li className="flex gap-4 items-center">
                        <span className="text-red-500">[CRITICAL]</span>
                        <span>Founder Burnout</span>
                    </li>
                </ul>

                <p className="mt-24 text-2xl md:text-4xl font-bold leading-tight max-w-md">
                    You are a visionary building the future.
                    <br />
                    <span className="text-white/40">Your marketing is a hallucination.</span>
                </p>
            </div>

            {/* RIGHT PANE: THE REALIZATION */}
            <div className="flex-1 bg-[#F0F0F0] text-black p-12 md:p-24 flex flex-col justify-center items-center text-center relative">
                {/* Scanline effect */}
                <div className="absolute inset-0 pointer-events-none opacity-[0.05]"
                    style={{ background: 'linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06))', backgroundSize: '100% 2px, 3px 100%' }}
                />

                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    className="font-mono text-6xl md:text-8xl font-bold tracking-tighter mb-8"
                >
                    ERROR
                </motion.div>

                <div className="inline-block px-4 py-2 bg-black text-white font-mono text-sm uppercase tracking-widest mb-8">
                    Strategy_Not_Found
                </div>

                <p className="max-w-md text-sm md:text-base font-medium opacity-80 leading-relaxed">
                    Stop throwing spaghetti at the wall.
                    <br />
                    Code requires logic. Marketing requires a system.
                </p>

                {/* Blinking Cursor */}
                <div className="absolute bottom-12 right-12 w-4 h-8 bg-black animate-pulse" />
            </div>

        </section>
    );
}
