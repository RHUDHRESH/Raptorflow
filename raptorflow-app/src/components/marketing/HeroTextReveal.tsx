'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

interface HeroTextRevealProps {
    children: string;
    as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
    className?: string;
    delay?: number;
    splitBy?: 'words' | 'chars';
    stagger?: number;
    duration?: number;
}

export function HeroTextReveal({
    children,
    as: Tag = 'h1',
    className = '',
    delay = 0,
    splitBy = 'words',
    stagger = 0.05,
    duration = 0.8,
}: HeroTextRevealProps) {
    const containerRef = useRef<HTMLElement>(null);
    const hasAnimated = useRef(false);

    useEffect(() => {
        const container = containerRef.current;
        if (!container || hasAnimated.current) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        hasAnimated.current = true;

        // Split text
        const text = container.textContent || '';
        let elements: Element[];

        if (splitBy === 'chars') {
            const chars = text.split('');
            container.innerHTML = chars
                .map((char) => {
                    if (char === ' ') return ' ';
                    return `<span class="char-wrapper"><span class="char">${char}</span></span>`;
                })
                .join('');
            elements = Array.from(container.querySelectorAll('.char'));
        } else {
            const words = text.split(' ');
            container.innerHTML = words
                .map((word) => `<span class="word-wrapper"><span class="word">${word}</span></span>`)
                .join(' ');
            elements = Array.from(container.querySelectorAll('.word'));
        }

        // Set initial state
        gsap.set(elements, {
            y: '110%',
            opacity: 0,
            rotateX: -10,
        });

        // Animate in
        gsap.to(elements, {
            y: '0%',
            opacity: 1,
            rotateX: 0,
            duration,
            delay,
            stagger,
            ease: 'power3.out',
        });
    }, [children, delay, splitBy, stagger, duration]);

    // @ts-expect-error - Dynamic tag assignment
    return <Tag ref={containerRef} className={className}>{children}</Tag>;
}

// ============================================================================
// ANIMATED HEADLINE - For multi-line headlines with line-by-line animation
// ============================================================================

interface AnimatedHeadlineProps {
    lines: string[];
    className?: string;
    lineClassName?: string;
    delay?: number;
    stagger?: number;
}

export function AnimatedHeadline({
    lines,
    className = '',
    lineClassName = '',
    delay = 0.2,
    stagger = 0.15,
}: AnimatedHeadlineProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const lineElements = container.querySelectorAll('.headline-line');

        gsap.set(lineElements, {
            y: 60,
            opacity: 0,
            clipPath: 'inset(0 0 100% 0)',
        });

        gsap.to(lineElements, {
            y: 0,
            opacity: 1,
            clipPath: 'inset(0 0 0% 0)',
            duration: 1,
            delay,
            stagger,
            ease: 'power3.out',
        });
    }, [delay, stagger]);

    return (
        <div ref={containerRef} className={className}>
            {lines.map((line, index) => (
                <div
                    key={index}
                    className={`headline-line overflow-hidden ${lineClassName}`}
                    style={{ display: 'block' }}
                >
                    {line}
                </div>
            ))}
        </div>
    );
}

// ============================================================================
// TYPEWRITER EFFECT - Premium typing animation
// ============================================================================

interface TypewriterProps {
    text: string;
    className?: string;
    speed?: number;
    delay?: number;
    cursor?: boolean;
}

export function Typewriter({
    text,
    className = '',
    speed = 50,
    delay = 0,
    cursor = true,
}: TypewriterProps) {
    const containerRef = useRef<HTMLSpanElement>(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) {
            container.textContent = text;
            return;
        }

        container.textContent = '';

        const chars = text.split('');
        let currentIndex = 0;

        const timeout = setTimeout(() => {
            const interval = setInterval(() => {
                if (currentIndex < chars.length) {
                    container.textContent += chars[currentIndex];
                    currentIndex++;
                } else {
                    clearInterval(interval);
                }
            }, speed);

            return () => clearInterval(interval);
        }, delay);

        return () => clearTimeout(timeout);
    }, [text, speed, delay]);

    return (
        <span className={className}>
            <span ref={containerRef} />
            {cursor && (
                <span
                    className="inline-block w-[2px] h-[1em] bg-current ml-1 animate-pulse"
                    style={{ animation: 'pulse 1s step-end infinite' }}
                />
            )}
        </span>
    );
}
