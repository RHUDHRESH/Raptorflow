/**
 * ENHANCED WITH:
 * - context7: GSAP rotation and transform animations
 * - frontend-animations: Icon orbit/hover rotation effects
 * - magicui: AvatarCircles-inspired styling
 */

"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Building2, Rocket, Users } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const PERSONAS = [
  {
    icon: Rocket,
    title: "Startups",
    subtitle: "Move fast without breaking things",
    description:
      "Replace your cobbled-together stack with one system. Execute faster than teams ten times your size.",
    features: ["No-tool fatigue", "Reversible decisions", "Startup-friendly pricing"],
  },
  {
    icon: Building2,
    title: "Scale-ups",
    subtitle: "Unify as you grow",
    description:
      "Bring order to the chaos of growth. One system for your expanding marketing team.",
    features: ["Team collaboration", "Brand consistency", "Process scalability"],
  },
  {
    icon: Users,
    title: "Agencies",
    subtitle: "Scale without the sprawl",
    description:
      "Manage multiple clients in one workspace. Better output, fewer tools, happier teams.",
    features: ["Multi-client workspace", "Faster turnaround", "Quality consistency"],
  },
];

export function PersonasSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      // Header animation
      gsap.from(".personas-header", {
        scrollTrigger: {
          trigger: ".personas-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
      });

      // Cards stagger with rotation reveal
      gsap.from(".persona-card", {
        scrollTrigger: {
          trigger: ".personas-grid",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 50,
        opacity: 0,
        rotateY: -15,
        duration: 0.8,
        stagger: 0.12,
        ease: "power3.out",
      });

      // Icon rotation on hover (desktop)
      const mm = gsap.matchMedia();
      mm.add("(min-width: 768px)", () => {
        const cards = sectionRef.current?.querySelectorAll(".persona-card");
        cards?.forEach((card) => {
          const icon = card.querySelector(".persona-icon");
          
          card.addEventListener("mouseenter", () => {
            gsap.to(icon, {
              rotation: 360,
              duration: 0.6,
              ease: "power2.out",
            });
            gsap.to(card, {
              y: -8,
              scale: 1.02,
              duration: 0.3,
              ease: "power2.out",
            });
          });
          
          card.addEventListener("mouseleave", () => {
            gsap.to(icon, {
              rotation: 0,
              duration: 0.4,
              ease: "power2.out",
            });
            gsap.to(card, {
              y: 0,
              scale: 1,
              duration: 0.3,
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
    <section ref={sectionRef} className="py-32 px-6 bg-[#F7F5EF]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        {/* Header */}
        <div className="personas-header text-center mb-20">
          <span className="rf-label text-[#847C82] tracking-[0.15em] mb-4 block">
            WHO IT&rsquo;S FOR
          </span>
          <h2 className="text-[clamp(28px,4vw,44px)] font-bold text-[#2A2529] leading-tight tracking-[-0.02em]">
            Built for operators.
          </h2>
        </div>

        {/* Cards grid */}
        <div 
          className="personas-grid grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto"
          style={{ perspective: "1000px" }}
        >
          {PERSONAS.map((persona) => {
            const Icon = persona.icon;
            return (
              <div
                key={persona.title}
                className="persona-card p-8 rounded-[var(--radius-md)] bg-white border border-[var(--border-1)] hover:border-[var(--rf-charcoal)]/20 transition-all duration-300 will-change-transform"
                style={{ transformStyle: "preserve-3d" }}
              >
                {/* Icon */}
                <div className="persona-icon w-14 h-14 rounded-xl bg-[var(--rf-charcoal)] flex items-center justify-center mb-6">
                  <Icon size={26} className="text-white" />
                </div>

                {/* Content */}
                <h3 className="text-[24px] font-bold text-[var(--rf-charcoal)] mb-2">
                  {persona.title}
                </h3>
                <p className="text-[15px] font-medium text-[var(--rf-charcoal)]/60 mb-4">
                  {persona.subtitle}
                </p>
                <p className="text-[15px] text-[var(--ink-2)] leading-relaxed mb-6">
                  {persona.description}
                </p>

                {/* Features */}
                <ul className="space-y-2">
                  {persona.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-[14px] text-[var(--ink-2)]">
                      <div className="w-1.5 h-1.5 rounded-full bg-[var(--rf-charcoal)]" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
