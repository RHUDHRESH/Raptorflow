import React, { useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Target, Calendar, Sparkles, FlaskConical, ArrowRight, Check } from 'lucide-react'
import { Link } from 'react-router-dom'

// ═══════════════════════════════════════════════════════════════════════════════
// WAR ROOM SECTION - Scroll-driven cinematic features
// Left rail: 4 steps with progress | Right: Vignette that changes per step
// ═══════════════════════════════════════════════════════════════════════════════

const STEPS = [
    {
        id: 1,
        title: 'Lock Strategy',
        promise: 'In 10 minutes, get a decision-ready strategy kit.',
        outputs: ['ICP + pain map', 'Offer + proof inventory', 'Messaging spine'],
        proof: 'No strategy, no campaign.',
        cta: 'View Strategy Kit',
        icon: Target
    },
    {
        id: 2,
        title: 'Build the War Plan',
        promise: "A 30–90 day plan that knows what 'success' means.",
        outputs: ['Objective + KPI contract', 'Channel mix + cadence', 'Measurement rules'],
        proof: "If KPI isn't defined, campaign stays Draft.",
        cta: 'See a War Plan',
        icon: Calendar
    },
    {
        id: 3,
        title: 'Generate Ammo',
        promise: 'Assets arrive ready to fire, not drafts you babysit.',
        outputs: ['Post/email/ad/script packs', 'Variants for testing', 'Scheduled execution checklist'],
        proof: 'You ship daily.',
        cta: 'Watch assets generate',
        icon: Sparkles
    },
    {
        id: 4,
        title: 'Kill Weakness',
        promise: 'Winners get promoted. Losers get buried.',
        outputs: ['A/B duels on headlines/CTAs', 'Decision logs', 'Patterns library'],
        proof: 'System compounds weekly.',
        cta: 'See Lab results',
        icon: FlaskConical
    }
]

// Vignette components for each step
const StrategyVignette = () => (
    <div className="space-y-4">
        <div className="bg-white rounded-xl p-5 border border-zinc-200 shadow-sm">
            <div className="text-xs font-bold text-amber-600 uppercase mb-2">ICP Definition</div>
            <div className="text-lg font-semibold text-zinc-900 mb-3">SaaS Founders, $1-5M ARR</div>
            <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-zinc-600">
                    <span className="w-2 h-2 rounded-full bg-red-400" />
                    Pain: Scattered marketing, no system
                </div>
                <div className="flex items-center gap-2 text-sm text-zinc-600">
                    <span className="w-2 h-2 rounded-full bg-red-400" />
                    Pain: Guessing what content works
                </div>
                <div className="flex items-center gap-2 text-sm text-zinc-600">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    Goal: 20 booked calls/month
                </div>
            </div>
        </div>
        <div className="bg-white rounded-xl p-5 border border-zinc-200 shadow-sm">
            <div className="text-xs font-bold text-amber-600 uppercase mb-2">Messaging Spine</div>
            <div className="text-sm text-zinc-600 space-y-1">
                <div><span className="font-medium text-zinc-800">Say:</span> "Stop guessing, start executing"</div>
                <div><span className="font-medium text-zinc-800">Avoid:</span> "AI-powered" (overused)</div>
            </div>
        </div>
    </div>
)

const WarPlanVignette = () => (
    <div className="space-y-4">
        <div className="bg-white rounded-xl p-5 border border-zinc-200 shadow-sm">
            <div className="text-xs font-bold text-amber-600 uppercase mb-2">Campaign: Q1 Lead Gen</div>
            <div className="flex items-center justify-between mb-4">
                <div className="text-3xl font-bold text-zinc-900">0 → 50</div>
                <div className="text-sm text-zinc-500">qualified leads in 30 days</div>
            </div>
            <div className="h-2 bg-zinc-100 rounded-full overflow-hidden">
                <div className="h-full w-1/3 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full" />
            </div>
        </div>
        <div className="bg-white rounded-xl p-5 border border-zinc-200 shadow-sm">
            <div className="text-xs font-bold text-amber-600 uppercase mb-3">Channel Mix</div>
            <div className="grid grid-cols-3 gap-3">
                {['LinkedIn', 'Email', 'Twitter'].map(ch => (
                    <div key={ch} className="text-center p-3 bg-zinc-50 rounded-lg">
                        <div className="text-sm font-medium text-zinc-700">{ch}</div>
                        <div className="text-xs text-zinc-500">3x/week</div>
                    </div>
                ))}
            </div>
        </div>
    </div>
)

const AmmoVignette = () => (
    <div className="space-y-4">
        <div className="bg-white rounded-xl p-5 border border-zinc-200 shadow-sm">
            <div className="text-xs font-bold text-amber-600 uppercase mb-3">Today's Queue</div>
            <div className="space-y-2">
                {[
                    { done: true, text: 'LinkedIn carousel: ICP pain points' },
                    { done: true, text: 'Follow-up email sequence' },
                    { done: false, text: 'Twitter thread: founder story' }
                ].map((task, i) => (
                    <div key={i} className={`flex items-center gap-3 p-3 rounded-lg ${task.done ? 'bg-emerald-50' : 'bg-zinc-50'}`}>
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center ${task.done ? 'bg-emerald-500' : 'border-2 border-zinc-300'}`}>
                            {task.done && <Check className="w-3 h-3 text-white" />}
                        </div>
                        <span className={`text-sm ${task.done ? 'text-zinc-500 line-through' : 'text-zinc-700'}`}>{task.text}</span>
                    </div>
                ))}
            </div>
        </div>
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 border border-amber-200">
            <div className="text-sm font-medium text-amber-800">✨ 3 assets ready to fire</div>
        </div>
    </div>
)

const LabVignette = () => (
    <div className="space-y-4">
        <div className="bg-white rounded-xl p-5 border border-zinc-200 shadow-sm">
            <div className="text-xs font-bold text-amber-600 uppercase mb-3">Active Duel: CTA Button</div>
            <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-zinc-50 rounded-lg text-center">
                    <div className="text-sm font-medium text-zinc-600 mb-2">Variant A</div>
                    <div className="text-xs text-zinc-500 mb-2">"Get Started Free"</div>
                    <div className="text-2xl font-bold text-zinc-400">12%</div>
                </div>
                <div className="p-4 bg-emerald-50 rounded-lg text-center border-2 border-emerald-300">
                    <div className="text-sm font-medium text-emerald-700 mb-2">Variant B 🏆</div>
                    <div className="text-xs text-zinc-500 mb-2">"Start My War Plan"</div>
                    <div className="text-2xl font-bold text-emerald-600">18%</div>
                </div>
            </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-zinc-200 shadow-sm">
            <div className="text-xs font-bold text-zinc-500 uppercase mb-2">Decision Log</div>
            <div className="text-sm text-zinc-600">
                "War" language resonates with ICP. Promoted to default.
            </div>
        </div>
    </div>
)

const VIGNETTES = [StrategyVignette, WarPlanVignette, AmmoVignette, LabVignette]

export const WarRoomSection = () => {
    const containerRef = useRef<HTMLDivElement>(null)
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end end"]
    })

    // Map scroll progress to active step (0-3)
    const activeStepRaw = useTransform(scrollYProgress, [0, 1], [0, 3.5])
    const [activeStep, setActiveStep] = React.useState(0)

    React.useEffect(() => {
        const unsubscribe = activeStepRaw.on("change", (v) => {
            setActiveStep(Math.min(3, Math.max(0, Math.floor(v))))
        })
        return () => unsubscribe()
    }, [activeStepRaw])

    const ActiveVignette = VIGNETTES[activeStep]

    return (
        <section
            ref={containerRef}
            id="war-room"
            className="relative"
            style={{ height: '300vh' }} // Scroll height
        >
            <div
                className="sticky top-0 min-h-screen py-16 overflow-hidden"
                style={{ backgroundColor: '#FDFBF7' }}
            >
                <div className="max-w-7xl mx-auto px-6 h-full">
                    {/* Header */}
                    <div className="text-center mb-12">
                        <span className="text-sm font-semibold text-amber-600 uppercase tracking-wider">
                            The System
                        </span>
                        <h2 className="font-serif text-4xl md:text-5xl text-zinc-900 mt-3 mb-4">
                            How we win the war
                        </h2>
                    </div>

                    {/* Two-column layout */}
                    <div className="grid lg:grid-cols-[35%_65%] gap-12 items-start">
                        {/* Left Rail - Steps */}
                        <div className="relative">
                            {/* Progress line */}
                            <div className="absolute left-[14px] top-0 bottom-0 w-0.5 bg-zinc-200">
                                <motion.div
                                    className="w-full bg-gradient-to-b from-amber-400 to-orange-500 origin-top"
                                    style={{
                                        height: `${((activeStep + 1) / 4) * 100}%`,
                                        transition: 'height 0.3s ease-out'
                                    }}
                                />
                            </div>

                            {/* Steps */}
                            <div className="space-y-8">
                                {STEPS.map((step, i) => {
                                    const isActive = i === activeStep
                                    const isPast = i < activeStep
                                    const StepIcon = step.icon

                                    return (
                                        <motion.div
                                            key={step.id}
                                            className={`relative pl-10 transition-all duration-300 ${isActive ? 'opacity-100' : 'opacity-50'
                                                }`}
                                            animate={{ x: isActive ? 10 : 0 }}
                                        >
                                            {/* Step indicator */}
                                            <div className={`absolute left-0 w-7 h-7 rounded-full flex items-center justify-center transition-all ${isActive
                                                    ? 'bg-gradient-to-br from-amber-400 to-orange-500 shadow-lg shadow-amber-200'
                                                    : isPast
                                                        ? 'bg-amber-100 border-2 border-amber-300'
                                                        : 'bg-zinc-100 border-2 border-zinc-200'
                                                }`}>
                                                {isPast ? (
                                                    <Check className="w-4 h-4 text-amber-600" />
                                                ) : (
                                                    <span className={`text-xs font-bold ${isActive ? 'text-white' : 'text-zinc-400'}`}>
                                                        {step.id}
                                                    </span>
                                                )}
                                            </div>

                                            {/* Content */}
                                            <div>
                                                <h3 className={`text-lg font-bold mb-1 ${isActive ? 'text-zinc-900' : 'text-zinc-500'}`}>
                                                    {step.title}
                                                </h3>

                                                {isActive && (
                                                    <motion.div
                                                        initial={{ opacity: 0, height: 0 }}
                                                        animate={{ opacity: 1, height: 'auto' }}
                                                        transition={{ duration: 0.3 }}
                                                    >
                                                        <p className="text-sm text-zinc-600 mb-3">{step.promise}</p>
                                                        <ul className="space-y-1.5 mb-3">
                                                            {step.outputs.map((output, j) => (
                                                                <li key={j} className="flex items-center gap-2 text-sm text-zinc-700">
                                                                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                                                    {output}
                                                                </li>
                                                            ))}
                                                        </ul>
                                                        <p className="text-xs font-medium text-amber-600 italic mb-3">
                                                            {step.proof}
                                                        </p>
                                                        <Link
                                                            to="/signup"
                                                            className="inline-flex items-center gap-1 text-sm font-semibold text-amber-600 hover:text-amber-700"
                                                        >
                                                            {step.cta} <ArrowRight className="w-4 h-4" />
                                                        </Link>
                                                    </motion.div>
                                                )}
                                            </div>
                                        </motion.div>
                                    )
                                })}
                            </div>
                        </div>

                        {/* Right - Vignette */}
                        <div className="hidden lg:block">
                            <motion.div
                                className="bg-zinc-50 rounded-2xl p-6 border border-zinc-200 min-h-[400px]"
                                key={activeStep}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3 }}
                            >
                                <ActiveVignette />
                            </motion.div>
                        </div>
                    </div>

                    {/* Proof Strip */}
                    <div className="mt-16 pt-8 border-t border-zinc-200">
                        <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12 text-center">
                            {[
                                { value: '1,200+', label: 'campaigns shipped' },
                                { value: '50K', label: 'assets generated' },
                                { value: '+12%', label: 'avg conversion lift' }
                            ].map((stat) => (
                                <div key={stat.label}>
                                    <div className="text-2xl md:text-3xl font-bold text-amber-600">{stat.value}</div>
                                    <div className="text-sm text-zinc-500">{stat.label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}

export default WarRoomSection
