import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Rocket, Globe, DiamondsFour, Dna, Sparkle, Check, EnvelopeSimple } from '@phosphor-icons/react'
import PremiumPageLayout, { GlassCard } from '../components/PremiumPageLayout'
import careersRocketArt from '../assets/careers_perk_rocket.png'

const perks = [
    {
        icon: Rocket,
        title: 'Move Fast',
        description: 'Small team, big ambitions. Every person makes an outsized impact.',
        color: 'from-orange-500/20 to-red-500/10'
    },
    {
        icon: Globe,
        title: 'Remote-First',
        description: 'Work from anywhere. We care about output, not office hours.',
        color: 'from-blue-500/20 to-cyan-500/10'
    },
    {
        icon: DiamondsFour,
        title: 'Cutting Edge',
        description: 'Work with the latest AI tech. Push boundaries daily.',
        color: 'from-purple-500/20 to-pink-500/10'
    },
    {
        icon: Dna,
        title: 'Founder DNA',
        description: 'We think like founders. Equity, ownership, and skin in the game.',
        color: 'from-amber-500/20 to-orange-500/10'
    }
]

const PerkCard = ({ perk, index }) => {
    const Icon = perk.icon

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
        >
            <GlassCard className="p-6 h-full group">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${perk.color} border border-white/10 flex items-center justify-center mb-5 group-hover:scale-110 group-hover:border-amber-500/30 transition-all duration-500`}>
                    <Icon className="w-6 h-6 text-amber-400" weight="duotone" />
                </div>
                <h3 className="text-lg font-medium text-white mb-2 group-hover:text-amber-300 transition-colors">
                    {perk.title}
                </h3>
                <p className="text-white/50 text-sm leading-relaxed group-hover:text-white/70 transition-colors">
                    {perk.description}
                </p>
            </GlassCard>
        </motion.div>
    )
}

const Careers = () => {
    const [email, setEmail] = useState('')
    const [status, setStatus] = useState('idle')

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!email) return

        setStatus('loading')
        await new Promise(resolve => setTimeout(resolve, 1500))
        setStatus('success')
        setEmail('')
        setTimeout(() => setStatus('idle'), 3000)
    }

    return (
        <PremiumPageLayout>
            <div className="pt-32 pb-24">

                {/* Hero */}
                <section className="max-w-4xl mx-auto px-6 md:px-12 mb-24 text-center relative">
                    {/* Background artwork */}
                    <div className="absolute top-0 right-0 w-64 h-64 opacity-20 pointer-events-none">
                        <img src={careersRocketArt} alt="" className="w-full h-full object-contain" />
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="relative z-10"
                    >
                        <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium mb-8">
                            <Sparkle weight="fill" className="w-4 h-4" />
                            Careers
                        </span>

                        <h1 className="text-4xl md:text-6xl lg:text-7xl font-light text-white leading-tight mb-8">
                            Build the future of
                            <br />
                            <span className="italic bg-gradient-to-r from-amber-300 via-amber-400 to-orange-400 text-transparent bg-clip-text">
                                founder marketing
                            </span>
                        </h1>

                        <p className="text-xl text-white/50 max-w-2xl mx-auto leading-relaxed">
                            We're assembling a small, exceptional team to build something that matters.
                            If you're passionate about AI, marketing, and helping founders win—we should talk.
                        </p>
                    </motion.div>
                </section>

                {/* Culture */}
                <section className="max-w-5xl mx-auto px-6 md:px-12 mb-24">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <div className="text-center mb-12">
                            <span className="text-xs uppercase tracking-[0.3em] text-amber-400 font-medium mb-4 block">
                                Culture
                            </span>
                            <h2 className="text-3xl md:text-4xl font-light text-white">
                                Why join us?
                            </h2>
                        </div>

                        <div className="grid md:grid-cols-2 gap-6">
                            {perks.map((perk, index) => (
                                <PerkCard key={perk.title} perk={perk} index={index} />
                            ))}
                        </div>
                    </motion.div>
                </section>

                {/* Open Roles */}
                <section className="max-w-3xl mx-auto px-6 md:px-12 mb-24">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="text-center"
                    >
                        <GlassCard className="p-12 relative overflow-hidden">
                            {/* Background glow */}
                            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-radial from-amber-500/10 to-transparent blur-3xl" />

                            <div className="relative z-10">
                                <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/20 flex items-center justify-center">
                                    <Sparkle weight="fill" className="w-8 h-8 text-amber-400" />
                                </div>

                                <h2 className="text-2xl md:text-3xl font-light text-white mb-4">
                                    No open roles right now
                                </h2>

                                <p className="text-white/50 mb-8 max-w-md mx-auto">
                                    We're not actively hiring, but we're always looking for exceptional people.
                                    Drop your email and we'll reach out when the right opportunity opens.
                                </p>

                                {/* Email Signup */}
                                <form onSubmit={handleSubmit} className="max-w-md mx-auto mb-6">
                                    <div className={`
                                        flex items-center gap-2 p-1.5 rounded-xl border transition-all duration-300
                                        ${status === 'success'
                                            ? 'border-emerald-500/40 bg-emerald-500/5'
                                            : 'border-white/10 bg-white/5 focus-within:border-amber-500/40 focus-within:bg-amber-500/5 focus-within:shadow-[0_0_30px_rgba(245,158,11,0.1)]'
                                        }
                                    `}>
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="Enter your email"
                                            className="flex-1 px-4 py-3 bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
                                            disabled={status !== 'idle'}
                                        />

                                        <motion.button
                                            type="submit"
                                            disabled={status !== 'idle' || !email}
                                            className="px-5 py-3 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg text-sm flex items-center gap-2 disabled:opacity-50 transition-all"
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                        >
                                            <AnimatePresence mode="wait">
                                                {status === 'loading' ? (
                                                    <motion.div
                                                        key="loading"
                                                        className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin"
                                                    />
                                                ) : status === 'success' ? (
                                                    <Check className="w-4 h-4" weight="bold" />
                                                ) : (
                                                    <span>Notify me</span>
                                                )}
                                            </AnimatePresence>
                                        </motion.button>
                                    </div>

                                    {status === 'success' && (
                                        <motion.p
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="text-emerald-400 text-sm mt-3"
                                        >
                                            You're on the list! We'll be in touch.
                                        </motion.p>
                                    )}
                                </form>

                                {/* Direct contact */}
                                <p className="text-white/30 text-sm flex items-center justify-center gap-2">
                                    Or reach out directly at{' '}
                                    <a href="mailto:careers@raptorflow.com" className="text-amber-400 hover:text-amber-300 transition-colors inline-flex items-center gap-1">
                                        <EnvelopeSimple weight="duotone" className="w-4 h-4" />
                                        careers@raptorflow.com
                                    </a>
                                </p>
                            </div>
                        </GlassCard>
                    </motion.div>
                </section>
            </div>
        </PremiumPageLayout>
    )
}

export default Careers
