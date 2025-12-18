import React, { useRef, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useScroll, useTransform, useSpring, useMotionValue } from 'framer-motion'
import { ArrowRight } from 'lucide-react'

/* ═══════════════════════════════════════════════════════════════════════════
   SPECTACULAR HERO - RAPTORFLOW DESIGN SYSTEM
   Tokens: paper, ink, zinc palette
   ═══════════════════════════════════════════════════════════════════════════ */

// Typewriter phrases
const phrases = [
  'Start commanding.',
  'Start winning.',
  'Start scaling.',
  'Start dominating.'
]

// Floating 3D polyhedron component
const FloatingShape = ({ delay = 0, size = 60, position, depth = 1 }) => {
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 40 * depth
      const y = (e.clientY / window.innerHeight - 0.5) * 40 * depth
      mouseX.set(x)
      mouseY.set(y)
    }
    window.addEventListener('mousemove', handleMouse)
    return () => window.removeEventListener('mousemove', handleMouse)
  }, [depth])

  const springX = useSpring(mouseX, { stiffness: 50, damping: 20 })
  const springY = useSpring(mouseY, { stiffness: 50, damping: 20 })

  return (
    <motion.div
      className="absolute pointer-events-none"
      style={{ left: position.x, top: position.y, x: springX, y: springY }}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 1, ease: [0.22, 1, 0.36, 1] }}
    >
      {/* Glow behind shape */}
      <div
        className="absolute rounded-full"
        style={{
          width: size * 1.5,
          height: size * 1.5,
          left: -size * 0.25,
          top: -size * 0.25,
          background: 'radial-gradient(circle, rgba(255,177,98,0.4) 0%, transparent 60%)',
          filter: 'blur(10px)'
        }}
      />
      <motion.svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        animate={{ rotateY: [0, 360] }}
        transition={{ duration: 15 + delay * 3, repeat: Infinity, ease: "linear" }}
      >
        <defs>
          <linearGradient id={`grad-${delay}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFB162" stopOpacity="0.9" />
            <stop offset="50%" stopColor="#FFC48A" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#E89A4A" stopOpacity="0.8" />
          </linearGradient>
          <filter id={`glow-${delay}`}>
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <polygon
          points="50,5 95,30 80,85 20,85 5,30"
          fill={`url(#grad-${delay})`}
          stroke="#FFB162"
          strokeWidth="2"
          filter={`url(#glow-${delay})`}
        />
        <polygon
          points="50,15 85,35 72,75 28,75 15,35"
          fill="none"
          stroke="#FFD194"
          strokeWidth="1.5"
          strokeOpacity="0.8"
        />
        {/* Inner highlight */}
        <polygon
          points="50,25 75,38 65,65 35,65 25,38"
          fill="rgba(255,255,255,0.1)"
          stroke="#FFFFFF"
          strokeWidth="0.5"
          strokeOpacity="0.3"
        />
      </motion.svg>
    </motion.div>
  )
}

const ParticleHero = () => {
  const navigate = useNavigate()
  const containerRef = useRef<HTMLElement>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [currentPhrase, setCurrentPhrase] = useState(0)
  const [displayText, setDisplayText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)

  // Mouse tracking for 3D parallax
  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      setMousePos({
        x: (e.clientX / window.innerWidth - 0.5) * 2,
        y: (e.clientY / window.innerHeight - 0.5) * 2
      })
    }
    window.addEventListener('mousemove', handleMouse)
    return () => window.removeEventListener('mousemove', handleMouse)
  }, [])

  // Typewriter effect
  useEffect(() => {
    const phrase = phrases[currentPhrase]
    const speed = isDeleting ? 50 : 100

    const timer = setTimeout(() => {
      if (!isDeleting && displayText.length < phrase.length) {
        setDisplayText(phrase.slice(0, displayText.length + 1))
      } else if (!isDeleting && displayText.length === phrase.length) {
        setTimeout(() => setIsDeleting(true), 2000)
      } else if (isDeleting && displayText.length > 0) {
        setDisplayText(displayText.slice(0, -1))
      } else if (isDeleting && displayText.length === 0) {
        setIsDeleting(false)
        setCurrentPhrase((prev) => (prev + 1) % phrases.length)
      }
    }, speed)

    return () => clearTimeout(timer)
  }, [displayText, isDeleting, currentPhrase])

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const y = useTransform(scrollYProgress, [0, 0.5], [0, 80])

  // 3D transform values based on mouse
  const rotateX = mousePos.y * -5
  const rotateY = mousePos.x * 5
  const translateZ = 20

  return (
    <section
      ref={containerRef}
      className="relative min-h-screen flex flex-col items-center justify-center px-6 overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #EEE9DF 0%, #E5DFD3 50%, #EEE9DF 100%)' }}
    >
      {/* SVG Filter for Morphing Blobs */}
      <svg className="hidden">
        <defs>
          <filter id="goo">
            <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
            <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo" />
          </filter>
        </defs>
      </svg>

      {/* Morphing Blob Background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden" style={{ filter: 'url(#goo)' }}>
        <motion.div
          className="absolute w-[500px] h-[500px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(255,177,98,0.15) 0%, transparent 70%)', left: '20%', top: '20%' }}
          animate={{
            x: [0, 100, 50, 0],
            y: [0, -50, 100, 0],
            scale: [1, 1.2, 0.9, 1]
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute w-[600px] h-[600px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(44,59,77,0.08) 0%, transparent 70%)', right: '10%', top: '30%' }}
          animate={{
            x: [0, -80, 30, 0],
            y: [0, 80, -40, 0],
            scale: [1, 0.8, 1.1, 1]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut", delay: 5 }}
        />
        <motion.div
          className="absolute w-[400px] h-[400px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(201,193,177,0.2) 0%, transparent 70%)', left: '50%', bottom: '10%' }}
          animate={{
            x: [0, 60, -60, 0],
            y: [0, -60, 60, 0],
            scale: [1, 1.3, 0.95, 1]
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut", delay: 8 }}
        />
      </div>

      {/* Animated Floating Particles */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 rounded-full"
            style={{
              background: i % 3 === 0 ? '#FFB162' : i % 3 === 1 ? '#2C3B4D' : '#C9C1B1',
              opacity: 0.4 + Math.random() * 0.4,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30 - Math.random() * 50, 0],
              x: [0, (Math.random() - 0.5) * 40, 0],
              opacity: [0.3, 0.7, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 4 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 3,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      {/* Floating 3D Polyhedrons - NOW BIGGER */}
      <FloatingShape delay={0.3} size={120} position={{ x: '8%', y: '12%' }} depth={1.5} />
      <FloatingShape delay={0.8} size={90} position={{ x: '88%', y: '18%' }} depth={0.8} />
      <FloatingShape delay={1.2} size={100} position={{ x: '78%', y: '68%' }} depth={1.2} />
      <FloatingShape delay={1.6} size={70} position={{ x: '12%', y: '72%' }} depth={1} />
      <FloatingShape delay={0.5} size={50} position={{ x: '50%', y: '8%' }} depth={0.6} />
      <FloatingShape delay={1.8} size={60} position={{ x: '45%', y: '85%' }} depth={0.9} />

      {/* Noise texture overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Grid overlay - slightly more visible */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(44,59,77,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(44,59,77,0.05)_1px,transparent_1px)] bg-[size:50px_50px] pointer-events-none" />

      {/* Content */}
      <motion.div
        style={{
          opacity,
          y,
          perspective: 1000,
        }}
        className="relative z-10 flex flex-col items-center justify-center text-center max-w-5xl"
      >
        {/* Eyebrow */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="text-xs uppercase tracking-[0.3em] text-blueFantastic-muted mb-8 font-medium"
        >
          AI-Powered Marketing OS
        </motion.p>

        {/* 3D Parallax Headlines */}
        <motion.div
          style={{
            transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(${translateZ}px)`,
            transformStyle: 'preserve-3d'
          }}
          className="transition-transform duration-100 ease-out"
        >
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="font-display text-5xl sm:text-6xl md:text-7xl lg:text-8xl leading-[0.95] mb-4"
            style={{ color: '#2C3B4D', textShadow: '0 4px 30px rgba(44,59,77,0.1)' }}
          >
            Stop guessing.
          </motion.h1>
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
            className="font-display italic text-5xl sm:text-6xl md:text-7xl lg:text-8xl leading-[0.95]"
            style={{ color: '#FFB162', textShadow: '0 4px 40px rgba(255,177,98,0.3)' }}
          >
            {displayText}
            <motion.span
              animate={{ opacity: [1, 0] }}
              transition={{ duration: 0.5, repeat: Infinity }}
              className="inline-block w-[4px] h-[0.8em] bg-burningFlame ml-2 align-middle"
            />
          </motion.h1>
        </motion.div>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="mt-10 text-lg md:text-xl max-w-2xl leading-relaxed"
          style={{ color: '#6B7A8C' }}
        >
          RaptorFlow transforms your GTM chaos into a precision execution machine.
          <span style={{ color: '#2C3B4D' }}> Clear strategy. Controlled execution. Measurable results.</span>
        </motion.p>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <motion.button
            onClick={() => navigate('/start')}
            className="group relative flex items-center justify-center gap-3 px-8 py-4 rounded-xl text-sm font-medium overflow-hidden"
            style={{ background: '#FFB162', color: '#2C3B4D', minWidth: '200px' }}
            whileHover={{ scale: 1.02, boxShadow: '0 8px 30px rgba(255,177,98,0.4)' }}
            whileTap={{ scale: 0.98 }}
          >
            {/* Shimmer effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -skew-x-12"
              animate={{ x: ['-200%', '200%'] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3, ease: "easeInOut" }}
            />
            {/* Rocket with particle trail on hover */}
            <span className="relative z-10 flex items-center gap-2">
              Start Free
              <motion.span
                className="inline-block"
                whileHover={{ x: [0, 2, 0], y: [0, -2, 0] }}
                transition={{ duration: 0.3, repeat: Infinity }}
              >
                🚀
              </motion.span>
            </span>
            {/* Particle trail on hover */}
            <motion.div
              className="absolute right-12 top-1/2 -translate-y-1/2 pointer-events-none opacity-0 group-hover:opacity-100"
              initial={{ opacity: 0 }}
            >
              {[...Array(5)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1.5 h-1.5 rounded-full bg-white/60"
                  style={{ right: i * 6, top: (i % 2 === 0 ? -2 : 2) }}
                  animate={{
                    opacity: [0.8, 0],
                    scale: [1, 0.5],
                    x: [-10 * i, -20 * i],
                  }}
                  transition={{
                    duration: 0.6,
                    repeat: Infinity,
                    delay: i * 0.1,
                  }}
                />
              ))}
            </motion.div>
          </motion.button>

          <button
            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
            className="px-8 py-4 text-sm font-medium transition-colors"
            style={{ color: '#6B7A8C' }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#2C3B4D'}
            onMouseLeave={(e) => e.currentTarget.style.color = '#6B7A8C'}
          >
            See How It Works
          </button>
        </motion.div>

        {/* Animated Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1, duration: 0.8 }}
          className="mt-20 flex items-center gap-12 md:gap-16"
        >
          {[
            { value: '90', label: 'Day war plan' },
            { value: '3x', label: 'Faster execution' },
            { value: '∞', label: 'Clarity unlocked' }
          ].map((stat, i) => (
            <motion.div
              key={i}
              className="text-center"
              whileHover={{ scale: 1.05, y: -5 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <div
                className="text-4xl md:text-5xl font-light tracking-tight"
                style={{ color: '#2C3B4D' }}
              >
                {stat.value}
              </div>
              <div className="text-xs uppercase tracking-widest mt-2" style={{ color: '#6B7A8C' }}>{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-12 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          <div className="w-px h-16 bg-gradient-to-b from-oatmeal to-transparent" />
        </motion.div>
      </motion.div>
    </section>
  )
}

export default ParticleHero

