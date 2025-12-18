import React, { useRef } from 'react'
import { motion, useScroll, useTransform, useMotionValue } from 'framer-motion'
import Scene3D from './Scene3D'

const MagneticButton = ({ children, className = "", onClick = undefined }) => {
  const ref = useRef(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const handleMouseMove = (e) => {
    const { clientX, clientY } = e
    const { left, top, width, height } = ref.current.getBoundingClientRect()
    const centerX = left + width / 2
    const centerY = top + height / 2
    x.set((clientX - centerX) * 0.3) // Magnetic strength
    y.set((clientY - centerY) * 0.3)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.button
      ref={ref}
      className={className}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={{ x, y }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
    >
      {children}
    </motion.button>
  )
}

const PremiumHero = () => {
  const { scrollY } = useScroll()
  const y1 = useTransform(scrollY, [0, 500], [0, 200])
  const y2 = useTransform(scrollY, [0, 500], [0, -150])

  return (
    <section className="relative min-h-[120vh] flex flex-col justify-center overflow-hidden bg-background">
      {/* 3D Background - Fixed position to create depth */}
      <div className="absolute inset-0 z-0">
        <Scene3D />
      </div>

      <div className="container mx-auto px-6 relative z-10 pt-32">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-9">
            <motion.h1 
              className="text-[clamp(4rem,10vw,12rem)] leading-[0.85] font-serif font-medium tracking-tighter mix-blend-difference text-white"
              initial={{ opacity: 0, y: 100 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            >
              STRATEGY <br />
              <span className="italic font-light ml-12 md:ml-24">ELEVATED</span> <br />
              TO ART.
            </motion.h1>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6 mt-12 md:mt-24 items-end">
          <div className="col-span-12 md:col-span-4 md:col-start-9">
            <motion.div
              style={{ y: y2 }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 1 }}
            >
              <p className="text-xl md:text-2xl font-light leading-relaxed text-zinc-300 mb-8 backdrop-blur-sm">
                The operating system for founders who demand precision. Turn chaos into a masterpiece of growth.
              </p>
              
              <div className="flex gap-4">
                 <MagneticButton className="px-8 py-4 bg-white text-black rounded-full text-sm font-bold uppercase tracking-widest hover:bg-accent transition-colors">
                  Start Trial
                </MagneticButton>
                <MagneticButton className="px-8 py-4 border border-white/20 text-white rounded-full text-sm font-bold uppercase tracking-widest backdrop-blur-md hover:bg-white/10 transition-colors">
                  Showreel
                </MagneticButton>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
      
      {/* Scroll Indicator */}
      <motion.div 
        style={{ opacity: useTransform(scrollY, [0, 200], [1, 0]) }}
        className="absolute bottom-12 left-6 right-6 flex justify-between items-end text-xs text-zinc-500 uppercase tracking-widest mix-blend-difference"
      >
        <div>San Francisco / New York</div>
        <div className="h-12 w-[1px] bg-zinc-700 animate-pulse"></div>
        <div>V2.0 Premium Edition</div>
      </motion.div>
    </section>
  )
}

export default PremiumHero

