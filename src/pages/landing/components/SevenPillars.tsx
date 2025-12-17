import React from 'react'
import { motion } from 'framer-motion'
import { Brain, Target, Crosshair, Zap, BarChart2, Repeat, Flag } from 'lucide-react'

// "Seven Pillars" - The strategic framework
const PILLARS = [
    { icon: Brain, title: "Psychology", desc: "Understand behavior." },
    { icon: Target, title: "Positioning", desc: "Own your lane." },
    { icon: Crosshair, title: "Targeting", desc: "Find your tribe." },
    { icon: Zap, title: "Offer", desc: "Make it irresistible." },
    { icon: BarChart2, title: "Economics", desc: "Know your numbers." },
    { icon: Repeat, title: "Funnel", desc: "Capture value." },
    { icon: Flag, title: "Identity", desc: "Build a legacy." }
]

export const SevenPillars = () => {
    return (
        <section className="py-24 bg-card border-y border-border relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/5 via-background to-background" />

            <div className="container-editorial relative z-10">
                <div className="text-center max-w-2xl mx-auto mb-16">
                    <div className="inline-block px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider mb-4">
                        The Framework
                    </div>
                    <h2 className="font-serif text-3xl md:text-5xl font-medium mb-4">
                        The 7 Pillars of <span className="text-primary">War</span>
                    </h2>
                    <p className="text-muted-foreground text-lg">
                        Strategy isn't magic. It's a structure. We force you to answer the hard questions.
                    </p>
                </div>

                <div className="flex flex-wrap justify-center gap-6">
                    {PILLARS.map((pillar, i) => (
                        <motion.div
                            key={i}
                            className="group relative w-[160px] h-[160px] rounded-2xl bg-background border border-border hover:border-primary/50 flex flex-col items-center justify-center p-4 text-center transition-all duration-300"
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.1 }}
                            whileHover={{ y: -5, scale: 1.05 }}
                        >
                            <div className="w-10 h-10 rounded-full bg-muted group-hover:bg-primary/10 flex items-center justify-center mb-3 transition-colors">
                                <pillar.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                            </div>
                            <h4 className="font-bold text-foreground mb-1">{pillar.title}</h4>
                            <p className="text-xs text-muted-foreground">{pillar.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    )
}
