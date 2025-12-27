"use client"

import React from "react"
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetTrigger
} from "@/components/ui/sheet"
import {
    BrainCircuit, Info, CheckCircle2, XCircle, AlertTriangle,
    TrendingUp, History, Quote, ChevronDown, ChevronUp
} from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { EXPERTS } from "../council/CouncilChamber"
import { PedigreeVisualizer } from "../council/PedigreeVisualizer"
import { ConfidenceHeatmap } from "../council/ConfidenceHeatmap"
import { cn } from "@/lib/utils"
import { useState } from "react"

interface RationaleDrawerProps {
    isOpen: boolean
    onClose: () => void
    move: {
        id: string
        name: string
        reasoning?: string
        confidence?: number
        campaignName?: string
    }
}

export function RationaleDrawer({ isOpen, onClose, move }: RationaleDrawerProps) {
    const [showDebate, setShowDebate] = useState(false)

    // ... mockRationale ...

const mockRationale = {
    decree: "The Council of 12 has reached 94% alignment on this move. The primary driver is a detected shift in competitor search volume (Δ +12%) matched with our brand's unique ability to serve high-intent retention signals.",
    expertThoughts: [
        { expertId: "direct_response", thought: "Conversion path is optimized for this specific keyword group. Expected CTR: 4.2%." },
        { expertId: "brand_philosopher", thought: "Maintaining editorial restraint here will actually increase perceived value. Avoid emojis in the snippet." },
        { expertId: "data_quant", thought: "Competitor B has dropped their bid floor on these terms by 15% over the last 48 hours." }
    ],
    consensusAlignment: 0.94,
    strategicConfidence: 0.88
}

    return (
        <Sheet open={isOpen} onOpenChange={onClose}>
            <SheetContent className="sm:max-w-xl overflow-y-auto bg-canvas border-l border-borders/50">
                <SheetHeader className="space-y-4 pb-6 border-b border-borders/30">
                    <div className="flex items-center gap-2 text-accent">
                        <BrainCircuit className="h-5 w-5" />
                        <span className="text-[10px] uppercase tracking-widest font-bold font-mono">Council Rationale</span>
                    </div>
                    <div>
                        <SheetTitle className="text-2xl font-serif text-ink italic">{move.name}</SheetTitle>
                        <SheetDescription className="text-secondary-text mt-1">
                            Strategic origin and consensus data for this move.
                        </SheetDescription>
                    </div>
                </SheetHeader>

                <div className="py-8 space-y-10">
                    {/* 0. Lineage Visualizer */}
                    <section className="space-y-3">
                        <h4 className="text-xs font-bold uppercase tracking-widest text-muted-fill flex items-center gap-2">
                            <TrendingUp className="h-3 w-3" />
                            Strategic Lineage
                        </h4>
                        <PedigreeVisualizer />
                    </section>

                    {/* 1. The Decree */}
                    <section className="space-y-3">
                        <h4 className="text-xs font-bold uppercase tracking-widest text-muted-fill flex items-center gap-2">
                            <Info className="h-3 w-3" />
                            Strategic Decree
                        </h4>
                        <div className="p-5 rounded-2xl bg-surface border border-borders/50 shadow-sm">
                            <p className="text-lg font-serif italic text-primary-text leading-relaxed">
                                "{mockRationale.decree}"
                            </p>
                            <p className="text-sm text-secondary-text mt-4 leading-relaxed">
                                {mockRationale.rationale}
                            </p>
                        </div>
                    </section>

                    {/* 2. Consensus Metrics */}
                    <section className="grid grid-cols-1 gap-6">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 rounded-xl border border-borders/30 bg-surface/50">
                                <p className="text-[10px] text-secondary-text uppercase tracking-widest mb-1">Alignment</p>
                                <div className="flex items-center gap-2">
                                    <TrendingUp className="h-4 w-4 text-accent" />
                                    <span className="text-2xl font-mono font-bold text-ink">{(mockRationale.consensus * 100).toFixed(0)}%</span>
                                </div>
                            </div>
                            <div className="p-4 rounded-xl border border-borders/30 bg-surface/50">
                                <p className="text-[10px] text-secondary-text uppercase tracking-widest mb-1">Confidence</p>
                                <div className="flex items-center gap-2">
                                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                                    <span className="text-2xl font-mono font-bold text-ink">{(move.confidence || 0) * 10}%</span>
                                </div>
                            </div>
                        </div>
                        <ConfidenceHeatmap />
                    </section>

                    {/* 3. Expert Perspectives */}
                    <section className="space-y-4">
                        <button
                            onClick={() => setShowDebate(!showDebate)}
                            className="flex items-center justify-between w-full text-xs font-bold uppercase tracking-widest text-muted-fill group"
                        >
                            <span>Expert Perspectives</span>
                            {showDebate ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3 group-hover:translate-y-0.5 transition-transform" />}
                        </button>

                        <AnimatePresence>
                            {showDebate && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="overflow-hidden space-y-3"
                                >
                                    {mockRationale.expertThoughts.map((thought, idx) => {
                                        const expert = EXPERTS.find(e => e.id === thought.agent)
                                        if (!expert) return null
                                        return (
                                            <div key={idx} className="flex gap-4 p-4 rounded-xl hover:bg-surface/80 transition-colors">
                                                <Avatar className="h-8 w-8 shrink-0">
                                                    <AvatarFallback className="bg-muted-fill/10">
                                                        <expert.icon className={cn("h-4 w-4", expert.color)} />
                                                    </AvatarFallback>
                                                </Avatar>
                                                <div className="space-y-1">
                                                    <p className="text-[11px] font-bold text-primary-text uppercase tracking-wider">{expert.name}</p>
                                                    <p className="text-xs text-secondary-text leading-relaxed italic font-mono">
                                                        "{thought.thought}"
                                                    </p>
                                                </div>
                                            </div>
                                        )
                                    })}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </section>

                    {/* 3.5 Historical Parallel */}
                    <section className="space-y-3">
                        <h4 className="text-xs font-bold uppercase tracking-widest text-muted-fill flex items-center gap-2">
                            <History className="h-3 w-3" />
                            Historical Parallel
                        </h4>
                        <div className="p-5 rounded-2xl bg-accent/5 border border-accent/20">
                            <div className="flex gap-3 items-start">
                                <Quote className="h-5 w-5 text-accent opacity-40 shrink-0" />
                                <div>
                                    <p className="text-sm font-serif italic text-primary-text">
                                        This move parallels the 1994 Nike "Play" [Exploit].
                                        By pivoting from product features to identity-based messaging, they achieved a 40% increase in brand recall within 6 months.
                                    </p>
                                    <p className="text-[10px] text-accent font-bold uppercase tracking-widest mt-3">RaptorFlow Precedent ID: RF-94-NK</p>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* 4. Rejected Paths */}
                    <section className="space-y-4 pt-6 border-t border-borders/20">
                        <h4 className="text-xs font-bold uppercase tracking-widest text-muted-fill flex items-center gap-2">
                            <XCircle className="h-3 w-3 text-red-400" />
                            Discarded Alternatives
                        </h4>
                        <div className="space-y-3">
                            {mockRationale.rejected.map((path, idx) => (
                                <div key={idx} className="flex items-start gap-3">
                                    <AlertTriangle className="h-3 w-3 text-amber-500 mt-1" />
                                    <div>
                                        <p className="text-xs font-medium text-primary-text">{path.path}</p>
                                        <p className="text-[11px] text-secondary-text">{path.reason}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>

                <div className="sticky bottom-0 pt-6 pb-2 bg-canvas/80 backdrop-blur-sm border-t border-borders/20">
                    <button
                        onClick={onClose}
                        className="w-full py-3 rounded-xl bg-ink text-white font-medium hover:bg-ink/90 transition-colors"
                    >
                        Understood
                    </button>
                </div>
            </SheetContent>
        </Sheet>
    )
}
