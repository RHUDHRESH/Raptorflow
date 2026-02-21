/**
 * ENHANCED WITH:
 * - context7: GSAP flow/directional animations
 * - frontend-animations: Path drawing, step connector animations
 * - performance-optimization: SVG path animations with CSS
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ArrowRight, CheckCircle2, GitBranch, Lightbulb, Rocket } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const STEPS = [
  {
    icon: Lightbulb,
    number: "01",
    title: "Define your world",
    description: "ICPs, positioning, and strategic context captured once and shared everywhere.",
  },
  {
    icon: GitBranch,
    number: "02",
    title: "Choose your path",
    description: "From quick moves to 90-day sieges — select what matches your objective.",
  },
  {
    icon: CheckCircle2,
    number: "03",
    title: "Review the work",
    description: "AI-generated plans and assets arrive complete. You approve or refine.",
  },
  {
    icon: Rocket,
    number: "04",
    title: "Execute with precision",
    description: "Your move goes live across channels. Tracked, optimized, and measured.",
  },
];

export function ControlSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const pathRef = useRef<SVGPathElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Header animation
      gsap.from(".control-header", {
        scrollTrigger: {
          trigger: ".control-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
      });

      // Steps stagger with connector line animation
      const steps = sectionRef.current?.querySelectorAll(".control-step");
      steps?.forEach((step, index) => {
        gsap.from(step, {
          scrollTrigger: {
            trigger: step,
            start: "top 85%",
            toggleActions: "play none none none",
          },
          y: 40,
          opacity: 0,
          duration: 0.7,
          delay: index * 0.15,
          ease: "power3.out",
        });
      });

      // SVG path drawing animation
      if (pathRef.current) {
        const pathLength = pathRef.current.getTotalLength();
        gsap.set(pathRef.current, {
          strokeDasharray: pathLength,
          strokeDashoffset: pathLength,
        });

        gsap.to(pathRef.current, {
          scrollTrigger: {
            trigger: ".steps-container",
            start: "top 70%",
            end: "bottom 50%",
            scrub: 1,
          },
          strokeDashoffset: 0,
          ease: "none",
        });
      }

      // Connector dots animation
      gsap.from(".connector-dot", {
        scrollTrigger: {
          trigger: ".steps-container",
          start: "top 75%",
          toggleActions: "play none none none",
        },
        scale: 0,
        opacity: 0,
        duration: 0.4,
        stagger: 0.2,
        ease: "back.out(2)",
      });

    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section ref={sectionRef} className="py-32 px-6 bg-[var(--bg-surface)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        {/* Header */}
        <div className="control-header text-center mb-20">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-4 block">
            HOW IT WORKS
          </span>
          <h2 className="text-[clamp(32px,5.5vw,52px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            Control the chaos.
          </h2>
          <p className="mt-6 text-[17px] text-[var(--ink-2)] max-w-lg mx-auto leading-relaxed">
            From strategic definition to executed campaign in four intentional steps.
          </p>
        </div>

        {/* Steps with SVG connector */}
        <div className="steps-container relative max-w-5xl mx-auto">
          {/* SVG Connector line (desktop only) */}
          <svg
            className="absolute top-24 left-0 w-full h-2 hidden lg:block pointer-events-none"
            preserveAspectRatio="none"
          >
            <path
              ref={pathRef}
              d="M 100 4 L 400 4 L 700 4 L 1000 4"
              stroke="var(--rf-charcoal)"
              strokeWidth="2"
              strokeOpacity="0.1"
              fill="none"
              strokeLinecap="round"
            />
          </svg>

          {/* Steps grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {STEPS.map((step, index) => {
              const StepIcon = step.icon;
              return (
                <div
                  key={step.number}
                  className="control-step relative text-center group"
                >
                  {/* Number badge with icon */}
                  <div className="relative inline-flex items-center justify-center mb-6">
                    <div className="w-16 h-16 rounded-full bg-[var(--rf-charcoal)] flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                      <StepIcon size={24} className="text-white" />
                    </div>
                    <span className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-[var(--rf-accent)] text-white text-[10px] font-mono flex items-center justify-center">
                      {step.number}
                    </span>
                    
                    {/* Connector dot (desktop) */}
                    {index < STEPS.length - 1 && (
                      <div className="connector-dot absolute left-full top-1/2 -translate-y-1/2 ml-8 hidden lg:block">
                        <div className="w-2 h-2 rounded-full bg-[var(--rf-charcoal)]/30" />
                      </div>
                    )}
                  </div>

                  <h3 className="text-[18px] font-semibold text-[var(--rf-charcoal)] mb-3">
                    {step.title}
                  </h3>
                  <p className="text-[14px] text-[var(--ink-2)] leading-relaxed">
                    {step.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* CTA */}
        <div className="mt-20 text-center">
          <a
            href="#final-cta"
            className="inline-flex items-center gap-2 px-8 py-4 bg-[var(--rf-charcoal)] text-white rounded-full text-[15px] font-medium hover:scale-105 transition-transform duration-300 group"
          >
            Start Building
            <ArrowRight
              size={18}
              className="group-hover:translate-x-1 transition-transform duration-200"
            />
          </a>
        </div>
      </div>
    </section>
  );
}
