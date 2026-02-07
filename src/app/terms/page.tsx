'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';

export default function TermsPage() {
    return (
        <MarketingLayout>
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-4xl px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h1 className="font-serif text-5xl lg:text-6xl font-medium text-gray-900 mb-6 leading-tight">
                            Terms of Service
                        </h1>
                        <p className="text-lg text-gray-600 leading-relaxed max-w-2xl mx-auto">
                            Last updated: December 26, 2024
                        </p>
                    </div>

                    <div className="prose prose-lg max-w-none space-y-8">
                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Acceptance of Terms</h2>
                            <p>
                                By accessing and using RaptorFlow ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Description of Service</h2>
                            <p>
                                RaptorFlow is a marketing platform that provides tools and services for creating, managing, and optimizing marketing campaigns. The service includes features such as campaign management, analytics, content creation, and performance tracking.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">User Accounts</h2>
                            <p>
                                To access certain features of the service, you must register for an account. You agree to provide accurate, current, and complete information during registration and to update such information to keep it accurate, current, and complete.
                            </p>
                            <p>
                                You are responsible for safeguarding the password that you use to access the service and for any activities or actions under your password. You agree not to disclose your password to any third party.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">User Content</h2>
                            <p>
                                You retain ownership of all content you create, upload, or share through the service. By using our service, you grant us a license to use, modify, and display your content for the purpose of providing and improving the service.
                            </p>
                            <p>
                                You represent and warrant that you own or have the necessary licenses, rights, consents, and permissions to use and authorize us to use all patent, trademark, trade secret, copyright, or other proprietary rights in and to any and all content to enable inclusion and use of the content in the manner contemplated by the service.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Subscription Plans and Payment</h2>
                            <p>
                                RaptorFlow offers various subscription plans with different features and pricing. You agree to pay all fees and charges incurred in connection with your account at the rates in effect when such charges are incurred.
                            </p>
                            <p>
                                All fees are charged in Indian Rupees (INR) and are non-refundable except as expressly provided in these terms. We reserve the right to modify our fees at any time.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Prohibited Uses</h2>
                            <p>
                                You may not use our service for any illegal or unauthorized purpose. You agree not to use the service to:
                            </p>
                            <ul className="list-disc pl-6 space-y-2">
                                <li>Violate any applicable laws or regulations</li>
                                <li>Infringe upon or violate our intellectual property rights or the intellectual property rights of others</li>
                                <li>Harass, abuse, insult, harm, defame, or discriminate</li>
                                <li>Submit false or misleading information</li>
                                <li>Upload viruses or other malicious code</li>
                                <li>Spam, phish, pharm, pretext, spider, crawl, or scrape</li>
                                <li>Interfere with or circumvent the security features of the service</li>
                            </ul>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Intellectual Property</h2>
                            <p>
                                The service and its original content, features, and functionality are and will remain the exclusive property of RaptorFlow and its licensors. The service is protected by copyright, trademark, and other laws.
                            </p>
                            <p>
                                Our trademarks and trade dress may not be used in connection with any product or service without the prior written consent of RaptorFlow.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Privacy Policy</h2>
                            <p>
                                Your privacy is important to us. Our Privacy Policy explains how we collect, use, and protect your information when you use our service. By using the service, you agree to the collection and use of information in accordance with our Privacy Policy.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Service Availability</h2>
                            <p>
                                We strive to maintain the service's availability, but we do not guarantee that the service will be available at all times. We may experience hardware, software, or other problems that could lead to interruptions.
                            </p>
                            <p>
                                We reserve the right to modify, suspend, or discontinue the service at any time without notice to you.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Disclaimer of Warranties</h2>
                            <p>
                                The service is provided on an "AS IS" and "AS AVAILABLE" basis. We make no representations or warranties of any kind, express or implied, as to the operation of the service or the information, content, materials, or products included on the service.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Limitation of Liability</h2>
                            <p>
                                In no event shall RaptorFlow, our directors, employees, partners, agents, suppliers, or affiliates be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your use of the service.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Governing Law</h2>
                            <p>
                                These terms shall be interpreted and governed by the laws of India, without regard to its conflict of law provisions. Any disputes arising from these terms shall be subject to the exclusive jurisdiction of the courts located in Bengaluru, India.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Changes to Terms</h2>
                            <p>
                                We reserve the right, at our sole discretion, to modify or replace these Terms of Service at any time. If a revision is material, we will provide at least 30 days notice prior to any new terms taking effect.
                            </p>
                        </div>

                        <div className="text-gray-700 leading-relaxed space-y-6">
                            <h2 className="font-serif text-2xl font-medium text-gray-900">Contact Information</h2>
                            <div className="space-y-2">
                                <p>
                                    <strong>RaptorFlow</strong><br />
                                    Email: legal@raptorflow.com<br />
                                    Website: www.raptorflow.com
                                </p>
                                <p className="text-sm">
                                    These Terms of Service are effective as of December 26, 2024 and govern your use of the RaptorFlow service.
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
