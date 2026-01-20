"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Module {
    name: string;
    desc: string;
    tag: string;
    icon: string;
}

const MODULES: Module[] = [
    { name: "Foundation", desc: "Our 22-step cognitive onboarding extracts your Precision Soundbites and builds your 90-day plan in minutes.", tag: "Strategy", icon: "◈" },
    { name: "Cohorts", desc: "Segment by behavioral science markers, not demographics. Know exactly who converts—and why.", tag: "Intelligence", icon: "◉" },
    { name: "Moves", desc: "Ready-to-ship execution packets delivered every Monday. Content drafted. Tasks clear. Just ship.", tag: "Execution", icon: "▲" },
    { name: "Muse", desc: "Generate content that sounds like your specific brand voice, not a generic robot. Scale your ideas.", tag: "Creation", icon: "✦" },
    { name: "Matrix", desc: "The Boardroom View. See what's actually driving pipeline. Cut what isn't. Decide in seconds.", tag: "Analytics", icon: "◇" },
    { name: "Blackbox", desc: "The Cognitive Spine. Every experiment, every outcome, and every insight preserved forever.", tag: "Memory", icon: "■" },
];

// Constellation node positions (normalized 0-1)
const NODE_POSITIONS = [
    { x: 0.2, y: 0.25 },   // Foundation
    { x: 0.8, y: 0.2 },    // Cohorts
    { x: 0.15, y: 0.7 },   // Moves
    { x: 0.5, y: 0.5 },    // Muse (center)
    { x: 0.85, y: 0.65 },  // Matrix
    { x: 0.5, y: 0.85 },   // Blackbox
];

// Connection lines between nodes
const CONNECTIONS = [
    [0, 3], [1, 3], [2, 3], [3, 4], [3, 5], // Muse connects to all
    [0, 2], [1, 4], [4, 5], [2, 5], // Secondary connections
];

export default function ModuleConstellation() {
    const [activeNode, setActiveNode] = useState<number | null>(null);
    const [hoveredNode, setHoveredNode] = useState<number | null>(null);

    return (
        <div className="relative w-full aspect-[16/10] max-h-[600px]">
            {/* SVG Connection Lines */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
                <defs>
                    <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="rgba(224, 141, 121, 0.3)" />
                        <stop offset="50%" stopColor="rgba(140, 169, 179, 0.4)" />
                        <stop offset="100%" stopColor="rgba(166, 196, 185, 0.3)" />
                    </linearGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {CONNECTIONS.map(([from, to], i) => {
                    const fromPos = NODE_POSITIONS[from];
                    const toPos = NODE_POSITIONS[to];
                    const isActive = activeNode === from || activeNode === to ||
                        hoveredNode === from || hoveredNode === to;

                    return (
                        <motion.line
                            key={i}
                            x1={`${fromPos.x * 100}%`}
                            y1={`${fromPos.y * 100}%`}
                            x2={`${toPos.x * 100}%`}
                            y2={`${toPos.y * 100}%`}
                            stroke="url(#lineGradient)"
                            strokeWidth={isActive ? 2 : 1}
                            opacity={isActive ? 0.8 : 0.3}
                            filter={isActive ? "url(#glow)" : undefined}
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 1.5, delay: i * 0.1 }}
                        />
                    );
                })}

                {/* Animated pulse along connections when node is active */}
                {activeNode !== null && CONNECTIONS.filter(([from, to]) =>
                    from === activeNode || to === activeNode
                ).map(([from, to], i) => {
                    const fromPos = NODE_POSITIONS[from];
                    const toPos = NODE_POSITIONS[to];
                    const isFromActive = from === activeNode;
                    const startX = isFromActive ? fromPos.x : toPos.x;
                    const startY = isFromActive ? fromPos.y : toPos.y;
                    const endX = isFromActive ? toPos.x : fromPos.x;
                    const endY = isFromActive ? toPos.y : fromPos.y;

                    return (
                        <motion.circle
                            key={`pulse-${i}`}
                            r="3"
                            fill="rgba(224, 141, 121, 0.8)"
                            filter="url(#glow)"
                            initial={{ cx: `${startX * 100}%`, cy: `${startY * 100}%` }}
                            animate={{
                                cx: [`${startX * 100}%`, `${endX * 100}%`],
                                cy: [`${startY * 100}%`, `${endY * 100}%`],
                                opacity: [1, 0]
                            }}
                            transition={{
                                duration: 1,
                                delay: i * 0.15,
                                repeat: Infinity,
                                repeatDelay: 1
                            }}
                        />
                    );
                })}
            </svg>

            {/* Constellation Nodes */}
            {MODULES.map((module, i) => {
                const pos = NODE_POSITIONS[i];
                const isActive = activeNode === i;
                const isHovered = hoveredNode === i;

                return (
                    <motion.div
                        key={i}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                        style={{ left: `${pos.x * 100}%`, top: `${pos.y * 100}%` }}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.5 + i * 0.1, type: "spring", stiffness: 200 }}
                        onMouseEnter={() => setHoveredNode(i)}
                        onMouseLeave={() => setHoveredNode(null)}
                        onClick={() => setActiveNode(isActive ? null : i)}
                    >
                        {/* Node circle */}
                        <motion.div
                            className={`
                                relative w-20 h-20 md:w-24 md:h-24 rounded-full flex items-center justify-center
                                border-2 transition-all duration-300
                                ${isActive
                                    ? "bg-[var(--ink)] border-[var(--ink)] text-[var(--canvas)]"
                                    : "bg-[var(--canvas)] border-[var(--border)] text-[var(--ink)]"
                                }
                            `}
                            animate={{
                                scale: isHovered || isActive ? 1.1 : 1,
                                boxShadow: isActive
                                    ? "0 0 30px rgba(224, 141, 121, 0.4)"
                                    : isHovered
                                        ? "0 0 20px rgba(140, 169, 179, 0.3)"
                                        : "0 4px 20px rgba(0, 0, 0, 0.05)"
                            }}
                        >
                            {/* Ripple effect on hover */}
                            {isHovered && !isActive && (
                                <motion.div
                                    className="absolute inset-0 rounded-full border-2 border-[var(--rf-ocean)]"
                                    initial={{ scale: 1, opacity: 0.5 }}
                                    animate={{ scale: 1.5, opacity: 0 }}
                                    transition={{ duration: 0.8, repeat: Infinity }}
                                />
                            )}

                            <div className="text-center">
                                <span className="text-2xl md:text-3xl">{module.icon}</span>
                            </div>
                        </motion.div>

                        {/* Label */}
                        <motion.div
                            className="absolute top-full mt-2 left-1/2 -translate-x-1/2 whitespace-nowrap text-center"
                            animate={{ opacity: isHovered || isActive ? 1 : 0.7 }}
                        >
                            <span className="text-xs uppercase tracking-wider text-[var(--muted)] block">
                                {module.tag}
                            </span>
                            <span className={`text-sm font-semibold ${isActive ? "text-[var(--ink)]" : "text-[var(--secondary)]"}`}>
                                {module.name}
                            </span>
                        </motion.div>
                    </motion.div>
                );
            })}

            {/* Expanded Description Panel */}
            <AnimatePresence>
                {activeNode !== null && (
                    <motion.div
                        className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        transition={{ type: "spring", stiffness: 300, damping: 25 }}
                    >
                        <div className="bg-[var(--canvas)] border border-[var(--border)] rounded-2xl p-6 shadow-xl">
                            <div className="flex items-center gap-3 mb-3">
                                <span className="text-2xl">{MODULES[activeNode].icon}</span>
                                <div>
                                    <span className="text-xs uppercase tracking-wider text-[var(--muted)] block">
                                        {MODULES[activeNode].tag}
                                    </span>
                                    <h3 className="text-xl font-bold">{MODULES[activeNode].name}</h3>
                                </div>
                            </div>
                            <p className="text-[var(--secondary)] leading-relaxed">
                                {MODULES[activeNode].desc}
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
