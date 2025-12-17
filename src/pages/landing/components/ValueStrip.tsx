import React from 'react'
import { motion } from 'framer-motion'

const LOGOS = [
    "Linear", "Notion", "Slack", "OpenAI", "Stripe", "PostHog"
]

export const ValueStrip = () => {
    return (
        <section className="py-12 border-b border-border bg-background/50">
            <div className="container px-6 mx-auto">
                <p className="text-center text-xs font-bold text-muted-foreground uppercase tracking-widest mb-8">
                    Integrates with the modern stack
                </p>
                <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
                    {/* Placeholder for Logos - using text for now, but would normally be SVGs */}
                    {LOGOS.map((logo) => (
                        <span key={logo} className="text-xl font-bold font-serif text-foreground/40 hover:text-foreground transition-colors cursor-default">
                            {logo}
                        </span>
                    ))}
                </div>
            </div>
        </section>
    )
}
