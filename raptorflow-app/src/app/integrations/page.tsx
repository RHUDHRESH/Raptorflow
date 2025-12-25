'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const integrations = [
    {
        category: 'Data & Analytics',
        items: [
            {
                name: 'Google Analytics',
                description: 'Track campaign performance and user behavior with real-time insights and custom dashboards',
                status: 'Available',
                setupTime: '5 min',
                features: ['Real-time tracking', 'Custom reports', 'Goal conversion', 'Audience insights'],
                pricing: 'Free'
            },
            {
                name: 'Mixpanel',
                description: 'Advanced product analytics and funnel tracking with cohort analysis and retention metrics',
                status: 'Available',
                setupTime: '10 min',
                features: ['Funnel analysis', 'Retention tracking', 'Cohort analysis', 'Custom events'],
                pricing: 'Free tier available'
            },
            {
                name: 'Segment',
                description: 'Customer data platform for unified tracking across all your marketing tools',
                status: 'Coming Soon',
                setupTime: '15 min',
                features: ['Data collection', 'Identity resolution', 'Audience building', 'Data governance'],
                pricing: 'Starting at $120/month'
            },
        ],
    },
    {
        category: 'Email & Communication',
        items: [
            {
                name: 'SendGrid',
                description: 'Transactional email and marketing campaigns with advanced deliverability and analytics',
                status: 'Available',
                setupTime: '5 min',
                features: ['Email delivery', 'Template engine', 'Analytics', 'A/B testing'],
                pricing: 'Free tier available'
            },
            {
                name: 'Mailgun',
                description: 'Reliable email delivery service with powerful APIs and email validation',
                status: 'Available',
                setupTime: '5 min',
                features: ['Email APIs', 'Validation', 'Analytics', 'Routing rules'],
                pricing: 'Free tier available'
            },
            {
                name: 'Postmark',
                description: 'High-performance email delivery with lightning-fast speeds and excellent deliverability',
                status: 'Coming Soon',
                setupTime: '5 min',
                features: ['Fast delivery', 'Template management', 'Analytics', 'Dedicated IPs'],
                pricing: 'Starting at $10/month'
            },
        ],
    },
    {
        category: 'CRM & Sales',
        items: [
            {
                name: 'HubSpot',
                description: 'Complete CRM platform for growing businesses with marketing, sales, and service tools',
                status: 'Available',
                setupTime: '15 min',
                features: ['Contact management', 'Deal tracking', 'Marketing automation', 'Reporting'],
                pricing: 'Free tier available'
            },
            {
                name: 'Salesforce',
                description: 'Enterprise CRM and sales automation with extensive customization options',
                status: 'Coming Soon',
                setupTime: '30 min',
                features: ['Sales cloud', 'Service cloud', 'Custom objects', 'AppExchange'],
                pricing: 'Starting at $25/user/month'
            },
            {
                name: 'Pipedrive',
                description: 'Sales-focused CRM for small teams with visual pipeline management',
                status: 'Coming Soon',
                setupTime: '10 min',
                features: ['Visual pipeline', 'Activity tracking', 'Deal management', 'Mobile app'],
                pricing: 'Starting at $14/user/month'
            },
        ],
    },
    {
        category: 'Social Media',
        items: [
            {
                name: 'Twitter API',
                description: 'Post and monitor Twitter campaigns with advanced analytics and engagement tracking',
                status: 'Available',
                setupTime: '10 min',
                features: ['Tweet scheduling', 'Analytics', 'Hashtag tracking', 'Engagement metrics'],
                pricing: 'Free tier available'
            },
            {
                name: 'LinkedIn API',
                description: 'Professional networking and B2B marketing with company page management',
                status: 'Available',
                setupTime: '10 min',
                features: ['Company updates', 'Employee advocacy', 'Lead generation', 'Analytics'],
                pricing: 'Free tier available'
            },
            {
                name: 'Meta Business Suite',
                description: 'Facebook and Instagram management with advanced ad targeting and insights',
                status: 'Coming Soon',
                setupTime: '15 min',
                features: ['Post scheduling', 'Ad management', 'Audience insights', 'Cross-platform'],
                pricing: 'Free with paid ads'
            },
        ],
    },
    {
        category: 'Storage & CDN',
        items: [
            {
                name: 'AWS S3',
                description: 'Scalable object storage for assets with enterprise-grade security and performance',
                status: 'Available',
                setupTime: '10 min',
                features: ['Object storage', 'CDN integration', 'Version control', 'Security'],
                pricing: 'Pay-as-you-go'
            },
            {
                name: 'Cloudflare R2',
                description: 'Zero-egress storage solution with global CDN and DDoS protection',
                status: 'Available',
                setupTime: '10 min',
                features: ['Zero egress fees', 'Global CDN', 'DDoS protection', 'API access'],
                pricing: 'Pay-as-you-go'
            },
            {
                name: 'Google Cloud Storage',
                description: 'Enterprise-grade storage platform with advanced security and analytics',
                status: 'Coming Soon',
                setupTime: '15 min',
                features: ['Object storage', 'ML analytics', 'Security', 'Data lifecycle'],
                pricing: 'Pay-as-you-go'
            },
        ],
    },
    {
        category: 'Marketing Automation',
        items: [
            {
                name: 'Zapier',
                description: 'Connect 5000+ apps with automated workflows and custom logic',
                status: 'Available',
                setupTime: '5 min',
                features: ['Workflow automation', 'Multi-step zaps', 'Filters', 'Scheduling'],
                pricing: 'Free tier available'
            },
            {
                name: 'Make (Integromat)',
                description: 'Visual automation platform with advanced scenario building',
                status: 'Coming Soon',
                setupTime: '10 min',
                features: ['Visual builder', 'Advanced logic', 'Error handling', 'Monitoring'],
                pricing: 'Free tier available'
            },
        ],
    },
];

export default function IntegrationsPage() {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('All');

    const categories = ['All', ...integrations.map(cat => cat.category)];

    const filteredIntegrations = integrations.filter(category => {
        const matchesCategory = selectedCategory === 'All' || category.category === selectedCategory;
        const matchesSearch = category.items.some(item =>
            item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
        return matchesCategory && matchesSearch;
    });

    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Integrations
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            Connect your entire stack.
                        </h1>
                        <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed mb-8">
                            RaptorFlow seamlessly integrates with 100+ tools you already use. No migration required.
                            Set up in minutes, not months.
                        </p>

                        {/* Search and Filter */}
                        <div className="max-w-2xl mx-auto space-y-4">
                            <div className="relative">
                                <input
                                    type="search"
                                    placeholder="Search integrations..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-full h-12 px-4 pr-12 rounded-xl border border-border bg-background text-lg"
                                />
                                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                                    <svg className="h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                    </svg>
                                </div>
                            </div>

                            {/* Category Filter */}
                            <div className="flex flex-wrap gap-2 justify-center">
                                {categories.map((category) => (
                                    <button
                                        key={category}
                                        onClick={() => setSelectedCategory(category)}
                                        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                                            selectedCategory === category
                                                ? 'bg-foreground text-background'
                                                : 'bg-muted text-muted-foreground hover:bg-foreground/10'
                                        }`}
                                    >
                                        {category}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Integration Categories */}
            <section className="pb-24 lg:pb-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="space-y-16">
                        {filteredIntegrations.map((category) => (
                            <div key={category.category}>
                                <h2 className="font-display text-2xl font-semibold mb-8">{category.category}</h2>
                                <div className="grid lg:grid-cols-3 gap-6">
                                    {category.items.map((integration) => (
                                        <div
                                            key={integration.name}
                                            className="rounded-xl border border-border bg-card p-6 hover:border-foreground/20 transition-all duration-200 hover:shadow-lg"
                                        >
                                            <div className="flex items-start justify-between mb-4">
                                                <h3 className="font-semibold text-lg">{integration.name}</h3>
                                                <span
                                                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                                                        integration.status === 'Available'
                                                            ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                                                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                                                    }`}
                                                >
                                                    {integration.status}
                                                </span>
                                            </div>

                                            <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
                                                {integration.description}
                                            </p>

                                            {/* Features */}
                                            <div className="mb-4">
                                                <div className="flex flex-wrap gap-1">
                                                    {integration.features.map((feature) => (
                                                        <span key={feature} className="text-xs bg-muted px-2 py-1 rounded-md">
                                                            {feature}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>

                                            {/* Setup Time & Pricing */}
                                            <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                                                <div className="flex items-center gap-1">
                                                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                    </svg>
                                                    <span>{integration.setupTime}</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                                                    </svg>
                                                    <span>{integration.pricing}</span>
                                                </div>
                                            </div>

                                            {integration.status === 'Available' ? (
                                                <div className="space-y-2">
                                                    <Button className="w-full">
                                                        Connect Now
                                                    </Button>
                                                    <Button variant="outline" size="sm" className="w-full">
                                                        View Documentation
                                                    </Button>
                                                </div>
                                            ) : (
                                                <div className="space-y-2">
                                                    <Button variant="outline" className="w-full">
                                                        Join Waitlist
                                                    </Button>
                                                    <Button variant="ghost" size="sm" className="w-full">
                                                        Get Notified
                                                    </Button>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Developer Section */}
            <section className="border-y border-border bg-muted/30 py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <h2 className="font-display text-3xl font-medium mb-6">
                            Build your own integrations
                        </h2>
                        <p className="text-lg text-muted-foreground mb-8">
                            Use our REST API and webhooks to connect RaptorFlow with any tool in your stack.
                            Full documentation, SDKs, and developer support included.
                        </p>

                        {/* API Features */}
                        <div className="grid md:grid-cols-3 gap-6 mb-8">
                            <div className="bg-card rounded-xl p-6">
                                <div className="h-12 w-12 bg-foreground/10 rounded-lg flex items-center justify-center mb-4">
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold mb-2">REST API</h3>
                                <p className="text-sm text-muted-foreground">
                                    Complete RESTful API with authentication, rate limiting, and comprehensive endpoints
                                </p>
                            </div>
                            <div className="bg-card rounded-xl p-6">
                                <div className="h-12 w-12 bg-foreground/10 rounded-lg flex items-center justify-center mb-4">
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold mb-2">Webhooks</h3>
                                <p className="text-sm text-muted-foreground">
                                    Real-time webhooks for campaigns, moves, and analytics events
                                </p>
                            </div>
                            <div className="bg-card rounded-xl p-6">
                                <div className="h-12 w-12 bg-foreground/10 rounded-lg flex items-center justify-center mb-4">
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold mb-2">SDKs & Libraries</h3>
                                <p className="text-sm text-muted-foreground">
                                    Official SDKs for Node.js, Python, Ruby, and more
                                </p>
                            </div>
                        </div>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Button asChild size="lg">
                                <Link href="/docs">View API Docs</Link>
                            </Button>
                            <Button variant="outline" size="lg" asChild>
                                <Link href="/community">Join Developer Community</Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
                        <div>
                            <div className="text-3xl font-bold mb-2">100+</div>
                            <div className="text-sm text-muted-foreground">Available Integrations</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-2">5min</div>
                            <div className="text-sm text-muted-foreground">Average Setup Time</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-2">99.9%</div>
                            <div className="text-sm text-muted-foreground">API Uptime</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-2">24/7</div>
                            <div className="text-sm text-muted-foreground">Developer Support</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="border-t border-border bg-foreground text-background py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center">
                        <h2 className="font-display text-4xl font-medium mb-6">
                            Missing an integration?
                        </h2>
                        <p className="text-lg text-background/70 mb-10">
                            We're adding new integrations every week. Let us know what you need.
                        </p>
                        <Button asChild size="lg" variant="secondary" className="h-14 px-8 text-base rounded-xl">
                            <Link href="/contact">Request Integration</Link>
                        </Button>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
