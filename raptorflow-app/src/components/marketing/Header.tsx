'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

const navLinks = [
    {
        label: 'Features',
        href: '/landing#features',
        dropdown: [
            { label: 'Foundation', href: '/features/foundation', description: 'BrandKit & positioning' },
            { label: 'Cohorts', href: '/features/cohorts', description: 'ICP & segmentation' },
            { label: 'Moves', href: '/features/moves', description: 'Weekly execution packets' },
            { label: 'Campaigns', href: '/features/campaigns', description: '90-day strategic arcs' },
            { label: 'Muse', href: '/features/muse', description: 'Asset factory & AI content' },
            { label: 'Matrix', href: '/features/matrix', description: 'Dashboard & analytics' },
            { label: 'Blackbox', href: '/features/blackbox', description: 'A/B testing & experiments' },
            { label: 'Radar', href: '/features/radar', description: 'Competitor intelligence' },
        ],
    },
    { label: 'Pricing', href: '/pricing' },
    { label: 'FAQ', href: '/faq' },
    { label: 'About', href: '/about' },
];

export function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [featuresOpen, setFeaturesOpen] = useState(false);

    return (
        <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
                <nav className="flex h-16 items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-lg bg-foreground flex items-center justify-center">
                                <span className="text-background font-display font-bold text-sm">RF</span>
                            </div>
                            <span className="font-display text-xl font-semibold tracking-tight">RaptorFlow</span>
                        </div>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden lg:flex lg:items-center lg:gap-8">
                        {navLinks.map((link) => (
                            <div key={link.label} className="relative">
                                {link.dropdown ? (
                                    <div
                                        className="relative"
                                        onMouseEnter={() => setFeaturesOpen(true)}
                                        onMouseLeave={() => setFeaturesOpen(false)}
                                    >
                                        <button className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1">
                                            {link.label}
                                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </button>
                                        {featuresOpen && (
                                            <div className="absolute top-full left-1/2 -translate-x-1/2 pt-4">
                                                <div className="w-[480px] rounded-xl border border-border bg-card p-4 shadow-lg grid grid-cols-2 gap-2">
                                                    {link.dropdown.map((item) => (
                                                        <Link
                                                            key={item.label}
                                                            href={item.href}
                                                            className="flex flex-col gap-1 rounded-lg p-3 hover:bg-muted transition-colors"
                                                        >
                                                            <span className="text-sm font-medium">{item.label}</span>
                                                            <span className="text-xs text-muted-foreground">{item.description}</span>
                                                        </Link>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <Link
                                        href={link.href}
                                        className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                                    >
                                        {link.label}
                                    </Link>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* CTA */}
                    <div className="hidden lg:flex lg:items-center lg:gap-4">
                        <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                            Log in
                        </Link>
                        <Button asChild className="h-10 px-6 rounded-xl">
                            <Link href="/login">Get Started</Link>
                        </Button>
                    </div>

                    {/* Mobile menu button */}
                    <button
                        className="lg:hidden p-2 -mr-2"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    >
                        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            {mobileMenuOpen ? (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            )}
                        </svg>
                    </button>
                </nav>

                {/* Mobile menu */}
                {mobileMenuOpen && (
                    <div className="lg:hidden py-4 border-t border-border">
                        <div className="flex flex-col gap-4">
                            {navLinks.map((link) => (
                                <div key={link.label}>
                                    {link.dropdown ? (
                                        <div className="flex flex-col gap-2">
                                            <span className="text-sm font-medium text-foreground">{link.label}</span>
                                            <div className="pl-4 flex flex-col gap-2">
                                                {link.dropdown.map((item) => (
                                                    <Link
                                                        key={item.label}
                                                        href={item.href}
                                                        className="text-sm text-muted-foreground hover:text-foreground"
                                                        onClick={() => setMobileMenuOpen(false)}
                                                    >
                                                        {item.label}
                                                    </Link>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        <Link
                                            href={link.href}
                                            className="text-sm font-medium text-muted-foreground hover:text-foreground"
                                            onClick={() => setMobileMenuOpen(false)}
                                        >
                                            {link.label}
                                        </Link>
                                    )}
                                </div>
                            ))}
                            <div className="pt-4 border-t border-border flex flex-col gap-3">
                                <Link href="/login" className="text-sm font-medium text-muted-foreground">
                                    Log in
                                </Link>
                                <Button asChild className="w-full h-12 rounded-xl">
                                    <Link href="/login">Get Started</Link>
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
}
