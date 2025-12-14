import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import { ReactLenis } from 'lenis/react'
import Header from '../pages/landing/Header'
import Footer from '../pages/landing/Footer'
import CustomCursor from './CustomCursor'

// Floating orbs background - creates depth and premium feel
const FloatingOrbs = () => {
    const orbs = useMemo(() => [
        { size: 400, x: '15%', y: '25%', duration: 25, delay: 0, color: 'from-amber-500/8 to-orange-600/5' },
        { size: 250, x: '75%', y: '55%', duration: 20, delay: 5, color: 'from-amber-400/6 to-yellow-500/4' },
        { size: 350, x: '55%', y: '75%', duration: 30, delay: 10, color: 'from-orange-500/5 to-amber-600/3' },
    ], [])

    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
            {orbs.map((orb, i) => (
                <motion.div
                    key={i}
                    className={`absolute rounded-full bg-gradient-radial ${orb.color} blur-3xl`}
                    style={{
                        width: orb.size,
                        height: orb.size,
                        left: orb.x,
                        top: orb.y,
                        transform: 'translate(-50%, -50%)',
                    }}
                    animate={{
                        x: [0, 40, -30, 0],
                        y: [0, -30, 25, 0],
                        scale: [1, 1.1, 0.95, 1],
                    }}
                    transition={{
                        duration: orb.duration,
                        repeat: Infinity,
                        ease: 'easeInOut',
                        delay: orb.delay,
                    }}
                />
            ))}
        </div>
    )
}

// Noise texture overlay for premium film-grain effect
const NoiseOverlay = () => (
    <div
        className="fixed inset-0 opacity-[0.015] pointer-events-none mix-blend-overlay z-[1]"
        style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
        }}
    />
)

// Glass card component for premium sections
export const GlassCard = ({ children, className = '', hover = true }) => (
    <div className={`relative rounded-2xl bg-white/[0.02] backdrop-blur-xl border border-white/[0.05] ${hover ? 'hover:border-amber-500/20 transition-all duration-500' : ''} ${className}`}>
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/[0.03] to-transparent pointer-events-none" />
        <div className="relative z-10">{children}</div>
    </div>
)

// Premium Page Layout wrapper
const PremiumPageLayout = ({
    children,
    showOrbs = true,
    showNoise = true,
    className = ''
}) => {
    return (
        <ReactLenis root>
            <div className={`min-h-screen bg-[#0a0a0a] antialiased font-sans selection:bg-amber-500/30 relative ${className}`}>
                <CustomCursor />
                <Header />

                {/* Background effects */}
                {showOrbs && <FloatingOrbs />}
                {showNoise && <NoiseOverlay />}

                {/* Main Content */}
                <main className="relative z-10">
                    {children}
                </main>

                <Footer />
            </div>
        </ReactLenis>
    )
}

export default PremiumPageLayout
