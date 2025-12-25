'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register plugin
if (typeof window !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
}

// ============================================================================
// QUOTE REVEAL - Elegant quote with word-by-word animation
// ============================================================================

interface QuoteRevealProps {
    quote: string;
    author?: string;
    className?: string;
    delay?: number;
}

export function QuoteReveal({
    quote,
    author,
    className = '',
    delay = 0,
}: QuoteRevealProps) {
    const quoteRef = useRef<HTMLParagraphElement>(null);
    const authorRef = useRef<HTMLElement>(null);

    useEffect(() => {
        const quoteElement = quoteRef.current;
        const authorElement = authorRef.current;
        if (!quoteElement) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        // Split quote into words
        const text = quoteElement.textContent || '';
        const words = text.split(' ');

        quoteElement.innerHTML = words
            .map((word) => `<span class="word-wrapper" style="display: inline-block; overflow: hidden;"><span class="word" style="display: inline-block;">${word}</span></span>`)
            .join(' ');

        const wordElements = quoteElement.querySelectorAll('.word');

        gsap.set(wordElements, { y: '100%', opacity: 0 });
        if (authorElement) {
            gsap.set(authorElement, { opacity: 0, y: 20 });
        }

        const tl = gsap.timeline({
            scrollTrigger: {
                trigger: quoteElement,
                start: 'top 80%',
            },
        });

        tl.to(wordElements, {
            y: '0%',
            opacity: 1,
            duration: 0.6,
            delay,
            stagger: 0.03,
            ease: 'power3.out',
        });

        if (authorElement) {
            tl.to(authorElement, {
                opacity: 1,
                y: 0,
                duration: 0.6,
                ease: 'power2.out',
            }, '-=0.3');
        }

        return () => {
            quoteElement.innerHTML = text;
            tl.kill();
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === quoteElement) {
                    trigger.kill();
                }
            });
        };
    }, [quote, delay]);

    return (
        <blockquote className={`text-center ${className}`}>
            <p
                ref={quoteRef}
                className="font-display text-3xl lg:text-4xl font-medium leading-relaxed text-foreground"
            >
                &quot;{quote}&quot;
            </p>
            {author && (
                <footer
                    ref={authorRef}
                    className="block mt-6 text-sm text-muted-foreground not-italic"
                >
                    — {author}
                </footer>
            )}
        </blockquote>
    );
}

// ============================================================================
// HIGHLIGHT QUOTE - Quote with highlighted key words
// ============================================================================

interface HighlightQuoteProps {
    text: string;
    highlights: string[];
    className?: string;
}

export function HighlightQuote({
    text,
    highlights,
    className = '',
}: HighlightQuoteProps) {
    const quoteRef = useRef<HTMLParagraphElement>(null);

    useEffect(() => {
        const quote = quoteRef.current;
        if (!quote) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const highlightSpans = quote.querySelectorAll('.highlight-word');

        gsap.set(highlightSpans, {
            backgroundSize: '0% 100%',
        });

        gsap.to(highlightSpans, {
            backgroundSize: '100% 100%',
            duration: 0.8,
            stagger: 0.2,
            ease: 'power2.out',
            scrollTrigger: {
                trigger: quote,
                start: 'top 80%',
            },
        });

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === quote) {
                    trigger.kill();
                }
            });
        };
    }, [text, highlights]);

    // Create highlighted text
    let processedText = text;
    highlights.forEach((highlight) => {
        processedText = processedText.replace(
            new RegExp(`(${highlight})`, 'gi'),
            `<span class="highlight-word" style="background: linear-gradient(90deg, hsl(var(--accent) / 0.3) 0%, hsl(var(--accent) / 0.3) 100%); background-repeat: no-repeat; background-position: 0 80%; padding: 0 4px; margin: 0 -4px;">$1</span>`
        );
    });

    return (
        <p
            ref={quoteRef}
            className={`font-display text-2xl lg:text-3xl font-medium leading-relaxed ${className}`}
            dangerouslySetInnerHTML={{ __html: processedText }}
        />
    );
}

// ============================================================================
// TESTIMONIAL CARD - Animated testimonial with author info
// ============================================================================

interface TestimonialProps {
    quote: string;
    author: string;
    role?: string;
    company?: string;
    className?: string;
    delay?: number;
}

export function TestimonialCard({
    quote,
    author,
    role,
    company,
    className = '',
    delay = 0,
}: TestimonialProps) {
    const cardRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const card = cardRef.current;
        if (!card) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        gsap.set(card, { opacity: 0, y: 40 });

        gsap.to(card, {
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay,
            ease: 'power3.out',
            scrollTrigger: {
                trigger: card,
                start: 'top 85%',
            },
        });

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === card) {
                    trigger.kill();
                }
            });
        };
    }, [delay]);

    return (
        <div
            ref={cardRef}
            className={`bg-card border border-border rounded-2xl p-8 ${className}`}
        >
            <blockquote>
                <p className="text-lg leading-relaxed text-foreground mb-6">
                    &quot;{quote}&quot;
                </p>
                <footer className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                        <span className="text-lg font-medium">{author.charAt(0)}</span>
                    </div>
                    <div>
                        <div className="font-medium text-foreground">{author}</div>
                        {(role || company) && (
                            <div className="text-sm text-muted-foreground">
                                {role}{role && company && ' · '}{company}
                            </div>
                        )}
                    </div>
                </footer>
            </blockquote>
        </div>
    );
}
