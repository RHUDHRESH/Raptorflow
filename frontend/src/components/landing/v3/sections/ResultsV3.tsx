"use client";

import React from "react";

export function ResultsV3() {
    const data = [
        { id: "USR_0942", metric: "PIPELINE_GEN", value: "$240,000", delta: "+140%" },
        { id: "USR_1182", metric: "HOURS_SAVED", value: "18.5 HRS", delta: "WEEKLY" },
        { id: "USR_0551", metric: "ENGAGEMENT", value: "482,000", delta: "+850%" },
        { id: "USR_2209", metric: "CONVERSION", value: "4.8%", delta: "+2.1%" },
        { id: "USR_0104", metric: "PUBLISHED", value: "124 PCS", delta: "AUTO" },
    ];

    return (
        <section className="bg-[#050505] text-[#00FF94] py-32 border-b border-white/10 font-mono">
            <div className="max-w-[1440px] mx-auto px-6 md:px-12">

                <div className="mb-12 border-b border-[#00FF94]/20 pb-4 flex justify-between items-end">
                    <div>
                        <div className="text-xs uppercase tracking-widest opacity-50 mb-2">Query: SELECT * FROM SUCCESS_STORIES LIMIT 5</div>
                        <h2 className="text-3xl md:text-4xl font-bold tracking-tighter">
                            THE OUTPUT
                        </h2>
                    </div>
                    <div className="text-xs uppercase tracking-widest opacity-50 hidden md:block">
                        Status: VERIFIED
                    </div>
                </div>

                {/* Data Table */}
                <div className="hidden md:block w-full text-left border-collapse">
                    <div className="grid grid-cols-4 border-b border-[#00FF94]/30 py-4 opacity-50 text-xs uppercase tracking-widest">
                        <div>User_ID</div>
                        <div>Metric</div>
                        <div>Value</div>
                        <div>Delta</div>
                    </div>
                    {data.map((row, i) => (
                        <div key={i} className="grid grid-cols-4 py-8 border-b border-[#00FF94]/10 hover:bg-[#00FF94]/5 transition-colors cursor-default">
                            <div className="opacity-50">{row.id}</div>
                            <div className="font-bold">{row.metric}</div>
                            <div className="text-xl md:text-2xl text-white font-sans font-bold">{row.value}</div>
                            <div className="flex items-center gap-2">
                                <span className="inline-block w-2 h-2 bg-[#00FF94] rounded-full animate-pulse" />
                                {row.delta}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Mobile Card View */}
                <div className="md:hidden space-y-4">
                    {data.map((row, i) => (
                        <div key={i} className="border border-[#00FF94]/20 p-6 bg-[#00FF94]/5">
                            <div className="flex justify-between mb-4 opacity-50 text-xs">
                                <span>{row.id}</span>
                                <span>{row.delta}</span>
                            </div>
                            <div className="text-lg font-bold mb-1">{row.metric}</div>
                            <div className="text-3xl text-white font-sans font-bold">{row.value}</div>
                        </div>
                    ))}
                </div>

            </div>
        </section>
    );
}
