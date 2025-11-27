import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Check,
  Menu,
  X,
  Rocket,
  Target,
  Brain,
  Zap,
  Shield,
  BarChart3,
  Layers,
  Lock,
  Mail,
  Download,
  CheckCircle2,
  ChevronDown,
  Minus,
  Plus,
  Users,
  TrendingUp,
  FileText,
  BookOpen,
  Map,
  ClipboardList,
  AlertCircle,
  Star,
  Circle,
  Globe,
  Activity,
  Award,
  DollarSign,
  Calendar
} from 'lucide-react'
import FluidHero from '../components/art/FluidHero'
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

// ============================================================================
// MAIN LANDING COMPONENT
// ============================================================================
export default function Landing() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const heroRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [0, 150])
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 1], [1, 0.95])

  const springConfig = { stiffness: 100, damping: 30, restDelta: 0.001 }
  const ySpring = useSpring(y, springConfig)

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <div className="min-h-screen bg-cream text-ink overflow-hidden">
      {/* ====================================================================== */}
      {/* STICKY NAVIGATION */}
      {/* ====================================================================== */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="sticky top-0 z-50 border-b border-black/10 bg-white/95 backdrop-blur-xl"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/landing" className="group flex items-center gap-3">
              <motion.div
                whileHover={{ scale: 1.1, rotate: 6 }}
                whileTap={{ scale: 0.95 }}
                className="relative flex h-10 w-10 items-center justify-center rounded-lg border-2 border-black bg-black transition-all duration-300 overflow-hidden"
              >
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
                <motion.div
                  animate={{ y: [0, -2, 0] }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                >
                  <Rocket className="h-5 w-5 text-white relative z-10" strokeWidth={2.5} />
                </motion.div>
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

      {/* ====================================================================== */}
      {/* HERO SECTION - ARTISTIC OVERHAUL */}
      {/* ====================================================================== */}
      <section ref={heroRef} className="relative min-h-screen overflow-hidden bg-white flex items-center">
        {/* FLUID ART BACKGROUND */}
        <FluidHero />

        {/* CONTENT OVERLAY */}
        <motion.div
          style={{ y: ySpring, opacity, scale }}
          className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 w-full"
        >
          <div className="max-w-6xl">
            {/* Badge - Minimal & Sharp */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              className="mb-12 inline-flex items-center gap-3 border-l-4 border-black pl-6"
            >
              <span className="text-xs font-mono uppercase tracking-[0.4em] text-black mix-blend-difference">
                The Art of Strategy
              </span>
            </motion.div>

            {/* Main Headline - KINETIC TYPOGRAPHY */}
            <h1 className="mb-16 font-serif font-black leading-[0.85] tracking-tighter mix-blend-exclusion text-black"
              style={{ fontSize: 'clamp(5rem, 18vw, 18rem)' }}>
              <motion.div
                initial={{ y: 100, opacity: 0, rotateX: -45 }}
                animate={{ y: 0, opacity: 1, rotateX: 0 }}
                transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                className="origin-bottom"
              >
                Marketing
              </motion.div>
              <motion.div
                initial={{ y: 100, opacity: 0, rotateX: -45 }}
                animate={{ y: 0, opacity: 1, rotateX: 0 }}
                transition={{ duration: 1.2, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
                className="origin-bottom text-transparent bg-clip-text bg-gradient-to-r from-black via-gray-500 to-black bg-[length:200%_auto] animate-gradient"
              >
                As
              </motion.div>
              <motion.div
                initial={{ y: 100, opacity: 0, rotateX: -45 }}
                animate={{ y: 0, opacity: 1, rotateX: 0 }}
                transition={{ duration: 1.2, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
                className="origin-bottom"
              >
                Mastery
              </motion.div>
            </h1>

            {/* Subheadline - Editorial Style */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.8 }}
              className="mb-20 max-w-xl border-t-2 border-black pt-8"
            >
              <p className="text-lg font-light leading-relaxed text-black/80">
                Chaos is a choice. Order is a discipline. RaptorFlow transforms the noise of daily operations into a masterpiece of strategic clarity.
              </p>
            </motion.div>

            {/* CTA Buttons - Avant-Garde */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1 }}
              className="flex flex-col sm:flex-row items-start gap-8"
            >
              <Link
                to="/register"
                className="group relative overflow-hidden bg-black px-12 py-6 text-white transition-all hover:scale-105"
              >
                <div className="absolute inset-0 bg-white/20 translate-y-full transition-transform duration-500 group-hover:translate-y-0" />
                <span className="relative z-10 flex items-center gap-4 text-sm font-bold uppercase tracking-[0.2em]">
                  Begin The Work
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Link>

              <Link
                to="/strategy/wizard"
                className="group flex items-center gap-4 px-4 py-6 text-sm font-bold uppercase tracking-[0.2em] text-black transition-colors hover:text-black/60"
              >
                <span>Explore The System</span>
                <div className="h-[2px] w-12 bg-black transition-all group-hover:w-20" />
              </Link>
            </motion.div>

            {/* Stats - Abstract Representation */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.4, ease: "easeOut" }}
              className="grid grid-cols-3 gap-12 border-t-2 border-black pt-16"
            >
              {[
                { value: 40, suffix: '%', label: 'Less Busywork' },
                { value: 3, suffix: 'x', label: 'Faster' },
                { value: 100, suffix: '%', label: 'Clarity' }
              ].map((stat, i) => (
                <div key={i}>
                  <div className="mb-3 font-serif font-black tracking-tighter leading-none" style={{ fontSize: 'clamp(4rem, 8vw, 12rem)' }}>
                    <AnimatedCounter end={stat.value} suffix={stat.suffix} />
                  </div>
                  <div className="text-sm font-bold uppercase tracking-[0.3em] text-black">
                    {stat.label}
                  </div>
                </div>
              ))}
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* ====================================================================== */}
      {/* WHY NOW SECTION - EXTREME MINIMAL */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-white py-32 sm:py-40 relative overflow-hidden">
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

        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
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
            <h2 className="mb-8 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Most Marketing Tools
              <br />
              Let You Do Everything
            </h2>
            <motion.p
              className="text-sm text-black font-light leading-relaxed max-w-2xl mx-auto"
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

      {/* ====================================================================== */}
      {/* NOT ANOTHER POST EVERY DAY TOOL */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-gray-100 py-32 sm:py-40 relative overflow-hidden">
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

        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-12 sm:mb-20 text-center"
          >
            <motion.p
              className="text-micro mb-4"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              A Different Approach
            </motion.p>
            <h2 className="mb-8 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              This is not another
              <br />
              "post every day" tool
            </h2>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-2 max-w-6xl mx-auto">
            {/* The Usual Marketing Advice */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative border-2 border-black bg-white p-8 sm:p-10"
            >
              <div className="mb-6">
                <motion.div
                  className="inline-flex items-center gap-2 mb-4"
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                >
                  <X className="h-6 w-6 text-black" strokeWidth={3} />
                  <span className="text-micro text-gray-500">The usual marketing advice</span>
                </motion.div>
                <h3 className="font-serif text-2xl sm:text-3xl font-black tracking-tight mb-6">
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
                    <span className="text-sm leading-relaxed">{item}</span>
                  </motion.li>
                ))}
              </ul>
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
              className="relative border-2 border-black bg-black p-6 sm:p-8 text-white"
            >
              <div className="mb-6">
                <motion.div
                  className="inline-flex items-center gap-2 mb-4"
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                >
                  <Check className="h-6 w-6 text-black" strokeWidth={3} />
                  <span className="text-micro text-white/60">What RaptorFlow cares about instead</span>
                </motion.div>
                <h3 className="font-serif text-2xl sm:text-3xl font-black tracking-tight mb-6">
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
                    <span className="text-sm leading-relaxed text-white/90">{item}</span>
                  </motion.li>
                ))}
              </ul>

              <motion.div
                className="pt-6 border-t border-white/10"
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 }}
              >
                <p className="text-lg sm:text-xl font-bold text-white">
                  No gurus. No fake urgency.
                  <br />
                  <span className="text-white/70">Just a clearer brain for your marketing.</span>
                </p>
              </motion.div>

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

      {/* ====================================================================== */}
      {/* YOUR BUYERS AS COHORTS */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-white py-32 sm:py-40 relative overflow-hidden">
        <motion.div
          className="absolute top-20 right-10 h-96 w-96 rounded-full bg-black/[0.02] blur-3xl hidden lg:block"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 12, repeat: Infinity }}
        />

        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-16 sm:mb-24 text-center"
          >
            <p className="text-micro mb-6">Core Concept</p>
            <h2 className="mb-8 font-serif font-black tracking-tighter leading-[0.9] max-w-4xl mx-auto" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Your Buyers
              <br />
              as Cohorts
            </h2>
            <motion.p
              className="max-w-2xl mx-auto text-sm text-black font-light leading-relaxed px-4"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              Instead of vague "target audiences," RaptorFlow helps you create{' '}
              <span className="font-bold text-black">ICP cohorts</span>—detailed profiles of real people you're trying to reach.
            </motion.p>
          </motion.div>

          {/* Visual Before/After Comparison */}
          <div className="grid gap-8 sm:gap-12 md:grid-cols-2 mb-12 sm:mb-20">
            {/* Before */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative"
            >
              <div className="mb-6 flex items-center gap-3">
                <X className="h-6 w-6 text-black" strokeWidth={3} />
                <span className="text-sm font-bold uppercase tracking-wider text-gray-500">
                  How most people market
                </span>
              </div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                className="border-2 border-black/10 bg-white p-6 sm:p-8 relative min-h-[400px] flex flex-col"
              >
                <div className="mb-6">
                  <h3 className="font-serif text-2xl sm:text-3xl font-black mb-3 text-gray-400">
                    Target Audience
                  </h3>
                  <div className="h-1 w-16 bg-gray-300 rounded-full" />
                </div>

                <div className="space-y-6 text-gray-500 flex-1">
                  <p className="text-xl sm:text-2xl font-bold">
                    "Small business owners"
                  </p>
                  <div className="space-y-3 text-base sm:text-lg opacity-60">
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

            {/* After - Cohort Rotator */}
            <CohortRotator />
          </div>

          {/* Three Key Elements - MINIMAL */}
          <div className="grid gap-6 sm:gap-10 md:grid-cols-3 mb-12 sm:mb-16">
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
                transition={{ delay: i * 0.1, ease: "easeOut", duration: 0.4 }}
                className="border-2 border-black bg-white p-8 hover:bg-black hover:text-white transition-all duration-300 group"
              >
                <div className="flex h-12 w-12 items-center justify-center border-2 border-black bg-white group-hover:bg-white group-hover:border-white mb-6 transition-colors">
                  <item.icon className="h-6 w-6 text-black" strokeWidth={2} />
                </div>
                <h3 className="font-serif text-2xl font-black mb-4">{item.title}</h3>
                <p className="text-sm leading-relaxed opacity-80">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          {/* Bottom CTA */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="border-2 border-black bg-black p-12 sm:p-16 text-white"
          >
            <div className="max-w-4xl">
              <h3 className="font-serif font-black mb-8 leading-[0.9] tracking-tighter" style={{ fontSize: 'clamp(3rem, 8vw, 8rem)' }}>
                Stop talking to "everyone"
              </h3>
              <p className="text-lg sm:text-xl text-white/80 leading-relaxed mb-10 max-w-2xl font-light">
                Use cohorts to guide every piece of content, every campaign, every decision. When you know exactly who you're talking to, marketing becomes clarity.
              </p>
              <Link
                to="/register"
                className="inline-flex items-center gap-3 border-2 border-white bg-white px-8 py-4 text-sm font-bold uppercase tracking-wider text-black transition-all duration-200 hover:bg-black hover:text-white hover:border-white"
              >
                Start talking to real people
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* WHAT YOU GET - RULE OF 3 */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-white py-32 sm:py-40 relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 sm:mb-32"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 border-l-2 border-black pl-4">What You Get</p>
            <h2 className="mb-8 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Everything You Need.
              <br />
              Nothing You Don't.
            </h2>
            <p className="text-sm text-black font-light max-w-xl leading-relaxed">
              Stop guessing and start shipping marketing that makes sense
            </p>
          </motion.div>

          <div className="grid gap-0 md:grid-cols-3 border-2 border-black">
            {[
              {
                number: '01',
                title: 'Define',
                subtitle: 'Your Real Buyers',
                desc: 'Cohort builder that captures who they are, what they struggle with, and how you help.',
                icon: Target,
                features: ['ICP cohorts', 'Microproofs', 'Real language']
              },
              {
                number: '02',
                title: 'Plan',
                subtitle: 'Strategic Moves',
                desc: 'Campaign planner that turns ideas into finishable work. 1-3 moves per week.',
                icon: Brain,
                features: ['Weekly moves', 'Daily actions', 'Brain dump tool']
              },
              {
                number: '03',
                title: 'Ship',
                subtitle: 'Track Progress',
                desc: 'See what\'s working without vanity metrics. Track posture mix and cadence streaks.',
                icon: TrendingUp,
                features: ['Real analytics', 'Tone guardian', 'Team sync']
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className={`group relative p-10 sm:p-12 transition-all duration-300 hover:bg-black hover:text-white ${i !== 2 ? 'border-b-2 md:border-b-0 md:border-r-2 border-black' : ''}`}
              >
                <div className="flex justify-between items-start mb-12">
                  <span className="font-mono text-xl font-bold opacity-30 group-hover:opacity-100 transition-opacity">
                    {item.number}
                  </span>
                  <item.icon className="h-8 w-8 opacity-100 group-hover:text-white transition-colors" strokeWidth={1.5} />
                </div>

                <h3 className="font-serif text-4xl font-black tracking-tighter mb-2">
                  {item.title}
                </h3>
                <p className="text-xs uppercase tracking-widest opacity-60 mb-8">{item.subtitle}</p>

                <p className="text-sm leading-relaxed opacity-80 mb-10 min-h-[60px]">
                  {item.desc}
                </p>

                <ul className="space-y-3 border-t-2 border-black/10 group-hover:border-white/20 pt-8">
                  {item.features.map((feature, j) => (
                    <li key={j} className="flex items-center gap-3 text-xs font-medium uppercase tracking-wider opacity-70">
                      <Check className="h-3 w-3" strokeWidth={3} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>

          {/* Bottom tagline */}
          <motion.div
            className="mt-12 sm:mt-16 text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
          >
            <p className="text-xl sm:text-2xl font-serif font-black text-gray-900">
              No templates. No gurus. No BS.
            </p>
          </motion.div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* BEFORE/AFTER COMPARISON */}
      {/* ====================================================================== */}
      {/* ====================================================================== */}
      {/* BEFORE/AFTER COMPARISON - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-gray-100 py-32 sm:py-40">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 sm:mb-32"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 border-l-2 border-black pl-4">The Difference</p>
            <h2 className="mb-6 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Chaos vs. Clarity
            </h2>
          </motion.div>

          <div className="grid gap-0 md:grid-cols-2 border-2 border-black bg-white">
            {/* Before */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="p-10 sm:p-16 border-b-2 md:border-b-0 md:border-r-2 border-black"
            >
              <div className="mb-10 flex items-center gap-4">
                <X className="h-8 w-8" strokeWidth={3} />
                <h3 className="font-serif text-3xl font-black">Without RaptorFlow</h3>
              </div>
              <ul className="space-y-6">
                {[
                  'Drowning in endless task lists',
                  'No clear audience definition',
                  'Random acts of marketing',
                  'Inconsistent brand voice',
                  'Can\'t measure what matters',
                  'Team always misaligned',
                  'Burnout from busywork'
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-4 text-gray-500">
                    <Minus className="mt-1 h-4 w-4 flex-shrink-0" strokeWidth={2} />
                    <span className="text-sm font-medium">{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>

            {/* After */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="p-10 sm:p-16 bg-black text-white"
            >
              <div className="mb-10 flex items-center gap-4">
                <Check className="h-8 w-8" strokeWidth={3} />
                <h3 className="font-serif text-3xl font-black">With RaptorFlow</h3>
              </div>
              <ul className="space-y-6">
                {[
                  '1-3 focused moves per week',
                  'Crystal-clear cohort definitions',
                  'Strategic, posture-aware execution',
                  'AI-powered tone consistency',
                  'Track only what drives growth',
                  'Real-time team alignment',
                  'Sustainable, calm workflow'
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-4">
                    <Check className="mt-1 h-4 w-4 flex-shrink-0" strokeWidth={2} />
                    <span className="text-sm font-medium">{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* FEATURES GRID */}
      {/* ====================================================================== */}



      {/* ====================================================================== */}
      {/* FEATURES GRID - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-white py-32 sm:py-40 relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 border-l-2 border-black pl-4">System</p>
            <h2 className="mb-8 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Complete Marketing OS
            </h2>
            <p className="max-w-2xl text-sm text-black font-light leading-relaxed">
              Every tool you need to plan, execute, and track marketing that actually works.
            </p>
          </motion.div>

          <div className="grid gap-0 md:grid-cols-2 lg:grid-cols-3 border-2 border-black">
            {[
              { icon: Target, title: 'Smart Cohorts', description: 'Define rare audiences with microproofs, objections, and language your buyers actually use.', metric: '3-7 cohorts' },
              { icon: Brain, title: 'Strategic Moves', description: 'Plan operations with posture-aware pacing. Offensive when hot, defensive when protecting altitude.', metric: '1-3 weekly moves' },
              { icon: Zap, title: 'Daily Actions', description: 'Execute with focus. Time-boxed tasks that actually move the needle, not busywork.', metric: '3 actions/day' },
              { icon: Shield, title: 'Tone Guardian', description: 'AI sentinel that flags drift, fatigue, and cadence gaps without adding another inbox.', metric: '0 tone leaks' },
              { icon: BarChart3, title: 'Real Analytics', description: 'Track what matters. Posture mix, cadence streaks, and alert count. No vanity metrics.', metric: 'Signal only' },
              { icon: Layers, title: 'Team Sync', description: 'Keep everyone aligned with clear ownership, binary status, and exportable recaps.', metric: 'One source' }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                className={`group relative p-8 sm:p-10 transition-all duration-300 hover:bg-black hover:text-white border-b-2 border-r-2 border-black ${i % 3 === 2 ? 'lg:border-r-0' : ''} ${i >= 3 ? 'border-b-0' : ''}`}
              >
                <div className="relative">
                  <div className="mb-8 flex items-start justify-between">
                    <div className="flex h-12 w-12 items-center justify-center border-2 border-black bg-white group-hover:border-white transition-colors">
                      <feature.icon className="h-6 w-6 text-black" strokeWidth={2} />
                    </div>
                    <span className="text-xs font-mono uppercase tracking-widest opacity-60">{feature.metric}</span>
                  </div>
                  <h3 className="mb-4 font-serif text-2xl font-bold tracking-tight">{feature.title}</h3>
                  <p className="leading-relaxed text-sm opacity-80">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* WEEKLY CADENCE TIMELINE */}
      {/* ====================================================================== */}
      {/* ====================================================================== */}
      {/* WEEKLY CADENCE TIMELINE - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-gray-100 py-32 sm:py-40 relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 sm:mb-32"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 border-l-2 border-black pl-4">Weekly Rhythm</p>
            <h2 className="mb-8 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Seven Days of
              <br />
              Calm Execution
            </h2>
            <p className="max-w-2xl text-sm text-black font-light leading-relaxed">
              A proven weekly cadence that turns marketing chaos into a sustainable, finishable system.
            </p>
          </motion.div>

          <div className="space-y-0 border-l-2 border-black ml-4 sm:ml-8">
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
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="group relative pl-8 sm:pl-12 py-8 sm:py-10 border-b border-black/10 last:border-b-0 hover:bg-white transition-colors duration-300"
              >
                <div className="absolute left-[-5px] top-10 h-2 w-2 bg-black rounded-full group-hover:scale-150 transition-transform duration-300" />

                <div className="flex flex-col sm:flex-row items-baseline gap-4 sm:gap-8">
                  <span className="font-mono text-4xl font-black opacity-20 group-hover:opacity-100 transition-opacity duration-300">
                    {item.num}
                  </span>

                  <div className="flex-1">
                    <div className="flex flex-col sm:flex-row sm:items-baseline gap-2 sm:gap-4 mb-2">
                      <h3 className="font-serif text-3xl font-black tracking-tight group-hover:translate-x-2 transition-transform duration-300">
                        {item.day}
                      </h3>
                      <span className="text-xs font-mono uppercase tracking-widest opacity-60">{item.label}</span>
                    </div>

                    <p className="text-sm text-gray-600 leading-relaxed max-w-2xl group-hover:text-black transition-colors">
                      {item.desc}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* DELIVERABLES */}
      {/* ====================================================================== */}
      {/* ====================================================================== */}
      {/* DELIVERABLES - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-white py-32 sm:py-40">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 sm:mb-32"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 border-l-2 border-black pl-4">Outputs</p>
            <h2 className="mb-6 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              What Leaves
              <br />
              The Room
            </h2>
          </motion.div>

          <div className="grid gap-0 md:grid-cols-3 border-2 border-black">
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
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className={`group p-10 sm:p-12 transition-all duration-300 hover:bg-black hover:text-white ${i !== 2 ? 'border-b-2 md:border-b-0 md:border-r-2 border-black' : ''}`}
              >
                <div className="mb-8 flex h-12 w-12 items-center justify-center border-2 border-black bg-white group-hover:border-white transition-colors">
                  <item.icon className="h-6 w-6 text-black group-hover:text-black" strokeWidth={2} />
                </div>
                <h3 className="mb-4 font-serif text-2xl font-bold tracking-tight">
                  {item.title}
                </h3>
                <p className="mb-8 leading-relaxed text-sm opacity-80">
                  {item.desc}
                </p>
                <ul className="space-y-3 border-t-2 border-black/10 group-hover:border-white/20 pt-6">
                  {item.features.map((feature, j) => (
                    <li key={j} className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider opacity-70">
                      <Check className="h-3 w-3" strokeWidth={3} />
                      {feature}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* USE CASES */}
      {/* ====================================================================== */}
      {/* ====================================================================== */}
      {/* USE CASES - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-gray-100 py-32 sm:py-40 relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 sm:mb-32"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 border-l-2 border-black pl-4">Perfect For</p>
            <h2 className="mb-6 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Your Team,
              <br />
              Your Way
            </h2>
            <p className="text-sm text-black font-light max-w-xl leading-relaxed">
              Whether you're flying solo or leading a team, RaptorFlow adapts to your workflow
            </p>
          </motion.div>

          <div className="grid gap-0 md:grid-cols-2 border-2 border-black bg-white">
            {[
              {
                title: 'Solo Founders',
                icon: Users,
                tagline: 'You wear all the hats. RaptorFlow gives you a marketing system that doesn\'t require a team.',
                benefits: ['Quick setup (< 1 hour)', 'No learning curve', 'Scales with you'],
              },
              {
                title: 'Lean Marketing Teams',
                icon: Shield,
                tagline: 'Small team, big ambitions. Stay aligned without endless meetings and status updates.',
                benefits: ['Clear ownership', 'Async-friendly', 'No tool sprawl'],
              },
              {
                title: 'Agencies',
                icon: Rocket,
                tagline: 'Manage multiple clients with consistent quality. Export briefs and recaps in seconds.',
                benefits: ['Client-ready exports', 'Template library', 'White-label ready'],
              },
              {
                title: 'Product Teams',
                icon: Brain,
                tagline: 'Launch features with clarity. Define cohorts, plan moves, track what resonates.',
                benefits: ['Launch playbooks', 'Feature adoption', 'User feedback loops'],
              }
            ].map((useCase, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className={`group relative p-10 sm:p-12 transition-all duration-300 hover:bg-black hover:text-white border-b-2 border-black ${i % 2 === 0 ? 'md:border-r-2' : ''} ${i >= 2 ? 'md:border-b-0' : ''}`}
              >
                <div className="flex items-center gap-6 mb-8">
                  <div className="flex h-12 w-12 items-center justify-center border-2 border-black bg-white group-hover:border-white transition-colors">
                    <useCase.icon className="h-6 w-6 text-black" strokeWidth={2} />
                  </div>
                  <h3 className="font-serif text-3xl font-black tracking-tight">
                    {useCase.title}
                  </h3>
                </div>

                <p className="mb-8 text-sm leading-relaxed opacity-80 font-medium">
                  {useCase.tagline}
                </p>

                <ul className="space-y-3">
                  {useCase.benefits.map((benefit, j) => (
                    <li key={j} className="flex items-center gap-3 text-xs font-medium uppercase tracking-wider opacity-70">
                      <Check className="h-3 w-3" strokeWidth={3} />
                      <span>{benefit}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* PRICING - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-white py-32 sm:py-40 relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 sm:mb-32"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 border-l-2 border-black pl-4">Pricing</p>
            <h2 className="mb-8 font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Simple, Honest
              <br />
              Pricing
            </h2>
            <p className="text-sm text-black font-light max-w-xl leading-relaxed">
              Choose your altitude. Scale as you grow.
            </p>
          </motion.div>

          <div className="grid gap-0 lg:grid-cols-3 border-2 border-black">
            {[
              {
                name: 'ASCENT',
                tagline: 'Serious solo / small team',
                price: 3500,
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
                price: 7000,
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
                price: 10000,
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
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className={`relative p-10 sm:p-12 transition-all duration-300 hover:bg-black hover:text-white border-b-2 lg:border-b-0 lg:border-r-2 border-black ${i === 2 ? 'lg:border-r-0' : ''} group`}
              >
                {tier.highlight && (
                  <div className="absolute top-0 right-0 bg-black text-white px-4 py-1 text-xs font-mono uppercase tracking-widest group-hover:bg-white group-hover:text-black transition-colors">
                    Most Popular
                  </div>
                )}

                <div className="mb-10">
                  <p className="mb-4 text-xs font-mono uppercase tracking-widest opacity-60">
                    {tier.name}
                  </p>
                  <div className="mb-6 flex items-baseline gap-2">
                    <span className="font-serif text-5xl sm:text-6xl font-black tracking-tighter">
                      <AnimatedCounter end={tier.price} prefix="₹" />
                    </span>
                    <span className="text-sm opacity-60">/month</span>
                  </div>
                  <p className="text-sm font-medium mb-2">
                    {tier.tagline}
                  </p>
                  <p className="text-sm opacity-70 italic">
                    "{tier.description}"
                  </p>
                </div>

                <ul className="mb-10 space-y-3">
                  {tier.features.map((feature, j) => (
                    <li key={j} className="flex items-center gap-3 text-xs font-medium uppercase tracking-wider opacity-70">
                      <Check className="h-3 w-3" strokeWidth={3} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  to="/register"
                  className="block w-full py-4 text-center text-xs font-bold uppercase tracking-widest border-2 border-black bg-white text-black hover:bg-black hover:text-white hover:border-white transition-all duration-300 group-hover:border-white group-hover:bg-white group-hover:text-black"
                >
                  Start with {tier.name}
                </Link>
              </motion.div>
            ))}
          </div>

          <p className="mt-12 text-center text-xs font-mono uppercase tracking-widest opacity-60">
            Annual plans: 2 months free • Monthly billing • Cancel anytime
          </p>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* FAQ */}
      {/* ====================================================================== */}
      {/* ====================================================================== */}
      {/* FAQ - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-gray-100 py-32 sm:py-40">
        <div className="mx-auto max-w-4xl px-4 sm:px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 sm:mb-32"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 border-l-2 border-black pl-4">FAQ</p>
            <h2 className="font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 10vw, 10rem)' }}>
              Straight Answers
            </h2>
          </motion.div>

          <div className="space-y-0 border-t-2 border-black">
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
              <div key={i} className="border-b-2 border-black py-8 group hover:bg-white transition-colors duration-300 px-4">
                <h3 className="font-serif text-2xl font-bold mb-4">{item.q}</h3>
                <p className="text-sm leading-relaxed opacity-80 max-w-2xl">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* TRUST INDICATORS */}
      {/* ====================================================================== */}
      {/* ====================================================================== */}
      {/* TRUST INDICATORS - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="border-b-2 border-black bg-white py-32 sm:py-40 relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-20 sm:mb-32 text-center"
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8">Built on Trust</p>
            <h2 className="font-serif font-black tracking-tighter leading-[0.9]" style={{ fontSize: 'clamp(3rem, 8vw, 8rem)' }}>
              Your Data,
              <br />
              Your Control
            </h2>
          </motion.div>

          <div className="grid gap-12 sm:gap-16 md:grid-cols-3 text-center">
            {[
              {
                icon: Lock,
                title: 'Privacy First',
                desc: 'Your data stays yours. We store in Supabase. No public feeds, no surprise sharing.',
              },
              {
                icon: Mail,
                title: 'Human Support',
                desc: 'Real people, not bots. Response inside business hours. support@raptorflow.in',
              },
              {
                icon: Download,
                title: 'Export Everything',
                desc: 'PDF, Markdown, JSON. Your data is portable. Leave anytime with everything intact.',
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="group"
              >
                <div className="mx-auto mb-8 flex h-20 w-20 items-center justify-center rounded-full border-2 border-black bg-white group-hover:bg-black transition-colors duration-300">
                  <item.icon className="h-8 w-8 text-black group-hover:text-white transition-colors duration-300" strokeWidth={2} />
                </div>

                <h3 className="mb-4 font-serif text-2xl font-bold">
                  {item.title}
                </h3>

                <p className="text-sm leading-relaxed opacity-70 max-w-xs mx-auto">
                  {item.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* FINAL CTA */}
      {/* ====================================================================== */}
      {/* ====================================================================== */}
      {/* FINAL CTA - MONOCHROME */}
      {/* ====================================================================== */}
      <section className="bg-black py-32 sm:py-40 text-white relative overflow-hidden">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <p className="text-xs font-mono uppercase tracking-widest mb-8 text-white/60">Ready</p>
            <h2 className="mb-12 font-serif font-black leading-[0.9] tracking-tighter" style={{ fontSize: 'clamp(4rem, 12vw, 12rem)' }}>
              Transform Your
              <br />
              Marketing Today
            </h2>
            <p className="mb-16 text-lg sm:text-xl text-white/60 font-light max-w-2xl mx-auto">
              Join hundreds of teams who've ditched the chaos for clarity.
              <br />
              Get started in minutes. No complexity.
            </p>
            <div className="flex flex-col sm:flex-row flex-wrap items-center justify-center gap-6">
              <Link to="/register" className="group inline-flex items-center justify-center gap-3 bg-white px-10 py-5 text-base font-bold uppercase tracking-widest text-black transition-all duration-300 hover:bg-gray-200">
                Get Started Now
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link to="/login" className="inline-flex items-center justify-center gap-3 border-2 border-white px-10 py-5 text-base font-bold uppercase tracking-widest text-white transition-all duration-300 hover:bg-white hover:text-black">
                Sign In
              </Link>
            </div>
            <p className="mt-12 text-xs font-mono uppercase tracking-widest text-white/40 flex items-center justify-center gap-2">
              <CheckCircle2 className="h-3 w-3" />
              Monthly billing • Cancel anytime • No surprises
            </p>
          </motion.div>
        </div>
      </section>

      {/* ====================================================================== */}
      {/* FOOTER */}
      {/* ====================================================================== */}
      {/* ====================================================================== */}
      {/* FOOTER - MONOCHROME */}
      {/* ====================================================================== */}
      <footer className="border-t-2 border-black bg-white py-12 sm:py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="flex flex-col items-center justify-between gap-8 md:flex-row">
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center border-2 border-black bg-black text-white">
                <Rocket className="h-5 w-5" strokeWidth={2} />
              </div>
              <span className="font-serif text-2xl font-black tracking-tight">RaptorFlow</span>
            </div>
            <div className="flex flex-wrap justify-center gap-8 text-xs font-bold uppercase tracking-widest text-black">
              <Link to="/privacy" className="hover:underline">
                Privacy
              </Link>
              <Link to="/terms" className="hover:underline">
                Terms
              </Link>
              <a href="mailto:support@raptorflow.in" className="hover:underline">
                Support
              </a>
            </div>
          </div>
          <div className="mt-12 text-center text-xs font-mono uppercase tracking-widest opacity-40">
            © 2025 RaptorFlow. Marketing clarity, delivered.
          </div>
        </div>
      </footer>
    </div>
  )
}