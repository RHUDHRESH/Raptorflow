import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowLeft, Shield, Lock, Eye, Database, UserCheck } from 'lucide-react';

export default function Privacy() {
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
                            <Shield className="h-5 w-5 text-white" />
                            <span className="font-mono text-sm font-bold text-white">Privacy Policy</span>
                        </motion.div>
                        <h1 className="mb-4 font-serif text-6xl font-black tracking-tight">
                            Your Data,
                            <br />
                            Your Control
                        </h1>
                        <p className="text-xl text-gray-600">
                            Last updated: November 25, 2024
                        </p>
                    </div>

                    <div className="space-y-12">
                        {/* What We Collect */}
                        <section>
                            <div className="mb-4 flex items-center gap-3">
                                <Database className="h-6 w-6" />
                                <h2 className="font-serif text-3xl font-black">What We Collect</h2>
                            </div>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    <strong>Account Information:</strong> Email, name, and password (hashed). We use Supabase Auth for secure authentication.
                                </p>
                                <p>
                                    <strong>Strategy Data:</strong> Cohorts, moves, actions, and analytics you create within RaptorFlow. This is your intellectual property.
                                </p>
                                <p>
                                    <strong>Usage Data:</strong> Login times, feature usage, and error logs to improve the product. No third-party tracking pixels.
                                </p>
                            </div>
                        </section>

                        {/* How We Use It */}
                        <section>
                            <div className="mb-4 flex items-center gap-3">
                                <Eye className="h-6 w-6" />
                                <h2 className="font-serif text-3xl font-black">How We Use It</h2>
                            </div>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    We use your data to:
                                </p>
                                <ul className="list-disc space-y-2 pl-6">
                                    <li>Provide and improve RaptorFlow's features</li>
                                    <li>Send you product updates and support emails (you can opt out)</li>
                                    <li>Analyze usage patterns to build better tools</li>
                                    <li>Comply with legal obligations</li>
                                </ul>
                                <p className="font-bold">
                                    We never sell your data. We never share it with advertisers. Period.
                                </p>
                            </div>
                        </section>

                        {/* Data Storage */}
                        <section>
                            <div className="mb-4 flex items-center gap-3">
                                <Lock className="h-6 w-6" />
                                <h2 className="font-serif text-3xl font-black">Data Storage & Security</h2>
                            </div>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    <strong>Where:</strong> All data is stored in Supabase (PostgreSQL) with encryption at rest and in transit.
                                </p>
                                <p>
                                    <strong>Access:</strong> Only you and authorized RaptorFlow team members (for support) can access your data.
                                </p>
                                <p>
                                    <strong>Backups:</strong> Automated daily backups. You can export your data anytime (PDF, Markdown, JSON).
                                </p>
                            </div>
                        </section>

                        {/* Your Rights */}
                        <section>
                            <div className="mb-4 flex items-center gap-3">
                                <UserCheck className="h-6 w-6" />
                                <h2 className="font-serif text-3xl font-black">Your Rights</h2>
                            </div>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>You have the right to:</p>
                                <ul className="list-disc space-y-2 pl-6">
                                    <li><strong>Access:</strong> Request a copy of all your data</li>
                                    <li><strong>Delete:</strong> Permanently delete your account and all associated data</li>
                                    <li><strong>Export:</strong> Download your strategy data in portable formats</li>
                                    <li><strong>Correct:</strong> Update or fix any incorrect information</li>
                                </ul>
                                <p>
                                    To exercise these rights, email us at{' '}
                                    <a href="mailto:privacy@raptorflow.in" className="font-bold underline">
                                        privacy@raptorflow.in
                                    </a>
                                </p>
                            </div>
                        </section>

                        {/* Cookies */}
                        <section>
                            <div className="mb-4 flex items-center gap-3">
                                <Shield className="h-6 w-6" />
                                <h2 className="font-serif text-3xl font-black">Cookies & Tracking</h2>
                            </div>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    We use minimal cookies:
                                </p>
                                <ul className="list-disc space-y-2 pl-6">
                                    <li><strong>Authentication:</strong> To keep you logged in</li>
                                    <li><strong>Preferences:</strong> To remember your settings</li>
                                </ul>
                                <p>
                                    <strong>No Google Analytics. No Facebook Pixel. No third-party trackers.</strong>
                                </p>
                            </div>
                        </section>

                        {/* Changes */}
                        <section>
                            <h2 className="mb-4 font-serif text-3xl font-black">Changes to This Policy</h2>
                            <div className="space-y-4 text-lg leading-relaxed text-gray-700">
                                <p>
                                    We may update this policy occasionally. We'll notify you via email if we make significant changes.
                                </p>
                            </div>
                        </section>

                        {/* Contact */}
                        <section className="border-t-2 border-black/10 pt-12">
                            <h2 className="mb-4 font-serif text-3xl font-black">Questions?</h2>
                            <p className="text-lg text-gray-700">
                                Email us at{' '}
                                <a href="mailto:privacy@raptorflow.in" className="font-bold underline">
                                    privacy@raptorflow.in
                                </a>
                            </p>
                        </section>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
