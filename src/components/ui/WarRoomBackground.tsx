import React, { useEffect, useRef } from 'react'
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'

export const WarRoomBackground = () => {
    const { scrollY } = useScroll()

    // Parallax the grid slightly against scroll for depth
    const y1 = useTransform(scrollY, [0, 1000], [0, 200])

    return (
        <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden bg-white">
            {/* 1. Base Gradient - Monochrome Depth */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,#f4f4f5_0%,#ffffff_100%)]" />

            {/* 2. The Tactical Grid - Perspective Plane */}
            <motion.div
                className="absolute inset-0 opacity-[0.05]"
                style={{ y: y1 }}
            >
                <div
                    className="absolute inset-0"
                    style={{
                        backgroundImage: `linear-gradient(to right, #000 1px, transparent 1px), linear-gradient(to bottom, #000 1px, transparent 1px)`,
                        backgroundSize: '4rem 4rem',
                        maskImage: 'linear-gradient(to bottom, black 40%, transparent 100%)'
                    }}
                />
            </motion.div>

            {/* 3. Ambient Fog / Noise - Grain for texture */}
            <div className="absolute inset-0 opacity-[0.02] mix-blend-multiply"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
                }}
            />

            {/* 4. Scanning Radar Line - Subtle animation */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-[1px] bg-zinc-900/10 shadow-[0_0_20px_rgba(0,0,0,0.1)] animate-scan-slow" />
            </div>

            {/* 5. Vignette - Focus center */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,white_100%)]" />
        </div>
    )
}
