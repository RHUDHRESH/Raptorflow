'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

// Feature page data - reusable template pattern
interface FeaturePageData {
    name: string;
    tagline: string;
    description: string;
    problem: {
        title: string;
        description: string;
    };
    solution: {
        title: string;
        steps: { title: string; description: string }[];
    };
    benefits: string[];
    cta: string;
}

const featureData: Record<string, FeaturePageData> = {
    foundation: {
        name: 'Foundation',
        tagline: 'Your BrandKit. Your Positioning. Your Source of Truth.',
        description: 'Build the strategic foundation that makes every piece of marketing connect. No more scattered docs, conflicting messages, or "what do we even say?"',
        problem: {
            title: 'The Problem',
            description: 'Founders spend months with unclear positioning. Every piece of content feels like starting from scratch. Team members tell different stories. The brand lives in your head, not on paper.',
        },
        solution: {
            title: 'How Foundation Works',
            steps: [
                { title: 'Capture Everything', description: 'Our guided intake pulls the strategy out of your head—positioning, proof points, competitive angles, voice.' },
                { title: 'Generate Structure', description: 'AI turns your messy context into organized frameworks: messaging pillars, objection handlers, proof statements.' },
                { title: 'Single Source', description: 'One living document that feeds every campaign, every Move, every asset. Change once, update everywhere.' },
            ],
        },
        benefits: [
            'Never explain your positioning twice',
            'New team members onboard in minutes, not weeks',
            'Every asset speaks with one voice',
            'Positioning that actually differentiates',
        ],
        cta: 'Build Your Foundation',
    },
    cohorts: {
        name: 'Cohorts',
        tagline: 'Know exactly who you are talking to.',
        description: 'Define Ideal Customer Profiles that go beyond demographics. Behavioral segmentation that actually predicts who will buy—and why.',
        problem: {
            title: 'The Problem',
            description: 'Generic personas based on job titles and company size. Marketing that speaks to everyone and resonates with no one. Zero insight into what actually makes someone convert.',
        },
        solution: {
            title: 'How Cohorts Works',
            steps: [
                { title: 'Behavioral Mapping', description: 'Define ICPs by what they do, what they fear, what they want to signal—not just their LinkedIn headline.' },
                { title: 'Segment Intelligence', description: 'Understand which cohorts convert fastest, spend most, and evangelize loudest.' },
                { title: 'Targeted Execution', description: 'Every Move, every campaign, every asset knows exactly which cohort it is speaking to.' },
            ],
        },
        benefits: [
            'Messaging that makes people feel seen',
            'Prioritize cohorts by revenue potential',
            'Stop wasting spend on wrong-fit leads',
            'Content that converts, not just attracts',
        ],
        cta: 'Define Your Cohorts',
    },
    moves: {
        name: 'Moves',
        tagline: 'Weekly execution that actually ships.',
        description: 'Stop planning and start doing. Moves are bite-sized execution packets that turn your 90-day plan into daily action.',
        problem: {
            title: 'The Problem',
            description: 'Grand strategies that never execute. Content calendars that go stale by week 2. The gap between "what we should do" and "what we actually do" is a canyon.',
        },
        solution: {
            title: 'How Moves Works',
            steps: [
                { title: 'Auto-Generated Actions', description: 'AI creates 7 Moves every week based on your campaigns, cohorts, and current priorities.' },
                { title: 'One-Click Execution', description: 'Each Move comes with the asset, the context, the channel, and the tracking—ready to ship.' },
                { title: 'Compounding Progress', description: 'Every Move builds on the last. Weekly momentum instead of weekly reset.' },
            ],
        },
        benefits: [
            'Never wonder "what should I post?"',
            'Consistent execution without constant planning',
            '7+ pieces shipped every single week',
            'Strategy translated into action automatically',
        ],
        cta: 'Start Your First Move',
    },
    campaigns: {
        name: 'Campaigns',
        tagline: '90-day arcs that compound.',
        description: 'Strategic campaigns that build on each other. Not random acts of content, but coordinated efforts with clear outcomes.',
        problem: {
            title: 'The Problem',
            description: 'Posting without a plan. Campaigns that end and leave nothing behind. No connection between this week post and next quarter revenue.',
        },
        solution: {
            title: 'How Campaigns Works',
            steps: [
                { title: 'Strategic Arc Planning', description: 'Define 90-day campaigns with clear themes, outcomes, and cohort focus.' },
                { title: 'Orchestrated Execution', description: 'Campaigns break down into weekly Moves. Every piece serves the arc.' },
                { title: 'Compounding Assets', description: 'Content from one campaign seeds the next. Nothing is throwaway.' },
            ],
        },
        benefits: [
            'Marketing that builds, not just buzzes',
            'Clear connection to revenue outcomes',
            'Campaigns that feed each other',
            'Every week adds to a larger story',
        ],
        cta: 'Plan Your First Campaign',
    },
    muse: {
        name: 'Muse',
        tagline: 'AI content that sounds like you.',
        description: 'Asset generation that actually works—because it is trained on your Foundation, your voice, your strategy.',
        problem: {
            title: 'The Problem',
            description: 'Generic AI content that sounds like everyone else. Hours spent editing ChatGPT output. Content that does not connect to your positioning.',
        },
        solution: {
            title: 'How Muse Works',
            steps: [
                { title: 'Strategy-First Generation', description: 'Muse pulls from your Foundation—positioning, proof, voice—so every asset is on-brand.' },
                { title: 'Cohort-Aware Content', description: 'Generated content speaks to specific ICPs, not generic audiences.' },
                { title: 'Multi-Format Factory', description: 'LinkedIn posts, emails, landing copy, threads—all from a single content engine.' },
            ],
        },
        benefits: [
            'AI that actually sounds like you',
            'Content connected to your strategy',
            '10x faster asset creation',
            'Consistent voice across everything',
        ],
        cta: 'Generate Your First Asset',
    },
    matrix: {
        name: 'Matrix',
        tagline: 'See everything. Control everything.',
        description: 'Your command center. RAG status, progress tracking, and the kill-switch when something is not working.',
        problem: {
            title: 'The Problem',
            description: 'Marketing data scattered across 12 dashboards. No idea what is working. Decisions made on vibes, not data.',
        },
        solution: {
            title: 'How Matrix Works',
            steps: [
                { title: 'Unified Dashboard', description: 'One view for campaigns, Moves, assets, and cohort performance.' },
                { title: 'RAG Status', description: 'Red-Amber-Green signals for everything. Know what needs attention immediately.' },
                { title: 'Strategic Pivots', description: 'Data-driven suggestions for what to double down on and what to kill.' },
            ],
        },
        benefits: [
            'One dashboard, not twelve',
            'Instant clarity on what is working',
            'Data-driven decisions, not vibes',
            'Kill underperformers fast',
        ],
        cta: 'See Your Matrix',
    },
    blackbox: {
        name: 'Blackbox',
        tagline: 'Prove what works.',
        description: 'Automatic A/B testing and experiments. Stop guessing. Start knowing.',
        problem: {
            title: 'The Problem',
            description: 'Marketing by gut feel. No idea if that landing page actually converts. Zero experimentation culture because "we do not have time."',
        },
        solution: {
            title: 'How Blackbox Works',
            steps: [
                { title: 'Auto-Generated Experiments', description: 'Blackbox suggests tests based on your campaigns and historical performance.' },
                { title: 'Easy Execution', description: 'One-click A/B tests on headlines, CTAs, messaging angles, and more.' },
                { title: 'Clear Winners', description: 'Statistical significance, not opinions. Know what works and why.' },
            ],
        },
        benefits: [
            'Testing without the overhead',
            'Decisions backed by data',
            'Continuous optimization built-in',
            'Learn what resonates, fast',
        ],
        cta: 'Run Your First Experiment',
    },
    radar: {
        name: 'Radar',
        tagline: 'Know what your competitors do not.',
        description: 'Competitor intelligence that keeps you three moves ahead. Positioning gaps, messaging patterns, opportunity windows.',
        problem: {
            title: 'The Problem',
            description: 'Competitors launch something and you find out on Twitter. No systematic way to track the market. Positioning in a vacuum.',
        },
        solution: {
            title: 'How Radar Works',
            steps: [
                { title: 'Competitor Tracking', description: 'Monitor messaging, positioning, and campaigns across your competitive set.' },
                { title: 'Gap Analysis', description: 'Find positioning whitespace your competitors are not occupying.' },
                { title: 'Opportunity Alerts', description: 'Get notified when competitors shift, so you can respond strategically.' },
            ],
        },
        benefits: [
            'Stay ahead, not reactive',
            'Find positioning gaps to own',
            'Competitive context for every campaign',
            'Market intelligence on autopilot',
        ],
        cta: 'Activate Radar',
    },
};

interface FeaturePageProps {
    params: Promise<{ feature: string }>;
}

export default async function FeaturePage({ params }: FeaturePageProps) {
    const { feature } = await params;
    const data = featureData[feature];

    if (!data) {
        return (
            <MarketingLayout>
                <div className="mx-auto max-w-7xl px-6 lg:px-8 py-24 text-center">
                    <h1 className="font-display text-4xl">Feature not found</h1>
                    <p className="mt-4 text-muted-foreground">The feature you are looking for does not exist.</p>
                    <Button asChild className="mt-8">
                        <Link href="/landing">Back to Home</Link>
                    </Button>
                </div>
            </MarketingLayout>
        );
    }

    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            {data.name}
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            {data.tagline}
                        </h1>
                        <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
                            {data.description}
                        </p>
                    </div>
                </div>
            </section>

            {/* Problem */}
            <section className="border-y border-border bg-muted/30 py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-6">{data.problem.title}</h2>
                        <p className="text-lg text-muted-foreground leading-relaxed">{data.problem.description}</p>
                    </div>
                </div>
            </section>

            {/* Solution / How It Works */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl mb-16">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium">{data.solution.title}</h2>
                    </div>
                    <div className="grid lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {data.solution.steps.map((step, index) => (
                            <div key={step.title}>
                                <div className="text-5xl font-mono font-bold text-muted/30 mb-4">0{index + 1}</div>
                                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                                <p className="text-muted-foreground leading-relaxed">{step.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Benefits */}
            <section className="border-y border-border bg-muted/30 py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-8">What You Get</h2>
                        <ul className="space-y-4">
                            {data.benefits.map((benefit) => (
                                <li key={benefit} className="flex items-start gap-4">
                                    <div className="h-6 w-6 rounded-full bg-foreground flex items-center justify-center flex-shrink-0 mt-0.5">
                                        <svg className="h-3 w-3 text-background" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                    <span className="text-lg">{benefit}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center">
                        <h2 className="font-display text-4xl lg:text-5xl font-medium mb-6">
                            Ready to start?
                        </h2>
                        <Button asChild size="lg" className="h-14 px-8 text-base rounded-xl">
                            <Link href="/foundation">{data.cta}</Link>
                        </Button>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
