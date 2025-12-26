'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ImagePlaceholder } from '@/components/ui/ImagePlaceholder';
import { ArrowRight, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

gsap.registerPlugin(ScrollTrigger);

// Import the new animation styles
import '@/styles/landing-animations.css';

export function CinematicHero() {
    const sectionRef = useRef<HTMLDivElement>(null);
    const headlineRef = useRef<HTMLDivElement>(null);
    const productRef = useRef<HTMLDivElement>(null);
    const ctaRef = useRef<HTMLDivElement>(null);
    const eyebrowRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const ctx = gsap.context(() => {
            // Create a master timeline
            const tl = gsap.timeline({ delay: 0.3 });

            // Eyebrow entrance
            tl.from(eyebrowRef.current, {
                opacity: 0,
                y: 20,
                duration: 0.6,
                ease: 'power3.out',
            });

            // Headline word-by-word reveal
            tl.from('.hero-word', {
                opacity: 0,
                y: 80,
                rotationX: -40,
                stagger: 0.08,
                duration: 0.8,
                ease: 'power4.out',
            }, '-=0.3');

            // Subheadline
            tl.from('.hero-subhead', {
                opacity: 0,
                y: 30,
                duration: 0.6,
                ease: 'power3.out',
            }, '-=0.4');

            // CTA buttons
            tl.from(ctaRef.current?.children || [], {
                opacity: 0,
                y: 20,
                stagger: 0.1,
                duration: 0.5,
                ease: 'power3.out',
            }, '-=0.3');

            // Product mockup - dramatic entrance
            tl.from(productRef.current, {
                opacity: 0,
                scale: 0.85,
                y: 60,
                rotationY: -10,
                duration: 1.2,
                ease: 'power3.out',
            }, '-=0.8');

            // Floating badges entrance
            tl.from('.floating-badge', {
                opacity: 0,
                scale: 0,
                stagger: 0.15,
                duration: 0.5,
                ease: 'back.out(1.7)',
            }, '-=0.5');

            // Continuous floating animation for product
            gsap.to(productRef.current, {
                y: -15,
                duration: 3,
                ease: 'sine.inOut',
                repeat: -1,
                yoyo: true,
            });

            // Parallax on scroll
            gsap.to(headlineRef.current, {
                y: 150,
                opacity: 0.3,
                scrollTrigger: {
                    trigger: sectionRef.current,
                    start: 'top top',
                    end: 'bottom top',
                    scrub: 1,
                },
            });

            gsap.to(productRef.current, {
                y: -80,
                scrollTrigger: {
                    trigger: sectionRef.current,
                    start: 'top top',
                    end: 'bottom top',
                    scrub: 1,
                },
            });
        }, sectionRef);

        return () => ctx.revert();
    }, []);

    const headlineWords = ['Marketing.', 'Finally', 'under', 'control.'];

    return (
        <section
            ref={sectionRef}
            className="relative min-h-screen flex items-center overflow-hidden"
        >
            {/* Background gradient mesh */}
            <div className="absolute inset-0 gradient-mesh-light dark:gradient-mesh-dark -z-10" />

            {/* Subtle grid pattern */}
            <div className="absolute inset-0 opacity-[0.015] -z-10">
                <svg className="w-full h-full">
                    <defs>
                        <pattern id="hero-grid" width="60" height="60" patternUnits="userSpaceOnUse">
                            <path d="M 60 0 L 0 0 0 60" fill="none" stroke="currentColor" strokeWidth="1" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#hero-grid)" />
                </svg>
            </div>

            {/* Floating ambient orbs */}
            <div className="absolute top-20 left-[10%] w-96 h-96 rounded-full bg-gradient-to-br from-zinc-200/20 to-transparent blur-3xl -z-10 floating-slow" />
            <div className="absolute bottom-20 right-[15%] w-80 h-80 rounded-full bg-gradient-to-br from-zinc-300/15 to-transparent blur-3xl -z-10 floating-drift" />

            <div className="mx-auto max-w-7xl px-6 lg:px-8 py-32 lg:py-40">
                <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
                    {/* Left: Content */}
                    <div className="text-center lg:text-left">
                        {/* Eyebrow */}
                        <div ref={eyebrowRef} className="mb-8">
                            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-border/50 bg-background/50 backdrop-blur-sm text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                                <Sparkles className="w-3.5 h-3.5" />
                                The Founder Marketing OS
                            </span>
                        </div>

                        {/* Headline */}
                        <div ref={headlineRef} className="mb-8 overflow-hidden">
                            <h1 className="font-display fluid-headline font-semibold tracking-tight">
                                {headlineWords.map((word, i) => (
                                    <span
                                        key={i}
                                        className={cn(
                                            'hero-word inline-block mr-[0.25em]',
                                            i === 0 && 'text-foreground',
                                            i > 0 && i < 3 && 'text-muted-foreground/80',
                                            i === 3 && 'text-foreground'
                                        )}
                                        style={{ transformStyle: 'preserve-3d' }}
                                    >
                                        {word}
                                    </span>
                                ))}
                            </h1>
                        </div>

                        {/* Subheadline */}
                        <p className="hero-subhead text-lg lg:text-xl text-muted-foreground leading-relaxed mb-10 max-w-xl mx-auto lg:mx-0">
                            Turn messy business context into clear positioning and a 90-day marketing war plan—then ship weekly Moves that compound into revenue.
                        </p>

                        {/* CTAs */}
                        <div ref={ctaRef} className="flex flex-col sm:flex-row items-center lg:items-start justify-center lg:justify-start gap-4">
                            <Button
                                asChild
                                size="lg"
                                className="h-14 px-8 text-base rounded-xl bg-foreground text-background hover:bg-foreground/90 interactive-lift"
                            >
                                <Link href="/login" className="group inline-flex items-center gap-2">
                                    Get Started Free
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </Link>
                            </Button>
                            <Button
                                asChild
                                variant="outline"
                                size="lg"
                                className="h-14 px-8 text-base rounded-xl border-border/50 interactive-lift"
                            >
                                <Link href="#demo">Watch Demo</Link>
                            </Button>
                        </div>

                        {/* Trust indicators */}
                        <div className="mt-12 flex items-center gap-6 justify-center lg:justify-start">
                            <div className="flex -space-x-3">
                                {[1, 2, 3, 4, 5].map((i) => (
                                    <div
                                        key={i}
                                        className="w-9 h-9 rounded-full border-2 border-background bg-gradient-to-br from-zinc-300 to-zinc-500 dark:from-zinc-600 dark:to-zinc-800"
                                        style={{ zIndex: 5 - i }}
                                    />
                                ))}
                            </div>
                            <p className="text-sm text-muted-foreground">
                                <span className="font-semibold text-foreground">500+</span> founders shipping weekly
                            </p>
                        </div>
                    </div>

                    {/* Right: Product Mockup */}
                    <div ref={productRef} className="relative">
                        {/* Main product image - tilted for dynamism */}
                        <div className="tilted-card-right depth-layer-hero rounded-2xl overflow-hidden">
                            <ImagePlaceholder
                                prompt="3D isometric floating dashboard mockup. Dark mode UI with clean cards showing analytics, AI chat, and campaign timeline. Subtle glow effects around edges. Product cards breaking out of frame with soft shadows. Premium SaaS aesthetic, no device frames. Zinc/platinum color palette with subtle gold accents. 4K render quality."
                                aspectRatio="square"
                                size="lg"
                            />
                        </div>

                        {/* Floating badges that "break out" */}
                        <div className="floating-badge absolute -top-4 -left-4 lg:-left-8 bg-background/95 backdrop-blur-sm rounded-xl px-4 py-3 border border-border/50 depth-layer-2">
                            <p className="text-sm font-semibold flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                                10min Setup
                            </p>
                        </div>

                        <div className="floating-badge absolute -bottom-4 -right-4 lg:-right-8 bg-background/95 backdrop-blur-sm rounded-xl px-4 py-3 border border-border/50 depth-layer-2">
                            <p className="text-sm font-semibold flex items-center gap-2">
                                <Sparkles className="w-4 h-4 text-amber-500" />
                                AI-Powered
                            </p>
                        </div>

                        <div className="floating-badge absolute top-1/2 -left-6 lg:-left-12 -translate-y-1/2 bg-background/95 backdrop-blur-sm rounded-xl px-4 py-3 border border-border/50 depth-layer-2">
                            <p className="text-sm font-semibold">7 Moves/week</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Scroll indicator */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-muted-foreground/50">
                <span className="text-xs uppercase tracking-widest">Scroll</span>
                <div className="w-5 h-8 rounded-full border border-current flex items-start justify-center p-1">
                    <div className="w-1 h-2 rounded-full bg-current animate-bounce" />
                </div>
            </div>
        </section>
    );
}
