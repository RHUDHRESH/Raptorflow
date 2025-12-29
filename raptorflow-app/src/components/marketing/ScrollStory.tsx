'use client';

import { useEffect, useRef, useState, ReactNode } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register plugin
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

// ============================================================================
// SCROLLY STORY - Narrative scroll-linked reveals (Factors.ai style)
// ============================================================================

interface StoryStep {
  id: string;
  headline: string;
  subheadline?: string;
  description?: string;
  visual?: ReactNode;
  highlight?: string;
}

interface ScrollyStoryProps {
  steps: StoryStep[];
  className?: string;
}

export function ScrollyStory({ steps, className = '' }: ScrollyStoryProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    const stepElements = container.querySelectorAll('.story-step');

    stepElements.forEach((step, index) => {
      ScrollTrigger.create({
        trigger: step,
        start: 'top center',
        end: 'bottom center',
        onEnter: () => setActiveStep(index),
        onEnterBack: () => setActiveStep(index),
      });

      // Animate step content on scroll
      const content = step.querySelector('.step-content');
      if (content) {
        gsap.fromTo(
          content,
          { opacity: 0, y: 80, scale: 0.95 },
          {
            opacity: 1,
            y: 0,
            scale: 1,
            duration: 0.8,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: step,
              start: 'top 80%',
              toggleActions: 'play none none reverse',
            },
          }
        );
      }
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    };
  }, [steps]);

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Progress indicator */}
      <div className="fixed left-8 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-3">
        {steps.map((_, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index === activeStep
                ? 'bg-foreground scale-150'
                : index < activeStep
                  ? 'bg-foreground/50'
                  : 'bg-foreground/20'
            }`}
          />
        ))}
      </div>

      {/* Story steps */}
      {steps.map((step, index) => (
        <div
          key={step.id}
          className="story-step min-h-screen flex items-center justify-center py-24"
        >
          <div className="step-content mx-auto max-w-5xl px-6 lg:px-8 text-center">
            {step.highlight && (
              <span className="inline-block px-4 py-1.5 rounded-full text-xs font-medium uppercase tracking-widest bg-foreground/5 text-foreground/60 mb-6">
                {step.highlight}
              </span>
            )}
            <h2 className="font-display text-4xl lg:text-6xl font-medium tracking-tight mb-6">
              {step.headline}
            </h2>
            {step.subheadline && (
              <p className="text-xl lg:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
                {step.subheadline}
              </p>
            )}
            {step.description && (
              <p className="text-lg text-muted-foreground/80 max-w-2xl mx-auto mb-12">
                {step.description}
              </p>
            )}
            {step.visual && <div className="mt-12">{step.visual}</div>}
          </div>
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// HORIZONTAL SCROLL GALLERY - Premium horizontal scroll section
// ============================================================================

interface GalleryItem {
  id: string;
  title: string;
  description: string;
  icon?: ReactNode;
}

interface HorizontalGalleryProps {
  items: GalleryItem[];
  className?: string;
}

export function HorizontalGallery({
  items,
  className = '',
}: HorizontalGalleryProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const track = trackRef.current;
    if (!container || !track) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    const scrollDistance = track.scrollWidth - container.offsetWidth;

    gsap.to(track, {
      x: -scrollDistance,
      ease: 'none',
      scrollTrigger: {
        trigger: container,
        start: 'top top',
        end: `+=${scrollDistance}`,
        pin: true,
        scrub: 1,
        anticipatePin: 1,
      },
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => {
        if (trigger.trigger === container) {
          trigger.kill();
        }
      });
    };
  }, [items]);

  return (
    <div ref={containerRef} className={`overflow-hidden ${className}`}>
      <div
        ref={trackRef}
        className="flex gap-8 will-change-transform"
        style={{ width: `${items.length * 400}px` }}
      >
        {items.map((item, index) => (
          <div
            key={item.id}
            className="w-[350px] flex-shrink-0 bg-card border border-border rounded-2xl p-8"
          >
            {item.icon && <div className="mb-6 text-4xl">{item.icon}</div>}
            <h3 className="font-display text-xl font-semibold mb-3">
              {item.title}
            </h3>
            <p className="text-muted-foreground">{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// SPLIT SCROLL - Content on one side, sticky visual on other
// ============================================================================

interface SplitScrollItem {
  id: string;
  title: string;
  description: string;
}

interface SplitScrollProps {
  items: SplitScrollItem[];
  visual: ReactNode;
  visualSide?: 'left' | 'right';
  className?: string;
}

export function SplitScroll({
  items,
  visual,
  visualSide = 'right',
  className = '',
}: SplitScrollProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const textItems = container.querySelectorAll('.split-text-item');

    textItems.forEach((item, index) => {
      ScrollTrigger.create({
        trigger: item,
        start: 'top center',
        end: 'bottom center',
        onEnter: () => setActiveIndex(index),
        onEnterBack: () => setActiveIndex(index),
      });
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    };
  }, [items]);

  const textContent = (
    <div className="space-y-32 lg:space-y-48 py-24">
      {items.map((item, index) => (
        <div
          key={item.id}
          className={`split-text-item transition-opacity duration-500 ${
            index === activeIndex ? 'opacity-100' : 'opacity-40'
          }`}
        >
          <h3 className="font-display text-3xl lg:text-4xl font-medium mb-4">
            {item.title}
          </h3>
          <p className="text-lg text-muted-foreground leading-relaxed">
            {item.description}
          </p>
        </div>
      ))}
    </div>
  );

  const visualContent = (
    <div className="sticky top-1/4 h-[50vh] flex items-center justify-center">
      {visual}
    </div>
  );

  return (
    <div
      ref={containerRef}
      className={`grid lg:grid-cols-2 gap-16 lg:gap-24 ${className}`}
    >
      {visualSide === 'left' ? (
        <>
          <div className="hidden lg:block">{visualContent}</div>
          {textContent}
        </>
      ) : (
        <>
          {textContent}
          <div className="hidden lg:block">{visualContent}</div>
        </>
      )}
    </div>
  );
}

// ============================================================================
// MARQUEE - Infinite horizontal scroll
// ============================================================================

interface MarqueeProps {
  children: ReactNode;
  speed?: number;
  pauseOnHover?: boolean;
  direction?: 'left' | 'right';
  className?: string;
}

export function Marquee({
  children,
  speed = 30,
  pauseOnHover = true,
  direction = 'left',
  className = '',
}: MarqueeProps) {
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    const content = track.firstElementChild as HTMLElement;
    if (!content) return;

    const contentWidth = content.offsetWidth;
    const duration = contentWidth / speed;

    gsap.to(track, {
      x: direction === 'left' ? -contentWidth : contentWidth,
      duration,
      ease: 'none',
      repeat: -1,
    });
  }, [speed, direction]);

  return (
    <div
      className={`overflow-hidden ${className}`}
      style={{
        maskImage:
          'linear-gradient(to right, transparent, black 10%, black 90%, transparent)',
        WebkitMaskImage:
          'linear-gradient(to right, transparent, black 10%, black 90%, transparent)',
      }}
    >
      <div
        ref={trackRef}
        className={`flex gap-8 ${pauseOnHover ? 'hover:[animation-play-state:paused]' : ''}`}
        style={{ width: 'max-content' }}
      >
        <div className="flex gap-8 shrink-0">{children}</div>
        <div className="flex gap-8 shrink-0">{children}</div>
        <div className="flex gap-8 shrink-0">{children}</div>
      </div>
    </div>
  );
}

// ============================================================================
// DRAMATIC REVEAL - Full-screen scroll-triggered reveal
// ============================================================================

interface DramaticRevealProps {
  children: ReactNode;
  className?: string;
  backgroundColor?: string;
}

export function DramaticReveal({
  children,
  className = '',
  backgroundColor = 'hsl(var(--background))',
}: DramaticRevealProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    const content = contentRef.current;
    if (!container || !content) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) return;

    // Initial state - content is scaled down and blurred
    gsap.set(content, {
      scale: 0.8,
      opacity: 0,
      filter: 'blur(20px)',
      y: 100,
    });

    // Animate on scroll
    gsap.to(content, {
      scale: 1,
      opacity: 1,
      filter: 'blur(0px)',
      y: 0,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: container,
        start: 'top 80%',
        end: 'top 20%',
        scrub: 1,
      },
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => {
        if (trigger.trigger === container) {
          trigger.kill();
        }
      });
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={`relative min-h-screen flex items-center justify-center ${className}`}
      style={{ backgroundColor }}
    >
      <div ref={contentRef} className="w-full">
        {children}
      </div>
    </div>
  );
}

// ============================================================================
// TEXT SCRAMBLE - Matrix-style text scramble effect
// ============================================================================

interface TextScrambleProps {
  text: string;
  className?: string;
  speed?: number;
  trigger?: 'scroll' | 'mount';
}

export function TextScramble({
  text,
  className = '',
  speed = 30,
  trigger = 'scroll',
}: TextScrambleProps) {
  const elementRef = useRef<HTMLSpanElement>(null);
  const [displayText, setDisplayText] = useState(text);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;
    if (prefersReducedMotion) {
      setDisplayText(text);
      return;
    }

    const chars =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let frame = 0;

    const scramble = () => {
      const progress = frame / (text.length * 2);

      const scrambledText = text
        .split('')
        .map((char, index) => {
          if (char === ' ') return ' ';
          if (index < frame) return text[index];
          return chars[Math.floor(Math.random() * chars.length)];
        })
        .join('');

      setDisplayText(scrambledText);

      if (frame < text.length * 2) {
        frame++;
        setTimeout(scramble, speed);
      }
    };

    if (trigger === 'mount') {
      scramble();
    } else {
      ScrollTrigger.create({
        trigger: element,
        start: 'top 80%',
        onEnter: scramble,
        once: true,
      });
    }

    return () => {
      ScrollTrigger.getAll().forEach((t) => {
        if (t.trigger === element) {
          t.kill();
        }
      });
    };
  }, [text, speed, trigger]);

  return (
    <span ref={elementRef} className={`font-mono ${className}`}>
      {displayText}
    </span>
  );
}

// ============================================================================
// GLITCH TEXT - Glitch effect on hover or scroll
// ============================================================================

interface GlitchTextProps {
  text: string;
  className?: string;
}

export function GlitchText({ text, className = '' }: GlitchTextProps) {
  return (
    <span className={`relative inline-block ${className}`}>
      <span className="relative z-10">{text}</span>
      <span
        className="absolute inset-0 text-foreground/30 z-0"
        style={{
          clipPath: 'polygon(0 0, 100% 0, 100% 45%, 0 45%)',
          transform: 'translate(-2px, -1px)',
        }}
        aria-hidden="true"
      >
        {text}
      </span>
      <span
        className="absolute inset-0 text-foreground/30 z-0"
        style={{
          clipPath: 'polygon(0 55%, 100% 55%, 100% 100%, 0 100%)',
          transform: 'translate(2px, 1px)',
        }}
        aria-hidden="true"
      >
        {text}
      </span>
    </span>
  );
}
