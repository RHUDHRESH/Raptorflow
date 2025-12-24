'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const plans = [
    {
        name: 'Ascent',
        price: '5,000',
        description: 'For founders just getting started with systematic marketing.',
        features: [
            { name: 'Active Campaigns', value: '3' },
            { name: 'Moves / month', value: '20' },
            { name: 'Move Generations', value: '60' },
            { name: 'Cohorts', value: '3' },
            { name: 'Matrix Access', included: true },
            { name: 'Blackbox (Lab A/B)', included: false },
            { name: 'Radar Access', included: false },
            { name: 'Support', value: 'Email' },
        ],
        cta: 'Start with Ascent',
        popular: false,
    },
    {
        name: 'Glide',
        price: '7,000',
        description: 'For growing teams ready to scale their marketing machine.',
        features: [
            { name: 'Active Campaigns', value: '6' },
            { name: 'Moves / month', value: '60' },
            { name: 'Move Generations', value: '200' },
            { name: 'Cohorts', value: '6' },
            { name: 'Matrix Access', included: true },
            { name: 'Blackbox (Lab A/B)', included: true },
            { name: 'Radar Access', included: true },
            { name: 'Support', value: 'Priority' },
        ],
        cta: 'Start with Glide',
        popular: true,
    },
    {
        name: 'Soar',
        price: '10,000',
        description: 'For serious operators running multiple campaigns at scale.',
        features: [
            { name: 'Active Campaigns', value: '9' },
            { name: 'Moves / month', value: '150' },
            { name: 'Move Generations', value: '700' },
            { name: 'Cohorts', value: '9' },
            { name: 'Matrix Access', included: true },
            { name: 'Blackbox (Lab A/B)', included: true },
            { name: 'Radar Access', included: true },
            { name: 'Support', value: 'Dedicated' },
        ],
        cta: 'Start with Soar',
        popular: false,
    },
];

const faqs = [
    {
        question: 'Can I change plans later?',
        answer: 'Yes, you can upgrade or downgrade at any time. Changes take effect at the start of your next billing cycle.',
    },
    {
        question: 'What counts as a "Move"?',
        answer: 'A Move is a single execution packet—one piece of content with its context, channel, and tracking. 20 Moves means you ship 20 pieces of marketing per month.',
    },
    {
        question: 'What is the difference between Moves and Move Generations?',
        answer: 'Moves are what you ship. Move Generations are AI-generated options you can choose from. More generations = more options to find the perfect angle.',
    },
    {
        question: 'Is there a free trial?',
        answer: 'Yes! All plans include a 14-day free trial. No credit card required to start.',
    },
];

export default function PricingPage() {
    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Pricing
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            Simple, honest pricing.
                        </h1>
                        <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
                            No hidden fees. No surprise charges. Just marketing that compounds.
                        </p>
                    </div>
                </div>
            </section>

            {/* Pricing Cards */}
            <section className="pb-24 lg:pb-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="grid lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {plans.map((plan) => (
                            <div
                                key={plan.name}
                                className={`rounded-2xl border p-8 relative ${plan.popular
                                        ? 'border-2 border-foreground bg-card'
                                        : 'border-border bg-card'
                                    }`}
                            >
                                {plan.popular && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-foreground text-background px-4 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                                        Most Popular
                                    </div>
                                )}

                                <div className={plan.popular ? 'mt-2' : ''}>
                                    <h3 className="text-xl font-semibold">{plan.name}</h3>
                                    <p className="mt-2 text-sm text-muted-foreground">{plan.description}</p>

                                    <div className="mt-6 flex items-baseline">
                                        <span className="text-4xl font-mono font-semibold">₹{plan.price}</span>
                                        <span className="ml-2 text-muted-foreground">/month</span>
                                    </div>

                                    <Button
                                        asChild
                                        className={`mt-8 w-full h-12 rounded-xl ${plan.popular ? '' : 'bg-muted text-foreground hover:bg-muted/80'
                                            }`}
                                        variant={plan.popular ? 'default' : 'secondary'}
                                    >
                                        <Link href="/foundation">{plan.cta}</Link>
                                    </Button>

                                    <ul className="mt-8 space-y-4">
                                        {plan.features.map((feature) => (
                                            <li key={feature.name} className="flex items-center justify-between text-sm">
                                                <span className="text-muted-foreground">{feature.name}</span>
                                                {feature.included !== undefined ? (
                                                    feature.included ? (
                                                        <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                        </svg>
                                                    ) : (
                                                        <svg className="h-5 w-5 text-muted-foreground/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                        </svg>
                                                    )
                                                ) : (
                                                    <span className="font-medium">{feature.value}</span>
                                                )}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Feature Comparison Quote */}
            <section className="border-y border-border bg-muted/30 py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <blockquote className="mx-auto max-w-3xl text-center">
                        <p className="text-2xl font-display font-medium text-foreground">
                            &quot;Not another tool. A system: decide → ship → measure → iterate.&quot;
                        </p>
                    </blockquote>
                </div>
            </section>

            {/* Pricing FAQs */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-12 text-center">
                            Common Questions
                        </h2>
                        <div className="space-y-6">
                            {faqs.map((faq) => (
                                <div key={faq.question} className="rounded-xl border border-border bg-card p-6">
                                    <h3 className="font-semibold mb-2">{faq.question}</h3>
                                    <p className="text-muted-foreground">{faq.answer}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="border-t border-border bg-foreground text-background py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center">
                        <h2 className="font-display text-4xl font-medium mb-6">
                            Start free. Upgrade when you are ready.
                        </h2>
                        <p className="text-lg text-background/70 mb-10">
                            14-day trial on all plans. No credit card required.
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
