import React, { useRef, useState } from 'react'
import { motion, useInView, useMotionValue, useSpring, useTransform } from 'framer-motion'
import {
  Target,
  Shield,
  Zap,
  BarChart3,
  Sparkles,
  Layers,
  Users,
  TrendingUp,
  Clock,
  CheckCircle2
} from 'lucide-react'

// 3D Tilt card component
const TiltCard = ({ children, className = "" }) => {
  const ref = useRef(null)
  const [hovering, setHovering] = useState(false)

  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const mouseXSpring = useSpring(x, { stiffness: 300, damping: 30 })
  const mouseYSpring = useSpring(y, { stiffness: 300, damping: 30 })

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["8deg", "-8deg"])
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-8deg", "8deg"])

  const handleMouseMove = (e) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const width = rect.width
    const height = rect.height
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top
    x.set((mouseX / width) - 0.5)
    y.set((mouseY / height) - 0.5)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
    setHovering(false)
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={handleMouseLeave}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      className={`relative ${className}`}
    >
      {/* Glow effect on hover */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: hovering ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        className="absolute -inset-px bg-gradient-to-r from-amber-500/20 via-yellow-500/20 to-amber-500/20 rounded-2xl blur-xl"
      />

      <div
        className="relative bg-zinc-900/80 backdrop-blur-sm border border-white/10 rounded-2xl overflow-hidden h-full"
        style={{ transform: "translateZ(40px)" }}
      >
        {children}
      </div>
    </motion.div>
  )
}

// Feature card content
const FeatureCard = ({ feature, index }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: "-50px" })
  const Icon = feature.icon

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ delay: index * 0.1, duration: 0.6 }}
    >
      <TiltCard className="h-full">
        <div className="p-8">
          {/* Icon */}
          <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6`}>
            <Icon className="w-7 h-7 text-white" />
          </div>

          {/* Content */}
          <h3 className="text-xl font-medium text-white mb-3">{feature.title}</h3>
          <p className="text-white/50 text-sm leading-relaxed mb-6">{feature.description}</p>

          {/* Highlights */}
          <ul className="space-y-2">
            {feature.highlights.map((highlight, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-white/40">
                <CheckCircle2 className="w-4 h-4 text-amber-400/60" />
                {highlight}
              </li>
            ))}
          </ul>
        </div>
      </TiltCard>
    </motion.div>
  )
}

// Main FeatureShowcase component
const FeatureShowcase = () => {
  const sectionRef = useRef(null)
  const inView = useInView(sectionRef, { once: true, margin: "-100px" })

  const features = [
    {
      icon: Target,
      title: "6D ICP Engine",
      description: "Build laser-focused customer profiles with firmographics, technographics, psychographics, behaviors, buying committees, and category context.",
      gradient: "from-purple-500/20 to-purple-900/20",
      highlights: [
        "AI-generated ICP profiles",
        "Fit scoring algorithm",
        "Messaging angle extraction"
      ]
    },
    {
      icon: Shield,
      title: "Barrier Engine",
      description: "Classify exactly where prospects get stuck: Obscurity, Risk, Inertia, Friction, Capacity, or Atrophy. Then attack with precision.",
      gradient: "from-blue-500/20 to-blue-900/20",
      highlights: [
        "6-stage barrier taxonomy",
        "Auto protocol matching",
        "Confidence scoring"
      ]
    },
    {
      icon: Zap,
      title: "Protocol System (A-F)",
      description: "Six battle-tested GTM protocols that map directly to barriers. Authority Blitz, Trust Anchor, Cost of Inaction, and more.",
      gradient: "from-amber-500/20 to-amber-900/20",
      highlights: [
        "Pre-built move templates",
        "Channel recommendations",
        "Success metrics defined"
      ]
    },
    {
      icon: Layers,
      title: "Campaign Command",
      description: "Strategic containers that bind goals, ICPs, barriers, and protocols. Multi-step wizard gets you from chaos to clarity.",
      gradient: "from-emerald-500/20 to-emerald-900/20",
      highlights: [
        "Goal-based architecture",
        "Protocol binding",
        "Budget allocation"
      ]
    },
    {
      icon: Sparkles,
      title: "Muse AI Factory",
      description: "Generate battle-ready assets: webinar scripts, email sequences, battlecards, comparison pages. All tailored to your ICP.",
      gradient: "from-pink-500/20 to-pink-900/20",
      highlights: [
        "10+ asset types",
        "ICP-personalized copy",
        "One-click generation"
      ]
    },
    {
      icon: BarChart3,
      title: "RAG Matrix",
      description: "Real-time health dashboard. Red/Amber/Green status for every metric. See problems before they become catastrophes.",
      gradient: "from-cyan-500/20 to-cyan-900/20",
      highlights: [
        "Automated RAG calculation",
        "Trend analysis",
        "Kill switch integration"
      ]
    }
  ]

  return (
    <section
      id="features"
      ref={sectionRef}
      className="relative py-32 bg-black overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* Gradient orbs */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        {/* Section header */}
        <div className="text-center mb-20">
          <motion.span
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            className="text-[10px] uppercase tracking-[0.4em] text-amber-400/60"
          >
            The System
          </motion.span>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="mt-6 text-4xl md:text-5xl lg:text-6xl font-light text-white"
          >
            Six pillars of{' '}
            <span className="italic font-normal bg-gradient-to-r from-amber-200 via-yellow-100 to-amber-200 bg-clip-text text-transparent">
              GTM control
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="mt-6 text-lg text-white/40 max-w-2xl mx-auto"
          >
            Every component designed to work together. Strategy flows into execution flows into measurement.
          </motion.p>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <FeatureCard key={index} feature={feature} index={index} />
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.8, duration: 0.6 }}
          className="mt-16 text-center"
        >
          <p className="text-white/30 text-sm">
            And this is just the foundation. The Spike system brings it all together.
          </p>
        </motion.div>
      </div>
    </section>
  )
}

export default FeatureShowcase

