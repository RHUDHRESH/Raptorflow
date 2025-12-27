"use client"

import React from "react"
import { motion } from "framer-motion"
import { EXPERTS } from "./CouncilChamber"
import { cn } from "@/lib/utils"

export function CouncilBriefing() {
    return (
        <div className="max-w-2xl mx-auto p-12 bg-white border border-borders/50 shadow-2xl rounded-sm font-serif text-ink">
            {/* Letterhead */}
            <header className="text-center border-b-2 border-ink pb-8 mb-12">
                <h2 className="text-sm font-bold uppercase tracking-[0.4em] mb-4">The Expert Council</h2>
                <p className="text-[10px] uppercase tracking-widest text-muted-fill">Chamber Dispatch: Alpha-One</p>
            </header>

            {/* Salutation */}
            <div className="space-y-8 leading-relaxed">
                <p className="text-lg">Dear Founder,</p>

                <p>
                    Following a 14-round strategic debate, the Council has reached a supermajority alignment (91.4%)
                    on your growth trajectory for the upcoming cycle.
                </p>

                <div className="py-6 border-y border-borders/30 italic text-2xl text-center px-4">
                    "Transition from aggressive acquisition to authority-based retention."
                </div>

                <p>
                    Our data quants have identified a significant delta in your competitor's recent positioning shifts.
                    The Brand Philosopher has refined your narrative to counter this movement while maintaining
                    the 'Quiet Luxury' aesthetic that defines your current market moat.
                </p>

                <div className="space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-widest border-b border-borders/30 pb-2">Top Strategic Moves</h4>
                    <ul className="space-y-3">
                        <li className="flex items-start gap-3">
                            <span className="w-1.5 h-1.5 rounded-full bg-accent mt-2 shrink-0" />
                            <span className="text-sm">Launch 'Identity Pivot' sequence on LinkedIn (Estimated ROI: 4.2x)</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="w-1.5 h-1.5 rounded-full bg-accent mt-2 shrink-0" />
                            <span className="text-sm">Audit landing page for cognitive load friction.</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="w-1.5 h-1.5 rounded-full bg-accent mt-2 shrink-0" />
                            <span className="text-sm">Initialize partnership outreach with high-overlap SaaS cohorts.</span>
                        </li>
                    </ul>
                </div>

                <p>
                    The path is clear. Execution readiness is high. We await your signal to propagate these moves into the workspace.
                </p>

                <div className="pt-12">
                    <p className="text-sm italic">With strategic intent,</p>
                    <div className="mt-6 grid grid-cols-4 gap-2 opacity-40 grayscale group hover:grayscale-0 hover:opacity-100 transition-all">
                        {EXPERTS.slice(0, 4).map(e => (
                            <div key={e.id} className="text-center">
                                <div className="text-[8px] font-bold uppercase tracking-tighter">{e.name}</div>
                                <div className="text-[6px] italic">Expert {e.id.split('_')[0]}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Footer Seal */}
            <footer className="mt-20 pt-8 border-t border-borders/20 text-center opacity-30">
                <div className="inline-block p-4 rounded-full border-2 border-borders">
                    <div className="text-[8px] font-bold uppercase tracking-[0.5em]">RaptorFlow</div>
                </div>
            </footer>
        </div>
    )
}
