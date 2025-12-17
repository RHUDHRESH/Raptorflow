import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Check, Copy, LifeBuoy, Mail, Receipt, ShieldCheck, Twitter, Linkedin } from 'lucide-react'
import { Link } from 'react-router-dom'

import { MarketingLayout } from '@/components/MarketingLayout'

/* ═══════════════════════════════════════════════════════════════════════════
   CONTACT - HIGH FASHION EDITORIAL DESIGN
   Contact page with minimal, sophisticated aesthetic
   ═══════════════════════════════════════════════════════════════════════════ */

const SocialLink = ({ href, icon: Icon, label }) => (
    <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-center gap-3 p-4 bg-card border border-border/50 hover:border-primary/50 transition-all"
    >
        <Icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" strokeWidth={1.5} />
        <span className="text-foreground">{label}</span>
    </a>
)

const InternalLinkCard = ({ to, title, description, icon: Icon }) => (
    <Link
        to={to}
        className="group rounded-card border border-border bg-card p-6 shadow-editorial-sm transition-editorial hover:shadow-editorial"
    >
        <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground group-hover:border-primary/30 group-hover:text-primary transition-editorial">
                <Icon className="h-4 w-4" strokeWidth={1.5} />
            </div>
            <div>
                <div className="font-medium text-foreground">{title}</div>
                <p className="mt-1 text-body-sm text-muted-foreground leading-relaxed">{description}</p>
                <div className="mt-3 inline-flex items-center gap-2 text-body-xs text-primary">
                    Open
                    <ArrowRight className="h-3.5 w-3.5" />
                </div>
            </div>
        </div>
    </Link>
)

const Contact = () => {
    const [copied, setCopied] = useState(false)
    const email = 'hello@raptorflow.com'
    const supportEmail = 'support@raptorflow.com'

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
        <MarketingLayout>
            <div className="container-editorial py-16 md:py-24">
                {/* Hero */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                    className="text-center mb-16"
                >
                    <p className="text-editorial-caption mb-4">Support</p>
                    <h1 className="font-serif text-headline-xl md:text-[4.25rem] leading-[1.06] text-foreground mb-4">
                        Contact.
                        <br />
                        <span className="italic text-primary">Get a clear next step.</span>
                    </h1>

                    <p className="text-body-lg text-muted-foreground max-w-[70ch] mx-auto leading-relaxed">
                        If you're stuck, curious, or considering RaptorFlow, we’ll help you route the question to the right place.
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.08, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                    className="rounded-card border border-border bg-card p-8 mb-12"
                >
                    <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                        <div>
                            <div className="text-editorial-caption">Next step</div>
                            <div className="mt-2 font-serif text-headline-sm text-foreground">Prefer to explore first?</div>
                            <p className="mt-2 text-body-sm text-muted-foreground max-w-[65ch] leading-relaxed">
                                Start the onboarding flow, or review pricing and policies. If you still have questions, email us.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            <Link
                                to="/start"
                                className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                            >
                                Get started
                            </Link>
                            <Link
                                to="/pricing"
                                className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                            >
                                View pricing
                            </Link>
                            <Link
                                to="/faq"
                                className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                            >
                                Read FAQ
                            </Link>
                        </div>
                    </div>
                </motion.div>

                {/* Email Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="mb-12"
                >
                    <div className="rounded-card border border-border bg-card p-8">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="flex h-12 w-12 items-center justify-center rounded-card border border-border bg-background">
                                <Mail className="w-5 h-5 text-primary" strokeWidth={1.5} />
                            </div>
                            <div>
                                <h3 className="font-serif text-headline-sm text-foreground">Email us</h3>
                                <p className="text-body-xs text-muted-foreground">Best way to reach us</p>
                            </div>
                        </div>

                        <button
                            onClick={handleCopy}
                            className="w-full group flex items-center justify-between rounded-card border border-border bg-secondary p-6 transition-editorial hover:border-primary/30 hover:bg-secondary/80"
                            aria-label="Copy email address"
                        >
                            <span className="text-2xl md:text-3xl font-light text-foreground">
                                {email}
                            </span>
                            <div className="flex h-10 w-10 items-center justify-center rounded-card border border-border transition-editorial group-hover:border-primary/30">
                                {copied ? (
                                    <Check className="w-5 h-5 text-primary" strokeWidth={1.5} />
                                ) : (
                                    <Copy className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" strokeWidth={1.5} />
                                )}
                            </div>
                        </button>

                        <p className="text-body-xs text-muted-foreground mt-4">
                            We typically respond within 24 hours
                        </p>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.16 }}
                    className="mb-12"
                >
                    <div className="flex items-center gap-4 mb-4">
                        <div className="h-px w-12 bg-border" />
                        <p className="text-editorial-caption">Route your question</p>
                    </div>

                    <div className="grid gap-4 md:grid-cols-3">
                        <div className="rounded-card border border-border bg-card p-6">
                            <div className="flex items-center gap-3">
                                <div className="flex h-9 w-9 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                    <LifeBuoy className="h-4 w-4" strokeWidth={1.5} />
                                </div>
                                <div>
                                    <div className="font-medium text-foreground">Product & support</div>
                                    <div className="text-body-xs text-muted-foreground">Setup, bugs, access</div>
                                </div>
                            </div>
                            <a
                                href={`mailto:${supportEmail}`}
                                className="mt-4 inline-flex items-center gap-2 text-body-sm text-primary underline underline-offset-4"
                            >
                                Email {supportEmail}
                            </a>
                        </div>

                        <div className="rounded-card border border-border bg-card p-6">
                            <div className="flex items-center gap-3">
                                <div className="flex h-9 w-9 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                    <Receipt className="h-4 w-4" strokeWidth={1.5} />
                                </div>
                                <div>
                                    <div className="font-medium text-foreground">Billing</div>
                                    <div className="text-body-xs text-muted-foreground">Invoices, upgrades</div>
                                </div>
                            </div>
                            <Link to="/pricing" className="mt-4 inline-flex items-center gap-2 text-body-sm text-primary underline underline-offset-4">
                                Review pricing
                            </Link>
                        </div>

                        <div className="rounded-card border border-border bg-card p-6">
                            <div className="flex items-center gap-3">
                                <div className="flex h-9 w-9 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                    <ShieldCheck className="h-4 w-4" strokeWidth={1.5} />
                                </div>
                                <div>
                                    <div className="font-medium text-foreground">Policies</div>
                                    <div className="text-body-xs text-muted-foreground">Refunds, terms</div>
                                </div>
                            </div>
                            <Link to="/refunds" className="mt-4 inline-flex items-center gap-2 text-body-sm text-primary underline underline-offset-4">
                                Read refund policy
                            </Link>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.22 }}
                    className="mb-12"
                >
                    <div className="flex items-center gap-4 mb-4">
                        <div className="h-px w-12 bg-border" />
                        <p className="text-editorial-caption">Fast links</p>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                        <InternalLinkCard
                            to="/status"
                            title="Status"
                            description="See system health and recent incidents."
                            icon={ShieldCheck}
                        />
                        <InternalLinkCard
                            to="/changelog"
                            title="Changelog"
                            description="What changed lately and what’s shipping next."
                            icon={ArrowRight}
                        />
                    </div>
                </motion.div>

                {/* Social Links */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mb-12"
                >
                    <p className="text-editorial-caption mb-4">Find us on social</p>
                    <div className="grid grid-cols-2 gap-4">
                        <SocialLink href="https://twitter.com/raptorflow" icon={Twitter} label="Twitter" />
                        <SocialLink href="https://linkedin.com/company/raptorflow" icon={Linkedin} label="LinkedIn" />
                    </div>
                </motion.div>

                {/* Support Email */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="text-center pt-8 border-t border-border/30"
                >
                    <p className="text-body-xs text-muted-foreground">
                        For support inquiries:{' '}
                        <a href={`mailto:${supportEmail}`} className="text-primary hover:underline">
                            {supportEmail}
                        </a>
                    </p>
                </motion.div>
            </div>
        </MarketingLayout>
    )
}

export default Contact
