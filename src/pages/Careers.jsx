import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, Globe2, Mail, Rocket, Sparkles } from 'lucide-react'

import { MarketingLayout } from '@/components/MarketingLayout'

import careersRocketArt from '../assets/careers_perk_rocket.png'

const perks = [
    {
        icon: Rocket,
        title: 'Move Fast',
        description: 'Small team, big ambitions. Every person makes an outsized impact.',
        tone: 'pill-editorial pill-neutral'
    },
    {
        icon: Globe2,
        title: 'Remote-First',
        description: 'Work from anywhere. We care about output, not office hours.',
        tone: 'pill-editorial pill-neutral'
    },
    {
        icon: Sparkles,
        title: 'Cutting Edge',
        description: 'Work with the latest AI tech. Push boundaries daily.',
        tone: 'pill-editorial pill-neutral'
    },
    {
        icon: Sparkles,
        title: 'Founder DNA',
        description: 'We think like founders. Equity, ownership, and skin in the game.',
        tone: 'pill-editorial pill-neutral'
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
            <div className="h-full rounded-card border border-border bg-card p-6 shadow-editorial-sm transition-editorial hover:shadow-editorial">
                <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                        <Icon className="h-4 w-4" />
                    </div>
                    <div>
                        <div className="text-editorial-caption">{perk.title}</div>
                        <p className="mt-2 text-body-sm text-muted-foreground leading-relaxed">{perk.description}</p>
                    </div>
                </div>
            </div>
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
        <MarketingLayout>
            <div className="container-editorial py-16 md:py-24">
                <header className="relative">
                    <div className="pointer-events-none absolute -right-8 -top-8 hidden h-40 w-40 opacity-25 md:block">
                        <img src={careersRocketArt} alt="" className="h-full w-full object-contain" />
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                        className="max-w-3xl"
                    >
                        <div className="text-editorial-caption">Company</div>
                        <h1 className="mt-3 font-serif text-headline-xl md:text-[4.25rem] leading-[1.06] text-foreground">
                            Careers.
                            <br />
                            <span className="italic text-primary">Built for builders.</span>
                        </h1>
                        <p className="mt-6 text-body-lg text-muted-foreground leading-relaxed max-w-[70ch]">
                            We’re assembling a small team to build a calmer marketing operating system for founders.
                            If you care about craft, constraint, and compounding execution—stay close.
                        </p>
                    </motion.div>
                </header>

                <section className="mt-14">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="h-px w-12 bg-border" />
                        <div className="text-editorial-caption">How we work</div>
                    </div>

                    <div className="grid gap-6 md:grid-cols-2">
                        {perks.map((perk, index) => (
                            <PerkCard key={perk.title} perk={perk} index={index} />
                        ))}
                    </div>
                </section>

                <section className="mt-14">
                    <div className="rounded-card border border-border bg-card p-8">
                        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                            <div>
                                <div className="text-editorial-caption">Open roles</div>
                                <div className="mt-2 font-serif text-headline-sm text-foreground">No open roles right now.</div>
                                <p className="mt-2 text-body-sm text-muted-foreground leading-relaxed max-w-[65ch]">
                                    We’re not actively hiring, but we’re always looking for exceptional people.
                                    Leave your email and we’ll reach out when the right opportunity opens.
                                </p>
                            </div>

                            <div className="inline-flex items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-body-xs text-muted-foreground">
                                <Mail className="h-4 w-4" />
                                careers@raptorflow.com
                            </div>
                        </div>

                        <form onSubmit={handleSubmit} className="mt-8 max-w-xl">
                            <div className="flex items-stretch gap-2">
                                <label className="sr-only" htmlFor="careers-email">
                                    Email
                                </label>
                                <input
                                    id="careers-email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="you@company.com"
                                    className="h-10 w-full rounded-md border border-border bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                                    disabled={status !== 'idle'}
                                />

                                <motion.button
                                    type="submit"
                                    disabled={status !== 'idle' || !email}
                                    className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground disabled:opacity-50"
                                    whileHover={{ scale: 1.01 }}
                                    whileTap={{ scale: 0.99 }}
                                >
                                    <AnimatePresence mode="wait">
                                        {status === 'loading' ? (
                                            <motion.div
                                                key="loading"
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                className="text-sm"
                                            >
                                                Saving…
                                            </motion.div>
                                        ) : status === 'success' ? (
                                            <motion.div
                                                key="success"
                                                initial={{ scale: 0.9, opacity: 0 }}
                                                animate={{ scale: 1, opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                className="inline-flex items-center gap-2"
                                            >
                                                <Check className="h-4 w-4" />
                                                Saved
                                            </motion.div>
                                        ) : (
                                            <motion.div
                                                key="default"
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                className="inline-flex items-center gap-2"
                                            >
                                                <Sparkles className="h-4 w-4" />
                                                Notify me
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </motion.button>
                            </div>

                            {status === 'success' && (
                                <motion.p initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} className="mt-3 text-body-xs text-muted-foreground">
                                    You’re on the list.
                                </motion.p>
                            )}
                        </form>
                    </div>
                </section>
            </div>
        </MarketingLayout>
    )
}

export default Careers
