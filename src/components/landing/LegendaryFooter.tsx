import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Check, Copy, Heart, Github, Twitter, Linkedin, Mail, ExternalLink, Rocket, Coffee, Music, ChevronUp } from 'lucide-react'
import { motion, AnimatePresence, useMotionValue, useSpring, useReducedMotion } from 'framer-motion'
import { RaptorFlowLogo } from '@/components/brand/Logo'
import { cn } from '@/lib/utils'

// ═══════════════════════════════════════════════════════════════════════════════
// LEGENDARY FOOTER - Extracted from LandingPage.tsx
// ═══════════════════════════════════════════════════════════════════════════════

// Live momentum counter - shows "activity" to create FOMO
const MomentumCounter = () => {
    const [stats, setStats] = useState({
        movesThisWeek: 1247,
        contentGenerated: 3891,
        testsWon: 127
    })

    useEffect(() => {
        const interval = setInterval(() => {
            setStats(prev => ({
                movesThisWeek: prev.movesThisWeek + Math.floor(Math.random() * 3),
                contentGenerated: prev.contentGenerated + Math.floor(Math.random() * 5),
                testsWon: prev.testsWon + (Math.random() > 0.85 ? 1 : 0)
            }))
        }, 3000)
        return () => clearInterval(interval)
    }, [])

    // Custom inline icons
    const icons = {
        launch: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-primary">
                <path d="M12 2C16 4 18 8 18 12C18 16 16 20 12 22C8 20 6 16 6 12C6 8 8 4 12 2Z" stroke="currentColor" strokeWidth="1.5" fill="currentColor" fillOpacity="0.1" />
                <circle cx="12" cy="10" r="2" fill="currentColor" />
            </svg>
        ),
        magic: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-primary">
                <path d="M12 2L13.5 8L20 8.5L14.5 12L16 19L12 14.5L8 19L9.5 12L4 8.5L10.5 8L12 2Z" fill="currentColor" fillOpacity="0.15" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
            </svg>
        ),
        winner: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-primary">
                <path d="M6 4H18V8C18 12.4183 14.4183 16 10 16H14C14 16 12 20 12 22" stroke="currentColor" strokeWidth="1.5" />
                <path d="M9 22H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                <path d="M12 8L12.5 10H14L13 11L13.5 13L12 12L10.5 13L11 11L10 10H11.5L12 8Z" fill="currentColor" />
            </svg>
        )
    }

    return (
        <motion.div
            className="grid grid-cols-3 gap-4 p-4 rounded-2xl bg-gradient-to-br from-primary/5 via-primary/10 to-primary/5 border border-primary/20"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
        >
            {[
                { value: stats.movesThisWeek, label: 'Moves shipped', icon: icons.launch },
                { value: stats.contentGenerated, label: 'AI generations', icon: icons.magic },
                { value: stats.testsWon, label: 'A/B tests won', icon: icons.winner }
            ].map((stat) => (
                <motion.div
                    key={stat.label}
                    className="text-center group cursor-default"
                    whileHover={{ scale: 1.05 }}
                >
                    <motion.div
                        className="text-2xl md:text-3xl font-mono font-bold text-foreground"
                        key={stat.value}
                        initial={{ scale: 1.2, color: 'hsl(var(--primary))' }}
                        animate={{ scale: 1, color: 'hsl(var(--foreground))' }}
                        transition={{ duration: 0.3 }}
                    >
                        {stat.value.toLocaleString()}
                    </motion.div>
                    <div className="text-xs text-muted-foreground flex items-center justify-center gap-1 mt-1">
                        <span className="group-hover:scale-110 transition-transform">{stat.icon}</span>
                        {stat.label}
                    </div>
                </motion.div>
            ))}
        </motion.div>
    )
}

// Magnetic social button with gravity effect
const MagneticButton = ({ href, icon: Icon, label, color }: { href: string, icon: React.ComponentType<{ className?: string }>, label: string, color: string }) => {
    const buttonRef = useRef<HTMLAnchorElement>(null)
    const [isHovered, setIsHovered] = useState(false)

    const x = useMotionValue(0)
    const y = useMotionValue(0)

    const springConfig = { damping: 15, stiffness: 150 }
    const xSpring = useSpring(x, springConfig)
    const ySpring = useSpring(y, springConfig)

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!buttonRef.current) return
        const rect = buttonRef.current.getBoundingClientRect()
        const centerX = rect.left + rect.width / 2
        const centerY = rect.top + rect.height / 2
        x.set((e.clientX - centerX) * 0.3)
        y.set((e.clientY - centerY) * 0.3)
    }

    const handleMouseLeave = () => {
        x.set(0)
        y.set(0)
        setIsHovered(false)
    }

    return (
        <motion.a
            ref={buttonRef}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={label}
            className="relative group min-w-[44px] min-h-[44px] flex items-center justify-center"
            style={{ x: xSpring, y: ySpring }}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={handleMouseLeave}
        >
            <motion.div
                className={cn(
                    "w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 border",
                    isHovered ? `bg-gradient-to-br ${color} border-white/20 shadow-xl` : "bg-muted/50 border-border"
                )}
                whileHover={{ scale: 1.15, rotate: 5 }}
                whileTap={{ scale: 0.9, rotate: -5 }}
            >
                <Icon className={cn("w-6 h-6 transition-colors", isHovered ? "text-white" : "text-muted-foreground")} aria-hidden="true" />
                <span className="sr-only">{label}</span>
            </motion.div>

            {/* Tooltip */}
            <AnimatePresence>
                {isHovered && (
                    <motion.span
                        initial={{ opacity: 0, y: 10, scale: 0.8 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 5, scale: 0.9 }}
                        className="absolute -top-12 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-foreground text-background text-xs font-medium rounded-lg whitespace-nowrap pointer-events-none"
                    >
                        {label}
                        <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-foreground rotate-45" />
                    </motion.span>
                )}
            </AnimatePresence>
        </motion.a>
    )
}

// Interactive email with copy functionality
const CopyableEmail = () => {
    const [copied, setCopied] = useState(false)
    const [isHovered, setIsHovered] = useState(false)
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
        <motion.button
            onClick={handleCopy}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            aria-label={copied ? 'Email copied to clipboard' : 'Copy email address to clipboard'}
            className={cn(
                "group flex items-center gap-3 px-5 py-3 min-h-[44px] rounded-xl border transition-all duration-300",
                copied ? "bg-primary/20 border-primary/40" : "bg-muted/50 border-border hover:border-primary/30"
            )}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
        >
            <Mail className={cn("w-5 h-5 transition-colors", copied ? "text-primary" : "text-muted-foreground")} />
            <span className={cn("font-mono text-sm transition-colors", copied ? "text-primary" : "text-muted-foreground group-hover:text-foreground")}>
                {email}
            </span>
            <AnimatePresence mode="wait">
                {copied ? (
                    <motion.div
                        key="check"
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        exit={{ scale: 0, rotate: 180 }}
                        className="ml-auto"
                    >
                        <Check className="w-4 h-4 text-primary" />
                    </motion.div>
                ) : (
                    <motion.div
                        key="copy"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                        className="ml-auto"
                    >
                        <Copy className={cn("w-4 h-4 transition-colors", isHovered ? "text-primary" : "text-muted-foreground/50")} />
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.button>
    )
}

// Animated footer link with hover underline
const FooterLink = ({ href, children, external = false }: { href: string, children: React.ReactNode, external?: boolean }) => {
    const [isHovered, setIsHovered] = useState(false)

    const LinkComponent = external ? 'a' : Link
    const linkProps = external ? { href, target: '_blank', rel: 'noopener noreferrer' } : { to: href }

    return (
        <motion.div
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            whileHover={{ x: 6 }}
            transition={{ type: "spring", stiffness: 400, damping: 20 }}
        >
            <LinkComponent
                {...linkProps as any}
                className="group relative inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
                <motion.span
                    className="absolute -left-3 w-1.5 h-1.5 rounded-full bg-primary"
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: isHovered ? 1 : 0, opacity: isHovered ? 1 : 0 }}
                    transition={{ duration: 0.2 }}
                />
                {children}
                {external && (
                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
            </LinkComponent>
        </motion.div>
    )
}

// Easter egg: Konami code detector
const useKonamiCode = (callback: () => void) => {
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA']
    const [position, setPosition] = useState(0)

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.code === konamiCode[position]) {
                if (position === konamiCode.length - 1) {
                    callback()
                    setPosition(0)
                } else {
                    setPosition(position + 1)
                }
            } else {
                setPosition(0)
            }
        }

        window.addEventListener('keydown', handleKeyDown)
        return () => window.removeEventListener('keydown', handleKeyDown)
    }, [position, callback])
}

// Interactive scroll progress indicator - Performance optimized
const ScrollProgress = () => {
    const [progress, setProgress] = useState(0)
    const prefersReducedMotion = useReducedMotion()
    const docHeightRef = useRef(0)
    const rafRef = useRef<number>()

    useEffect(() => {
        // Cache document height on mount and resize
        const updateDocHeight = () => {
            docHeightRef.current = document.documentElement.scrollHeight - window.innerHeight
        }
        updateDocHeight()
        window.addEventListener('resize', updateDocHeight)

        // Throttled scroll handler with RAF
        const handleScroll = () => {
            if (rafRef.current) return
            rafRef.current = requestAnimationFrame(() => {
                const scrollTop = window.scrollY
                if (docHeightRef.current > 0) {
                    setProgress(scrollTop / docHeightRef.current)
                }
                rafRef.current = undefined
            })
        }

        window.addEventListener('scroll', handleScroll, { passive: true })
        return () => {
            window.removeEventListener('scroll', handleScroll)
            window.removeEventListener('resize', updateDocHeight)
            if (rafRef.current) cancelAnimationFrame(rafRef.current)
        }
    }, [])

    return (
        <motion.div
            className="fixed bottom-8 right-8 z-50"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: progress > 0.1 ? 1 : 0, opacity: progress > 0.1 ? 1 : 0 }}
        >
            <motion.button
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                aria-label="Scroll to top of page"
                className="w-14 h-14 rounded-full bg-card/90 backdrop-blur-sm md:backdrop-blur-xl border border-border flex items-center justify-center shadow-2xl group"
                whileHover={prefersReducedMotion ? undefined : { scale: 1.1 }}
                whileTap={prefersReducedMotion ? undefined : { scale: 0.9 }}
            >
                <svg className="absolute inset-0 w-full h-full -rotate-90">
                    <circle
                        cx="28"
                        cy="28"
                        r="24"
                        fill="none"
                        stroke="hsl(var(--border))"
                        strokeWidth="2"
                    />
                    <motion.circle
                        cx="28"
                        cy="28"
                        r="24"
                        fill="none"
                        stroke="hsl(var(--primary))"
                        strokeWidth="2"
                        strokeLinecap="round"
                        style={{
                            pathLength: progress,
                            strokeDasharray: '1 1'
                        }}
                    />
                </svg>
                {/* Removed infinite bobbing animation */}
                <ChevronUp className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
            </motion.button>
        </motion.div>
    )
}

// Mini particle trail on logo hover
const ParticleField = ({ isActive }: { isActive: boolean }) => {
    if (!isActive) return null

    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {[...Array(20)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-1 h-1 rounded-full bg-primary"
                    style={{
                        left: '50%',
                        top: '50%',
                    }}
                    initial={{ scale: 0, x: 0, y: 0 }}
                    animate={{
                        scale: [0, 1, 0],
                        x: Math.cos(i * 18 * Math.PI / 180) * (40 + Math.random() * 30),
                        y: Math.sin(i * 18 * Math.PI / 180) * (40 + Math.random() * 30),
                        opacity: [1, 0.5, 0]
                    }}
                    transition={{
                        duration: 0.8,
                        delay: i * 0.02,
                        ease: "easeOut"
                    }}
                />
            ))}
        </div>
    )
}

// The Legendary Footer Component
export const LegendaryFooter = () => {
    const [logoClicks, setLogoClicks] = useState(0)
    const [showEasterEgg, setShowEasterEgg] = useState(false)
    const [showParticles, setShowParticles] = useState(false)
    const currentYear = new Date().getFullYear()

    // Konami code easter egg
    useKonamiCode(() => setShowEasterEgg(true))

    // Logo click counter for hidden feature
    const handleLogoClick = () => {
        setShowParticles(true)
        setTimeout(() => setShowParticles(false), 800)
        setLogoClicks(prev => prev + 1)
        if (logoClicks >= 4) {
            setShowEasterEgg(true)
            setLogoClicks(0)
        }
    }

    const socialLinks = [
        { icon: Twitter, href: 'https://x.com/raptorflow', label: 'X / Twitter', color: 'from-orange-500 to-orange-600' },
        { icon: Linkedin, href: 'https://linkedin.com/company/raptorflow', label: 'LinkedIn', color: 'from-orange-600 to-orange-800' },
        { icon: Github, href: 'https://github.com/raptorflow', label: 'GitHub', color: 'from-gray-700 to-gray-900' },
    ]

    const footerLinks = {
        product: [
            { name: 'Features', href: '/#features' },
            { name: 'Pricing', href: '/pricing' },
            { name: 'Manifesto', href: '/manifesto' },
            { name: 'Changelog', href: '/changelog' },
            { name: 'Status', href: '/status', external: true },
        ],
        company: [
            { name: 'About', href: '/about' },
            { name: 'Blog', href: '/blog' },
            { name: 'Careers', href: '/careers' },
            { name: 'Contact', href: '/contact' },
        ],
        legal: [
            { name: 'Privacy', href: '/privacy' },
            { name: 'Terms', href: '/terms' },
            { name: 'Refunds', href: '/refunds' },
            { name: 'Cookies', href: '/cookies' },
        ]
    }

    return (
        <>
            <ScrollProgress />

            <footer className="relative pt-24 pb-12 bg-gradient-to-b from-background via-muted/30 to-muted/50 overflow-hidden">
                {/* Ambient gradient orbs - Static for performance, no infinite animation */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    <div
                        className="absolute w-[600px] h-[600px] rounded-full bg-gradient-radial from-primary/10 via-primary/5 to-transparent blur-2xl md:blur-3xl"
                        style={{ top: '-200px', left: '-100px' }}
                    />
                    <div
                        className="absolute w-[400px] h-[400px] rounded-full bg-gradient-radial from-primary/8 via-primary/3 to-transparent blur-2xl md:blur-3xl"
                        style={{ bottom: '-100px', right: '-50px' }}
                    />
                </div>

                {/* Grid pattern overlay */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.03)_1px,transparent_1px)] bg-[size:50px_50px] pointer-events-none" />

                <div className="container mx-auto px-6 relative z-10">
                    <div className="max-w-6xl mx-auto">

                        {/* Top section: Brand + Stats */}
                        <div className="grid lg:grid-cols-2 gap-12 mb-16">
                            {/* Brand section */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                className="space-y-6"
                            >
                                {/* Interactive Logo */}
                                <motion.div
                                    className="relative inline-block cursor-pointer"
                                    onClick={handleLogoClick}
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    <ParticleField isActive={showParticles} />
                                    <div className="flex items-center gap-4">
                                        <RaptorFlowLogo size="xl" showText={false} animated />
                                        <div>
                                            <h3 className="font-serif text-2xl font-semibold text-foreground tracking-tight">
                                                Raptor<span className="text-primary">Flow</span>
                                            </h3>
                                            <p className="text-sm text-muted-foreground">Marketing OS for founders</p>
                                        </div>
                                    </div>
                                </motion.div>

                                <p className="text-muted-foreground max-w-md leading-relaxed">
                                    The AI-first marketing operating system. Build campaigns, generate content, and ship daily—all in one place.
                                </p>

                                {/* Social Links */}
                                <div className="flex items-center gap-4">
                                    {socialLinks.map((social) => (
                                        <MagneticButton
                                            key={social.label}
                                            href={social.href}
                                            icon={social.icon}
                                            label={social.label}
                                            color={social.color}
                                        />
                                    ))}
                                </div>

                                {/* Email */}
                                <CopyableEmail />
                            </motion.div>

                            {/* Momentum Counter */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.1 }}
                                className="flex flex-col justify-center"
                            >
                                <div className="mb-4 flex items-center gap-2">
                                    {/* Static pulse indicator - removed infinite animation */}
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                    <span className="text-sm text-muted-foreground">Live momentum</span>
                                </div>
                                <MomentumCounter />
                            </motion.div>
                        </div>

                        {/* Links Grid */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                            className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16 py-10 border-y border-border/50"
                        >
                            <div>
                                <h4 className="font-medium text-foreground mb-6 text-sm uppercase tracking-wider">Product</h4>
                                <ul className="space-y-4">
                                    {footerLinks.product.map((link) => (
                                        <li key={link.name}>
                                            <FooterLink href={link.href} external={link.external}>
                                                {link.name}
                                            </FooterLink>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h4 className="font-medium text-foreground mb-6 text-sm uppercase tracking-wider">Company</h4>
                                <ul className="space-y-4">
                                    {footerLinks.company.map((link) => (
                                        <li key={link.name}>
                                            <FooterLink href={link.href}>{link.name}</FooterLink>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h4 className="font-medium text-foreground mb-6 text-sm uppercase tracking-wider">Legal</h4>
                                <ul className="space-y-4">
                                    {footerLinks.legal.map((link) => (
                                        <li key={link.name}>
                                            <FooterLink href={link.href}>{link.name}</FooterLink>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Get Started Mini CTA */}
                            <div>
                                <h4 className="font-medium text-foreground mb-6 text-sm uppercase tracking-wider">Get Started</h4>
                                <div className="space-y-4">
                                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                                        <Link
                                            to="/signup"
                                            className="flex items-center gap-2 px-5 py-3 bg-primary text-primary-foreground rounded-xl font-medium text-sm hover:opacity-90 transition-opacity shadow-lg shadow-primary/25"
                                        >
                                            <Rocket className="w-4 h-4" />
                                            Start free
                                        </Link>
                                    </motion.div>
                                    <p className="text-xs text-muted-foreground">
                                        14-day money-back guarantee
                                    </p>
                                </div>
                            </div>
                        </motion.div>

                        {/* Bottom Bar */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            whileInView={{ opacity: 1 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.3 }}
                            className="flex flex-col md:flex-row items-center justify-between gap-6"
                        >
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <span>© {currentYear} RaptorFlow.</span>
                                <span className="hidden md:inline">•</span>
                                <motion.span
                                    className="hidden md:flex items-center gap-1"
                                    whileHover={{ scale: 1.05 }}
                                >
                                    Crafted with
                                    {/* Static heart - removed infinite pulse animation */}
                                    <Heart className="w-3.5 h-3.5 text-red-500 fill-red-500 inline mx-1" />
                                    in India
                                </motion.span>
                            </div>

                            <div className="flex items-center gap-6 text-xs text-muted-foreground">
                                <motion.span
                                    className="flex items-center gap-1 cursor-default"
                                    whileHover={{ color: 'hsl(var(--foreground))' }}
                                >
                                    <Coffee className="w-3.5 h-3.5" />
                                    Powered by caffeine
                                </motion.span>
                                <motion.span
                                    className="hidden md:flex items-center gap-1 cursor-default"
                                    whileHover={{ color: 'hsl(var(--foreground))' }}
                                >
                                    <Music className="w-3.5 h-3.5" />
                                    Built with lo-fi beats
                                </motion.span>
                                {logoClicks > 0 && logoClicks < 5 && (
                                    <motion.span
                                        initial={{ opacity: 0, scale: 0 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="text-primary text-xs"
                                    >
                                        {5 - logoClicks} more clicks... 🤫
                                    </motion.span>
                                )}
                            </div>
                        </motion.div>
                    </div>
                </div>

                {/* Easter Egg Modal */}
                <AnimatePresence>
                    {showEasterEgg && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md"
                            onClick={() => setShowEasterEgg(false)}
                        >
                            <motion.div
                                initial={{ scale: 0, rotate: -10 }}
                                animate={{ scale: 1, rotate: 0 }}
                                exit={{ scale: 0, rotate: 10 }}
                                className="bg-card border border-border rounded-3xl p-8 max-w-md text-center shadow-2xl"
                                onClick={e => e.stopPropagation()}
                            >
                                <motion.div
                                    animate={{ rotate: [0, 10, -10, 0], scale: [1, 1.1, 1] }}
                                    transition={{ duration: 0.5, repeat: 2 }}
                                    className="text-6xl mb-4"
                                >
                                    🎮
                                </motion.div>
                                <h3 className="font-serif text-2xl font-medium text-foreground mb-2">
                                    You found it!
                                </h3>
                                <p className="text-muted-foreground mb-6">
                                    You're clearly a curious founder. We like that. Here's a secret:
                                    <span className="text-primary font-medium"> the best marketing is the marketing you actually ship.</span>
                                </p>
                                <motion.button
                                    onClick={() => setShowEasterEgg(false)}
                                    className="px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium"
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    Now go ship something! 🚀
                                </motion.button>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </footer>
        </>
    )
}

export default LegendaryFooter
