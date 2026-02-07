import React, { useState, useRef, useEffect } from 'react'
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion'
import ScrambleText from '../../components/ScrambleText'

const HowItWorks = () => {
    const [activeStep, setActiveStep] = useState(0)

    const steps = [
        {
            num: '01',
            title: 'Intake',
            desc: 'Plug in your answers, site, and deck. We map it across audience, value, differentiation, competition, discovery, remarkability, and proof.'
        },
        {
            num: '02',
            title: 'War plan',
            desc: 'Raptorflow drafts a 90-day plan broken into 3 phases and 3–5 moves, aligned to your goals and constraints.'
        },
        {
            num: '03',
            title: 'Execution',
            desc: 'Muse-style briefs turn each move into emails, pages, scripts, and posts your team or tools can execute without re-thinking strategy.'
        }
    ]

    return (
        <section id="how-it-works" className="py-16 md:py-24 border-b border-line bg-canvas relative overflow-hidden">
            {/* Subtle background glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-gold/5 to-aubergine/5 blur-3xl"></div>

            <div className="max-w-7xl mx-auto px-6 md:px-8 relative z-10">
                <div className="flex flex-col lg:flex-row gap-16 lg:gap-24">

                    {/* Sticky Left Panel (Title + Visual) */}
                    <div className="lg:w-1/2 lg:h-screen lg:sticky lg:top-0 flex flex-col justify-center py-12">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            className="mb-12"
                        >
                            <div className="flex items-center gap-3 mb-6">
                                <div className="w-12 h-px bg-gold"></div>
                                <p className="text-[10px] uppercase tracking-[0.3em] text-gold font-semibold">
                                    How it works
                                </p>
                            </div>
                            <h2 className="font-serif text-4xl md:text-5xl leading-[1.1] mb-6 text-charcoal">
                                From chaos to<br />
                                <span className="italic text-aubergine">clarity.</span>
                            </h2>
                            <p className="text-base text-charcoal/80 leading-relaxed font-sans font-light max-w-sm">
                                A structured conversation that turns your loose ideas into a battle-ready 90-day map.
                            </p>
                        </motion.div>

                        {/* Dynamic Visual Container */}
                        <div className="w-full aspect-[4/3] bg-white border border-line rounded-3xl shadow-2xl relative overflow-hidden p-8">
                            <AnimatePresence mode="wait">
                                {activeStep === 0 && (
                                    <motion.div
                                        key="step1"
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -20 }}
                                        transition={{ duration: 0.5 }}
                                        className="h-full flex flex-col gap-4"
                                    >
                                        {/* Intake Form Visual */}
                                        <div className="w-1/3 h-4 bg-charcoal/10 rounded-full mb-4"></div>
                                        <div className="space-y-3">
                                            <div className="h-10 w-full border border-line rounded-lg bg-canvas/50"></div>
                                            <div className="h-10 w-full border border-line rounded-lg bg-canvas/50"></div>
                                            <div className="h-24 w-full border border-line rounded-lg bg-canvas/50"></div>
                                        </div>
                                        <div className="mt-auto flex justify-end">
                                            <div className="h-10 w-24 bg-aubergine rounded-full"></div>
                                        </div>
                                    </motion.div>
                                )}
                                {activeStep === 1 && (
                                    <motion.div
                                        key="step2"
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -20 }}
                                        transition={{ duration: 0.5 }}
                                        className="h-full relative"
                                    >
                                        {/* War Map Visual */}
                                        <div className="flex gap-4 mb-6">
                                            <div className="flex-1 h-32 bg-gold/10 rounded-xl border border-gold/20 p-3">
                                                <div className="w-8 h-8 bg-gold/20 rounded-full mb-2"></div>
                                                <div className="w-16 h-2 bg-gold/30 rounded-full"></div>
                                            </div>
                                            <div className="flex-1 h-32 bg-charcoal/5 rounded-xl border border-charcoal/10 p-3 mt-8">
                                                <div className="w-8 h-8 bg-charcoal/20 rounded-full mb-2"></div>
                                                <div className="w-16 h-2 bg-charcoal/30 rounded-full"></div>
                                            </div>
                                        </div>
                                        <div className="h-px w-full bg-line mb-4"></div>
                                        <div className="flex justify-between">
                                            <div className="w-8 h-8 rounded-full border border-line"></div>
                                            <div className="w-8 h-8 rounded-full border border-line"></div>
                                            <div className="w-8 h-8 rounded-full border border-line"></div>
                                        </div>
                                    </motion.div>
                                )}
                                {activeStep === 2 && (
                                    <motion.div
                                        key="step3"
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -20 }}
                                        transition={{ duration: 0.5 }}
                                        className="h-full bg-white border border-line shadow-sm p-6 rotate-[-2deg] scale-95 origin-center"
                                    >
                                        {/* Brief Visual */}
                                        <div className="w-12 h-12 bg-aubergine/10 rounded-full flex items-center justify-center mb-6">
                                            <span className="font-serif italic text-aubergine text-xl">Aa</span>
                                        </div>
                                        <div className="space-y-3">
                                            <div className="h-6 w-3/4 bg-charcoal/80 rounded-sm"></div>
                                            <div className="h-3 w-full bg-charcoal/20 rounded-sm"></div>
                                            <div className="h-3 w-full bg-charcoal/20 rounded-sm"></div>
                                            <div className="h-3 w-2/3 bg-charcoal/20 rounded-sm"></div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Overlay Gradient */}
                            <div className="absolute inset-0 bg-gradient-to-t from-white/50 to-transparent pointer-events-none"></div>
                        </div>
                    </div>

                    {/* Scrollable Right Panel (Steps) */}
                    <div className="lg:w-1/2 lg:py-12 space-y-32">
                        {steps.map((step, index) => (
                            <StepCard
                                key={index}
                                step={step}
                                index={index}
                                onActive={() => setActiveStep(index)}
                            />
                        ))}
                        <div className="h-[20vh]"></div> {/* Spacer for last item */}
                    </div>

                </div>
            </div>
        </section>
    )
}

const StepCard = ({ step, index, onActive }) => {
    const ref = useRef(null)
    const { scrollYProgress } = useScroll({
        target: ref,
        offset: ["start center", "end center"]
    })

    useEffect(() => {
        const unsubscribe = scrollYProgress.on("change", (v) => {
            if (v > 0 && v < 1) {
                onActive()
            }
        })
        return () => unsubscribe()
    }, [scrollYProgress, onActive])

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0.2 }}
            whileInView={{ opacity: 1 }}
            viewport={{ margin: "-20% 0px -20% 0px" }}
            transition={{ duration: 0.5 }}
            className="flex flex-col sm:flex-row gap-8 p-8 rounded-3xl border border-transparent hover:border-line/50 transition-colors"
        >
            <div className="relative flex-shrink-0">
                <div className="relative w-20 h-20 rounded-2xl bg-white border border-gold/30 flex items-center justify-center shadow-sm">
                    <span className="font-serif text-4xl font-bold text-aubergine">
                        <ScrambleText text={step.num} />
                    </span>
                </div>
            </div>

            <div className="pt-2">
                <h3 className="text-3xl font-serif text-charcoal mb-4">
                    {step.title}
                </h3>
                <p className="text-lg text-charcoal/80 leading-relaxed font-sans font-light">
                    {step.desc}
                </p>
            </div>
        </motion.div>
    )
}

export default HowItWorks
