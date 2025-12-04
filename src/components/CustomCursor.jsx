import React, { useEffect, useState } from 'react'
import { motion, useSpring } from 'framer-motion'

const CustomCursor = () => {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isHovering, setIsHovering] = useState(false)
  const [isClicking, setIsClicking] = useState(false)
  const [cursorText, setCursorText] = useState('')

  const cursorX = useSpring(position.x, { stiffness: 500, damping: 28, mass: 0.5 })
  const cursorY = useSpring(position.y, { stiffness: 500, damping: 28, mass: 0.5 })

  const dotX = useSpring(position.x, { stiffness: 2000, damping: 50, mass: 0.1 })
  const dotY = useSpring(position.y, { stiffness: 2000, damping: 50, mass: 0.1 })

  useEffect(() => {
    const updatePosition = (e) => {
      setPosition({ x: e.clientX, y: e.clientY })
    }

    const handleMouseDown = () => setIsClicking(true)
    const handleMouseUp = () => setIsClicking(false)

    const handleMouseOver = (e) => {
      const target = e.target.closest('a, button, input, textarea, [role="button"], [data-cursor]')
      if (target) {
        setIsHovering(true)
        setCursorText(target.dataset?.cursor || '')
      } else {
        setIsHovering(false)
        setCursorText('')
      }
    }

    window.addEventListener('mousemove', updatePosition)
    window.addEventListener('mousedown', handleMouseDown)
    window.addEventListener('mouseup', handleMouseUp)
    window.addEventListener('mouseover', handleMouseOver)

    return () => {
      window.removeEventListener('mousemove', updatePosition)
      window.removeEventListener('mousedown', handleMouseDown)
      window.removeEventListener('mouseup', handleMouseUp)
      window.removeEventListener('mouseover', handleMouseOver)
    }
  }, [])

  return (
    <>
      {/* Outer ring */}
      <motion.div
        className="fixed top-0 left-0 pointer-events-none z-[9998] hidden md:flex items-center justify-center"
        style={{ 
          x: cursorX, 
          y: cursorY,
          translateX: '-50%',
          translateY: '-50%',
        }}
        animate={{
          width: isHovering ? 80 : 40,
          height: isHovering ? 80 : 40,
          borderColor: isHovering ? 'rgba(201, 169, 98, 0.5)' : 'rgba(10, 10, 10, 0.2)',
        }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      >
        <div 
          className="w-full h-full rounded-full border transition-colors duration-300"
          style={{
            borderColor: 'inherit',
            transform: isClicking ? 'scale(0.9)' : 'scale(1)',
            transition: 'transform 0.15s ease'
          }}
        />
        
        {/* Cursor text */}
        {cursorText && (
          <motion.span
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute text-[8px] uppercase tracking-widest text-noir font-medium"
          >
            {cursorText}
          </motion.span>
        )}
      </motion.div>

      {/* Center dot */}
      <motion.div
        className="fixed top-0 left-0 w-1 h-1 rounded-full pointer-events-none z-[9999] hidden md:block"
        style={{ 
          x: dotX, 
          y: dotY,
          translateX: '-50%',
          translateY: '-50%',
        }}
        animate={{
          backgroundColor: isHovering ? '#C9A962' : '#0A0A0A',
          scale: isClicking ? 2 : 1,
        }}
        transition={{ duration: 0.2 }}
      />
    </>
  )
}

export default CustomCursor
