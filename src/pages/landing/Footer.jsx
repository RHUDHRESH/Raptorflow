import React, { useState, useRef, useEffect } from 'react'
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from 'framer-motion'
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
  Heart
} from 'lucide-react'

// Magnetic button that follows cursor
const MagneticLink = ({ children, href, className = '' }) => {
  const ref = useRef(null)
  const [isHovered, setIsHovered] = useState(false)
  
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  
  const springConfig = { damping: 15, stiffness: 150 }
  const xSpring = useSpring(x, springConfig)
  const ySpring = useSpring(y, springConfig)

  const handleMouseMove = (e) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    
    const distanceX = e.clientX - centerX
    const distanceY = e.clientY - centerY
    
    x.set(distanceX * 0.3)
    y.set(distanceY * 0.3)
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
      className={`relative inline-flex items-center gap-2 group ${className}`}
      style={{ x: xSpring, y: ySpring }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      <motion.span
        className="absolute -inset-2 bg-amber-500/10 rounded-lg -z-10"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: isHovered ? 1 : 0, opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.2 }}
      />
    </motion.a>
  )
}

// Interactive email with copy functionality
const EmailCopy = () => {
  const [copied, setCopied] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
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
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="relative flex items-center gap-3 px-4 py-3 bg-white/5 border border-white/10 rounded-xl group overflow-hidden"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Animated background gradient */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-amber-500/20 via-yellow-500/20 to-amber-500/20"
        initial={{ x: '-100%' }}
        animate={{ x: isHovered ? '100%' : '-100%' }}
        transition={{ duration: 0.6, ease: 'easeInOut' }}
      />
      
      <Mail className="w-5 h-5 text-amber-400 relative z-10" />
      <span className="text-white/70 group-hover:text-white transition-colors relative z-10">
        {email}
      </span>
      
      <AnimatePresence mode="wait">
        {copied ? (
          <motion.div
            key="check"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 180 }}
            className="relative z-10"
          >
            <Check className="w-4 h-4 text-emerald-400" />
          </motion.div>
        ) : (
          <motion.div
            key="copy"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className="relative z-10"
          >
            <Copy className="w-4 h-4 text-white/30 group-hover:text-white/60 transition-colors" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  )
}

// Animated scroll to top button
const ScrollToTop = () => {
  const [isVisible, setIsVisible] = useState(false)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const scrollPercent = scrollTop / docHeight
      
      setProgress(scrollPercent)
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
          className="fixed bottom-8 right-8 z-50 w-12 h-12 rounded-full bg-zinc-900 border border-white/10 flex items-center justify-center group"
        >
          {/* Progress ring */}
          <svg className="absolute inset-0 w-full h-full -rotate-90">
            <circle
              cx="24"
              cy="24"
              r="22"
              fill="none"
              stroke="rgba(245, 158, 11, 0.2)"
              strokeWidth="2"
            />
            <motion.circle
              cx="24"
              cy="24"
              r="22"
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
            animate={{ y: [0, -3, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <ChevronUp className="w-5 h-5 text-white/60 group-hover:text-amber-400 transition-colors" />
          </motion.div>
        </motion.button>
      )}
    </AnimatePresence>
  )
}

// Social link with ripple effect
const SocialLink = ({ href, icon: Icon, label }) => {
  const [ripples, setRipples] = useState([])

  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    
    const newRipple = { x, y, id: Date.now() }
    setRipples(prev => [...prev, newRipple])
    
    setTimeout(() => {
      setRipples(prev => prev.filter(r => r.id !== newRipple.id))
    }, 600)
  }

  return (
    <motion.a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      onClick={handleClick}
      className="relative w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center overflow-hidden group"
      whileHover={{ scale: 1.1, borderColor: 'rgba(245, 158, 11, 0.3)' }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Ripples */}
      {ripples.map(ripple => (
        <motion.span
          key={ripple.id}
          className="absolute bg-amber-500/30 rounded-full pointer-events-none"
          initial={{ width: 0, height: 0, x: ripple.x, y: ripple.y, opacity: 1 }}
          animate={{ width: 100, height: 100, x: ripple.x - 50, y: ripple.y - 50, opacity: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      ))}
      
      <Icon className="w-5 h-5 text-white/50 group-hover:text-amber-400 transition-colors relative z-10" />
      
      {/* Tooltip */}
      <motion.span
        className="absolute -top-10 left-1/2 -translate-x-1/2 px-2 py-1 bg-zinc-800 text-white text-xs rounded whitespace-nowrap pointer-events-none"
        initial={{ opacity: 0, y: 5 }}
        whileHover={{ opacity: 1, y: 0 }}
      >
        {label}
      </motion.span>
    </motion.a>
  )
}

// Newsletter signup with animation
const NewsletterSignup = () => {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle') // idle, loading, success, error
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email) return
    
    setStatus('loading')
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setStatus('success')
    setEmail('')
    
    setTimeout(() => setStatus('idle'), 3000)
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <motion.div
        className={`
          relative flex items-center gap-2 p-1.5 rounded-xl border transition-colors
          ${isFocused ? 'border-amber-500/50 bg-amber-500/5' : 'border-white/10 bg-white/5'}
        `}
        animate={{
          boxShadow: isFocused ? '0 0 20px rgba(245, 158, 11, 0.1)' : '0 0 0px rgba(245, 158, 11, 0)'
        }}
      >
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Enter your email"
          className="flex-1 px-4 py-2.5 bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
          disabled={status === 'loading' || status === 'success'}
        />
        
        <motion.button
          type="submit"
          disabled={status === 'loading' || status === 'success' || !email}
          className="px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg text-sm flex items-center gap-2 disabled:opacity-50 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <AnimatePresence mode="wait">
            {status === 'loading' ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
                className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin"
              />
            ) : status === 'success' ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
              >
                <Check className="w-4 h-4" />
              </motion.div>
            ) : (
              <motion.div
                key="send"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
              >
                <Send className="w-4 h-4" />
              </motion.div>
            )}
          </AnimatePresence>
          <span>{status === 'success' ? 'Subscribed!' : 'Subscribe'}</span>
        </motion.button>
      </motion.div>
      
      {/* Success message */}
      <AnimatePresence>
        {status === 'success' && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute -bottom-6 left-0 text-emerald-400 text-xs flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3" />
            Welcome to the inner circle!
          </motion.p>
        )}
      </AnimatePresence>
    </form>
  )
}

// Animated logo
const AnimatedLogo = () => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      className="flex items-center gap-3 cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <motion.div 
        className="w-10 h-10 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg flex items-center justify-center"
        animate={{ 
          rotate: isHovered ? [0, -10, 10, -5, 5, 0] : 0,
          scale: isHovered ? 1.1 : 1
        }}
        transition={{ duration: 0.5 }}
      >
        <span className="text-black font-bold">Rf</span>
      </motion.div>
      <div className="text-2xl text-white font-light tracking-tight">
        Raptor<motion.span 
          className="italic text-amber-200"
          animate={{ 
            textShadow: isHovered ? '0 0 20px rgba(245, 158, 11, 0.5)' : '0 0 0px rgba(245, 158, 11, 0)' 
          }}
        >
          flow
        </motion.span>
      </div>
    </motion.div>
  )
}

// Main Footer component
const Footer = () => {
  const currentYear = new Date().getFullYear()
  
  const footerLinks = {
    product: [
      { name: 'Features', href: '#features' },
      { name: 'Pricing', href: '#pricing' },
      { name: 'Radar', href: '#radar' },
      { name: 'Cohorts', href: '#cohorts' },
    ],
    company: [
      { name: 'About', href: '/about' },
      { name: 'Blog', href: '/blog' },
      { name: 'Careers', href: '/careers' },
      { name: 'Contact', href: '/contact' },
    ],
    legal: [
      { name: 'Privacy', href: '/privacy' },
      { name: 'Terms', href: '/terms' },
      { name: 'Refunds', href: '/refunds' },
    ]
  }

  return (
    <>
      <ScrollToTop />
      
      <footer className="relative bg-black border-t border-white/5 overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute -top-1/2 left-1/4 w-[600px] h-[600px] bg-gradient-radial from-amber-900/10 via-transparent to-transparent"
            animate={{
              x: [0, 50, 0],
              y: [0, 30, 0],
            }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          />
          <motion.div
            className="absolute -bottom-1/2 right-1/4 w-[400px] h-[400px] bg-gradient-radial from-amber-800/5 via-transparent to-transparent"
            animate={{
              x: [0, -30, 0],
              y: [0, -50, 0],
            }}
            transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
          />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6 py-16">
          {/* Top section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
            {/* Left - Brand & Newsletter */}
            <div className="space-y-8">
              <AnimatedLogo />
              
              <p className="text-white/50 max-w-md leading-relaxed">
                The AI-first marketing operating system for founders who refuse to guess. 
                Build strategy, not spreadsheets.
              </p>
              
              <div className="space-y-3">
                <p className="text-white/70 text-sm font-medium">Join the insider list</p>
                <NewsletterSignup />
              </div>
            </div>

            {/* Right - Links */}
            <div className="grid grid-cols-3 gap-8">
              <div>
                <h4 className="text-white font-medium mb-4">Product</h4>
                <ul className="space-y-3">
                  {footerLinks.product.map((link) => (
                    <li key={link.name}>
                      <MagneticLink href={link.href} className="text-white/40 hover:text-amber-400 text-sm transition-colors">
                        {link.name}
                      </MagneticLink>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="text-white font-medium mb-4">Company</h4>
                <ul className="space-y-3">
                  {footerLinks.company.map((link) => (
                    <li key={link.name}>
                      <MagneticLink href={link.href} className="text-white/40 hover:text-amber-400 text-sm transition-colors">
                        {link.name}
                      </MagneticLink>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="text-white font-medium mb-4">Legal</h4>
                <ul className="space-y-3">
                  {footerLinks.legal.map((link) => (
                    <li key={link.name}>
                      <MagneticLink href={link.href} className="text-white/40 hover:text-amber-400 text-sm transition-colors">
                        {link.name}
                      </MagneticLink>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Middle section - Contact & Social */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 py-8 border-y border-white/5">
            <EmailCopy />
            
            <div className="flex items-center gap-3">
              <SocialLink href="https://twitter.com/raptorflow" icon={Twitter} label="Twitter" />
              <SocialLink href="https://linkedin.com/company/raptorflow" icon={Linkedin} label="LinkedIn" />
            </div>
          </div>

          {/* Bottom section */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8">
            <motion.p 
              className="text-white/30 text-sm flex items-center gap-1"
              whileHover={{ color: 'rgba(255,255,255,0.5)' }}
            >
              © {currentYear} Raptorflow. Made with 
              <motion.span
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              >
                <Heart className="w-3 h-3 text-red-400 fill-red-400 inline mx-1" />
              </motion.span>
              in India.
            </motion.p>
            
            <motion.p 
              className="text-white/20 text-xs"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              Building the future of marketing, one founder at a time.
            </motion.p>
          </div>
        </div>
      </footer>
    </>
  )
}

export default Footer
