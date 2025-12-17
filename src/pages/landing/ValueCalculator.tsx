import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Calculator, Clock, IndianRupee, ArrowRight, TrendingUp, AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { BrandIcon } from '@/components/brand/BrandSystem'

// ═══════════════════════════════════════════════════════════════════════════════
// VALUE CALCULATOR - What you gain vs what you lose by not using RaptorFlow
// ═══════════════════════════════════════════════════════════════════════════════

export const ValueCalculator = () => {
    const [hoursPerWeek, setHoursPerWeek] = useState(10)
    const [contentPieces, setContentPieces] = useState(5)
    const [toolsCost, setToolsCost] = useState(5000)

    // Calculate values
    const hourlyRate = 500 // Average founder hourly value in INR
    const timeSavedPerWeek = Math.round(hoursPerWeek * 0.7) // 70% time savings
    const moneySavedFromTime = timeSavedPerWeek * 4 * hourlyRate
    const contentMultiplier = 3
    const extraContent = contentPieces * (contentMultiplier - 1) * 4 // per month
    const raptorflowPrice = 6999

    return (
        <section className="relative py-24 md:py-32 bg-muted/30 overflow-hidden">
            {/* Background decoration */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.02)_1px,transparent_1px)] bg-[size:50px_50px]" />

            <div className="container-editorial relative z-10">
                {/* Header */}
                <motion.div
                    className="max-w-3xl mx-auto text-center mb-12"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <div className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground mb-4">
                        <span className="w-8 h-px bg-border" />
                        ROI Calculator
                    </div>
                    <h2 className="font-serif text-3xl md:text-5xl font-medium text-foreground">
                        What you <span className="text-primary">gain</span> vs. what you <span className="text-red-400">lose</span>
                    </h2>
                </motion.div>

                <div className="max-w-5xl mx-auto">
                    <div className="grid md:grid-cols-3 gap-6">
                        {/* Left - What You Lose By Not Joining */}
                        <motion.div
                            className="p-6 rounded-2xl border-2 border-red-500/30 bg-red-500/5 order-1"
                            initial={{ opacity: 0, x: -30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                        >
                            <h3 className="font-serif text-lg font-medium text-red-400 mb-6 flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5" />
                                What You Lose
                            </h3>

                            <div className="space-y-4">
                                <div className="p-4 rounded-xl bg-card border border-border">
                                    <div className="flex items-center gap-3">
                                        <Clock className="w-5 h-5 text-red-400" />
                                        <div>
                                            <div className="text-2xl font-mono font-bold text-foreground">
                                                {hoursPerWeek * 4}h
                                            </div>
                                            <p className="text-xs text-muted-foreground">wasted on busywork/mo</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-4 rounded-xl bg-card border border-border">
                                    <div className="flex items-center gap-3">
                                        <BrandIcon name="speed" className="w-5 h-5 text-red-400" />
                                        <div>
                                            <div className="text-2xl font-mono font-bold text-foreground">
                                                0
                                            </div>
                                            <p className="text-xs text-muted-foreground">campaigns optimized</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-4 rounded-xl bg-card border border-border">
                                    <div className="flex items-center gap-3">
                                        <IndianRupee className="w-5 h-5 text-red-400" />
                                        <div>
                                            <div className="text-2xl font-mono font-bold text-foreground">
                                                ???
                                            </div>
                                            <p className="text-xs text-muted-foreground">ROI from marketing</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>

                        {/* Center - Your Situation (Inputs) */}
                        <motion.div
                            className="p-6 rounded-2xl border-2 border-border bg-card order-2"
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.1 }}
                        >
                            <h3 className="font-serif text-lg font-medium text-foreground mb-6 flex items-center gap-2">
                                <Calculator className="w-5 h-5 text-muted-foreground" />
                                Your Current Situation
                            </h3>

                            {/* Hours slider */}
                            <div className="mb-6">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-sm text-muted-foreground">
                                        Hours/week on marketing
                                    </label>
                                    <span className="text-lg font-mono font-bold text-foreground">
                                        {hoursPerWeek}h
                                    </span>
                                </div>
                                <input
                                    type="range"
                                    min="2"
                                    max="30"
                                    value={hoursPerWeek}
                                    onChange={(e) => setHoursPerWeek(parseInt(e.target.value))}
                                    className="w-full h-3 bg-muted rounded-full appearance-none cursor-grab active:cursor-grabbing accent-primary"
                                    style={{ touchAction: 'none' }}
                                />
                            </div>

                            {/* Campaigns slider */}
                            <div className="mb-6">
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-sm text-muted-foreground">
                                        Campaigns/month
                                    </label>
                                    <span className="text-lg font-mono font-bold text-foreground">
                                        {contentPieces}
                                    </span>
                                </div>
                                <input
                                    type="range"
                                    min="1"
                                    max="20"
                                    value={contentPieces}
                                    onChange={(e) => setContentPieces(parseInt(e.target.value))}
                                    className="w-full h-3 bg-muted rounded-full appearance-none cursor-grab active:cursor-grabbing accent-primary"
                                    style={{ touchAction: 'none' }}
                                />
                            </div>

                            {/* Assets slider */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-sm text-muted-foreground">
                                        Assets created/month
                                    </label>
                                    <span className="text-lg font-mono font-bold text-foreground">
                                        {toolsCost}
                                    </span>
                                </div>
                                <input
                                    type="range"
                                    min="5"
                                    max="100"
                                    step="5"
                                    value={toolsCost}
                                    onChange={(e) => setToolsCost(parseInt(e.target.value))}
                                    className="w-full h-3 bg-muted rounded-full appearance-none cursor-grab active:cursor-grabbing accent-primary"
                                    style={{ touchAction: 'none' }}
                                />
                            </div>
                        </motion.div>

                        {/* Right - What You Gain */}
                        <motion.div
                            className="p-6 rounded-2xl border-2 border-primary bg-primary/5 order-3"
                            initial={{ opacity: 0, x: 30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                        >
                            <h3 className="font-serif text-lg font-medium text-primary mb-6 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5" />
                                What You Gain
                            </h3>

                            <div className="space-y-4">
                                <motion.div
                                    className="p-4 rounded-xl bg-card border border-border"
                                    key={`time-${timeSavedPerWeek}`}
                                >
                                    <div className="flex items-center gap-3">
                                        <Clock className="w-5 h-5 text-emerald-500" />
                                        <div>
                                            <div className="text-2xl font-mono font-bold text-foreground">
                                                {timeSavedPerWeek * 4}h
                                            </div>
                                            <p className="text-xs text-muted-foreground">saved per month</p>
                                        </div>
                                    </div>
                                </motion.div>

                                <motion.div
                                    className="p-4 rounded-xl bg-card border border-border"
                                    key={`content-${extraContent}`}
                                >
                                    <div className="flex items-center gap-3">
                                        <BrandIcon name="speed" className="w-5 h-5 text-emerald-500" />
                                        <div>
                                            <div className="text-2xl font-mono font-bold text-foreground">
                                                3x
                                            </div>
                                            <p className="text-xs text-muted-foreground">faster asset creation</p>
                                        </div>
                                    </div>
                                </motion.div>

                                <motion.div
                                    className="p-4 rounded-xl bg-card border border-border"
                                    key={`money-${moneySavedFromTime}`}
                                >
                                    <div className="flex items-center gap-3">
                                        <IndianRupee className="w-5 h-5 text-emerald-500" />
                                        <div>
                                            <div className="text-2xl font-mono font-bold text-foreground">
                                                100%
                                            </div>
                                            <p className="text-xs text-muted-foreground">clarity on what works</p>
                                        </div>
                                    </div>
                                </motion.div>
                            </div>
                        </motion.div>
                    </div>

                    {/* CTA */}
                    <motion.div
                        className="mt-12 text-center"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.3 }}
                    >
                        <Link
                            to="/signup"
                            className="group inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-xl font-medium text-lg hover:opacity-90 transition-all shadow-lg shadow-primary/25"
                        >
                            Start gaining, stop losing
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <p className="text-sm text-muted-foreground mt-3">
                            RaptorFlow Glide plan: ₹{raptorflowPrice.toLocaleString()}/month
                        </p>
                    </motion.div>
                </div>
            </div>
        </section>
    )
}

export default ValueCalculator
