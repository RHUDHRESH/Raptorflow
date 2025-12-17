import React, { useState } from 'react'

import { motion, AnimatePresence } from 'framer-motion'
import { Check, Mail } from 'lucide-react'

import { MarketingLayout } from '@/components/MarketingLayout'

const Blog = () => {
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
                <header className="text-center max-w-3xl mx-auto">
                    <p className="text-editorial-caption mb-6">Writing</p>
                    <h1 className="font-serif text-headline-xl md:text-[4.25rem] leading-[1.06] text-foreground">
                        Notes on positioning,
                        <br />
                        <span className="italic text-primary">founder marketing</span>, and execution.
                    </h1>
                    <p className="mt-6 text-body-lg text-muted-foreground">
                        Short, opinionated, and practical. Built for founders who ship.
                    </p>
                </header>

                <section className="mt-14 rounded-card border border-border bg-card p-8">
                    <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                        <div>
                            <div className="text-editorial-caption">Get updates</div>
                            <div className="mt-2 font-serif text-headline-sm text-foreground">One email when we publish.</div>
                            <p className="mt-2 text-body-sm text-muted-foreground max-w-[60ch]">
                                No spam. No weekly newsletters. Just the next post.
                            </p>
                        </div>

                        <form onSubmit={handleSubmit} className="w-full md:max-w-md">
                            <div className="flex items-stretch gap-2">
                                <label className="sr-only" htmlFor="blog-email">
                                    Email
                                </label>
                                <input
                                    id="blog-email"
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
                                                Sending…
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
                                                <Mail className="h-4 w-4" />
                                                Notify me
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </motion.button>
                            </div>
                        </form>
                    </div>

                    {status === 'success' && (
                        <motion.p initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} className="mt-3 text-body-xs text-muted-foreground">
                            You’re on the list.
                        </motion.p>
                    )}
                </section>

                <section className="mt-10 grid gap-6 md:grid-cols-2">
                    {[
                        {
                            title: 'Why weekly resets kill momentum',
                            summary: 'The quiet compounding advantage of a 90-day map and one decision per day.',
                            meta: 'Draft · 6 min read',
                        },
                        {
                            title: 'A founder’s guide to positioning without templates',
                            summary: 'How to choose a lane, say no, and ship a message that converts.',
                            meta: 'Draft · 8 min read',
                        },
                    ].map((post) => (
                        <article key={post.title} className="rounded-card border border-border bg-card p-6">
                            <div className="text-body-xs text-muted-foreground">{post.meta}</div>
                            <h2 className="mt-2 font-serif text-headline-sm text-foreground">{post.title}</h2>
                            <p className="mt-2 text-body-sm text-muted-foreground leading-relaxed">{post.summary}</p>
                            <div className="mt-4 text-body-xs text-muted-foreground">Coming soon</div>
                        </article>
                    ))}
                </section>
            </div>
        </MarketingLayout>
    )
}

export default Blog
