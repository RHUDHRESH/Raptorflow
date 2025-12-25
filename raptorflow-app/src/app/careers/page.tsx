'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

const openPositions = [
    {
        id: 'senior-frontend-engineer',
        title: 'Senior Frontend Engineer',
        department: 'Engineering',
        location: 'Remote (Global)',
        type: 'Full-time',
        experience: 'Senior',
        salary: '$120k - $180k',
        posted: '2024-12-15',
        description: 'Build the frontend experience for our marketing operating system. You will work on React, Next.js, and modern web technologies to create beautiful, performant interfaces that founders love.',
        requirements: [
            '5+ years of frontend development experience',
            'Expert knowledge of React, TypeScript, and modern CSS',
            'Experience with Next.js and server-side rendering',
            'Strong understanding of UX/UI principles',
            'Ability to work independently in a remote environment',
        ],
        responsibilities: [
            'Lead frontend development for new features',
            'Collaborate with design and product teams',
            'Optimize application performance and user experience',
            'Mentor junior engineers and establish best practices',
            'Contribute to technical architecture decisions',
        ],
        benefits: ['Equity package', 'Flexible work hours', 'Home office stipend', 'Learning budget'],
        teamSize: 8,
        growth: 'Senior → Staff → Principal Engineer',
    },
    {
        id: 'product-marketing-manager',
        title: 'Product Marketing Manager',
        department: 'Marketing',
        location: 'Remote (Global)',
        type: 'Full-time',
        experience: 'Mid-level',
        salary: '$90k - $130k',
        posted: '2024-12-10',
        description: 'Drive product marketing strategy and execution for RaptorFlow. You will own positioning, messaging, and go-to-market for new features and products that help founders succeed.',
        requirements: [
            '4+ years of product marketing experience',
            'Experience with B2B SaaS products',
            'Strong writing and communication skills',
            'Ability to translate complex features into clear benefits',
            'Data-driven approach to marketing decisions',
        ],
        responsibilities: [
            'Develop product positioning and messaging',
            'Create launch strategies for new features',
            'Write compelling copy for website and campaigns',
            'Analyze market trends and competitive landscape',
            'Collaborate with product and sales teams',
        ],
        benefits: ['Equity package', 'Flexible work hours', 'Conference budget', 'Professional development'],
        teamSize: 4,
        growth: 'PM → Senior PM → Head of Product Marketing',
    },
    {
        id: 'customer-success-manager',
        title: 'Customer Success Manager',
        department: 'Customer Success',
        location: 'Remote (Global)',
        type: 'Full-time',
        experience: 'Mid-level',
        salary: '$70k - $100k',
        posted: '2024-12-08',
        description: 'Help founders succeed with RaptorFlow. You will onboard customers, provide strategic guidance, and ensure they get maximum value from our marketing operating system.',
        requirements: [
            '3+ years of customer success or account management experience',
            'Experience working with founders and small businesses',
            'Strong problem-solving and communication skills',
            'Ability to understand customer needs and translate to product feedback',
            'Passion for helping businesses grow',
        ],
        responsibilities: [
            'Onboard new customers and ensure successful implementation',
            'Provide strategic guidance and best practices',
            'Gather customer feedback and work with product team',
            'Create customer success stories and case studies',
            'Maintain high customer satisfaction and retention',
        ],
        benefits: ['Equity package', 'Flexible work hours', 'Health insurance', 'Remote work setup'],
        teamSize: 3,
        growth: 'CSM → Senior CSM → Head of Customer Success',
    },
    {
        id: 'backend-engineer',
        title: 'Backend Engineer',
        department: 'Engineering',
        location: 'Remote (Global)',
        type: 'Full-time',
        experience: 'Mid-level',
        salary: '$100k - $150k',
        posted: '2024-12-05',
        description: 'Build scalable backend systems for our marketing operating system. You will work on APIs, data processing, and infrastructure that powers our platform.',
        requirements: [
            '4+ years of backend development experience',
            'Strong knowledge of Python, Node.js, or similar',
            'Experience with databases and data modeling',
            'Understanding of cloud services and DevOps',
            'Ability to design scalable systems',
        ],
        responsibilities: [
            'Develop and maintain backend APIs',
            'Design database schemas and data models',
            'Implement monitoring and logging systems',
            'Collaborate with frontend team on integrations',
            'Participate in code reviews and architecture discussions',
        ],
        benefits: ['Equity package', 'Flexible work hours', 'Home office stipend', 'Tech budget'],
        teamSize: 6,
        growth: 'Engineer → Senior → Staff Engineer',
    },
    {
        id: 'ai-researcher',
        title: 'AI Research Engineer',
        department: 'AI',
        location: 'Remote (Global)',
        type: 'Full-time',
        experience: 'Senior',
        salary: '$130k - $180k',
        posted: '2024-12-01',
        description: 'Push the boundaries of AI in marketing. You will work on cutting-edge machine learning models for content generation, campaign optimization, and market intelligence.',
        requirements: [
            '5+ years of AI/ML research or engineering experience',
            'Strong background in NLP and deep learning',
            'Experience with large language models',
            'Proficiency in Python and ML frameworks',
            'Published research or significant projects',
        ],
        responsibilities: [
            'Research and develop new AI models for marketing',
            'Implement and optimize ML pipelines',
            'Collaborate with product team on AI features',
            'Stay current with latest AI research and trends',
            'Contribute to technical publications and presentations',
        ],
        benefits: ['Equity package', 'Flexible work hours', 'Research budget', 'Conference attendance'],
        teamSize: 5,
        growth: 'Researcher → Senior → Principal AI Scientist',
    },
];

const departments = ['All', 'Engineering', 'Marketing', 'Customer Success', 'AI'];
const locations = ['All', 'Remote (Global)', 'Hybrid', 'On-site'];
const types = ['All', 'Full-time', 'Part-time', 'Contract'];

const benefits = [
    'Competitive salary and equity',
    'Flexible work hours and remote-first culture',
    'Health, dental, and vision insurance',
    'Unlimited PTO',
    'Learning and development budget',
    'Top-tier hardware and tools',
    'Regular team retreats',
];

export default function CareersPage() {
    const [selectedDepartment, setSelectedDepartment] = useState('All');
    const [selectedLocation, setSelectedLocation] = useState('All');
    const [selectedType, setSelectedType] = useState('All');
    const [searchTerm, setSearchTerm] = useState('');

    const filteredPositions = openPositions.filter(position => {
        const matchesDepartment = selectedDepartment === 'All' || position.department === selectedDepartment;
        const matchesLocation = selectedLocation === 'All' || position.location === selectedLocation;
        const matchesType = selectedType === 'All' || position.type === selectedType;
        const matchesSearch = position.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            position.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            position.requirements.some(req => req.toLowerCase().includes(searchTerm.toLowerCase()));

        return matchesDepartment && matchesLocation && matchesType && matchesSearch;
    });

    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            Careers
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            Build the future of marketing.
                        </h1>
                        <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed mb-8">
                            Join a team that is obsessed with helping founders build marketing that actually compounds.
                        </p>

                        {/* Stats */}
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                            <div className="text-center">
                                <div className="text-3xl font-bold mb-2">25+</div>
                                <div className="text-sm text-muted-foreground">Team Members</div>
                            </div>
                            <div className="text-center">
                                <div className="text-3xl font-bold mb-2">15+</div>
                                <div className="text-sm text-muted-foreground">Countries</div>
                            </div>
                            <div className="text-center">
                                <div className="text-3xl font-bold mb-2">100%</div>
                                <div className="text-sm text-muted-foreground">Remote</div>
                            </div>
                            <div className="text-center">
                                <div className="text-3xl font-bold mb-2">$2M</div>
                                <div className="text-sm text-muted-foreground">Raised</div>
                            </div>
                        </div>

                        <Button size="lg" className="h-14 px-8 text-base rounded-xl">
                            View Open Positions
                        </Button>
                    </div>
                </div>
            </section>

            {/* Search and Filters */}
            <section className="pb-16">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="max-w-4xl mx-auto space-y-6">
                        {/* Search */}
                        <div className="relative">
                            <input
                                type="search"
                                placeholder="Search positions..."
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

                        {/* Filters */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Department Filter */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Department</label>
                                <div className="flex flex-wrap gap-2">
                                    {departments.map((dept) => (
                                        <button
                                            key={dept}
                                            onClick={() => setSelectedDepartment(dept)}
                                            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                selectedDepartment === dept
                                                    ? 'bg-foreground text-background'
                                                    : 'bg-muted text-muted-foreground hover:bg-foreground/10'
                                            }`}
                                        >
                                            {dept}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Location Filter */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Location</label>
                                <div className="flex flex-wrap gap-2">
                                    {locations.map((loc) => (
                                        <button
                                            key={loc}
                                            onClick={() => setSelectedLocation(loc)}
                                            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                selectedLocation === loc
                                                    ? 'bg-foreground text-background'
                                                    : 'bg-muted text-muted-foreground hover:bg-foreground/10'
                                            }`}
                                        >
                                            {loc}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Type Filter */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Type</label>
                                <div className="flex flex-wrap gap-2">
                                    {types.map((type) => (
                                        <button
                                            key={type}
                                            onClick={() => setSelectedType(type)}
                                            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                                                selectedType === type
                                                    ? 'bg-foreground text-background'
                                                    : 'bg-muted text-muted-foreground hover:bg-foreground/10'
                                            }`}
                                        >
                                            {type}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
                            {/* Open Positions */}
            <section className="pb-24 lg:pb-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-4">Open Positions</h2>
                        <p className="text-lg text-muted-foreground">
                            {filteredPositions.length} position{filteredPositions.length !== 1 ? 's' : ''} available
                        </p>
                    </div>

                    <div className="space-y-6">
                        {filteredPositions.map((position) => (
                            <div
                                key={position.id}
                                className="rounded-xl border border-border bg-card p-8 hover:border-foreground/20 transition-all duration-200 hover:shadow-lg"
                            >
                                <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6 mb-6">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-3">
                                            <h3 className="font-display text-2xl font-semibold">{position.title}</h3>
                                            <span className="px-3 py-1 rounded-full text-xs font-medium bg-foreground text-background">
                                                {position.experience}
                                            </span>
                                        </div>
                                        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-4">
                                            <div className="flex items-center gap-1">
                                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                                </svg>
                                                <span>{position.department}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                                </svg>
                                                <span>{position.location}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                                </svg>
                                                <span>{position.type}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                                <span>{position.salary}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                                </svg>
                                                <span>Posted {position.posted}</span>
                                            </div>
                                        </div>
                                        <p className="text-muted-foreground leading-relaxed mb-4">{position.description}</p>
                                    </div>
                                    <div className="flex flex-col gap-3">
                                        <Button asChild className="w-full lg:w-auto">
                                            <Link href={`/careers/${position.id}`}>Apply Now</Link>
                                        </Button>
                                        <Button variant="outline" className="w-full lg:w-auto">
                                            Save Position
                                        </Button>
                                    </div>
                                </div>

                                <div className="grid lg:grid-cols-3 gap-6">
                                    {/* Requirements */}
                                    <div>
                                        <h4 className="font-semibold mb-3">Requirements</h4>
                                        <ul className="space-y-2">
                                            {position.requirements.map((req, index) => (
                                                <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                                                    <svg className="h-4 w-4 text-foreground mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                    </svg>
                                                    <span>{req}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Responsibilities */}
                                    <div>
                                        <h4 className="font-semibold mb-3">Responsibilities</h4>
                                        <ul className="space-y-2">
                                            {position.responsibilities.map((resp, index) => (
                                                <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                                                    <svg className="h-4 w-4 text-foreground mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                    </svg>
                                                    <span>{resp}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Team Info */}
                                    <div>
                                        <h4 className="font-semibold mb-3">Team & Growth</h4>
                                        <div className="space-y-3">
                                            <div>
                                                <div className="text-sm text-muted-foreground">Team Size</div>
                                                <div className="font-medium">{position.teamSize} members</div>
                                            </div>
                                            <div>
                                                <div className="text-sm text-muted-foreground">Career Path</div>
                                                <div className="font-medium text-sm">{position.growth}</div>
                                            </div>
                                            <div>
                                                <div className="text-sm text-muted-foreground mb-2">Key Benefits</div>
                                                <div className="flex flex-wrap gap-1">
                                                    {position.benefits.slice(0, 2).map((benefit) => (
                                                        <span key={benefit} className="text-xs bg-muted px-2 py-1 rounded-md">
                                                            {benefit}
                                                        </span>
                                                    ))}
                                                    {position.benefits.length > 2 && (
                                                        <span className="text-xs bg-muted px-2 py-1 rounded-md">
                                                            +{position.benefits.length - 2}
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {filteredPositions.length === 0 && (
                        <div className="text-center py-12">
                            <p className="text-muted-foreground">No positions found matching your criteria.</p>
                        </div>
                    )}
                </div>
            </section>
                        {/* Why Join */}
            <section className="border-y border-border bg-muted/30 py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-12">Why Join RaptorFlow</h2>
                        <div className="grid lg:grid-cols-2 gap-8">
                            <div>
                                <h3 className="text-xl font-semibold mb-4">Mission-Driven Work</h3>
                                <p className="text-muted-foreground mb-6">
                                    We are not just building another SaaS tool. We are solving a real problem that affects millions of founders worldwide. Your work will directly help businesses grow and succeed.
                                </p>
                                <h3 className="text-xl font-semibold mb-4">Learn and Grow</h3>
                                <p className="text-muted-foreground">
                                    Work alongside experienced founders, marketers, and engineers. You will be challenged, learn constantly, and have opportunities to take on more responsibility.
                                </p>
                            </div>
                            <div>
                                <h3 className="text-xl font-semibold mb-4">Remote-First Culture</h3>
                                <p className="text-muted-foreground mb-6">
                                    We are distributed across the globe but connected by our mission. Work from anywhere, with flexible hours that fit your life. We care about results, not face time.
                                </p>
                                <h3 className="text-xl font-semibold mb-4">Build in Public</h3>
                                <p className="text-muted-foreground">
                                    We believe in transparency and building in public. You will have direct access to users, see the impact of your work, and help shape the future of the product.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Benefits */}
            <section className="py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-12">Benefits & Perks</h2>
                        <div className="grid lg:grid-cols-2 gap-6">
                            {benefits.map((benefit) => (
                                <div key={benefit} className="flex items-center gap-3">
                                    <div className="h-2 w-2 rounded-full bg-foreground" />
                                    <span className="text-lg">{benefit}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Culture */}
            <section className="border-y border-border bg-muted/30 py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-12">Our Culture</h2>
                        <div className="grid lg:grid-cols-3 gap-8">
                            <div>
                                <div className="w-12 h-12 rounded-full bg-foreground text-background flex items-center justify-center mx-auto mb-4">
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-lg mb-2">Move Fast</h3>
                                <p className="text-muted-foreground text-sm">
                                    We ship quickly and iterate based on feedback. Speed is our competitive advantage.
                                </p>
                            </div>
                            <div>
                                <div className="w-12 h-12 rounded-full bg-foreground text-background flex items-center justify-center mx-auto mb-4">
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-lg mb-2">Customer Obsessed</h3>
                                <p className="text-muted-foreground text-sm">
                                    We start with the customer and work backwards. Their success is our success.
                                </p>
                            </div>
                            <div>
                                <div className="w-12 h-12 rounded-full bg-foreground text-background flex items-center justify-center mx-auto mb-4">
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                </div>
                                <h3 className="font-semibold text-lg mb-2">Always Learning</h3>
                                <p className="text-muted-foreground text-sm">
                                    We stay curious and embrace challenges. Every day is an opportunity to grow.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-6">
                            Ready to build the future?
                        </h2>
                        <p className="text-lg text-muted-foreground mb-8">
                            Join us in helping millions of founders build marketing that actually compounds.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center gap-4 justify-center">
                            <Button size="lg" className="h-14 px-8 text-base rounded-xl">
                                View All Positions
                            </Button>
                            <Button variant="outline" size="lg" className="h-14 px-8 text-base rounded-xl">
                                Learn More
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
