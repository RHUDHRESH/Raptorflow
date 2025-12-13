import React, { useState, useRef, useEffect, useMemo } from 'react'
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence, useInView } from 'framer-motion'
import {
  Twitter,
  Linkedin,
  Mail,
  ArrowUpRight,
  Sparkles,
  ChevronUp,
  Send,
  Check,
  Copy,
  Heart,
  Zap,
  Star,
  ArrowRight,
  ExternalLink
} from 'lucide-react'

// Floating orbs background
const FloatingOrbs = () => {
  const orbs = useMemo(() => [
    { size: 300, x: '10%', y: '20%', duration: 25, delay: 0, color: 'from-primary/5 to-primary/2' },
    { size: 200, x: '80%', y: '60%', duration: 20, delay: 5, color: 'from-primary/4 to-primary/2' },
    { size: 400, x: '50%', y: '80%', duration: 30, delay: 10, color: 'from-primary/3 to-primary/1' },
    { size: 150, x: '70%', y: '10%', duration: 22, delay: 8, color: 'from-primary/5 to-primary/3' },
  ], [])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {orbs.map((orb, i) => (
        <motion.div
          key={i}
          className={`absolute rounded-full bg-gradient-radial ${orb.color} blur-3xl`}
          style={{
            width: orb.size,
            height: orb.size,
            left: orb.x,
            top: orb.y,
            transform: 'translate(-50%, -50%)',
          }}
          animate={{
            x: [0, 50, -30, 0],
            y: [0, -40, 30, 0],
            scale: [1, 1.1, 0.9, 1],
          }}
          transition={{
            duration: orb.duration,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: orb.delay,
          }}
        />
      ))}
    </div>
  )
}

// Premium noise texture overlay
const NoiseOverlay = () => (
  <div
    className="absolute inset-0 opacity-[0.015] pointer-events-none mix-blend-overlay"
    style={{
      backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
    }}
  />
)

// Animated text reveal
const RevealText = ({ children, className = '', delay = 0 }) => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <div ref={ref} className="overflow-hidden">
      <motion.div
        initial={{ y: '100%', opacity: 0 }}
        animate={isInView ? { y: 0, opacity: 1 } : { y: '100%', opacity: 0 }}
        transition={{ duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] }}
        className={className}
      >
        {children}
      </motion.div>
    </div>
  )
}

// Large typographic statement
const FooterStatement = () => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <div ref={ref} className="relative text-center mb-24">
      <motion.div
        initial={{ opacity: 0 }}
        animate={isInView ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 1 }}
        className="absolute inset-0 flex items-center justify-center pointer-events-none"
      >
        <div className="w-[600px] h-[600px] bg-gradient-radial from-primary/10 via-primary/5 to-transparent blur-3xl" />
      </motion.div>

      <RevealText className="inline-block">
        <span className="text-display text-4xl md:text-5xl text-foreground tracking-tight">
          Stop guessing.
        </span>
      </RevealText>
      <br />
      <RevealText delay={0.1} className="inline-block">
        <span className="text-display text-4xl md:text-5xl tracking-tight">
          Start <span className="text-primary italic">winning.</span>
        </span>
      </RevealText>

      <RevealText delay={0.3}>
        <p className="text-muted-foreground text-lg mt-8 max-w-xl mx-auto leading-relaxed">
          Join thousands of founders building legendary brands with AI-powered clarity
        </p>
      </RevealText>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="mt-10"
      >
        <a
          href="/signup"
          className="group inline-flex items-center gap-2 px-8 py-4 bg-foreground hover:bg-primary text-background text-caption transition-all"
        >
          Get started free
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </a>
      </motion.div>
    </div>
  )
}

// Premium glass card
const GlassCard = ({ children, className = '' }) => (
  <div className={`relative rounded-2xl bg-white/[0.02] backdrop-blur-xl border border-white/[0.05] p-6 ${className}`}>
    <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent pointer-events-none" />
    {children}
  </div>
)

// Interactive link with glow
const FooterLink = ({ href, children, external = false }) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.a
      href={href}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
      className="group relative inline-flex items-center gap-1.5 text-white/40 hover:text-white text-sm transition-colors duration-300"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ x: 4 }}
    >
      <motion.span
        className="absolute -left-3 w-1.5 h-1.5 rounded-full bg-amber-400"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: isHovered ? 1 : 0, opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.2 }}
      />
      {children}
      {external && (
        <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
      )}
    </motion.a>
  )
}

// Newsletter with premium styling
const PremiumNewsletter = () => {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle')
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email) return

    setStatus('loading')
    await new Promise(resolve => setTimeout(resolve, 1500))
    setStatus('success')
    setEmail('')
    setTimeout(() => setStatus('idle'), 3000)
  }

  return (
    <GlassCard className="relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-radial from-amber-500/10 to-transparent blur-2xl" />

      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-black" />
          </div>
          <h4 className="text-white font-medium">Join the inner circle</h4>
        </div>

        <p className="text-white/40 text-sm mb-5">
          Weekly insights on AI marketing, positioning, and founder growth.
        </p>

        <form onSubmit={handleSubmit}>
          <motion.div
            className={`
              relative flex items-center gap-2 p-1 rounded-xl border transition-all duration-300
              ${isFocused
                ? 'border-amber-500/40 bg-amber-500/5 shadow-[0_0_30px_rgba(245,158,11,0.1)]'
                : 'border-white/10 bg-white/5'
              }
            `}
          >
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Your email"
              className="flex-1 px-4 py-3 bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
              disabled={status !== 'idle'}
            />

            <motion.button
              type="submit"
              disabled={status !== 'idle' || !email}
              className="px-5 py-3 bg-white text-black font-medium rounded-lg text-sm flex items-center gap-2 disabled:opacity-50 transition-all hover:bg-white/90"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <AnimatePresence mode="wait">
                {status === 'loading' ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0, rotate: 0 }}
                    animate={{ opacity: 1, rotate: 360 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                    className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full"
                  />
                ) : status === 'success' ? (
                  <motion.div
                    key="success"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                  >
                    <Check className="w-4 h-4" />
                  </motion.div>
                ) : (
                  <motion.span
                    key="text"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    Subscribe
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          </motion.div>
        </form>

        <AnimatePresence>
          {status === 'success' && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-emerald-400 text-xs mt-3 flex items-center gap-1"
            >
              <Star className="w-3 h-3" />
              Welcome to the inner circle!
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    </GlassCard>
  )
}

// Social link with magnetic effect
const SocialLink = ({ href, icon: Icon, label }) => {
  const ref = useRef(null)
  const [isHovered, setIsHovered] = useState(false)

  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const springConfig = { damping: 15, stiffness: 200 }
  const xSpring = useSpring(x, springConfig)
  const ySpring = useSpring(y, springConfig)

  const handleMouseMove = (e) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    x.set((e.clientX - centerX) * 0.2)
    y.set((e.clientY - centerY) * 0.2)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
    setIsHovered(false)
  }

  return (
    <motion.a
      ref={ref}
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="group relative"
      style={{ x: xSpring, y: ySpring }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center transition-colors duration-300 group-hover:border-amber-500/30 group-hover:bg-amber-500/5"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        <Icon className="w-5 h-5 text-white/40 group-hover:text-amber-400 transition-colors" />
      </motion.div>

      {/* Tooltip */}
      <AnimatePresence>
        {isHovered && (
          <motion.span
            initial={{ opacity: 0, y: 5, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 5, scale: 0.9 }}
            className="absolute -top-10 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-white text-black text-xs font-medium rounded-lg whitespace-nowrap pointer-events-none"
          >
            {label}
            <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-white rotate-45" />
          </motion.span>
        )}
      </AnimatePresence>
    </motion.a>
  )
}

// Email copy button
const EmailButton = () => {
  const [copied, setCopied] = useState(false)
  const email = 'hello@raptorflow.com'

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(email)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <motion.button
      onClick={handleCopy}
      className="group flex items-center gap-3 px-5 py-3 bg-white/5 border border-white/10 rounded-xl hover:border-amber-500/30 hover:bg-amber-500/5 transition-all duration-300"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Mail className="w-4 h-4 text-amber-400" />
      <span className="text-white/70 group-hover:text-white transition-colors text-sm">
        {email}
      </span>
      <AnimatePresence mode="wait">
        {copied ? (
          <motion.div
            key="check"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
          >
            <Check className="w-4 h-4 text-emerald-400" />
          </motion.div>
        ) : (
          <motion.div
            key="copy"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
          >
            <Copy className="w-4 h-4 text-white/30 group-hover:text-white/60 transition-colors" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  )
}

// Animated logo
const AnimatedLogo = () => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.a
      href="/"
      className="flex items-center gap-3"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <motion.div
        className="relative w-11 h-11 bg-gradient-to-br from-amber-400 via-amber-500 to-orange-500 rounded-xl flex items-center justify-center overflow-hidden"
        animate={{
          rotate: isHovered ? [0, -5, 5, 0] : 0,
          scale: isHovered ? 1.05 : 1
        }}
        transition={{ duration: 0.4 }}
      >
        <motion.div
          className="absolute inset-0 bg-gradient-to-tr from-white/20 to-transparent"
          animate={{ opacity: isHovered ? 0.3 : 0 }}
        />
        <span className="text-black font-bold text-lg relative z-10">Rf</span>
      </motion.div>
      <div className="text-2xl text-white font-light tracking-tight">
        Raptor<motion.span
          className="italic font-normal"
          animate={{
            color: isHovered ? '#fcd34d' : '#fde68a'
          }}
          transition={{ duration: 0.3 }}
        >
          flow
        </motion.span>
      </div>
    </motion.a>
  )
}

// Scroll to top
const ScrollToTop = () => {
  const [isVisible, setIsVisible] = useState(false)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      setProgress(scrollTop / docHeight)
      setIsVisible(scrollTop > 500)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.button
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-50 w-14 h-14 rounded-full bg-zinc-900/90 backdrop-blur-xl border border-white/10 flex items-center justify-center group shadow-2xl"
        >
          <svg className="absolute inset-0 w-full h-full -rotate-90">
            <circle
              cx="28"
              cy="28"
              r="26"
              fill="none"
              stroke="rgba(245, 158, 11, 0.15)"
              strokeWidth="2"
            />
            <motion.circle
              cx="28"
              cy="28"
              r="26"
              fill="none"
              stroke="rgb(245, 158, 11)"
              strokeWidth="2"
              strokeLinecap="round"
              style={{
                pathLength: progress,
                strokeDasharray: '1 1'
              }}
            />
          </svg>

          <motion.div
            animate={{ y: [0, -2, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <ChevronUp className="w-5 h-5 text-white/60 group-hover:text-amber-400 transition-colors" />
          </motion.div>
        </motion.button>
      )}
    </AnimatePresence>
  )
}

// Main Footer component
const Footer = () => {
  const currentYear = new Date().getFullYear()
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  type FooterNavLink = { name: string; href: string; external?: boolean }

  const footerLinks: { product: FooterNavLink[]; company: FooterNavLink[]; legal: FooterNavLink[] } = {
    product: [
      { name: 'Features', href: '#features' },
      { name: 'Pricing', href: '/pricing' },
      { name: 'How it Works', href: '#how-it-works' },
      { name: 'Manifesto', href: '/manifesto' },
    ],
    company: [
      { name: 'About', href: '/about' },
      { name: 'Blog', href: '/blog', external: true },
      { name: 'Careers', href: '/careers' },
      { name: 'Contact', href: '/contact' },
    ],
    legal: [
      { name: 'Privacy Policy', href: '/privacy' },
      { name: 'Terms of Service', href: '/terms' },
      { name: 'Refund Policy', href: '/refunds' },
    ]
  }

  return (
    <>
      <ScrollToTop />

      <footer ref={ref} className="relative bg-background overflow-hidden">
        {/* Background elements */}
        <FloatingOrbs />
        <NoiseOverlay />

        {/* Top gradient line */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

        <div className="relative z-10">
          {/* Statement section */}
          <div className="max-w-7xl mx-auto px-6 pt-24 pb-8">
            <FooterStatement />
          </div>

          {/* Main content */}
          <div className="max-w-7xl mx-auto px-6 pb-16">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 40 }}
              transition={{ duration: 0.8 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-12"
            >
              {/* Left - Brand, Newsletter */}
              <div className="lg:col-span-5 space-y-8">
                <AnimatedLogo />

                <p className="text-muted-foreground max-w-sm leading-relaxed">
                  The AI-first marketing operating system for founders who refuse to guess.
                  Build strategy, not spreadsheets.
                </p>

                <PremiumNewsletter />
              </div>

              {/* Right - Links Grid */}
              <div className="lg:col-span-7">
                <div className="grid grid-cols-3 gap-8">
                  <div>
                    <h4 className="text-white/80 font-medium mb-6 text-sm uppercase tracking-wider">Product</h4>
                    <ul className="space-y-4">
                      {footerLinks.product.map((link) => (
                        <li key={link.name}>
                          <FooterLink href={link.href} external={link.external}>
                            {link.name}
                          </FooterLink>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="text-foreground font-medium mb-6 text-caption">Company</h4>
                    <ul className="space-y-4">
                      {footerLinks.company.map((link) => (
                        <li key={link.name}>
                          <FooterLink href={link.href} external={link.external}>
                            {link.name}
                          </FooterLink>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="text-foreground font-medium mb-6 text-caption">Legal</h4>
                    <ul className="space-y-4">
                      {footerLinks.legal.map((link) => (
                        <li key={link.name}>
                          <FooterLink href={link.href}>
                            {link.name}
                          </FooterLink>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Bottom bar */}
          <div className="border-t border-border/30">
            <div className="max-w-7xl mx-auto px-6 py-6">
              <motion.div
                initial={{ opacity: 0 }}
                animate={isInView ? { opacity: 1 } : { opacity: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="flex flex-col md:flex-row items-center justify-between gap-6"
              >
                {/* Left - Contact */}
                <div className="flex items-center gap-4">
                  <EmailButton />

                  <div className="flex items-center gap-2">
                    <SocialLink href="https://twitter.com/raptorflow" icon={Twitter} label="Twitter" />
                    <SocialLink href="https://linkedin.com/company/raptorflow" icon={Linkedin} label="LinkedIn" />
                  </div>
                </div>

                {/* Right - Copyright */}
                <div className="flex flex-col md:flex-row items-center gap-4 text-sm">
                  <motion.p
                    className="text-white/30 flex items-center gap-1"
                    whileHover={{ color: 'rgba(255,255,255,0.5)' }}
                  >
                    © {currentYear} Raptorflow. Crafted with
                    <motion.span
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1.2, repeat: Infinity }}
                    >
                      <Heart className="w-3.5 h-3.5 text-red-400 fill-red-400 mx-0.5" />
                    </motion.span>
                    in India
                  </motion.p>

                  <span className="hidden md:block text-white/10">•</span>

                  <p className="text-white/20 text-xs">
                    Building legendary brands, one founder at a time.
                  </p>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </footer>
    </>
  )
}

export default Footer
