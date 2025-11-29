import { useState, useRef, useEffect } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'
import { Check, X, GripVertical } from 'lucide-react'
import useReducedMotion from '../hooks/useReducedMotion'

/**
 * Comparison Slider Component
 * Interactive before/after comparison with draggable slider
 * Left side: "The Hamster Wheel" (Negative)
 * Right side: "Actual Marketing" (Positive)
 */
export default function ComparisonSlider() {
    const [sliderPosition, setSliderPosition] = useState(50)
    const [isDragging, setIsDragging] = useState(false)
    const containerRef = useRef(null)
    const prefersReducedMotion = useReducedMotion()

    // Motion value for slider position (0 to 100)
    const x = useMotionValue(50)

    // Handle drag
    const handleDrag = (_, info) => {
        if (!containerRef.current) return
        const width = containerRef.current.offsetWidth
        const newPos = Math.max(0, Math.min(100, (info.point.x / width) * 100))
        x.set(newPos)
        setSliderPosition(newPos)
    }

    // Initial animation to show interactivity
    useEffect(() => {
        if (prefersReducedMotion) return

        const controls = animate(x, [50, 45, 55, 50], {
            duration: 1.5,
            delay: 1,
            ease: "easeInOut"
        })

        return () => controls.stop()
    }, [prefersReducedMotion, x])

    // Sync state with motion value for non-drag updates
    useEffect(() => {
        const unsubscribe = x.on("change", (v) => setSliderPosition(v))
        return () => unsubscribe()
    }, [x])

    const leftItems = [
        { text: 'Post daily', icon: X },
        { text: 'Dance on Reels', icon: X },
        { text: '47 templates', icon: X },
        { text: 'One weird hack', icon: X }
    ]

    const rightItems = [
        { text: 'Real people', icon: Check },
        { text: 'Clear goals', icon: Check },
        { text: 'Finishable work', icon: Check },
        { text: 'Less guilt', icon: Check }
    ]

    return (
        <div
            ref={containerRef}
            className="relative h-[500px] w-full max-w-4xl mx-auto overflow-hidden rounded-2xl border border-white/10 bg-black select-none cursor-ew-resize"
            onMouseMove={(e) => {
                if (!isDragging && containerRef.current) {
                    const rect = containerRef.current.getBoundingClientRect()
                    const newPos = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100))
                    x.set(newPos)
                }
            }}
            onTouchMove={(e) => {
                if (containerRef.current) {
                    const rect = containerRef.current.getBoundingClientRect()
                    const touch = e.touches[0]
                    const newPos = Math.max(0, Math.min(100, ((touch.clientX - rect.left) / rect.width) * 100))
                    x.set(newPos)
                }
            }}
        >
            {/* RIGHT SIDE (Positive - "Actual Marketing") - Background Layer */}
            <div className="absolute inset-0 flex items-center justify-center bg-black">
                <div className="w-full max-w-md px-8 text-center">
                    <h3 className="mb-8 font-serif text-3xl font-bold text-white tracking-tight">
                        ACTUAL MARKETING
                    </h3>
                    <div className="grid gap-6">
                        {rightItems.map((item, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.2 + i * 0.1 }}
                                className="flex items-center gap-4 text-left"
                            >
                                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black">
                                    <item.icon className="h-5 w-5" strokeWidth={3} />
                                </div>
                                <span className="text-xl font-medium text-white">{item.text}</span>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>

            {/* LEFT SIDE (Negative - "The Hamster Wheel") - Overlay Layer */}
            <motion.div
                className="absolute inset-0 overflow-hidden bg-[#111] border-r border-white/20"
                style={{ width: `${sliderPosition}%` }}
            >
                <div className="absolute inset-0 flex items-center justify-center w-full max-w-4xl mx-auto">
                    <div className="w-full max-w-md px-8 text-center opacity-60 grayscale filter blur-[0.5px]">
                        <h3 className="mb-8 font-serif text-3xl font-bold text-white/50 tracking-tight line-through decoration-white/30">
                            THE HAMSTER WHEEL
                        </h3>
                        <div className="grid gap-6">
                            {leftItems.map((item, i) => (
                                <div key={i} className="flex items-center gap-4 text-left">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white/50">
                                        <item.icon className="h-5 w-5" />
                                    </div>
                                    <span className="text-xl font-medium text-white/50 line-through decoration-white/30">{item.text}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </motion.div>

            {/* Slider Handle */}
            <motion.div
                className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize z-20 shadow-[0_0_30px_rgba(255,255,255,0.5)]"
                style={{ left: `${sliderPosition}%` }}
            >
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex h-12 w-12 items-center justify-center rounded-full bg-white text-black shadow-lg">
                    <GripVertical className="h-6 w-6" />
                </div>
            </motion.div>

            {/* Instructions Overlay (fades out) */}
            <motion.div
                initial={{ opacity: 1 }}
                animate={{ opacity: 0 }}
                transition={{ delay: 3, duration: 1 }}
                className="absolute bottom-6 left-1/2 -translate-x-1/2 text-xs font-mono uppercase tracking-widest text-white/50 pointer-events-none"
            >
                Drag to compare
            </motion.div>
        </div>
    )
}
