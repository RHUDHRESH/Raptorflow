import React, { useRef, useState, useEffect } from 'react'
import { motion, useInView } from 'framer-motion'

/* ═══════════════════════════════════════════════════════════════════════════
   INTERACTIVE FLOW - Simplified 4-step process with cleaner cards
   ═══════════════════════════════════════════════════════════════════════════ */

// Nanobana-style step icons
const IntakeIcon = ({ className = '' }) => (
  <svg viewBox="0 0 32 32" fill="none" className={className}>
    <circle cx="16" cy="16" r="12" stroke="currentColor" strokeWidth="1.5" />
    <path d="M16 10V22M10 16H22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

const BrainIcon = ({ className = '' }) => (
  <svg viewBox="0 0 32 32" fill="none" className={className}>
    <circle cx="16" cy="16" r="10" stroke="currentColor" strokeWidth="1.5" />
    <path d="M12 12C14 10 18 10 20 12M12 20C14 22 18 22 20 20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    <circle cx="12" cy="16" r="2" fill="currentColor" fillOpacity="0.5" />
    <circle cx="20" cy="16" r="2" fill="currentColor" fillOpacity="0.5" />
  </svg>
)

const RocketIcon = ({ className = '' }) => (
  <svg viewBox="0 0 32 32" fill="none" className={className}>
    <path d="M16 4L22 16L16 28L10 16L16 4Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <circle cx="16" cy="14" r="3" fill="currentColor" fillOpacity="0.3" />
    <path d="M6 22L10 18M26 22L22 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

const ChartIcon = ({ className = '' }) => (
  <svg viewBox="0 0 32 32" fill="none" className={className}>
    <rect x="4" y="18" width="6" height="10" rx="1" stroke="currentColor" strokeWidth="1.5" />
    <rect x="12" y="12" width="6" height="16" rx="1" stroke="currentColor" strokeWidth="1.5" />
    <rect x="20" y="6" width="6" height="22" rx="1" stroke="currentColor" strokeWidth="1.5" />
  </svg>
)

// Animated checkmark icon with slow tick effect
const AnimatedCheckmark = () => (
  <motion.svg
    viewBox="0 0 16 16"
    className="w-4 h-4"
    fill="none"
  >
    <motion.path
      d="M3 8L7 12L13 4"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
    />
  </motion.svg>
)

// Sparkle particle for clarity effect
const SparkleParticle = ({ delay = 0 }) => (
  <motion.div
    className="absolute w-1 h-1 bg-zinc-300 rounded-full"
    style={{
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
    }}
    initial={{ opacity: 0, scale: 0 }}
    animate={{
      opacity: [0, 1, 0],
      scale: [0, 1.5, 0],
    }}
    transition={{
      duration: 1.5,
      repeat: Infinity,
      delay: delay,
      repeatDelay: Math.random() * 2,
    }}
  />
)

// Step card component with animated checkmarks
const StepCard = ({ step, index, isActive, isCompleted, onClick }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-50px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      onClick={onClick}
      className="cursor-pointer group"
    >
      <div className={`
        relative p-6 rounded-xl border transition-all duration-300
        ${isActive
          ? 'bg-zinc-900/60 border-zinc-500/25 shadow-lg shadow-zinc-500/10'
          : 'bg-zinc-900/40 border-white/[0.06] hover:border-white/[0.12]'
        }
      `}>
        {/* Step number or animated checkmark */}
        <motion.div
          className={`
            absolute -top-3 -left-3 w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium
            ${isCompleted
              ? 'bg-emerald-500 text-white'
              : isActive
                ? 'bg-zinc-500 text-black'
                : 'bg-zinc-800 text-white/50 border border-white/[0.1]'
            }
          `}
          animate={{
            scale: isCompleted ? [1, 1.2, 1] : 1,
            boxShadow: isCompleted ? ['0 0 0 rgba(52,211,153,0)', '0 0 12px rgba(52,211,153,0.5)', '0 0 0 rgba(52,211,153,0)'] : 'none'
          }}
          transition={{ duration: 0.5 }}
        >
          {isCompleted ? <AnimatedCheckmark /> : index + 1}
        </motion.div>

        {/* Icon */}
        <motion.div
          className={`w-10 h-10 mb-4 ${isActive ? 'text-zinc-400' : isCompleted ? 'text-emerald-400/60' : 'text-white/30'}`}
          animate={{
            scale: isActive ? [1, 1.08, 1] : 1,
            rotate: isActive && index === 1 ? [0, 5, -5, 0] : 0, // Brain icon subtle wobble
          }}
          transition={{ duration: 1.5, repeat: isActive ? Infinity : 0 }}
        >
          <step.icon className="w-full h-full" />
        </motion.div>

        {/* Content */}
        <h3 className={`text-lg font-medium mb-2 ${isActive ? 'text-white' : isCompleted ? 'text-white/60' : 'text-white/70'}`}>
          {step.title}
        </h3>
        <p className={`text-sm leading-relaxed ${isActive ? 'text-white/50' : 'text-white/30'}`}>
          {step.description}
        </p>

        {/* Duration */}
        <div className={`
          mt-4 inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs
          ${isActive ? 'bg-zinc-500/15 text-zinc-300' : isCompleted ? 'bg-emerald-500/10 text-emerald-300' : 'bg-white/5 text-white/30'}
        `}>
          {step.duration}
        </div>
      </div>
    </motion.div>
  )
}

const InteractiveFlow = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })
  const [activeStep, setActiveStep] = useState(0)
  const [isPaused, setIsPaused] = useState(false)

  // Auto-advance timer
  useEffect(() => {
    if (!inView || isPaused) return

    const timer = setInterval(() => {
      setActiveStep(prev => (prev + 1) % 4)
    }, 4000)

    return () => clearInterval(timer)
  }, [inView, isPaused])

  const steps = [
    {
      icon: IntakeIcon,
      title: "Strategic Intake",
      description: "Answer strategic questions. We extract your positioning, ICPs, and market context.",
      duration: "15 minutes"
    },
    {
      icon: BrainIcon,
      title: "AI Strategy Build",
      description: "Our agents analyze, score, and generate your complete GTM battle plan.",
      duration: "Instant"
    },
    {
      icon: RocketIcon,
      title: "Launch Your Spike",
      description: "Activate your 30-day GTM sprint with guardrails and kill switches in place.",
      duration: "30 days"
    },
    {
      icon: ChartIcon,
      title: "Measure & Iterate",
      description: "Track RAG metrics. Review performance. Learn and improve continuously.",
      duration: "Ongoing"
    }
  ]

  return (
    <section ref={sectionRef} className="relative py-32 md:py-40 bg-[#050505] overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/5 to-transparent" />

        {/* Subtle flow lines */}
        <svg className="absolute inset-0 w-full h-full opacity-[0.05]">
          <defs>
            <pattern id="flow-dots" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
              <circle cx="20" cy="20" r="0.5" fill="#F59E0B" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#flow-dots)" />
        </svg>
      </div>

      <div className="max-w-6xl mx-auto px-6 md:px-12 relative z-10">
        {/* Header */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="inline-flex items-center gap-3 mb-8"
          >
            <span className="w-12 h-px bg-gradient-to-r from-transparent to-zinc-500/50" />
            <span className="text-[11px] uppercase tracking-[0.4em] text-zinc-400/60 font-medium">
              The Process
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-zinc-500/50" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight"
          >
            From{' '}
            <motion.span
              className="relative inline-block text-red-400/80"
              whileHover={{ scale: 1.05, rotate: [-1, 1, -1, 0] }}
              transition={{ duration: 0.3 }}
            >
              chaos
            </motion.span>
            {' '}to{' '}
            <span className="relative inline-block">
              <span className="bg-gradient-to-r from-zinc-200 via-zinc-100 to-zinc-200 bg-clip-text text-transparent">
                clarity
              </span>
              {/* Sparkle particles */}
              {[...Array(6)].map((_, i) => (
                <SparkleParticle key={i} delay={i * 0.3} />
              ))}
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="mt-6 text-lg md:text-xl text-white/35 max-w-2xl mx-auto"
          >
            Four phases. One outcome: GTM clarity you can actually execute.
          </motion.p>
        </div>

        {/* Steps grid with connecting lines */}
        <div
          className="relative"
          onMouseEnter={() => setIsPaused(true)}
          onMouseLeave={() => setIsPaused(false)}
        >
          {/* Connecting lines (desktop only) */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 -translate-y-1/2">
            <div className="h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            {/* Animated pulse */}
            <motion.div
              className="absolute top-0 h-1 w-16 bg-gradient-to-r from-zinc-500/0 via-zinc-500/60 to-zinc-500/0 rounded-full -translate-y-1/2"
              animate={{
                left: [`${activeStep * 25}%`, `${((activeStep + 1) % 4) * 25}%`]
              }}
              transition={{ duration: 4, ease: "linear" }}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((step, index) => (
              <StepCard
                key={step.title}
                step={step}
                index={index}
                isActive={activeStep === index}
                isCompleted={index < activeStep}
                onClick={() => setActiveStep(index)}
              />
            ))}
          </div>
        </div>

        {/* Progress dots with auto-play indicator */}
        <div className="flex items-center justify-center gap-4 mt-12">
          <div className="flex gap-2">
            {steps.map((_, index) => (
              <button
                key={index}
                onClick={() => setActiveStep(index)}
                className={`
                  h-2 rounded-full transition-all duration-300
                  ${activeStep === index ? 'w-6 bg-zinc-400' : index < activeStep ? 'w-2 bg-emerald-400/60' : 'w-2 bg-white/20 hover:bg-white/40'}
                `}
              />
            ))}
          </div>
          <button
            onClick={() => setIsPaused(!isPaused)}
            className="text-white/30 hover:text-white/60 transition-colors"
            title={isPaused ? "Resume auto-play" : "Pause auto-play"}
          >
            {isPaused ? (
              <svg viewBox="0 0 16 16" className="w-4 h-4" fill="currentColor">
                <path d="M4 3L12 8L4 13V3Z" />
              </svg>
            ) : (
              <svg viewBox="0 0 16 16" className="w-4 h-4" fill="currentColor">
                <rect x="3" y="3" width="4" height="10" rx="1" />
                <rect x="9" y="3" width="4" height="10" rx="1" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </section>
  )
}

export default InteractiveFlow

