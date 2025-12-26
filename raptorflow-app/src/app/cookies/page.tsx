'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';

export default function CookiesPage() {
    return (
        <MarketingLayout>
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-4xl px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h1 className="font-serif text-5xl lg:text-6xl font-medium text-gray-900 mb-6 leading-tight">
                            Cookie Policy
                        </h1>
                        <p className="text-lg text-gray-600 leading-relaxed max-w-2xl mx-auto">
                            Last updated: December 26, 2024
                        </p>
                    </div>

                    <div className="prose prose-lg max-w-none space-y-8">
                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">What Are Cookies</h2>
                            <p>
                                Cookies are small text files that are stored on your device (computer, tablet, or mobile) when you visit a website. They are widely used to make websites work more efficiently and to provide information to website owners.
                            </p>
                            <p>
                                This Cookie Policy explains how RaptorFlow uses cookies and similar technologies when you visit our website and use our services.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">How We Use Cookies</h2>
                            <p>
                                We use cookies for several purposes to enhance your experience and improve our services:
                            </p>
                            <ul className="list-disc pl-6 space-y-2">
                                <li><strong>Essential Cookies:</strong> These are necessary for the website to function and cannot be switched off in our systems.</li>
                                <li><strong>Performance Cookies:</strong> These help us understand how visitors interact with our website by collecting and reporting information anonymously.</li>
                                <li><strong>Functional Cookies:</strong> These enable the website to provide enhanced functionality and personalization.</li>
                                <li><strong>Marketing Cookies:</strong> These are used to track visitors across websites to display relevant advertisements.</li>
                            </ul>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Types of Cookies We Use</h2>
                            <p>
                                We use the following types of cookies on our website:
                            </p>
                            <ul className="list-disc pl-6 space-y-2">
                                <li><strong>Session Cookies:</strong> These are temporary cookies that are erased when you close your browser.</li>
                                <li><strong>Persistent Cookies:</strong> These remain on your device for a set period or until you delete them.</li>
                                <li><strong>First-Party Cookies:</strong> These are set by our website directly.</li>
                                <li><strong>Third-Party Cookies:</strong> These are set by external services we use on our website.</li>
                            </ul>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Third-Party Cookies</h2>
                            <p>
                                We may use third-party services that set their own cookies on your device when you use our website. These third-party services include:
                            </p>
                            <ul className="list-disc pl-6 space-y-2">
                                <li><strong>Analytics Services:</strong> Google Analytics and similar tools to understand website usage patterns.</li>
                                <li><strong>Payment Processors:</strong> Secure payment gateways for processing subscriptions and transactions.</li>
                                <li><strong>Marketing Platforms:</strong> Tools for tracking campaign performance and user engagement.</li>
                                <li><strong>Social Media:</strong> Integration with social media platforms for sharing and authentication.</li>
                            </ul>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Managing Your Cookie Preferences</h2>
                            <p>
                                You have several options to manage cookies:
                            </p>
                            <ul className="list-disc pl-6 space-y-2">
                                <li><strong>Browser Settings:</strong> Most browsers allow you to control cookies through their settings. You can accept or reject cookies, or delete specific cookies.</li>
                                <li><strong>Cookie Consent Banner:</strong> When you first visit our website, you'll see a cookie consent banner where you can choose which types of cookies to accept.</li>
                                <li><strong>Opt-Out Tools:</strong> Some third-party services provide opt-out tools for their advertising cookies.</li>
                            </ul>
                            <p>
                                Please note that disabling certain cookies may affect the functionality and performance of our website.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Cookie Duration</h2>
                            <p>
                                Different cookies have different lifespans:
                            </p>
                            <ul className="list-disc pl-6 space-y-2">
                                <li><strong>Session Cookies:</strong> Expire when you close your browser</li>
                                <li><strong>Persistent Cookies:</strong> Typically expire after 30 days to 2 years</li>
                                <li><strong>Authentication Cookies:</strong> Expire after 24 hours of inactivity</li>
                                <li><strong>Analytics Cookies:</strong> Expire after 2 years</li>
                            </ul>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Your Rights Under DPDPA 2023</h2>
                            <p>
                                Under the Digital Personal Data Protection Act, 2023, you have the right to:
                            </p>
                            <ul className="list-disc pl-6 space-y-2">
                                <li>Know what personal data is being collected through cookies</li>
                                <li>Withdraw consent for non-essential cookies</li>
                                <li>Request deletion of data collected through cookies</li>
                                <li>Opt out of targeted advertising</li>
                            </ul>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Updates to This Cookie Policy</h2>
                            <p>
                                We may update this Cookie Policy from time to time to reflect changes in our use of cookies, legal requirements, or business practices. We will notify you of any material changes by posting the updated policy on our website and updating the "Last updated" date at the top of this policy.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Contact Information</h2>
                            <div className="space-y-2">
                                <p>
                                    <strong>RaptorFlow</strong><br />
                                    Email: privacy@raptorflow.com<br />
                                    Website: www.raptorflow.com
                                </p>
                                <p className="text-sm">
                                    This Cookie Policy is effective as of December 26, 2024 and complies with the Digital Personal Data Protection Act, 2023 (India).
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="text-center mt-16">
                        <Link href="/" className="inline-flex items-center justify-center rounded-lg bg-gray-900 px-6 py-3 text-white font-medium hover:bg-gray-800 transition-colors">
                            Back to Home
                        </Link>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
