'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const blogPosts = [
    {
        id: 'marketing-compounds',
        title: 'Marketing Should Compound, Not Reset Every Monday',
        excerpt: 'Why most founders are stuck in the "try marketing" loop and how to build a system that actually compounds.',
        author: 'RaptorFlow Team',
        authorAvatar: '/images/team/raptorflow.jpg',
        date: '2024-12-18',
        readTime: '8 min read',
        category: 'Strategy',
        featured: true,
        tags: ['Marketing Strategy', 'Growth', 'Systems', 'Compound Effect'],
        views: 2456,
        likes: 189,
        comments: 23,
        coverImage: '/images/blog/marketing-compounds.jpg',
        content: 'Most founders treat marketing like a slot machine...',
    },
    {
        id: 'positioning-playbook',
        title: 'The Positioning Playbook: From Messy Context to Crystal Clear',
        excerpt: 'A step-by-step guide to extracting positioning from your head and putting it into your marketing.',
        author: 'Sarah Chen',
        authorAvatar: '/images/team/sarah.jpg',
        date: '2024-12-15',
        readTime: '12 min read',
        category: 'Foundation',
        featured: false,
        tags: ['Positioning', 'Strategy', 'Brand', 'Messaging'],
        views: 1823,
        likes: 145,
        comments: 18,
        coverImage: '/images/blog/positioning-playbook.jpg',
        content: 'Positioning is the foundation of all marketing...',
    },
    {
        id: 'moves-vs-campaigns',
        title: 'Moves vs Campaigns: What Actually Drives Growth',
        excerpt: 'Understanding the difference between strategic campaigns and tactical moves—and why you need both.',
        author: 'Mike Johnson',
        authorAvatar: '/images/team/mike.jpg',
        date: '2024-12-10',
        readTime: '6 min read',
        category: 'Execution',
        featured: false,
        tags: ['Campaigns', 'Moves', 'Growth', 'Strategy'],
        views: 1567,
        likes: 98,
        comments: 12,
        coverImage: '/images/blog/moves-vs-campaigns.jpg',
        content: 'The distinction between moves and campaigns...',
    },
    {
        id: 'blackbox-experiments',
        title: 'Inside the Blackbox: How We Test Marketing Ideas',
        excerpt: 'A look at our experimental sandbox for growth marketing and how you can apply the same principles.',
        author: 'Alex Rivera',
        authorAvatar: '/images/team/alex.jpg',
        date: '2024-12-05',
        readTime: '10 min read',
        category: 'Innovation',
        featured: false,
        tags: ['Blackbox', 'Experiments', 'Testing', 'Innovation'],
        views: 2134,
        likes: 167,
        comments: 31,
        coverImage: '/images/blog/blackbox-experiments.jpg',
        content: 'Our Blackbox experimental lab represents...',
    },
    {
        id: 'muse-ai-assistant',
        title: 'Building Muse: The AI Assistant That Actually Gets Your Brand',
        excerpt: 'The story behind Muse, our AI assistant that understands brand voice and creates authentic content.',
        author: 'Emma Wilson',
        authorAvatar: '/images/team/emma.jpg',
        date: '2024-12-01',
        readTime: '15 min read',
        category: 'AI',
        featured: false,
        tags: ['AI', 'Muse', 'Content', 'Brand Voice'],
        views: 3456,
        likes: 289,
        comments: 45,
        coverImage: '/images/blog/muse-ai-assistant.jpg',
        content: 'Building Muse was our most ambitious project...',
    },
    {
        id: 'radar-intelligence',
        title: 'Radar Intelligence: Seeing Around Marketing Corners',
        excerpt: 'How our market intelligence system helps founders anticipate trends and opportunities before competitors.',
        author: 'David Kim',
        authorAvatar: '/images/team/david.jpg',
        date: '2024-11-28',
        readTime: '9 min read',
        category: 'Analytics',
        featured: false,
        tags: ['Radar', 'Intelligence', 'Trends', 'Analytics'],
        views: 1789,
        likes: 134,
        comments: 19,
        coverImage: '/images/blog/radar-intelligence.jpg',
        content: 'Market intelligence shouldn\'t be a luxury...',
    },
    {
        id: 'cohort-mastery',
        title: 'Cohort Mastery: From Data to Decisions',
        excerpt: 'A practical guide to cohort analysis that turns user behavior into actionable insights.',
        author: 'Lisa Park',
        authorAvatar: '/images/team/lisa.jpg',
        date: '2024-11-25',
        readTime: '11 min read',
        category: 'Analytics',
        featured: false,
        tags: ['Cohorts', 'Analytics', 'Data', 'Insights'],
        views: 1456,
        likes: 112,
        comments: 15,
        coverImage: '/images/blog/cohort-mastery.jpg',
        content: 'Cohort analysis is the cornerstone of...',
    },
    {
        id: 'foundation-framework',
        title: 'The Foundation Framework: Marketing Architecture That Scales',
        excerpt: 'How to build a marketing foundation that scales from startup to enterprise without breaking.',
        author: 'RaptorFlow Team',
        authorAvatar: '/images/team/raptorflow.jpg',
        date: '2024-11-20',
        readTime: '14 min read',
        category: 'Strategy',
        featured: false,
        tags: ['Foundation', 'Architecture', 'Scale', 'Strategy'],
        views: 2234,
        likes: 198,
        comments: 28,
        coverImage: '/images/blog/foundation-framework.jpg',
        content: 'Most marketing systems break as companies scale...',
    },
];

const categories = ['All', 'Strategy', 'Foundation', 'Execution', 'Innovation', 'AI', 'Analytics'];
const popularTags = ['Marketing Strategy', 'Growth', 'AI', 'Analytics', 'Positioning'];

export default function BlogPage() {
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [searchTerm, setSearchTerm] = useState('');

    const filteredPosts = blogPosts.filter(post => {
        const matchesCategory = selectedCategory === 'All' || post.category === selectedCategory;
        const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            post.excerpt.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            post.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
        return matchesCategory && matchesSearch;
    });

    const featuredPost = blogPosts.find(post => post.featured);
    const regularPosts = filteredPosts.filter(post => !post.featured);

    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Blog
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            Thoughts on building marketing that works.
                        </h1>
                        <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed mb-8">
                            Insights, frameworks, and case studies from our journey building the marketing operating system for founders.
                        </p>

                        {/* Search and Filter */}
                        <div className="max-w-2xl mx-auto space-y-4">
                            <div className="relative">
                                <input
                                    type="search"
                                    placeholder="Search articles..."
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
                            {/* Featured Post */}
            {featuredPost && (
                <section className="pb-16 lg:pb-24">
                    <div className="mx-auto max-w-7xl px-6 lg:px-8">
                        <div className="rounded-2xl border border-border bg-card p-8 lg:p-12 hover:shadow-lg transition-shadow duration-200">
                            <div className="flex items-center gap-3 mb-4">
                                <span className="px-3 py-1 rounded-full text-xs font-medium bg-foreground text-background">
                                    Featured
                                </span>
                                <span className="px-3 py-1 rounded-full text-xs font-medium bg-muted">
                                    {featuredPost.category}
                                </span>
                            </div>
                            <h2 className="font-display text-3xl lg:text-4xl font-medium mb-4">
                                {featuredPost.title}
                            </h2>
                            <p className="text-lg text-muted-foreground mb-6 max-w-3xl leading-relaxed">
                                {featuredPost.excerpt}
                            </p>

                            {/* Author Info */}
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                                        <span className="text-sm font-medium">{featuredPost.author.charAt(0)}</span>
                                    </div>
                                    <div>
                                        <div className="font-medium">{featuredPost.author}</div>
                                        <div className="text-sm text-muted-foreground">
                                            {featuredPost.date} • {featuredPost.readTime}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                    <div className="flex items-center gap-1">
                                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                        </svg>
                                        <span>{featuredPost.views.toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                        </svg>
                                        <span>{featuredPost.likes}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                        </svg>
                                        <span>{featuredPost.comments}</span>
                                    </div>
                                </div>
                            </div>

                            <Button asChild size="lg">
                                <Link href={`/blog/${featuredPost.id}`}>Read Article</Link>
                            </Button>
                        </div>
                    </div>
                </section>
            )}

            {/* Blog Grid */}
            <section className="pb-24 lg:pb-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="grid lg:grid-cols-3 gap-8">
                        {regularPosts.map((post) => (
                            <article key={post.id} className="group">
                                <div className="rounded-xl border border-border bg-card overflow-hidden hover:border-foreground/20 transition-all duration-200 hover:shadow-lg">
                                    {/* Cover Image */}
                                    <div className="h-48 bg-muted relative">
                                        <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
                                        <div className="absolute top-4 left-4">
                                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-foreground text-background">
                                                {post.category}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="p-6">
                                        <h3 className="font-semibold text-lg mb-3 group-hover:text-foreground transition-colors">
                                            <Link href={`/blog/${post.id}`} className="hover:underline">
                                                {post.title}
                                            </Link>
                                        </h3>
                                        <p className="text-muted-foreground text-sm mb-4 leading-relaxed">
                                            {post.excerpt}
                                        </p>

                                        {/* Tags */}
                                        <div className="flex flex-wrap gap-1 mb-4">
                                            {post.tags.slice(0, 2).map((tag) => (
                                                <span key={tag} className="text-xs bg-muted px-2 py-1 rounded-md">
                                                    {tag}
                                                </span>
                                            ))}
                                            {post.tags.length > 2 && (
                                                <span className="text-xs bg-muted px-2 py-1 rounded-md">
                                                    +{post.tags.length - 2}
                                                </span>
                                            )}
                                        </div>

                                        {/* Meta */}
                                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                                            <div className="flex items-center gap-3">
                                                <span>{post.author}</span>
                                                <span>•</span>
                                                <span>{post.readTime}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <div className="flex items-center gap-1">
                                                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                                    </svg>
                                                    <span>{post.views}</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                                    </svg>
                                                    <span>{post.likes}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </article>
                        ))}
                    </div>

                    {filteredPosts.length === 0 && (
                        <div className="text-center py-12">
                            <p className="text-muted-foreground">No articles found matching your criteria.</p>
                        </div>
                    )}
                </div>
            </section>
                {/* Newsletter Signup */}
            <section className="border-y border-border bg-muted/30 py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <h2 className="font-display text-3xl font-medium mb-6">
                            Get insights in your inbox
                        </h2>
                        <p className="text-lg text-muted-foreground mb-8">
                            Weekly thoughts on marketing, strategy, and building products that people actually want.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center gap-4 max-w-md mx-auto">
                            <input
                                type="email"
                                placeholder="Enter your email"
                                className="flex-1 h-12 px-4 rounded-xl border border-border bg-background"
                            />
                            <Button size="lg" className="w-full sm:w-auto">
                                Subscribe
                            </Button>
                        </div>
                        <p className="text-sm text-muted-foreground mt-4">
                            No spam. Unsubscribe anytime.
                        </p>
                    </div>
                </div>
            </section>

            {/* Popular Tags */}
            <section className="py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="text-center mb-8">
                        <h3 className="font-display text-2xl font-medium mb-4">Popular Topics</h3>
                        <p className="text-muted-foreground">Explore our most popular content categories</p>
                    </div>
                    <div className="flex flex-wrap gap-3 justify-center">
                        {popularTags.map((tag) => (
                            <button
                                key={tag}
                                onClick={() => setSearchTerm(tag)}
                                className="px-4 py-2 rounded-full border border-border bg-background hover:bg-muted transition-colors text-sm"
                            >
                                {tag}
                            </button>
                        ))}
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="border-t border-border bg-foreground text-background py-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
                        <div>
                            <div className="text-3xl font-bold mb-2">50K+</div>
                            <div className="text-sm text-background/70">Monthly Readers</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-2">200+</div>
                            <div className="text-sm text-background/70">Articles Published</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-2">1M+</div>
                            <div className="text-sm text-background/70">Total Views</div>
                        </div>
                        <div>
                            <div className="text-3xl font-bold mb-2">Weekly</div>
                            <div className="text-sm text-background/70">New Content</div>
                        </div>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
