'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const communityStats = [
  { label: 'Active Members', value: '1,200+' },
  { label: 'Daily Discussions', value: '50+' },
  { label: 'Campaigns Shared', value: '500+' },
  { label: 'Success Stories', value: '100+' },
];

const discussionTopics = [
  {
    title: 'Campaign Strategies',
    description: 'Share and discuss campaign approaches',
    posts: 234,
    activity: 'Active',
  },
  {
    title: 'Content Creation',
    description: 'Tips and tricks for creating effective content',
    posts: 189,
    activity: 'Very Active',
  },
  {
    title: 'Analytics & Results',
    description: 'Discuss performance metrics and optimization',
    posts: 156,
    activity: 'Active',
  },
  {
    title: 'Feature Requests',
    description: 'Suggest and vote on new features',
    posts: 98,
    activity: 'Moderate',
  },
  {
    title: 'Success Stories',
    description: 'Share your wins and learn from others',
    posts: 67,
    activity: 'Growing',
  },
  {
    title: 'General Discussion',
    description: 'Everything else related to marketing and growth',
    posts: 412,
    activity: 'Very Active',
  },
];

export default function CommunityPage() {
  return (
    <MarketingLayout>
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              Community
            </p>
            <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
              Learn from fellow founders.
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Join thousands of founders sharing strategies, wins, and lessons
              learned in their marketing journey.
            </p>
          </div>
        </div>
      </section>

      <section className="pb-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {communityStats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold mb-2">{stat.value}</div>
                <div className="text-sm text-muted-foreground">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="pb-24 lg:pb-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <h2 className="font-display text-3xl font-medium mb-12">
            Popular Discussions
          </h2>
          <div className="grid lg:grid-cols-2 gap-6">
            {discussionTopics.map((topic) => (
              <div
                key={topic.title}
                className="rounded-xl border border-border bg-card p-6"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold">{topic.title}</h3>
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-muted text-muted-foreground">
                    {topic.activity}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  {topic.description}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {topic.posts} posts
                  </span>
                  <Button variant="ghost" size="sm">
                    Join Discussion →
                  </Button>
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
              Community Guidelines
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Be respectful, helpful, and focused on helping fellow founders
              succeed.
            </p>
            <Button variant="outline" asChild>
              <Link href="/community/guidelines">View Guidelines</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="border-t border-border bg-foreground text-background py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="font-display text-4xl font-medium mb-6">
              Ready to join?
            </h2>
            <p className="text-lg text-background/70 mb-10">
              Start contributing to the community and learn from experienced
              founders.
            </p>
            <Button
              asChild
              size="lg"
              variant="secondary"
              className="h-14 px-8 text-base rounded-xl"
            >
              <Link href="/foundation">Sign Up Free</Link>
            </Button>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
