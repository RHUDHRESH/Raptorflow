/**
 * ENHANCED WITH:
 * - context7: GSAP 3D perspective transforms
 * - frontend-animations: Card tilt, hover depth effects
 * - performance-optimization: transform-only animations
 * - raptorflow-design-vibe: Clean, confident presentation
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Heart, Layers, Shield, Zap } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const PRINCIPLES = [
  {
    icon: Shield,
    title: "You remain in control",
    description: "AI suggests. You decide. Every move requires your approval.",
    color: "bg-[var(--rf-charcoal)]/10",
  },
  {
    icon: Layers,
    title: "Context is king",
    description: "Your company context flows through every module. No silos. No repetition.",
    color: "bg-[var(--rf-charcoal)]/10",
  },
  {
    icon: Zap,
    title: "Speed without sacrifice",
    description: "90-day sieges planned in hours, not weeks. Quality preserved, time reclaimed.",
    color: "bg-[var(--rf-charcoal)]/10",
  },
  {
    icon: Heart,
    title: "Built for operators",
    description: "Not consultants. Not agencies. For the people actually doing the work.",
    color: "bg-[var(--rf-charcoal)]/10",
  },
];

export function PrinciplesSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Header entrance
      gsap.from(".principles-header", {
        scrollTrigger: {
          trigger: ".principles-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
      });

      // Cards stagger with 3D tilt
      gsap.from(".principle-card", {
        scrollTrigger: {
          trigger: ".principles-grid",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 60,
        opacity: 0,
        rotateX: 15,
        duration: 0.8,
        stagger: 0.1,
        ease: "power3.out",
      });

      // Desktop hover effects
      const mm = gsap.matchMedia();
      mm.add("(min-width: 768px)", () => {
        const cards = sectionRef.current?.querySelectorAll(".principle-card");
        cards?.forEach((card) => {
          card.addEventListener("mouseenter", () => {
            gsap.to(card, {
              y: -12,
              rotateX: 5,
              rotateY: 5,
              duration: 0.35,
              ease: "power2.out",
            });
          });
          
          card.addEventListener("mouseleave", () => {
            gsap.to(card, {
              y: 0,
              rotateX: 0,
              rotateY: 0,
              duration: 0.35,
              ease: "power2.out",
            });
          });
        });
        
        return;
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section ref={sectionRef} className="py-32 px-6 bg-[var(--bg-canvas)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        {/* Header */}
        <div className="principles-header text-center mb-20">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-4 block">
            OUR PRINCIPLES
          </span>
          <h2 className="text-[clamp(28px,4vw,44px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            Built on conviction.
          </h2>
        </div>

        {/* Cards grid with 3D perspective */}
        <div 
          className="principles-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto"
          style={{ perspective: "1200px" }}
        >
          {PRINCIPLES.map((principle) => {
            const Icon = principle.icon;
            return (
              <div
                key={principle.title}
                className="principle-card group p-6 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)] hover:border-[var(--rf-charcoal)]/20 transition-colors duration-300 will-change-transform"
                style={{ transformStyle: "preserve-3d" }}
              >
                {/* Icon */}
                <div
                  className={`w-12 h-12 rounded-xl ${principle.color} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}
                >
                  <Icon size={22} className="text-[var(--rf-charcoal)]" />
                </div>

                {/* Content */}
                <h3 className="text-[17px] font-semibold text-[var(--rf-charcoal)] mb-3">
                  {principle.title}
                </h3>
                <p className="text-[14px] text-[var(--ink-2)] leading-relaxed">
                  {principle.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
