"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { foundationCards } from "@/lib/landing-copy";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingFoundation() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Tiny cards stagger in
      gsap.from(".foundation-chip", {
        y: 20,
        opacity: 0,
        duration: 0.5,
        stagger: 0.035,
        ease: "power2.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 78%",
          once: true,
        },
      });

      // SVG lines draw toward core
      const paths = gsap.utils.toArray<SVGLineElement>(".foundation-line");
      paths.forEach((path) => {
        gsap.fromTo(
          path,
          { opacity: 0, strokeDashoffset: 60 },
          {
            opacity: 1,
            strokeDashoffset: 0,
            duration: 0.7,
            stagger: 0.03,
            ease: "power2.out",
            scrollTrigger: {
              trigger: sectionRef.current,
              start: "top 73%",
              once: true,
            },
          }
        );
      });

      // Core pulse
      gsap.to(".foundation-core", {
        boxShadow: "0 0 48px rgba(245,158,11,0.45)",
        scale: 1.05,
        duration: 1.8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="foundation"
      eyebrow="Foundation"
      title="The system starts with your business, not a blank prompt."
      description="Foundation captures your ICP, positioning, competitors, pricing, channels, goals, voice, budget, assets, frustrations, and strategist style. That context powers every campaign and recommendation after it."
      className="bg-[#0f0f0f] border-t border-zinc-900"
    >
      <div ref={sectionRef} className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

        {/* Blueprint grid of chips */}
        <div className="relative">
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
            {foundationCards.map((label, i) => (
              <div
                key={i}
                className="foundation-chip bg-[#1a1a1a] border border-zinc-800 rounded-lg px-3 py-2 text-center hover:border-amber-500/40 hover:bg-[#1f1f1f] transition-all duration-200 cursor-default group"
              >
                <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest group-hover:text-amber-500 transition-colors duration-200 block leading-tight">
                  {label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Core diagram */}
        <div className="flex flex-col items-center gap-8">
          <div className="relative flex items-center justify-center w-full">
            {/* SVG lines converging */}
            <svg
              viewBox="0 0 300 200"
              className="absolute inset-0 w-full h-full"
              fill="none"
              aria-hidden="true"
            >
              <line className="foundation-line" x1="0" y1="30" x2="150" y2="100" stroke="rgba(245,158,11,0.3)" strokeWidth="1" strokeDasharray="60" />
              <line className="foundation-line" x1="300" y1="30" x2="150" y2="100" stroke="rgba(245,158,11,0.3)" strokeWidth="1" strokeDasharray="60" />
              <line className="foundation-line" x1="0" y1="100" x2="150" y2="100" stroke="rgba(245,158,11,0.3)" strokeWidth="1" strokeDasharray="60" />
              <line className="foundation-line" x1="300" y1="100" x2="150" y2="100" stroke="rgba(245,158,11,0.3)" strokeWidth="1" strokeDasharray="60" />
              <line className="foundation-line" x1="0" y1="170" x2="150" y2="100" stroke="rgba(245,158,11,0.3)" strokeWidth="1" strokeDasharray="60" />
              <line className="foundation-line" x1="300" y1="170" x2="150" y2="100" stroke="rgba(245,158,11,0.3)" strokeWidth="1" strokeDasharray="60" />
              <line className="foundation-line" x1="150" y1="0" x2="150" y2="100" stroke="rgba(245,158,11,0.3)" strokeWidth="1" strokeDasharray="60" />
              <line className="foundation-line" x1="150" y1="200" x2="150" y2="100" stroke="rgba(245,158,11,0.3)" strokeWidth="1" strokeDasharray="60" />
            </svg>

            {/* Core node */}
            <div
              className="foundation-core relative z-10 w-28 h-28 bg-[#1a1a1a] border-2 border-amber-500 rounded-full flex flex-col items-center justify-center my-12"
              style={{ boxShadow: "0 0 32px rgba(245,158,11,0.25)" }}
            >
              <span className="text-[10px] font-mono text-amber-500 uppercase tracking-widest">Context</span>
              <span className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest mt-0.5">Core</span>
            </div>
          </div>

          {/* Copy below */}
          <div className="text-center max-w-xs">
            <p className="text-sm font-mono text-zinc-600 uppercase tracking-widest">
              21 context signals → one unified intelligence layer
            </p>
          </div>
        </div>
      </div>
    </LandingSection>
  );
}
