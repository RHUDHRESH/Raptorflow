import React, { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { TrendingDown, Clock, DollarSign, ArrowDown } from 'lucide-react'

// Premium problem stat card
const ProblemCard = ({ icon: Icon, stat, label, description, delay, accent }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-50px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ delay, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className="group relative"
    >
      <div className={`
        relative p-8 bg-zinc-900/50 border border-white/[0.06] rounded-2xl
        hover:border-white/[0.12] transition-all duration-500
        hover:shadow-[0_20px_60px_-15px_rgba(0,0,0,0.5)]
      `}>
        {/* Subtle top accent line */}
        <div className={`absolute top-0 left-8 right-8 h-px bg-gradient-to-r from-transparent via-${accent}-500/30 to-transparent`} />

        {/* Icon */}
        <div className={`w-12 h-12 rounded-xl bg-${accent}-500/10 border border-${accent}-500/20 flex items-center justify-center mb-6`}>
          <Icon className={`w-5 h-5 text-${accent}-400`} />
        </div>

        {/* Stat */}
        <div className="mb-4">
          <span className={`text-5xl font-extralight text-${accent}-100 tracking-tight`}>
            {stat}
          </span>
        </div>

        {/* Label */}
        <h3 className="text-lg font-medium text-white mb-3">{label}</h3>

        {/* Description */}
        <p className="text-sm text-white/40 leading-relaxed">{description}</p>
      </div>
    </motion.div>
  )
}

// Main ProblemStatement component - Premium redesign
const ProblemStatement = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  const problems = [
    {
      icon: TrendingDown,
      stat: "73%",
      label: "of GTM Efforts Fail",
      description: "Most go-to-market initiatives never achieve their targets due to scattered execution and unclear strategy.",
      accent: "red"
    },
    {
      icon: Clock,
      stat: "6+",
      label: "Months Wasted",
      description: "Average time founders spend pivoting strategies before finding what actually works for their market.",
      accent: "amber"
    },
    {
      icon: DollarSign,
      stat: "₹50L+",
      label: "Burned on Guesswork",
      description: "Average marketing spend wasted on channels and campaigns that don't convert.",
      accent: "orange"
    }
  ]

  const painPoints = [
    "Running campaigns without a clear ICP",
    "No idea which channels actually convert",
    "Metrics everywhere, insights nowhere",
    "Strategy docs gathering dust",
    "Team executing without alignment",
    "Burning budget on experiments that never learn"
  ]

  return (
    <section
      ref={sectionRef}
      className="relative py-32 md:py-40 bg-[#0a0a0a] overflow-hidden"
    >
      {/* Subtle background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-red-500/10 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

        {/* Subtle gradient */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-red-950/20 to-transparent blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
        {/* Section header */}
        <div className="text-center mb-20 md:mb-24">
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-3 mb-8"
          >
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-red-500/50" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-red-400/70 font-medium">
              The Problem
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-red-500/50" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight mb-8"
          >
            Your GTM is{' '}
            <span className="text-red-400/90">chaos</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-lg md:text-xl text-white/40 max-w-2xl mx-auto leading-relaxed"
          >
            Scattered campaigns. Disconnected metrics. No clear strategy.
            <span className="text-white/50"> You're flying blind and burning cash.</span>
          </motion.p>
        </div>

        {/* Problem cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 mb-24">
          {problems.map((problem, index) => (
            <ProblemCard
              key={index}
              {...problem}
              delay={0.3 + index * 0.1}
            />
          ))}
        </div>

        {/* Sound familiar section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.7, duration: 0.6 }}
          className="text-center"
        >
          <p className="text-[11px] text-white/25 uppercase tracking-[0.3em] mb-10">
            Sound familiar?
          </p>

          <div className="flex flex-wrap justify-center gap-3 max-w-4xl mx-auto">
            {painPoints.map((pain, index) => (
              <motion.span
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={inView ? { opacity: 1, scale: 1 } : {}}
                transition={{ delay: 0.8 + index * 0.05, duration: 0.4 }}
                className="px-5 py-2.5 bg-white/[0.03] border border-white/[0.06] rounded-full text-sm text-white/40 hover:text-white/60 hover:border-white/10 transition-all duration-300 cursor-default"
              >
                {pain}
              </motion.span>
            ))}
          </div>
        </motion.div>

        {/* Transition arrow */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="mt-24 text-center"
        >
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className="inline-flex flex-col items-center gap-4"
          >
            <span className="text-[11px] uppercase tracking-[0.3em] text-amber-400/60 font-medium">
              There's a better way
            </span>
            <ArrowDown className="w-4 h-4 text-amber-400/40" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

export default ProblemStatement
