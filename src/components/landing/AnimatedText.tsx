"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

interface AnimatedTextProps {
  children: string;
  as?: "h1" | "h2" | "h3" | "p" | "span";
  className?: string;
  type?: "words" | "lines" | "chars";
  stagger?: number;
  duration?: number;
  delay?: number;
  blur?: boolean;
}

/**
 * AnimatedText - Sophisticated text reveal
 * 
 * Complex but subtle. Text reveals with calculated timing,
 * creating a wave-like effect that's felt more than seen.
 */
export function AnimatedText({
  children,
  as: Component = "span",
  className = "",
  type = "words",
  stagger = 0.03,
  duration = 0.6,
  delay = 0,
  blur = false,
}: AnimatedTextProps) {
  const containerRef = useRef<HTMLElement>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (!containerRef.current || hasAnimated.current) return;

    const el = containerRef.current;
    const text = children;

    // Split text
    let elements: string[] = [];
    if (type === "words") {
      elements = text.split(" ");
      el.innerHTML = elements
        .map((word) => `<span class="inline-block overflow-hidden"><span class="inline-block reveal-target">${word}</span></span>`)
        .join(" ");
    } else if (type === "chars") {
      elements = text.split("");
      el.innerHTML = elements
        .map((char) => `<span class="inline-block overflow-hidden"><span class="inline-block reveal-target">${char === " " ? "&nbsp;" : char}</span></span>`)
        .join("");
    }

    const targets = el.querySelectorAll(".reveal-target");

    // Set initial state
    gsap.set(targets, {
      y: type === "chars" ? 8 : 16,
      opacity: 0,
      filter: blur ? "blur(4px)" : "none",
    });

    // Animate
    const trigger = ScrollTrigger.create({
      trigger: el,
      start: "top 85%",
      onEnter: () => {
        hasAnimated.current = true;
        gsap.to(targets, {
          y: 0,
          opacity: 1,
          filter: "blur(0px)",
          duration,
          stagger,
          delay,
          ease: "power2.out",
        });
      },
      once: true,
    });

    return () => {
      trigger.kill();
    };
  }, [children, type, stagger, duration, delay, blur]);

  return (
    <Component ref={containerRef as any} className={className}>
      {children}
    </Component>
  );
}

/**
 * RevealOnScroll - Simple fade up with elegance
 */
export function RevealOnScroll({
  children,
  className = "",
  delay = 0,
  y = 30,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  y?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const el = ref.current;

    gsap.set(el, { y, opacity: 0 });

    const trigger = ScrollTrigger.create({
      trigger: el,
      start: "top 85%",
      onEnter: () => {
        gsap.to(el, {
          y: 0,
          opacity: 1,
          duration: 0.8,
          delay,
          ease: "power2.out",
        });
      },
      once: true,
    });

    return () => trigger.kill();
  }, [delay, y]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}

/**
 * StaggerContainer - Children reveal in sequence
 */
export function StaggerContainer({
  children,
  className = "",
  childClassName = "stagger-child",
  stagger = 0.1,
}: {
  children: React.ReactNode;
  className?: string;
  childClassName?: string;
  stagger?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const children = ref.current.querySelectorAll(`.${childClassName}`);

    gsap.set(children, { y: 20, opacity: 0 });

    const trigger = ScrollTrigger.create({
      trigger: ref.current,
      start: "top 80%",
      onEnter: () => {
        gsap.to(children, {
          y: 0,
          opacity: 1,
          duration: 0.6,
          stagger,
          ease: "power2.out",
        });
      },
      once: true,
    });

    return () => trigger.kill();
  }, [childClassName, stagger]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}

/**
 * ParallaxLayer - Subtle depth on scroll
 */
export function ParallaxLayer({
  children,
  className = "",
  speed = 0.3,
}: {
  children: React.ReactNode;
  className?: string;
  speed?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    gsap.to(ref.current, {
      yPercent: speed * 100,
      ease: "none",
      scrollTrigger: {
        trigger: ref.current,
        start: "top bottom",
        end: "bottom top",
        scrub: true,
      },
    });
  }, [speed]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}

/**
 * LineReveal - SVG line that draws on scroll
 */
export function LineReveal({
  className = "",
  color = "var(--border-1)",
}: {
  className?: string;
  color?: string;
}) {
  const ref = useRef<SVGLineElement>(null);

  useEffect(() => {
    if (!ref.current) return;

    const line = ref.current;
    const length = 100;

    gsap.set(line, {
      strokeDasharray: length,
      strokeDashoffset: length,
    });

    const trigger = ScrollTrigger.create({
      trigger: line,
      start: "top 80%",
      onEnter: () => {
        gsap.to(line, {
          strokeDashoffset: 0,
          duration: 1.2,
          ease: "power2.inOut",
        });
      },
      once: true,
    });

    return () => trigger.kill();
  }, []);

  return (
    <svg className={className} viewBox="0 0 100 2" preserveAspectRatio="none">
      <line
        ref={ref}
        x1="0"
        y1="1"
        x2="100"
        y2="1"
        stroke={color}
        strokeWidth="2"
      />
    </svg>
  );
}
