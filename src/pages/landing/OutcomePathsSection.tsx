import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight, Phone, Users, TrendingUp, Calendar, FileText, ListChecks } from 'lucide-react'
import { Link } from 'react-router-dom'

// ═══════════════════════════════════════════════════════════════════════════════
// OUTCOME PATHS SECTION - Goal-based cards (not personas)
// "Pick your goal. Get a plan. Execute daily."
// Single CTA that updates based on selection
// ═══════════════════════════════════════════════════════════════════════════════

type OutcomeId = 'calls' | 'leads' | 'revenue'

interface Outcome {
    id: OutcomeId
    title: string
    kpi: string
    target: string
    days: string
    deliverables: string[]
    icon: React.ComponentType<{ className?: string }>
}

const OUTCOMES: Outcome[] = [
    {
        id: 'calls',
        title: 'Get Clarity',
        kpi: 'Strategy locked',
        target: 'Chaos → System',
        days: '10 min',
        deliverables: [
            'ICP definition',
            'Messaging framework',
            'First campaign outline'
        ],
        icon: Phone
    },
    {
        id: 'leads',
        title: 'Start Executing',
        kpi: 'Daily tasks done',
        target: '0 → consistent',
        days: 'Daily',
        deliverables: [
            'Daily action checklist',
            'Content calendar',
            'Execution tracker'
        ],
        icon: Users
    },
    {
        id: 'revenue',
        title: 'See Results',
        kpi: 'Conversion data',
        target: 'Guesses → Facts',
        days: 'Ongoing',
        deliverables: [
            'A/B test results',
            'Performance insights',
            'Optimization suggestions'
        ],
        icon: TrendingUp
    }
]

// Preview component for each outcome
const PreviewCard = ({ outcome }: { outcome: Outcome }) => (
    <motion.div
        key={outcome.id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2 }}
        className="bg-white rounded-2xl border border-zinc-200 p-6 shadow-lg"
    >
        <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-zinc-100 flex items-center justify-center">
                <outcome.icon className="w-5 h-5 text-zinc-700" />
            </div>
            <div>
                <div className="text-xs font-bold text-zinc-600 uppercase">{outcome.kpi}</div>
                <div className="text-lg font-bold text-zinc-900">{outcome.target} in {outcome.days}</div>
            </div>
        </div>

        {/* Mini War Plan Preview */}
        <div className="space-y-3 mb-4">
            <div className="flex items-center gap-3 p-3 bg-zinc-50 rounded-lg">
                <Calendar className="w-4 h-4 text-zinc-400" />
                <span className="text-sm text-zinc-600">Campaign: {outcome.days} sprint</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-zinc-50 rounded-lg">
                <FileText className="w-4 h-4 text-zinc-400" />
                <span className="text-sm text-zinc-600">Strategy kit: 1 page</span>
            </div>
            <div className="flex items-center gap-3 p-3 bg-zinc-50 rounded-lg">
                <ListChecks className="w-4 h-4 text-zinc-400" />
                <span className="text-sm text-zinc-600">Today's checklist: 3 tasks</span>
            </div>
        </div>

        {/* What you get */}
        <div className="pt-4 border-t border-zinc-100">
            <div className="text-xs font-bold text-zinc-500 uppercase mb-2">What you get in 15 minutes</div>
            <ul className="space-y-1.5">
                {outcome.deliverables.map((d, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-zinc-600">
                        <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                        {d}
                    </li>
                ))}
            </ul>
        </div>
    </motion.div>
)

export const OutcomePathsSection = () => {
    const [selectedOutcome, setSelectedOutcome] = useState<OutcomeId>('calls')
    const currentOutcome = OUTCOMES.find(o => o.id === selectedOutcome)!

    return (
        <section className="py-24" style={{ backgroundColor: '#FAFAFA' }}>
            <div className="max-w-5xl mx-auto px-6">
                {/* Header */}
                <div className="text-center mb-12">
                    <h2 className="font-serif text-4xl md:text-5xl text-zinc-900 mb-4">
                        The 3-step system
                    </h2>
                    <p className="text-lg text-zinc-500">
                        From chaos to clarity to results
                    </p>
                </div>

                {/* Cards + Preview Layout */}
                <div className="grid lg:grid-cols-[1fr_1.2fr] gap-8 items-start">
                    {/* Goal Cards */}
                    <div className="space-y-4">
                        {OUTCOMES.map((outcome) => {
                            const isSelected = outcome.id === selectedOutcome
                            const Icon = outcome.icon

                            return (
                                <motion.button
                                    key={outcome.id}
                                    onClick={() => setSelectedOutcome(outcome.id)}
                                    className={`w-full text-left p-5 rounded-xl border-2 transition-all ${isSelected
                                        ? 'bg-white border-zinc-900 shadow-lg shadow-zinc-200'
                                        : 'bg-white/50 border-zinc-200 hover:border-zinc-300'
                                        }`}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    <div className="flex items-start gap-4">
                                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${isSelected ? 'bg-zinc-900' : 'bg-zinc-100'
                                            }`}>
                                            <Icon className={`w-6 h-6 ${isSelected ? 'text-white' : 'text-zinc-400'}`} />
                                        </div>
                                        <div>
                                            <div className={`text-lg font-bold ${isSelected ? 'text-zinc-900' : 'text-zinc-600'}`}>
                                                {outcome.title}
                                            </div>
                                            <div className="text-sm text-zinc-500">
                                                {outcome.target} in {outcome.days}
                                            </div>
                                        </div>
                                        {isSelected && (
                                            <motion.div
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                className="ml-auto w-6 h-6 rounded-full bg-zinc-900 flex items-center justify-center"
                                            >
                                                <span className="text-white text-xs">✓</span>
                                            </motion.div>
                                        )}
                                    </div>
                                </motion.button>
                            )
                        })}

                        {/* Not sure link */}
                        <div className="text-center pt-4">
                            <button className="text-sm text-zinc-500 hover:text-zinc-900 underline underline-offset-4">
                                Not sure? Take the 30-second briefing
                            </button>
                        </div>
                    </div>

                    {/* Live Preview */}
                    <div className="hidden lg:block">
                        <AnimatePresence mode="wait">
                            <PreviewCard outcome={currentOutcome} />
                        </AnimatePresence>
                    </div>
                </div>

                {/* Single CTA */}
                <motion.div
                    className="mt-12 text-center"
                    key={selectedOutcome}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <Link
                        to="/signup"
                        className="inline-flex items-center gap-3 px-10 py-5 bg-zinc-900 text-white rounded-2xl font-bold text-lg shadow-xl hover:bg-black hover:shadow-2xl transition-all hover:scale-[1.02]"
                    >
                        Generate my {currentOutcome.title} Plan
                        <ArrowRight className="w-5 h-5" />
                    </Link>
                    <p className="text-sm text-zinc-500 mt-4">
                        Free to start. Ready in 15 minutes.
                    </p>
                </motion.div>
            </div>
        </section>
    )
}

export default OutcomePathsSection

