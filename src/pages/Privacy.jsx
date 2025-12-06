import React from 'react'
import { motion } from 'framer-motion'
import { ShieldCheck, Lock, Cookie, UserCircle, Database, ArrowsClockwise, Envelope } from '@phosphor-icons/react'
import PremiumPageLayout, { GlassCard } from '../components/PremiumPageLayout'

const Privacy = () => {
    const lastUpdated = 'December 1, 2024'

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
            icon: UserCircle,
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
            icon: ArrowsClockwise,
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
            icon: ArrowsClockwise,
            title: '7. Changes to This Policy',
            content: [
                'We may update this privacy policy from time to time.',
                'We will notify you of any significant changes via email or through our platform.',
                'Your continued use of Raptorflow after changes constitutes acceptance of the updated policy.',
            ]
        },
        {
            icon: Envelope,
            title: '8. Contact Us',
            content: [
                'If you have questions about this privacy policy or your data, please contact us at:',
                'Email: privacy@raptorflow.com',
                'We aim to respond to all enquiries within 48 hours.',
            ]
        },
    ]

    return (
        <PremiumPageLayout>
            <div className="pt-32 pb-24">
                <div className="max-w-3xl mx-auto px-6 md:px-12">

                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="mb-16"
                    >
                        <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium mb-6">
                            <ShieldCheck weight="fill" className="w-4 h-4" />
                            Legal
                        </span>

                        <h1 className="text-4xl md:text-5xl font-light text-white mb-4">
                            Privacy Policy
                        </h1>

                        <p className="text-white/40">
                            Last updated: {lastUpdated}
                        </p>
                    </motion.div>

                    {/* Introduction */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.1 }}
                        className="mb-12"
                    >
                        <GlassCard className="p-6">
                            <p className="text-lg text-white/70 leading-relaxed">
                                At Raptorflow, we take your privacy seriously. This policy explains what information
                                we collect, how we use it, and your rights regarding your personal data. We believe
                                in transparency and keeping things simple.
                            </p>
                        </GlassCard>
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
                                    className="border-b border-white/5 pb-8"
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                            <Icon className="w-4 h-4 text-amber-400" weight="duotone" />
                                        </div>
                                        <h2 className="text-xl font-medium text-white">
                                            {section.title}
                                        </h2>
                                    </div>
                                    <ul className="space-y-3 ml-11">
                                        {section.content.map((item, i) => (
                                            <li key={i} className="text-white/60 leading-relaxed flex items-start gap-3 group">
                                                <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-amber-500/50 to-orange-500/50 mt-2.5 flex-shrink-0 group-hover:from-amber-500 group-hover:to-orange-500 transition-colors" />
                                                {item}
                                            </li>
                                        ))}
                                    </ul>
                                </motion.div>
                            )
                        })}
                    </div>
                </div>
            </div>
        </PremiumPageLayout>
    )
}

export default Privacy
