'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

export default function TermsPage() {
    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Terms of Service
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            Our agreement.
                        </h1>
                        <p className="text-lg text-muted-foreground leading-relaxed">
                            Last updated: December 20, 2024
                        </p>
                    </div>
                </div>
            </section>

            {/* Content */}
            <section className="pb-24 lg:pb-32">
                <div className="mx-auto max-w-4xl px-6 lg:px-8">
                    <div className="prose prose-lg max-w-none">
                        <div className="space-y-8">
                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Agreement to Terms</h2>
                                <p className="text-muted-foreground">
                                    By accessing and using RaptorFlow ("the Service"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you may not use the Service.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Description of Service</h2>
                                <p className="text-muted-foreground">
                                    RaptorFlow is a marketing operating system that helps founders create, manage, and optimize their marketing campaigns. The Service includes features for strategy development, content creation, campaign management, and analytics.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">User Accounts</h2>
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Registration</h3>
                                        <p className="text-muted-foreground">
                                            You must create an account to use the Service. You agree to provide accurate, current, and complete information during registration.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Account Security</h3>
                                        <p className="text-muted-foreground">
                                            You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Account Termination</h3>
                                        <p className="text-muted-foreground">
                                            You may terminate your account at any time. We reserve the right to suspend or terminate accounts for violations of these Terms.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Subscription Plans and Payment</h2>
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Subscription Fees</h3>
                                        <p className="text-muted-foreground">
                                            RaptorFlow offers various subscription plans with different features and usage limits. Fees are charged monthly or annually as specified in your chosen plan.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Payment Terms</h3>
                                        <p className="text-muted-foreground">
                                            You agree to pay all fees associated with your account. Payments are processed through third-party payment processors, and you agree to their terms.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Refunds</h3>
                                        <p className="text-muted-foreground">
                                            We offer a 14-day free trial for new accounts. After the trial period, refunds are handled on a case-by-case basis.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Acceptable Use</h2>
                                <p className="text-muted-foreground mb-4">You agree not to:</p>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li>• Use the Service for illegal or unauthorized purposes</li>
                                    <li>• Violate any applicable laws or regulations</li>
                                    <li>• Infringe on intellectual property rights</li>
                                    <li>• Distribute malware or engage in harmful activities</li>
                                    <li>• Attempt to gain unauthorized access to our systems</li>
                                    <li>• Use the Service to harass, abuse, or harm others</li>
                                    <li>• Create false or misleading content</li>
                                </ul>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Intellectual Property</h2>
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Our Content</h3>
                                        <p className="text-muted-foreground">
                                            RaptorFlow and its content, features, and functionality are owned by us and protected by intellectual property laws.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Your Content</h3>
                                        <p className="text-muted-foreground">
                                            You retain ownership of all marketing content you create and store in RaptorFlow. You grant us a license to use your content solely to provide and improve the Service.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Privacy</h2>
                                <p className="text-muted-foreground">
                                    Your privacy is important to us. Please review our Privacy Policy, which also governs your use of the Service, to understand our practices.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Service Availability</h2>
                                <p className="text-muted-foreground">
                                    We strive to maintain high availability of the Service but do not guarantee uninterrupted access. We may temporarily suspend the Service for maintenance, updates, or other reasons.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Disclaimer of Warranties</h2>
                                <p className="text-muted-foreground">
                                    The Service is provided "as is" without warranties of any kind. We disclaim all warranties, whether express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Limitation of Liability</h2>
                                <p className="text-muted-foreground">
                                    To the maximum extent permitted by law, RaptorFlow shall not be liable for any indirect, incidental, special, or consequential damages arising from your use of the Service.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Termination</h2>
                                <p className="text-muted-foreground">
                                    We may terminate or suspend your account immediately, without prior notice or liability, for any reason, including if you breach the Terms.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Governing Law</h2>
                                <p className="text-muted-foreground">
                                    These Terms shall be governed by and construed in accordance with the laws of the jurisdiction in which RaptorFlow operates, without regard to conflict of law provisions.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Changes to Terms</h2>
                                <p className="text-muted-foreground">
                                    We reserve the right to modify these Terms at any time. We will notify you of any changes by posting the updated Terms on this page and updating the "Last updated" date.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Contact Information</h2>
                                <p className="text-muted-foreground mb-4">
                                    If you have questions about these Terms, please contact us:
                                </p>
                                <div className="space-y-2 text-muted-foreground">
                                    <p>Email: legal@raptorflow.com</p>
                                    <p>Address: Remote (Global)</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="border-t border-border bg-foreground text-background py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center">
                        <h2 className="font-display text-4xl font-medium mb-6">
                            Ready to get started?
                        </h2>
                        <p className="text-lg text-background/70 mb-10">
                            Join thousands of founders building marketing that compounds.
                        </p>
                        <Button asChild size="lg" variant="secondary" className="h-14 px-8 text-base rounded-xl">
                            <Link href="/foundation">Start Free Trial</Link>
                        </Button>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
