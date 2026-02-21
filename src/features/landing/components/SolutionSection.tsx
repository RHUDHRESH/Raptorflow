/**
 * ENHANCED WITH:
 * - context7: GSAP timeline sequences for complex animations
 * - frontend-animations: 3D card flip, morphing reveals
 * - performance-optimization: GPU-accelerated transforms
 * - raptorflow-design-vibe: High contrast, intentional hierarchy
 */

"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLandingStore } from "./LandingClient";

const FEATURES = [
  {
    title: "Company Memory",
    description:
      "Your positioning, ICPs, and past wins — all accessible to every AI module. No repetition. No drift.",
  },
  {
    title: "Active Components",
    description:
      "Charts, tables, calculators, and mockups that actually work and edit themselves. Not static images.",
  },
  {
    title: "Unified Intelligence",
    description:
      "CRM, analytics, and planning in one cockpit. The left hand finally sees what the right is doing.",
  },
  {
    title: "Agentic Execution",
    description:
      "You approve the moves. AI executes the details — scheduling, content, campaigns — in context.",
  },
];

export function SolutionSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Header animation
      const headerTl = gsap.timeline({
        scrollTrigger: {
          trigger: ".solution-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
      });

      headerTl
        .from(".solution-label", {
          y: 20,
          opacity: 0,
          duration: 0.5,
          ease: "power2.out",
        })
        .from(".solution-title span", {
          y: 50,
          opacity: 0,
          duration: 0.8,
          stagger: 0.08,
          ease: "power3.out",
        }, "-=0.3")
        .from(".solution-description", {
          y: 20,
          opacity: 0,
          filter: "blur(8px)",
          duration: 0.6,
          ease: "power2.out",
          clearProps: "filter",
        }, "-=0.4");

      // Feature items stagger
      gsap.from(".feature-item", {
        scrollTrigger: {
          trigger: ".features-list",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        x: -30,
        opacity: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: "power3.out",
      });

      // Visual card entrance with 3D
      gsap.from(".solution-visual", {
        scrollTrigger: {
          trigger: ".solution-visual",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 60,
        rotateX: 10,
        opacity: 0,
        duration: 1,
        ease: "power3.out",
      });

      // Floating decorative elements
      gsap.to(".visual-glow", {
        opacity: 0.6,
        scale: 1.1,
        duration: 2,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
      });

    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  // Handle feature selection animation
  const handleFeatureSelect = (index: number) => {
    if (index === activeIndex) return;
    
    setActiveIndex(index);
    
    // Visual feedback animation
    const visual = sectionRef.current?.querySelector(".solution-visual");
    if (visual) {
      gsap.to(visual, {
        scale: 0.98,
        duration: 0.15,
        ease: "power2.in",
        yoyo: true,
        repeat: 1,
      });
    }
  };

  return (
    <section ref={sectionRef} className="py-32 px-6 bg-[var(--bg-canvas)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        {/* Header */}
        <div className="solution-header text-center mb-20">
          <span className="solution-label rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-4 block">
            THE SOLUTION
          </span>
          <h2 className="solution-title text-[clamp(32px,5.5vw,52px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            {"One operating system.".split(" ").map((word, i) => (
              <span key={i} className="inline-block mr-[0.3em]">{word}</span>
            ))}
            <br />
            {"Every marketing move.".split(" ").map((word, i) => (
              <span key={i} className="inline-block mr-[0.3em] text-[var(--rf-charcoal)]/50">{word}</span>
            ))}
          </h2>
          <p className="solution-description mt-6 text-[17px] text-[var(--ink-2)] max-w-xl mx-auto leading-relaxed">
            RaptorFlow replaces your entire marketing stack with a single system built for operators who need precision and scale.
          </p>
        </div>

        {/* Content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start max-w-6xl mx-auto">
          {/* Features list with interactive selection */}
          <div className="features-list space-y-4">
            {FEATURES.map((feature, index) => (
              <div
                key={feature.title}
                className={`feature-item group p-6 rounded-[var(--radius-md)] border cursor-pointer transition-all duration-300 ${
                  activeIndex === index
                    ? "bg-[var(--rf-charcoal)] border-[var(--rf-charcoal)]"
                    : "bg-white border-transparent hover:border-[var(--border-2)]"
                }`}
                onClick={() => handleFeatureSelect(index)}
                style={{ transformStyle: "preserve-3d" }}
              >
                <div className="flex items-start gap-4">
                  <span
                    className={`text-[12px] font-mono tracking-wider transition-colors duration-300 ${
                      activeIndex === index ? "text-white/40" : "text-[var(--ink-3)]"
                    }`}
                  >
                    0{index + 1}
                  </span>
                  <div className="flex-1">
                    <h3
                      className={`text-[18px] font-semibold mb-2 transition-colors duration-300 ${
                        activeIndex === index ? "text-white" : "text-[var(--rf-charcoal)]"
                      }`}
                    >
                      {feature.title}
                    </h3>
                    <p
                      className={`text-[14px] leading-relaxed transition-colors duration-300 ${
                        activeIndex === index ? "text-white/60" : "text-[var(--ink-2)]"
                      }`}
                    >
                      {feature.description}
                    </p>
                  </div>
                  <div
                    className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
                      activeIndex === index
                        ? "bg-white scale-100"
                        : "bg-[var(--border-2)] scale-0 group-hover:scale-100"
                    }`}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Visual mockup with glow */}
          <div 
            className="solution-visual relative lg:sticky lg:top-32"
            style={{ perspective: "1000px" }}
          >
            <div className="relative rounded-[var(--radius-lg)] border border-[var(--border-1)] bg-[var(--bg-surface)] p-8 will-change-transform">
              <div className="visual-glow absolute -inset-1 bg-gradient-to-r from-[var(--rf-charcoal)]/5 via-transparent to-[var(--rf-charcoal)]/5 rounded-[var(--radius-lg)] blur-xl opacity-0 pointer-events-none" />
              
              <div className="relative">
                <div className="flex items-center gap-2 mb-6 pb-6 border-b border-[var(--border-1)]">
                  <div className="w-3 h-3 rounded-full bg-[var(--rf-charcoal)]/10" />
                  <div className="w-3 h-3 rounded-full bg-[var(--rf-charcoal)]/10" />
                  <div className="w-3 h-3 rounded-full bg-[var(--rf-charcoal)]/10" />
                  <div className="ml-4 flex-1 h-2 rounded bg-[var(--border-2)]" />
                </div>

                <div className="space-y-4">
                  <div className="flex gap-4">
                    <div className="w-1/3 h-24 rounded-lg bg-[var(--border-1)]" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 rounded bg-[var(--border-2)] w-3/4" />
                      <div className="h-4 rounded bg-[var(--border-2)] w-1/2" />
                      <div className="h-4 rounded bg-[var(--border-2)] w-2/3" />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="h-20 rounded-lg bg-[var(--border-1)]" />
                    <div className="h-20 rounded-lg bg-[var(--border-1)]" />
                    <div className="h-20 rounded-lg bg-[var(--border-1)]" />
                  </div>
                </div>

                <div className="absolute -right-2 top-1/2 -translate-y-1/2 translate-x-full hidden lg:block">
                  <div className="flex items-center gap-2">
                    <div className="h-px w-8 bg-[var(--rf-charcoal)]/20" />
                    <span className="text-[11px] font-mono text-[var(--ink-3)] whitespace-nowrap">
                      FEATURE 0{activeIndex + 1}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
