"use client";

import React from "react";
import { motion } from "framer-motion";

export function GapV3() {
    return (
        <section className="relative py-32 bg-white text-black border-b border-black overflow-hidden">
            <div className="max-w-[1440px] mx-auto px-6 md:px-12">

                <div className="text-center mb-24">
                    <h2 className="text-[6vw] md:text-[5rem] leading-[0.9] font-bold tracking-tighter uppercase mb-6">
                        The Gap.
                    </h2>
                    <p className="font-mono text-sm md:text-base uppercase tracking-widest opacity-60 max-w-xl mx-auto">
                        Why your current stack is failing you.
                    </p>
                </div>

                <div className="relative flex flex-col md:flex-row items-center justify-center h-[600px] md:h-[500px]">

                    {/* Circle A: Generalist AI */}
                    <div className="absolute top-0 md:top-auto md:left-1/4 w-64 h-64 md:w-80 md:h-80 rounded-full border border-dashed border-black/30 flex items-center justify-center p-8 text-center bg-[#FAFAFA] z-10">
                        <div>
                            <div className="font-mono text-xs uppercase tracking-widest mb-2 opacity-50">Too Generic</div>
                            <h3 className="text-xl font-bold">Generalist AI</h3>
                            <p className="text-sm mt-2 opacity-60">(ChatGPT, Claude, etc)</p>
                        </div>
                    </div>

                    {/* Circle B: Scheduling Tools */}
                    <div className="absolute bottom-0 md:bottom-auto md:right-1/4 w-64 h-64 md:w-80 md:h-80 rounded-full border border-dashed border-black/30 flex items-center justify-center p-8 text-center bg-[#FAFAFA] z-10">
                        <div>
                            <div className="font-mono text-xs uppercase tracking-widest mb-2 opacity-50">Just Logistics</div>
                            <h3 className="text-xl font-bold">Schedulers</h3>
                            <p className="text-sm mt-2 opacity-60">(Buffer, Hootsuite)</p>
                        </div>
                    </div>

                    {/* THE GAP - RaptorFlow */}
                    {/* Positioned explicitly in the center, overlapping/bridging them */}
                    <div className="relative z-20 w-80 md:w-[500px] h-40 bg-black text-white flex items-center justify-center shadow-2xl skew-y-3 hover:skew-y-0 transition-transform duration-500 cursor-pointer group">
                        <div className="text-center">
                            <div className="font-mono text-xs text-[#00FF94] uppercase tracking-widest mb-2 opacity-0 group-hover:opacity-100 transition-opacity absolute -top-8 left-0 w-full">
                                The Missing Link
                            </div>
                            <h3 className="text-3xl md:text-4xl font-bold tracking-tight">
                                The Operating System
                            </h3>
                            <p className="text-sm text-white/60 mt-2">
                                Strategy + Execution + Memory
                            </p>
                        </div>

                        {/* Connector Lines */}
                        <div className="absolute top-1/2 left-0 w-full h-[1px] bg-white/20 -z-10" />
                    </div>

                </div>
            </div>
        </section>
    );
}
