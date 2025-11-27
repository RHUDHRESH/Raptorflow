import { Link } from 'react-router-dom'
import {
  Sparkles,
  Target,
  Shield,
  ArrowRight,
  CheckCircle2,
  Zap,
  TrendingUp,
  Users,
  Brain,
  Rocket,
  ChevronRight,
  Clock,
  BarChart3,
  Layers,
  Calendar,
  FileText,
  Lock,
  Mail,
  Download,
  BookOpen,
  Map,
  ClipboardList,
  AlertCircle,
  X,
  Check,
  Minus,
  Star,
  Circle,
  Plus,
  ChevronDown,
  Menu,
  Globe,
  Activity,
  Award,
  DollarSign
} from 'lucide-react'
import { motion, useScroll, useTransform, useSpring, useInView, AnimatePresence } from 'framer-motion'
import { useRef, useState, useEffect, memo, useCallback } from 'react'

// ============================================================================
// OPTIMIZED ANIMATED COUNTER
// ============================================================================
const AnimatedCounter = memo(({ end, duration = 2, suffix = '', prefix = '' }) => {
  const [count, setCount] = useState(0)
  const nodeRef = useRef(null)
  const isInView = useInView(nodeRef, { once: true, amount: 0.5 })

  useEffect(() => {
    if (!isInView) return

    let startTime = null
    let rafId = null

    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / (duration * 1000), 1)
      const easeOutQuart = 1 - Math.pow(1 - progress, 4)
      setCount(Math.floor(easeOutQuart * end))

      if (progress < 1) {
        rafId = requestAnimationFrame(animate)
      }
    }
    rafId = requestAnimationFrame(animate)

    return () => {
      if (rafId) cancelAnimationFrame(rafId)
    }
  }, [isInView, end, duration])

  return (
    <span ref={nodeRef} className="tabular-nums">
      {prefix}{count}{suffix}
    </span>
  )
})

AnimatedCounter.displayName = 'AnimatedCounter'

// ============================================================================
// IMPROVED COHORT ROTATOR WITH MANUAL CONTROLS
// ============================================================================
const CohortRotator = memo(() => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPaused, setIsPaused] = useState(false)

  const cohorts = [
    {
      title: 'Overwhelmed Agency Owner',
      whoTheyAre: 'Runs a 5-15 person marketing agency. Drowning in client deliverables. Struggles to find time for their own marketing.',
      whatTheyNeed: 'A system that doesn\'t add more work. Clear priorities. Finishable tasks that fit between client calls.',
      howYouHelp: '"Marketing that fits your actual life. 1-3 moves per week. No guilt, just clarity."'
    },
    {
      title: 'Solo Founder Wearing All Hats',
      whoTheyAre: 'Building a product solo. Marketing feels like a distraction. Every hour counts. No team to delegate to.',
      whatTheyNeed: 'Marketing that doesn\'t require a full-time commitment. Clear next steps. No analysis paralysis.',
      howYouHelp: '"Ship marketing moves between product sprints. Stay visible without burning out."'
    },
    {
      title: 'Product Manager Launching New Feature',
      whoTheyAre: 'Responsible for adoption metrics. Needs users to actually try the new feature. Limited marketing budget.',
      whatTheyNeed: 'Targeted campaigns that reach the right users. Measurable results. Fast execution.',
      howYouHelp: '"Turn feature launches into focused campaigns. Track what matters. No vanity metrics."'
    }
  ]

  useEffect(() => {
    if (isPaused) return

    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % cohorts.length)
    }, 6000)

    return () => clearInterval(timer)
  }, [isPaused, cohorts.length])

  const handleDotClick = useCallback((index) => {
    setCurrentIndex(index)
    setIsPaused(true)
    setTimeout(() => setIsPaused(false), 10000) // Resume after 10s
  }, [])

  const currentCohort = cohorts[currentIndex]

  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
      className="relative"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="mb-6 flex items-center gap-3">
        <Check className="h-6 w-6 text-green-600" strokeWidth={3} />
        <span className="text-sm font-bold uppercase tracking-wider text-gray-500">
          With RaptorFlow cohorts
        </span>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5 }}
          whileHover={{
            scale: 1.02,
            boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
            transition: { duration: 0.2 }
          }}
          className="border-2 border-black bg-black p-8 text-white relative overflow-hidden min-h-[450px] flex flex-col shadow-2xl"
        >
          {/* Shimmer */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
            animate={{
              x: ['-200%', '200%'],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              repeatDelay: 2
            }}
          />

          <div className="mb-6 relative z-10">
            <h3 className="font-serif text-3xl font-black mb-3">
              ICP Cohort: "{currentCohort.title}"
            </h3>
            <div className="h-1 w-16 bg-white rounded-full" />
          </div>

          <div className="space-y-6 text-white/90 relative z-10 flex-1">
            <div>
              <p className="text-xs uppercase tracking-wider text-white/60 mb-2 font-bold">
                Who They Are
              </p>
              <p className="text-base leading-relaxed">
                {currentCohort.whoTheyAre}
              </p>
            </div>

            <div>
              <p className="text-xs uppercase tracking-wider text-white/60 mb-2 font-bold">
                What They Need
              </p>
              <p className="text-base leading-relaxed">
                {currentCohort.whatTheyNeed}
              </p>
            </div>

            <div>
              <p className="text-xs uppercase tracking-wider text-white/60 mb-2 font-bold">
                How You Help
              </p>
              <p className="text-base leading-relaxed font-serif italic">
                {currentCohort.howYouHelp}
              </p>
            </div>

            <div className="pt-6 mt-auto border-t border-white/10">
              <p className="text-sm text-white/70 font-bold">
                ✓ Specific, actionable, real
              </p>
            </div>
          </div>

          {/* Manual control dots */}
          <div className="absolute bottom-4 right-4 flex gap-2 z-10">
            {cohorts.map((_, i) => (
              <motion.button
                key={i}
                onClick={() => handleDotClick(i)}
                className={`h-2.5 w-2.5 rounded-full transition-all cursor-pointer ${i === currentIndex ? 'bg-white w-6' : 'bg-white/30 hover:bg-white/50'
                  }`}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                aria-label={`View cohort ${i + 1}`}
              />
            ))}
          </div>
        </motion.div>
      </AnimatePresence>
    </motion.div>
  )
})

CohortRotator.displayName = 'CohortRotator'

// ============================================================================
// IMPROVED MAGNETIC BUTTON
// ============================================================================
const MagneticButton = memo(({ children, className, to, onClick }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const buttonRef = useRef(null)

  const handleMouseMove = useCallback((e) => {
    if (!buttonRef.current) return
    const rect = buttonRef.current.getBoundingClientRect()
    const x = (e.clientX - rect.left - rect.width / 2) * 0.3
    const y = (e.clientY - rect.top - rect.height / 2) * 0.3
    setPosition({ x, y })
  }, [])

  const handleMouseLeave = useCallback(() => {
    setPosition({ x: 0, y: 0 })
  }, [])

  const Component = to ? Link : 'button'

  return (
    <Component
      to={to}
      ref={buttonRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      className={className}
      style={{
        transform: `translate(${position.x}px, ${position.y}px)`,
        transition: 'transform 0.2s ease-out'
      }}
    >
      {children}
    </Component>
  )
})

MagneticButton.displayName = 'MagneticButton'

// ============================================================================
// FAQ ACCORDION ITEM
// ============================================================================
const FAQItem = memo(({ question, answer, index }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.05 }}
      className="border border-black/10 bg-white overflow-hidden"
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-6 text-left flex items-center justify-between hover:bg-black/[0.02] transition-colors"
        aria-expanded={isOpen}
      >
        <h3 className="font-serif text-xl font-bold pr-8">{question}</h3>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
          className="flex-shrink-0"
        >
          <ChevronDown className="h-6 w-6" />
        </motion.div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <p className="px-6 pb-6 leading-relaxed text-gray-700">
              {answer}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
})

FAQItem.displayName = 'FAQItem'

// ============================================================================
// MOBILE NAVIGATION
// ============================================================================
const MobileNav = memo(({ isOpen, onClose }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={onClose}
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 w-80 bg-white z-50 shadow-2xl"
          >
            <div className="p-6">
              <button
                onClick={onClose}
                className="absolute top-6 right-6 p-2 hover:bg-black/5 rounded-lg transition-colors"
                aria-label="Close menu"
              >
                <X className="h-6 w-6" />
              </button>
              <div className="mt-16 space-y-6">
                <Link
                  to="/login"
                  onClick={onClose}
                  className="block text-lg font-medium hover:text-black/70 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  onClick={onClose}
                  className="block w-full btn-primary text-center"
                >
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
})

MobileNav.displayName = 'MobileNav'


export default function Landing() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const heroRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
    layoutEffect: false
  })

  const y = useTransform(scrollYProgress, [0, 1], [0, 150])
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 1], [1, 0.95])

  // Smooth spring physics
  const springConfig = { stiffness: 100, damping: 30, restDelta: 0.001 }
  const ySpring = useSpring(y, springConfig)

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <div className="min-h-screen bg-cream text-ink overflow-hidden">
      {/* Sticky Navigation with slide down animation */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="sticky top-0 z-50 border-b border-black/10 bg-white/95 backdrop-blur-xl"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/landing" className="group flex items-center gap-3">
              <motion.div
                whileHover={{ scale: 1.1, rotate: 6 }}
                whileTap={{ scale: 0.95 }}
                className="relative flex h-10 w-10 items-center justify-center rounded-lg border-2 border-black bg-black transition-all duration-300 overflow-hidden"
              >
                {/* Pulsing glow effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 opacity-0 group-hover:opacity-20"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0, 0.2, 0]
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />

                {/* Rocket with launch animation */}
                <motion.div
                  animate={{
                    y: [0, -2, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                >
                  <Rocket className="h-5 w-5 text-white relative z-10" strokeWidth={2.5} />
                </motion.div>

                {/* Exhaust particles */}
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute bottom-0 left-1/2 w-1 h-1 bg-orange-400 rounded-full opacity-0 group-hover:opacity-60"
                    animate={{
                      y: [0, 15],
                      x: [0, (i - 1) * 3],
                      opacity: [0.6, 0],
                      scale: [1, 0.5]
                    }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      delay: i * 0.15,
                      ease: "easeOut"
                    }}
                  />
                ))}
              </motion.div>
              <div className="hidden sm:block">
                <span className="text-2xl font-serif font-black tracking-tight">RaptorFlow</span>
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="ml-2 text-xs font-mono uppercase tracking-widest text-gray-400 hidden md:inline"
                >
                  Strategy Engine
                </motion.span>
              </div>
              <div className="sm:hidden">
                <span className="text-xl font-serif font-black tracking-tight">RaptorFlow</span>
              </div>
            </Link>
            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-3">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link to="/login" className="btn-ghost">Sign In</Link>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative group"
              >
                <Link to="/register" className="btn-primary relative overflow-hidden">
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                    animate={{
                      x: ['-200%', '200%'],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      repeatDelay: 1,
                      ease: 'linear'
                    }}
                  />
                  <span className="relative z-10">Get Started</span>
                  <motion.div
                    animate={{ x: [0, 3, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="relative z-10"
                  >
                    <ArrowRight className="h-4 w-4" />
                  </motion.div>
                </Link>
              </motion.div>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileNavOpen(true)}
              className="md:hidden p-2 hover:bg-black/5 rounded-lg transition-colors"
              aria-label="Open menu"
            >
              <Menu className="h-6 w-6" />
            </button>
          </div>
        </div>
      </motion.nav>

      <MobileNav isOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />

      {/* Hero Section with Parallax */}
      <section ref={heroRef} className="relative overflow-hidden border-b border-black/5 bg-white" style={{ position: 'relative' }}>
        {/* Animated Background Grid */}
        <motion.div
          style={{ opacity: useTransform(scrollYProgress, [0, 0.5], [0.03, 0]) }}
          className="absolute inset-0"
        >
          <div className="absolute inset-0" style={{
            backgroundImage: `linear-gradient(to right, black 1px, transparent 1px),
                            linear-gradient(to bottom, black 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }} />
        </motion.div>

        {/* Floating Orbs with parallax */}
        <motion.div
          style={{ y: useTransform(scrollYProgress, [0, 1], [0, -50]) }}
          className="floating-orb left-[10%] top-20 h-64 w-64 bg-gray-200"
        />
        <motion.div
          style={{ y: useTransform(scrollYProgress, [0, 1], [0, -100]) }}
          className="floating-orb right-[15%] top-40 h-80 w-80 bg-gray-100"
        />
        <motion.div
          style={{ y: useTransform(scrollYProgress, [0, 1], [0, -75]) }}
          className="floating-orb left-[20%] bottom-20 h-72 w-72 bg-gray-300"
        />

        {/* Floating particles */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute h-2 w-2 rounded-full bg-black/5"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.1, 0.3, 0.1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}

        <motion.div
          style={{ y: ySpring, opacity, scale }}
          className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 py-20 sm:py-32 md:py-40">
          <div className="max-w-5xl">
            {/* Badge with pulse animation */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              whileHover={{ scale: 1.05 }}
              className="mb-8 inline-flex items-center gap-2 rounded-sm border border-black/20 bg-black px-4 py-2"
            >
              <motion.div
                animate={{ rotate: [0, 5, -5, 0] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
              >
                <Sparkles className="h-4 w-4 text-white" strokeWidth={2} />
              </motion.div>
              <span className="text-xs font-mono uppercase tracking-widest text-white">Marketing Command Center</span>
            </motion.div>

            {/* Main Headline with staggered animation */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="mb-8 font-serif text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-black leading-[0.95] tracking-tighter">
              <motion.span
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="inline-block"
              >
                Marketing
              </motion.span>
              <br />
              <motion.span
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="relative inline-block"
              >
                Clarity
                <svg className="absolute -bottom-4 left-0 w-full" height="20" viewBox="0 0 400 20" fill="none">
                  <motion.path
                    d="M0 10 Q 200 20, 400 10"
                    stroke="black"
                    strokeWidth="3"
                    fill="none"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 1 }}
                    transition={{ duration: 1.2, delay: 0.8, ease: "easeInOut" }}
                  />
                </svg>
              </motion.span>
              <br />
              <motion.span
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="inline-block"
              >
                In Minutes
              </motion.span>
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="mb-12 max-w-2xl text-lg sm:text-xl md:text-2xl leading-relaxed text-gray-700"
            >
              Stop drowning in tasks. RaptorFlow turns chaos into clarity with smart cohorts,
              strategic moves, and a system that actually helps you <motion.span
                className="font-serif italic"
                whileHover={{ scale: 1.1, display: 'inline-block' }}
              >
                finish
              </motion.span> what you start.
            </motion.p>

            {/* CTA Buttons with magnetic effect */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="mb-16 flex flex-col sm:flex-row flex-wrap items-center gap-4"
            >
              <MagneticButton to="/register" className="group btn-primary text-base w-full sm:w-auto">
                Get Started Now
                <motion.div
                  animate={{ x: [0, 3, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ArrowRight className="h-5 w-5" />
                </motion.div>
              </MagneticButton>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="w-full sm:w-auto">
                <Link to="/strategy/wizard" className="btn-secondary text-base w-full sm:w-auto block text-center">
                  See How It Works
                </Link>
              </motion.div>
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="text-sm text-gray-500 flex items-center gap-1"
              >
                <CheckCircle2 className="h-4 w-4" />
                Start in minutes
              </motion.span>
            </motion.div>

            {/* Stats with animated counters */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.7 }}
              className="grid grid-cols-3 gap-8 border-t border-black/10 pt-12"
            >
              {[
                { value: 40, suffix: '%', label: 'Less Busywork' },
                { value: 3, suffix: 'x', label: 'Faster Execution' },
                { value: 100, suffix: '%', label: 'Clarity' }
              ].map((stat, i) => (
                <motion.div
                  key={i}
                  className="group"
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.8 + i * 0.1 }}
                  whileHover={{ scale: 1.1 }}
                >
                  <div className="mb-2 font-serif text-5xl font-black tracking-tight transition-all duration-300">
                    <AnimatedCounter end={stat.value} suffix={stat.suffix} />
                  </div>
                  <div className="text-sm uppercase tracking-wider text-gray-500">{stat.label}</div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="flex flex-col items-center gap-2"
          >
            <span className="text-xs font-mono uppercase tracking-widest text-gray-400">Scroll</span>
            <motion.div
              animate={{ scaleY: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <ChevronRight className="h-5 w-5 rotate-90 text-gray-400" />
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* Why Now - Honest messaging */}
      <section className="border-b border-black/5 bg-cream py-20 relative overflow-hidden">
        <motion.div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `linear-gradient(to right, black 1px, transparent 1px),
                            linear-gradient(to bottom, black 1px, transparent 1px)`,
            backgroundSize: '80px 80px'
          }}
          animate={{
            backgroundPosition: ['0px 0px', '80px 80px'],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center max-w-3xl mx-auto"
          >
            <motion.p
              className="text-micro mb-4"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              The Problem
            </motion.p>
            <h2 className="mb-6 font-serif text-5xl font-black tracking-tight">
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="inline-block"
              >
                Most Marketing Tools
              </motion.span>
              <br />
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 }}
                className="inline-block"
              >
                Let You Do Everything
              </motion.span>
            </h2>
            <motion.p
              className="text-xl text-gray-600 leading-relaxed"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              Which means you <span className="font-bold text-black">finish nothing</span>. RaptorFlow caps you at{' '}
              <span className="font-bold text-black">7 cohorts</span>,{' '}
              <span className="font-bold text-black">3 moves/week</span>,{' '}
              <span className="font-bold text-black">3 actions/day</span>.{' '}
              Less choice. More done.
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Not Another "Post Every Day" Tool */}
      <section className="border-b border-black/5 bg-white py-32 relative overflow-hidden">
        {/* Subtle grid background */}
        <motion.div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(to right, black 1px, transparent 1px),
                            linear-gradient(to bottom, black 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
          animate={{
            backgroundPosition: ['0px 0px', '60px 60px'],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 text-center"
          >
            <motion.p
              className="text-micro mb-4"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              A Different Approach
            </motion.p>
            <h2 className="mb-6 font-serif text-6xl font-black tracking-tight">
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="inline-block"
              >
                This is not another
              </motion.span>
              <br />
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 }}
                className="inline-block"
              >
                "post every day" tool
              </motion.span>
            </h2>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-2 max-w-6xl mx-auto">
            {/* The Usual Marketing Advice */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative border-2 border-black/10 bg-cream p-8"
            >
              <div className="mb-6">
                <motion.div
                  className="inline-flex items-center gap-2 mb-4"
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                >
                  <X className="h-6 w-6 text-red-600" strokeWidth={3} />
                  <span className="text-micro text-gray-500">The usual marketing advice</span>
                </motion.div>
                <h3 className="font-serif text-3xl font-black tracking-tight mb-6">
                  The Hamster Wheel
                </h3>
              </div>

              <ul className="space-y-4">
                {[
                  'Post every single day (even when you have nothing to say)',
                  'Make Reels! Dance! Point at text!',
                  'Use these 47 templates (that everyone else is using)',
                  'Try this one weird hack (that worked once for someone else)'
                ].map((item, i) => (
                  <motion.li
                    key={i}
                    className="flex items-start gap-3 text-gray-700"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <Minus className="mt-1 h-5 w-5 flex-shrink-0 text-gray-400" strokeWidth={2} />
                    <span className="text-lg leading-relaxed">{item}</span>
                  </motion.li>
                ))}
              </ul>

              {/* Subtle corner decoration */}
              <motion.div
                className="absolute -bottom-8 -right-8 h-24 w-24 rounded-full bg-black/[0.03]"
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5, type: 'spring' }}
              />
            </motion.div>

            {/* What RaptorFlow Cares About */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              whileHover={{
                scale: 1.02,
                boxShadow: '0 20px 60px rgba(0,0,0,0.1)',
                transition: { duration: 0.2 }
              }}
              className="relative border-2 border-black bg-black p-8 text-white"
            >
              <div className="mb-6">
                <motion.div
                  className="inline-flex items-center gap-2 mb-4"
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                >
                  <Check className="h-6 w-6 text-green-400" strokeWidth={3} />
                  <span className="text-micro text-white/60">What RaptorFlow cares about instead</span>
                </motion.div>
                <h3 className="font-serif text-3xl font-black tracking-tight mb-6">
                  Actual Marketing
                </h3>
              </div>

              <ul className="space-y-4 mb-8">
                {[
                  'Real people with real problems you can actually help',
                  'Clear objectives that tie to your business goals',
                  'Finishable work that fits into your actual life',
                  'Less guilt, more clarity, better marketing'
                ].map((item, i) => (
                  <motion.li
                    key={i}
                    className="flex items-start gap-3"
                    initial={{ opacity: 0, x: 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    whileHover={{ x: 5 }}
                  >
                    <motion.div
                      className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10 flex-shrink-0 mt-1"
                      whileHover={{ rotate: 360, backgroundColor: 'rgba(255,255,255,0.2)' }}
                      transition={{ duration: 0.5 }}
                    >
                      <Check className="h-4 w-4 text-white" strokeWidth={3} />
                    </motion.div>
                    <span className="text-lg leading-relaxed text-white/90">{item}</span>
                  </motion.li>
                ))}
              </ul>

              {/* Bottom tagline */}
              <motion.div
                className="pt-6 border-t border-white/10"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 }}
              >
                <p className="text-xl font-bold text-white">
                  No gurus. No fake urgency.
                  <br />
                  <span className="text-white/70">Just a clearer brain for your marketing.</span>
                </p>
              </motion.div>

              {/* Shimmer effect */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
                animate={{
                  x: ['-200%', '200%'],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  repeatDelay: 2,
                  ease: 'easeInOut'
                }}
              />
            </motion.div>
          </div>
        </div>
      </section>

      {/* Your Buyers as Cohorts - With Visual Comparison */}
      <section className="border-b border-black/5 bg-cream py-32 relative overflow-hidden">
        <motion.div
          className="absolute top-20 right-10 h-96 w-96 rounded-full bg-black/[0.02] blur-3xl"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 12, repeat: Infinity }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-24 text-center"
          >
            <p className="text-micro mb-6">Core Concept</p>
            <h2 className="mb-8 font-serif text-6xl font-black tracking-tight max-w-4xl mx-auto leading-[1.1]">
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="inline-block"
              >
                Your Buyers
              </motion.span>
              <br />
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 }}
                className="inline-block"
              >
                as Cohorts
              </motion.span>
            </h2>
            <motion.p
              className="max-w-3xl mx-auto text-2xl text-gray-700 leading-relaxed"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              Instead of vague "target audiences," RaptorFlow helps you create <span className="font-bold text-black">ICP cohorts</span>—detailed profiles of real people you're trying to reach.
            </motion.p>
          </motion.div>

          {/* Visual Before/After Comparison */}
          <div className="grid gap-12 md:grid-cols-2 mb-20">
            {/* Before - Vague Target Audience */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative"
            >
              <div className="mb-6 flex items-center gap-3">
                <X className="h-6 w-6 text-red-600" strokeWidth={3} />
                <span className="text-sm font-bold uppercase tracking-wider text-gray-500">How most people market</span>
              </div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                className="border-2 border-black/10 bg-white p-8 relative min-h-[400px] flex flex-col"
              >
                <div className="mb-6">
                  <h3 className="font-serif text-3xl font-black mb-3 text-gray-400">Target Audience</h3>
                  <div className="h-1 w-16 bg-gray-300 rounded-full" />
                </div>

                <div className="space-y-6 text-gray-500 flex-1">
                  <p className="text-2xl font-bold">
                    "Small business owners"
                  </p>
                  <div className="space-y-3 text-lg opacity-60">
                    <p>Age: 25-45</p>
                    <p>Location: Urban areas</p>
                    <p>Income: $50K-$150K</p>
                  </div>
                  <div className="pt-6 mt-auto border-t border-gray-200">
                    <p className="text-sm text-gray-400 italic">
                      Vague, generic, could be anyone...
                    </p>
                  </div>
                </div>
              </motion.div>
            </motion.div>

            {/* After - Detailed ICP Cohort with Rotation */}
            <CohortRotator />
          </div>

          {/* Three Key Elements */}
          <div className="grid gap-10 md:grid-cols-3 mb-16">
            {[
              {
                title: 'Who They Are',
                desc: 'Not demographics. Real people with real contexts, jobs, and daily struggles.',
                icon: Users
              },
              {
                title: 'What They Need',
                desc: 'The specific problems they face that you can actually solve.',
                icon: Target
              },
              {
                title: 'How You Help',
                desc: 'Your unique value proposition, in their language, not yours.',
                icon: Zap
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, type: 'spring' }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="border-2 border-black/10 bg-white p-8 hover:border-black/20 transition-all duration-300"
              >
                <motion.div
                  className="flex h-14 w-14 items-center justify-center rounded-lg border-2 border-black bg-black mb-6"
                  whileHover={{ rotate: 12, scale: 1.1 }}
                >
                  <item.icon className="h-7 w-7 text-white" strokeWidth={2.5} />
                </motion.div>
                <h3 className="font-serif text-2xl font-black mb-4">{item.title}</h3>
                <p className="text-gray-700 leading-relaxed text-lg">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          {/* Bottom CTA */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="border-2 border-black bg-black p-10 text-white"
          >
            <div className="max-w-3xl">
              <h3 className="font-serif text-4xl font-black mb-8 leading-tight">
                Stop talking to "everyone"
              </h3>
              <p className="text-2xl text-white/90 leading-relaxed mb-8">
                Use cohorts to guide every piece of content, every campaign, every decision. When you know exactly who you're talking to, marketing becomes <span className="font-bold text-white">clarity, not chaos</span>.
              </p>
              <motion.div
                className="inline-flex items-center gap-3 text-white/70 text-lg"
                whileHover={{ x: 5 }}
              >
                <ArrowRight className="h-6 w-6" />
                <span className="font-medium uppercase tracking-wider">Start talking to real people</span>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* What You Get - Rule of 3 */}
      <section className="border-b border-black/5 bg-white py-32 relative overflow-hidden">
        {/* Animated grid */}
        <motion.div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `linear-gradient(to right, black 1px, transparent 1px),
                            linear-gradient(to bottom, black 1px, transparent 1px)`,
            backgroundSize: '80px 80px'
          }}
          animate={{
            backgroundPosition: ['0px 0px', '80px 80px'],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 text-center"
          >
            <p className="text-micro mb-4">What You Get</p>
            <h2 className="mb-6 font-serif text-6xl font-black tracking-tight">
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="inline-block"
              >
                Everything You Need.
              </motion.span>
              <br />
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 }}
                className="inline-block"
              >
                Nothing You Don't.
              </motion.span>
            </h2>
            <motion.p
              className="text-xl text-gray-600 max-w-3xl mx-auto"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              Stop guessing and start shipping marketing that makes sense
            </motion.p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3 max-w-6xl mx-auto">
            {[
              {
                number: '01',
                title: 'Define',
                subtitle: 'Your Real Buyers',
                desc: 'Cohort builder that captures who they are, what they struggle with, and how you help. No more vague "target audiences."',
                icon: Target,
                features: ['ICP cohorts', 'Microproofs', 'Real language']
              },
              {
                number: '02',
                title: 'Plan',
                subtitle: 'Strategic Moves',
                desc: 'Campaign planner that turns ideas into finishable work. 1-3 moves per week, each with clear objectives and posture.',
                icon: Brain,
                features: ['Weekly moves', 'Daily actions', 'Brain dump tool']
              },
              {
                number: '03',
                title: 'Ship',
                subtitle: 'Track Progress',
                desc: 'See what\'s working without vanity metrics. Track posture mix, cadence streaks, and what actually drives growth.',
                icon: TrendingUp,
                features: ['Real analytics', 'Tone guardian', 'Team sync']
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 60, rotateX: -20 }}
                whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
                viewport={{ once: true }}
                transition={{
                  delay: i * 0.15,
                  type: 'spring',
                  stiffness: 80
                }}
                whileHover={{
                  y: -12,
                  scale: 1.03,
                  boxShadow: '0 25px 60px rgba(0,0,0,0.12)',
                  transition: { duration: 0.3 }
                }}
                className="group relative border-2 border-black/10 bg-cream p-8 hover:border-black/20 transition-all duration-300"
                style={{ transformStyle: 'preserve-3d' }}
              >
                {/* Number badge */}
                <motion.div
                  className="absolute -top-4 -right-4 h-16 w-16 rounded-full border-2 border-black bg-black flex items-center justify-center"
                  initial={{ scale: 0, rotate: -180 }}
                  whileInView={{ scale: 1, rotate: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.15 + 0.3, type: 'spring' }}
                  whileHover={{ rotate: 360 }}
                >
                  <span className="font-mono text-xl font-black text-white">{item.number}</span>
                </motion.div>

                {/* Icon */}
                <motion.div
                  className="flex h-16 w-16 items-center justify-center rounded-xl border-2 border-black bg-black mb-6 relative overflow-hidden"
                  whileHover={{
                    scale: 1.1,
                    rotate: [0, -5, 5, -5, 0]
                  }}
                  transition={{ duration: 0.5 }}
                >
                  {/* Shimmer */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                    animate={{
                      x: ['-200%', '200%'],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      repeatDelay: 2,
                      delay: i * 0.5
                    }}
                  />
                  <item.icon className="h-8 w-8 text-white relative z-10" strokeWidth={2.5} />
                </motion.div>

                {/* Content */}
                <div className="mb-6">
                  <h3 className="font-serif text-4xl font-black tracking-tight mb-2">{item.title}</h3>
                  <p className="text-micro text-gray-500 mb-4">{item.subtitle}</p>
                  <motion.div
                    className="h-1 w-16 bg-black rounded-full"
                    initial={{ width: 0 }}
                    whileInView={{ width: 64 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.15 + 0.4, duration: 0.6 }}
                  />
                </div>

                <p className="text-lg leading-relaxed text-gray-700 mb-6">
                  {item.desc}
                </p>

                {/* Features */}
                <ul className="space-y-2">
                  {item.features.map((feature, j) => (
                    <motion.li
                      key={j}
                      className="flex items-center gap-2 text-sm text-gray-600"
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.15 + j * 0.05 + 0.5 }}
                    >
                      <Check className="h-4 w-4 flex-shrink-0" strokeWidth={3} />
                      <span>{feature}</span>
                    </motion.li>
                  ))}
                </ul>

                {/* Corner decoration */}
                <motion.div
                  className="absolute -bottom-8 -left-8 h-24 w-24 rounded-full bg-black/[0.03]"
                  initial={{ scale: 0, rotate: 0 }}
                  whileInView={{ scale: 1, rotate: 45 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.15 + 0.6, type: 'spring' }}
                />
              </motion.div>
            ))}
          </div>

          {/* Bottom tagline */}
          <motion.div
            className="mt-16 text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
          >
            <p className="text-2xl font-serif font-black text-gray-900">
              No templates. No gurus. No BS.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Before/After Comparison with slide-in animations */}
      <section className="border-b border-black/5 bg-cream py-32">
        <div className="mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-20 text-center"
          >
            <motion.p
              className="text-micro mb-4"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              The Difference
            </motion.p>
            <h2 className="mb-6 font-serif text-6xl font-black tracking-tight">
              <motion.span
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 }}
                className="inline-block"
              >
                Chaos
              </motion.span>{' '}
              <motion.span
                initial={{ opacity: 0, scale: 0 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 }}
                className="inline-block"
              >
                vs.
              </motion.span>{' '}
              <motion.span
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3 }}
                className="inline-block"
              >
                Clarity
              </motion.span>
            </h2>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-2">
            {/* Before */}
            <motion.div
              initial={{ opacity: 0, x: -50, rotateY: -10 }}
              whileInView={{ opacity: 1, x: 0, rotateY: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              whileHover={{ scale: 1.02, rotateY: 2 }}
              className="border-2 border-black/20 bg-white p-8"
              style={{ transformStyle: 'preserve-3d' }}
            >
              <div className="mb-6 flex items-center gap-3">
                <motion.div
                  animate={{ rotate: [0, 90, 0] }}
                  transition={{ duration: 0.5 }}
                >
                  <X className="h-8 w-8" strokeWidth={3} />
                </motion.div>
                <h3 className="font-serif text-3xl font-black">Without RaptorFlow</h3>
              </div>
              <ul className="space-y-4">
                {[
                  'Drowning in endless task lists',
                  'No clear audience definition',
                  'Random acts of marketing',
                  'Inconsistent brand voice',
                  'Can\'t measure what matters',
                  'Team always misaligned',
                  'Burnout from busywork'
                ].map((item, i) => (
                  <motion.li
                    key={i}
                    className="flex items-start gap-3 text-gray-700"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <Minus className="mt-1 h-5 w-5 flex-shrink-0" strokeWidth={2} />
                    <span className="text-lg">{item}</span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>

            {/* After */}
            <motion.div
              initial={{ opacity: 0, x: 50, rotateY: 10 }}
              whileInView={{ opacity: 1, x: 0, rotateY: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              whileHover={{ scale: 1.02, rotateY: -2, boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)' }}
              className="border-2 border-black bg-black p-8 text-white"
              style={{ transformStyle: 'preserve-3d' }}
            >
              <div className="mb-6 flex items-center gap-3">
                <motion.div
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ type: 'spring', stiffness: 200 }}
                >
                  <Check className="h-8 w-8" strokeWidth={3} />
                </motion.div>
                <h3 className="font-serif text-3xl font-black">With RaptorFlow</h3>
              </div>
              <ul className="space-y-4">
                {[
                  '1-3 focused moves per week',
                  'Crystal-clear cohort definitions',
                  'Strategic, posture-aware execution',
                  'AI-powered tone consistency',
                  'Track only what drives growth',
                  'Real-time team alignment',
                  'Sustainable, calm workflow'
                ].map((item, i) => (
                  <motion.li
                    key={i}
                    className="flex items-start gap-3"
                    initial={{ opacity: 0, x: 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    whileHover={{ x: 5 }}
                  >
                    <Check className="mt-1 h-5 w-5 flex-shrink-0" strokeWidth={2} />
                    <span className="text-lg">{item}</span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Grid with staggered animations */}
      <section className="border-b border-black/5 bg-white py-32 relative overflow-hidden">
        {/* Background decoration */}
        <motion.div
          className="absolute top-20 right-10 h-64 w-64 rounded-full bg-gray-100 blur-3xl opacity-50"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-20"
          >
            <p className="text-micro mb-4">System</p>
            <h2 className="mb-6 font-serif text-6xl font-black tracking-tight">
              Everything You Need.
              <br />
              Nothing You Don't.
            </h2>
            <p className="max-w-2xl text-xl text-gray-700">
              A complete marketing command center designed for teams who want results, not busywork.
            </p>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: Target,
                title: 'Smart Cohorts',
                description: 'Define rare audiences with microproofs, objections, and language your buyers actually use.',
                metric: '3-7 cohorts',
                color: 'from-gray-900 to-black'
              },
              {
                icon: Brain,
                title: 'Strategic Moves',
                description: 'Plan operations with posture-aware pacing. Offensive when hot, defensive when protecting altitude.',
                metric: '1-3 weekly moves',
                color: 'from-black to-gray-800'
              },
              {
                icon: Zap,
                title: 'Daily Actions',
                description: 'Execute with focus. Time-boxed tasks that actually move the needle, not busywork.',
                metric: '3 actions/day',
                color: 'from-gray-800 to-gray-900'
              },
              {
                icon: Shield,
                title: 'Tone Guardian',
                description: 'AI sentinel that flags drift, fatigue, and cadence gaps without adding another inbox.',
                metric: '0 tone leaks',
                color: 'from-gray-900 to-black'
              },
              {
                icon: BarChart3,
                title: 'Real Analytics',
                description: 'Track what matters. Posture mix, cadence streaks, and alert count. No vanity metrics.',
                metric: 'Signal only',
                color: 'from-black to-gray-800'
              },
              {
                icon: Layers,
                title: 'Team Sync',
                description: 'Keep everyone aligned with clear ownership, binary status, and exportable recaps.',
                metric: 'One source',
                color: 'from-gray-800 to-gray-900'
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50, scale: 0.9 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true }}
                transition={{
                  duration: 0.5,
                  delay: i * 0.1,
                  type: 'spring',
                  stiffness: 100
                }}
                whileHover={{
                  y: -10,
                  scale: 1.02,
                  transition: { duration: 0.2 }
                }}
                className="group relative overflow-hidden border border-black/10 bg-cream p-8"
              >
                {/* Animated gradient on hover */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-black/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                />

                <div className="relative">
                  <div className="mb-6 flex items-start justify-between">
                    <motion.div
                      className="flex h-14 w-14 items-center justify-center rounded-lg border-2 border-black bg-black"
                      whileHover={{
                        scale: 1.1,
                        rotate: 6,
                        transition: { type: 'spring', stiffness: 400 }
                      }}
                    >
                      <feature.icon className="h-7 w-7 text-white" strokeWidth={2} />
                    </motion.div>
                    <motion.span
                      className="text-micro"
                      initial={{ opacity: 0, x: 20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.1 + 0.2 }}
                    >
                      {feature.metric}
                    </motion.span>
                  </div>

                  <h3 className="mb-3 font-serif text-2xl font-bold tracking-tight">{feature.title}</h3>
                  <p className="mb-4 leading-relaxed text-gray-700">{feature.description}</p>

                  <motion.div
                    className="flex items-center text-sm font-medium uppercase tracking-wider"
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 0 }}
                    whileHover={{ opacity: 1 }}
                  >
                    Learn more
                    <motion.div
                      animate={{ x: [0, 3, 0] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    >
                      <ChevronRight className="ml-1 h-4 w-4" />
                    </motion.div>
                  </motion.div>
                </div>

                {/* Corner decoration */}
                <motion.div
                  className="absolute -bottom-8 -right-8 h-24 w-24 rounded-full bg-black/5"
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 + 0.3, type: 'spring' }}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Weekly Cadence Timeline */}
      <section className="border-b border-black/5 bg-cream py-32 relative overflow-hidden">
        <motion.div
          className="absolute top-20 left-10 h-96 w-96 rounded-full bg-black/[0.02] blur-3xl"
          animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 10, repeat: Infinity }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20"
          >
            <p className="text-micro mb-4">Weekly Rhythm</p>
            <h2 className="mb-6 font-serif text-6xl font-black tracking-tight">
              Seven Days of
              <br />
              Calm Execution
            </h2>
            <p className="max-w-2xl text-xl text-gray-700">
              A proven weekly cadence that turns marketing chaos into a sustainable, finishable system.
            </p>
          </motion.div>

          <div className="space-y-4">
            {[
              { day: 'Monday', label: 'Brain Dump', desc: 'Offload the week in 10 minutes. System labels intent, risk, and effort automatically.', num: '01' },
              { day: 'Tuesday', label: 'Cohort Refresh', desc: 'Update microproofs, objections, and language from the week\'s calls and conversations.', num: '02' },
              { day: 'Wednesday', label: 'Lock Moves', desc: 'Choose 1-3 strategic moves. Each gets a finish line, owner, and posture assignment.', num: '03' },
              { day: 'Thursday', label: 'Daily Actions', desc: 'Bite-sized, time-boxed tasks. Ship, log, move on. No endless lists.', num: '04' },
              { day: 'Friday', label: 'Sentinel Review', desc: 'Resolve tone leaks, cadence gaps, and fatigue flags before they compound.', num: '05' },
              { day: 'Saturday', label: 'Weekly Recap', desc: 'One-page summary. Exportable. Board-ready. No slides needed.', num: '06' },
              { day: 'Sunday', label: 'Reset', desc: 'Carry only what matters into the next sprint. Archive the rest.', num: '07' }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08, type: 'spring', stiffness: 100 }}
                whileHover={{
                  x: 10,
                  scale: 1.02,
                  boxShadow: '0 10px 40px rgba(0,0,0,0.08)',
                  transition: { duration: 0.2 }
                }}
                className="group relative border-2 border-black/10 bg-white p-6 hover:border-black/20 transition-all duration-300"
              >
                {/* Progress indicator */}
                <motion.div
                  className="absolute left-0 top-0 bottom-0 w-1 bg-black origin-top"
                  initial={{ scaleY: 0 }}
                  whileInView={{ scaleY: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 + 0.2, duration: 0.4 }}
                />

                <div className="flex items-start gap-6">
                  {/* Day number badge */}
                  <motion.div
                    className="flex-shrink-0 flex h-16 w-16 items-center justify-center rounded-lg border-2 border-black bg-black relative overflow-hidden"
                    whileHover={{
                      scale: 1.1,
                      rotate: [0, -5, 5, -5, 0],
                      transition: { duration: 0.5 }
                    }}
                  >
                    {/* Shimmer */}
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                      animate={{
                        x: ['-200%', '200%'],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        repeatDelay: 2,
                        delay: i * 0.3
                      }}
                    />
                    <span className="font-mono text-2xl font-black text-white relative z-10">{item.num}</span>
                  </motion.div>

                  <div className="flex-1">
                    <div className="flex items-baseline gap-3 mb-2">
                      <h3 className="font-serif text-2xl font-black tracking-tight">{item.day}</h3>
                      <motion.span
                        className="text-micro"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: i * 0.08 + 0.3 }}
                      >
                        {item.label}
                      </motion.span>
                    </div>

                    {/* Animated underline */}
                    <motion.div
                      className="h-0.5 bg-black rounded-full mb-3"
                      initial={{ width: 0 }}
                      whileInView={{ width: 80 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.08 + 0.4, duration: 0.5 }}
                    />

                    <motion.p
                      className="text-gray-700 leading-relaxed"
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.08 + 0.5 }}
                    >
                      {item.desc}
                    </motion.p>
                  </div>

                  {/* Hover arrow */}
                  <motion.div
                    className="opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <ArrowRight className="h-6 w-6 text-black" strokeWidth={2} />
                  </motion.div>
                </div>

                {/* Corner decoration */}
                <motion.div
                  className="absolute -bottom-6 -right-6 h-16 w-16 rounded-full bg-black/[0.03]"
                  initial={{ scale: 0, rotate: 0 }}
                  whileInView={{ scale: 1, rotate: 45 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 + 0.6, type: 'spring' }}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Deliverables */}
      <section className="border-b border-black/5 bg-white py-32">
        <div className="mx-auto max-w-7xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20"
          >
            <p className="text-micro mb-4">Outputs</p>
            <h2 className="mb-6 font-serif text-6xl font-black tracking-tight">
              What Leaves
              <br />
              The Room
            </h2>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                icon: FileText,
                title: 'Runway Brief',
                desc: 'Single page. Cohorts, objective, posture, and three moves. Made to send, not to present.',
                features: ['PDF export', 'Markdown copy', 'Print-ready']
              },
              {
                icon: ClipboardList,
                title: 'Cadence Log',
                desc: 'Daily actions with timestamps and outcomes. Receipts without the bloat.',
                features: ['Action history', 'Time tracking', 'Owner logs']
              },
              {
                icon: AlertCircle,
                title: 'Signals Board',
                desc: 'Tone leaks, fatigue, risks, and callouts. Only when action is required.',
                features: ['Alert summary', 'Risk flags', 'Trend analysis']
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50, rotateX: -10 }}
                whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15, type: 'spring' }}
                whileHover={{ y: -10, rotateX: 5, scale: 1.02 }}
                className="group border-2 border-black/10 bg-cream p-8 transition-all duration-300 hover:border-black hover:shadow-[0_20px_60px_rgba(0,0,0,0.15)]"
                style={{ transformStyle: 'preserve-3d' }}
              >
                <motion.div
                  className="mb-6 flex h-16 w-16 items-center justify-center rounded-lg border-2 border-black bg-white transition-all duration-300 group-hover:bg-black"
                  whileHover={{ rotate: 12, scale: 1.1 }}
                >
                  <item.icon className="h-8 w-8 transition-colors group-hover:text-white" strokeWidth={2} />
                </motion.div>
                <h3 className="mb-3 font-serif text-2xl font-bold tracking-tight">{item.title}</h3>
                <p className="mb-6 leading-relaxed text-gray-700">{item.desc}</p>
                <ul className="space-y-2 border-t border-black/10 pt-4">
                  {item.features.map((feature, j) => (
                    <motion.li
                      key={j}
                      className="flex items-center gap-2 text-sm"
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.15 + j * 0.05 }}
                    >
                      <Check className="h-4 w-4" strokeWidth={2} />
                      {feature}
                    </motion.li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases – Clean monochrome with sophisticated animations */}
      <section className="border-b border-black/5 bg-white py-32 relative overflow-hidden">
        {/* Subtle animated grid background */}
        <motion.div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `linear-gradient(to right, black 1px, transparent 1px),
                            linear-gradient(to bottom, black 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
          animate={{
            backgroundPosition: ['0px 0px', '60px 60px'],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        />

        {/* Floating subtle orbs */}
        <motion.div
          className="absolute top-20 left-10 h-96 w-96 rounded-full bg-black/[0.02] blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 30, 0],
            y: [0, -20, 0]
          }}
          transition={{ duration: 15, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-20 right-10 h-96 w-96 rounded-full bg-black/[0.015] blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            x: [0, -40, 0],
            y: [0, 30, 0]
          }}
          transition={{ duration: 18, repeat: Infinity }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 text-center"
          >
            <motion.p
              className="text-micro mb-4"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
            >
              Perfect For
            </motion.p>
            <h2 className="mb-6 font-serif text-6xl font-black tracking-tight">
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 }}
                className="inline-block"
              >
                Your Team,
              </motion.span>
              <br />
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 }}
                className="inline-block"
              >
                Your Way
              </motion.span>
            </h2>
            <motion.p
              className="text-xl text-gray-600 max-w-2xl mx-auto"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              Whether you're flying solo or leading a team, RaptorFlow adapts to your workflow
            </motion.p>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-2">
            {[
              {
                title: 'Solo Founders',
                icon: Users,
                tagline: 'You wear all the hats. RaptorFlow gives you a marketing system that doesn\'t require a team.',
                benefits: [
                  'Quick setup (< 1 hour)',
                  'No learning curve',
                  'Scales with you'
                ],
                cta: 'Start Free',
                link: '/register'
              },
              {
                title: 'Lean Marketing Teams',
                icon: Shield,
                tagline: 'Small team, big ambitions. Stay aligned without endless meetings and status updates.',
                benefits: [
                  'Clear ownership',
                  'Async-friendly',
                  'No tool sprawl'
                ],
                cta: 'Start Free',
                link: '/register'
              },
              {
                title: 'Agencies',
                icon: Rocket,
                tagline: 'Manage multiple clients with consistent quality. Export briefs and recaps in seconds.',
                benefits: [
                  'Client-ready exports',
                  'Template library',
                  'White-label ready'
                ],
                cta: 'Start Free',
                link: '/register'
              },
              {
                title: 'Product Teams',
                icon: Brain,
                tagline: 'Launch features with clarity. Define cohorts, plan moves, track what resonates.',
                benefits: [
                  'Launch playbooks',
                  'Feature adoption',
                  'User feedback loops'
                ],
                cta: 'Start Free',
                link: '/register'
              }
            ].map((useCase, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50, rotateX: -15 }}
                whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
                viewport={{ once: true }}
                transition={{
                  delay: i * 0.1,
                  type: 'spring',
                  stiffness: 100,
                  damping: 15
                }}
                whileHover={{
                  y: -8,
                  scale: 1.02,
                  boxShadow: '0 20px 60px rgba(0,0,0,0.08)',
                  transition: { duration: 0.2 }
                }}
                className="group relative border-2 border-black/10 bg-cream p-8 rounded-lg overflow-hidden transition-all duration-300 hover:border-black/20"
                style={{ transformStyle: 'preserve-3d' }}
              >
                {/* Subtle glow on hover */}
                <motion.div
                  className="absolute inset-0 bg-black/[0.02] opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-lg"
                />

                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <motion.div
                        className="flex h-14 w-14 items-center justify-center rounded-xl border-2 border-black bg-black shadow-lg relative overflow-hidden"
                        whileHover={{
                          rotate: [0, -5, 5, -5, 0],
                          scale: 1.1
                        }}
                        transition={{ duration: 0.5 }}
                      >
                        {/* Subtle shimmer */}
                        <motion.div
                          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                          animate={{
                            x: ['-200%', '200%'],
                          }}
                          transition={{
                            duration: 3,
                            repeat: Infinity,
                            repeatDelay: 2,
                            ease: 'easeInOut'
                          }}
                        />
                        <useCase.icon className="h-7 w-7 text-white relative z-10" strokeWidth={2.5} />
                      </motion.div>
                      <div>
                        <h3 className="font-serif text-3xl font-black tracking-tight mb-1">{useCase.title}</h3>
                        <motion.div
                          className="h-1 w-12 bg-black rounded-full"
                          initial={{ width: 0 }}
                          whileInView={{ width: 48 }}
                          viewport={{ once: true }}
                          transition={{ delay: i * 0.1 + 0.3, duration: 0.6 }}
                        />
                      </div>
                    </div>
                  </div>

                  <p className="mb-6 text-lg leading-relaxed text-gray-700 font-medium">
                    {useCase.tagline}
                  </p>

                  <ul className="mb-6 space-y-3">
                    {useCase.benefits.map((benefit, j) => (
                      <motion.li
                        key={j}
                        className="flex items-center gap-3"
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: i * 0.1 + j * 0.05 + 0.4 }}
                        whileHover={{ x: 5 }}
                      >
                        <motion.div
                          className="flex h-6 w-6 items-center justify-center rounded-full bg-black"
                          whileHover={{ rotate: 360 }}
                          transition={{ duration: 0.5 }}
                        >
                          <Check className="h-4 w-4 text-white" strokeWidth={3} />
                        </motion.div>
                        <span className="text-gray-700 font-medium">{benefit}</span>
                      </motion.li>
                    ))}
                  </ul>

                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Link
                      to={useCase.link}
                      className="group/btn inline-flex items-center justify-center gap-2 bg-black px-6 py-3 text-base font-bold text-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden"
                    >
                      {/* Shimmer on button */}
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                        animate={{
                          x: ['-200%', '200%'],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          repeatDelay: 1,
                          ease: 'linear'
                        }}
                      />
                      <span className="relative z-10">{useCase.cta}</span>
                      <motion.div
                        animate={{ x: [0, 3, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="relative z-10"
                      >
                        <ArrowRight className="h-5 w-5" strokeWidth={2.5} />
                      </motion.div>
                    </Link>
                  </motion.div>
                </div>

                {/* Subtle corner decoration */}
                <motion.div
                  className="absolute -bottom-12 -right-12 h-32 w-32 rounded-full bg-black/[0.03]"
                  initial={{ scale: 0, rotate: 0 }}
                  whileInView={{ scale: 1, rotate: 45 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 + 0.5, type: 'spring' }}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing - 3 Tiers */}
      <section className="border-b border-black/5 bg-white py-32 relative overflow-hidden">
        <motion.div
          className="absolute bottom-20 right-10 h-96 w-96 rounded-full bg-gray-100 blur-3xl opacity-40"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 12, repeat: Infinity }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 text-center"
          >
            <p className="text-micro mb-4">Pricing</p>
            <h2 className="mb-6 font-serif text-6xl font-black tracking-tight">
              Simple, Honest Pricing
            </h2>
            <p className="text-xl text-gray-700">Choose your altitude. Scale as you grow.</p>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                name: 'ASCENT',
                tagline: 'Serious solo / small team',
                price: '₹3,500',
                description: 'Guided weekly moves for one brand',
                features: [
                  'Up to 3 cohorts (ICPs)',
                  'Up to 3 active moves',
                  'Standard Muse usage',
                  'Basic Matrix analytics',
                  '1 user seat',
                  'Email support'
                ],
                highlight: false
              },
              {
                name: 'GLIDE',
                tagline: 'Growing team, multiple plays',
                price: '₹7,000',
                description: 'Run multiple plays, see what works',
                features: [
                  'Up to 6 cohorts',
                  'Up to 5 active moves',
                  'Higher Muse limits + priority',
                  'Deep Matrix analytics',
                  '3-5 user seats',
                  'Priority support',
                  'Cohort comparisons',
                  'Timing insights'
                ],
                highlight: true
              },
              {
                name: 'SOAR',
                tagline: 'Agency / full command center',
                price: '₹10,000',
                description: 'Full matrix, war room, ops guardrails',
                features: [
                  'Up to 9+ cohorts',
                  '10-12+ active moves',
                  'Highest Muse limits + fast lane',
                  'Full Matrix analytics',
                  '5-10+ user seats',
                  'Multi-workspace support',
                  'Advanced guards & sentinel',
                  'Brand constitutions',
                  'Anomaly alerts',
                  'Priority onboarding'
                ],
                highlight: false
              }
            ].map((tier, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15, type: 'spring', stiffness: 100 }}
                whileHover={{ y: -10, scale: 1.02 }}
                className={`relative border-2 p-8 transition-all duration-300 ${tier.highlight
                  ? 'border-black bg-black text-white shadow-[0_20px_60px_rgba(0,0,0,0.2)]'
                  : 'border-black/10 bg-cream hover:border-black/30 hover:shadow-[0_20px_60px_rgba(0,0,0,0.1)]'
                  }`}
              >
                {tier.highlight && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute -top-4 left-8 bg-white px-4 py-1 text-xs font-mono uppercase tracking-widest text-black"
                  >
                    Most Popular
                  </motion.div>
                )}

                <div className="mb-8">
                  <motion.p
                    className={`mb-2 text-xs font-mono uppercase tracking-widest ${tier.highlight ? 'text-white/60' : 'text-gray-500'}`}
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.15 + 0.1 }}
                  >
                    {tier.name}
                  </motion.p>
                  <motion.div
                    className="mb-4 flex items-baseline gap-2"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.15 + 0.2 }}
                  >
                    <span className="font-serif text-6xl font-black tracking-tight">
                      <AnimatedCounter end={parseInt(tier.price.replace(/[₹,]/g, ''))} prefix="₹" />
                    </span>
                    <span className={tier.highlight ? 'text-white/60' : 'text-gray-600'}>/month</span>
                  </motion.div>
                  <p className={`text-sm ${tier.highlight ? 'text-white/80' : 'text-gray-700'}`}>{tier.tagline}</p>
                  <p className={`mt-2 font-serif text-lg italic ${tier.highlight ? 'text-white/90' : 'text-gray-800'}`}>
                    "{tier.description}"
                  </p>
                </div>

                <ul className="mb-8 space-y-3">
                  {tier.features.map((feature, j) => (
                    <motion.li
                      key={j}
                      className="flex items-center gap-3"
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.15 + 0.3 + j * 0.03 }}
                      whileHover={{ x: 5 }}
                    >
                      <Check className="h-5 w-5 flex-shrink-0" strokeWidth={2} />
                      <span className="text-sm">{feature}</span>
                    </motion.li>
                  ))}
                </ul>

                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Link
                    to="/register"
                    className={`block w-full py-3 text-center text-sm font-medium uppercase tracking-wide transition-all duration-200 ${tier.highlight
                      ? 'bg-white text-black hover:bg-gray-100'
                      : 'border-2 border-black bg-black text-white hover:bg-gray-900'
                      }`}
                  >
                    Start with {tier.name}
                  </Link>
                </motion.div>
              </motion.div>
            ))}
          </div>

          <motion.p
            className="mt-12 text-center text-sm text-gray-600"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6 }}
          >
            Annual plans: 2 months free • Monthly billing • Cancel anytime
          </motion.p>
        </div>
      </section>

      {/* FAQ */}
      <section className="border-b border-black/5 bg-cream py-32">
        <div className="mx-auto max-w-4xl px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20"
          >
            <p className="text-micro mb-4">FAQ</p>
            <h2 className="font-serif text-6xl font-black tracking-tight">
              Straight Answers
            </h2>
          </motion.div>

          <div className="space-y-4">
            {[
              {
                q: 'Is this another content calendar?',
                a: 'No. We start with cohorts and postures, then map moves to daily actions. The calendar is an output, not the product.'
              },
              {
                q: 'How long to get value?',
                a: 'Most teams see clarity after the first sprint (one week). The intake takes under an hour, including cohorts.'
              },
              {
                q: 'Who is it for?',
                a: 'Solo founders, lean teams, and agencies who want fewer tasks with higher signal. If you hate guru theatrics, you will like this.'
              },
              {
                q: 'Do you lock me in?',
                a: 'No. Monthly billing. Export everything at any time. Your data is yours.'
              },
              {
                q: 'What makes RaptorFlow different?',
                a: 'We enforce constraints: 3-7 cohorts, 1-3 moves per week, 3 actions per day. Constraints create clarity. Most tools let you do everything, which means you finish nothing.'
              },
              {
                q: 'Can I use this with my existing tools?',
                a: 'Yes. RaptorFlow is your strategy layer. Export briefs to Notion, actions to Asana, or recaps to Slack. We play nice with others.'
              },
              {
                q: 'What about AI features?',
                a: 'AI helps with tone consistency (Sentinel), cohort suggestions, and move prioritization. But you stay in control. No auto-posting, no black boxes.'
              },
              {
                q: 'What\'s the difference between tiers?',
                a: 'Ascent is for one brand, Glide for multiple plays, Soar for agencies/multi-brand. Each tier unlocks more cohorts, moves, analytics depth, and team seats.'
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06 }}
                whileHover={{ x: 5, scale: 1.01 }}
                className="border border-black/10 bg-white p-6 transition-all duration-300 hover:border-black/30 hover:shadow-[0_8px_24px_rgba(0,0,0,0.06)]"
              >
                <h3 className="mb-3 font-serif text-xl font-bold">{item.q}</h3>
                <p className="leading-relaxed text-gray-700">{item.a}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Indicators */}
      <section className="border-b border-black/5 bg-white py-32 relative overflow-hidden">
        {/* Subtle animated grid background */}
        <motion.div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(to right, black 1px, transparent 1px),
                            linear-gradient(to bottom, black 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
          animate={{
            backgroundPosition: ['0px 0px', '60px 60px'],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        />

        <div className="mx-auto max-w-7xl px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-16 text-center"
          >
            <motion.p
              className="text-micro mb-4"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
            >
              Built on Trust
            </motion.p>
            <h2 className="font-serif text-5xl font-black tracking-tight">
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="inline-block"
              >
                Your Data, Your Control
              </motion.span>
            </h2>
          </motion.div>

          <div className="grid gap-12 md:grid-cols-3">
            {[
              {
                icon: Lock,
                title: 'Privacy First',
                desc: 'Your data stays yours. We store in Supabase. No public feeds, no surprise sharing.',
                animationType: 'lock'
              },
              {
                icon: Mail,
                title: 'Human Support',
                desc: 'Real people, not bots. Response inside business hours. support@raptorflow.in',
                animationType: 'mail'
              },
              {
                icon: Download,
                title: 'Export Everything',
                desc: 'PDF, Markdown, JSON. Your data is portable. Leave anytime with everything intact.',
                animationType: 'download'
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50, rotateX: -20 }}
                whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15, type: 'spring', stiffness: 80 }}
                whileHover={{
                  y: -12,
                  transition: { duration: 0.3, type: 'spring', stiffness: 300 }
                }}
                className="group text-center relative"
                style={{ transformStyle: 'preserve-3d' }}
              >
                {/* Subtle glow on hover */}
                <motion.div
                  className="absolute inset-0 bg-black/[0.02] opacity-0 group-hover:opacity-100 blur-3xl transition-opacity duration-500 rounded-3xl"
                />

                <div className="relative">
                  {/* Icon container with complex animations */}
                  <motion.div
                    className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-2xl border-2 border-black bg-black shadow-lg relative overflow-hidden"
                    whileHover={{
                      scale: 1.1,
                      rotate: [0, -5, 5, -5, 0],
                      transition: { duration: 0.5 }
                    }}
                  >
                    {/* Shimmer effect */}
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                      animate={{
                        x: ['-200%', '200%'],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        repeatDelay: 2,
                        ease: 'easeInOut'
                      }}
                    />

                    {/* Lock Animation - Pulsing */}
                    {item.animationType === 'lock' && (
                      <motion.div
                        animate={{
                          scale: [1, 1.1, 1],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          repeatDelay: 1
                        }}
                      >
                        <item.icon className="h-12 w-12 text-white relative z-10" strokeWidth={2} />
                      </motion.div>
                    )}

                    {/* Mail Animation - Envelope opening */}
                    {item.animationType === 'mail' && (
                      <motion.div
                        animate={{
                          rotateX: [0, -15, 0],
                          y: [0, -2, 0]
                        }}
                        transition={{
                          duration: 2.5,
                          repeat: Infinity,
                          repeatDelay: 1.5
                        }}
                      >
                        <item.icon className="h-12 w-12 text-white relative z-10" strokeWidth={2} />
                      </motion.div>
                    )}

                    {/* Download Animation - Arrow moving down with progress */}
                    {item.animationType === 'download' && (
                      <div className="relative">
                        <motion.div
                          animate={{
                            y: [0, 8, 0],
                          }}
                          transition={{
                            duration: 1.5,
                            repeat: Infinity,
                            ease: 'easeInOut'
                          }}
                        >
                          <item.icon className="h-12 w-12 text-white relative z-10" strokeWidth={2} />
                        </motion.div>

                        {/* Download progress line */}
                        <motion.div
                          className="absolute bottom-2 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-white/30 rounded-full overflow-hidden"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: [0, 1, 1, 0] }}
                          transition={{
                            duration: 1.5,
                            repeat: Infinity,
                            times: [0, 0.2, 0.8, 1]
                          }}
                        >
                          <motion.div
                            className="h-full bg-white rounded-full"
                            animate={{
                              width: ['0%', '100%'],
                            }}
                            transition={{
                              duration: 1.5,
                              repeat: Infinity,
                              ease: 'easeInOut'
                            }}
                          />
                        </motion.div>
                      </div>
                    )}

                    {/* Rotating ring decoration */}
                    <motion.div
                      className="absolute inset-0 border-2 border-white/10 rounded-2xl"
                      animate={{
                        rotate: 360,
                        scale: [1, 1.05, 1]
                      }}
                      transition={{
                        rotate: { duration: 8, repeat: Infinity, ease: 'linear' },
                        scale: { duration: 2, repeat: Infinity }
                      }}
                    />
                  </motion.div>

                  {/* Title */}
                  <motion.h3
                    className="mb-3 font-serif text-2xl font-bold transition-all duration-300"
                    whileHover={{
                      scale: 1.05,
                      transition: { duration: 0.2 }
                    }}
                  >
                    {item.title}
                  </motion.h3>

                  {/* Animated underline */}
                  <motion.div
                    className="mx-auto mb-4 h-0.5 bg-black rounded-full"
                    initial={{ width: 0 }}
                    whileInView={{ width: 60 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.15 + 0.3, duration: 0.6 }}
                  />

                  <motion.p
                    className="text-gray-700 leading-relaxed px-4"
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.15 + 0.4 }}
                  >
                    {item.desc}
                  </motion.p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA with maximum impact */}
      <section className="bg-black py-32 text-white relative overflow-hidden">
        {/* Animated background elements */}
        <motion.div
          className="absolute top-0 left-0 h-full w-full opacity-10"
          style={{
            backgroundImage: `radial-gradient(circle at 20% 50%, white 1px, transparent 1px)`,
            backgroundSize: '50px 50px'
          }}
          animate={{
            backgroundPosition: ['0px 0px', '50px 50px'],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
        />

        <div className="mx-auto max-w-5xl px-6 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, type: 'spring' }}
          >
            <motion.p
              className="text-micro mb-6 text-white/60"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              Ready
            </motion.p>
            <motion.h2
              className="mb-8 font-serif text-7xl font-black leading-tight tracking-tight md:text-8xl"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              Transform Your
              <br />
              <motion.span
                className="inline-block"
                animate={{
                  textShadow: [
                    '0 0 20px rgba(255,255,255,0)',
                    '0 0 20px rgba(255,255,255,0.3)',
                    '0 0 20px rgba(255,255,255,0)'
                  ]
                }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                Marketing Today
              </motion.span>
            </motion.h2>
            <motion.p
              className="mb-12 text-xl text-white/80"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              Join hundreds of teams who've ditched the chaos for clarity.
              <br />
              Get started in minutes. No complexity.
            </motion.p>
            <motion.div
              className="flex flex-wrap items-center justify-center gap-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              <motion.div
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link to="/register" className="group inline-flex items-center justify-center gap-2 bg-white px-8 py-4 text-base font-medium uppercase tracking-wide text-black transition-all duration-200">
                  Get Started Now
                  <motion.div
                    animate={{ x: [0, 3, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <ArrowRight className="h-5 w-5" />
                  </motion.div>
                </Link>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link to="/login" className="inline-flex items-center justify-center gap-2 border border-white/30 px-8 py-4 text-base font-medium uppercase tracking-wide text-white transition-all duration-200 hover:bg-white/10">
                  Sign In
                </Link>
              </motion.div>
            </motion.div>
            <motion.p
              className="mt-8 text-sm text-white/60"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
            >
              <CheckCircle2 className="mr-2 inline h-4 w-4" />
              Monthly billing • Cancel anytime • No surprises
            </motion.p>
          </motion.div>
        </div>

        {/* Floating elements */}
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute h-1 w-1 rounded-full bg-white/20"
            style={{
              left: `${10 + i * 12}%`,
              top: `${20 + (i % 3) * 25}%`,
            }}
            animate={{
              y: [0, -20, 0],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: 3 + i * 0.5,
              repeat: Infinity,
              delay: i * 0.3,
            }}
          />
        ))}
      </section>

      {/* Footer with fade-in */}
      <motion.footer
        className="border-t border-black/10 bg-white py-12"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
            <div className="flex items-center gap-3">
              <motion.div
                className="flex h-10 w-10 items-center justify-center rounded-lg border-2 border-black bg-black"
                whileHover={{ scale: 1.1, rotate: 6 }}
              >
                <Rocket className="h-5 w-5 text-white" strokeWidth={2.5} />
              </motion.div>
              <span className="font-serif text-xl font-black">RaptorFlow</span>
            </div>
            <div className="flex gap-8 text-sm uppercase tracking-wider text-gray-600">
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0 }}
              >
                <Link
                  to="/privacy"
                  className="transition-colors hover:text-black"
                >
                  Privacy
                </Link>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 }}
              >
                <Link
                  to="/terms"
                  className="transition-colors hover:text-black"
                >
                  Terms
                </Link>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 }}
              >
                <a
                  href="mailto:support@raptorflow.in"
                  className="transition-colors hover:text-black"
                >
                  Support
                </a>
              </motion.div>
            </div>
          </div>
          <motion.div
            className="mt-8 text-center text-sm text-gray-500"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
          >
            © 2025 RaptorFlow. Marketing clarity, delivered.
          </motion.div>
        </div>
      </motion.footer>
    </div>
  )
}
