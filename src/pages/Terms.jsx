import React from 'react'
import { motion } from 'framer-motion'
import { Scales, FileText, UserCheck, CreditCard, Files, Robot, Prohibit, Warning, MapPin, Envelope } from '@phosphor-icons/react'
import PremiumPageLayout, { GlassCard } from '../components/PremiumPageLayout'

const Terms = () => {
    const lastUpdated = 'December 1, 2024'

    const sections = [
        {
            icon: Scales,
            title: '1. Acceptance of Terms',
            content: [
                'By accessing or using Raptorflow, you agree to be bound by these Terms of Service.',
                'If you do not agree to these terms, please do not use our service.',
            ]
        },
        {
            icon: FileText,
            title: '2. Description of Service',
            content: [
                'Raptorflow is an AI-powered marketing operating system for founders.',
                'Features and functionality may change as we improve the platform.',
            ]
        },
        {
            icon: UserCheck,
            title: '3. Account Registration',
            content: [
                'You must provide accurate information when creating an account.',
                'You are responsible for maintaining the security of your credentials.',
                'You must be at least 18 years old to create an account.',
            ]
        },
        {
            icon: CreditCard,
            title: '4. Subscription and Payment',
            content: [
                'Some features require a paid subscription.',
                'Payments are processed securely through Razorpay.',
                'Prices are in INR and inclusive of applicable taxes.',
            ]
        },
        {
            icon: Files,
            title: '5. User Content',
            content: [
                'You retain ownership of content you create using Raptorflow.',
                'You grant us a license to store and process your content to provide our service.',
            ]
        },
        {
            icon: Robot,
            title: '6. AI-Generated Content',
            content: [
                'AI-generated content is provided as a starting point and should be reviewed.',
                'We do not guarantee accuracy of AI-generated content.',
            ]
        },
        {
            icon: Prohibit,
            title: '7. Prohibited Uses',
            content: [
                'Using the service for illegal purposes is prohibited.',
                'Attempting unauthorized access to our systems is prohibited.',
            ]
        },
        {
            icon: Warning,
            title: '8. Limitation of Liability',
            content: [
                'Raptorflow is provided "as is" without warranties.',
                'Our total liability shall not exceed amounts paid in the past 12 months.',
            ]
        },
        {
            icon: MapPin,
            title: '9. Governing Law',
            content: [
                'These terms are governed by the laws of India.',
                'Disputes shall be resolved in the courts of Chennai, Tamil Nadu.',
                'Raptorflow is operated by Peregrien Stratgen.',
            ]
        },
        {
            icon: Envelope,
            title: '10. Contact',
            content: [
                'For questions, contact us at: legal@raptorflow.com',
            ]
        },
    ]

    return (
        <PremiumPageLayout>
            <div className="pt-32 pb-24">
                <div className="max-w-3xl mx-auto px-6 md:px-12">

                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="mb-16"
                    >
                        <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium mb-6">
                            <Scales weight="fill" className="w-4 h-4" />
                            Legal
                        </span>
                        <h1 className="text-4xl md:text-5xl font-light text-white mb-4">
                            Terms of Service
                        </h1>
                        <p className="text-white/40">Last updated: {lastUpdated}</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.1 }}
                        className="mb-12"
                    >
                        <GlassCard className="p-6">
                            <p className="text-lg text-white/70 leading-relaxed">
                                These Terms of Service govern your use of Raptorflow. Please read them carefully.
                            </p>
                        </GlassCard>
                    </motion.div>

                    <div className="space-y-8">
                        {sections.map((section, index) => {
                            const Icon = section.icon
                            return (
                                <motion.div
                                    key={section.title}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true, margin: '-50px' }}
                                    transition={{ duration: 0.5, delay: index * 0.03 }}
                                    className="border-b border-white/5 pb-8"
                                >
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                            <Icon className="w-4 h-4 text-amber-400" weight="duotone" />
                                        </div>
                                        <h2 className="text-xl font-medium text-white">{section.title}</h2>
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

export default Terms
