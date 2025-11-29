import { Link } from 'react-router-dom'
import {
  Target,
  Shield,
  ArrowRight,
  CheckCircle2,
  Zap,
  TrendingUp,
  Brain,
  ChevronDown,
  Menu,
  X,
  Check,
  Zap as ZapIcon,
  Rocket,
  Users,
  Activity,
  Globe,
  BarChart3,
  Layers
} from 'lucide-react'
import { motion, useScroll, useTransform, useInView, AnimatePresence, useSpring } from 'framer-motion'
import { useRef, useState, useEffect, memo, useCallback } from 'react'

// ============================================================================
// NOISE OVERLAY
// ============================================================================
const NoiseOverlay = memo(() => (
  <div className="fixed inset-0 pointer-events-none z-0 opacity-[0.03] mix-blend-overlay">
    <svg className="w-full h-full">
      <filter id="noise">
        <feTurbulence
          type="fractalNoise"
          baseFrequency="0.8"
          numOctaves="3"
          stitchTiles="stitch"
        />
      </filter>
      <rect width="100%" height="100%" filter="url(#noise)" />
    </svg>
  </div>
))
NoiseOverlay.displayName = 'NoiseOverlay'

// ============================================================================
// LIVE ACTIVITY TOAST
// ============================================================================
const LiveActivity = () => {
  const [activity, setActivity] = useState<{ text: string, time: string } | null>(null)
  
  const activities = [
    { text: "New cohort 'Enterprise CTOs' created", time: "2s ago" },
    { text: "Strategy move shipped in London", time: "5s ago" },
    { text: "Brief generated for 'Q3 Launch'", time: "12s ago" },
    { text: "Tone drift detected and fixed", time: "Just now" }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      const randomActivity = activities[Math.floor(Math.random() * activities.length)]
      setActivity(randomActivity)
      setTimeout(() => setActivity(null), 4000)
    }, 8000)
    return () => clearInterval(interval)
  }, [])

  return (
    <AnimatePresence>
      {activity && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.9 }}
          className="fixed bottom-8 left-8 z-50 bg-white border border-black/10 shadow-2xl rounded-lg p-4 flex items-center gap-4 max-w-xs hidden md:flex"
        >
          <div className="relative">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <div className="absolute inset-0 bg-green-500 rounded-full animate-ping opacity-20" />
          </div>
          <div>
            <p className="text-sm font-bold text-black">{activity.text}</p>
            <p className="text-xs text-gray-500">{activity.time}</p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// ============================================================================
// SPOTLIGHT CARD
// ============================================================================
const SpotlightCard = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => {
  const divRef = useRef<HTMLDivElement>(null)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [opacity, setOpacity] = useState(0)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!divRef.current) return
    const rect = divRef.current.getBoundingClientRect()
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top })
  }

  return (
    <div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative overflow-hidden transition-all duration-300 ${className}`}
    >
      <div
        className="pointer-events-none absolute -inset-px opacity-0 transition duration-300 z-10"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(0,0,0,0.04), transparent 40%)`
        }}
      />
      {children}
    </div>
  )
}

// ============================================================================
// ANIMATED COUNTER
// ============================================================================
const AnimatedCounter = memo(({ end, duration = 2, suffix = '', prefix = '' }: { end: number, duration?: number, suffix?: string, prefix?: string }) => {
  const [count, setCount] = useState(0)
  const nodeRef = useRef(null)
  const isInView = useInView(nodeRef, { once: true, amount: 0.5 })

  useEffect(() => {
    if (!isInView) return
    let startTime: number | null = null
    let rafId: number | null = null
    const animate = (currentTime: number) => {
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
// MAGNETIC BUTTON
// ============================================================================
const MagneticButton = memo(({ children, className, to, onClick, variant = 'primary' }: { children: React.ReactNode, className?: string, to?: string, onClick?: () => void, variant?: 'primary' | 'secondary' | 'ghost' }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const buttonRef = useRef<any>(null)

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
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
  
  const baseStyles = "relative inline-flex items-center justify-center px-8 py-4 text-base font-bold uppercase tracking-wider transition-all duration-200 overflow-hidden rounded-sm"
  const variants = {
    primary: "bg-black text-white hover:bg-gray-900 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.2)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]",
    secondary: "bg-white text-black border-2 border-black hover:bg-gray-50 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]",
    ghost: "text-black hover:bg-black/5"
  }

  return (
    <Component
      to={to as string}
      ref={buttonRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      className={`${baseStyles} ${variants[variant]} ${className}`}
      style={{
        transform: `translate(${position.x}px, ${position.y}px)`,
        transition: 'transform 0.2s ease-out'
      }}
    >
      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </Component>
  )
})
MagneticButton.displayName = 'MagneticButton'

// ============================================================================
// MOBILE NAV COMPONENT
// ============================================================================
const MobileNav = ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60]"
            onClick={onClose}
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 w-80 bg-white z-[70] shadow-2xl border-l border-black/10"
          >
            <div className="p-6 flex flex-col h-full">
              <div className="flex justify-between items-center mb-8">
                <span className="font-display font-black text-xl">Menu</span>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-black/5 rounded-lg transition-colors"
                  aria-label="Close menu"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-6 flex-1">
                {['Features', 'Pricing', 'FAQ'].map((item) => (
                  <a
                    key={item}
                    href={`#${item.toLowerCase()}`}
                    onClick={onClose}
                    className="block text-2xl font-display font-bold hover:text-gray-500 transition-colors"
                  >
                    {item}
                  </a>
                ))}
                <Link
                  to="/login"
                  onClick={onClose}
                  className="block text-2xl font-display font-bold hover:text-gray-500 transition-colors"
                >
                  Sign In
                </Link>
              </div>

              <Link
                to="/register"
                onClick={onClose}
                className="block w-full bg-black text-white text-center py-4 font-bold uppercase tracking-widest hover:bg-gray-900 transition-colors"
              >
                Get Started
              </Link>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// ============================================================================
// FEATURE BENTO GRID
// ============================================================================
const BentoGrid = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-7xl mx-auto px-4">
      {/* Large Card */}
      <SpotlightCard className="md:col-span-2 row-span-2 bg-white border-2 border-black p-8 rounded-2xl relative group">
        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <Target className="w-32 h-32" />
        </div>
        <div className="h-full flex flex-col justify-between relative z-10">
          <div className="space-y-4">
            <div className="w-12 h-12 bg-black rounded-full flex items-center justify-center text-white mb-6">
              <Target className="w-6 h-6" />
            </div>
            <h3 className="text-4xl font-display font-black">Precision Cohorts</h3>
            <p className="text-xl text-gray-600 max-w-md">
              Define your audience with surgical precision. Demographics are dead. Long live psychographics, triggers, and micro-moments.
            </p>
          </div>
          <div className="mt-12 relative h-64 bg-gray-50 rounded-xl border border-black/10 overflow-hidden group-hover:border-black/30 transition-colors">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-full max-w-sm space-y-3 p-6">
                {[1, 2, 3].map((i) => (
                  <motion.div
                    key={i}
                    initial={{ x: -20, opacity: 0 }}
                    whileInView={{ x: 0, opacity: 1 }}
                    transition={{ delay: i * 0.2 }}
                    className="flex items-center gap-3 bg-white p-3 rounded-lg shadow-sm border border-black/5"
                  >
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <div className="h-2 bg-gray-200 rounded w-24" />
                    <div className="h-2 bg-gray-100 rounded w-full" />
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </SpotlightCard>

      {/* Tall Card */}
      <SpotlightCard className="row-span-2 bg-black text-white p-8 rounded-2xl relative overflow-hidden group min-h-[500px] md:min-h-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-gray-800 via-black to-black opacity-50" />
        <div className="relative z-10 h-full flex flex-col">
          <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-black mb-6">
            <Zap className="w-6 h-6" />
          </div>
          <h3 className="text-3xl font-display font-black mb-4">Velocity</h3>
          <p className="text-gray-400 mb-8">
            Ship 3x faster with pre-built strategic moves and automated briefs.
          </p>
          <div className="flex-1 relative">
            <div className="absolute inset-0 flex flex-col gap-2 overflow-hidden">
              {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                <motion.div
                  key={i}
                  initial={{ x: 100, opacity: 0 }}
                  whileInView={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.5 + i * 0.1, type: "spring" }}
                  className="h-12 border border-white/10 rounded-lg flex items-center px-4 gap-3 bg-white/5 backdrop-blur-sm"
                >
                  <div className="w-4 h-4 border border-white/20 rounded-full" />
                  <div className="h-2 w-full bg-white/10 rounded" />
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </SpotlightCard>

      {/* Small Card 1 */}
      <SpotlightCard className="bg-[#f8f8f8] border-2 border-black p-8 rounded-2xl group">
        <div className="absolute top-4 right-4">
          <Activity className="w-6 h-6 text-gray-300 group-hover:text-black transition-colors" />
        </div>
        <div className="space-y-4">
          <Brain className="w-8 h-8" />
          <h3 className="text-xl font-bold font-display">AI Sentinel</h3>
          <p className="text-sm text-gray-600">
            Real-time tone monitoring. Never drift off-brand again.
          </p>
        </div>
      </SpotlightCard>

      {/* Small Card 2 */}
      <SpotlightCard className="bg-[#f8f8f8] border-2 border-black p-8 rounded-2xl group">
        <div className="absolute top-4 right-4">
          <BarChart3 className="w-6 h-6 text-gray-300 group-hover:text-black transition-colors" />
        </div>
        <div className="space-y-4">
          <TrendingUp className="w-8 h-8" />
          <h3 className="text-xl font-bold font-display">True Metrics</h3>
          <p className="text-sm text-gray-600">
            Track impact, not just vanity numbers. Signal over noise.
          </p>
        </div>
      </SpotlightCard>
    </div>
  )
}

// ============================================================================
// COMPARISON TABLE
// ============================================================================
const ComparisonTable = () => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b-2 border-black">
            <th className="p-6 font-display font-black text-xl bg-white sticky left-0 z-10 w-1/3">Feature</th>
            <th className="p-6 font-display font-bold text-gray-400 w-1/3">Traditional Tools</th>
            <th className="p-6 font-display font-black bg-black text-white w-1/3">RaptorFlow</th>
          </tr>
        </thead>
        <tbody>
          {[
            { feature: "Workflow", old: "Endless task lists", new: "Strategic Moves" },
            { feature: "Audience", old: "Vague demographics", new: "Psychographic Cohorts" },
            { feature: "Content", old: "Post every day", new: "High-impact Cadence" },
            { feature: "Analytics", old: "Vanity metrics (likes)", new: "Impact metrics (revenue)" },
            { feature: "Tone", old: "Manual checks", new: "AI Sentinel Guardrails" },
            { feature: "Setup", old: "Weeks of config", new: "45 minutes" }
          ].map((row, i) => (
            <tr key={i} className="border-b border-black/5 hover:bg-gray-50 transition-colors">
              <td className="p-6 font-bold bg-white sticky left-0 z-10">{row.feature}</td>
              <td className="p-6 text-gray-500 flex items-center gap-2">
                <X className="w-4 h-4 text-red-400" /> {row.old}
              </td>
              <td className="p-6 font-bold border-l-2 border-black/5 bg-black/5">
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-600" /> {row.new}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ============================================================================
// INFINITE SCROLL LOGOS
// ============================================================================
const InfiniteLogos = () => {
  return (
    <div className="w-full overflow-hidden bg-white py-12 border-y border-black/5">
      <div className="max-w-7xl mx-auto relative">
        <div className="flex overflow-hidden mask-linear-fade">
          <motion.div 
            className="flex gap-16 items-center whitespace-nowrap"
            animate={{ x: ["0%", "-50%"] }}
            transition={{ duration: 20, ease: "linear", repeat: Infinity }}
          >
            {[...Array(16)].map((_, i) => (
              <span key={i} className="text-2xl font-display font-black text-black/10 uppercase tracking-widest flex items-center gap-4">
                <Globe className="w-6 h-6 opacity-20" />
                TRUSTED BRAND {i + 1}
              </span>
            ))}
          </motion.div>
        </div>
        <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-white to-transparent pointer-events-none" />
        <div className="absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-white to-transparent pointer-events-none" />
      </div>
    </div>
  )
}

// ============================================================================
// FAQ ACCORDION
// ============================================================================
const FAQAccordion = ({ items }: { items: { q: string, a: string }[] }) => {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      {items.map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="border-2 border-black bg-white overflow-hidden rounded-lg"
        >
          <button
            onClick={() => setOpenIndex(openIndex === i ? null : i)}
            className="w-full flex items-center justify-between p-6 text-left bg-white hover:bg-gray-50 transition-colors"
            aria-expanded={openIndex === i}
          >
            <span className="font-bold text-lg pr-8">{item.q}</span>
            <motion.div
              animate={{ rotate: openIndex === i ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDown className="w-5 h-5" />
            </motion.div>
          </button>
          <AnimatePresence>
            {openIndex === i && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <div className="p-6 pt-0 text-gray-600 leading-relaxed border-t border-black/5">
                  {item.a}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      ))}
    </div>
  )
}

// ============================================================================
// PRICING CARD
// ============================================================================
const PricingCard = ({ title, price, features, isPopular }: { title: string, price: string, features: string[], isPopular?: boolean }) => (
  <div className={`relative p-8 border-2 flex flex-col h-full transition-transform hover:-translate-y-2 duration-300 ${isPopular ? 'border-black bg-black text-white scale-105 shadow-2xl z-10' : 'border-black/10 bg-white text-black'}`}>
    {isPopular && (
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-white text-black px-4 py-1 text-xs font-bold uppercase tracking-widest border-2 border-black shadow-lg">
        Most Popular
      </div>
    )}
    <div className="mb-8">
      <h3 className="text-xl font-bold uppercase tracking-widest mb-4">{title}</h3>
      <div className="flex items-baseline gap-1">
        <span className="text-5xl font-display font-black">{price}</span>
        <span className="opacity-60">/mo</span>
      </div>
    </div>
    <div className="flex-1 mb-8 space-y-4">
      {features.map((feat, i) => (
        <div key={i} className="flex items-start gap-3">
          <Check className={`w-5 h-5 flex-shrink-0 ${isPopular ? 'text-green-400' : 'text-black'}`} />
          <span className="text-sm leading-tight opacity-80">{feat}</span>
        </div>
      ))}
    </div>
    <MagneticButton
      to="/register"
      variant={isPopular ? 'secondary' : 'primary'}
      className="w-full"
    >
      Get Started
    </MagneticButton>
  </div>
)

// ============================================================================
// MAIN LANDING COMPONENT
// ============================================================================
export default function Landing() {
  const { scrollYProgress } = useScroll()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  // Hero Parallax
  const heroY = useTransform(scrollYProgress, [0, 0.5], [0, 200])
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0])

  return (
    <div className="min-h-screen bg-[#f8f8f8] text-black selection:bg-black selection:text-white font-sans overflow-x-hidden relative">
      <NoiseOverlay />
      <LiveActivity />
      
      {/* PROGRESS BAR */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-black origin-left z-[50]"
        style={{ scaleX: scrollYProgress }}
      />

      {/* MOBILE NAV */}
      <MobileNav isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />

      {/* NAV */}
      <nav className="fixed top-0 w-full z-40 px-4 py-4 sm:px-6 lg:px-8 backdrop-blur-md border-b border-black/5 bg-white/80">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 bg-black text-white flex items-center justify-center rounded-lg transition-transform group-hover:rotate-12">
              <ZapIcon className="w-6 h-6" />
            </div>
            <span className="text-xl font-sans font-black tracking-tight">RaptorFlow</span>
          </Link>

          <div className="hidden md:flex items-center gap-8 font-medium text-sm uppercase tracking-widest">
            <a href="#features" className="hover:text-gray-600 transition-colors">Features</a>
            <a href="#pricing" className="hover:text-gray-600 transition-colors">Pricing</a>
            <a href="#faq" className="hover:text-gray-600 transition-colors">FAQ</a>
            <Link to="/login" className="hover:text-gray-600 transition-colors">Login</Link>
            <MagneticButton to="/register" className="!py-2 !px-6 !text-xs">
              Sign Up
            </MagneticButton>
          </div>

          <button 
            className="md:hidden p-2" 
            onClick={() => setMobileMenuOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="w-6 h-6" />
          </button>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-50 pointer-events-none" />
        
        {/* Scanning Line */}
        <motion.div 
          className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-black/10 to-transparent"
          animate={{ top: ["0%", "100%"] }}
          transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
        />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-black/10 shadow-sm mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-widest text-gray-500">Marketing OS v2.0</span>
          </motion.div>

          <motion.h1
            style={{ y: heroY, opacity: heroOpacity }}
            className="text-5xl sm:text-7xl lg:text-9xl font-display font-black tracking-tighter leading-[0.9] mb-8"
          >
            Strategy is <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-b from-black to-gray-600">
              Not Chaos.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="max-w-2xl mx-auto text-xl sm:text-2xl text-gray-600 mb-12 leading-relaxed"
          >
            Stop the random acts of marketing. Build precise cohorts, plan strategic moves, and ship with calm consistency.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <MagneticButton to="/register" className="w-full sm:w-auto">
              Start Building <ArrowRight className="w-4 h-4 ml-2" />
            </MagneticButton>
            <MagneticButton to="#demo" variant="secondary" className="w-full sm:w-auto">
              View Demo
            </MagneticButton>
          </motion.div>
        </div>
      </section>

      {/* LOGO SCROLL */}
      <div className="border-y border-black/5 bg-white/50 backdrop-blur-sm">
        <InfiniteLogos />
      </div>

      {/* PROBLEM STATEMENT */}
      <section className="py-24 bg-black text-white relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full opacity-10">
           <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-gray-800 via-black to-black" />
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-display font-black mb-6 leading-tight">
                Most teams are <br />
                <span className="text-red-500">drowning in noise.</span>
              </h2>
              <div className="space-y-6 text-lg text-gray-400">
                <p>
                  You have 50 tabs open. Your task list is endless. You're posting because you feel guilty, not because you have a strategy.
                </p>
                <p>
                  Without constraints, marketing expands to fill every waking hour. And you still feel like you're falling behind.
                </p>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-4 bg-red-500/20 blur-3xl rounded-full" />
              <div className="relative bg-gray-900 border border-white/10 p-8 rounded-2xl">
                <div className="space-y-4 opacity-50">
                  <div className="flex items-center gap-4 border-b border-white/5 pb-4">
                    <X className="text-red-500 w-6 h-6" />
                    <span>Post on LinkedIn (again)</span>
                  </div>
                  <div className="flex items-center gap-4 border-b border-white/5 pb-4">
                    <X className="text-red-500 w-6 h-6" />
                    <span>Update TikTok strategy</span>
                  </div>
                  <div className="flex items-center gap-4 border-b border-white/5 pb-4">
                    <X className="text-red-500 w-6 h-6" />
                    <span>Respond to 400 emails</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <X className="text-red-500 w-6 h-6" />
                    <span>Panic about metrics</span>
                  </div>
                </div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="bg-red-500 text-white px-6 py-2 font-bold uppercase tracking-widest rotate-[-12deg] shadow-xl border-2 border-white">
                    Burnout Mode
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES BENTO */}
      <section id="features" className="py-32 bg-gray-50">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-6xl font-display font-black mb-4">The Operating System</h2>
          <p className="text-xl text-gray-600">Constraints that create freedom.</p>
        </div>
        <BentoGrid />
      </section>

      {/* COMPARISON */}
      <section className="py-32 bg-white overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-6xl font-display font-black mb-4">Compare & Contrast</h2>
            <p className="text-xl text-gray-600">Why teams switch to RaptorFlow.</p>
          </div>
          <ComparisonTable />
        </div>
      </section>

      {/* PRICING */}
      <section id="pricing" className="py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-6xl font-display font-black mb-4">Simple Pricing</h2>
            <p className="text-xl text-gray-600">Invest in clarity, not shelfware.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 items-start">
            <PricingCard
              title="Ascent"
              price="₹3,500"
              features={['3 Active Cohorts', 'Weekly Strategy Moves', 'Basic Analytics', 'Email Support']}
            />
            <PricingCard
              title="Glide"
              price="₹7,000"
              features={['6 Active Cohorts', 'Advanced Moves Planner', 'AI Tone Guardian', 'Priority Support', 'Team Access (3 Seats)']}
              isPopular
            />
            <PricingCard
              title="Soar"
              price="₹10,000"
              features={['Unlimited Cohorts', 'Full Command Center', 'Agency Whitelabeling', 'Dedicated Manager', 'API Access']}
            />
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-32 bg-white border-t border-black/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-display font-black mb-4">Straight Answers</h2>
          </div>
          <FAQAccordion items={[
            { q: "Is this just a content calendar?", a: "No. A calendar tells you 'when'. RaptorFlow tells you 'who', 'what', and 'why'. It's a strategy engine first, execution tool second." },
            { q: "How long does setup take?", a: "About 45 minutes to define your first cohort and plan your first week of moves. We force you to keep it simple." },
            { q: "Can I invite my team?", a: "Yes. The Glide and Soar plans support team members with specific roles and permission levels." },
            { q: "What if I hate it?", a: "Cancel anytime. Export your data. No hard feelings. We want you to win, even if it's not with us." }
          ]} />
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="py-32 bg-black text-white text-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
           <div className="absolute inset-0 bg-[linear-gradient(45deg,#ffffff33_1px,transparent_1px)] [background-size:40px_40px]" />
        </div>
        <div className="relative z-10 max-w-4xl mx-auto px-4">
          <h2 className="text-5xl md:text-8xl font-display font-black mb-8 tracking-tighter text-white">
            Ready to <br />
            <span className="text-gray-400">
              Get Serious?
            </span>
          </h2>
          <p className="text-xl md:text-2xl text-gray-400 mb-12">
            Join the top 1% of marketers who plan before they post.
          </p>
          <MagneticButton to="/register" variant="secondary" className="text-xl px-12 py-6">
            Start Your Free Trial
          </MagneticButton>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-black text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-gray-900 via-black to-black opacity-50" />
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 lg:gap-8 mb-20">
            {/* Brand & Newsletter */}
            <div className="lg:col-span-2 space-y-8">
              <Link to="/" className="flex items-center gap-2 group w-fit">
                <div className="w-10 h-10 bg-white text-black flex items-center justify-center rounded-lg transition-transform group-hover:rotate-12">
                  <ZapIcon className="w-6 h-6" />
                </div>
                <span className="text-2xl font-sans font-black tracking-tight">RaptorFlow</span>
              </Link>
              <p className="text-gray-400 max-w-sm text-lg leading-relaxed">
                The operating system for high-performance marketing teams. Plan, execute, and track your strategy without the chaos.
              </p>
              
              <div className="space-y-4">
                <h4 className="text-sm font-bold uppercase tracking-widest text-white/60">Subscribe to Updates</h4>
                <div className="flex gap-2 max-w-md">
                  <input 
                    type="email" 
                    placeholder="Enter your email" 
                    className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-white/30 transition-colors"
                  />
                  <button className="bg-white text-black px-6 py-3 rounded-lg font-bold hover:bg-gray-200 transition-colors">
                    Join
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-2 text-sm text-green-400">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span>All systems operational</span>
              </div>
            </div>

            {/* Links Column 1 */}
            <div>
              <h4 className="text-sm font-bold uppercase tracking-widest text-white/60 mb-6">Product</h4>
              <ul className="space-y-4">
                {['Features', 'Pricing', 'Changelog', 'Docs', 'Integrations', 'API'].map((item) => (
                  <li key={item}>
                    <Link to="#" className="text-gray-400 hover:text-white transition-colors">{item}</Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Links Column 2 */}
            <div>
              <h4 className="text-sm font-bold uppercase tracking-widest text-white/60 mb-6">Company</h4>
              <ul className="space-y-4">
                {['About', 'Careers', 'Blog', 'Contact', 'Partners', 'Legal'].map((item) => (
                  <li key={item}>
                    <Link to="#" className="text-gray-400 hover:text-white transition-colors">{item}</Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex flex-wrap gap-8 text-sm text-gray-500">
              <span>© 2025 RaptorFlow Inc.</span>
              <Link to="#" className="hover:text-white transition-colors">Privacy Policy</Link>
              <Link to="#" className="hover:text-white transition-colors">Terms of Service</Link>
              <Link to="#" className="hover:text-white transition-colors">Cookie Settings</Link>
            </div>
            
            <div className="flex gap-6">
              {['Twitter', 'GitHub', 'LinkedIn', 'Discord'].map((social) => (
                <Link key={social} to="#" className="text-gray-500 hover:text-white transition-colors">
                  <span className="sr-only">{social}</span>
                  {/* Placeholder icons - replace with actual social icons if desired */}
                  <div className="w-5 h-5 bg-current rounded-sm" />
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Giant Text Background */}
        <div className="absolute bottom-0 left-0 right-0 overflow-hidden opacity-[0.03] pointer-events-none select-none">
          <h1 className="text-[20vw] font-display font-black leading-[0.8] text-white whitespace-nowrap text-center transform translate-y-1/4">
            RAPTORFLOW
          </h1>
        </div>
      </footer>
    </div>
  )
}
