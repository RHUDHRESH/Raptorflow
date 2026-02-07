'use client';

import { useRef, useEffect, ReactNode, forwardRef } from 'react';
import { gsap } from 'gsap';

interface MagneticButtonProps {
    children: ReactNode;
    className?: string;
    strength?: number;
    as?: 'div' | 'button' | 'span';
    onClick?: () => void;
}

export function MagneticButton({
    children,
    className = '',
    strength = 0.35,
    as: Tag = 'div',
    onClick,
}: MagneticButtonProps) {
    const buttonRef = useRef<any>(null);
    const innerRef = useRef<HTMLSpanElement>(null);

    useEffect(() => {
        const button = buttonRef.current;
        const inner = innerRef.current;
        if (!button || !inner) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const handleMouseMove = (e: MouseEvent) => {
            const rect = button.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            const deltaX = (e.clientX - centerX) * strength;
            const deltaY = (e.clientY - centerY) * strength;

            gsap.to(button, {
                x: deltaX,
                y: deltaY,
                duration: 0.4,
                ease: 'power2.out',
            });

            // Inner content moves slightly more for depth effect
            gsap.to(inner, {
                x: deltaX * 0.15,
                y: deltaY * 0.15,
                duration: 0.4,
                ease: 'power2.out',
            });
        };

        const handleMouseLeave = () => {
            gsap.to(button, {
                x: 0,
                y: 0,
                duration: 0.7,
                ease: 'elastic.out(1, 0.4)',
            });

            gsap.to(inner, {
                x: 0,
                y: 0,
                duration: 0.7,
                ease: 'elastic.out(1, 0.4)',
            });
        };

        button.addEventListener('mousemove', handleMouseMove);
        button.addEventListener('mouseleave', handleMouseLeave);

        return () => {
            button.removeEventListener('mousemove', handleMouseMove);
            button.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, [strength]);

    return (
        <Tag
            ref={buttonRef}
            className={`magnetic-btn ${className}`}
            onClick={onClick}
            style={{ display: 'inline-block' }}
        >
            <span ref={innerRef} className="magnetic-btn-inner">
                {children}
            </span>
        </Tag>
    );
}

MagneticButton.displayName = 'MagneticButton';

// ============================================================================
// HOVER SCALE WRAPPER - Simple scale-on-hover with spring physics
// ============================================================================

interface HoverScaleProps {
    children: ReactNode;
    className?: string;
    scale?: number;
}

export function HoverScale({
    children,
    className = '',
    scale = 1.02
}: HoverScaleProps) {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const handleMouseEnter = () => {
            gsap.to(element, {
                scale,
                duration: 0.4,
                ease: 'power2.out',
            });
        };

        const handleMouseLeave = () => {
            gsap.to(element, {
                scale: 1,
                duration: 0.5,
                ease: 'elastic.out(1, 0.5)',
            });
        };

        element.addEventListener('mouseenter', handleMouseEnter);
        element.addEventListener('mouseleave', handleMouseLeave);

        return () => {
            element.removeEventListener('mouseenter', handleMouseEnter);
            element.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, [scale]);

    return (
        <div ref={elementRef} className={className}>
            {children}
        </div>
    );
}

// ============================================================================
// HOVER LIFT - Card lift effect with shadow
// ============================================================================

interface HoverLiftProps {
    children: ReactNode;
    className?: string;
    liftAmount?: number;
}

export function HoverLift({
    children,
    className = '',
    liftAmount = 8
}: HoverLiftProps) {
    const elementRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const handleMouseEnter = () => {
            gsap.to(element, {
                y: -liftAmount,
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.08)',
                duration: 0.3,
                ease: 'power2.out',
            });
        };

        const handleMouseLeave = () => {
            gsap.to(element, {
                y: 0,
                boxShadow: '0 0 0 rgba(0, 0, 0, 0)',
                duration: 0.4,
                ease: 'power2.out',
            });
        };

        element.addEventListener('mouseenter', handleMouseEnter);
        element.addEventListener('mouseleave', handleMouseLeave);

        return () => {
            element.removeEventListener('mouseenter', handleMouseEnter);
            element.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, [liftAmount]);

    return (
        <div ref={elementRef} className={className}>
            {children}
        </div>
    );
}

// ============================================================================
// RIPPLE BUTTON - Click ripple effect
// ============================================================================

interface RippleButtonProps {
    children: ReactNode;
    className?: string;
    onClick?: () => void;
}

export function RippleButton({
    children,
    className = '',
    onClick
}: RippleButtonProps) {
    const buttonRef = useRef<HTMLButtonElement>(null);

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
        const button = buttonRef.current;
        if (!button) return;

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (!prefersReducedMotion) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.style.cssText = `
        position: absolute;
        left: ${x}px;
        top: ${y}px;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: hsl(var(--foreground) / 0.1);
        transform: translate(-50%, -50%);
        pointer-events: none;
      `;
            button.appendChild(ripple);

            gsap.to(ripple, {
                width: 300,
                height: 300,
                opacity: 0,
                duration: 0.6,
                ease: 'power2.out',
                onComplete: () => ripple.remove(),
            });
        }

        onClick?.();
    };

    return (
        <button
            ref={buttonRef}
            className={`relative overflow-hidden ${className}`}
            onClick={handleClick}
            style={{ position: 'relative' }}
        >
            {children}
        </button>
    );
}
