'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

// Feature data
const features = [
    {
        name: 'Foundation',
        description: 'Build your BrandKit, positioning, and messaging architecture in one place.',
        href: '/features/foundation',
        icon: (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
        ),
    },
    {
        name: 'Cohorts',
        description: 'Define and track your Ideal Customer Profiles with behavioral segmentation.',
        href: '/features/cohorts',
        icon: (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
            </svg>
        ),
    },
    {
        name: 'Moves',
        description: 'Weekly execution packets that turn strategy into action.',
        href: '/features/moves',
        icon: (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
        ),
    },
    {
        name: 'Campaigns',
        description: '90-day strategic arcs that compound your marketing efforts.',
        href: '/features/campaigns',
        icon: (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
            </svg>
        ),
    },
    {
        name: 'Muse',
        description: 'AI-powered asset factory for content that actually converts.',
        href: '/features/muse',
        icon: (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
            </svg>
        ),
    },
    {
        name: 'Matrix',
        description: 'Your command center. See everything. Control everything.',
        href: '/features/matrix',
        icon: (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
            </svg>
        ),
    },
    {
        name: 'Blackbox',
        description: 'A/B testing and experiments that prove what works.',
        href: '/features/blackbox',
        icon: (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
            </svg>
        ),
    },
    {
        name: 'Radar',
        description: 'Competitor intelligence that keeps you three moves ahead.',
        href: '/features/radar',
        icon: (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7.5 3.75H6A2.25 2.25 0 003.75 6v1.5M16.5 3.75H18A2.25 2.25 0 0120.25 6v1.5m0 9V18A2.25 2.25 0 0118 20.25h-1.5m-9 0H6A2.25 2.25 0 013.75 18v-1.5M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
        ),
    },
];

// Comparison data
const comparison = {
    without: [
        { label: 'Content', value: 'ChatGPT + Pray' },
        { label: 'Tasks', value: '5 scattered apps' },
        { label: 'Testing', value: '"Hope it works"' },
        { label: 'Strategy', value: 'Vibes only' },
        { label: 'Data', value: 'Zero' },
    ],
    with: [
        { label: 'Content', value: 'AI writes from your strategy' },
        { label: 'Tasks', value: 'One daily checklist' },
        { label: 'Testing', value: 'Automatic A/B testing' },
        { label: 'Strategy', value: '90-day war plan' },
        { label: 'Data', value: 'Everything tracked' },
    ],
};

// Stats
const stats = [
    { value: '10', unit: 'min', label: 'to build your 90-day plan' },
    { value: '1', unit: 'system', label: 'instead of 5+ tools' },
    { value: '7', unit: 'moves', label: 'shipped every week' },
];

export default function LandingPage() {
    return (
        <MarketingLayout>
            {/* Hero Section */}
            <section className="relative overflow-hidden">
                <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24 lg:py-32">
                    <div className="mx-auto max-w-3xl text-center">
                        {/* Eyebrow */}
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-6">
                            The Founder Marketing Operating System
                        </p>

                        {/* Main Headline */}
                        <h1 className="font-display text-5xl lg:text-7xl font-medium tracking-tight text-foreground mb-6">
                            Marketing.
                            <br />
                            <span className="text-muted-foreground">Finally under control.</span>
                        </h1>

                        {/* Subheadline */}
                        <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed mb-10 max-w-2xl mx-auto">
                            Turn messy business context into clear positioning and a 90-day marketing war plan—then ship weekly Moves that drive revenue.
                        </p>

                        {/* CTAs */}
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Button asChild size="lg" className="h-14 px-8 text-base rounded-xl">
                                <Link href="/foundation">Get Started Free</Link>
                            </Button>
                            <Button asChild variant="outline" size="lg" className="h-14 px-8 text-base rounded-xl">
                                <Link href="#features">See How It Works</Link>
                            </Button>
                        </div>

                        {/* Trust line */}
                        <p className="mt-8 text-sm text-muted-foreground">
                            No credit card required. Start in 2 minutes.
                        </p>
                    </div>
                </div>

                {/* Gradient background */}
                <div className="absolute inset-0 -z-10 overflow-hidden">
                    <div className="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-foreground/5 to-transparent blur-3xl" />
                </div>
            </section>

            {/* Pain Point Quote */}
            <section className="border-y border-border bg-muted/30">
                <div className="mx-auto max-w-7xl px-6 lg:px-8 py-16">
                    <blockquote className="mx-auto max-w-3xl text-center">
                        <p className="text-2xl lg:text-3xl font-display font-medium text-foreground leading-relaxed">
                            "If your marketing is confusing, you're losing—silently."
                        </p>
                    </blockquote>
                </div>
            </section>

            {/* Comparison Section */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center mb-16">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            The Difference
                        </p>
                        <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
                            Before & After
                        </h2>
                    </div>

                    <div className="grid lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
                        {/* Without */}
                        <div className="rounded-2xl border border-border bg-card p-8">
                            <div className="flex items-center gap-3 mb-8">
                                <div className="h-10 w-10 rounded-full bg-destructive/10 flex items-center justify-center">
                                    <svg className="h-5 w-5 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </div>
                                <h3 className="text-xl font-semibold">Without RaptorFlow</h3>
                            </div>
                            <ul className="space-y-4">
                                {comparison.without.map((item) => (
                                    <li key={item.label} className="flex items-center justify-between py-3 border-b border-border last:border-0">
                                        <span className="text-muted-foreground">{item.label}</span>
                                        <span className="font-medium text-foreground">{item.value}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* With */}
                        <div className="rounded-2xl border-2 border-foreground bg-card p-8 relative">
                            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-foreground text-background px-4 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                                With RaptorFlow
                            </div>
                            <div className="flex items-center gap-3 mb-8 mt-2">
                                <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                                    <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                </div>
                                <h3 className="text-xl font-semibold">Marketing Machine</h3>
                            </div>
                            <ul className="space-y-4">
                                {comparison.with.map((item) => (
                                    <li key={item.label} className="flex items-center justify-between py-3 border-b border-border last:border-0">
                                        <span className="text-muted-foreground">{item.label}</span>
                                        <span className="font-medium text-foreground">{item.value}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="border-y border-border bg-muted/30 py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="grid grid-cols-3 gap-8">
                        {stats.map((stat) => (
                            <div key={stat.label} className="text-center">
                                <div className="flex items-baseline justify-center gap-1">
                                    <span className="font-mono text-4xl lg:text-5xl font-semibold tracking-tight">{stat.value}</span>
                                    <span className="text-lg text-muted-foreground">{stat.unit}</span>
                                </div>
                                <p className="mt-2 text-sm text-muted-foreground">{stat.label}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center mb-16">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            The System
                        </p>
                        <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
                            Clarify. Build. Run.
                        </h2>
                        <p className="mt-4 text-lg text-muted-foreground">
                            Three steps to marketing that compounds instead of resetting every Monday.
                        </p>
                    </div>

                    <div className="grid lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {[
                            {
                                step: '01',
                                title: 'Clarify',
                                description: 'Intake → ICP → positioning → proof. We turn your messy context into crystal-clear strategy.',
                            },
                            {
                                step: '02',
                                title: 'Build',
                                description: '90-day war plan → weekly Moves → assets. Every piece connects to your positioning.',
                            },
                            {
                                step: '03',
                                title: 'Run',
                                description: 'Publish → track → tweak. Results compound because every week builds on the last.',
                            },
                        ].map((item) => (
                            <div key={item.step} className="relative">
                                <div className="text-6xl font-mono font-bold text-muted/30 mb-4">{item.step}</div>
                                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                                <p className="text-muted-foreground leading-relaxed">{item.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section id="features" className="py-24 lg:py-32 border-t border-border bg-muted/30">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center mb-16">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Everything You Need
                        </p>
                        <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight">
                            One System. Zero Chaos.
                        </h2>
                        <p className="mt-4 text-lg text-muted-foreground">
                            Not another tool. A complete marketing operating system.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {features.map((feature) => (
                            <Link
                                key={feature.name}
                                href={feature.href}
                                className="group rounded-2xl border border-border bg-card p-6 hover:border-foreground/20 hover:-translate-y-1 transition-all duration-200"
                            >
                                <div className="h-12 w-12 rounded-xl bg-muted flex items-center justify-center text-foreground mb-4 group-hover:bg-foreground group-hover:text-background transition-colors">
                                    {feature.icon}
                                </div>
                                <h3 className="text-lg font-semibold mb-2">{feature.name}</h3>
                                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
                            </Link>
                        ))}
                    </div>
                </div>
            </section>

            {/* Testimonial / Quote */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <blockquote>
                            <p className="font-display text-3xl lg:text-4xl font-medium leading-relaxed text-foreground">
                                "You shouldn't have to guess your marketing.
                                <br />
                                <span className="text-muted-foreground">With RaptorFlow, you won't."</span>
                            </p>
                        </blockquote>
                    </div>
                </div>
            </section>

            {/* Final CTA */}
            <section className="border-t border-border bg-foreground text-background">
                <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24">
                    <div className="mx-auto max-w-2xl text-center">
                        <h2 className="font-display text-4xl lg:text-5xl font-medium tracking-tight mb-6">
                            Stop trying marketing.
                            <br />
                            Start running a machine.
                        </h2>
                        <p className="text-lg text-background/70 mb-10">
                            Give us your messy context. We'll turn it into a plan you can actually execute.
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
