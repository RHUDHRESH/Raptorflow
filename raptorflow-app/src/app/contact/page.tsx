'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const contactOptions = [
    {
        title: 'Sales & General Inquiries',
        email: 'hello@raptorflow.com',
        description: 'Questions about RaptorFlow, pricing, or getting started? We are here to help.',
        responseTime: 'Within 24 hours',
    },
    {
        title: 'Customer Support',
        email: 'support@raptorflow.com',
        description: 'Need help with your account, have technical questions, or found an issue?',
        responseTime: 'Within 12 hours',
    },
    {
        title: 'Partnerships',
        email: 'partnerships@raptorflow.com',
        description: 'Interested in partnering with us or exploring integration opportunities?',
        responseTime: 'Within 48 hours',
    },
    {
        title: 'Press & Media',
        email: 'press@raptorflow.com',
        description: 'Media inquiries, interview requests, or press kit access.',
        responseTime: 'Within 24 hours',
    },
];

const faqs = [
    {
        question: 'How quickly can I get started with RaptorFlow?',
        answer: 'You can sign up and start building your Foundation in under 10 minutes. No credit card required for the trial.',
    },
    {
        question: 'Do you offer enterprise plans?',
        answer: 'Yes! We offer custom enterprise plans with advanced features, dedicated support, and SLAs. Contact our sales team to learn more.',
    },
    {
        question: 'Can I import my existing marketing data?',
        answer: 'Yes! We support imports from various platforms and can help you migrate your existing campaigns, assets, and customer data.',
    },
    {
        question: 'What kind of support do you provide?',
        answer: 'All plans include email support. Higher tiers include priority support, and enterprise plans get dedicated account managers.',
    },
    {
        question: 'Is my data secure?',
        answer: 'Absolutely. We use enterprise-grade security, encrypt all data, and comply with GDPR and other privacy regulations.',
    },
];

export default function ContactPage() {
    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Contact Us
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            Let's talk.
                        </h1>
                        <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
                            Have questions? Want to see a demo? Need help getting started? We are here to help you succeed.
                        </p>
                    </div>
                </div>
            </section>

            {/* Contact Options */}
            <section className="pb-24 lg:pb-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="grid lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
                        {contactOptions.map((option) => (
                            <div key={option.title} className="rounded-xl border border-border bg-card p-6">
                                <h3 className="text-xl font-semibold mb-3">{option.title}</h3>
                                <p className="text-muted-foreground mb-4">{option.description}</p>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <Button variant="outline" asChild>
                                            <Link href={`mailto:${option.email}`}>{option.email}</Link>
                                        </Button>
                                    </div>
                                    <span className="text-sm text-muted-foreground">{option.responseTime}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Demo Request */}
            <section className="border-y border-border bg-muted/30 py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <h2 className="font-display text-3xl font-medium mb-6">
                            Want a personalized demo?
                        </h2>
                        <p className="text-lg text-muted-foreground mb-8">
                            See how RaptorFlow can transform your marketing with a 30-minute personalized walkthrough.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Button asChild>
                                <Link href="mailto:hello@raptorflow.com?subject=Demo Request">Schedule Demo</Link>
                            </Button>
                            <Button variant="outline" asChild>
                                <Link href="/foundation">Try It Yourself</Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

            {/* FAQs */}
            <section className="py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl font-medium mb-12">Frequently Asked Questions</h2>
                        <div className="space-y-6">
                            {faqs.map((faq) => (
                                <div key={faq.question} className="rounded-xl border border-border bg-card p-6">
                                    <h3 className="font-semibold mb-3">{faq.question}</h3>
                                    <p className="text-muted-foreground">{faq.answer}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Office Hours */}
            <section className="border-y border-border py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <h2 className="font-display text-3xl font-medium mb-6">
                            Founder Office Hours
                        </h2>
                        <p className="text-lg text-muted-foreground mb-8">
                            Every Thursday, our founders host office hours to chat about marketing, strategy, and building products. No sales pitch—just genuine conversation.
                        </p>
                        <div className="bg-muted/50 rounded-xl p-6 mb-8">
                            <div className="text-lg font-medium mb-2">Every Thursday</div>
                            <div className="text-muted-foreground mb-2">2:00 PM - 3:00 PM EST</div>
                            <div className="text-sm text-muted-foreground">30-minute slots available</div>
                        </div>
                        <Button asChild>
                            <Link href="mailto:officehours@raptorflow.com?subject=Office Hours Request">Book a Slot</Link>
                        </Button>
                    </div>
                </div>
            </section>

            {/* Community */}
            <section className="py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <h2 className="font-display text-3xl font-medium mb-6">
                            Join our community
                        </h2>
                        <p className="text-lg text-muted-foreground mb-8">
                            Connect with other founders, share strategies, and get help from the RaptorFlow team.
                        </p>
                        <div className="grid sm:grid-cols-2 gap-4">
                            <Button variant="outline" asChild>
                                <Link href="/community">Join Community Forum</Link>
                            </Button>
                            <Button variant="outline" asChild>
                                <Link href="/blog">Read Our Blog</Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="border-t border-border bg-foreground text-background py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center">
                        <h2 className="font-display text-4xl font-medium mb-6">
                            Ready to stop guessing?
                        </h2>
                        <p className="text-lg text-background/70 mb-10">
                            Start building marketing that actually compounds. No credit card required.
                        </p>
                        <Button asChild size="lg" variant="secondary" className="h-14 px-8 text-base rounded-xl">
                            <Link href="/foundation">Get Started Free</Link>
                        </Button>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
