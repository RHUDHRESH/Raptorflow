import React, { useRef, useState } from 'react'
import { motion, useInView, AnimatePresence, useMotionValue, useSpring, useTransform } from 'framer-motion'

/* ═══════════════════════════════════════════════════════════════════════════
   FEATURE SHOWCASE - Simplified with 2D Nanobana icons (no gyroscope)
   Clean grid layout showing the 6 pillars
   ═══════════════════════════════════════════════════════════════════════════ */

// Nanobana-style 2D icons (single zinc color)
const NanoTarget = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <circle cx="24" cy="24" r="18" stroke="currentColor" strokeWidth="1" />
    <circle cx="24" cy="24" r="12" stroke="currentColor" strokeWidth="1.5" />
    <circle cx="24" cy="24" r="6" stroke="currentColor" strokeWidth="1" strokeDasharray="4 2" />
    <circle cx="24" cy="24" r="2" fill="currentColor" />
    <path d="M24 4V10M24 38V44M4 24H10M38 24H44" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
  </svg>
)

const NanoShield = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <path d="M24 4L6 12V24C6 34 14 42 24 44C34 42 42 34 42 24V12L24 4Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M24 12V28L16 22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="24" cy="28" r="3" fill="currentColor" fillOpacity="0.3" />
  </svg>
)

const NanoZap = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <path d="M26 4L8 26H22L20 44L40 20H26L26 4Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M18 26H30" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
  </svg>
)

const NanoLayers = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <path d="M4 32L24 42L44 32" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M4 24L24 34L44 24" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M24 6L4 16L24 26L44 16L24 6Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <circle cx="24" cy="16" r="3" fill="currentColor" fillOpacity="0.3" />
  </svg>
)

const NanoSparkles = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <path d="M24 4L28 18L42 24L28 30L24 44L20 30L6 24L20 18L24 4Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <circle cx="24" cy="24" r="4" fill="currentColor" fillOpacity="0.3" />
    <path d="M24 20V28M20 24H28" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
  </svg>
)

const NanoChart = ({ className = '' }) => (
  <svg viewBox="0 0 48 48" fill="none" className={className}>
    <rect x="6" y="28" width="8" height="14" rx="1" stroke="currentColor" strokeWidth="1.5" />
    <rect x="18" y="18" width="8" height="24" rx="1" stroke="currentColor" strokeWidth="1.5" />
    <rect x="30" y="8" width="8" height="34" rx="1" stroke="currentColor" strokeWidth="1.5" />
    <path d="M6 44H42" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
    <circle cx="22" cy="8" r="2" fill="currentColor" />
  </svg>
)

// Feature card component with 3D tilt and glow effects
const FeatureCard = ({ feature, index }) => {
  const cardRef = useRef<HTMLDivElement>(null)
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-50px" })
  const [isExpanded, setIsExpanded] = useState(false)

  // 3D Tilt motion values
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  // Spring for smooth movement
  const springConfig = { stiffness: 300, damping: 30 }
  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [8, -8]), springConfig)
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-8, 8]), springConfig)

  // Glare position
  const glareX = useSpring(useTransform(x, [-0.5, 0.5], [0, 100]), springConfig)
  const glareY = useSpring(useTransform(y, [-0.5, 0.5], [0, 100]), springConfig)

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    x.set((e.clientX - centerX) / rect.width)
    y.set((e.clientY - centerY) / rect.height)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  // Icon animation variants
  const getIconAnimation = () => {
    const animations = {
      'NanoTarget': { scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] },
      'NanoShield': { y: [0, -3, 0], scale: [1, 1.05, 1] },
      'NanoZap': { x: [0, 2, -2, 0], opacity: [1, 0.8, 1] },
      'NanoLayers': { rotateX: [0, 10, 0] },
      'NanoSparkles': { scale: [1, 1.15, 1], rotate: [0, 180, 360] },
      'NanoChart': { y: [0, -2, 0, -2, 0] }
    }
    return animations[feature.icon.name] || { scale: [1, 1.1, 1] }
  }

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ delay: index * 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="group relative"
      style={{ perspective: 1000 }}
    >
      <motion.div
        ref={cardRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{
          rotateX,
          rotateY,
          transformStyle: 'preserve-3d'
        }}
        className="relative p-8 rounded-2xl border transition-all duration-300 h-full overflow-hidden"
        whileHover={{ scale: 1.02 }}
      >
        {/* Background with MP072 colors */}
        <div
          className="absolute inset-0 rounded-2xl"
          style={{ background: 'linear-gradient(135deg, rgba(238,233,223,0.9) 0%, rgba(229,223,211,0.8) 100%)', border: '1px solid rgba(201,193,177,0.5)' }}
        />

        {/* 3D Glare effect */}
        <motion.div
          className="absolute inset-0 rounded-2xl pointer-events-none"
          style={{
            background: `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(255,177,98,0.15) 0%, transparent 50%)`,
            zIndex: 1
          }}
        />

        {/* Hover glow */}
        <motion.div
          className="absolute -inset-1 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
          style={{ background: 'linear-gradient(135deg, rgba(255,177,98,0.2) 0%, transparent 50%)', filter: 'blur(20px)' }}
        />

        {/* Icon with animation */}
        <motion.div
          className="relative z-10 w-14 h-14 mb-6"
          style={{ color: '#FFB162', transform: 'translateZ(20px)' }}
          whileHover={getIconAnimation()}
          transition={{ duration: 0.8 }}
        >
          <feature.icon className="w-full h-full" />
        </motion.div>

        {/* Content */}
        <h3
          className="relative z-10 text-xl font-medium mb-3"
          style={{ color: '#2C3B4D', transform: 'translateZ(15px)' }}
        >
          {feature.title}
        </h3>
        <p
          className="relative z-10 leading-relaxed text-sm mb-6"
          style={{ color: '#6B7A8C', transform: 'translateZ(10px)' }}
        >
          {feature.description}
        </p>

        {/* Highlights */}
        <ul className="relative z-10 space-y-2" style={{ transform: 'translateZ(5px)' }}>
          {feature.highlights.map((highlight, i) => (
            <li key={i} className="flex items-center gap-2 text-xs" style={{ color: '#6B7A8C' }}>
              <div className="w-1.5 h-1.5 rounded-full" style={{ background: '#FFB162' }} />
              {highlight}
            </li>
          ))}
        </ul>

        {/* Expandable details */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
              style={{ transform: 'translateZ(5px)' }}
            >
              <div className="pt-6 mt-6" style={{ borderTop: '1px solid rgba(201,193,177,0.3)' }}>
                <p className="text-sm leading-relaxed" style={{ color: '#6B7A8C' }}>
                  {feature.expandedDetails || `${feature.title} is a core component of the RaptorFlow system, designed to bring clarity and precision to your GTM strategy.`}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Learn more button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="relative z-10 mt-6 flex items-center gap-2 text-xs transition-colors"
          style={{ color: '#FFB162' }}
        >
          <span>{isExpanded ? 'Show less' : 'Learn more'}</span>
          <motion.svg
            viewBox="0 0 12 12"
            className="w-3 h-3"
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          </motion.svg>
        </button>
      </motion.div>
    </motion.div>
  )
}

const FeatureShowcase = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  const features = [
    {
      icon: NanoTarget,
      title: "6D ICP Engine",
      description: "Build laser-focused customer profiles with firmographics, technographics, psychographics, and behavior patterns.",
      highlights: ["AI-generated ICP profiles", "Fit scoring algorithm", "Messaging angle extraction"]
    },
    {
      icon: NanoShield,
      title: "Barrier Engine",
      description: "Classify exactly where prospects get stuck: Obscurity, Risk, Inertia, Friction, Capacity, or Atrophy.",
      highlights: ["6-stage barrier taxonomy", "Auto protocol matching", "Confidence scoring"]
    },
    {
      icon: NanoZap,
      title: "Protocol System",
      description: "Six battle-tested GTM protocols that map directly to barriers.",
      highlights: ["Pre-built move templates", "Channel recommendations", "Success metrics defined"]
    },
    {
      icon: NanoLayers,
      title: "Campaign Command",
      description: "Strategic containers that bind goals, ICPs, barriers, and protocols into unified execution.",
      highlights: ["Goal-based architecture", "Protocol binding", "Budget allocation"]
    },
    {
      icon: NanoSparkles,
      title: "Muse AI Factory",
      description: "Generate battle-ready assets: webinar scripts, email sequences, battlecards.",
      highlights: ["10+ asset types", "ICP-personalized copy", "One-click generation"]
    },
    {
      icon: NanoChart,
      title: "RAG Matrix",
      description: "Real-time health dashboard. Red/zinc/Green status for every metric you track.",
      highlights: ["Automated RAG calculation", "Trend analysis", "Kill switch integration"]
    }
  ]

  return (
    <section id="features" ref={sectionRef} className="relative py-32 md:py-40 bg-[#050505] overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-zinc-500/10 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-zinc-500/10 to-transparent" />

        {/* Geometric grid */}
        <svg className="absolute inset-0 w-full h-full opacity-[0.04]" preserveAspectRatio="xMidYMid slice">
          <defs>
            <pattern id="feature-grid" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse">
              <circle cx="30" cy="30" r="0.5" fill="#F59E0B" />
              <path d="M30 0V60M0 30H60" stroke="#F59E0B" strokeWidth="0.2" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#feature-grid)" />
        </svg>

        {/* Radial glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-gradient-radial from-zinc-500/5 to-transparent blur-3xl" />
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
              The System
            </span>
            <span className="w-12 h-px bg-gradient-to-l from-transparent to-zinc-500/50" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight"
          >
            Six pillars of{' '}
            <span className="bg-gradient-to-r from-zinc-200 via-zinc-100 to-zinc-200 bg-clip-text text-transparent">
              GTM control
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="mt-6 text-lg md:text-xl text-white/35 max-w-2xl mx-auto"
          >
            A complete system for understanding your market and executing with precision.
          </motion.p>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}

export default FeatureShowcase

