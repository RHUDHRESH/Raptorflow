import { motion } from 'framer-motion'
import { ArrowRight, Cookie, Database, Lock, Mail, RefreshCcw, ShieldCheck, User } from 'lucide-react'
import { Link } from 'react-router-dom'

import { MarketingLayout } from '@/components/MarketingLayout'

const Privacy = () => {
    const lastUpdated = 'December 1, 2024'

    const sectionToId = (title) =>
        title
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '')

    const sections = [
        {
            icon: Database,
            title: '1. Information We Collect',
            content: [
                'Account Information: When you create an account, we collect your name, email address, and password.',
                'Usage Data: We collect information about how you use Raptorflow, including features accessed and actions taken.',
                'Payment Information: If you subscribe to a paid plan, we collect payment information through our secure payment processor (Razorpay). We do not store your complete credit card details.',
                'Communications: When you contact us, we collect the information you provide in your messages.',
            ]
        },
        {
            icon: User,
            title: '2. How We Use Your Information',
            content: [
                'To provide and maintain our service',
                'To process your transactions and manage your subscription',
                'To send you important updates about our service',
                'To respond to your inquiries and provide customer support',
                'To improve and personalize your experience',
                'To analyze usage patterns and optimize our platform',
            ]
        },
        {
            icon: Lock,
            title: '3. Data Storage and Security',
            content: [
                'We use industry-standard security measures to protect your data.',
                'Your data is stored on secure servers provided by our cloud infrastructure partners.',
                'We use encryption in transit (HTTPS) and at rest to protect sensitive information.',
                'We regularly review and update our security practices.',
            ]
        },
        {
            icon: RefreshCcw,
            title: '4. Data Sharing',
            content: [
                'We do not sell your personal information to third parties.',
                'We may share data with service providers who help us operate our platform (e.g., payment processors, hosting providers).',
                'We may disclose information if required by law or to protect our rights.',
            ]
        },
        {
            icon: ShieldCheck,
            title: '5. Your Rights',
            content: [
                'Access: You can request a copy of your personal data.',
                'Correction: You can update your account information at any time.',
                'Deletion: You can request deletion of your account and associated data.',
                'Export: You can export your data in a standard format.',
            ]
        },
        {
            icon: Cookie,
            title: '6. Cookies',
            content: [
                'We use essential cookies to maintain your session and preferences.',
                'We use analytics cookies to understand how you use our service.',
                'You can control cookie settings through your browser.',
            ]
        },
        {
            icon: RefreshCcw,
            title: '7. Changes to This Policy',
            content: [
                'We may update this privacy policy from time to time.',
                'We will notify you of any significant changes via email or through our platform.',
                'Your continued use of Raptorflow after changes constitutes acceptance of the updated policy.',
            ]
        },
        {
            icon: Mail,
            title: '8. Contact Us',
            content: [
                'If you have questions about this privacy policy or your data, please contact us at:',
                'Email: privacy@raptorflow.com',
                'We aim to respond to all enquiries within 48 hours.',
            ]
        },
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
                        <h1 className="font-serif text-headline-lg text-foreground mb-4">Privacy Policy</h1>
                        <p className="text-body-xs text-muted-foreground">Last updated: {lastUpdated}</p>
                    </motion.div>

                    <section className="mb-12">
                        <div className="rounded-card border border-border bg-card p-6">
                            <div className="text-editorial-caption">Quick links</div>
                            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2">
                                {sections.slice(0, 7).map((s) => (
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

                    {/* Introduction */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.1 }}
                        className="mb-12"
                    >
                        <div className="rounded-card border border-border bg-card p-6">
                            <p className="text-body-md text-muted-foreground leading-relaxed">
                                At Raptorflow, we take your privacy seriously. This policy explains what information
                                we collect, how we use it, and your rights regarding your personal data. We believe
                                in transparency and keeping things simple.
                            </p>
                        </div>
                    </motion.div>

                    {/* Sections */}
                    <div className="space-y-8">
                        {sections.map((section, index) => {
                            const Icon = section.icon
                            return (
                                <motion.div
                                    key={section.title}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true, margin: '-50px' }}
                                    transition={{ duration: 0.5, delay: index * 0.05 }}
                                    className="border-b border-border/50 pb-8"
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="flex h-8 w-8 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
                                            <Icon className="h-4 w-4" strokeWidth={1.5} />
                                        </div>
                                        <h2 id={sectionToId(section.title)} className="font-serif text-headline-sm text-foreground">
                                            {section.title}
                                        </h2>
                                    </div>
                                    <ul className="space-y-3 ml-11">
                                        {section.content.map((item, i) => (
                                            <li key={i} className="text-body-sm text-muted-foreground leading-relaxed flex items-start gap-3">
                                                <span className="w-1.5 h-1.5 rounded-full bg-primary/60 mt-2.5 flex-shrink-0" />
                                                {item}
                                            </li>
                                        ))}
                                    </ul>
                                </motion.div>
                            )
                        })}
                    </div>

                    <section className="mt-16 border-t border-border pt-12">
                        <div className="rounded-card border border-border bg-card p-8">
                            <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                                <div>
                                    <div className="text-editorial-caption">Next steps</div>
                                    <div className="mt-2 font-serif text-headline-sm text-foreground">Need a privacy answer?</div>
                                    <p className="mt-2 text-body-sm text-muted-foreground max-w-[65ch] leading-relaxed">
                                        If you have questions about your data, reach out. You can also review terms and cookies.
                                    </p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    <Link
                                        to="/contact"
                                        className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                                    >
                                        Contact
                                    </Link>
                                    <Link
                                        to="/terms"
                                        className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                                    >
                                        Terms
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
}

export default Privacy
