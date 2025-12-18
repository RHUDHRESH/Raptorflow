import React, { useRef, useState } from 'react'
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion'

const LiveMatrix = () => {
  const ref = useRef(null)
  const [activeZone, setActiveZone] = useState(null)
  
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  })

  const rotateX = useTransform(scrollYProgress, [0, 0.5, 1], [15, 0, -15])
  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.9, 1, 0.9])
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0])

  return (
    <section className="py-32 border-b border-line bg-charcoal relative overflow-hidden perspective-1000">
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-20" style={{ 
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
        backgroundSize: '40px 40px'
      }}></div>

      <div className="max-w-7xl mx-auto px-6 md:px-8 lg:px-12 relative z-10">
        <div className="text-center mb-20">
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-[10px] uppercase tracking-[0.3em] text-gold font-bold mb-4"
          >
            The Control Room
          </motion.p>
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="font-serif text-4xl md:text-5xl lg:text-6xl text-white"
          >
            Interactive Intelligence.<br /><span className="text-white/50">Hover to explore.</span>
          </motion.h2>
        </div>

        {/* 3D Dashboard Interface */}
        <div ref={ref} className="relative h-[600px] md:h-[800px] perspective-1000 flex items-center justify-center">
          <motion.div 
            style={{ rotateX, scale, opacity }}
            className="relative w-full h-full bg-charcoal/80 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl overflow-hidden group"
          >
            {/* Fake Dashboard UI */}
            <div className="absolute inset-0 p-6 grid grid-cols-12 gap-6">
                
                {/* Sidebar - Zone 1 */}
                <div 
                    className="col-span-2 border-r border-white/10 hidden md:block space-y-6 hover:bg-white/5 transition-colors rounded-l-xl p-2 cursor-pointer relative"
                    onMouseEnter={() => setActiveZone('sidebar')}
                    onMouseLeave={() => setActiveZone(null)}
                >
                    <div className="w-8 h-8 rounded-full bg-gold/20"></div>
                    <div className="space-y-3">
                        {[1,2,3,4,5].map(i => (
                            <div key={i} className="h-2 w-3/4 bg-white/10 rounded-full"></div>
                        ))}
                    </div>
                    
                    <AnimatePresence>
                        {activeZone === 'sidebar' && (
                            <motion.div 
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -10 }}
                                className="absolute left-full top-0 ml-4 w-48 bg-white/10 backdrop-blur-xl p-4 rounded-xl border border-white/20 text-white z-50"
                            >
                                <h4 className="font-serif text-gold mb-1">Navigation</h4>
                                <p className="text-xs text-white/60">Quick access to your 90-day war map and active briefs.</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Main Content */}
                <div className="col-span-12 md:col-span-10 grid grid-cols-3 gap-6 content-start">
                    
                    {/* Header - Zone 2 */}
                    <div 
                        className="col-span-3 h-12 border-b border-white/10 flex items-center justify-between mb-4 px-2 cursor-pointer hover:bg-white/5 rounded-lg transition-colors relative"
                        onMouseEnter={() => setActiveZone('header')}
                        onMouseLeave={() => setActiveZone(null)}
                    >
                        <div className="h-4 w-32 bg-white/20 rounded-full"></div>
                        <div className="flex gap-2">
                            <div className="h-8 w-8 rounded-full bg-white/10"></div>
                            <div className="h-8 w-8 rounded-full bg-white/10"></div>
                        </div>

                        <AnimatePresence>
                            {activeZone === 'header' && (
                                <motion.div 
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="absolute top-full right-0 mt-2 w-48 bg-white/10 backdrop-blur-xl p-4 rounded-xl border border-white/20 text-white z-50"
                                >
                                    <h4 className="font-serif text-gold mb-1">Team Pulse</h4>
                                    <p className="text-xs text-white/60">Real-time status of who is executing which move.</p>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Stat Cards - Zone 3 */}
                    {[1,2,3].map(i => (
                        <div 
                            key={i} 
                            className="h-32 rounded-xl bg-white/5 border border-white/10 p-4 hover:border-gold/50 hover:bg-white/10 transition-all cursor-pointer relative"
                            onMouseEnter={() => setActiveZone(`stat-${i}`)}
                            onMouseLeave={() => setActiveZone(null)}
                        >
                            <div className="h-3 w-12 bg-white/20 rounded-full mb-4"></div>
                            <div className="h-8 w-24 bg-white/10 rounded-full mb-2"></div>
                            <div className="h-2 w-full bg-white/5 rounded-full mt-8">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    whileInView={{ width: "70%" }}
                                    transition={{ duration: 1.5 }}
                                    className="h-full bg-gold/50 rounded-full"
                                ></motion.div>
                            </div>

                            <AnimatePresence>
                                {activeZone === `stat-${i}` && (
                                    <motion.div 
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.9 }}
                                        className="absolute inset-0 bg-charcoal/90 backdrop-blur-sm flex items-center justify-center rounded-xl border border-gold/30"
                                    >
                                        <div className="text-center">
                                            <div className="text-gold font-serif text-xl">Metric #{i}</div>
                                            <div className="text-xs text-white/60">+24% WoW</div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ))}

                    {/* Big Chart - Zone 4 */}
                    <div 
                        className="col-span-3 md:col-span-2 h-64 rounded-xl bg-white/5 border border-white/10 p-6 relative overflow-hidden cursor-crosshair group/chart"
                        onMouseEnter={() => setActiveZone('chart')}
                        onMouseLeave={() => setActiveZone(null)}
                    >
                        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-gold/20 to-transparent clip-path-polygon"></div>
                        {/* CSS Chart Representation */}
                        <div className="flex items-end justify-between h-full gap-2 pb-4 px-4">
                            {[40, 60, 45, 70, 55, 80, 65, 85, 75, 90, 100].map((h, idx) => (
                                <motion.div 
                                    key={idx}
                                    initial={{ height: 0 }}
                                    whileInView={{ height: `${h}%` }}
                                    transition={{ duration: 1, delay: idx * 0.05 }}
                                    className="w-full bg-white/10 rounded-t-sm group-hover/chart:bg-gold/60 transition-colors"
                                ></motion.div>
                            ))}
                        </div>

                        <AnimatePresence>
                            {activeZone === 'chart' && (
                                <motion.div 
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="absolute top-4 right-4 bg-gold/20 text-gold text-xs uppercase tracking-widest px-3 py-1 rounded-full border border-gold/30 backdrop-blur-md"
                                >
                                    Live Velocity
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Activity Feed - Zone 5 */}
                    <div 
                        className="col-span-3 md:col-span-1 h-64 rounded-xl bg-white/5 border border-white/10 p-4 space-y-3 hover:border-aubergine/50 transition-colors cursor-pointer relative overflow-hidden"
                        onMouseEnter={() => setActiveZone('feed')}
                        onMouseLeave={() => setActiveZone(null)}
                    >
                        <div className="h-3 w-20 bg-white/20 rounded-full mb-4"></div>
                        {[1,2,3,4].map(i => (
                            <div key={i} className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-white/10"></div>
                                <div className="space-y-1 flex-1">
                                    <div className="h-2 w-full bg-white/10 rounded-full"></div>
                                    <div className="h-2 w-1/2 bg-white/5 rounded-full"></div>
                                </div>
                            </div>
                        ))}
                        
                        <AnimatePresence>
                            {activeZone === 'feed' && (
                                <motion.div 
                                    initial={{ y: "100%" }}
                                    animate={{ y: 0 }}
                                    exit={{ y: "100%" }}
                                    className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-charcoal via-charcoal/90 to-transparent p-4"
                                >
                                    <button className="w-full py-2 bg-gold text-charcoal text-xs font-bold uppercase tracking-widest rounded-lg hover:bg-white transition-colors">
                                        View All Updates
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                </div>
            </div>

            {/* Reflection/Glow */}
            <div className="absolute inset-0 bg-gradient-to-tr from-gold/10 via-transparent to-transparent pointer-events-none"></div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

export default LiveMatrix

