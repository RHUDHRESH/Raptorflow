'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

export default function GDPRPage() {
    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            GDPR Compliance
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            Your data rights protected.
                        </h1>
                        <p className="text-lg text-muted-foreground leading-relaxed">
                            How we comply with GDPR and protect your personal data.
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
                                <h2 className="text-2xl font-semibold mb-4">What is GDPR?</h2>
                                <p className="text-muted-foreground">
                                    The General Data Protection Regulation (GDPR) is a regulation in EU law on data protection and privacy for all individuals within the European Union. It also addresses the transfer of personal data outside the EU.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Our Commitment to GDPR</h2>
                                <p className="text-muted-foreground">
                                    RaptorFlow is committed to protecting your personal data and complying with GDPR requirements. We have implemented comprehensive measures to ensure your data is processed lawfully, fairly, and transparently.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Data We Collect</h2>
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Personal Information</h3>
                                        <p className="text-muted-foreground">
                                            Name, email address, and other contact information you provide when creating an account.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Usage Data</h3>
                                        <p className="text-muted-foreground">
                                            Information about how you use our service, including features accessed and time spent.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Technical Data</h3>
                                        <p className="text-muted-foreground">
                                            IP address, browser type, device information, and cookies.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Marketing Content</h3>
                                        <p className="text-muted-foreground">
                                            Campaigns, strategies, and assets you create in our platform.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Legal Basis for Processing</h2>
                                <p className="text-muted-foreground mb-4">
                                    We process your personal data based on the following legal bases:
                                </p>
                                <ul className="space-y-2 text-muted-foreground">
                                    <li>• <strong>Consent:</strong> When you explicitly agree to our processing of your data</li>
                                    <li>• <strong>Contract:</strong> To provide services under our agreement with you</li>
                                    <li>• <strong>Legal Obligation:</strong> When required by law or regulation</li>
                                    <li>• <strong>Legitimate Interest:</strong> For purposes that are necessary for our legitimate business interests</li>
                                </ul>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Your GDPR Rights</h2>
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Right to Access</h3>
                                        <p className="text-muted-foreground">
                                            You have the right to request a copy of your personal data that we hold.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Right to Rectification</h3>
                                        <p className="text-muted-foreground">
                                            You can request correction of inaccurate or incomplete personal data.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Right to Erasure</h3>
                                        <p className="text-muted-foreground">
                                            You can request deletion of your personal data in certain circumstances.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Right to Restrict Processing</h3>
                                        <p className="text-muted-foreground">
                                            You can request restriction of processing your personal data.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Right to Data Portability</h3>
                                        <p className="text-muted-foreground">
                                            You can request transfer of your data to another service provider.
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium mb-2">Right to Object</h3>
                                        <p className="text-muted-foreground">
                                            You can object to processing of your personal data in certain circumstances.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Data Security</h2>
                                <p className="text-muted-foreground">
                                    We implement appropriate technical and organizational measures to protect your personal data, including encryption, access controls, regular security audits, and employee training on data protection.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">International Data Transfers</h2>
                                <p className="text-muted-foreground">
                                    Your data may be processed outside the EU. We ensure appropriate safeguards are in place, including standard contractual clauses and adherence to EU Commission adequacy decisions.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Data Breach Notification</h2>
                                <p className="text-muted-foreground">
                                    In the event of a personal data breach, we will notify affected individuals and relevant authorities within 72 hours of becoming aware of the breach, as required by GDPR.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Data Protection Officer</h2>
                                <p className="text-muted-foreground">
                                    We have appointed a Data Protection Officer (DPO) to oversee our data protection strategy and GDPR compliance. You can contact our DPO at dpo@raptorflow.com.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Children's Data</h2>
                                <p className="text-muted-foreground">
                                    RaptorFlow is not intended for children under 16. We do not knowingly collect personal data from children under 16. If we become aware that we have collected personal data from children without verification of parental consent, we take steps to remove that information immediately.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">How to Exercise Your Rights</h2>
                                <p className="text-muted-foreground mb-4">
                                    To exercise your GDPR rights, please contact us:
                                </p>
                                <div className="bg-muted/50 rounded-lg p-4">
                                    <p className="font-medium mb-2">Email: privacy@raptorflow.com</p>
                                    <p className="text-sm text-muted-foreground">
                                        Please include "GDPR Request" in the subject line and provide sufficient information to identify yourself and your request.
                                    </p>
                                </div>
                                <p className="text-muted-foreground mt-4">
                                    We will respond to your request within one month of receipt, though this may be extended in complex cases.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Changes to This Policy</h2>
                                <p className="text-muted-foreground">
                                    We may update this GDPR policy from time to time to reflect changes in our practices or legal requirements. We will notify you of any significant changes by posting the updated policy on this page.
                                </p>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold mb-4">Contact Information</h2>
                                <p className="text-muted-foreground mb-4">
                                    For GDPR-related inquiries, please contact us:
                                </p>
                                <div className="space-y-2 text-muted-foreground">
                                    <p>Email: privacy@raptorflow.com</p>
                                    <p>DPO: dpo@raptorflow.com</p>
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
                            Questions about your data rights?
                        </h2>
                        <p className="text-lg text-background/70 mb-10">
                            We are committed to protecting your privacy and complying with GDPR.
                        </p>
                        <Button asChild size="lg" variant="secondary" className="h-14 px-8 text-base rounded-xl">
                            <Link href="mailto:privacy@raptorflow.com">Contact DPO</Link>
                        </Button>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
