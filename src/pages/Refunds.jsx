import { motion } from 'framer-motion'
import { Check, Clock, HelpCircle, Mail, RefreshCcw, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

import { MarketingLayout } from '@/components/MarketingLayout'

const Refunds = () => {
    const lastUpdated = 'December 1, 2024'

    const keyPoints = [
        {
            icon: ShieldCheck,
            title: '7-Day Guarantee',
            description: 'Full refund within 7 days of purchase, no questions asked.',
        },
        {
            icon: Clock,
            title: 'Fast Processing',
            description: 'Refunds processed within 5-7 business days.',
        },
        {
            icon: Mail,
            title: 'Easy Request',
            description: 'Simply email us—no complicated forms.',
        }
    ]

    return (
        <MarketingLayout>
            <div className="container-editorial py-16 md:py-24">

                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="mb-16"
                    >
                        <div className="text-editorial-caption mb-6">Legal</div>
                        <h1 className="font-serif text-headline-lg text-foreground mb-4">Refund Policy</h1>
                        <p className="text-body-xs text-muted-foreground">Last updated: {lastUpdated}</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.12 }}
                        className="rounded-card border border-border bg-card p-8 mb-16"
                    >
                        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                            <div>
                                <div className="text-editorial-caption">Next steps</div>
                                <div className="mt-2 font-serif text-headline-sm text-foreground">Need help right now?</div>
                                <p className="mt-2 text-body-sm text-muted-foreground max-w-[65ch] leading-relaxed">
                                    If you're unsure about eligibility or timelines, start with the pricing details or email support.
                                </p>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                <Link
                                    to="/pricing"
                                    className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                                >
                                    View pricing
                                </Link>
                                <Link
                                    to="/contact"
                                    className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                                >
                                    Contact support
                                </Link>
                                <Link
                                    to="/start"
                                    className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                                >
                                    Get started
                                </Link>
                            </div>
                        </div>
                        <div className="mt-4 flex flex-wrap gap-4 text-body-xs text-muted-foreground">
                            <Link to="/terms" className="underline underline-offset-4 hover:text-foreground">Terms</Link>
                            <Link to="/privacy" className="underline underline-offset-4 hover:text-foreground">Privacy</Link>
                        </div>
                    </motion.div>

                    {/* Key Points */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.1 }}
                        className="grid md:grid-cols-3 gap-4 mb-16"
                    >
                        {keyPoints.map((point) => {
                            const Icon = point.icon
                            return (
                                <div
                                    key={point.title}
                                    className="rounded-card border border-border bg-card p-6 shadow-editorial-sm"
                                >
                                    <div className="flex items-start gap-4">
                                        <div className="flex h-10 w-10 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                            <Icon className="h-4 w-4" strokeWidth={1.5} />
                                        </div>
                                        <div>
                                            <div className="font-medium text-foreground">{point.title}</div>
                                            <p className="mt-1 text-body-sm text-muted-foreground leading-relaxed">
                                                {point.description}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )
                        })}
                    </motion.div>

                    {/* Content */}
                    <div className="space-y-8">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="border-b border-border/50 pb-8"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="flex h-8 w-8 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                    <ShieldCheck className="h-4 w-4" strokeWidth={1.5} />
                                </div>
                                <h2 className="font-serif text-headline-sm text-foreground">Our Commitment</h2>
                            </div>
                            <p className="text-body-sm text-muted-foreground leading-relaxed ml-11">
                                We want you to love Raptorflow. If for any reason you're not satisfied with your purchase,
                                we offer a straightforward refund policy. We believe in our product enough to stand behind it.
                            </p>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="border-b border-border/50 pb-8"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="flex h-8 w-8 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                    <Check className="h-4 w-4" strokeWidth={1.5} />
                                </div>
                                <h2 className="font-serif text-headline-sm text-foreground">Eligibility</h2>
                            </div>
                            <ul className="space-y-3 ml-11">
                                <li className="text-body-sm text-muted-foreground flex items-start gap-3">
                                    <Check className="mt-0.5 h-4 w-4 text-primary flex-shrink-0" strokeWidth={1.5} />
                                    <span>Request must be made within 7 days of initial purchase</span>
                                </li>
                                <li className="text-body-sm text-muted-foreground flex items-start gap-3">
                                    <Check className="mt-0.5 h-4 w-4 text-primary flex-shrink-0" strokeWidth={1.5} />
                                    <span>Applies to first-time subscriptions only</span>
                                </li>
                                <li className="text-body-sm text-muted-foreground flex items-start gap-3">
                                    <Check className="mt-0.5 h-4 w-4 text-primary flex-shrink-0" strokeWidth={1.5} />
                                    <span>One refund per customer</span>
                                </li>
                            </ul>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="border-b border-border/50 pb-8"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="flex h-8 w-8 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                    <Mail className="h-4 w-4" strokeWidth={1.5} />
                                </div>
                                <h2 className="font-serif text-headline-sm text-foreground">How to Request</h2>
                            </div>
                            <div className="ml-11">
                                <p className="text-body-sm text-muted-foreground leading-relaxed mb-4">
                                    Email us at{' '}
                                    <a href="mailto:support@raptorflow.com" className="text-primary hover:underline">
                                        support@raptorflow.com
                                    </a>{' '}
                                    with:
                                </p>
                                <ul className="space-y-2 text-body-sm text-muted-foreground">
                                    <li className="flex items-start gap-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-primary/60 mt-2.5 flex-shrink-0" />
                                        Your account email address
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-primary/60 mt-2.5 flex-shrink-0" />
                                        Date of purchase
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-primary/60 mt-2.5 flex-shrink-0" />
                                        Reason for refund (optional, helps us improve)
                                    </li>
                                </ul>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="border-b border-border/50 pb-8"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="flex h-8 w-8 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                    <RefreshCcw className="h-4 w-4" strokeWidth={1.5} />
                                </div>
                                <h2 className="font-serif text-headline-sm text-foreground">Processing</h2>
                            </div>
                            <p className="text-body-sm text-muted-foreground leading-relaxed ml-11">
                                Once approved, refunds are processed within 5-7 business days. The refund will
                                be credited to the original payment method. Your account access will be
                                revoked upon refund processing.
                            </p>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="flex h-8 w-8 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                    <HelpCircle className="h-4 w-4" strokeWidth={1.5} />
                                </div>
                                <h2 className="font-serif text-headline-sm text-foreground">Questions?</h2>
                            </div>
                            <p className="text-body-sm text-muted-foreground leading-relaxed ml-11">
                                Have questions about our refund policy? Contact us at{' '}
                                <a href="mailto:support@raptorflow.com" className="text-primary hover:underline">
                                    support@raptorflow.com
                                </a>
                            </p>
                        </motion.div>
                    </div>

                    <section className="mt-16 border-t border-border pt-12">
                        <div className="rounded-card border border-border bg-card p-8">
                            <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                                <div>
                                    <div className="text-editorial-caption">Short version</div>
                                    <div className="mt-2 font-serif text-headline-sm text-foreground">7-day guarantee.</div>
                                    <p className="mt-2 text-body-sm text-muted-foreground max-w-[65ch] leading-relaxed">
                                        If you're within 7 days of purchase, email support and we'll help you quickly.
                                    </p>
                                </div>
                                <a
                                    href="mailto:support@raptorflow.com"
                                    className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                                >
                                    Email support
                                </a>
                            </div>
                        </div>
                    </section>
            </div>
        </MarketingLayout>
    )
}

export default Refunds
