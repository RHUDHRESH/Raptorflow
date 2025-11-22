import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "../../utils/cn"

const TooltipProvider = ({ children }) => {
  return <>{children}</>
}

const Tooltip = ({ children, content, delay = 200 }) => {
  const [open, setOpen] = React.useState(false)
  const timeoutRef = React.useRef(null)

  const handleMouseEnter = () => {
    timeoutRef.current = setTimeout(() => {
      setOpen(true)
    }, delay)
  }

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setOpen(false)
  }

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return (
    <div
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      <AnimatePresence>
        {open && content && (
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            transition={{ duration: 0.18, ease: [0.4, 0, 0.2, 1] }}
            className="absolute left-full ml-2 z-50 px-3 py-1.5 bg-black text-white text-xs font-medium whitespace-nowrap rounded shadow-lg pointer-events-none"
            style={{
              top: "50%",
              transform: "translateY(-50%)",
            }}
          >
            {content}
            <div
              className="absolute right-full top-1/2 -translate-y-1/2 w-0 h-0 border-t-4 border-b-4 border-r-4 border-transparent border-r-black"
              style={{ marginRight: "-1px" }}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export { Tooltip, TooltipProvider }
