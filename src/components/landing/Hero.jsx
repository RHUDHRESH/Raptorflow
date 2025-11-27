import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { LuxeButton } from '../ui/PremiumUI'

export const Hero = () => {
    return (
        <section className="relative min-h-[90vh] flex items-center justify-center bg-white text-black overflow-hidden">
            {/* Subtle Grain Texture for texture without noise */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>

            <div className="relative z-10 max-w-[1400px] mx-auto px-6 md:px-12 w-full">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-end">

                    {/* Main Headline Area */}
                    <div className="lg:col-span-8">
                        <motion.h1
                            initial={{ opacity: 0, y: 40 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                            className="font-serif text-7xl md:text-9xl lg:text-[10rem] leading-[0.85] tracking-tighter mb-8"
                        >
                            Strategy <br />
                            <span className="italic font-light">Execution.</span>
                        </motion.h1>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                            className="flex flex-col md:flex-row gap-8 md:items-center"
                        >
                            <p className="text-lg md:text-xl font-light max-w-md leading-relaxed text-neutral-600">
                                The operating system for modern agencies.
                                Turn chaos into clarity with a single, elegant platform.
                            </p>

                            <div className="flex items-center gap-4">
                                <LuxeButton className="bg-black text-white hover:bg-neutral-800 rounded-none px-8 py-4 h-auto text-lg transition-all duration-300">
                                    Start Trial
                                </LuxeButton>
                                <button className="group flex items-center gap-2 text-black font-medium border-b border-black pb-0.5 hover:opacity-60 transition-opacity">
                                    View Demo <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </button>
                            </div>
                        </motion.div>
                    </div>

                    {/* Minimalist Visual / Stat */}
                    <div className="lg:col-span-4 flex flex-col justify-end">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 1.2, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
                            className="border-t border-black pt-6"
                        >
                            <div className="flex justify-between items-end mb-2">
                                <span className="text-sm font-mono uppercase tracking-widest text-neutral-500">Efficiency Gain</span>
                                <span className="text-6xl font-light font-serif">312%</span>
                            </div>
                            <p className="text-sm text-neutral-400 max-w-[200px]">
                                Average increase in execution speed for teams using RaptorFlow.
                            </p>
                        </motion.div>
                    </div>
                </div>
            </div>
        </section>
    )
}
