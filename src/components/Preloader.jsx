import React, { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const Preloader = ({ onComplete }) => {
  const [progress, setProgress] = useState(0)
  const [phase, setPhase] = useState('loading') // loading, complete
  const onCompleteRef = useRef(onComplete)
  const hasCompletedRef = useRef(false)

  // Keep the ref updated
  useEffect(() => {
    onCompleteRef.current = onComplete
  }, [onComplete])

  useEffect(() => {
    const duration = 2000  // 2 second animation
    const interval = 30
    const steps = duration / interval
    const increment = 100 / steps

    let current = 0

    const complete = () => {
      if (hasCompletedRef.current) return
      hasCompletedRef.current = true
      setProgress(100)
      setPhase('complete')
      setTimeout(() => onCompleteRef.current?.(), 600)
    }

    const timer = setInterval(() => {
      current += increment
      if (current >= 100) {
        clearInterval(timer)
        complete()
      } else {
        setProgress(current)
      }
    }, interval)

    // Safety timeout - always complete after 3 seconds max
    const safetyTimeout = setTimeout(() => {
      clearInterval(timer)
      complete()
    }, 3000)

    return () => {
      clearInterval(timer)
      clearTimeout(safetyTimeout)
    }
  }, []) // Empty dependency array - run only once

  return (
    <AnimatePresence>
      {phase !== 'done' && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="fixed inset-0 z-[100] bg-black flex items-center justify-center"
        >
          {/* Background grain */}
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
            }}
          />

          {/* Center content */}
          <div className="relative flex flex-col items-center">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="mb-12"
            >
              <span className="text-white text-3xl tracking-tight font-light">
                Raptor<span className="italic font-normal text-amber-200">flow</span>
              </span>
            </motion.div>

            {/* Progress bar container */}
            <div className="relative w-48">
              {/* Track */}
              <div className="h-px bg-white/10" />

              {/* Fill */}
              <motion.div
                className="absolute top-0 left-0 h-px bg-gradient-to-r from-amber-400 to-amber-200"
                style={{ width: `${progress}%` }}
                transition={{ duration: 0.05 }}
              />
            </div>

            {/* Percentage */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-6"
            >
              <span className="font-mono text-xs text-white/30 tracking-widest">
                {Math.round(progress)}%
              </span>
            </motion.div>
          </div>

          {/* Corner accents */}
          <div className="absolute top-8 left-8 w-8 h-8 border-l border-t border-white/10" />
          <div className="absolute top-8 right-8 w-8 h-8 border-r border-t border-white/10" />
          <div className="absolute bottom-8 left-8 w-8 h-8 border-l border-b border-white/10" />
          <div className="absolute bottom-8 right-8 w-8 h-8 border-r border-b border-white/10" />
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default Preloader
