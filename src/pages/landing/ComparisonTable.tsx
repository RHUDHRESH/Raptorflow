import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, X, ArrowRight, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { IconContent, IconTesting, IconTasks, IconTarget, IconResults, IconSpeed } from '@/components/brand/BrandSystem'

// ═══════════════════════════════════════════════════════════════════════════════
// COMPARISON TABLE - Premium animated before/after comparison
// ═══════════════════════════════════════════════════════════════════════════════

const COMPARISON_ITEMS = [
    {
        feature: 'Content',
        oldWay: 'ChatGPT + pray',
        newWay: 'AI from your strategy',
        Icon: IconContent
    },
    {
        feature: 'Testing',
        oldWay: 'Spreadsheets (maybe)',
        newWay: 'Auto A/B testing',
        Icon: IconTesting
    },
    {
        feature: 'Tasks',
        oldWay: '5+ scattered apps',
        newWay: 'One daily checklist',
        Icon: IconTasks
    },
    {
        feature: 'Strategy',
        oldWay: 'Dusty planning doc',
        newWay: '90-day campaigns',
        Icon: IconTarget
    },
    {
        feature: 'Results',
        oldWay: 'Gut feeling',
        newWay: 'Clear conversion data',
        Icon: IconResults
    },
    {
        feature: 'Speed',
        oldWay: '2-3 hours/asset',
        newWay: '2-3 minutes',
        Icon: IconSpeed
    }
]

export const ComparisonTable = () => {
    const [hoveredRow, setHoveredRow] = useState<number | null>(null)

    return (
        <section className="relative py-24 md:py-32 overflow-hidden">
            {/* Subtle background gradient */}
            <div className="absolute inset-0 bg-gradient-to-b from-background via-muted/20 to-background" />

            <div className="container-editorial relative z-10">
                {/* Header */}
                <motion.div
                    className="max-w-3xl mx-auto text-center mb-16"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <div className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground mb-4">
                        <span className="w-8 h-px bg-border" />
                        The Transformation
                    </div>
                    <h2 className="font-serif text-3xl md:text-5xl font-medium text-foreground">
                        From <span className="text-red-400 line-through opacity-60">chaos</span> to{' '}
                        <span className="text-primary">clarity</span>
                    </h2>
                    <p className="mt-4 text-lg text-muted-foreground">
                        See what changes when you have a system
                    </p>
                </motion.div>

                {/* Comparison container */}
                <div className="max-w-4xl mx-auto">
                    {/* Header badges */}
                    <div className="grid grid-cols-[120px_1fr_1fr] md:grid-cols-[150px_1fr_1fr] gap-4 mb-8">
                        <div></div>
                        <motion.div
                            className="flex justify-center"
                            initial={{ opacity: 0, scale: 0.8 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                        >
                            <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-red-500/10 border border-red-500/20">
                                <X className="w-4 h-4 text-red-400" />
                                <span className="text-red-400 font-medium">Without</span>
                            </div>
                        </motion.div>
                        <motion.div
                            className="flex justify-center"
                            initial={{ opacity: 0, scale: 0.8 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.3 }}
                        >
                            <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-primary/10 border border-primary/20 shadow-lg shadow-primary/10">
                                <Check className="w-4 h-4 text-primary" />
                                <span className="text-primary font-medium">With RaptorFlow</span>
                                <Sparkles className="w-3 h-3 text-primary animate-pulse" />
                            </div>
                        </motion.div>
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
                                            ? "bg-primary/5 border border-primary/20 shadow-lg"
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
                                            className="text-primary"
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
                                                hoveredRow === i && "line-through opacity-50"
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
                                            hoveredRow === i ? "text-primary" : "text-foreground"
                                        )}>
                                            <motion.div
                                                className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center"
                                                animate={hoveredRow === i ? { scale: 1.2, backgroundColor: "hsl(var(--primary) / 0.3)" } : { scale: 1 }}
                                            >
                                                <Check className="w-3 h-3 text-primary" />
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
                        className="my-10 h-px bg-gradient-to-r from-red-400/30 via-primary/50 to-primary/30"
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
                                <div className="text-3xl font-mono font-bold text-primary">{stat.value}</div>
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
                                to="/signup"
                                className="group inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground rounded-2xl font-medium text-lg shadow-xl shadow-primary/25 hover:shadow-2xl hover:shadow-primary/30 transition-all"
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
