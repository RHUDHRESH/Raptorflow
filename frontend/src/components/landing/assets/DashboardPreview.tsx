"use client";

import React from "react";
import { motion } from "framer-motion";

/**
 * A tilted, glassmorphic dashboard preview mockup.
 * Shows a stylized version of the RaptorFlow dashboard.
 */
export function DashboardPreview() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 40, rotateX: 15 }}
            animate={{ opacity: 1, y: 0, rotateX: 5 }}
            transition={{ duration: 1, delay: 0.6, ease: "easeOut" }}
            style={{ perspective: 1000, transformStyle: "preserve-3d" }}
            className="relative w-full max-w-md mx-auto"
        >
            {/* Main Card - The Dashboard */}
            <div className="relative bg-[var(--canvas)] border border-[var(--border)] rounded-2xl shadow-2xl shadow-[var(--ink)]/10 overflow-hidden backdrop-blur-sm">

                {/* Top Bar */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)] bg-[var(--surface)]/50">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-400/60" />
                        <div className="w-3 h-3 rounded-full bg-yellow-400/60" />
                        <div className="w-3 h-3 rounded-full bg-green-400/60" />
                    </div>
                    <span className="text-xs font-mono text-[var(--muted)]">RaptorFlow Dashboard</span>
                    <div className="w-16" /> {/* Spacer */}
                </div>

                {/* Dashboard Content */}
                <div className="p-4 space-y-4">
                    {/* Header Row */}
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="h-2.5 w-20 bg-[var(--ink)] rounded mb-1.5" />
                            <div className="h-2 w-32 bg-[var(--border)] rounded" />
                        </div>
                        <div className="flex gap-2">
                            <div className="px-2 py-1 text-[8px] font-bold uppercase tracking-wider bg-[var(--accent)]/20 text-[var(--accent)] rounded">Active</div>
                        </div>
                    </div>

                    {/* Metrics Row */}
                    <div className="grid grid-cols-3 gap-3">
                        {[
                            { label: "Pipeline", value: "$42K", change: "+12%" },
                            { label: "Moves", value: "7", change: "This Week" },
                            { label: "Velocity", value: "89", change: "+5 pts" },
                        ].map((metric, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.8 + i * 0.1 }}
                                className="p-3 bg-[var(--surface)] border border-[var(--border)] rounded-lg"
                            >
                                <div className="text-[9px] text-[var(--muted)] uppercase tracking-wider">{metric.label}</div>
                                <div className="text-lg font-bold text-[var(--ink)] font-mono">{metric.value}</div>
                                <div className="text-[8px] text-[var(--accent)]">{metric.change}</div>
                            </motion.div>
                        ))}
                    </div>

                    {/* Task List Preview */}
                    <div className="space-y-2">
                        <div className="text-[10px] uppercase tracking-wider text-[var(--muted)] font-semibold">This Week's Moves</div>
                        {[
                            { status: "done", text: "Publish LinkedIn carousel" },
                            { status: "active", text: "Send cold email batch #3" },
                            { status: "pending", text: "Record founder intro video" },
                        ].map((task, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 1 + i * 0.1 }}
                                className="flex items-center gap-2 p-2 bg-[var(--canvas)] border border-[var(--border)] rounded-lg"
                            >
                                <div className={`w-2.5 h-2.5 rounded-full ${task.status === 'done' ? 'bg-green-500' :
                                        task.status === 'active' ? 'bg-[var(--accent)] animate-pulse' :
                                            'bg-[var(--border)]'
                                    }`} />
                                <span className={`text-[10px] ${task.status === 'done' ? 'line-through text-[var(--muted)]' : 'text-[var(--ink)]'}`}>
                                    {task.text}
                                </span>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Reflection/Glow underneath */}
            <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-3/4 h-8 bg-[var(--ink)]/5 blur-xl rounded-full" />
        </motion.div>
    );
}
