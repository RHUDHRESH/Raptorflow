'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const docSections = [
  {
    title: 'Getting Started',
    description: 'Everything you need to get up and running with RaptorFlow',
    articles: [
      {
        title: 'Quick Start Guide',
        description: 'Get your first campaign running in 10 minutes',
        time: '5 min read',
      },
      {
        title: 'Understanding Foundation',
        description: 'Learn how to build your marketing foundation',
        time: '8 min read',
      },
      {
        title: 'Setting Up Your First Cohort',
        description: 'Create and manage customer cohorts',
        time: '6 min read',
      },
      {
        title: 'Creating Your First Move',
        description: 'Ship your first marketing move',
        time: '4 min read',
      },
    ],
  },
  {
    title: 'Core Concepts',
    description: 'Deep dive into RaptorFlow concepts and methodology',
    articles: [
      {
        title: 'The Marketing Operating System',
        description: 'Understanding our systematic approach',
        time: '12 min read',
      },
      {
        title: 'Foundation → Strategy → Execution',
        description: 'How our three-step process works',
        time: '10 min read',
      },
      {
        title: 'Moves vs Campaigns',
        description: 'Understanding the difference and relationship',
        time: '7 min read',
      },
      {
        title: 'Cohort-Based Marketing',
        description: 'Targeting the right customers at the right time',
        time: '9 min read',
      },
    ],
  },
  {
    title: 'Features',
    description: 'Detailed guides for each RaptorFlow feature',
    articles: [
      {
        title: 'Foundation Builder',
        description: 'Create your marketing foundation',
        time: '15 min read',
      },
      {
        title: 'Campaign Manager',
        description: 'Build and manage multi-phase campaigns',
        time: '12 min read',
      },
      {
        title: 'Move Library',
        description: 'Browse and create marketing moves',
        time: '8 min read',
      },
      {
        title: 'Muse AI Assistant',
        description: 'AI-powered content creation',
        time: '10 min read',
      },
      {
        title: 'Matrix Analytics',
        description: 'Track and measure performance',
        time: '11 min read',
      },
      {
        title: 'Blackbox Experiments',
        description: 'Test and optimize marketing ideas',
        time: '9 min read',
      },
      {
        title: 'Radar Intelligence',
        description: 'Market intelligence and trend detection',
        time: '7 min read',
      },
    ],
  },
  {
    title: 'Integrations',
    description: 'Connect RaptorFlow with your existing tools',
    articles: [
      {
        title: 'Google Analytics Integration',
        description: 'Connect your analytics account',
        time: '5 min read',
      },
      {
        title: 'Email Service Providers',
        description: 'Integrate with SendGrid, Mailgun, and more',
        time: '6 min read',
      },
      {
        title: 'CRM Connections',
        description: 'Sync with HubSpot, Salesforce, and others',
        time: '8 min read',
      },
      {
        title: 'Social Media Platforms',
        description: 'Connect Twitter, LinkedIn, and Meta',
        time: '7 min read',
      },
      {
        title: 'Custom Webhooks',
        description: 'Build custom integrations',
        time: '10 min read',
      },
    ],
  },
  {
    title: 'API Reference',
    description: 'Technical documentation for developers',
    articles: [
      {
        title: 'Authentication',
        description: 'API keys and authentication methods',
        time: '5 min read',
      },
      {
        title: 'REST API Endpoints',
        description: 'Complete API reference',
        time: '20 min read',
      },
      {
        title: 'Webhooks Guide',
        description: 'Set up and handle webhooks',
        time: '8 min read',
      },
      {
        title: 'Rate Limiting',
        description: 'Understanding API limits',
        time: '3 min read',
      },
      {
        title: 'Error Handling',
        description: 'Common errors and solutions',
        time: '6 min read',
      },
    ],
  },
  {
    title: 'Best Practices',
    description: 'Pro tips and strategies for success',
    articles: [
      {
        title: 'Campaign Planning Best Practices',
        description: 'Structure your campaigns for success',
        time: '10 min read',
      },
      {
        title: 'Content Creation Workflow',
        description: 'Efficient content creation process',
        time: '8 min read',
      },
      {
        title: 'Analytics and Reporting',
        description: 'Measure what matters',
        time: '7 min read',
      },
      {
        title: 'Team Collaboration',
        description: 'Work effectively with your team',
        time: '6 min read',
      },
    ],
  },
];

export default function DocsPage() {
  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              Documentation
            </p>
            <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
              Everything you need to succeed.
            </h1>
            <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
              Comprehensive guides, API documentation, and best practices to
              help you get the most out of RaptorFlow.
            </p>
          </div>
        </div>
      </section>

      {/* Search Bar */}
      <section className="pb-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl">
            <div className="relative">
              <input
                type="search"
                placeholder="Search documentation..."
                className="w-full h-12 px-4 pr-12 rounded-xl border border-border bg-background text-lg"
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <svg
                  className="h-5 w-5 text-muted-foreground"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Links */}
      <section className="pb-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button variant="outline" asChild className="h-12 justify-start">
              <Link href="/docs/quick-start">Quick Start →</Link>
            </Button>
            <Button variant="outline" asChild className="h-12 justify-start">
              <Link href="/docs/api">API Reference →</Link>
            </Button>
            <Button variant="outline" asChild className="h-12 justify-start">
              <Link href="/docs/integrations">Integrations →</Link>
            </Button>
            <Button variant="outline" asChild className="h-12 justify-start">
              <Link href="/docs/best-practices">Best Practices →</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="pb-24 lg:pb-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="space-y-16">
            {docSections.map((section) => (
              <div key={section.title}>
                <h2 className="font-display text-3xl font-medium mb-4">
                  {section.title}
                </h2>
                <p className="text-lg text-muted-foreground mb-8">
                  {section.description}
                </p>
                <div className="grid lg:grid-cols-2 gap-6">
                  {section.articles.map((article) => (
                    <div key={article.title} className="group">
                      <div className="rounded-xl border border-border bg-card p-6 hover:border-foreground/20 transition-colors">
                        <h3 className="font-semibold mb-2 group-hover:text-foreground transition-colors">
                          {article.title}
                        </h3>
                        <p className="text-sm text-muted-foreground mb-3">
                          {article.description}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-muted-foreground">
                            {article.time}
                          </span>
                          <Button variant="ghost" size="sm" asChild>
                            <Link
                              href={`/docs/${article.title.toLowerCase().replace(/\s+/g, '-')}`}
                            >
                              Read →
                            </Link>
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Community Resources */}
      <section className="border-y border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="font-display text-3xl font-medium mb-6">
              Need more help?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Join our community of founders and get help from the RaptorFlow
              team.
            </p>
            <div className="grid sm:grid-cols-2 gap-4">
              <Button asChild>
                <Link href="/community">Join Community</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/help">Contact Support</Link>
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
              Ready to build?
            </h2>
            <p className="text-lg text-background/70 mb-10">
              Start with our quick start guide and have your first campaign
              running today.
            </p>
            <Button
              asChild
              size="lg"
              variant="secondary"
              className="h-14 px-8 text-base rounded-xl"
            >
              <Link href="/foundation">Get Started Free</Link>
            </Button>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
