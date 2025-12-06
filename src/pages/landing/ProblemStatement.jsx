import React, { useRef, useEffect, useState } from 'react'
import { motion, useInView, useAnimation } from 'framer-motion'
import { AlertTriangle, TrendingDown, Clock, DollarSign, Target, Zap } from 'lucide-react'

// Animated counter hook
const useCounter = (end, duration = 2000, startOnView = true) => {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-100px" })
  const started = useRef(false)

  useEffect(() => {
    if (startOnView && !inView) return
    if (started.current) return
    started.current = true

    let startTime = null
    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      setCount(Math.floor(progress * end))
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [end, duration, inView, startOnView])

  return { count, ref }
}

// Glitch text effect
const GlitchText = ({ children, className = "" }) => {
  const [glitch, setGlitch] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      setGlitch(true)
      setTimeout(() => setGlitch(false), 150)
    }, 3000 + Math.random() * 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <span className={`relative inline-block ${className}`}>
      <span className={glitch ? 'opacity-0' : ''}>{children}</span>
      {glitch && (
        <>
          <span className="absolute inset-0 text-red-500/80 translate-x-[2px]">{children}</span>
          <span className="absolute inset-0 text-cyan-500/80 -translate-x-[2px]">{children}</span>
        </>
      )}
    </span>
  )
}

// Problem stat card with animation
const ProblemCard = ({ icon: Icon, stat, label, description, delay, color = "red" }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-50px" })
  const controls = useAnimation()

  useEffect(() => {
    if (inView) {
      controls.start({ opacity: 1, y: 0, transition: { delay, duration: 0.6 } })
    }
  }, [inView, controls, delay])

  const colorClasses = {
    red: "from-red-500/20 to-red-900/20 border-red-500/20 text-red-400",
    amber: "from-amber-500/20 to-amber-900/20 border-amber-500/20 text-amber-400",
    orange: "from-orange-500/20 to-orange-900/20 border-orange-500/20 text-orange-400"
  }

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={controls}
      className={`relative group p-6 bg-gradient-to-br ${colorClasses[color]} border rounded-xl backdrop-blur-sm`}
    >
      {/* Hover glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-xl" />

      <div className="relative z-10">
        <Icon className="w-8 h-8 mb-4 opacity-60" />
        <div className="text-4xl font-light text-white mb-2">
          <GlitchText>{stat}</GlitchText>
        </div>
        <div className="text-sm font-medium text-white/80 mb-2">{label}</div>
        <p className="text-sm text-white/40 leading-relaxed">{description}</p>
      </div>
    </motion.div>
  )
}

// Main ProblemStatement component
const ProblemStatement = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  const problems = [
    {
      icon: TrendingDown,
      stat: "73%",
      label: "of GTM Efforts Fail",
      description: "Most go-to-market initiatives never achieve their targets due to scattered execution.",
      color: "red"
    },
    {
      icon: Clock,
      stat: "6+",
      label: "Months Wasted",
      description: "Average time founders spend pivoting strategies before finding what works.",
      color: "amber"
    },
    {
      icon: DollarSign,
      stat: "₹50L+",
      label: "Burned on Guesswork",
      description: "Average marketing spend wasted on channels that don't convert.",
      color: "orange"
    }
  ]

  return (
    <section
      ref={sectionRef}
      className="relative py-32 bg-black overflow-hidden"
    >
      {/* Background elements */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-red-500/20 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* Subtle warning pattern */}
        <div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `repeating-linear-gradient(
              -45deg,
              transparent,
              transparent 40px,
              rgba(239, 68, 68, 0.1) 40px,
              rgba(239, 68, 68, 0.1) 80px
            )`
          }}
        />
      </div>

      <div className="max-w-6xl mx-auto px-6 relative z-10">
        {/* Section header */}
        <div className="text-center mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-full mb-6"
          >
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span className="text-xs font-medium tracking-wide text-red-400">The Problem</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-4xl md:text-5xl lg:text-6xl font-light text-white mb-6"
          >
            Your GTM is{' '}
            <span className="text-red-400">
              <GlitchText>chaos</GlitchText>
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed"
          >
            Scattered campaigns. Disconnected metrics. No clear strategy.
            You're flying blind and burning cash.
          </motion.p>
        </div>

        {/* Problem cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
          {problems.map((problem, index) => (
            <ProblemCard
              key={index}
              {...problem}
              delay={0.3 + index * 0.15}
            />
          ))}
        </div>

        {/* The chaos list */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="text-center"
        >
          <p className="text-sm text-white/30 uppercase tracking-[0.2em] mb-8">
            Sound familiar?
          </p>

          <div className="flex flex-wrap justify-center gap-4 max-w-4xl mx-auto">
            {[
              "Running campaigns without a clear ICP",
              "No idea which channels actually convert",
              "Metrics everywhere, insights nowhere",
              "Strategy docs gathering dust",
              "Team executing without alignment",
              "Burning budget on experiments that never learn"
            ].map((pain, index) => (
              <motion.span
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={inView ? { opacity: 1, scale: 1 } : {}}
                transition={{ delay: 1 + index * 0.1, duration: 0.4 }}
                className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white/50 hover:text-white/70 hover:border-white/20 transition-all cursor-default"
              >
                {pain}
              </motion.span>
            ))}
          </div>
        </motion.div>

        {/* Transition to solution */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1.8, duration: 0.6 }}
          className="mt-20 text-center"
        >
          <div className="inline-flex items-center gap-2 text-amber-400">
            <span className="w-8 h-px bg-gradient-to-r from-transparent to-amber-400" />
            <Zap className="w-5 h-5" />
            <span className="text-sm font-medium tracking-wide">There's a better way</span>
            <span className="w-8 h-px bg-gradient-to-l from-transparent to-amber-400" />
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default ProblemStatement

