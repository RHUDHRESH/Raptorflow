"use client"

import React from "react"
import { motion } from "framer-motion"
import {
    Radio,
    ArrowRight,
    Users,
    CheckCircle2,
    FileText,
    BrainCircuit
} from "lucide-react"
import { cn } from "@/lib/utils"

interface PedigreeNodeProps {
    icon: React.ElementType
    label: string
    status: "done" | "active" | "pending"
    sublabel?: string
    delay?: number
}

const PedigreeNode = ({ icon: Icon, label, status, sublabel, delay = 0 }: PedigreeNodeProps) => {
    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay, duration: 0.5 }}
            className="flex flex-col items-center gap-3 relative z-10"
        >
            <div className={cn(
                "w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-500",
                status === "done" ? "bg-accent/10 border-accent text-accent" :
                status === "active" ? "bg-white border-accent border-dashed animate-pulse text-accent" :
                "bg-muted-fill/5 border-borders text-muted-fill"
            )}>
                <Icon className="h-5 w-5" />
            </div>
            <div className="text-center">
                <p className="text-[10px] font-bold uppercase tracking-widest text-ink">{label}</p>
                {sublabel && <p className="text-[9px] text-secondary-text mt-0.5">{sublabel}</p>}
            </div>
        </motion.div>
    )
}

export function PedigreeVisualizer() {
    return (
        <div className="relative p-8 rounded-3xl bg-surface border border-borders/50 overflow-hidden">
            {/* Background connecting line */}
            <div className="absolute top-[52px] left-12 right-12 h-[2px] bg-borders/30" />

            <div className="flex justify-between items-start relative">
                <PedigreeNode
                    icon={Radio}
                    label="Radar"
                    sublabel="Event Discovery"
                    status="done"
                    delay={0.1}
                />

                <PedigreeNode
                    icon={Users}
                    label="Debate"
                    sublabel="12 Experts"
                    status="done"
                    delay={0.3}
                />

                <PedigreeNode
                    icon={CheckCircle2}
                    label="Consensus"
                    sublabel="88% Alignment"
                    status="done"
                    delay={0.5}
                />

                <PedigreeNode
                    icon={BrainCircuit}
                    label="Synthesis"
                    sublabel="Strategic Decree"
                    status="active"
                    delay={0.7}
                />

                <PedigreeNode
                    icon={FileText}
                    label="Execution"
                    sublabel="Tactical Move"
                    status="pending"
                    delay={0.9}
                />
            </div>

            {/* Decorative Elements */}
            <div className="mt-8 flex justify-center">
                <div className="px-4 py-1.5 rounded-full border border-borders/30 bg-canvas/50 text-[9px] text-secondary-text uppercase tracking-widest font-mono">
                    Lineage: Chain_20251227_Alpha
                </div>
            </div>
        </div>
    )
}
