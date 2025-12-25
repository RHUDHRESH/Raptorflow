'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

export default function PrivacyPage() {
    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Privacy Policy
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            Your privacy matters.
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
                                <h2 className="text-2xl font-semibold mb-4">Introduction</h2>
                                <p className="text-muted-foreground">
                                    RaptorFlow ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and protect your information when you use our marketing operating system.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Information We Collect</h2>
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Account Information</h3>
                                        <p className="text-muted-foreground">
                                            When you create an account, we collect your name, email address, and other information you provide during registration.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Usage Data</h3>
                                        <p className="text-muted-foreground">
                                            We collect information about how you use RaptorFlow, including features accessed, time spent, and interactions with our platform.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Marketing Content</h3>
                                        <p className="text-muted-foreground">
                                            Your campaigns, strategies, assets, and marketing materials stored in our platform. This is your data, not ours.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Technical Data</h3>
                                        <p className="text-muted-foreground">
                                            IP address, browser type, device information, and other technical details needed to provide our service.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">How We Use Your Information</h2>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li>• To provide and maintain RaptorFlow services</li>
                                    <li>• To process your requests and transactions</li>
                                    <li>• To improve our products and user experience</li>
                                    <li>• To communicate with you about your account</li>
                                    <li>• To ensure security and prevent fraud</li>
                                    <li>• To comply with legal obligations</li>
                                </ul>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Data Security</h2>
                                <p className="text-muted-foreground">
                                    We implement industry-standard security measures including encryption, secure servers, and regular security audits. Your data is encrypted both in transit and at rest.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Data Retention</h2>
                                <p className="text-muted-foreground">
                                    We retain your information only as long as necessary to provide our services and comply with legal obligations. You can request deletion of your account and data at any time.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Third-Party Services</h2>
                                <p className="text-muted-foreground">
                                    We use trusted third-party services for payment processing, analytics, and customer support. These services have their own privacy policies and are contractually bound to protect your data.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Your Rights</h2>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li>• Access to your personal information</li>
                                    <li>• Correction of inaccurate data</li>
                                    <li>• Deletion of your account and data</li>
                                    <li>• Portability of your data</li>
                                    <li>• Opt-out of marketing communications</li>
                                </ul>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">International Data Transfers</h2>
                                <p className="text-muted-foreground">
                                    Your data may be processed in countries where we or our service providers operate. We ensure appropriate safeguards are in place for international data transfers.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Children's Privacy</h2>
                                <p className="text-muted-foreground">
                                    RaptorFlow is not intended for children under 13. We do not knowingly collect information from children under 13.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Changes to This Policy</h2>
                                <p className="text-muted-foreground">
                                    We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last updated" date.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
                                <p className="text-muted-foreground mb-4">
                                    If you have questions about this Privacy Policy or want to exercise your rights, please contact us:
                                </p>
                                <div className="space-y-2 text-muted-foreground">
                                    <p>Email: privacy@raptorflow.com</p>
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
                            Questions about your privacy?
                        </h2>
                        <p className="text-lg text-background/70 mb-10">
                            We are here to answer any questions about how we protect your data.
                        </p>
                        <Button asChild size="lg" variant="secondary" className="h-14 px-8 text-base rounded-xl">
                            <Link href="mailto:privacy@raptorflow.com">Contact Privacy Team</Link>
                        </Button>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
