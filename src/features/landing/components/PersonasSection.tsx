"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Rocket, Users, Building2 } from "lucide-react";
import { useLandingStore } from "./LandingClient";

const PERSONAS = [
  {
    Icon: Rocket,
    category: "Solo Operator",
    name: "The One-Person Army",
    subtitle: "Move faster than teams 10× your size",
    description:
      "Replace your cobbled-together stack with one system. Execute campaigns that would take a full team — from your laptop, alone, at speed.",
    features: [
      "Full BCM in 21 guided steps",
      "Moves sized for 1-person execution",
      "AI that writes in your voice",
      "No tool-switching required",
    ],
    href: "#",
  },
  {
    Icon: Users,
    category: "Growth Team",
    name: "The Scaling Team",
    subtitle: "Bring order to the chaos of growth",
    description:
      "One system for your expanding team. Brand consistency across every member, every channel, every campaign — without the weekly alignment meetings.",
    features: [
      "Shared BCM across the team",
      "Role-based campaign access",
      "Unified campaign calendar",
      "Performance that compounds",
    ],
    href: "#",
  },
  {
    Icon: Building2,
    category: "Agency",
    name: "The Modern Agency",
    subtitle: "Scale output without scaling headcount",
    description:
      "Manage multiple clients in one workspace. Faster turnaround, consistent quality, and an AI layer that never forgets a brand voice.",
    features: [
      "Multi-client workspace isolation",
      "Per-client BCM profiles",
      "Client-ready deliverables",
      "Agency-tier AI credits",
    ],
    href: "#",
  },
];

export function PersonasSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      gsap.from(".personas-header > *", {
        scrollTrigger: {
          trigger: ".personas-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.7,
        stagger: 0.1,
        ease: "power3.out",
      });

      gsap.from(".persona-card", {
        scrollTrigger: {
          trigger: ".personas-strip",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        x: 120,
        opacity: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: "power3.out",
      });

      const mm = gsap.matchMedia();
      mm.add("(min-width: 1024px)", () => {
        const cards = sectionRef.current?.querySelectorAll(".persona-card");
        cards?.forEach((card) => {
          card.addEventListener("mouseenter", () => {
            gsap.to(card, { y: -8, scale: 1.02, duration: 0.3, ease: "power2.out" });
          });
          card.addEventListener("mouseleave", () => {
            gsap.to(card, { y: 0, scale: 1, duration: 0.3, ease: "power2.out" });
          });
        });
        return () => {};
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section id="personas" ref={sectionRef} className="py-32 px-6 bg-[var(--bg-canvas)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        <div className="personas-header text-center mb-16">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-5 block">
            WHO IT&rsquo;S FOR
          </span>
          <h2 className="text-[clamp(28px,4.5vw,48px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            Built for operators who move.
          </h2>
          <p className="mt-5 text-[17px] text-[var(--ink-2)] max-w-lg mx-auto leading-relaxed">
            Whether you&rsquo;re a solo founder or running a growth team, RaptorFlow is sized for how you work.
          </p>
        </div>

        <div className="personas-strip overflow-x-auto pb-4 snap-x snap-mandatory -mx-6 px-6">
          <div className="flex gap-5 w-max lg:w-auto lg:grid lg:grid-cols-3">
            {PERSONAS.map((persona) => {
              const PIcon = persona.Icon;
              return (
                <div
                  key={persona.category}
                  className="persona-card snap-start flex-shrink-0 w-[340px] lg:w-auto rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)] p-10 flex flex-col will-change-transform"
                >
                  <div className="flex items-center gap-3 mb-8">
                    <div className="w-11 h-11 rounded-[var(--radius-sm)] bg-[var(--rf-charcoal)] flex items-center justify-center flex-shrink-0">
                      <PIcon size={20} className="text-[var(--rf-ivory)]" />
                    </div>
                    <span className="text-[11px] font-semibold tracking-[0.1em] text-[var(--ink-3)] uppercase">
                      {persona.category}
                    </span>
                  </div>

                  <h3 className="text-[26px] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.01em] mb-2">
                    {persona.name}
                  </h3>
                  <p className="text-[14px] font-medium text-[var(--ink-3)] mb-5">
                    {persona.subtitle}
                  </p>
                  <p className="text-[15px] text-[var(--ink-2)] leading-relaxed mb-8 flex-1">
                    {persona.description}
                  </p>

                  <ul className="space-y-2.5 mb-8">
                    {persona.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2.5 text-[14px] text-[var(--ink-2)]">
                        <span className="text-[var(--ink-3)] mt-0.5 flex-shrink-0">→</span>
                        {feature}
                      </li>
                    ))}
                  </ul>

                  <a
                    href={persona.href}
                    className="text-[13px] font-semibold text-[var(--rf-charcoal)] hover:text-[var(--ink-2)] transition-colors duration-200 flex items-center gap-1.5"
                  >
                    Learn more →
                  </a>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
