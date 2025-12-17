import { motion } from 'framer-motion'
import { ArrowRight, Mail } from 'lucide-react'
import { Link } from 'react-router-dom'

import { MarketingLayout } from '@/components/MarketingLayout'

/* ═══════════════════════════════════════════════════════════════════════════
   TERMS - HIGH FASHION EDITORIAL DESIGN
   Legal page with minimal, sophisticated aesthetic
   ═══════════════════════════════════════════════════════════════════════════ */

const sections = [
    { title: '1. Acceptance of Terms', content: ['By accessing Raptorflow, you agree to these Terms of Service.', 'If you disagree, please do not use our service.'] },
    { title: '2. Description of Service', content: ['Raptorflow is an AI-powered marketing operating system.', 'Features may change as we improve the platform.'] },
    { title: '3. Account Registration', content: ['Provide accurate information when creating an account.', 'Maintain security of your credentials.', 'Must be 18+ years old.'] },
    { title: '4. Payment', content: ['Some features require paid subscription.', 'Payments processed via Razorpay.', 'Prices in INR, inclusive of taxes.'] },
    { title: '5. User Content', content: ['You retain ownership of your content.', 'We may store and process content to provide service.'] },
    { title: '6. AI Content', content: ['AI content is a starting point and should be reviewed.', 'We do not guarantee accuracy.'] },
    { title: '7. Prohibited Uses', content: ['Illegal purposes prohibited.', 'Unauthorized access prohibited.'] },
    { title: '8. Liability', content: ['Service provided "as is".', 'Liability limited to amounts paid in past 12 months.'] },
    { title: '9. Governing Law', content: ['Governed by laws of India.', 'Disputes resolved in Chennai courts.'] },
    { title: '10. Contact', content: ['legal@raptorflow.com'] },
]

const sectionToId = (title) =>
    title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '')

const Terms = () => (
    <MarketingLayout>
        <div className="container-editorial py-16 md:py-24">
            {/* Header */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className="mb-16"
            >
                <p className="text-editorial-caption mb-4">Legal</p>
                <h1 className="font-serif text-headline-lg text-foreground mb-4">Terms of Service</h1>
                <p className="text-muted-foreground">Last updated: December 1, 2024</p>
            </motion.header>

            <section className="mb-12">
                <div className="rounded-card border border-border bg-card p-6">
                    <div className="text-editorial-caption">Quick links</div>
                    <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2">
                        {sections.slice(0, 9).map((s) => (
                            <a
                                key={s.title}
                                href={`#${sectionToId(s.title)}`}
                                className="text-body-xs text-muted-foreground underline underline-offset-4 hover:text-foreground"
                            >
                                {s.title}
                            </a>
                        ))}
                    </div>
                </div>
            </section>

            {/* Intro */}
            <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="rounded-card border border-border bg-card p-6 mb-12"
            >
                <p className="text-foreground leading-relaxed">
                    These Terms of Service govern your use of Raptorflow. Please read them carefully.
                </p>
            </motion.div>

            {/* Sections */}
            <div className="space-y-8">
                {sections.map((section, index) => (
                    <motion.div
                        key={section.title}
                        initial={{ opacity: 0, y: 16 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: index * 0.02 }}
                        className="border-b border-border/30 pb-8"
                    >
                        <h2 id={sectionToId(section.title)} className="font-serif text-headline-sm text-foreground mb-4">
                            {section.title}
                        </h2>
                        <ul className="space-y-2">
                            {section.content.map((item, i) => (
                                <li key={i} className="text-muted-foreground leading-relaxed flex items-start gap-3">
                                    <span className="w-1 h-1 bg-primary mt-2.5 flex-shrink-0" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </motion.div>
                ))}
            </div>

            <section className="mt-16 border-t border-border pt-12">
                <div className="rounded-card border border-border bg-card p-8">
                    <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                        <div>
                            <div className="text-editorial-caption">Next steps</div>
                            <div className="mt-2 font-serif text-headline-sm text-foreground">Questions about terms?</div>
                            <p className="mt-2 text-body-sm text-muted-foreground max-w-[65ch] leading-relaxed">
                                If you need clarification, reach out. For billing topics, see refunds. For tracking, see cookies.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            <Link
                                to="/contact"
                                className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                            >
                                <Mail className="mr-2 h-4 w-4" />
                                Contact
                            </Link>
                            <Link
                                to="/refunds"
                                className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                            >
                                Refunds
                            </Link>
                            <Link
                                to="/cookies"
                                className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                            >
                                Cookies
                            </Link>
                            <Link
                                to="/start"
                                className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                            >
                                Get started
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </MarketingLayout>
)

export default Terms
