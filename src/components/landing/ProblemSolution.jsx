import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { X, Check, ArrowRight } from 'lucide-react'
import { LuxeHeading } from '../ui/PremiumUI'

const ComparisonRow = ({ feature, oldWay, newWay, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6 py-8 border-b border-neutral-200 last:border-0 hover:bg-neutral-50 transition-colors px-6 rounded-xl"
    >
        <div className="font-serif text-xl font-bold text-neutral-900 flex items-center">
            {feature}
        </div>
        <div className="flex items-start gap-3 text-neutral-500">
            <div className="mt-1 min-w-[24px] h-6 w-6 rounded-full bg-red-100 flex items-center justify-center text-red-600">
                <X className="w-4 h-4" />
            </div>
            <p className="leading-relaxed">{oldWay}</p>
        </div>
        <div className="flex items-start gap-3 text-neutral-900 font-medium">
            <div className="mt-1 min-w-[24px] h-6 w-6 rounded-full bg-green-100 flex items-center justify-center text-green-600">
                <Check className="w-4 h-4" />
            </div>
            <p className="leading-relaxed">{newWay}</p>
        </div>
    </motion.div>
)

export const ProblemSolution = () => {
    return (
        <section className="py-32 bg-white">
            <div className="mx-auto max-w-7xl px-6">
                <div className="text-center mb-20">
                    <LuxeHeading level={2} className="mb-6">
                        Stop Managing Chaos. <br />
                        <span className="text-neutral-400">Start Managing Strategy.</span>
                    </LuxeHeading>
                    <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
                        Most agencies are stuck in the "Old Way". RaptorFlow is the "New Way".
                        See the difference for yourself.
                    </p>
                </div>

                <div className="bg-white rounded-3xl border border-neutral-200 shadow-xl overflow-hidden">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 bg-neutral-50 border-b border-neutral-200 text-sm font-bold uppercase tracking-wider text-neutral-500">
                        <div>Feature</div>
                        <div>The Old Way</div>
                        <div className="text-neutral-900">The RaptorFlow Way</div>
                    </div>

                    <ComparisonRow
                        feature="Cohort Analysis"
                        oldWay="Guessing based on 'feel' or basic demographics. Spreadsheets that break."
                        newWay="AI-driven behavioral segmentation. Automatically updates in real-time."
                        delay={0.1}
                    />
                    <ComparisonRow
                        feature="Campaign Launch"
                        oldWay="Manually coordinating email, ads, and social. Missed deadlines."
                        newWay="One-click multi-channel deployment. Perfect synchronization."
                        delay={0.2}
                    />
                    <ComparisonRow
                        feature="ROI Tracking"
                        oldWay="Wait for end-of-month reports. vague attribution."
                        newWay="Live P&L for every campaign. Know exactly what makes money."
                        delay={0.3}
                    />
                    <ComparisonRow
                        feature="Team Alignment"
                        oldWay="Endless Slack threads. 'Did you do that?' meetings."
                        newWay="Centralized command center. Everyone knows their moves."
                        delay={0.4}
                    />
                    <ComparisonRow
                        feature="Strategy Updates"
                        oldWay="Quarterly PDF decks that get ignored."
                        newWay="Living strategy that evolves with market data."
                        delay={0.5}
                    />
                </div>
            </div>
        </section>
    )
}
