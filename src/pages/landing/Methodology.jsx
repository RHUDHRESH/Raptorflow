import React from 'react'
import { ReactLenis } from 'lenis/react'
import Header from './Header'
import Footer from './Footer'
import CustomCursor from '../../components/CustomCursor'
import { motion } from 'framer-motion'
import { Brain, Target, Layers, ArrowRight } from 'lucide-react'

const Methodology = () => {
  return (
    <section className="py-32 bg-canvas border-b border-line">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
            <div className="text-center mb-24">
                <span className="text-xs uppercase tracking-[0.3em] text-gold font-medium">Our Philosophy</span>
                <h2 className="font-serif text-5xl md:text-7xl text-charcoal mt-6">
                    Deep Work for <br/><span className="italic text-aubergine">Modern Strategy</span>
                </h2>
            </div>

            {/* Bento Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[400px]">
                
                {/* Card 1: The Focus (Large) */}
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="md:col-span-2 bg-charcoal text-canvas p-10 rounded-3xl flex flex-col justify-between relative overflow-hidden group"
                >
                    <div className="absolute inset-0 bg-gradient-to-br from-aubergine/20 to-transparent opacity-50 group-hover:opacity-100 transition-opacity duration-700"></div>
                    <div className="relative z-10">
                        <div className="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center mb-6">
                            <Target className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-serif text-4xl mb-4">Ruthless Prioritization</h3>
                        <p className="text-white/60 text-lg max-w-md leading-relaxed">
                            We believe strategy is about what you <em>don't</em> do. Raptorflow forces you to cut 90% of your ideas to execute the 10% that matter.
                        </p>
                    </div>
                    <div className="relative z-10 flex gap-4 mt-8">
                       <div className="h-32 w-1 bg-gold/50 rounded-full"></div>
                       <div className="h-24 w-1 bg-gold/30 rounded-full"></div>
                       <div className="h-16 w-1 bg-gold/10 rounded-full"></div>
                    </div>
                </motion.div>

                {/* Card 2: The Brain (Tall) */}
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                    className="bg-white border border-charcoal/5 p-10 rounded-3xl flex flex-col justify-between relative overflow-hidden group hover:shadow-2xl transition-shadow duration-500"
                >
                    <div className="absolute -right-10 -top-10 w-40 h-40 bg-gold/10 rounded-full blur-3xl group-hover:bg-gold/20 transition-colors"></div>
                    <div>
                        <div className="w-12 h-12 bg-charcoal/5 rounded-full flex items-center justify-center mb-6 text-charcoal">
                            <Brain className="w-6 h-6" />
                        </div>
                        <h3 className="font-serif text-3xl text-charcoal mb-4">Cognitive Load</h3>
                        <p className="text-charcoal/60">
                            Your brain can only hold 3 strategic priorities at once. Our UI is designed to respect that biological limit.
                        </p>
                    </div>
                    <div className="mt-auto pt-8">
                        <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-charcoal/40">
                            <div className="w-2 h-2 bg-charcoal rounded-full animate-pulse"></div>
                            Optimized
                        </div>
                    </div>
                </motion.div>

                {/* Card 3: The System (Square) */}
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="bg-aubergine text-canvas p-10 rounded-3xl flex flex-col relative overflow-hidden"
                >
                    <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '200px' }}></div>
                    <Layers className="w-8 h-8 mb-6 opacity-80" />
                    <h3 className="font-serif text-3xl mb-2">System > Goals</h3>
                    <p className="text-white/60 text-sm mt-auto">
                        Goals set direction. Systems build progress. We give you the system.
                    </p>
                </motion.div>

                {/* Card 4: The Future (Wide) */}
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 }}
                    className="md:col-span-2 bg-white border border-charcoal/5 p-10 rounded-3xl flex items-center justify-between group hover:border-gold/30 transition-colors"
                >
                    <div className="max-w-lg">
                        <h3 className="font-serif text-3xl text-charcoal mb-4">Ready to deploy?</h3>
                        <p className="text-charcoal/60">
                            Join 500+ founders building with precision.
                        </p>
                    </div>
                    <button className="w-16 h-16 rounded-full bg-charcoal text-white flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        <ArrowRight className="w-6 h-6" />
                    </button>
                </motion.div>

            </div>
        </div>
    </section>
  )
}

export default Methodology
