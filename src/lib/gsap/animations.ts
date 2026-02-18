"use client";

import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";

// Register plugins
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, SplitText);
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEXT REVEALS - Sophisticated, nuanced
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Reveal text by lines with stagger
 * Each line fades up with a slight delay
 */
export function revealTextByLines(element: string | Element, options?: {
  y?: number;
  duration?: number;
  stagger?: number;
  ease?: string;
}) {
  const { y = 24, duration = 0.8, stagger = 0.08, ease = "power2.out" } = options || {};

  const el = typeof element === "string" ? document.querySelector(element) : element;
  if (!el) return;

  // Split into lines
  const split = new SplitText(el, { type: "lines", linesClass: "line-child" });

  gsap.fromTo(
    split.lines,
    { y, opacity: 0 },
    { y: 0, opacity: 1, duration, stagger, ease }
  );

  return split;
}

/**
 * Reveal text by words with subtle stagger
 * Creates a "wave" effect across words
 */
export function revealTextByWords(element: string | Element, options?: {
  y?: number;
  duration?: number;
  stagger?: number;
  ease?: string;
}) {
  const { y = 12, duration = 0.6, stagger = 0.02, ease = "power2.out" } = options || {};

  const el = typeof element === "string" ? document.querySelector(element) : element;
  if (!el) return;

  const split = new SplitText(el, { type: "words", wordsClass: "word-child" });

  gsap.fromTo(
    split.words,
    { y, opacity: 0 },
    { y: 0, opacity: 1, duration, stagger, ease }
  );

  return split;
}

/**
 * Reveal text by characters - very subtle
 * Used for headlines, small amounts of text
 */
export function revealTextByChars(element: string | Element, options?: {
  y?: number;
  duration?: number;
  stagger?: number;
}) {
  const { y = 8, duration = 0.4, stagger = 0.01 } = options || {};

  const el = typeof element === "string" ? document.querySelector(element) : element;
  if (!el) return;

  const split = new SplitText(el, { type: "chars", charsClass: "char-child" });

  gsap.fromTo(
    split.chars,
    { y, opacity: 0 },
    { y: 0, opacity: 1, duration, stagger, ease: "power2.out" }
  );

  return split;
}

/**
 * Blur to sharp reveal
 * Text starts blurry and comes into focus
 */
export function blurReveal(element: string | Element, options?: {
  duration?: number;
  delay?: number;
}) {
  const { duration = 0.8, delay = 0 } = options || {};

  const el = typeof element === "string" ? document.querySelector(element) : element;
  if (!el) return;

  gsap.fromTo(
    el,
    { filter: "blur(8px)", opacity: 0 },
    { filter: "blur(0px)", opacity: 1, duration, delay, ease: "power2.out" }
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCROLL-TRIGGERED REVEALS - Elegant, restrained
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Fade up on scroll - the classic, done right
 */
export function fadeUpOnScroll(element: string | Element, options?: {
  y?: number;
  duration?: number;
  start?: string;
  markers?: boolean;
}) {
  const { y = 40, duration = 0.8, start = "top 85%", markers = false } = options || {};

  const el = typeof element === "string" ? document.querySelector(element) : element;
  if (!el) return;

  gsap.fromTo(
    el,
    { y, opacity: 0 },
    {
      y: 0,
      opacity: 1,
      duration,
      ease: "power2.out",
      scrollTrigger: {
        trigger: el,
        start,
        markers,
        toggleActions: "play none none reverse",
      },
    }
  );
}

/**
 * Staggered children reveal
 * Parent triggers, children animate in sequence
 */
export function staggerChildren(parent: string | Element, childSelector: string, options?: {
  y?: number;
  duration?: number;
  stagger?: number;
  start?: string;
}) {
  const { y = 24, duration = 0.6, stagger = 0.1, start = "top 80%" } = options || {};

  const parentEl = typeof parent === "string" ? document.querySelector(parent) : parent;
  if (!parentEl) return;

  const children = parentEl.querySelectorAll(childSelector);

  gsap.fromTo(
    children,
    { y, opacity: 0 },
    {
      y: 0,
      opacity: 1,
      duration,
      stagger,
      ease: "power2.out",
      scrollTrigger: {
        trigger: parentEl,
        start,
        toggleActions: "play none none reverse",
      },
    }
  );
}

/**
 * Horizontal reveal - slide in from side
 */
export function slideIn(element: string | Element, options?: {
  x?: number;
  duration?: number;
  start?: string;
}) {
  const { x = -60, duration = 0.8, start = "top 85%" } = options || {};

  const el = typeof element === "string" ? document.querySelector(element) : element;
  if (!el) return;

  gsap.fromTo(
    el,
    { x, opacity: 0 },
    {
      x: 0,
      opacity: 1,
      duration,
      ease: "power2.out",
      scrollTrigger: {
        trigger: el,
        start,
        toggleActions: "play none none reverse",
      },
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// PARALLAX & SCROLL EFFECTS - Subtle depth
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Subtle parallax on scroll
 * Element moves slower than scroll
 */
export function subtleParallax(element: string | Element, speed: number = 0.3) {
  const el = typeof element === "string" ? document.querySelector(element) : element;
  if (!el) return;

  gsap.to(el, {
    yPercent: speed * 100,
    ease: "none",
    scrollTrigger: {
      trigger: el,
      start: "top bottom",
      end: "bottom top",
      scrub: true,
    },
  });
}

/**
 * Scale on scroll - element grows as it enters viewport
 */
export function scaleOnScroll(element: string | Element, options?: {
  startScale?: number;
  endScale?: number;
  start?: string;
  end?: string;
}) {
  const { startScale = 0.95, endScale = 1, start = "top 90%", end = "center center" } = options || {};

  const el = typeof element === "string" ? document.querySelector(element) : element;
  if (!el) return;

  gsap.fromTo(
    el,
    { scale: startScale },
    {
      scale: endScale,
      ease: "none",
      scrollTrigger: {
        trigger: el,
        start,
        end,
        scrub: true,
      },
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SVG & PATH ANIMATIONS - Refined line work
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Draw SVG path - line drawing effect
 */
export function drawPath(path: string | SVGPathElement, options?: {
  duration?: number;
  ease?: string;
  delay?: number;
}) {
  const { duration = 1.5, ease = "power2.inOut", delay = 0 } = options || {};

  const pathEl = typeof path === "string" ? document.querySelector(path) : path;
  if (!pathEl) return;

  const length = (pathEl as SVGPathElement).getTotalLength();

  gsap.set(pathEl, {
    strokeDasharray: length,
    strokeDashoffset: length,
  });

  gsap.to(pathEl, {
    strokeDashoffset: 0,
    duration,
    delay,
    ease,
  });
}

/**
 * Reveal SVG by groups
 */
export function revealSVG(svg: string | SVGElement, options?: {
  stagger?: number;
  duration?: number;
}) {
  const { stagger = 0.1, duration = 0.6 } = options || {};

  const svgEl = typeof svg === "string" ? document.querySelector(svg) : svg;
  if (!svgEl) return;

  const groups = svgEl.querySelectorAll("g, path, circle, rect");

  gsap.fromTo(
    groups,
    { opacity: 0, y: 10 },
    { opacity: 1, y: 0, duration, stagger, ease: "power2.out" }
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MICRO-INTERACTIONS - Thoughtful details
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Magnetic button effect - subtle pull toward cursor
 */
export function magneticButton(element: HTMLElement, options?: {
  strength?: number;
  ease?: number;
}) {
  const { strength = 0.3, ease = 0.1 } = options || {};

  let boundingRect = element.getBoundingClientRect();

  const onMouseMove = (e: MouseEvent) => {
    boundingRect = element.getBoundingClientRect();
    const x = e.clientX - boundingRect.left - boundingRect.width / 2;
    const y = e.clientY - boundingRect.top - boundingRect.height / 2;

    gsap.to(element, {
      x: x * strength,
      y: y * strength,
      duration: ease,
      ease: "power2.out",
    });
  };

  const onMouseLeave = () => {
    gsap.to(element, {
      x: 0,
      y: 0,
      duration: 0.4,
      ease: "elastic.out(1, 0.3)",
    });
  };

  element.addEventListener("mousemove", onMouseMove);
  element.addEventListener("mouseleave", onMouseLeave);

  return () => {
    element.removeEventListener("mousemove", onMouseMove);
    element.removeEventListener("mouseleave", onMouseLeave);
  };
}

/**
 * Underline draw on hover
 * Line draws from left to right
 */
export function underlineDraw(element: HTMLElement) {
  const line = document.createElement("span");
  line.className = "absolute bottom-0 left-0 h-px bg-current";
  line.style.width = "0%";
  element.style.position = "relative";
  element.appendChild(line);

  element.addEventListener("mouseenter", () => {
    gsap.to(line, { width: "100%", duration: 0.3, ease: "power2.out" });
  });

  element.addEventListener("mouseleave", () => {
    gsap.to(line, { width: "0%", duration: 0.3, ease: "power2.out" });
  });
}

/**
 * Counter animation with easing
 * Numbers count up with proper easing
 */
export function animateCounter(
  element: HTMLElement,
  endValue: number,
  options?: {
    duration?: number;
    prefix?: string;
    suffix?: string;
  }
) {
  const { duration = 2, prefix = "", suffix = "" } = options || {};

  const obj = { value: 0 };

  gsap.to(obj, {
    value: endValue,
    duration,
    ease: "power2.out",
    onUpdate: () => {
      element.textContent = prefix + Math.round(obj.value) + suffix;
    },
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// PAGE TRANSITIONS - Smooth, unobtrusive
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Page entrance - content fades up with stagger
 */
export function pageEntrance(container: HTMLElement) {
  const tl = gsap.timeline();

  tl.fromTo(
    container.querySelectorAll("[data-animate]"),
    { y: 30, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.6, stagger: 0.1, ease: "power2.out" }
  );

  return tl;
}

/**
 * Smooth scroll to element
 */
export function smoothScrollTo(target: string | Element, options?: {
  offset?: number;
  duration?: number;
}) {
  const { offset = 0, duration = 1 } = options || {};

  const el = typeof target === "string" ? document.querySelector(target) : target;
  if (!el) return;

  const targetY = el.getBoundingClientRect().top + window.scrollY - offset;

  gsap.to(window, {
    scrollTo: { y: targetY },
    duration,
    ease: "power2.inOut",
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// CLEANUP UTILS
// ═══════════════════════════════════════════════════════════════════════════════

export function killAllAnimations() {
  gsap.killTweensOf("*");
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
}

export function cleanupScrollTriggers() {
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
}
