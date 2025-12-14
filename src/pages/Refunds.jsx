import React from 'react'
import { motion } from 'framer-motion'
import { ShieldCheck, Clock, EnvelopeSimple, CheckCircle, CreditCard, ArrowsClockwise, Question } from '@phosphor-icons/react'
import PremiumPageLayout, { GlassCard } from '../components/PremiumPageLayout'

const Refunds = () => {
    const lastUpdated = 'December 1, 2024'

    const keyPoints = [
        {
            icon: ShieldCheck,
            title: '7-Day Guarantee',
            description: 'Full refund within 7 days of purchase, no questions asked.',
            color: 'from-emerald-500/20 to-green-500/10'
        },
        {
            icon: Clock,
            title: 'Fast Processing',
            description: 'Refunds processed within 5-7 business days.',
            color: 'from-blue-500/20 to-cyan-500/10'
        },
        {
            icon: EnvelopeSimple,
            title: 'Easy Request',
            description: 'Simply email us—no complicated forms.',
            color: 'from-amber-500/20 to-orange-500/10'
        }
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
                            <CreditCard weight="fill" className="w-4 h-4" />
                            Legal
                        </span>
                        <h1 className="text-4xl md:text-5xl font-light text-white mb-4">
                            Refund Policy
                        </h1>
                        <p className="text-white/40">Last updated: {lastUpdated}</p>
                    </motion.div>

                    {/* Key Points */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.1 }}
                        className="grid md:grid-cols-3 gap-4 mb-16"
                    >
                        {keyPoints.map((point, index) => {
                            const Icon = point.icon
                            return (
                                <GlassCard key={point.title} className="p-6 group">
                                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${point.color} border border-white/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                                        <Icon className="w-6 h-6 text-amber-400" weight="duotone" />
                                    </div>
                                    <h3 className="text-white font-medium mb-2">{point.title}</h3>
                                    <p className="text-white/50 text-sm leading-relaxed">{point.description}</p>
                                </GlassCard>
                            )
                        })}
                    </motion.div>

                    {/* Content */}
                    <div className="space-y-8">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="border-b border-white/5 pb-8"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                    <ShieldCheck className="w-4 h-4 text-amber-400" weight="duotone" />
                                </div>
                                <h2 className="text-xl font-medium text-white">Our Commitment</h2>
                            </div>
                            <p className="text-white/60 leading-relaxed ml-11">
                                We want you to love Raptorflow. If for any reason you're not satisfied with your purchase,
                                we offer a straightforward refund policy. We believe in our product enough to stand behind it.
                            </p>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="border-b border-white/5 pb-8"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                    <CheckCircle className="w-4 h-4 text-amber-400" weight="duotone" />
                                </div>
                                <h2 className="text-xl font-medium text-white">Eligibility</h2>
                            </div>
                            <ul className="space-y-3 ml-11">
                                <li className="text-white/60 flex items-start gap-3">
                                    <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" weight="fill" />
                                    <span>Request must be made within 7 days of initial purchase</span>
                                </li>
                                <li className="text-white/60 flex items-start gap-3">
                                    <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" weight="fill" />
                                    <span>Applies to first-time subscriptions only</span>
                                </li>
                                <li className="text-white/60 flex items-start gap-3">
                                    <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" weight="fill" />
                                    <span>One refund per customer</span>
                                </li>
                            </ul>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="border-b border-white/5 pb-8"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                    <EnvelopeSimple className="w-4 h-4 text-amber-400" weight="duotone" />
                                </div>
                                <h2 className="text-xl font-medium text-white">How to Request</h2>
                            </div>
                            <div className="ml-11">
                                <p className="text-white/60 leading-relaxed mb-4">
                                    Email us at <a href="mailto:support@raptorflow.com" className="text-amber-400 hover:text-amber-300 transition-colors">support@raptorflow.com</a> with:
                                </p>
                                <ul className="space-y-2 text-white/60">
                                    <li className="flex items-start gap-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 mt-2.5 flex-shrink-0" />
                                        Your account email address
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 mt-2.5 flex-shrink-0" />
                                        Date of purchase
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 mt-2.5 flex-shrink-0" />
                                        Reason for refund (optional, helps us improve)
                                    </li>
                                </ul>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="border-b border-white/5 pb-8"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                    <ArrowsClockwise className="w-4 h-4 text-amber-400" weight="duotone" />
                                </div>
                                <h2 className="text-xl font-medium text-white">Processing</h2>
                            </div>
                            <p className="text-white/60 leading-relaxed ml-11">
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
                                <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                    <Question className="w-4 h-4 text-amber-400" weight="duotone" />
                                </div>
                                <h2 className="text-xl font-medium text-white">Questions?</h2>
                            </div>
                            <p className="text-white/60 leading-relaxed ml-11">
                                Have questions about our refund policy? Contact us at{' '}
                                <a href="mailto:support@raptorflow.com" className="text-amber-400 hover:text-amber-300 transition-colors">
                                    support@raptorflow.com
                                </a>
                            </p>
                        </motion.div>
                    </div>
                </div>
            </div>
        </PremiumPageLayout>
    )
}

export default Refunds
