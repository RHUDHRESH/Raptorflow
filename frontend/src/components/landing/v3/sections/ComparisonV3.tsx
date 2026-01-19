"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Check, X } from "lucide-react";

const COMPARISON_DATA = [
    {
        feature: "Stragegy Execution",
        oldWay: "Scattered Google Docs",
        newWay: "Unified 90-Day War Plan"
    },
    {
        feature: "Content Creation",
        oldWay: "Generic ChatGPT Prompts",
        newWay: "Voice-Trained Muse AI"
    },
    {
        feature: "Analytics",
        oldWay: "Vanity Metrics (Likes)",
        newWay: "Pipeline Attribution ($)"
    },
    {
        feature: "Workflow",
        oldWay: "5 Disconnected Apps",
        newWay: "One Operating System"
    }
];

export function ComparisonV3() {
    return (
        <section className="bg-[#050505] text-white py-32 border-b border-white/10">
            <div className="max-w-[1200px] mx-auto px-6">

                <div className="text-center mb-16">
                    <h2 className="font-mono text-sm uppercase tracking-widest text-[#00FF94] mb-4">
                        // The_Ledger
                    </h2>
                    <h3 className="text-4xl md:text-5xl font-bold tracking-tighter">
                        Chaos vs. Order.
                    </h3>
                </div>

                {/* THE TABLE */}
                <div className="border border-white/20">
                    {/* Header */}
                    <div className="grid grid-cols-12 border-b border-white/20 bg-white/5 font-mono text-xs uppercase tracking-widest">
                        <div className="col-span-4 p-4 border-r border-white/20 text-white/50">Feature_ID</div>
                        <div className="col-span-4 p-4 border-r border-white/20 text-white/50">Common_Practice</div>
                        <div className="col-span-4 p-4 text-[#00FF94]">RaptorFlow_Protocol</div>
                    </div>

                    {/* Rows */}
                    {COMPARISON_DATA.map((row, i) => (
                        <div key={i} className="grid grid-cols-12 border-b border-white/10 last:border-b-0 group hover:bg-white/5 transition-colors">

                            {/* Feature Name */}
                            <div className="col-span-4 p-6 border-r border-white/10 flex items-center font-mono text-sm opacity-60">
                                {row.feature}
                            </div>

                            {/* Old Way (Chaos) */}
                            <div className="col-span-4 p-6 border-r border-white/10 flex items-center gap-3 opacity-40 group-hover:opacity-50 transition-opacity">
                                <X className="w-4 h-4 text-red-500" />
                                <span className="line-through decoration-red-500/50 decoration-2">
                                    {row.oldWay}
                                </span>
                            </div>

                            {/* New Way (Order) */}
                            <div className="col-span-4 p-6 flex items-center gap-3 font-semibold bg-white/0 group-hover:bg-[#00FF94]/5 transition-colors">
                                <Check className="w-4 h-4 text-[#00FF94]" />
                                <span className="text-white group-hover:text-[#00FF94] transition-colors">
                                    {row.newWay}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>

            </div>
        </section>
    );
}
