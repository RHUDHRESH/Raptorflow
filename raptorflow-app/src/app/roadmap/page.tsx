'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const roadmapItems = [
  {
    quarter: 'Q1 2025',
    status: 'current',
    theme: 'Foundation & Analytics',
    items: [
      {
        title: 'Advanced Analytics Dashboard',
        description:
          'Comprehensive analytics with cohort analysis, funnel tracking, and predictive insights powered by machine learning.',
        status: 'in-progress',
        progress: 70,
        priority: 'high',
        features: [
          'Cohort analysis',
          'Funnel tracking',
          'Predictive insights',
          'Custom dashboards',
          'Real-time data',
        ],
        targetDate: '2025-01-15',
        team: 'Analytics Team',
        votes: 245,
      },
      {
        title: 'Mobile App',
        description:
          'Native iOS and Android apps for on-the-go campaign management with full offline support.',
        status: 'in-progress',
        progress: 45,
        priority: 'high',
        features: [
          'Native iOS/Android',
          'Offline support',
          'Push notifications',
          'Biometric auth',
          'Real-time sync',
        ],
        targetDate: '2025-02-28',
        team: 'Mobile Team',
        votes: 189,
      },
      {
        title: 'Team Collaboration',
        description:
          'Real-time collaboration features with comments, approvals, and role-based access control.',
        status: 'planned',
        progress: 20,
        priority: 'medium',
        features: [
          'Real-time comments',
          'Approval workflows',
          'Role-based access',
          'Activity feeds',
          'Team mentions',
        ],
        targetDate: '2025-03-15',
        team: 'Platform Team',
        votes: 156,
      },
    ],
  },
  {
    quarter: 'Q2 2025',
    status: 'upcoming',
    theme: 'AI & Automation',
    items: [
      {
        title: 'AI-Powered Content Generation',
        description:
          'Advanced AI models for blog posts, social media, and email campaigns with brand voice consistency.',
        status: 'planned',
        progress: 0,
        priority: 'high',
        features: [
          'Multi-format content',
          'Brand voice learning',
          'A/B testing suggestions',
          'SEO optimization',
          'Multi-language',
        ],
        targetDate: '2025-04-30',
        team: 'AI Team',
        votes: 312,
      },
      {
        title: 'Advanced Segmentation',
        description:
          'Dynamic audience segmentation based on behavior, demographics, and predictive modeling.',
        status: 'planned',
        progress: 0,
        priority: 'high',
        features: [
          'Behavioral segmentation',
          'Predictive modeling',
          'Lookalike audiences',
          'Dynamic segments',
          'Cross-platform sync',
        ],
        targetDate: '2025-05-15',
        team: 'Analytics Team',
        votes: 278,
      },
      {
        title: 'Marketing Automation',
        description:
          'Visual workflow builder for complex marketing automation with trigger-based campaigns.',
        status: 'planned',
        progress: 0,
        priority: 'medium',
        features: [
          'Visual workflow builder',
          'Trigger-based campaigns',
          'Multi-channel automation',
          'Lead scoring',
          'Drip campaigns',
        ],
        targetDate: '2025-06-30',
        team: 'Platform Team',
        votes: 234,
      },
    ],
  },
  {
    quarter: 'Q3 2025',
    status: 'future',
    theme: 'Enterprise & Scale',
    items: [
      {
        title: 'Enterprise SSO & Security',
        description:
          'Advanced security features including SSO, SAML, and compliance certifications.',
        status: 'planned',
        progress: 0,
        priority: 'high',
        features: [
          'SSO/SAML integration',
          'Role-based permissions',
          'Audit logs',
          'SOC2 compliance',
          'Data encryption',
        ],
        targetDate: '2025-07-31',
        team: 'Security Team',
        votes: 198,
      },
      {
        title: 'Advanced Reporting',
        description:
          'Custom report builder with scheduled exports and advanced visualization options.',
        status: 'planned',
        progress: 0,
        priority: 'medium',
        features: [
          'Custom report builder',
          'Scheduled exports',
          'Advanced visualizations',
          'White-label reports',
          'API access',
        ],
        targetDate: '2025-08-15',
        team: 'Analytics Team',
        votes: 167,
      },
    ],
  },
  {
    quarter: 'Q4 2025',
    status: 'future',
    theme: 'Innovation & Future',
    items: [
      {
        title: 'Predictive Campaign Optimization',
        description:
          'AI-powered campaign optimization with automatic budget allocation and performance prediction.',
        status: 'planned',
        progress: 0,
        priority: 'medium',
        features: [
          'Budget optimization',
          'Performance prediction',
          'Auto-optimization',
          'Multi-variate testing',
          'ROI forecasting',
        ],
        targetDate: '2025-10-31',
        team: 'AI Team',
        votes: 289,
      },
      {
        title: 'Marketplace & Integrations',
        description:
          'Third-party app marketplace with hundreds of pre-built integrations and custom app development.',
        status: 'planned',
        progress: 0,
        priority: 'low',
        features: [
          'App marketplace',
          'Custom app SDK',
          'API extensions',
          'Webhook automation',
          'Integration templates',
        ],
        targetDate: '2025-12-15',
        team: 'Platform Team',
        votes: 145,
      },
    ],
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'in-progress':
      return 'bg-blue-100 text-blue-800';
    case 'planned':
      return 'bg-yellow-100 text-yellow-800';
    case 'completed':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export default function RoadmapPage() {
  const [selectedQuarter, setSelectedQuarter] = useState('all');
  const [selectedPriority, setSelectedPriority] = useState('all');

  const quarters = ['all', ...roadmapItems.map((q) => q.quarter)];
  const priorities = ['all', 'high', 'medium', 'low'];

  const filteredItems = roadmapItems.filter((quarter) => {
    const matchesQuarter =
      selectedQuarter === 'all' || quarter.quarter === selectedQuarter;
    const hasPriorityItems =
      selectedPriority === 'all' ||
      quarter.items.some((item) => item.priority === selectedPriority);
    return matchesQuarter && hasPriorityItems;
  });

  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              Roadmap
            </p>
            <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
              Building the future of marketing.
            </h1>
            <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed mb-8">
              See what we're building next. Our roadmap is transparent,
              community-driven, and focused on delivering value to founders and
              marketers.
            </p>

            {/* Filters */}
            <div className="max-w-2xl mx-auto space-y-4">
              {/* Quarter Filter */}
              <div className="flex flex-wrap gap-2 justify-center">
                {quarters.map((quarter) => (
                  <button
                    key={quarter}
                    onClick={() => setSelectedQuarter(quarter)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                      selectedQuarter === quarter
                        ? 'bg-foreground text-background'
                        : 'bg-muted text-muted-foreground hover:bg-foreground/10'
                    }`}
                  >
                    {quarter === 'all' ? 'All Quarters' : quarter}
                  </button>
                ))}
              </div>

              {/* Priority Filter */}
              <div className="flex flex-wrap gap-2 justify-center">
                {priorities.map((priority) => (
                  <button
                    key={priority}
                    onClick={() => setSelectedPriority(priority)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors capitalize ${
                      selectedPriority === priority
                        ? 'bg-foreground text-background'
                        : 'bg-muted text-muted-foreground hover:bg-foreground/10'
                    }`}
                  >
                    {priority === 'all'
                      ? 'All Priorities'
                      : `${priority} priority`}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
      {/* Roadmap Timeline */}
      <section className="pb-24 lg:pb-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="space-y-16">
            {filteredItems.map((quarter) => (
              <div key={quarter.quarter} className="relative">
                {/* Quarter Header */}
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h2 className="font-display text-3xl font-semibold mb-2">
                      {quarter.quarter}
                    </h2>
                    <p className="text-lg text-muted-foreground">
                      {quarter.theme}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        quarter.status === 'current'
                          ? 'bg-blue-100 text-blue-800'
                          : quarter.status === 'upcoming'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {quarter.status}
                    </span>
                  </div>
                </div>

                {/* Items Grid */}
                <div className="grid lg:grid-cols-3 gap-6">
                  {quarter.items
                    .filter(
                      (item) =>
                        selectedPriority === 'all' ||
                        item.priority === selectedPriority
                    )
                    .map((item) => (
                      <div
                        key={item.title}
                        className="rounded-xl border border-border bg-card p-6 hover:border-foreground/20 transition-all duration-200 hover:shadow-lg"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <h3 className="font-semibold text-lg">
                            {item.title}
                          </h3>
                          <div className="flex items-center gap-2">
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(item.status)}`}
                            >
                              {item.status}
                            </span>
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getPriorityColor(item.priority)}`}
                            >
                              {item.priority}
                            </span>
                          </div>
                        </div>

                        <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
                          {item.description}
                        </p>

                        {/* Progress Bar */}
                        <div className="mb-4">
                          <div className="flex items-center justify-between text-sm mb-2">
                            <span className="text-muted-foreground">
                              Progress
                            </span>
                            <span className="font-medium">
                              {item.progress}%
                            </span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="bg-foreground h-2 rounded-full transition-all duration-300"
                              style={{ width: `${item.progress}%` }}
                            />
                          </div>
                        </div>

                        {/* Features */}
                        <div className="mb-4">
                          <div className="flex flex-wrap gap-1">
                            {item.features.slice(0, 3).map((feature) => (
                              <span
                                key={feature}
                                className="text-xs bg-muted px-2 py-1 rounded-md"
                              >
                                {feature}
                              </span>
                            ))}
                            {item.features.length > 3 && (
                              <span className="text-xs bg-muted px-2 py-1 rounded-md">
                                +{item.features.length - 3} more
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Meta Info */}
                        <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                          <div className="flex items-center gap-1">
                            <svg
                              className="h-3 w-3"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                              />
                            </svg>
                            <span>{item.targetDate}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <svg
                              className="h-3 w-3"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                              />
                            </svg>
                            <span>{item.team}</span>
                          </div>
                        </div>

                        {/* Voting */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <svg
                              className="h-4 w-4 text-muted-foreground"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
                              />
                            </svg>
                            <span className="text-sm text-muted-foreground">
                              {item.votes} votes
                            </span>
                          </div>
                          <Button variant="outline" size="sm">
                            Vote
                          </Button>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>

          {filteredItems.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">
                No roadmap items found matching your criteria.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Feature Requests */}
      <section className="border-y border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="font-display text-3xl font-medium mb-6">
              Have a feature idea?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              We build based on customer feedback. Help us prioritize what
              matters most.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button asChild>
                <Link href="/contact">Request a Feature</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/community">Join the Discussion</Link>
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
              Build with us
            </h2>
            <p className="text-lg text-background/70 mb-10">
              Join thousands of founders building marketing that compounds.
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
