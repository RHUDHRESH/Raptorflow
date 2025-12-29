'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const pressReleases = [
  {
    id: 'blackbox-launch',
    date: '2024-12-15',
    title:
      'RaptorFlow Launches Blackbox: Experimental Sandbox for Growth Marketing',
    summary:
      'New feature enables founders to test marketing ideas with A/B testing capabilities and gamification elements.',
    category: 'Product Launch',
    downloadUrl: '#',
    featured: true,
    quote:
      'Blackbox represents our commitment to helping founders experiment boldly and systematically with their marketing.',
    author: 'Sarah Chen, CEO',
    tags: ['Product', 'Innovation', 'Growth Marketing'],
    readTime: '3 min',
    views: 12500,
    downloads: 850,
  },
  {
    id: 'seed-funding',
    date: '2024-11-20',
    title:
      'RaptorFlow Raises $2.5M Seed Round to Build Marketing OS for Founders',
    summary:
      'Funding will accelerate product development and expand customer success team to serve growing founder community.',
    category: 'Funding',
    downloadUrl: '#',
    featured: false,
    quote:
      'This investment validates our vision of systematic marketing for the next generation of founders.',
    author: 'Sarah Chen, CEO',
    tags: ['Funding', 'Investment', 'Growth'],
    readTime: '4 min',
    views: 8900,
    downloads: 620,
  },
  {
    id: 'milestone-users',
    date: '2024-11-01',
    title: 'RaptorFlow Reaches 1,000+ Founders Using Platform Monthly',
    summary:
      'Marketing operating system gains traction among early-stage startups and solo founders seeking systematic approach to growth.',
    category: 'Milestone',
    downloadUrl: '#',
    featured: false,
    quote:
      'Reaching 1,000 monthly active founders proves that systematic marketing resonates with the community.',
    author: 'Mike Johnson, Head of Growth',
    tags: ['Milestone', 'Growth', 'Community'],
    readTime: '2 min',
    views: 6700,
    downloads: 410,
  },
  {
    id: 'ai-integration',
    date: '2024-10-15',
    title: 'RaptorFlow Introduces AI-Powered Campaign Generation',
    summary:
      'New AI capabilities help founders generate campaign ideas and optimize marketing spend automatically.',
    category: 'Product Update',
    downloadUrl: '#',
    featured: false,
    quote:
      'AI is not replacing creativity—it amplifies it by handling the heavy lifting of campaign optimization.',
    author: 'Dr. Alex Rivera, CTO',
    tags: ['AI', 'Product', 'Innovation'],
    readTime: '3 min',
    views: 9200,
    downloads: 580,
  },
  {
    id: 'partnership-program',
    date: '2024-09-30',
    title: 'RaptorFlow Launches Agency Partner Program',
    summary:
      "New program enables marketing agencies to serve clients more efficiently using RaptorFlow's systematic approach.",
    category: 'Partnership',
    downloadUrl: '#',
    featured: false,
    quote:
      'Agencies are force multipliers for our mission to bring systematic marketing to every founder.',
    author: 'Lisa Park, Head of Partnerships',
    tags: ['Partnership', 'Agencies', 'Growth'],
    readTime: '3 min',
    views: 5400,
    downloads: 320,
  },
];

const mediaCoverage = [
  {
    id: 'techcrunch-feature',
    publication: 'TechCrunch',
    title:
      'This startup wants to end "marketing by vibes" with a systematic approach',
    date: '2024-12-10',
    url: '#',
    excerpt:
      'RaptorFlow is building what it calls a "marketing operating system" to help founders move from chaotic marketing to systematic execution.',
    author: 'Jordan Smith',
    category: 'Technology',
    featured: true,
    imageUrl: '/images/techcrunch-logo.png',
    readTime: '5 min',
    shares: 1200,
  },
  {
    id: 'product-hunt-featured',
    publication: 'Product Hunt',
    title: 'RaptorFlow - The marketing OS for founders who refuse to guess',
    date: '2024-11-15',
    url: '#',
    excerpt:
      'Featured as Product of the Day, RaptorFlow helps founders build marketing that actually compounds instead of resetting every Monday.',
    author: 'Product Hunt Team',
    category: 'Product Launch',
    featured: false,
    imageUrl: '/images/product-hunt-logo.png',
    readTime: '3 min',
    shares: 890,
  },
  {
    id: 'indie-hackers-deep-dive',
    publication: 'Indie Hackers',
    title:
      'From marketing chaos to clarity: How RaptorFlow systematizes growth',
    date: '2024-11-20',
    url: '#',
    excerpt:
      'Deep dive into how RaptorFlow helps solo founders and small teams compete with systematic marketing approaches.',
    author: 'Courtney Lee',
    category: 'Startup',
    featured: false,
    imageUrl: '/images/indie-hackers-logo.png',
    readTime: '7 min',
    shares: 650,
  },
  {
    id: 'venturebeat-analysis',
    publication: 'VentureBeat',
    title: 'Why systematic marketing is the next frontier for SaaS',
    date: '2024-10-25',
    url: '#',
    excerpt:
      'Analysis of how platforms like RaptorFlow are changing the landscape of marketing technology for early-stage companies.',
    author: 'Maria Garcia',
    category: 'Business',
    featured: false,
    imageUrl: '/images/venturebeat-logo.png',
    readTime: '6 min',
    shares: 480,
  },
];

const categories = [
  'All',
  'Product Launch',
  'Funding',
  'Milestone',
  'Product Update',
  'Partnership',
];
const mediaCategories = [
  'All',
  'Technology',
  'Product Launch',
  'Startup',
  'Business',
];

const mediaAssets = [
  {
    id: 'logo-kit',
    name: 'Logo Kit',
    description: 'RaptorFlow logo in various formats and colors',
    downloadUrl: '#',
    type: 'Branding',
    size: '2.4 MB',
    formats: ['SVG', 'PNG', 'PDF'],
  },
  {
    id: 'brand-guidelines',
    name: 'Brand Guidelines',
    description: 'Complete brand book with usage guidelines',
    downloadUrl: '#',
    type: 'Guidelines',
    size: '8.1 MB',
    formats: ['PDF'],
  },
  {
    id: 'headshots',
    name: 'Team Headshots',
    description: 'High-resolution photos of leadership team',
    downloadUrl: '#',
    type: 'Images',
    size: '15.7 MB',
    formats: ['JPG', 'PNG'],
  },
  {
    id: 'product-screenshots',
    name: 'Product Screenshots',
    description: 'High-quality screenshots of the platform',
    downloadUrl: '#',
    type: 'Product',
    size: '4.2 MB',
    formats: ['PNG', 'SVG'],
  },
];

export default function PressPage() {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedMediaCategory, setSelectedMediaCategory] = useState('All');
  const [activeTab, setActiveTab] = useState('releases');

  const filteredReleases = pressReleases.filter(
    (release) =>
      selectedCategory === 'All' || release.category === selectedCategory
  );

  const filteredMedia = mediaCoverage.filter(
    (coverage) =>
      selectedMediaCategory === 'All' ||
      coverage.category === selectedMediaCategory
  );

  const featuredRelease = pressReleases.find((release) => release.featured);
  const featuredMedia = mediaCoverage.find((coverage) => coverage.featured);

  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="py-24 lg:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
              Press & Media
            </p>
            <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
              Building the future of marketing.
            </h1>
            <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed mb-8">
              Get the latest news, updates, and media resources about
              RaptorFlow's mission to help founders build marketing that
              actually compounds.
            </p>

            <div className="flex flex-col sm:flex-row items-center gap-4 justify-center">
              <Button size="lg" className="h-14 px-8 text-base rounded-xl">
                Download Press Kit
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="h-14 px-8 text-base rounded-xl"
              >
                Contact PR Team
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold mb-2">50+</div>
              <div className="text-sm text-muted-foreground">
                Press Mentions
              </div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">1M+</div>
              <div className="text-sm text-muted-foreground">Media Reach</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">25+</div>
              <div className="text-sm text-muted-foreground">Publications</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">5</div>
              <div className="text-sm text-muted-foreground">
                Product Awards
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tabs */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="flex justify-center mb-12">
            <div className="inline-flex rounded-lg border border-border bg-muted/30 p-1">
              <button
                onClick={() => setActiveTab('releases')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'releases'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Press Releases
              </button>
              <button
                onClick={() => setActiveTab('media')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'media'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Media Coverage
              </button>
              <button
                onClick={() => setActiveTab('assets')}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'assets'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Media Assets
              </button>
            </div>
          </div>

          {/* Press Releases Tab */}
          {activeTab === 'releases' && (
            <div className="space-y-8">
              {/* Featured Release */}
              {featuredRelease && (
                <div className="rounded-2xl border border-border bg-card p-8 lg:p-12 hover:shadow-lg transition-shadow duration-200">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-foreground text-background">
                      Featured
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-muted">
                      {featuredRelease.category}
                    </span>
                  </div>
                  <h2 className="font-display text-3xl lg:text-4xl font-medium mb-4">
                    {featuredRelease.title}
                  </h2>
                  <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
                    {featuredRelease.summary}
                  </p>

                  <blockquote className="border-l-4 border-foreground pl-6 my-6 italic text-muted-foreground">
                    "{featuredRelease.quote}"
                    <footer className="mt-2 text-sm not-italic text-foreground">
                      {featuredRelease.author}
                    </footer>
                  </blockquote>

                  <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-6">
                    <span>{featuredRelease.date}</span>
                    <span>•</span>
                    <span>{featuredRelease.readTime} read</span>
                    <span>•</span>
                    <span>{featuredRelease.views.toLocaleString()} views</span>
                    <span>•</span>
                    <span>{featuredRelease.downloads} downloads</span>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-6">
                    {featuredRelease.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs bg-muted px-2 py-1 rounded-md"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4">
                    <Button asChild>
                      <Link href={featuredRelease.downloadUrl}>
                        Download Press Release
                      </Link>
                    </Button>
                    <Button variant="outline">Share</Button>
                  </div>
                </div>
              )}

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

              {/* Releases List */}
              <div className="space-y-6">
                {filteredReleases
                  .filter((release) => !release.featured)
                  .map((release) => (
                    <div
                      key={release.id}
                      className="rounded-xl border border-border bg-card p-6 hover:border-foreground/20 transition-all duration-200"
                    >
                      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-3">
                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-muted">
                              {release.category}
                            </span>
                            <span className="text-sm text-muted-foreground">
                              {release.date}
                            </span>
                          </div>
                          <h3 className="font-display text-xl font-semibold mb-3">
                            {release.title}
                          </h3>
                          <p className="text-muted-foreground mb-4">
                            {release.summary}
                          </p>

                          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                            <span>{release.readTime} read</span>
                            <span>•</span>
                            <span>{release.views.toLocaleString()} views</span>
                            <span>•</span>
                            <span>{release.downloads} downloads</span>
                          </div>
                        </div>
                        <div className="flex flex-col gap-3">
                          <Button asChild variant="outline">
                            <Link href={release.downloadUrl}>Download</Link>
                          </Button>
                          <Button variant="ghost" size="sm">
                            Share
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Media Coverage Tab */}
          {activeTab === 'media' && (
            <div className="space-y-8">
              {/* Featured Coverage */}
              {featuredMedia && (
                <div className="rounded-2xl border border-border bg-card p-8 lg:p-12 hover:shadow-lg transition-shadow duration-200">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-foreground text-background">
                      Featured
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-muted">
                      {featuredMedia.category}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-16 h-16 rounded-lg bg-muted flex items-center justify-center">
                      <span className="text-lg font-bold">
                        {featuredMedia.publication.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <div className="font-semibold text-lg">
                        {featuredMedia.publication}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {featuredMedia.date}
                      </div>
                    </div>
                  </div>
                  <h2 className="font-display text-3xl lg:text-4xl font-medium mb-4">
                    {featuredMedia.title}
                  </h2>
                  <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
                    {featuredMedia.excerpt}
                  </p>

                  <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-6">
                    <span>By {featuredMedia.author}</span>
                    <span>•</span>
                    <span>{featuredMedia.readTime} read</span>
                    <span>•</span>
                    <span>{featuredMedia.shares.toLocaleString()} shares</span>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4">
                    <Button asChild>
                      <Link href={featuredMedia.url}>Read Full Article</Link>
                    </Button>
                    <Button variant="outline">Share</Button>
                  </div>
                </div>
              )}

              {/* Category Filter */}
              <div className="flex flex-wrap gap-2 justify-center">
                {mediaCategories.map((category) => (
                  <button
                    key={category}
                    onClick={() => setSelectedMediaCategory(category)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                      selectedMediaCategory === category
                        ? 'bg-foreground text-background'
                        : 'bg-muted text-muted-foreground hover:bg-foreground/10'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>

              {/* Media List */}
              <div className="space-y-6">
                {filteredMedia
                  .filter((coverage) => !coverage.featured)
                  .map((coverage) => (
                    <div
                      key={coverage.id}
                      className="rounded-xl border border-border bg-card p-6 hover:border-foreground/20 transition-all duration-200"
                    >
                      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-3">
                            <div className="w-12 h-12 rounded-lg bg-muted flex items-center justify-center">
                              <span className="text-sm font-bold">
                                {coverage.publication.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <div className="font-semibold">
                                {coverage.publication}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {coverage.date}
                              </div>
                            </div>
                          </div>
                          <h3 className="font-display text-xl font-semibold mb-3">
                            {coverage.title}
                          </h3>
                          <p className="text-muted-foreground mb-4">
                            {coverage.excerpt}
                          </p>

                          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                            <span>By {coverage.author}</span>
                            <span>•</span>
                            <span>{coverage.readTime} read</span>
                            <span>•</span>
                            <span>
                              {coverage.shares.toLocaleString()} shares
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-col gap-3">
                          <Button asChild>
                            <Link href={coverage.url}>Read Article</Link>
                          </Button>
                          <Button variant="ghost" size="sm">
                            Share
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Media Assets Tab */}
          {activeTab === 'assets' && (
            <div className="space-y-8">
              <div className="text-center mb-12">
                <h2 className="font-display text-3xl lg:text-4xl font-medium mb-4">
                  Media Assets
                </h2>
                <p className="text-lg text-muted-foreground">
                  Download logos, brand guidelines, and other media resources.
                </p>
              </div>

              <div className="grid lg:grid-cols-2 gap-6">
                {mediaAssets.map((asset) => (
                  <div
                    key={asset.id}
                    className="rounded-xl border border-border bg-card p-6 hover:border-foreground/20 transition-all duration-200"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-display text-xl font-semibold mb-2">
                          {asset.name}
                        </h3>
                        <p className="text-muted-foreground text-sm mb-3">
                          {asset.description}
                        </p>
                      </div>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-muted">
                        {asset.type}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-4">
                      <span>{asset.size}</span>
                      <span>•</span>
                      <span>{asset.formats.join(', ')}</span>
                    </div>

                    <Button asChild className="w-full">
                      <Link href={asset.downloadUrl}>Download</Link>
                    </Button>
                  </div>
                ))}
              </div>

              <div className="text-center">
                <Button variant="outline" size="lg">
                  Request Custom Assets
                </Button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Contact */}
      <section className="border-y border-border bg-muted/30 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="font-display text-3xl lg:text-4xl font-medium mb-6">
              Media Inquiries
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              For press inquiries, interview requests, or additional
              information, please contact our PR team.
            </p>
            <div className="flex flex-col sm:flex-row items-center gap-4 justify-center">
              <Button size="lg" className="h-14 px-8 text-base rounded-xl">
                Email PR Team
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="h-14 px-8 text-base rounded-xl"
              >
                Schedule Interview
              </Button>
            </div>
          </div>
        </div>
      </section>
    </MarketingLayout>
  );
}
