"use client";

import React from "react";
import { motion } from "framer-motion";
import {
    Target,
    Cpu,
    BarChart3,
    ListTodo,
    Save,
    Users
} from "lucide-react"; // Using standard Lucide icons for now, styled sharply

const MODULES = [
    {
        id: "01",
        name: "FOUNDATION",
        desc: "STRATEGY_KERNEL",
        detail: "Positioning is not art. It is coordinates.",
        icon: Target
    },
    {
        id: "02",
        name: "MUSE",
        desc: "CONTENT_GENERATOR",
        detail: "Infinite drafts. Zero hallucination.",
        icon: Cpu
    },
    {
        id: "03",
        name: "MATRIX",
        desc: "ANALYTICS_CORE",
        detail: "Signal only. No vanity metrics.",
        icon: BarChart3
    },
    {
        id: "04",
        name: "MOVES",
        desc: "EXECUTION_PACKETS",
        detail: "Weekly logical steps. Execute. Repeat.",
        icon: ListTodo
    },
    {
        id: "05",
        name: "BLACKBOX",
        desc: "MEMORY_VAULT",
        detail: "Institutional knowledge, preserved.",
        icon: Save
    },
    {
        id: "06",
        name: "COHORTS",
        desc: "OFFENSE_UNIT",
        detail: "Segment. Target. Convert.",
        icon: Users
    },
];

export function SystemV3() {
    return (
        <section className="relative bg-[#050505] border-b border-white/10">
            {/* SECTION HEADER */}
            <div className="py-24 px-6 md:px-12 border-b border-white/10">
                <h2 className="text-[10vw] md:text-[6rem] leading-[0.9] font-bold tracking-tighter uppercase mb-4">
                    The<br />System
                </h2>
                <p className="font-mono text-sm uppercase tracking-widest text-white/50 max-w-md">
                    Six unified modules. One operating system.
                    <br />Status: Fully Integrated.
                </p>
            </div>

            {/* THE GRID */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 border-l border-white/10">
                {MODULES.map((module, i) => (
                    <div
                        key={module.id}
                        className="group relative h-[400px] border-r border-b border-white/10 p-8 flex flex-col justify-between transition-colors duration-200 hover:bg-white hover:text-black cursor-crosshair overflow-hidden"
                    >
                        {/* Technical Background (Visible on Hover) */}
                        <div className="absolute inset-0 opacity-0 group-hover:opacity-10 pointer-events-none transition-opacity duration-200"
                            style={{ backgroundImage: `radial-gradient(circle, #000 1px, transparent 1px)`, backgroundSize: '20px 20px' }}
                        />

                        {/* TOP ROW: ID + ICON */}
                        <div className="flex justify-between items-start">
                            <span className="font-mono text-xs tracking-widest opacity-50">
                                {module.id}
                            </span>
                            <module.icon strokeWidth={1.5} className="w-8 h-8 opacity-70 group-hover:opacity-100 transition-opacity" />
                        </div>

                        {/* BOTTOM ROW: CONTENT */}
                        <div className="relative z-10">
                            <div className="font-mono text-xs uppercase tracking-wider opacity-50 mb-2">
                                {module.desc}
                            </div>
                            <h3 className="text-3xl font-bold tracking-tight mb-4">
                                {module.name}
                            </h3>
                            <p className="text-sm opacity-70 group-hover:opacity-100 font-medium max-w-[200px]">
                                {module.detail}
                            </p>
                        </div>

                        {/* Corner Accent */}
                        <div className="absolute bottom-0 right-0 w-4 h-4 border-l border-t border-current opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                    </div>
                ))}
            </div>
        </section>
    );
}
