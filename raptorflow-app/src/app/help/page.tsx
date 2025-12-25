'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const helpCategories = [
    {
        title: 'Getting Started',
        articles: [
            'Account Setup',
            'First Campaign',
            'Understanding Foundation',
            'Basic Navigation',
        ],
    },
    {
        title: 'Features',
        articles: [
            'Campaigns',
            'Moves',
            'Muse AI',
            'Analytics',
        ],
    },
    {
        title: 'Billing & Account',
        articles: [
            'Subscription Plans',
            'Payment Methods',
            'Cancellation',
            'Refunds',
        ],
    },
    {
        title: 'Technical Issues',
        articles: [
            'Login Problems',
            'Performance Issues',
            'Data Sync',
            'Browser Compatibility',
        ],
    },
];

export default function HelpPage() {
    return (
        <MarketingLayout>
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Help Center
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            How can we help?
                        </h1>
                        <p className="text-lg text-muted-foreground mb-8">
                            Find answers to common questions or get in touch with our support team.
                        </p>
                        <div className="relative max-w-md mx-auto">
                            <input
                                type="search"
                                placeholder="Search for help..."
                                className="w-full h-12 px-4 pr-12 rounded-xl border border-border"
                            />
                        </div>
                    </div>
                </div>
            </section>

            <section className="pb-24 lg:pb-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="grid lg:grid-cols-2 gap-8">
                        {helpCategories.map((category) => (
                            <div key={category.title} className="rounded-xl border border-border bg-card p-6">
                                <h2 className="text-xl font-semibold mb-4">{category.title}</h2>
                                <div className="space-y-3">
                                    {category.articles.map((article) => (
                                        <div key={article} className="flex items-center justify-between">
                                            <span className="text-muted-foreground">{article}</span>
                                            <Button variant="ghost" size="sm">
                                                →
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <section className="border-y border-border bg-muted/30 py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <h2 className="font-display text-3xl font-medium mb-6">
                            Still need help?
                        </h2>
                        <p className="text-lg text-muted-foreground mb-8">
                            Our support team is here to help you succeed.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Button asChild>
                                <Link href="mailto:support@raptorflow.com">Email Support</Link>
                            </Button>
                            <Button variant="outline" asChild>
                                <Link href="/contact">Contact Us</Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
