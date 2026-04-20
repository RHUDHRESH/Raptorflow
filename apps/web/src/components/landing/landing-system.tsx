"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { systemPillars } from "@/lib/landing-copy";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingSystem() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Pillar cards stagger in
      gsap.from(".system-pillar", {
        y: 40,
        opacity: 0,
        duration: 0.8,
        stagger: 0.11,
        ease: "power3.out",
        scrollTrigger: {
          trigger: ".system-pillars",
          start: "top 78%",
          once: true,
        },
      });

      // Connector line draws
      gsap.fromTo(
        ".system-connector",
        { scaleX: 0 },
        {
          scaleX: 1,
          transformOrigin: "left center",
          duration: 1.2,
          ease: "power2.inOut",
          scrollTrigger: {
            trigger: ".system-pillars",
            start: "top 75%",
            once: true,
          },
        }
      );

      // Active amber glow moves through cards
      systemPillars.forEach((_, i) => {
        gsap.fromTo(
          `.system-active-${i}`,
          { opacity: 0 },
          {
            opacity: 1,
            duration: 0.4,
            delay: 0.3 + i * 0.25,
            ease: "power2.out",
            scrollTrigger: {
              trigger: ".system-pillars",
              start: "top 75%",
              once: true,
            },
          }
        );
      });
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="system"
      eyebrow="The operating loop"
      title="One loop for strategy, campaigns, intelligence, and action."
      description="RaptorFlow connects the parts of marketing that usually live in separate tabs."
      className="bg-[#F5F0E8] border-t border-[#E5DED4]"
    >
      <div ref={sectionRef}>
        {/* Connector line */}
        <div className="hidden lg:flex items-center mb-[-1px] mt-[-24px] px-2">
          <div className="system-connector h-px bg-[#D97757]/30 flex-1 origin-left" />
        </div>

        {/* Pillars */}
        <div className="system-pillars grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-0 border border-[#E5DED4]">
          {systemPillars.map((pillar, i) => (
            <div
              key={i}
              className={`system-pillar relative p-7 border-b lg:border-b-0 lg:border-r border-[#E5DED4] last:border-r-0 last:border-b-0 hover:bg-white transition-colors duration-200 group cursor-default`}
            >
              {/* Amber top accent — reveals sequentially */}
              <div
                className={`system-active-${i} absolute top-0 left-0 right-0 h-px bg-[#D97757]/70 opacity-0`}
              />

              <div className="flex items-center gap-3 mb-5">
                <span className="text-xs font-mono text-[#BAB0A0]">{pillar.number}</span>
                <span className="text-lg text-[#9A948C] group-hover:text-[#D97757] transition-colors duration-200">
                  {pillar.glyph}
                </span>
              </div>
              <h3 className="text-base font-semibold text-[#2A2622] mb-3 group-hover:text-[#D97757] transition-colors duration-200">
                {pillar.title}
              </h3>
              <p className="text-sm text-[#6B655E] leading-6">{pillar.body}</p>
            </div>
          ))}
        </div>
      </div>
    </LandingSection>
  );
}
