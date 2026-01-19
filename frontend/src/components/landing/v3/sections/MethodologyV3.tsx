"use client";

import React from "react";
import { ArrowDown, Cpu, Zap, FileText } from "lucide-react";

export function MethodologyV3() {
    const steps = [
        {
            id: "01",
            fn: "INITIALIZE_STRATEGY()",
            desc: "User inputs raw positioning data.",
            icon: FileText
        },
        {
            id: "02",
            fn: "COMPILE_ASSETS(MUSE_AI)",
            desc: "System generates 90-day content plan.",
            icon: Cpu
        },
        {
            id: "03",
            fn: "EXECUTE_PROTOCOL()",
            desc: "Publishing and distribution via API.",
            icon: Zap
        }
    ];

    return (
        <section className="bg-[#050505] text-[#FAFAFA] py-32 border-b border-white/10 relative overflow-hidden">

            {/* Background Grid */}
            <div className="absolute inset-0 pointer-events-none opacity-[0.05]"
                style={{ backgroundImage: `linear-gradient(to right, #00FF94 1px, transparent 1px), linear-gradient(to bottom, #00FF94 1px, transparent 1px)`, backgroundSize: '60px 60px' }}
            />

            <div className="max-w-2xl mx-auto px-6 relative z-10">
                <div className="text-center mb-16">
                    <h2 className="font-mono text-sm uppercase tracking-widest text-white/50 mb-4">
                        // The_Logic
                    </h2>
                    <h3 className="text-4xl font-bold tracking-tighter">
                        How it works.
                    </h3>
                </div>

                <div className="space-y-4">
                    {steps.map((step, i) => (
                        <React.Fragment key={i}>
                            {/* Step Card */}
                            <div className="border border-white/20 bg-black/50 backdrop-blur-sm p-8 flex items-center gap-8 group hover:border-[#00FF94] transition-colors duration-300">
                                <div className="font-mono text-xl md:text-2xl text-[#00FF94] opacity-50 group-hover:opacity-100">
                                    {step.id}
                                </div>
                                <div className="flex-1">
                                    <h4 className="font-mono text-lg md:text-xl font-bold mb-2 group-hover:text-[#00FF94] transition-colors">
                                        {step.fn}
                                    </h4>
                                    <p className="font-mono text-sm opacity-60">
                                        {step.desc}
                                    </p>
                                </div>
                                <step.icon className="w-8 h-8 opacity-20 group-hover:opacity-100 transition-opacity text-[#00FF94]" />
                            </div>

                            {/* Connector */}
                            {i < steps.length - 1 && (
                                <div className="flex justify-center py-4">
                                    <ArrowDown className="w-6 h-6 text-white/20 animate-bounce" />
                                </div>
                            )}
                        </React.Fragment>
                    ))}
                </div>

                {/* Final Output */}
                <div className="mt-16 text-center">
                    <div className="inline-block px-8 py-4 bg-[#00FF94] text-black font-mono font-bold uppercase tracking-widest text-sm shadow-[0_0_20px_rgba(0,255,148,0.4)]">
                        result: viral_growth
                    </div>
                </div>

            </div>
        </section>
    );
}
