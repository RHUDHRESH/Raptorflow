import React, { useState, useRef } from 'react'
import { motion, useMotionValue, useSpring, AnimatePresence } from 'framer-motion'
import { EnvelopeSimple, Copy, Check, Clock, TwitterLogo, LinkedinLogo, PaperPlaneTilt } from '@phosphor-icons/react'
import PremiumPageLayout, { GlassCard } from '../components/PremiumPageLayout'

// Magnetic social link with spring physics (like Footer)
const MagneticSocialLink = ({ href, icon: Icon, label }) => {
    const ref = useRef(null)
    const [isHovered, setIsHovered] = useState(false)

    const x = useMotionValue(0)
    const y = useMotionValue(0)

    const springConfig = { damping: 15, stiffness: 200 }
    const xSpring = useSpring(x, springConfig)
    const ySpring = useSpring(y, springConfig)

    const handleMouseMove = (e) => {
        if (!ref.current) return
        const rect = ref.current.getBoundingClientRect()
        const centerX = rect.left + rect.width / 2
        const centerY = rect.top + rect.height / 2
        x.set((e.clientX - centerX) * 0.2)
        y.set((e.clientY - centerY) * 0.2)
    }

    const handleMouseLeave = () => {
        x.set(0)
        y.set(0)
        setIsHovered(false)
    }

    return (
        <motion.a
            ref={ref}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="group relative"
            style={{ x: xSpring, y: ySpring }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
        >
            <GlassCard className="px-6 py-4 flex items-center gap-3">
                <Icon className="w-5 h-5 text-white/50 group-hover:text-amber-400 transition-colors" weight="duotone" />
                <span className="text-white/70 group-hover:text-white transition-colors">{label}</span>
            </GlassCard>

            {/* Tooltip */}
            <AnimatePresence>
                {isHovered && (
                    <motion.span
                        initial={{ opacity: 0, y: 5, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 5, scale: 0.9 }}
                        className="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-white text-black text-xs font-medium rounded-lg whitespace-nowrap pointer-events-none z-20"
                    >
                        Open in new tab
                        <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-white rotate-45" />
                    </motion.span>
                )}
            </AnimatePresence>
        </motion.a>
    )
}

const Contact = () => {
    const [copied, setCopied] = useState(false)
    const email = 'hello@raptorflow.com'

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(email)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        } catch (err) {
            console.error('Failed to copy:', err)
        }
    }

    return (
        <PremiumPageLayout>
            <div className="pt-32 pb-24 min-h-[80vh]">
                <div className="max-w-4xl mx-auto px-6 md:px-12">

                    {/* Hero */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="text-center mb-20"
                    >
                        <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium mb-8">
                            <PaperPlaneTilt weight="fill" className="w-4 h-4" />
                            Contact
                        </span>

                        <h1 className="text-4xl md:text-6xl lg:text-7xl font-light text-white leading-tight mb-8">
                            Let's <span className="italic bg-gradient-to-r from-amber-300 to-amber-400 text-transparent bg-clip-text">talk</span>
                        </h1>

                        <p className="text-xl text-white/50 max-w-xl mx-auto leading-relaxed">
                            Questions about Raptorflow? Want to partner? Just want to say hi?
                            We'd love to hear from you.
                        </p>
                    </motion.div>

                    {/* Email Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                        className="max-w-xl mx-auto mb-16"
                    >
                        <GlassCard className="p-8 md:p-12 relative overflow-hidden">
                            {/* Background glow */}
                            <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-radial from-amber-500/15 to-transparent blur-3xl" />

                            <div className="relative z-10">
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/20 flex items-center justify-center">
                                        <EnvelopeSimple className="w-7 h-7 text-amber-400" weight="duotone" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium text-white">Email us</h3>
                                        <p className="text-white/40 text-sm">Best way to reach us</p>
                                    </div>
                                </div>

                                {/* Large Email Display */}
                                <motion.button
                                    onClick={handleCopy}
                                    className="w-full group relative overflow-hidden text-left"
                                    whileHover={{ scale: 1.01 }}
                                    whileTap={{ scale: 0.99 }}
                                >
                                    <div className="relative flex items-center justify-between p-6 rounded-2xl bg-amber-500/5 border border-amber-500/20 group-hover:border-amber-500/40 group-hover:shadow-[0_0_30px_rgba(245,158,11,0.1)] transition-all duration-300">
                                        <span className="text-2xl md:text-3xl font-light text-white">
                                            {email}
                                        </span>
                                        <AnimatePresence mode="wait">
                                            {copied ? (
                                                <motion.div
                                                    key="check"
                                                    initial={{ scale: 0 }}
                                                    animate={{ scale: 1 }}
                                                    exit={{ scale: 0 }}
                                                    className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center"
                                                >
                                                    <Check className="w-5 h-5 text-emerald-400" weight="bold" />
                                                </motion.div>
                                            ) : (
                                                <motion.div
                                                    key="copy"
                                                    initial={{ scale: 0 }}
                                                    animate={{ scale: 1 }}
                                                    exit={{ scale: 0 }}
                                                    className="w-10 h-10 rounded-xl bg-white/10 group-hover:bg-amber-500/20 border border-white/10 group-hover:border-amber-500/30 flex items-center justify-center transition-all duration-300"
                                                >
                                                    <Copy className="w-5 h-5 text-white/50 group-hover:text-amber-400 transition-colors" weight="duotone" />
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>
                                </motion.button>

                                {/* Response Time */}
                                <div className="flex items-center gap-2 mt-6 text-white/40 text-sm">
                                    <Clock className="w-4 h-4" weight="duotone" />
                                    <span>We typically respond within 24 hours</span>
                                </div>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* Social Links */}
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.3 }}
                        className="text-center"
                    >
                        <p className="text-white/40 mb-6">Or find us on social</p>

                        <div className="flex items-center justify-center gap-4">
                            <MagneticSocialLink
                                href="https://twitter.com/raptorflow"
                                icon={TwitterLogo}
                                label="Twitter"
                            />
                            <MagneticSocialLink
                                href="https://linkedin.com/company/raptorflow"
                                icon={LinkedinLogo}
                                label="LinkedIn"
                            />
                        </div>
                    </motion.div>

                    {/* Support Email */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.8, delay: 0.5 }}
                        className="text-center mt-16 pt-12 border-t border-white/5"
                    >
                        <p className="text-white/30 text-sm flex items-center justify-center gap-2">
                            For support inquiries:{' '}
                            <a href="mailto:support@raptorflow.com" className="text-amber-400 hover:text-amber-300 transition-colors inline-flex items-center gap-1">
                                <EnvelopeSimple weight="duotone" className="w-4 h-4" />
                                support@raptorflow.com
                            </a>
                        </p>
                    </motion.div>
                </div>
            </div>
        </PremiumPageLayout>
    )
}

export default Contact
