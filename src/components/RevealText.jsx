import React, { useState, useEffect, useRef } from 'react'
import { motion, useInView } from 'framer-motion'

const RevealText = ({ text, className, delay = 0 }) => {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-10%" })
  const [displayText, setDisplayText] = useState("")
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+"

  useEffect(() => {
    if (isInView) {
      let iteration = 0
      const interval = setInterval(() => {
        setDisplayText(prev => 
          text.split("").map((char, index) => {
            if (index < iteration) {
              return text[index]
            }
            return chars[Math.floor(Math.random() * chars.length)]
          }).join("")
        )

        if (iteration >= text.length) {
          clearInterval(interval)
        }
        
        iteration += 1/3
      }, 30)
      
      return () => clearInterval(interval)
    }
  }, [isInView, text])

  return (
    <motion.span 
      ref={ref}
      className={className}
      initial={{ opacity: 0 }}
      animate={isInView ? { opacity: 1 } : { opacity: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      {displayText || text.split("").map(() => chars[Math.floor(Math.random() * chars.length)]).join("")}
    </motion.span>
  )
}

export default RevealText
