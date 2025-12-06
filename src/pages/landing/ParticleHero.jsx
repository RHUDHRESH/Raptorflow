import React, { useRef, useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useScroll, useTransform } from 'framer-motion'
import { ArrowRight } from 'lucide-react'

// Optimized particle system - lightweight for performance
const ParticleCanvas = React.memo(({ mousePosition }) => {
  const canvasRef = useRef(null)
  const particlesRef = useRef([])
  const animationRef = useRef(null)
  const lastMouseRef = useRef({ x: null, y: null })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d', { alpha: true })
    // Use lower resolution for performance
    const dpr = Math.min(window.devicePixelRatio || 1, 2)

    const resize = () => {
      canvas.width = window.innerWidth * dpr
      canvas.height = window.innerHeight * dpr
      canvas.style.width = `${window.innerWidth}px`
      canvas.style.height = `${window.innerHeight}px`
      ctx.scale(dpr, dpr)
    }

    resize()
    window.addEventListener('resize', resize)

    // Minimal particles for performance
    const particleCount = 25
    particlesRef.current = Array.from({ length: particleCount }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * 0.15,
      vy: (Math.random() - 0.5) * 0.15,
      radius: Math.random() * 1.5 + 0.5,
      opacity: Math.random() * 0.25 + 0.05,
    }))

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const w = window.innerWidth
      const h = window.innerHeight

      particlesRef.current.forEach((particle) => {
        particle.x += particle.vx
        particle.y += particle.vy

        if (particle.x < 0) particle.x = w
        if (particle.x > w) particle.x = 0
        if (particle.y < 0) particle.y = h
        if (particle.y > h) particle.y = 0

        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(251, 191, 36, ${particle.opacity})`
        ctx.fill()
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animationRef.current)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
      style={{ opacity: 0.3 }}
    />
  )
})

// Premium CTA button
const PremiumButton = ({ children, onClick, primary = true }) => (
  <motion.button
    onClick={onClick}
    whileHover={{ scale: 1.01 }}
    whileTap={{ scale: 0.99 }}
    className={`
      group relative px-10 py-5 font-medium tracking-wide overflow-hidden transition-all duration-500
      ${primary
        ? 'bg-white text-black hover:bg-amber-50'
        : 'text-white/60 hover:text-white'
      }
    `}
  >
    <span className="relative z-10 flex items-center gap-3 text-sm uppercase tracking-[0.1em]">
      {children}
    </span>

    {/* Subtle border glow on hover for primary */}
    {primary && (
      <motion.div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          boxShadow: 'inset 0 0 20px rgba(251, 191, 36, 0.3)'
        }}
      />
    )}
  </motion.button>
)

// Main ParticleHero component - Premium redesign
const ParticleHero = () => {
  const navigate = useNavigate()
  const containerRef = useRef(null)
  const [mousePosition, setMousePosition] = useState({ x: null, y: null })

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 1.05])
  const y = useTransform(scrollYProgress, [0, 0.5], [0, 80])

  const handleMouseMove = useCallback((e) => {
    setMousePosition({ x: e.clientX, y: e.clientY })
  }, [])

  return (
    <section
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setMousePosition({ x: null, y: null })}
      className="relative h-screen overflow-hidden bg-[#030303]"
    >
      {/* Background layers */}
      <motion.div style={{ scale }} className="absolute inset-0">
        {/* Deep gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-black/60 to-black" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/40 via-transparent to-black/40" />

        {/* Subtle radial glow */}
        <div
          className="absolute inset-0"
          style={{
            background: `
              radial-gradient(ellipse 80% 50% at 50% 40%, rgba(251, 191, 36, 0.04) 0%, transparent 60%)
            `
          }}
        />

        {/* Refined particle canvas */}
        <ParticleCanvas mousePosition={mousePosition} />

        {/* Subtle noise texture */}
        <div
          className="absolute inset-0 opacity-[0.015] mix-blend-overlay pointer-events-none"
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
        {/* Minimal eyebrow - refined, not playful */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 1 }}
          className="mb-12"
        >
          <span className="text-[11px] uppercase tracking-[0.5em] text-white/30 font-light">
            AI-Powered Marketing OS
          </span>
        </motion.div>

        {/* Main headline - LARGE and commanding */}
        <div className="text-center max-w-6xl">
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.6, ease: [0.22, 1, 0.36, 1] }}
            className="font-light text-white text-6xl sm:text-7xl md:text-8xl lg:text-[9rem] leading-[0.9] tracking-[-0.03em]"
          >
            Stop guessing.
          </motion.h1>
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.75, ease: [0.22, 1, 0.36, 1] }}
            className="font-light text-6xl sm:text-7xl md:text-8xl lg:text-[9rem] leading-[0.9] tracking-[-0.03em] mt-2"
          >
            <span className="bg-gradient-to-r from-amber-200 via-amber-100 to-amber-200 bg-clip-text text-transparent">
              Start commanding.
            </span>
          </motion.h1>
        </div>

        {/* Subtitle - authoritative, confident */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
          className="mt-10 text-lg md:text-xl text-white/40 font-light text-center max-w-2xl leading-relaxed tracking-wide"
        >
          RaptorFlow transforms your GTM chaos into a precision execution machine.
          <span className="text-white/60"> Clear strategy. Controlled execution. Measurable results.</span>
        </motion.p>

        {/* CTA buttons - refined, confident */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.3 }}
          className="mt-14 flex flex-col sm:flex-row items-center gap-6"
        >
          <PremiumButton onClick={() => navigate('/start')} primary>
            Start Your Spike
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </PremiumButton>

          <PremiumButton onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })} primary={false}>
            See How It Works
          </PremiumButton>
        </motion.div>

        {/* Stats - premium treatment */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.6, duration: 1 }}
          className="mt-20 flex items-center gap-16"
        >
          {[
            { value: '30', label: 'Days to clarity' },
            { value: '6', label: 'Core protocols' },
            { value: '500+', label: 'Founders served' }
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <div className="text-4xl md:text-5xl font-extralight text-white tracking-tight">{stat.value}</div>
              <div className="text-[10px] uppercase tracking-[0.25em] text-white/25 mt-2">{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* Scroll indicator - minimal */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.5 }}
          className="absolute bottom-16 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            className="flex flex-col items-center gap-4"
          >
            <div className="w-px h-16 bg-gradient-to-b from-white/20 to-transparent" />
          </motion.div>
        </motion.div>
      </motion.div>

      {/* Subtle vignette */}
      <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_300px_rgba(0,0,0,0.8)]" />
    </section>
  )
}

export default ParticleHero
