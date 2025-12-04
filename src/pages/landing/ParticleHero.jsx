import React, { useRef, useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion'
import { Play, ArrowRight, Sparkles } from 'lucide-react'

// Particle system with mouse interaction
const ParticleCanvas = ({ mousePosition }) => {
  const canvasRef = useRef(null)
  const particlesRef = useRef([])
  const animationRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1
    
    const resize = () => {
      canvas.width = window.innerWidth * dpr
      canvas.height = window.innerHeight * dpr
      canvas.style.width = `${window.innerWidth}px`
      canvas.style.height = `${window.innerHeight}px`
      ctx.scale(dpr, dpr)
    }
    
    resize()
    window.addEventListener('resize', resize)

    // Initialize particles
    const particleCount = 80
    particlesRef.current = Array.from({ length: particleCount }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      radius: Math.random() * 2 + 0.5,
      opacity: Math.random() * 0.5 + 0.1,
      originalX: 0,
      originalY: 0
    }))

    particlesRef.current.forEach(p => {
      p.originalX = p.x
      p.originalY = p.y
    })

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      particlesRef.current.forEach((particle, i) => {
        // Mouse interaction
        if (mousePosition.x && mousePosition.y) {
          const dx = mousePosition.x - particle.x
          const dy = mousePosition.y - particle.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          const maxDist = 200
          
          if (dist < maxDist) {
            const force = (maxDist - dist) / maxDist
            particle.vx -= (dx / dist) * force * 0.02
            particle.vy -= (dy / dist) * force * 0.02
          }
        }

        // Update position
        particle.x += particle.vx
        particle.y += particle.vy

        // Boundaries with wrap-around
        if (particle.x < 0) particle.x = window.innerWidth
        if (particle.x > window.innerWidth) particle.x = 0
        if (particle.y < 0) particle.y = window.innerHeight
        if (particle.y > window.innerHeight) particle.y = 0

        // Damping
        particle.vx *= 0.99
        particle.vy *= 0.99

        // Draw particle
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(251, 191, 36, ${particle.opacity})`
        ctx.fill()

        // Draw connections
        particlesRef.current.slice(i + 1).forEach(other => {
          const dx = particle.x - other.x
          const dy = particle.y - other.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          
          if (dist < 120) {
            ctx.beginPath()
            ctx.moveTo(particle.x, particle.y)
            ctx.lineTo(other.x, other.y)
            ctx.strokeStyle = `rgba(251, 191, 36, ${0.1 * (1 - dist / 120)})`
            ctx.lineWidth = 0.5
            ctx.stroke()
          }
        })
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationRef.current)
    }
  }, [mousePosition])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
      style={{ opacity: 0.6 }}
    />
  )
}

// Animated text reveal
const AnimatedText = ({ children, delay = 0 }) => (
  <motion.span
    initial={{ opacity: 0, y: 40 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] }}
    className="inline-block"
  >
    {children}
  </motion.span>
)

// Glowing button with pulse effect
const GlowButton = ({ children, onClick, primary = true }) => (
  <motion.button
    onClick={onClick}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 1.2, duration: 0.6 }}
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    className={`
      group relative px-8 py-4 font-medium tracking-wide overflow-hidden transition-all duration-300
      ${primary 
        ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-black' 
        : 'bg-white/5 text-white border border-white/10 hover:border-white/20'
      }
    `}
  >
    {/* Glow effect */}
    {primary && (
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-amber-400/50 to-yellow-400/50 blur-xl"
        animate={{ opacity: [0.5, 0.8, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
    )}
    
    <span className="relative z-10 flex items-center gap-3">
      {children}
    </span>

    {/* Shine effect on hover */}
    <motion.div
      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"
    />
  </motion.button>
)

// Floating badge
const FloatingBadge = () => (
  <motion.div
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.3, duration: 0.8 }}
    className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-full"
  >
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
    >
      <Sparkles className="w-4 h-4 text-amber-400" />
    </motion.div>
    <span className="text-xs font-medium tracking-wide text-white/60">
      AI-Powered GTM Operating System
    </span>
  </motion.div>
)

// Main ParticleHero component
const ParticleHero = () => {
  const navigate = useNavigate()
  const containerRef = useRef(null)
  const [mousePosition, setMousePosition] = useState({ x: null, y: null })
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 1.1])
  const y = useTransform(scrollYProgress, [0, 0.5], [0, 100])

  const handleMouseMove = useCallback((e) => {
    setMousePosition({ x: e.clientX, y: e.clientY })
  }, [])

  return (
    <section 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setMousePosition({ x: null, y: null })}
      className="relative h-screen overflow-hidden bg-black"
    >
      {/* Background layers */}
      <motion.div style={{ scale }} className="absolute inset-0">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/60 to-black" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-transparent to-black/60" />
        
        {/* Radial glow */}
        <div 
          className="absolute inset-0"
          style={{
            background: `
              radial-gradient(circle at 30% 40%, rgba(251, 191, 36, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(245, 158, 11, 0.06) 0%, transparent 50%)
            `
          }}
        />

        {/* Particle canvas */}
        <ParticleCanvas mousePosition={mousePosition} />

        {/* Grain texture */}
        <div 
          className="absolute inset-0 opacity-[0.02] mix-blend-overlay pointer-events-none"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
          }}
        />
      </motion.div>

      {/* Content */}
      <motion.div 
        style={{ opacity, y }}
        className="relative z-10 h-full flex flex-col items-center justify-center px-6"
      >
        {/* Floating badge */}
        <FloatingBadge />

        {/* Main headline */}
        <div className="text-center max-w-5xl mt-8">
          <h1 className="font-light text-white text-5xl sm:text-6xl md:text-7xl lg:text-8xl leading-[0.95] tracking-tight">
            <AnimatedText delay={0.5}>Stop guessing.</AnimatedText>
            <br />
            <AnimatedText delay={0.7}>
              <span className="italic font-normal bg-gradient-to-r from-amber-200 via-yellow-100 to-amber-200 bg-clip-text text-transparent">
                Start commanding.
              </span>
            </AnimatedText>
          </h1>
        </div>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
          className="mt-8 text-lg md:text-xl text-white/50 font-light text-center max-w-2xl leading-relaxed"
        >
          RaptorFlow transforms your GTM chaos into a{' '}
          <span className="text-white/70">precision execution machine</span>.{' '}
          Clear strategy. Controlled execution. Measurable results.
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-12 flex flex-col sm:flex-row items-center gap-4"
        >
          <GlowButton onClick={() => navigate('/start')} primary>
            <Play className="w-4 h-4 fill-current" />
            Start Your Spike
          </GlowButton>

          <GlowButton onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })} primary={false}>
            See How It Works
            <ArrowRight className="w-4 h-4" />
          </GlowButton>
        </motion.div>

        {/* Stats preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5, duration: 0.8 }}
          className="mt-16 flex items-center gap-8 text-center"
        >
          {[
            { value: '30', label: 'Days to Clarity' },
            { value: '6', label: 'Core Protocols' },
            { value: '1', label: 'Command Center' }
          ].map((stat, i) => (
            <div key={i} className="px-6">
              <div className="text-3xl font-light text-white">{stat.value}</div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-white/30 mt-1">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
          className="absolute bottom-12 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className="flex flex-col items-center gap-4"
          >
            <span className="text-[10px] uppercase tracking-[0.3em] text-white/30">
              Scroll to explore
            </span>
            <div className="w-px h-12 bg-gradient-to-b from-white/30 to-transparent" />
          </motion.div>
        </motion.div>
      </motion.div>

      {/* Vignette overlay */}
      <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_200px_rgba(0,0,0,0.9)]" />
    </section>
  )
}

export default ParticleHero

