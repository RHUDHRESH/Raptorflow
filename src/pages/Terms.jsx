import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileText, Scale, AlertCircle, Ban } from 'lucide-react';

export default function Terms() {
    return (
        <div className="min-h-screen bg-cream">
            {/* Header */}
            <motion.header
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="border-b border-black/10 bg-white/95 backdrop-blur-xl sticky top-0 z-50"
            >
                <div className="mx-auto max-w-4xl px-6 py-6">
                    <Link
                        to="/landing"
                        className="inline-flex items-center gap-2 text-sm font-medium hover:underline"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Home
                    </Link>
                </div>
            </motion.header>

            {/* Content */}
            <div className="mx-auto max-w-4xl px-6 py-20">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <div className="mb-12">
                        <motion.div
                            className="mb-4 inline-flex items-center gap-2 rounded-full border-2 border-black bg-black px-4 py-2"
                            whileHover={{ scale: 1.05 }}
                        >
                            <Scale className="h-5 w-5 text-white" />
                            <span className="font-mono text-sm font-bold text-white">Terms of Service</span>
                        </motion.div>
                        <h1 className="mb-4 font-serif text-6xl font-black tracking-tight">
                            Simple Terms,
                            <br />
                            No Surprises
                        </h1>
                        <p className="text-xl text-gray-600">
                            Last updated: November 25, 2024
                        </p>
                    </div>

                    <div className="space-y-12">
                        {/* Agreement */}
                        <section>
                            <div className="mb-4 flex items-center gap-3">
                                <FileText className="h-6 w-6" />
                                <h2 className="font-serif text-3xl font-black">The Agreement</h2>
                            </div>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    By using RaptorFlow, you agree to these terms. If you don't agree, don't use the service.
                                </p>
                                <p>
                                    RaptorFlow is a marketing strategy execution platform. We provide the tools, you create the strategy.
                                </p>
                            </div>
                        </section>

                        {/* Your Account */}
                        <section>
                            <h2 className="mb-4 font-serif text-3xl font-black">Your Account</h2>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    <strong>You're responsible for:</strong>
                                </p>
                                <ul className="list-disc space-y-2 pl-6">
                                    <li>Keeping your password secure</li>
                                    <li>All activity under your account</li>
                                    <li>Notifying us of unauthorized access</li>
                                </ul>
                                <p>
                                    <strong>One account per person.</strong> No sharing accounts across teams (use team seats instead).
                                </p>
                            </div>
                        </section>

                        {/* Payment */}
                        <section>
                            <h2 className="mb-4 font-serif text-3xl font-black">Payment & Billing</h2>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    <strong>Pricing:</strong> Monthly subscriptions (Ascent, Glide, Soar). Prices in INR.
                                </p>
                                <p>
                                    <strong>Billing:</strong> Charged monthly on your signup date. Auto-renewal unless you cancel.
                                </p>
                                <p>
                                    <strong>Refunds:</strong> 14-day money-back guarantee. No questions asked. Email support@raptorflow.in
                                </p>
                                <p>
                                    <strong>Cancellation:</strong> Cancel anytime. Access continues until the end of your billing period.
                                </p>
                            </div>
                        </section>

                        {/* Your Data */}
                        <section>
                            <h2 className="mb-4 font-serif text-3xl font-black">Your Data & Content</h2>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    <strong>You own your data.</strong> Cohorts, moves, actions, analytics — it's all yours.
                                </p>
                                <p>
                                    <strong>We can use it to:</strong>
                                </p>
                                <ul className="list-disc space-y-2 pl-6">
                                    <li>Provide the service (obviously)</li>
                                    <li>Improve features (anonymized)</li>
                                    <li>Debug issues (with your permission)</li>
                                </ul>
                                <p>
                                    <strong>We never:</strong> Sell your data, share it with advertisers, or use it for training AI models.
                                </p>
                            </div>
                        </section>

                        {/* Acceptable Use */}
                        <section>
                            <div className="mb-4 flex items-center gap-3">
                                <Ban className="h-6 w-6" />
                                <h2 className="font-serif text-3xl font-black">Acceptable Use</h2>
                            </div>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    <strong>Don't:</strong>
                                </p>
                                <ul className="list-disc space-y-2 pl-6">
                                    <li>Violate laws or regulations</li>
                                    <li>Spam, phish, or harass anyone</li>
                                    <li>Reverse-engineer or scrape the platform</li>
                                    <li>Share login credentials</li>
                                    <li>Upload malware or malicious code</li>
                                </ul>
                                <p>
                                    We reserve the right to suspend accounts that violate these terms.
                                </p>
                            </div>
                        </section>

                        {/* Service Availability */}
                        <section>
                            <h2 className="mb-4 font-serif text-3xl font-black">Service Availability</h2>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    We aim for 99.9% uptime, but we're not perfect. Maintenance, updates, and outages happen.
                                </p>
                                <p>
                                    <strong>We're not liable for:</strong>
                                </p>
                                <ul className="list-disc space-y-2 pl-6">
                                    <li>Temporary service interruptions</li>
                                    <li>Data loss (though we do daily backups)</li>
                                    <li>Third-party service failures (Supabase, Vercel, etc.)</li>
                                </ul>
                                <p>
                                    <strong>Recommendation:</strong> Export your data regularly.
                                </p>
                            </div>
                        </section>

                        {/* Liability */}
                        <section>
                            <div className="mb-4 flex items-center gap-3">
                                <AlertCircle className="h-6 w-6" />
                                <h2 className="font-serif text-3xl font-black">Limitation of Liability</h2>
                            </div>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    RaptorFlow is provided "as is." We're not liable for:
                                </p>
                                <ul className="list-disc space-y-2 pl-6">
                                    <li>Lost revenue or business opportunities</li>
                                    <li>Indirect, incidental, or consequential damages</li>
                                    <li>Marketing campaigns that don't perform</li>
                                </ul>
                                <p>
                                    <strong>Maximum liability:</strong> The amount you paid us in the last 12 months.
                                </p>
                            </div>
                        </section>

                        {/* Changes */}
                        <section>
                            <h2 className="mb-4 font-serif text-3xl font-black">Changes to Terms</h2>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    We may update these terms. We'll notify you via email 30 days before major changes.
                                </p>
                                <p>
                                    Continued use after changes means you accept the new terms.
                                </p>
                            </div>
                        </section>

                        {/* Termination */}
                        <section>
                            <h2 className="mb-4 font-serif text-3xl font-black">Termination</h2>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    <strong>You can:</strong> Cancel anytime. Export your data before closing your account.
                                </p>
                                <p>
                                    <strong>We can:</strong> Suspend or terminate accounts that violate these terms.
                                </p>
                            </div>
                        </section>

                        {/* Governing Law */}
                        <section>
                            <h2 className="mb-4 font-serif text-3xl font-black">Governing Law</h2>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    These terms are governed by the laws of India. Disputes will be resolved in Bangalore courts.
                                </p>
                            </div>
                        </section>

                        {/* Contact */}
                        <section className="border-t-2 border-black/10 pt-12">
                            <h2 className="mb-4 font-serif text-3xl font-black">Questions?</h2>
                            <p className="text-lg text-gray-700">
                                Email us at{' '}
                                <a href="mailto:legal@raptorflow.in" className="font-bold underline">
                                    legal@raptorflow.in
                                </a>
                            </p>
                        </section>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
