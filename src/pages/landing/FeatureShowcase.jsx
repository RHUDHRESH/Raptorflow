import React, { useRef, useState, useEffect } from 'react'
import { motion, useInView, useSpring, useTransform, useMotionValue } from 'framer-motion'
import { ChevronLeft, ChevronRight, CheckCircle2 } from 'lucide-react'

// --- PRECIOUS NANOBANA ICONS (Cinematic Gold & Glass) ---

const IconWrapper = ({ children, className }) => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <defs>
      <linearGradient id="gold-grad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor="#FBBF24" />
        <stop offset="50%" stopColor="#D97706" />
        <stop offset="100%" stopColor="#F59E0B" />
      </linearGradient>
      <linearGradient id="glass-grad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor="white" stopOpacity="0.4" />
        <stop offset="100%" stopColor="white" stopOpacity="0.1" />
      </linearGradient>
      <filter id="glow-filter" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="2" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
    </defs>
    {children}
  </svg>
)

const NanoTarget = ({ className }) => (
  <IconWrapper className={className}>
    <circle cx="12" cy="12" r="9" stroke="url(#gold-grad)" strokeWidth="0.5" strokeOpacity="0.4" />
    <path d="M12 21a9 9 0 0 0 0-18 9 9 0 0 0 0 18z" stroke="url(#glass-grad)" strokeWidth="1" strokeDasharray="4 4" />
    <path d="M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z" stroke="url(#gold-grad)" strokeWidth="1.5" />
    <circle cx="12" cy="12" r="2" fill="url(#gold-grad)" filter="url(#glow-filter)" />
    <path d="M12 2v3M12 19v3M2 12h3M19 12h3" stroke="url(#gold-grad)" strokeWidth="1" strokeLinecap="round" />
  </IconWrapper>
)

const NanoShield = ({ className }) => (
  <IconWrapper className={className}>
    <path d="M12 21.5s8-4 8-10V5l-8-3-8 3v6.5c0 6 8 10 8 10z" stroke="url(#gold-grad)" strokeWidth="1.5" strokeLinejoin="round" fill="url(#glass-grad)" />
    <path d="M12 5.5v7l4 2.5" stroke="url(#gold-grad)" strokeWidth="1.5" strokeLinecap="round" />
    <circle cx="12" cy="12.5" r="1.5" fill="white" />
  </IconWrapper>
)

const NanoZap = ({ className }) => (
  <IconWrapper className={className}>
    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="url(#gold-grad)" strokeWidth="1.5" strokeLinejoin="round" fill="url(#glass-grad)" />
    <path d="M10 12h4" stroke="white" strokeWidth="1" strokeLinecap="round" filter="url(#glow-filter)" />
  </IconWrapper>
)

const NanoLayers = ({ className }) => (
  <IconWrapper className={className}>
    <path d="M2 17l10 5 10-5M2 12l10 5 10-5M12 2L2 7l10 5 10-5z" stroke="url(#gold-grad)" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M12 7l5 2.5M7 9.5L12 12" stroke="url(#glass-grad)" strokeWidth="1" />
    <circle cx="12" cy="7" r="1.5" fill="url(#gold-grad)" />
  </IconWrapper>
)

const NanoSparkles = ({ className }) => (
  <IconWrapper className={className}>
    <path d="M12 2l2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5z" stroke="url(#gold-grad)" strokeWidth="1.5" fill="url(#glass-grad)" />
    <rect x="11" y="6" width="2" height="12" fill="white" fillOpacity="0.5" rx="1" transform="rotate(45 12 12)" />
    <rect x="11" y="6" width="2" height="12" fill="white" fillOpacity="0.5" rx="1" transform="rotate(-45 12 12)" />
    <circle cx="12" cy="12" r="1" fill="white" filter="url(#glow-filter)" />
  </IconWrapper>
)

const NanoChart = ({ className }) => (
  <IconWrapper className={className}>
    <rect x="3" y="14" width="4" height="6" rx="1" stroke="url(#gold-grad)" strokeWidth="1.5" />
    <rect x="9" y="8" width="4" height="12" rx="1" stroke="url(#gold-grad)" strokeWidth="1.5" fill="url(#glass-grad)" />
    <rect x="15" y="4" width="4" height="16" rx="1" stroke="url(#gold-grad)" strokeWidth="1.5" />
    <path d="M21 21H3" stroke="white" strokeWidth="1" strokeOpacity="0.3" strokeLinecap="round" />
    <circle cx="11" cy="4" r="1.5" fill="url(#gold-grad)" filter="url(#glow-filter)" />
  </IconWrapper>
)

// --- HYPER-COOL GYROSCOPE HUB ---

const GyroRing = ({ size, duration, delay, rotateX, rotateY, border = "border", opacity = 0.2, reverse = false }) => (
  <motion.div
    className={`absolute rounded-full ${border} border-amber-500/${Math.floor(opacity * 100)} shadow-[0_0_15px_rgba(251,191,36,0.1)]`}
    style={{
      width: size,
      height: size,
      transformStyle: 'preserve-3d',
    }}
    animate={{
      rotateX: rotateX,
      rotateY: rotateY,
      rotateZ: reverse ? [360, 0] : [0, 360]
    }}
    transition={{
      rotateZ: { duration: duration, repeat: Infinity, ease: "linear", delay: delay },
      default: { duration: 20, repeat: Infinity, repeatType: "mirror", ease: "easeInOut" }
    }}
  >
    {/* Decorative Nodes on Ring */}
    <div className="absolute top-0 left-1/2 w-1.5 h-1.5 bg-amber-400 rounded-full -translate-x-1/2 -translate-y-1/2 shadow-glow" />
    <div className="absolute bottom-0 left-1/2 w-1.5 h-1.5 bg-amber-400 rounded-full -translate-x-1/2 translate-y-1/2 shadow-glow" />

    {/* Internal ghost ring for depth */}
    <div className="absolute inset-2 rounded-full border border-white/5" />
  </motion.div>
)

const CoreReactor = ({ activeFeature, features }) => (
  <div className="relative w-full h-full flex items-center justify-center transform-style-3d">
    {/* Dynamic Volumetric Beam */}
    <motion.div
      className="absolute w-[600px] h-32 bg-gradient-to-r from-transparent via-amber-500/10 to-transparent blur-3xl"
      animate={{ rotate: [0, 180, 360], scale: [1, 1.2, 1] }}
      transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
    />

    {/* Core Glow */}
    <div className="absolute w-40 h-40 bg-amber-500/20 rounded-full blur-2xl animate-pulse" />

    {/* Geometric Particle Field (Stars) */}
    {[...Array(8)].map((_, i) => (
      <motion.div
        key={i}
        className="absolute w-1 h-1 bg-amber-300 rounded-full"
        initial={{ opacity: 0, scale: 0 }}
        animate={{
          opacity: [0, 1, 0],
          scale: [0, 1.5, 0],
          x: [0, (Math.random() - 0.5) * 200],
          y: [0, (Math.random() - 0.5) * 200]
        }}
        transition={{
          duration: 2 + Math.random() * 2,
          repeat: Infinity,
          delay: Math.random() * 2
        }}
      />
    ))}

    {/* Center Crystal */}
    <motion.div
      key={activeFeature}
      initial={{ scale: 0.8, opacity: 0, rotateY: 180 }}
      animate={{ scale: 1, opacity: 1, rotateY: 0 }}
      transition={{ duration: 0.6, type: "spring" }}
      className="relative z-20 w-32 h-32 rounded-3xl bg-gradient-to-br from-zinc-800/90 via-zinc-900/90 to-black/90 border border-amber-500/30 flex items-center justify-center backdrop-blur-md shadow-[0_0_50px_rgba(245,158,11,0.2)]"
    >
      <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />

      {/* Internal Jewel Facets */}
      <div className="absolute inset-2 border border-white/5 rounded-2xl" />
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />

      {/* Icon */}
      <motion.div
        animate={{ rotateY: [0, 360] }}
        transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        className="transform-style-3d relative z-10"
      >
        {React.createElement(features[activeFeature].icon, {
          className: "w-14 h-14 text-amber-300 drop-shadow-[0_0_15px_rgba(251,191,36,0.6)]"
        })}
      </motion.div>
    </motion.div>
  </div>
)

const CentralHub = ({ activeFeature, features }) => {
  return (
    <div className="relative w-[600px] h-[600px] flex items-center justify-center perspective-[1000px]">
      {/* Deep Space Background for Hub */}
      <div className="absolute inset-0 bg-gradient-radial from-amber-500/5 to-transparent blur-3xl opacity-50" />

      {/* Gyroscopic Rings - Increased Complexity */}
      <GyroRing size={500} duration={45} delay={0} rotateX={[60, 70, 60]} rotateY={[0, 10, 0]} opacity={0.1} border="border-dashed border-[0.5px]" />
      <GyroRing size={420} duration={35} delay={2} rotateX={[110, 100, 110]} rotateY={[20, -20, 20]} opacity={0.15} border="border-[1px]" reverse />
      <GyroRing size={340} duration={25} delay={5} rotateX={[45, 25, 45]} rotateY={[-10, 10, -10]} opacity={0.25} border="border-[2px]" />
      <GyroRing size={280} duration={15} delay={1} rotateX={[0, 360]} rotateY={[360, 0]} opacity={0.1} border="border-dotted border-[2px]" />

      <CoreReactor activeFeature={activeFeature} features={features} />
    </div>
  )
}

// Feature Detail Card
const FeatureDetail = ({ feature }) => (
  <motion.div
    key={feature.title}
    initial={{ opacity: 0, x: 50, filter: 'blur(10px)' }}
    animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
    exit={{ opacity: 0, x: -50, filter: 'blur(10px)' }}
    transition={{ duration: 0.5, ease: "easeOut" }}
    className="bg-zinc-950/60 border border-white/10 rounded-3xl p-8 backdrop-blur-xl relative overflow-hidden group hover:border-amber-500/30 transition-colors duration-500"
  >
    {/* Ambient light spill */}
    <div className="absolute -top-20 -right-20 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none group-hover:bg-amber-500/20 transition-all duration-700" />

    <div className="relative z-10">
      <div className="flex items-start gap-4 mb-8">
        <div className={`w-16 h-16 rounded-2xl bg-zinc-900/80 border border-white/10 flex items-center justify-center flex-shrink-0 shadow-lg group-hover:shadow-[0_0_20px_rgba(245,158,11,0.2)] transition-all duration-500`}>
          <feature.icon className="w-9 h-9 text-amber-300" />
        </div>
        <div>
          <h3 className="text-3xl lg:text-4xl font-light text-white mb-3 tracking-tight">{feature.title}</h3>
          <p className="text-lg text-white/50 leading-relaxed font-light">{feature.description}</p>
        </div>
      </div>

      <div className="space-y-4 pl-2">
        {feature.highlights.map((highlight, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 + (i * 0.1) }}
            className="flex items-center gap-4 group/item"
          >
            <div className="w-2 h-2 rounded-full bg-amber-500/30 group-hover/item:bg-amber-400 group-hover/item:shadow-glow transition-all duration-300" />
            <span className="text-base text-white/70 tracking-wide font-light">{highlight}</span>
          </motion.div>
        ))}
      </div>
    </div>
  </motion.div>
)

const FeatureOrbit = ({ features, activeFeature, onFeatureChange, mouseX, mouseY }) => {
  const angleStep = 360 / features.length

  return (
    <div className="absolute inset-0 pointer-events-none transform-style-3d">
      {/* Orbital Trail Line */}
      <svg className="absolute inset-0 w-full h-full rotate-90 opacity-20 pointer-events-none">
        <circle cx="50%" cy="50%" r="280" fill="none" stroke="url(#gold-grad)" strokeWidth="1" strokeDasharray="10 20" />
      </svg>

      {features.map((feature, index) => {
        const isActive = index === activeFeature
        const angleDeg = (index * angleStep - 90)
        const angleRad = angleDeg * (Math.PI / 180)
        const radius = 280 // Wider orbit

        // Calculate position
        const x = Math.cos(angleRad) * radius
        const y = Math.sin(angleRad) * radius

        return (
          <motion.button
            key={index}
            className={`absolute pointer-events-auto group z-30 focus:outline-none`}
            style={{
              left: `calc(50% + ${x}px)`,
              top: `calc(50% + ${y}px)`,
            }}
            whileHover={{ scale: 1.2 }}
            onClick={() => onFeatureChange(index)}
          >
            <motion.div
              className={`
                relative w-20 h-20 -ml-10 -mt-10 rounded-full flex items-center justify-center
                transition-all duration-500
                ${isActive
                  ? 'bg-amber-950/80 border-2 border-amber-400 shadow-[0_0_30px_rgba(245,158,11,0.5)]'
                  : 'bg-black/40 border border-white/10 hover:border-amber-500/50 hover:bg-zinc-900/80'
                }
                backdrop-blur-md
              `}
            >
              <feature.icon className={`w-9 h-9 transition-all duration-500 ${isActive ? 'text-amber-300 scale-110' : 'text-white/30 group-hover:text-amber-200/70'}`} />

              {/* Active Connector Beam to Center */}
              {isActive && (
                <motion.div
                  className="absolute top-1/2 left-1/2 h-[2px] origin-left -z-10"
                  style={{
                    width: radius - 60,
                    transform: `rotate(${angleDeg + 180}deg) translateX(0px)`,
                    background: 'linear-gradient(90deg, rgba(245,158,11,0.8) 0%, transparent 100%)',
                    boxShadow: '0 0 10px rgba(245,158,11,0.3)'
                  }}
                  initial={{ scaleX: 0, opacity: 0 }}
                  animate={{ scaleX: 1, opacity: 1 }}
                  transition={{ duration: 0.4 }}
                />
              )}
            </motion.div>

            {/* Label on Hover */}
            <div className={`absolute top-full mt-2 left-1/2 -translate-x-1/2 whitespace-nowrap px-3 py-1 rounded-full bg-black/80 border border-white/10 text-xs text-white/70 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none`}>
              {feature.title}
            </div>
          </motion.button>
        )
      })}
    </div>
  )
}

const FeatureShowcase = () => {
  const sectionRef = useRef(null)
  const containerRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })
  const [activeFeature, setActiveFeature] = useState(0)

  // Mouse Interactive Parallax
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const rotateX = useTransform(y, [-100, 100], [10, -10]) // Inverted for natural feel
  const rotateY = useTransform(x, [-100, 100], [-10, 10])

  const handleMouseMove = (e) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    x.set(e.clientX - centerX)
    y.set(e.clientY - centerY)
  }

  // Auto-rotate features
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveFeature(prev => (prev + 1) % 6)
    }, 5000)
    return () => clearInterval(timer)
  }, [])

  const features = [
    {
      icon: NanoTarget,
      title: "6D ICP Engine",
      description: "Build laser-focused customer profiles with firmographics, technographics, psychographics, behaviors, buying committees, and category context.",
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
      description: "Generate battle-ready assets: webinar scripts, email sequences, battlecards, comparison pages.",
      highlights: ["10+ asset types", "ICP-personalized copy", "One-click generation"]
    },
    {
      icon: NanoChart,
      title: "RAG Matrix",
      description: "Real-time health dashboard. Red/Amber/Green status for every metric you track.",
      highlights: ["Automated RAG calculation", "Trend analysis", "Kill switch integration"]
    }
  ]

  const nextFeature = () => setActiveFeature(prev => (prev + 1) % features.length)
  const prevFeature = () => setActiveFeature(prev => (prev - 1 + features.length) % features.length)

  return (
    <section
      id="features"
      ref={sectionRef}
      onMouseMove={handleMouseMove}
      className="relative py-32 md:py-40 bg-[#050505] overflow-hidden min-h-screen flex flex-col justify-center perspective-[2000px]"
    >
      {/* Cinematic Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-amber-500/20 to-transparent" />
        <div className="absolute top-[20%] left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/5 to-transparent" />
        <div className="absolute top-[80%] left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/5 to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1400px] h-[1400px] bg-gradient-radial from-amber-900/10 via-transparent to-transparent blur-3xl opacity-60" />
      </div>

      <div className="max-w-[1400px] mx-auto px-6 md:px-12 relative z-10 w-full">
        {/* Minimal Header */}
        <div className="text-center mb-16 lg:mb-24">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            className="inline-flex items-center gap-3 mb-6"
          >
            <span className="w-12 h-[1px] bg-amber-500/40" />
            <span className="text-sm uppercase tracking-[0.4em] text-amber-500 font-medium">The System</span>
            <span className="w-12 h-[1px] bg-amber-500/40" />
          </motion.div>
          <motion.h2
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="text-5xl md:text-6xl lg:text-7xl font-light text-white tracking-tight"
          >
            Six pillars of <span className="text-amber-200 font-normal drop-shadow-[0_0_15px_rgba(251,191,36,0.2)]">GTM control</span>
          </motion.h2>
        </div>

        {/* Main Interactive Stage */}
        <div className="grid lg:grid-cols-12 gap-12 items-center h-[800px]">
          {/* Left: Detail Card */}
          <div className="lg:col-span-4 order-2 lg:order-1 relative z-20">
            <FeatureDetail feature={features[activeFeature]} />

            {/* Controls */}
            <div className="flex gap-4 mt-8 justify-center lg:justify-start">
              <button onClick={prevFeature} className="p-4 rounded-full border border-white/10 hover:bg-white/5 text-white/60 hover:text-white hover:border-amber-500/50 transition-all active:scale-95"><ChevronLeft className="w-6 h-6" /></button>
              <button onClick={nextFeature} className="p-4 rounded-full border border-white/10 hover:bg-white/5 text-white/60 hover:text-white hover:border-amber-500/50 transition-all active:scale-95"><ChevronRight className="w-6 h-6" /></button>
            </div>
          </div>

          {/* Right: The Gyroscope */}
          <motion.div
            ref={containerRef}
            className="lg:col-span-8 order-1 lg:order-2 relative h-full min-h-[600px] flex items-center justify-center lg:justify-end"
            style={{ rotateX, rotateY, perspective: 1000 }}
          >
            {/* The "Circule Thing" - Hyper-Cool Edition */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="relative transform scale-75 md:scale-90 lg:scale-[0.85] origin-center transform-style-3d"
            >
              <CentralHub activeFeature={activeFeature} features={features} />
              <FeatureOrbit features={features} activeFeature={activeFeature} onFeatureChange={setActiveFeature} />
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

export default FeatureShowcase
