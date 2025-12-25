'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

export default function CookiesPage() {
    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Cookie Policy
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            How we use cookies.
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
                                <h2 className="text-2xl font-semibold mb-4">What Are Cookies</h2>
                                <p className="text-muted-foreground">
                                    Cookies are small text files that are stored on your device when you visit websites. They help us provide you with a better experience by remembering your preferences and improving website functionality.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">How We Use Cookies</h2>
                                <p className="text-muted-foreground mb-4">
                                    We use cookies for several purposes:
                                </p>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li>• <strong>Essential Cookies:</strong> Required for the website to function properly</li>
                                    <li>• <strong>Performance Cookies:</strong> Help us understand how visitors interact with our website</li>
                                    <li>• <strong>Functional Cookies:</strong> Remember your preferences and settings</li>
                                    <li>• <strong>Marketing Cookies:</strong> Used to deliver relevant advertisements and track marketing campaigns</li>
                                </ul>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Types of Cookies We Use</h2>
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Essential Cookies</h3>
                                        <p className="text-muted-foreground">
                                            These cookies are necessary for the website to function and cannot be switched off. They include authentication cookies and security tokens.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Analytics Cookies</h3>
                                        <p className="text-muted-foreground">
                                            We use Google Analytics and similar tools to understand how our website is used. This helps us improve user experience and website performance.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Functional Cookies</h3>
                                        <p className="text-muted-foreground">
                                            These cookies remember your preferences, such as language settings and login status, to provide a more personalized experience.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Advertising Cookies</h3>
                                        <p className="text-muted-foreground">
                                            These cookies are used to deliver advertisements that are relevant to you and your interests. They also help us measure the effectiveness of our marketing campaigns.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Third-Party Cookies</h2>
                                <p className="text-muted-foreground mb-4">
                                    We use third-party services that may place cookies on your device:
                                </p>
                                <div className="space-y-3">
                                    <div className="bg-muted/50 rounded-lg p-4">
                                        <h4 className="font-medium mb-1">Google Analytics</h4>
                                        <p className="text-sm text-muted-foreground">
                                            Used for website analytics and performance monitoring.
                                        </p>
                                    </div>
                                    <div className="bg-muted/50 rounded-lg p-4">
                                        <h4 className="font-medium mb-1">Payment Processors</h4>
                                        <p className="text-sm text-muted-foreground">
                                            Stripe and other payment providers use cookies for secure payment processing.
                                        </p>
                                    </div>
                                    <div className="bg-muted/50 rounded-lg p-4">
                                        <h4 className="font-medium mb-1">Customer Support</h4>
                                        <p className="text-sm text-muted-foreground">
                                            Intercom and similar tools use cookies for customer support functionality.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Managing Your Cookie Preferences</h2>
                                <p className="text-muted-foreground mb-4">
                                    You can control cookies in several ways:
                                </p>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li>• <strong>Browser Settings:</strong> Most browsers allow you to block or delete cookies through their settings</li>
                                    <li>• <strong>Cookie Banner:</strong> Use our cookie consent banner to manage preferences when you first visit</li>
                                    <li>• <strong>Privacy Settings:</strong> Update your preferences at any time through your account settings</li>
                                </ul>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Cookie Duration</h2>
                                <p className="text-muted-foreground mb-4">
                                    Cookies have different lifespans:
                                </p>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li>• <strong>Session Cookies:</strong> Expire when you close your browser</li>
                                    <li>• <strong>Persistent Cookies:</strong> Remain on your device for a set period or until you delete them</li>
                                    <li>• <strong>Authentication Cookies:</strong> Typically last 30 days to maintain your login session</li>
                                </ul>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Your Rights</h2>
                                <p className="text-muted-foreground">
                                    You have the right to accept or reject non-essential cookies. However, please note that blocking certain cookies may affect your user experience and some features of the website may not function properly.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">International Data Transfers</h2>
                                <p className="text-muted-foreground">
                                    Some third-party services may process your data outside your country. We ensure that appropriate safeguards are in place for international data transfers, including standard contractual clauses and other legal mechanisms.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Updates to This Policy</h2>
                                <p className="text-muted-foreground">
                                    We may update this Cookie Policy from time to time to reflect changes in our practices or for legal reasons. We will notify you of any significant changes by posting the updated policy on this page.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
                                <p className="text-muted-foreground mb-4">
                                    If you have questions about our use of cookies, please contact us:
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
                            Questions about cookies?
                        </h2>
                        <p className="text-lg text-background/70 mb-10">
                            We are transparent about how we use data to improve your experience.
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
