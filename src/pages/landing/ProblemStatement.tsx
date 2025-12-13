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
      <div className="relative p-8 bg-card border border-border/50">
        <div className="absolute top-0 left-8 right-8 h-px bg-border/80" />

        <div className="w-12 h-12 border border-border/50 flex items-center justify-center mb-6">
          <Icon className="w-5 h-5 text-primary" />
        </div>

        <div className="mb-4">
          <span className="text-5xl font-extralight text-foreground tracking-tight">
            {stat}
          </span>
        </div>

        <h3 className="text-lg font-medium text-foreground mb-3">{label}</h3>

        <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
      </div>
    </motion.div>
  )
}

// Main ProblemStatement component - Premium redesign
const ProblemStatement = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  const process = [
    {
      icon: TrendingDown,
      stat: "73%",
      label: "of GTM Efforts Fail",
      description: "Most go-to-market initiatives never achieve their targets due to scattered execution and unclear strategy.",
    },
  ]

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
    <section ref={sectionRef} className="bg-background relative overflow-hidden py-24">
      <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] via-transparent to-white/[0.03]" />

      <div className="max-w-6xl mx-auto px-6">
        {/* Intro */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="max-w-3xl mb-12"
        >
          <p className="text-caption text-muted-foreground mb-4">The Problem</p>
          <h2 className="text-display text-4xl md:text-5xl text-foreground mb-4">Your GTM is chaos</h2>
          <p className="text-muted-foreground text-lg leading-relaxed">
            Scattered campaigns. Disconnected metrics. No clear strategy. You're flying blind and burning cash.
          </p>
        </motion.div>

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
