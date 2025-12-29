'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const changelogEntries = [
  {
    version: '2.4.0',
    date: '2024-12-20',
    type: 'feature',
    title: 'Blackbox Experimental Lab',
    description:
      'New experimental sandbox for growth marketing with A/B testing capabilities and gamification elements.',
    changes: [
      'Added Experiments Lab feed for testing ideas',
      'Wild Moves quick test functionality',
      'Break Conventions bold ideas module',
      'Idea rating system (novelty, risk, reach, ICP alignment)',
      'Gamification elements with badges and streaks',
      'A/B testing framework with statistical significance',
      'Idea comparison and simulation tools',
    ],
    author: 'Product Team',
    tags: ['New Feature', 'AI', 'Testing', 'Gamification'],
    breaking: false,
  },
  {
    version: '2.3.0',
    date: '2024-12-15',
    type: 'feature',
    title: 'Enhanced Move Selection',
    description:
      'Improved move library with templates, custom move creation, and better user experience.',
    changes: [
      'Added MOVE_LIBRARY with 3 templates',
      'MoveTemplateCard component for better UX',
      'CustomMoveCard for personalized moves',
      'Direct campaign creation from move selection',
      'Improved navigation flow',
      'Move performance tracking',
      'Template sharing capabilities',
    ],
    author: 'Engineering Team',
    tags: ['Enhancement', 'UX', 'Templates'],
    breaking: false,
  },
  {
    version: '2.2.1',
    date: '2024-12-10',
    type: 'fix',
    title: 'Performance Improvements',
    description:
      'Fixed loading issues and improved overall performance across the platform.',
    changes: [
      'Optimized component rendering',
      'Fixed memory leaks in Matrix view',
      'Improved loading states',
      'Reduced bundle size by 15%',
      'Faster API response times',
      'Better error handling',
    ],
    author: 'Engineering Team',
    tags: ['Performance', 'Bug Fix', 'Optimization'],
    breaking: false,
  },
  {
    version: '2.2.0',
    date: '2024-12-05',
    type: 'feature',
    title: 'Radar Intelligence System',
    description:
      'Advanced market intelligence and competitive analysis system.',
    changes: [
      'Real-time competitor monitoring',
      'Market trend detection',
      'Positioning gap analysis',
      'Automated reporting',
      'Integration with Blackbox',
    ],
    author: 'Product Team',
    tags: ['New Feature', 'Analytics', 'Intelligence'],
    breaking: false,
  },
  {
    version: '2.1.0',
    date: '2024-11-28',
    type: 'feature',
    title: 'Muse AI Assistant',
    description: 'AI-powered content creation and campaign assistance.',
    changes: [
      'Natural language content generation',
      'Campaign strategy suggestions',
      'Visual asset creation',
      'Multi-language support',
      'Brand voice consistency',
    ],
    author: 'AI Team',
    tags: ['AI', 'Content', 'New Feature'],
    breaking: false,
  },
  {
    version: '2.0.0',
    date: '2024-11-15',
    type: 'major',
    title: 'Platform Redesign',
    description:
      'Complete redesign of the RaptorFlow platform with new architecture and improved user experience.',
    changes: [
      'New marketing operating system architecture',
      'Redesigned user interface',
      'Improved performance and scalability',
      'Enhanced security features',
      'Mobile-responsive design',
      'New API endpoints',
      'Migration tools for existing users',
    ],
    author: 'Product Team',
    tags: ['Major Release', 'Redesign', 'Architecture'],
    breaking: true,
  },
];

const getTypeColor = (type: string) => {
  switch (type) {
    case 'major':
      return 'bg-purple-100 text-purple-800';
    case 'feature':
      return 'bg-blue-100 text-blue-800';
    case 'fix':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export default function ChangelogPage() {
  const [selectedType, setSelectedType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const types = ['all', 'major', 'feature', 'fix'];

  const filteredEntries = changelogEntries.filter((entry) => {
    const matchesType = selectedType === 'all' || entry.type === selectedType;
    const matchesSearch =
      entry.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.changes.some((change) =>
        change.toLowerCase().includes(searchTerm.toLowerCase())
      );
    return matchesType && matchesSearch;
  });

  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              Changelog
            </p>
            <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
              What's new at RaptorFlow.
            </h1>
            <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed mb-8">
              Follow our journey as we build the marketing operating system for
              founders. Every feature, fix, and improvement documented.
            </p>

            {/* Search and Filter */}
            <div className="max-w-2xl mx-auto space-y-4">
              <div className="relative">
                <input
                  type="search"
                  placeholder="Search changelog..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
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

              {/* Type Filter */}
              <div className="flex flex-wrap gap-2 justify-center">
                {types.map((type) => (
                  <button
                    key={type}
                    onClick={() => setSelectedType(type)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors capitalize ${
                      selectedType === type
                        ? 'bg-foreground text-background'
                        : 'bg-muted text-muted-foreground hover:bg-foreground/10'
                    }`}
                  >
                    {type === 'all' ? 'All Updates' : type}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Changelog Entries */}
      <section className="pb-24 lg:pb-32">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <div className="space-y-12">
            {filteredEntries.map((entry) => (
              <div
                key={entry.version}
                className="border-b border-border pb-12 last:border-b-0"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="font-display text-2xl font-semibold">
                        {entry.version}
                      </h2>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${getTypeColor(entry.type)}`}
                      >
                        {entry.type}
                      </span>
                      {entry.breaking && (
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Breaking
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                      <time>{entry.date}</time>
                      <span>•</span>
                      <span>{entry.author}</span>
                      <span>•</span>
                      <span>{entry.changes.length} changes</span>
                    </div>
                  </div>
                </div>

                <h3 className="text-xl font-medium mb-3">{entry.title}</h3>
                <p className="text-muted-foreground mb-6 leading-relaxed">
                  {entry.description}
                </p>

                {/* Tags */}
                {entry.tags && (
                  <div className="flex flex-wrap gap-2 mb-6">
                    {entry.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs bg-muted px-2 py-1 rounded-md"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Changes List */}
                <div className="bg-muted/30 rounded-lg p-6">
                  <h4 className="font-medium mb-4">Changes</h4>
                  <ul className="space-y-2">
                    {entry.changes.map((change, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <svg
                          className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <span className="text-sm">{change}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>

          {filteredEntries.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">
                No changelog entries found matching your criteria.
              </p>
            </div>
          )}
        </div>
      </section>
      {/* Roadmap Preview */}
      <section className="border-y border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="font-display text-3xl font-medium mb-6">
              See what's coming next
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              We're building fast. Check our roadmap for upcoming features and
              improvements.
            </p>
            <Button asChild size="lg">
              <Link href="/roadmap">View Roadmap</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold mb-2">50+</div>
              <div className="text-sm text-muted-foreground">
                Releases This Year
              </div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">200+</div>
              <div className="text-sm text-muted-foreground">
                Features Shipped
              </div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">500+</div>
              <div className="text-sm text-muted-foreground">Bug Fixes</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">Weekly</div>
              <div className="text-sm text-muted-foreground">
                Update Cadence
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* RSS Feed Section */}
      <section className="border-t border-border bg-foreground text-background py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-display text-3xl font-medium mb-6">
              Stay updated
            </h2>
            <p className="text-lg text-background/70 mb-8">
              Subscribe to our changelog RSS feed or newsletter to never miss an
              update.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                variant="secondary"
                size="lg"
                className="h-14 px-8 text-base rounded-xl"
              >
                Subscribe to RSS Feed
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="h-14 px-8 text-base rounded-xl border-background/20 text-background hover:bg-background/10"
              >
                Join Newsletter
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
              Shape our future
            </h2>
            <p className="text-lg text-background/70 mb-10">
              Have feedback or feature requests? We'd love to hear from you.
            </p>
            <Button
              asChild
              size="lg"
              variant="secondary"
              className="h-14 px-8 text-base rounded-xl"
            >
              <Link href="/contact">Share Feedback</Link>
            </Button>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
