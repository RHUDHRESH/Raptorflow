import React, { useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'

const ScrambleText = ({ text, className, scrambleSpeed = 50, revealSpeed = 100 }) => {
  const [displayText, setDisplayText] = useState(text)
  const [isHovering, setIsHovering] = useState(false)
  const intervalRef = useRef(null)
  
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+"

  useEffect(() => {
    if (!isHovering) {
      setDisplayText(text)
      if (intervalRef.current) clearInterval(intervalRef.current)
      return
    }

    let iteration = 0
    
    intervalRef.current = setInterval(() => {
      setDisplayText(prev => 
        text.split("").map((char, index) => {
          if (index < iteration) {
            return text[index]
          }
          return chars[Math.floor(Math.random() * chars.length)]
        }).join("")
      )

      if (iteration >= text.length) {
        clearInterval(intervalRef.current)
      }
      
      iteration += 1/3
    }, 30)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [isHovering, text])

  return (
    <span 
      className={className}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {displayText}
    </span>
  )
}

export default ScrambleText
