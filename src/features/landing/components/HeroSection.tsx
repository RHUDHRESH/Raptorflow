/**
 * ENHANCED WITH:
 * - context7: GSAP advanced timeline sequences, matchMedia responsive animations
 * - frontend-animations: Staggered text reveals, parallax, micro-interactions
 * - magicui: Floating orbs, progress line animations
 * - performance-optimization: will-change, GPU acceleration, reduced motion
 * - raptorflow-design-vibe: Charcoal/Ivory only, quiet power aesthetic
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ArrowRight, Play } from "lucide-react";
import { useLandingStore } from "./LandingClient";

export function HeroSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLHeadingElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const artworkRef = useRef<HTMLDivElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Master entrance timeline
      const tl = gsap.timeline({
        delay: 0.3,
        defaults: { ease: "power4.out" },
      });

      // Label entrance
      tl.from(".hero-label", {
        y: 24,
        opacity: 0,
        duration: 0.7,
      });

      tl.from(".hero-word", {
        y: 80,
        opacity: 0,
        duration: 0.9,
        stagger: 0.1,
        ease: "power3.out",
      }, "-=0.35");

      // Accent line draw
      tl.from(".hero-accent-line", {
        scaleX: 0,
        transformOrigin: "left center",
        duration: 0.7,
      }, "-=0.5");

      // Description
      tl.from(".hero-description", {
        y: 30,
        opacity: 0,
        filter: "blur(8px)",
        duration: 0.7,
        clearProps: "filter",
      }, "-=0.4");

      // CTA buttons
      tl.from(".hero-cta", {
        y: 20,
        opacity: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: "back.out(1.5)",
      }, "-=0.3");

      // Artwork parallax entrance
      tl.from(artworkRef.current, {
        y: 80,
        opacity: 0,
        scale: 0.92,
        duration: 1.3,
        ease: "power3.out",
      }, "-=0.6");

      // Artwork panels stagger
      tl.from(".artwork-panel", {
        y: 30,
        opacity: 0,
        duration: 0.55,
        stagger: 0.07,
      }, "-=0.9");

      // Scroll-triggered parallax for artwork
      gsap.to(artworkRef.current, {
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top top",
          end: "bottom top",
          scrub: 1,
        },
        y: 60,
        ease: "none",
      });

      // Ambient orbs animation (continuous)
      gsap.to(".ambient-orb", {
        y: "random(-20, 20)",
        x: "random(-15, 15)",
        duration: "random(3, 5)",
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
        stagger: {
          each: 0.5,
          from: "random",
        },
      });

      // Mouse interaction for CTA buttons (desktop only)
      const mm = gsap.matchMedia();
      mm.add("(min-width: 768px)", () => {
        const primaryCta = ctaRef.current?.querySelector(".cta-primary");
        const secondaryCta = ctaRef.current?.querySelector(".cta-secondary");

        if (primaryCta) {
          primaryCta.addEventListener("mouseenter", () => {
            gsap.to(primaryCta, {
              scale: 1.05,
              duration: 0.25,
              ease: "power2.out",
            });
            gsap.to(".cta-arrow", {
              x: 4,
              duration: 0.2,
            });
          });

          primaryCta.addEventListener("mouseleave", () => {
            gsap.to(primaryCta, {
              scale: 1,
              duration: 0.25,
              ease: "power2.out",
            });
            gsap.to(".cta-arrow", {
              x: 0,
              duration: 0.2,
            });
          });
        }

        if (secondaryCta) {
          secondaryCta.addEventListener("mouseenter", () => {
            gsap.to(secondaryCta, {
              scale: 1.02,
              backgroundColor: "rgba(42, 37, 41, 0.05)",
              duration: 0.2,
            });
          });

          secondaryCta.addEventListener("mouseleave", () => {
            gsap.to(secondaryCta, {
              scale: 1,
              backgroundColor: "transparent",
              duration: 0.2,
            });
          });
        }

        return;
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section
      ref={sectionRef}
      className="relative min-h-screen pt-24 pb-20 px-6 overflow-hidden bg-[var(--bg-canvas)]"
    >
      {/* Ambient orbs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="ambient-orb absolute top-[20%] left-[10%] w-[300px] h-[300px] rounded-full bg-[var(--rf-charcoal)]/[0.02] blur-[80px]" />
        <div className="ambient-orb absolute top-[40%] right-[15%] w-[250px] h-[250px] rounded-full bg-[var(--rf-charcoal)]/[0.03] blur-[60px]" />
        <div className="ambient-orb absolute bottom-[20%] left-[30%] w-[200px] h-[200px] rounded-full bg-[var(--rf-charcoal)]/[0.02] blur-[50px]" />
      </div>

      <div className="max-w-[var(--shell-max-w)] mx-auto relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center min-h-[calc(100vh-6rem)]">
          {/* Left: Content */}
          <div className="pt-12 lg:pt-0">
            {/* Label */}
            <span className="hero-label inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--rf-charcoal)]/5 text-[12px] font-mono tracking-[0.15em] text-[var(--rf-charcoal)]/60 mb-8">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--rf-accent)] animate-pulse" />
              MARKETING OS FOR OPERATORS
            </span>

            {/* Headline */}
            <h1
              ref={headlineRef}
              className="text-[clamp(40px,8vw,72px)] font-bold text-[var(--rf-charcoal)] leading-[0.95] tracking-[-0.03em] mb-6"
            >
              <span className="hero-word inline-block">Stop</span>{" "}
              <span className="hero-word inline-block">juggling</span>{" "}
              <span className="hero-word inline-block">tools.</span>
              <br />
              <span className="hero-word inline-block">Start</span>{" "}
              <span className="hero-word inline-block">winning</span>{" "}
              <span className="hero-word inline-block relative">
                markets
                <span className="hero-accent-line absolute -bottom-2 left-0 w-full h-[6px] bg-[var(--rf-charcoal)]/10 rounded-full" />
              </span>
              <span className="hero-word inline-block text-[var(--rf-accent)]">.</span>
            </h1>

            {/* Description */}
            <p className="hero-description text-[18px] text-[var(--ink-2)] leading-relaxed mb-10 max-w-md">
              One operating system for every marketing move — from quarterly planning to daily execution.
              Built for operators who move with precision.
            </p>

            {/* CTAs */}
            <div ref={ctaRef} className="flex flex-col sm:flex-row gap-4">
              <a
                href="/onboarding"
                className="cta-primary cta-hero inline-flex items-center justify-center gap-2 px-8 py-4 bg-[var(--rf-charcoal)] text-white rounded-[var(--radius-sm)] text-[15px] font-semibold will-change-transform hover:bg-[#3d363b] transition-colors duration-200"
              >
                Start Building for Free
                <ArrowRight size={18} className="cta-arrow" />
              </a>
              <button className="cta-secondary cta-hero inline-flex items-center justify-center gap-2 px-8 py-4 border border-[var(--border-2)] text-[var(--rf-charcoal)] rounded-[var(--radius-sm)] text-[15px] font-medium transition-all duration-200 hover:border-[var(--rf-charcoal)] hover:bg-[var(--bg-surface)]">
                <Play size={16} fill="currentColor" />
                Watch Demo
              </button>
            </div>

            {/* Trust indicators */}
            <div className="mt-12 flex items-center gap-6">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded-full bg-[var(--border-2)] border-2 border-[var(--bg-canvas)]"
                  />
                ))}
              </div>
              <p className="text-[13px] text-[var(--ink-3)]">
                Trusted by 500+ marketing operators
              </p>
            </div>
          </div>

          {/* Right: Artwork */}
          <div
            ref={artworkRef}
            className="relative hidden lg:block will-change-transform"
          >
            <div className="relative aspect-square max-w-[560px] mx-auto">
              {/* Main cockpit mockup */}
              <div className="artwork-panel absolute inset-0 rounded-[var(--radius-lg)] bg-[var(--bg-surface)] border border-[var(--border-1)] overflow-hidden">
                {/* Header */}
                <div className="flex items-center gap-2 px-6 py-4 border-b border-[var(--border-1)]">
                  <div className="w-3 h-3 rounded-full bg-[var(--rf-charcoal)]/10" />
                  <div className="w-3 h-3 rounded-full bg-[var(--rf-charcoal)]/10" />
                  <div className="w-3 h-3 rounded-full bg-[var(--rf-charcoal)]/10" />
                  <div className="ml-auto flex gap-2">
                    <div className="w-20 h-2 rounded bg-[var(--border-2)]" />
                    <div className="w-8 h-2 rounded bg-[var(--border-2)]" />
                  </div>
                </div>

                {/* Content grid */}
                <div className="p-6 grid grid-cols-3 gap-4">
                  {/* Stats cards */}
                  <div className="col-span-2 space-y-4">
                    <div className="h-24 rounded-lg bg-[var(--border-1)] flex items-center px-4">
                      <div className="w-12 h-12 rounded bg-[var(--rf-charcoal)]/10" />
                      <div className="ml-4 space-y-2">
                        <div className="w-24 h-3 rounded bg-[var(--rf-charcoal)]/10" />
                        <div className="w-16 h-2 rounded bg-[var(--border-2)]" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="h-20 rounded-lg bg-[var(--border-1)]" />
                      <div className="h-20 rounded-lg bg-[var(--border-1)]" />
                    </div>
                  </div>

                  {/* Side panel */}
                  <div className="space-y-3">
                    <div className="h-8 rounded bg-[var(--rf-charcoal)]/10" />
                    <div className="h-16 rounded bg-[var(--border-1)]" />
                    <div className="h-16 rounded bg-[var(--border-1)]" />
                  </div>
                </div>

                {/* Bottom bar */}
                <div className="absolute bottom-0 left-0 right-0 px-6 py-4 border-t border-[var(--border-1)] flex justify-between">
                  <div className="flex gap-2">
                    <div className="w-16 h-2 rounded bg-[var(--border-2)]" />
                    <div className="w-12 h-2 rounded bg-[var(--border-2)]" />
                  </div>
                  <div className="w-20 h-6 rounded bg-[var(--rf-charcoal)]" />
                </div>
              </div>

              {/* Floating elements */}
              <div className="artwork-panel absolute -top-4 -right-4 w-32 h-32 rounded-[var(--radius-md)] bg-white border border-[var(--border-1)] p-4">
                <div className="w-full h-3 rounded bg-[var(--border-2)] mb-2" />
                <div className="w-2/3 h-3 rounded bg-[var(--border-2)] mb-4" />
                <div className="flex gap-2">
                  <div className="flex-1 h-12 rounded bg-[var(--border-1)]" />
                  <div className="flex-1 h-12 rounded bg-[var(--rf-charcoal)]/10" />
                </div>
              </div>

              <div className="artwork-panel absolute -bottom-4 -left-4 w-28 h-28 rounded-[var(--radius-md)] bg-[var(--rf-charcoal)] p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="w-6 h-6 rounded-full bg-white/20" />
                  <div className="text-[10px] text-white/60 font-mono">+24%</div>
                </div>
                <div className="w-full h-8 rounded bg-white/10" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
