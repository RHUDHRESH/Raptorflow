"use client"

import React, { useState, useEffect } from "react"
import {
    Target,
    Zap,
    BookOpen,
    BarChart3,
    Users,
    LineChart,
    Search,
    Globe,
    Brain,
    Box,
    Handshake,
    UserPlus,
    Activity
} from "lucide-react"
import { motion, AnimatePresence, LayoutGroup } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

export const EXPERTS = [
    { id: "direct_response", name: "Direct Response", role: "Conversion Architect", icon: Target, color: "text-red-500" },
    { id: "viral_alchemist", name: "Viral Alchemist", role: "Social Loop Expert", icon: Zap, color: "text-yellow-500" },
    { id: "brand_philosopher", name: "Brand Philosopher", role: "Positioning & Tone", icon: BookOpen, color: "text-blue-500" },
    { id: "data_quant", name: "Data Quant", role: "Competitive Intelligence", icon: BarChart3, color: "text-purple-500" },
    { id: "community_catalyst", name: "Community Catalyst", role: "Owned Audience", icon: Users, color: "text-green-500" },
    { id: "media_buyer", name: "Media Buyer", role: "Paid Arbitrage", icon: LineChart, color: "text-emerald-500" },
    { id: "seo_moat", name: "SEO Moat", role: "Search Intent", icon: Search, color: "text-cyan-500" },
    { id: "pr_specialist", name: "PR Specialist", role: "Earned Media", icon: Globe, color: "text-orange-500" },
    { id: "psychologist", name: "Psychologist", role: "Cognitive Biases", icon: Brain, color: "text-pink-500" },
    { id: "product_lead", name: "Product Lead", role: "PMF & Features", icon: Box, color: "text-indigo-500" },
    { id: "partnership_lead", name: "Partnership Lead", role: "Ecosystem Leverage", icon: Handshake, color: "text-teal-500" },
    { id: "retention_lead", name: "Retention Lead", role: "LTV & Churn", icon: UserPlus, color: "text-slate-500" },
]

interface CouncilChamberProps {
    debateHistory?: any[]
    consensusMetrics?: {
        alignment: number
        confidence: number
        risk: number
    }
}

export function CouncilChamber({ debateHistory = [], consensusMetrics }: CouncilChamberProps) {
    const [activeExpert, setActiveExpert] = useState<string | null>(null)
    const [isSimulating, setIsSimulating] = useState(false)

    // Simulate "Thought" pulses
    const [pulsingExpert, setPulsingExpert] = useState<string | null>(null)

    useEffect(() => {
        if (isSimulating) {
            const interval = setInterval(() => {
                const randomExpert = EXPERTS[Math.floor(Math.random() * EXPERTS.length)].id
                setPulsingExpert(randomExpert)
                setTimeout(() => setPulsingExpert(null), 1000)
            }, 2000)
            return () => clearInterval(interval)
        }
    }, [isSimulating])

    return (
        <div className="space-y-8 max-w-6xl mx-auto">
            <header className="text-center space-y-2">
                <h1 className="text-4xl font-serif text-ink dark:text-primary-text">The Expert Council</h1>
                <p className="text-secondary-text max-w-2xl mx-auto italic">
                    12 specialized intelligences converging on a single strategic truth.
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
                {/* Left: Experts Grid */}
                <div className="lg:col-span-2">
                    <LayoutGroup>
                        <div className="grid grid-cols-3 sm:grid-cols-4 gap-4">
                            {EXPERTS.map((expert) => (
                                <motion.div
                                    layout
                                    key={expert.id}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={cn(
                                    "relative flex flex-col items-center p-4 rounded-2xl border border-borders/50 bg-surface/50 cursor-pointer transition-all duration-300",
                                    activeExpert === expert.id ? "ring-2 ring-accent border-accent bg-surface" : "hover:border-borders hover:bg-surface",
                                    pulsingExpert === expert.id && "bg-accent/5 shadow-[0_0_15px_rgba(215,201,174,0.3)]"
                                )}
                                onClick={() => setActiveExpert(expert.id)}
                            >
                                <div className="relative">
                                    <Avatar className="h-16 w-16 mb-3 border-2 border-borders/30">
                                        <AvatarFallback className="bg-muted-fill/10">
                                            <expert.icon className={cn("h-8 w-8", expert.color)} />
                                        </AvatarFallback>
                                    </Avatar>
                                    {pulsingExpert === expert.id && (
                                        <motion.div
                                            initial={{ scale: 0.8, opacity: 0 }}
                                            animate={{
                                                scale: [1, 1.2, 1],
                                                opacity: [0.2, 0.5, 0.2]
                                            }}
                                            transition={{
                                                repeat: Infinity,
                                                duration: 2,
                                                ease: "easeInOut"
                                            }}
                                            className="absolute inset-0 rounded-full bg-accent pointer-events-none blur-md"
                                        />
                                    )}
                                </div>
                                <span className="text-xs font-semibold text-center leading-tight">{expert.name}</span>
                                <span className="text-[10px] text-secondary-text text-center mt-1">{expert.role}</span>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Right: Active Thought / Consensus */}
                <div className="space-y-6">
                    <Card className="bg-surface border-borders/50 shadow-sm min-h-[400px] flex flex-col">
                        <CardHeader className="border-b border-borders/30 pb-4">
                            <CardTitle className="text-lg font-medium flex items-center gap-2">
                                {activeExpert ? (
                                    <>
                                        {EXPERTS.find(e => e.id === activeExpert)?.name}
                                        <span className="text-xs font-normal text-secondary-text tracking-wider uppercase">Thought</span>
                                    </>
                                ) : (
                                    <>
                                        <Activity className="h-4 w-4 text-accent" />
                                        Chamber Status
                                    </>
                                )}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 p-6">
                            <AnimatePresence mode="wait">
                                {activeExpert ? (
                                    <motion.div
                                        key={activeExpert}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        className="space-y-4"
                                    >
                                        <p className="text-primary-text leading-relaxed font-serif text-lg">
                                            "Our strategy must leverage the current market delta. I propose a surgical strike on the top 3 competitor keywords while maintaining our core brand philosophy."
                                        </p>
                                        <div className="pt-4 border-t border-borders/20 flex justify-between items-center text-xs text-secondary-text">
                                            <span>Confidence: 94%</span>
                                            <span>Round 1 / Strategy</span>
                                        </div>
                                    </motion.div>
                                ) : (
                                    <div className="h-full flex flex-col items-center justify-center text-center space-y-4 py-12">
                                        <div className="p-4 rounded-full bg-accent/5">
                                            <Brain className="h-12 w-12 text-accent/40" />
                                        </div>
                                        <div className="space-y-2">
                                            <p className="font-medium text-primary-text">Select an Expert</p>
                                            <p className="text-sm text-secondary-text max-w-[200px]">
                                                Click on a council member to inspect their contribution to the current debate.
                                            </p>
                                        </div>
                                        <button
                                            onClick={() => setIsSimulating(!isSimulating)}
                                            className="mt-4 px-4 py-2 rounded-full border border-borders text-xs hover:bg-accent/10 transition-colors"
                                        >
                                            {isSimulating ? "Stop Simulation" : "Simulate Debate"}
                                        </button>
                                    </div>
                                )}
                            </AnimatePresence>
                        </CardContent>
                    </Card>

                    {/* Consensus Summary Card */}
                    {consensusMetrics && (
                        <Card className="bg-surface border-borders/50 shadow-sm overflow-hidden">
                            <div className="h-1 bg-accent" style={{ width: `${consensusMetrics.alignment * 100}%` }} />
                            <CardContent className="p-4 flex justify-between items-center">
                                <div className="space-y-1">
                                    <p className="text-[10px] text-secondary-text uppercase tracking-widest">Consensus Alignment</p>
                                    <p className="text-xl font-mono font-bold text-accent">{(consensusMetrics.alignment * 100).toFixed(0)}%</p>
                                </div>
                                <div className="text-right space-y-1">
                                    <p className="text-[10px] text-secondary-text uppercase tracking-widest text-right">Strategic Confidence</p>
                                    <p className="text-sm font-medium text-primary-text">{(consensusMetrics.confidence * 100).toFixed(0)}%</p>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    )
}
