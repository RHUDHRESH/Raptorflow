import React from 'react'
import { motion } from 'framer-motion'
import { ArrowUpRight } from 'lucide-react'

const FeatureItem = ({ number, title, description }) => (
    <div className="group border-t border-black py-12 flex flex-col md:flex-row gap-8 md:gap-32 transition-colors hover:bg-neutral-50">
        <span className="font-mono text-sm text-neutral-400 pt-2">{number}</span>
        <div className="flex-1">
            <h3 className="font-serif text-4xl md:text-5xl mb-4 font-light group-hover:translate-x-2 transition-transform duration-500">{title}</h3>
            <p className="text-neutral-500 text-lg max-w-xl leading-relaxed">{description}</p>
        </div>
        <div className="pt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <ArrowUpRight className="w-6 h-6" />
        </div>
    </div>
)

export const BentoGrid = () => {
    return (
        <section className="py-32 bg-white text-black">
            <div className="mx-auto max-w-[1400px] px-6 md:px-12">
                <div className="mb-24">
                    <h2 className="font-serif text-2xl md:text-3xl font-light italic">
                        The Collection
                    </h2>
                </div>

                <div className="flex flex-col">
                    <FeatureItem
                        number="01"
                        title="Strategic Intelligence"
                        description="Understand your market position with absolute clarity. AI-driven insights that cut through the noise."
                    />
                    <FeatureItem
                        number="02"
                        title="Cohort Analysis"
                        description="Segment your audience by behavior, not just demographics. Find the patterns that drive revenue."
                    />
                    <FeatureItem
                        number="03"
                        title="Campaign Execution"
                        description="Launch multi-channel campaigns with precision. Synchronize every move across your entire stack."
                    />
                    <FeatureItem
                        number="04"
                        title="Real-time Analytics"
                        description="Watch your strategy unfold in real-time. Live P&L tracking for every decision you make."
                    />
                </div>
            </div>
        </section>
    )
}
