import React, { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'

/* ═══════════════════════════════════════════════════════════════════════════
   PROBLEM STATEMENT - Reimagined with 2D art and cleaner design
   Shows the pain points founders face with their GTM chaos
   ═══════════════════════════════════════════════════════════════════════════ */

// Nanobana-style 2D icons (single color, zinc)
const ChaosIcon = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="1" strokeDasharray="4 4" />
    <path d="M12 24H36M24 12V36M16 16L32 32M32 16L16 32" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <circle cx="24" cy="24" r="4" fill="currentColor" fillOpacity="0.3" />
  </svg>
)

const BurnIcon = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <path d="M24 6L28 18L40 22L28 26L24 38L20 26L8 22L20 18L24 6Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <circle cx="24" cy="22" r="6" stroke="currentColor" strokeWidth="1" strokeDasharray="2 2" />
    <path d="M24 16V28M18 22H30" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
  </svg>
)

const TimeIcon = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <circle cx="24" cy="24" r="18" stroke="currentColor" strokeWidth="1.5" />
    <circle cx="24" cy="24" r="14" stroke="currentColor" strokeWidth="1" strokeDasharray="4 4" />
    <path d="M24 14V24L32 28" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="24" cy="24" r="2" fill="currentColor" />
  </svg>
)

// Animated counter hook
const useCounter = (end: string, inView: boolean) => {
  const [count, setCount] = React.useState(0)
  const numericEnd = parseInt(end.replace(/[^0-9]/g, '')) || 0

  React.useEffect(() => {
    if (!inView || numericEnd === 0) return

    let start = 0
    const duration = 1500
    const increment = numericEnd / (duration / 16)

    const timer = setInterval(() => {
      start += increment
      if (start >= numericEnd) {
        setCount(numericEnd)
        clearInterval(timer)
      } else {
        setCount(Math.floor(start))
      }
    }, 16)

    return () => clearInterval(timer)
  }, [inView, numericEnd])

  // Handle special formatting
  if (end.includes('%')) return `${count}%`
  if (end.includes('₹')) return `₹${count}L+`
  if (end.includes('+')) return `${count}+`
  return count.toString()
}

// Problem card component with animated counter and hover particles
const ProblemCard = ({ icon: Icon, stat, title, description, delay }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-50px" })
  const [isHovered, setIsHovered] = useState(false)
  const animatedStat = useCounter(stat, inView)

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ delay, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative p-8 bg-zinc-900/40 border border-white/[0.06] rounded-2xl hover:border-zinc-500/20 transition-colors duration-500 overflow-hidden">
        {/* Subtle hover glow */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-zinc-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        {/* Hover particle burst */}
        <AnimatePresence>
          {isHovered && (
            <>
              {[...Array(6)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 rounded-full bg-zinc-400/60"
                  initial={{
                    x: '50%',
                    y: '50%',
                    opacity: 1,
                    scale: 0
                  }}
                  animate={{
                    x: `${50 + (Math.random() - 0.5) * 100}%`,
                    y: `${50 + (Math.random() - 0.5) * 100}%`,
                    opacity: 0,
                    scale: 1.5
                  }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                />
              ))}
            </>
          )}
        </AnimatePresence>

        {/* Icon */}
        <motion.div
          className="relative z-10 w-16 h-16 mb-6 text-zinc-500/70"
          animate={{ scale: isHovered ? 1.1 : 1 }}
          transition={{ duration: 0.3 }}
        >
          <Icon className="w-full h-full" />
        </motion.div>

        {/* Stat - animated counter */}
        <div className="relative z-10 mb-4">
          <span className="text-5xl md:text-6xl font-extralight text-white tracking-tight">
            {animatedStat}
          </span>
        </div>

        {/* Title */}
        <h3 className="relative z-10 text-xl font-medium text-white mb-3">{title}</h3>

        {/* Description */}
        <p className="relative z-10 text-white/40 leading-relaxed">{description}</p>
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
      icon: ChaosIcon,
      stat: "73%",
      title: "GTM Efforts Fail",
      description: "Scattered campaigns. Unclear strategy. Most go-to-market initiatives never hit their targets."
    },
    {
      icon: TimeIcon,
      stat: "6+",
      title: "Months Wasted",
      description: "Average time founders spend pivoting strategies before finding what actually works."
    },
    {
      icon: BurnIcon,
      stat: "₹50L+",
      title: "Burned on Guesswork",
      description: "Average marketing spend wasted on channels and campaigns that never convert."
    }
  ]

  return (
    <section ref={sectionRef} className="relative bg-[#050505] py-32 md:py-40 overflow-hidden">
      {/* Background art */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-zinc-500/10 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-zinc-500/10 to-transparent" />

        {/* 2D geometric art - Nanobana style */}
        <svg className="absolute inset-0 w-full h-full opacity-10" preserveAspectRatio="xMidYMid slice">
          <defs>
            <pattern id="chaos-grid" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
              <circle cx="50" cy="50" r="1" fill="#F59E0B" />
              <path d="M0 50H100M50 0V100" stroke="#F59E0B" strokeWidth="0.3" strokeDasharray="4 8" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#chaos-grid)" />

          {/* Scattered elements */}
          <circle cx="15%" cy="30%" r="60" stroke="#F59E0B" strokeWidth="0.5" fill="none" />
          <circle cx="85%" cy="70%" r="80" stroke="#F59E0B" strokeWidth="0.5" fill="none" strokeDasharray="4 4" />
          <path d="M10% 80% L30% 60% L50% 85% L70% 55% L90% 75%" stroke="#F59E0B" strokeWidth="0.5" fill="none" />
        </svg>

        {/* Subtle radial gradient */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-zinc-500/5 to-transparent blur-3xl" />
      </div>

      <div className="max-w-6xl mx-auto px-6 md:px-12 relative z-10">
        {/* Header */}
        <div className="text-center mb-20">
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="inline-flex items-center gap-3 mb-8"
          >
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-zinc-500/50" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-zinc-400/60 font-medium">
              The Problem
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-zinc-500/50" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight"
          >
            Your GTM is{' '}
            <span className="text-white/40">chaos</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="mt-6 text-lg md:text-xl text-white/35 max-w-2xl mx-auto"
          >
            Scattered campaigns. Disconnected metrics. No clear strategy. You're flying blind.
          </motion.p>
        </div>

        {/* Problem cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {problems.map((problem, index) => (
            <ProblemCard
              key={index}
              {...problem}
              delay={0.3 + index * 0.1}
            />
          ))}
        </div>

        {/* Transition element */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="mt-20 text-center"
        >
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            className="inline-flex flex-col items-center gap-3"
          >
            <span className="text-[11px] uppercase tracking-[0.3em] text-zinc-400/50 font-medium">
              There's a better way
            </span>
            <div className="w-px h-8 bg-gradient-to-b from-zinc-500/40 to-transparent" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

export default ProblemStatement

