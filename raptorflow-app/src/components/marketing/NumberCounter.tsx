'use client';

import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register plugin
if (typeof window !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
}

// ============================================================================
// NUMBER COUNTER - Animated counting number
// ============================================================================

interface NumberCounterProps {
    value: number;
    className?: string;
    duration?: number;
    delay?: number;
    prefix?: string;
    suffix?: string;
    decimals?: number;
    triggerOnScroll?: boolean;
}

export function NumberCounter({
    value,
    className = '',
    duration = 2,
    delay = 0,
    prefix = '',
    suffix = '',
    decimals = 0,
    triggerOnScroll = true,
}: NumberCounterProps) {
    const counterRef = useRef<HTMLSpanElement>(null);
    const [displayValue, setDisplayValue] = useState(0);
    const hasAnimated = useRef(false);

    useEffect(() => {
        const counter = counterRef.current;
        if (!counter) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) {
            setDisplayValue(value);
            return;
        }

        const animate = () => {
            if (hasAnimated.current) return;
            hasAnimated.current = true;

            const obj = { value: 0 };
            gsap.to(obj, {
                value,
                duration,
                delay,
                ease: 'power2.out',
                onUpdate: () => {
                    setDisplayValue(Number(obj.value.toFixed(decimals)));
                },
            });
        };

        if (triggerOnScroll) {
            ScrollTrigger.create({
                trigger: counter,
                start: 'top 85%',
                onEnter: animate,
            });
        } else {
            animate();
        }

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === counter) {
                    trigger.kill();
                }
            });
        };
    }, [value, duration, delay, decimals, triggerOnScroll]);

    return (
        <span ref={counterRef} className={className}>
            {prefix}{displayValue}{suffix}
        </span>
    );
}

// ============================================================================
// STAT CARD - Animated stat with counter
// ============================================================================

interface StatCardProps {
    value: number;
    suffix?: string;
    label: string;
    className?: string;
    delay?: number;
}

export function StatCard({
    value,
    suffix = '',
    label,
    className = '',
    delay = 0,
}: StatCardProps) {
    const cardRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const card = cardRef.current;
        if (!card) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        gsap.set(card, { opacity: 0, y: 30 });

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
        <div ref={cardRef} className={`text-center ${className}`}>
            <div className="flex items-baseline justify-center gap-1">
                <NumberCounter
                    value={value}
                    className="font-mono text-4xl lg:text-5xl font-semibold tracking-tight"
                    delay={delay + 0.3}
                />
                <span className="text-lg text-muted-foreground">{suffix}</span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{label}</p>
        </div>
    );
}

// ============================================================================
// PROGRESS BAR ANIMATED - Scroll-triggered progress bar
// ============================================================================

interface AnimatedProgressProps {
    value: number;
    className?: string;
    barClassName?: string;
    duration?: number;
    delay?: number;
}

export function AnimatedProgress({
    value,
    className = '',
    barClassName = '',
    duration = 1.5,
    delay = 0,
}: AnimatedProgressProps) {
    const progressRef = useRef<HTMLDivElement>(null);
    const barRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const progress = progressRef.current;
        const bar = barRef.current;
        if (!progress || !bar) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) {
            gsap.set(bar, { width: `${value}%` });
            return;
        }

        gsap.set(bar, { width: '0%' });

        gsap.to(bar, {
            width: `${value}%`,
            duration,
            delay,
            ease: 'power3.out',
            scrollTrigger: {
                trigger: progress,
                start: 'top 85%',
            },
        });

        return () => {
            ScrollTrigger.getAll().forEach((trigger) => {
                if (trigger.trigger === progress) {
                    trigger.kill();
                }
            });
        };
    }, [value, duration, delay]);

    return (
        <div
            ref={progressRef}
            className={`w-full h-1 bg-muted rounded-full overflow-hidden ${className}`}
        >
            <div
                ref={barRef}
                className={`h-full bg-foreground rounded-full ${barClassName}`}
            />
        </div>
    );
}

// ============================================================================
// COUNTDOWN TIMER - Animated countdown
// ============================================================================

interface CountdownProps {
    targetDate: Date;
    className?: string;
}

export function Countdown({ targetDate, className = '' }: CountdownProps) {
    const [timeLeft, setTimeLeft] = useState({
        days: 0,
        hours: 0,
        minutes: 0,
        seconds: 0,
    });

    useEffect(() => {
        const calculateTimeLeft = () => {
            const difference = targetDate.getTime() - new Date().getTime();

            if (difference > 0) {
                setTimeLeft({
                    days: Math.floor(difference / (1000 * 60 * 60 * 24)),
                    hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
                    minutes: Math.floor((difference / 1000 / 60) % 60),
                    seconds: Math.floor((difference / 1000) % 60),
                });
            }
        };

        calculateTimeLeft();
        const timer = setInterval(calculateTimeLeft, 1000);

        return () => clearInterval(timer);
    }, [targetDate]);

    const timeUnits = [
        { value: timeLeft.days, label: 'Days' },
        { value: timeLeft.hours, label: 'Hours' },
        { value: timeLeft.minutes, label: 'Min' },
        { value: timeLeft.seconds, label: 'Sec' },
    ];

    return (
        <div className={`flex gap-4 ${className}`}>
            {timeUnits.map(({ value, label }) => (
                <div key={label} className="text-center">
                    <div className="font-mono text-3xl font-bold tabular-nums">
                        {String(value).padStart(2, '0')}
                    </div>
                    <div className="text-xs text-muted-foreground uppercase tracking-wide">
                        {label}
                    </div>
                </div>
            ))}
        </div>
    );
}
