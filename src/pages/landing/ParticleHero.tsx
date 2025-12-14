import React, { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useScroll, useTransform } from 'framer-motion'
import { ArrowRight } from 'lucide-react'

/* ═══════════════════════════════════════════════════════════════════════════
   PARTICLE HERO - HIGH FASHION EDITORIAL DESIGN
   Landing hero with minimal, sophisticated aesthetic
   ═══════════════════════════════════════════════════════════════════════════ */

const ParticleHero = () => {
  const navigate = useNavigate()
  const containerRef = useRef(null)

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const y = useTransform(scrollYProgress, [0, 0.5], [0, 80])

  return (
    <section
      ref={containerRef}
      className="relative min-h-screen flex flex-col items-center justify-center bg-background px-6"
    >
      {/* Content */}
      <motion.div
        style={{ opacity, y }}
        className="relative z-10 flex flex-col items-center justify-center text-center max-w-5xl"
      >
        {/* Eyebrow */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="text-caption text-muted-foreground mb-8"
        >
          AI-Powered Marketing OS
        </motion.p>

        {/* Main headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="text-display text-5xl sm:text-6xl md:text-7xl lg:text-8xl text-foreground leading-[0.95] mb-4"
        >
          Stop guessing.
        </motion.h1>
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="text-display text-5xl sm:text-6xl md:text-7xl lg:text-8xl leading-[0.95]"
        >
          <span className="italic text-primary">Start commanding.</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="mt-8 text-lg md:text-xl text-muted-foreground max-w-2xl leading-relaxed"
        >
          RaptorFlow transforms your GTM chaos into a precision execution machine.
          <span className="text-foreground"> Clear strategy. Controlled execution. Measurable results.</span>
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="mt-12 flex flex-col sm:flex-row items-center gap-4"
        >
          <button
            onClick={() => navigate('/start')}
            className="group flex items-center gap-2 px-8 py-4 bg-foreground hover:bg-primary text-background text-caption transition-all"
          >
            Start Your Spike
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>

          <button
            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
            className="px-8 py-4 text-muted-foreground hover:text-foreground text-caption transition-colors"
          >
            See How It Works
          </button>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1, duration: 0.8 }}
          className="mt-20 flex items-center gap-12 md:gap-16"
        >
          {[
            { value: '30', label: 'Days to clarity' },
            { value: '6', label: 'Core protocols' },
            { value: '500+', label: 'Founders served' }
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <div className="text-4xl md:text-5xl font-extralight text-foreground tracking-tight">{stat.value}</div>
              <div className="text-caption text-muted-foreground mt-2">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-12 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        >
          <div className="w-px h-12 bg-gradient-to-b from-border to-transparent" />
        </motion.div>
      </motion.div>
    </section>
  )
}

export default ParticleHero
