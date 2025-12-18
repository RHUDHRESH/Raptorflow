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
        title: 'Build the Execution Plan',
        promise: "A 30–90 day plan that knows what 'success' means.",
        outputs: ['Objective + KPI contract', 'Channel mix + cadence', 'Measurement rules'],
        proof: "If KPI isn't defined, campaigns stay Draft.",
        cta: 'See a Growth Plan',
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
    <div className="space-y-6">
        <div className="bg-zinc-900 rounded-2xl p-6 border border-zinc-800 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-red-500/5 -mr-12 -mt-12 rounded-full blur-xl" />
            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4">Command: ICP Strategy</div>
            <div className="text-xl font-medium text-white mb-4">SaaS Founders <span className="text-zinc-500 text-sm ml-2">$1-5M ARR</span></div>
            <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm text-zinc-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                    Pain: Fragmented execution
                </div>
                <div className="flex items-center gap-3 text-sm text-zinc-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                    Pain: Low-intent lead fatigue
                </div>
            </div>
        </div>
        <div className="bg-white rounded-2xl p-6 border border-zinc-200 shadow-xl">
            <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-[0.2em] mb-4 text-center">Messaging Spine</div>
            <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-zinc-50 rounded-xl border border-zinc-100">
                    <div className="text-[10px] font-bold text-zinc-400 mb-1 uppercase">Say</div>
                    <div className="text-xs text-zinc-900 font-medium">"System over hacks"</div>
                </div>
                <div className="p-3 bg-zinc-50 rounded-xl border border-zinc-100">
                    <div className="text-[10px] font-bold text-zinc-400 mb-1 uppercase">Avoid</div>
                    <div className="text-xs text-zinc-500">Generic AI fluff</div>
                </div>
            </div>
        </div>
    </div>
)

const WarPlanVignette = () => (
    <div className="space-y-6">
        <div className="bg-zinc-900 rounded-2xl p-8 border border-zinc-800 shadow-2xl">
            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4">Command: Growth Contract</div>
            <div className="flex items-end justify-between mb-6">
                <div>
                    <div className="text-4xl font-bold text-white tracking-tighter">0 → 50</div>
                    <div className="text-[10px] text-zinc-500 uppercase font-bold mt-1">Qualified Opps / 30D</div>
                </div>
                <div className="text-right">
                    <div className="text-xl font-medium text-zinc-400">34% <span className="text-xs align-top">↑</span></div>
                    <div className="text-[10px] text-zinc-500 uppercase font-bold">Velocity</div>
                </div>
            </div>
            <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '45%' }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="h-full bg-white shadow-[0_0_10px_white]"
                />
            </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-2xl p-4 border border-zinc-200">
                <div className="text-[10px] font-bold text-zinc-400 uppercase mb-2">Phase 01</div>
                <div className="text-sm font-bold text-zinc-900">Foundational Scale</div>
            </div>
            <div className="bg-white rounded-2xl p-4 border border-zinc-200">
                <div className="text-[10px] font-bold text-zinc-400 uppercase mb-2">Phase 02</div>
                <div className="text-sm font-bold text-zinc-400">Aggressive Capture</div>
            </div>
        </div>
    </div>
)

const AmmoVignette = () => (
    <div className="space-y-4">
        <div className="bg-zinc-900 rounded-2xl p-6 border border-zinc-800 shadow-2xl relative overflow-hidden">
            <div className="absolute inset-0 opacity-[0.05]" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '20px 20px' }} />
            <div className="relative z-10">
                <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-4">Daily Sync: Assets Ready</div>
                <div className="space-y-3">
                    {[
                        { done: true, text: 'Landing V2: Optimized messaging' },
                        { done: true, text: 'Campaign AMMO: Variant 04' },
                        { done: false, text: 'Strategic Outbound: Batch 01' }
                    ].map((task, i) => (
                        <div key={i} className={`flex items-center gap-3 p-3 rounded-xl border ${task.done ? 'bg-zinc-800/50 border-zinc-700/50' : 'bg-white border-zinc-200'}`}>
                            <div className={`w-5 h-5 rounded-full flex items-center justify-center ${task.done ? 'bg-zinc-700' : 'border-2 border-zinc-300'}`}>
                                {task.done && <Check className="w-3 h-3 text-zinc-400" />}
                            </div>
                            <span className={`text-xs font-medium ${task.done ? 'text-zinc-500 line-through' : 'text-zinc-900'}`}>{task.text}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
        <div className="flex items-center justify-between p-4 bg-white rounded-2xl border border-zinc-200 shadow-lg">
            <div className="text-xs font-bold text-zinc-900 uppercase tracking-widest">System Status</div>
            <div className="flex items-center gap-2">
                <motion.div
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="w-2 h-2 rounded-full bg-red-500"
                />
                <span className="text-[10px] font-bold text-zinc-500 uppercase">Operational</span>
            </div>
        </div>
    </div>
)

const LabVignette = () => (
    <div className="space-y-6">
        <div className="bg-zinc-900 rounded-2xl p-8 border border-zinc-800 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4">
                <div className="px-2 py-1 rounded bg-red-500/10 border border-red-500/20 text-[8px] font-bold text-red-500 uppercase">Live Duel</div>
            </div>
            <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-6">Execution Analytics</div>
            <div className="grid grid-cols-2 gap-6 relative z-10">
                <div className="space-y-2">
                    <div className="text-[10px] font-bold text-zinc-600 uppercase">Variant A</div>
                    <div className="text-2xl font-bold text-zinc-500 tracking-tighter line-through">12.4%</div>
                </div>
                <div className="space-y-2">
                    <div className="text-[10px] font-bold text-white uppercase flex items-center gap-1.5">
                        Variant B
                        <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                    </div>
                    <div className="text-3xl font-bold text-white tracking-tighter">18.9%</div>
                </div>
            </div>
            <div className="mt-8 pt-6 border-t border-zinc-800">
                <div className="text-[10px] font-bold text-zinc-500 uppercase mb-2">Decision Log</div>
                <p className="text-xs text-zinc-400 italic">"Variant B promoted to Default. Resonates 52% higher with Founders."</p>
            </div>
        </div>
        <div className="flex gap-4">
            <div className="flex-1 h-1 bg-zinc-800 rounded-full" />
            <div className="flex-1 h-1 bg-zinc-800 rounded-full" />
            <div className="flex-1 h-1 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.4)]" />
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
            id="execution-system"
            className="relative"
            style={{ height: '250vh' }}
        >
            <div
                className="sticky top-0 min-h-screen py-16 overflow-hidden flex flex-col justify-center"
                style={{ backgroundColor: '#ffffff' }}
            >
                {/* Cinematic Background for this specific section */}
                <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.03]">
                    <div
                        className="absolute inset-0"
                        style={{
                            backgroundImage: 'radial-gradient(circle at 2px 2px, black 1px, transparent 0)',
                            backgroundSize: '40px 40px'
                        }}
                    />
                </div>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(0,0,0,0.03)_0%,transparent_70%)] pointer-events-none" />

                <div className="max-w-7xl mx-auto px-6 h-full relative z-10 w-full">
                    {/* Header */}
                    <div className="text-center mb-20 max-w-3xl mx-auto">
                        <motion.span
                            initial={{ opacity: 0, y: 10 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            className="text-xs font-bold text-zinc-400 uppercase tracking-[0.3em] mb-4 block"
                        >
                            The Operating System
                        </motion.span>
                        <motion.h2
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="font-serif text-5xl md:text-7xl text-zinc-900 mt-3 mb-6 tracking-tight"
                        >
                            The 90-Day <span className="italic">War Plan</span>
                        </motion.h2>
                        <motion.p
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="text-lg text-zinc-500 leading-relaxed"
                        >
                            Strategic marketing isn't about hope. It's about a definitive operating cadence that turns strategy into daily wins.
                        </motion.p>
                    </div>

                    {/* Two-column layout */}
                    <div className="grid lg:grid-cols-[35%_65%] gap-12 items-start">
                        {/* Left Rail - Steps */}
                        <div className="relative">
                            {/* Progress line */}
                            <div className="absolute left-[14px] top-0 bottom-0 w-0.5 bg-zinc-200">
                                <motion.div
                                    className="w-full bg-zinc-800 origin-top"
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

                                    return (
                                        <motion.div
                                            key={step.id}
                                            className={`relative pl-10 transition-all duration-300 ${isActive ? 'opacity-100' : 'opacity-50'
                                                }`}
                                            animate={{ x: isActive ? 10 : 0 }}
                                        >
                                            {/* Step indicator */}
                                            <div className={`absolute left-0 w-7 h-7 rounded-full flex items-center justify-center transition-all ${isActive
                                                ? 'bg-zinc-900 shadow-lg shadow-zinc-300'
                                                : isPast
                                                    ? 'bg-zinc-100 border-2 border-zinc-300'
                                                    : 'bg-zinc-100 border-2 border-zinc-200'
                                                }`}>
                                                {isPast ? (
                                                    <Check className="w-4 h-4 text-zinc-700" />
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
                                                                    <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
                                                                    {output}
                                                                </li>
                                                            ))}
                                                        </ul>
                                                        <p className="text-xs font-medium text-zinc-600 italic mb-3">
                                                            {step.proof}
                                                        </p>
                                                        <Link
                                                            to="/signup"
                                                            className="inline-flex items-center gap-1 text-sm font-semibold text-zinc-900 hover:underline"
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
                        <div className="hidden lg:block relative">
                            <motion.div
                                className="bg-zinc-50/50 backdrop-blur-sm rounded-3xl p-8 border border-zinc-200 min-h-[450px] flex items-center justify-center shadow-inner"
                                key={activeStep}
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ duration: 0.4, ease: "easeOut" }}
                            >
                                <div className="w-full">
                                    <ActiveVignette />
                                </div>
                            </motion.div>
                        </div>
                    </div>

                    {/* Proof Strip */}
                    <div className="mt-20 pt-10 border-t border-zinc-100">
                        <div className="flex flex-wrap justify-center items-center gap-12 text-center">
                            {[
                                { value: '1,200+', label: 'war plans active' },
                                { value: '50K', label: 'moves executed' },
                                { value: '+24%', label: 'compound growth' }
                            ].map((stat) => (
                                <div key={stat.label}>
                                    <div className="text-3xl font-bold font-serif text-zinc-900">{stat.value}</div>
                                    <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest mt-1">{stat.label}</div>
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
