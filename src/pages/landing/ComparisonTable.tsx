import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, X, ArrowRight, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { IconContent, IconTesting, IconTasks } from '@/components/brand/BrandSystem'

// ═══════════════════════════════════════════════════════════════════════════════
// COMPARISON TABLE - Premium animated before/after comparison
// ═══════════════════════════════════════════════════════════════════════════════

const COMPARISON_ITEMS = [
    {
        feature: 'Content',
        oldWay: 'ChatGPT + pray',
        newWay: 'AI writes from your strategy',
        Icon: IconContent
    },
    {
        feature: 'Tasks',
        oldWay: '5+ scattered apps',
        newWay: 'One daily checklist',
        Icon: IconTasks
    },
    {
        feature: 'Testing',
        oldWay: 'Hope it works',
        newWay: 'Auto A/B testing',
        Icon: IconTesting
    }
]

export const ComparisonTable = () => {
    const [hoveredRow, setHoveredRow] = useState<number | null>(null)

    return (
        <section className="relative py-24 md:py-32 overflow-hidden bg-background">

            {/* Background gradient */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_30%,rgba(0,0,0,0.02),transparent_60%)]" />

            <div className="container-editorial relative z-10">
                {/* Header */}
                <motion.div
                    className="max-w-3xl mx-auto text-center mb-16"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <div className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground mb-6">
                        <span className="w-8 h-px bg-gradient-to-r from-transparent to-border" />
                        The Transformation
                        <span className="w-8 h-px bg-gradient-to-l from-transparent to-border" />
                    </div>
                    <h2 className="font-serif text-5xl md:text-7xl font-medium text-foreground flex flex-wrap items-center justify-center gap-6">
                        <span className="italic text-muted-foreground/50">chaos</span>
                        <span className="text-muted-foreground/50 text-4xl">→</span>
                        <span className="text-zinc-900 font-medium italic">clarity</span>
                    </h2>
                    <p className="mt-6 text-lg text-muted-foreground">
                        See what changes when you have a system
                    </p>
                </motion.div>

                {/* Comparison container */}
                <div className="max-w-4xl mx-auto">
                    {/* Header badges */}
                    <div className="grid grid-cols-[120px_1fr_1fr] md:grid-cols-[150px_1fr_1fr] gap-4 mb-8">
                        <div></div>
                        <div className="flex justify-center">
                            <div className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-muted border border-border">
                                <X className="w-4 h-4 text-muted-foreground" />
                                <span className="text-muted-foreground font-semibold">Without</span>
                            </div>
                        </div>
                        <div className="flex justify-center">
                            <div className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-zinc-100 border border-zinc-200 shadow-md">
                                <Check className="w-4 h-4 text-zinc-700" />
                                <span className="text-zinc-800 font-semibold">With RaptorFlow</span>
                            </div>
                        </div>
                    </div>

                    {/* Comparison rows */}
                    <div className="space-y-2">
                        {COMPARISON_ITEMS.map((item, i) => {
                            const ItemIcon = item.Icon
                            return (
                                <motion.div
                                    key={item.feature}
                                    className={cn(
                                        "grid grid-cols-[120px_1fr_1fr] md:grid-cols-[150px_1fr_1fr] gap-4 p-4 rounded-2xl transition-all duration-300 cursor-default",
                                        hoveredRow === i
                                            ? "bg-zinc-100 border border-zinc-300 shadow-lg"
                                            : "hover:bg-muted/50"
                                    )}
                                    initial={{ opacity: 0, x: -30 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: 0.1 + i * 0.08 }}
                                    onMouseEnter={() => setHoveredRow(i)}
                                    onMouseLeave={() => setHoveredRow(null)}
                                >
                                    {/* Feature name with icon */}
                                    <div className="flex items-center gap-3">
                                        <motion.div
                                            className="text-zinc-700"
                                            animate={hoveredRow === i ? { scale: 1.2, rotate: 10 } : { scale: 1, rotate: 0 }}
                                            transition={{ type: "spring", stiffness: 400 }}
                                        >
                                            <ItemIcon size={20} />
                                        </motion.div>
                                        <span className="font-medium text-foreground">{item.feature}</span>
                                    </div>

                                    {/* Old way */}
                                    <motion.div
                                        className="flex items-center justify-center"
                                        animate={hoveredRow === i ? { opacity: 0.5, x: -5 } : { opacity: 1, x: 0 }}
                                    >
                                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                            <motion.span
                                                className="w-1.5 h-1.5 rounded-full bg-red-400/60"
                                                animate={hoveredRow === i ? { scale: 0 } : { scale: 1 }}
                                            />
                                            <span className={cn(
                                                "transition-all duration-300",
                                                hoveredRow === i && "line-through opacity-30"
                                            )}>
                                                {item.oldWay}
                                            </span>
                                        </div>
                                    </motion.div>

                                    {/* New way */}
                                    <motion.div
                                        className="flex items-center justify-center"
                                        animate={hoveredRow === i ? { scale: 1.05, x: 5 } : { scale: 1, x: 0 }}
                                    >
                                        <div className={cn(
                                            "flex items-center gap-2 text-sm font-medium transition-all duration-300",
                                            hoveredRow === i ? "text-zinc-900" : "text-foreground"
                                        )}>
                                            <motion.div
                                                className="w-5 h-5 rounded-full bg-zinc-200 flex items-center justify-center"
                                                animate={hoveredRow === i ? { scale: 1.2, backgroundColor: "rgb(212, 212, 216)" } : { scale: 1 }}
                                            >
                                                <Check className="w-3 h-3 text-zinc-700" />
                                            </motion.div>
                                            <span>{item.newWay}</span>
                                        </div>
                                    </motion.div>
                                </motion.div>
                            )
                        })}
                    </div>

                    {/* Animated reveal line */}
                    <motion.div
                        className="my-10 h-px bg-gradient-to-r from-zinc-200 via-zinc-400 to-zinc-200"
                        initial={{ scaleX: 0, opacity: 0 }}
                        whileInView={{ scaleX: 1, opacity: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.2, ease: "easeOut" }}
                    />

                    {/* Summary stats */}
                    <motion.div
                        className="flex flex-wrap justify-center gap-8 mb-10"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.5 }}
                    >
                        {[
                            { value: '70%', label: 'less time on marketing' },
                            { value: '3x', label: 'more content output' },
                            { value: '100%', label: 'clarity on what works' }
                        ].map((stat) => (
                            <motion.div
                                key={stat.label}
                                className="text-center"
                                whileHover={{ y: -3 }}
                            >
                                <div className="text-3xl font-mono font-bold text-zinc-900">{stat.value}</div>
                                <div className="text-sm text-muted-foreground">{stat.label}</div>
                            </motion.div>
                        ))}
                    </motion.div>

                    {/* Bottom CTA */}
                    <motion.div
                        className="text-center"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.6 }}
                    >
                        <motion.div
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <Link
                                to="/app"
                                className="group inline-flex items-center gap-3 px-10 py-5 bg-zinc-900 text-white rounded-2xl font-medium text-lg shadow-xl hover:bg-black hover:shadow-2xl transition-all"
                            >
                                <span>Make the switch</span>
                                <motion.div
                                    animate={{ x: [0, 4, 0] }}
                                    transition={{ duration: 1.5, repeat: Infinity }}
                                >
                                    <ArrowRight className="w-5 h-5" />
                                </motion.div>
                            </Link>
                        </motion.div>
                        <p className="text-sm text-muted-foreground mt-4">
                            Join founders who stopped guessing
                        </p>
                    </motion.div>
                </div>
            </div>
        </section>
    )
}

export default ComparisonTable

