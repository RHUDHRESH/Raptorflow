import React from 'react'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'
import { Strategy, PencilLine, TrendUp } from '@phosphor-icons/react'

const steps = [
    {
        number: '01',
        icon: Strategy,
        title: 'Define Your Battleground',
        description: 'Answer sharp questions about your market, audience, and positioning. AI synthesizes your answers into a strategic foundation.',
        visual: 'positioning'
    },
    {
        number: '02',
        icon: PencilLine,
        title: 'Generate Your Playbook',
        description: 'Get AI-crafted briefs, campaign frameworks, and content strategies tailored to your unique position.',
        visual: 'content'
    },
    {
        number: '03',
        icon: TrendUp,
        title: 'Execute With Precision',
        description: 'Track your 90-day strategic bets. Focus on 3-5 moves that matter. Let everything else fade.',
        visual: 'execution'
    }
]

const StepVisual = ({ visual, isActive }) => {
    const visualContent = {
        positioning: (
            <div className="grid grid-cols-2 gap-3 p-6">
                <motion.div
                    className="aspect-square bg-gradient-to-br from-amber-500/20 to-amber-600/5 rounded-2xl border border-amber-500/20 flex items-center justify-center"
                    animate={isActive ? { scale: [1, 1.02, 1], opacity: [0.6, 1, 0.6] } : {}}
                    transition={{ duration: 3, repeat: Infinity }}
                >
                    <span className="text-amber-400/60 text-xs uppercase tracking-wider">You</span>
                </motion.div>
                <div className="aspect-square bg-white/[0.02] rounded-2xl border border-white/5" />
                <div className="aspect-square bg-white/[0.02] rounded-2xl border border-white/5" />
                <motion.div
                    className="aspect-square bg-gradient-to-br from-orange-500/20 to-red-600/5 rounded-2xl border border-orange-500/20 flex items-center justify-center"
                    animate={isActive ? { scale: [1, 1.02, 1], opacity: [0.4, 0.8, 0.4] } : {}}
                    transition={{ duration: 3, repeat: Infinity, delay: 0.5 }}
                >
                    <span className="text-orange-400/60 text-xs uppercase tracking-wider">Them</span>
                </motion.div>
            </div>
        ),
        content: (
            <div className="p-6 space-y-3">
                {[1, 0.7, 0.5, 0.8].map((width, i) => (
                    <motion.div
                        key={i}
                        className="h-3 bg-gradient-to-r from-white/10 to-transparent rounded-full"
                        style={{ width: `${width * 100}%` }}
                        initial={{ opacity: 0, x: -20 }}
                        animate={isActive ? { opacity: 1, x: 0 } : { opacity: 0.3, x: 0 }}
                        transition={{ delay: i * 0.1, duration: 0.5 }}
                    />
                ))}
                <motion.div
                    className="mt-6 p-4 bg-amber-500/10 rounded-xl border border-amber-500/20"
                    animate={isActive ? { opacity: [0.5, 1, 0.5] } : {}}
                    transition={{ duration: 2, repeat: Infinity }}
                >
                    <div className="h-2 w-1/2 bg-amber-500/30 rounded-full mb-2" />
                    <div className="h-2 w-3/4 bg-amber-500/20 rounded-full" />
                </motion.div>
            </div>
        ),
        execution: (
            <div className="p-6">
                <div className="flex items-end justify-between gap-3 h-32">
                    {[40, 65, 50, 80, 70, 95].map((height, i) => (
                        <motion.div
                            key={i}
                            className="flex-1 bg-gradient-to-t from-amber-500/40 to-amber-500/10 rounded-t-lg"
                            initial={{ height: 0 }}
                            animate={isActive ? { height: `${height}%` } : { height: `${height * 0.5}%`, opacity: 0.3 }}
                            transition={{ delay: i * 0.1, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                        />
                    ))}
                </div>
                <div className="mt-4 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
            </div>
        )
    }

    return (
        <div className="relative rounded-3xl bg-white/[0.02] border border-white/[0.05] overflow-hidden min-h-[280px]">
            {/* Glow effect */}
            <div className={`absolute inset-0 bg-gradient-radial from-amber-500/10 to-transparent transition-opacity duration-700 ${isActive ? 'opacity-100' : 'opacity-0'}`} />
            {visualContent[visual]}
        </div>
    )
}

const StepItem = ({ step, index, isActive, onClick }) => {
    const Icon = step.icon

    return (
        <motion.button
            onClick={onClick}
            className={`w-full text-left p-6 rounded-2xl border transition-all duration-500 ${isActive
                    ? 'bg-white/[0.03] border-amber-500/30 shadow-[0_0_60px_rgba(245,158,11,0.1)]'
                    : 'bg-transparent border-white/[0.05] hover:border-white/10'
                }`}
            whileHover={{ x: isActive ? 0 : 4 }}
        >
            <div className="flex items-start gap-5">
                {/* Number */}
                <div className={`text-4xl font-light transition-colors duration-500 ${isActive ? 'text-amber-400' : 'text-white/20'}`}>
                    {step.number}
                </div>

                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <div className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-500 ${isActive ? 'bg-amber-500/20 border border-amber-500/30' : 'bg-white/5 border border-white/10'
                            }`}>
                            <Icon className={`w-5 h-5 transition-colors ${isActive ? 'text-amber-400' : 'text-white/40'}`} weight="duotone" />
                        </div>
                        <h3 className={`text-xl font-light transition-colors ${isActive ? 'text-white' : 'text-white/60'}`}>
                            {step.title}
                        </h3>
                    </div>

                    <p className={`text-sm leading-relaxed transition-all duration-500 ${isActive ? 'text-white/60 max-h-20 opacity-100' : 'text-white/30 max-h-0 opacity-0 overflow-hidden'}`}>
                        {step.description}
                    </p>
                </div>
            </div>
        </motion.button>
    )
}

const HowItWorks = () => {
    const ref = useRef(null)
    const isInView = useInView(ref, { once: true, margin: '-100px' })
    const [activeStep, setActiveStep] = React.useState(0)

    // Auto-advance every 5 seconds
    React.useEffect(() => {
        const timer = setInterval(() => {
            setActiveStep(prev => (prev + 1) % steps.length)
        }, 5000)
        return () => clearInterval(timer)
    }, [])

    return (
        <section ref={ref} className="py-32 relative">
            {/* Background elements */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/4 left-0 w-96 h-96 bg-gradient-radial from-amber-500/5 to-transparent blur-3xl" />
                <div className="absolute bottom-1/4 right-0 w-96 h-96 bg-gradient-radial from-orange-500/5 to-transparent blur-3xl" />
            </div>

            <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.8 }}
                    className="text-center mb-20"
                >
                    <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium mb-6">
                        <span className="w-8 h-px bg-gradient-to-r from-transparent via-amber-500 to-transparent" />
                        The Process
                        <span className="w-8 h-px bg-gradient-to-r from-transparent via-amber-500 to-transparent" />
                    </span>

                    <h2 className="text-5xl md:text-6xl font-light text-white leading-tight">
                        From chaos to
                        <span className="block italic bg-gradient-to-r from-amber-300 via-amber-400 to-orange-400 text-transparent bg-clip-text">
                            strategic clarity
                        </span>
                    </h2>
                </motion.div>

                {/* Content Grid */}
                <div className="grid lg:grid-cols-2 gap-12 items-start">

                    {/* Steps List */}
                    <motion.div
                        initial={{ opacity: 0, x: -30 }}
                        animate={isInView ? { opacity: 1, x: 0 } : {}}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="space-y-4"
                    >
                        {steps.map((step, index) => (
                            <StepItem
                                key={step.number}
                                step={step}
                                index={index}
                                isActive={activeStep === index}
                                onClick={() => setActiveStep(index)}
                            />
                        ))}
                    </motion.div>

                    {/* Visual */}
                    <motion.div
                        initial={{ opacity: 0, x: 30 }}
                        animate={isInView ? { opacity: 1, x: 0 } : {}}
                        transition={{ duration: 0.8, delay: 0.3 }}
                        className="lg:sticky lg:top-32"
                    >
                        <StepVisual
                            visual={steps[activeStep].visual}
                            isActive={true}
                        />

                        {/* Progress bar */}
                        <div className="mt-8 flex gap-2">
                            {steps.map((_, i) => (
                                <button
                                    key={i}
                                    onClick={() => setActiveStep(i)}
                                    className={`h-1 flex-1 rounded-full transition-all duration-500 ${i === activeStep ? 'bg-amber-500' : 'bg-white/10 hover:bg-white/20'
                                        }`}
                                />
                            ))}
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    )
}

export default HowItWorks
