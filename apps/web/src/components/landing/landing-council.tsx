"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { councilPerspectives } from "@/lib/landing-copy";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingCouncil() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Perspective nodes light in sequence
      gsap.from(".council-node", {
        scale: 0.7,
        opacity: 0,
        duration: 0.4,
        stagger: 0.07,
        ease: "back.out(1.4)",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 78%",
          once: true,
        },
      });

      // Argument lines draw and converge
      gsap.fromTo(
        ".council-arg-line",
        { strokeDashoffset: 120 },
        {
          strokeDashoffset: 0,
          duration: 0.8,
          stagger: 0.05,
          ease: "power2.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 75%",
            once: true,
          },
        }
      );

      // Synthesis path draws in amber
      gsap.fromTo(
        ".council-synthesis",
        { strokeDashoffset: 200 },
        {
          strokeDashoffset: 0,
          duration: 1.2,
          delay: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 73%",
            once: true,
          },
        }
      );
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="council"
      eyebrow="Council"
      title="Better strategy comes from disagreement."
      description="Multiple perspectives challenge a campaign decision, then RaptorFlow turns the tension into one practical plan."
      className="bg-[#121212] border-t border-zinc-900"
    >
      <div ref={sectionRef} className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

        {/* Perspective node grid */}
        <div className="relative">
          {/* Nodes arranged in a ring */}
          <div className="relative w-full aspect-square max-w-[360px] mx-auto">
            {/* Convergence lines SVG */}
            <svg
              className="absolute inset-0 w-full h-full"
              viewBox="0 0 360 360"
              fill="none"
              aria-hidden="true"
            >
              {/* Lines from nodes to center */}
              {councilPerspectives.map((_, i) => {
                const total = councilPerspectives.length;
                const angle = (i / total) * 2 * Math.PI - Math.PI / 2;
                const r = 148;
                const x = 180 + r * Math.cos(angle);
                const y = 180 + r * Math.sin(angle);
                return (
                  <line
                    key={i}
                    className="council-arg-line"
                    x1={x}
                    y1={y}
                    x2="180"
                    y2="180"
                    stroke="rgba(245,158,11,0.18)"
                    strokeWidth="1"
                    strokeDasharray="120"
                  />
                );
              })}
              {/* Synthesis circle */}
              <circle
                className="council-synthesis"
                cx="180"
                cy="180"
                r="28"
                stroke="rgba(245,158,11,0.7)"
                strokeWidth="1.5"
                strokeDasharray="200"
                fill="none"
              />
            </svg>

            {/* Perspective nodes */}
            {councilPerspectives.map((label, i) => {
              const total = councilPerspectives.length;
              const angle = (i / total) * 2 * Math.PI - Math.PI / 2;
              const r = 148;
              const x = 180 + r * Math.cos(angle);
              const y = 180 + r * Math.sin(angle);
              return (
                <div
                  key={i}
                  className="council-node absolute -translate-x-1/2 -translate-y-1/2 bg-[#1a1a1a] border border-zinc-800 rounded-lg px-2 py-1 hover:border-amber-500/40 hover:bg-[#1f1f1f] transition-all duration-200 group cursor-default"
                  style={{ left: `${(x / 360) * 100}%`, top: `${(y / 360) * 100}%` }}
                >
                  <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest group-hover:text-amber-500 transition-colors duration-200 whitespace-nowrap">
                    {label}
                  </span>
                </div>
              );
            })}

            {/* Center synthesis node */}
            <div
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-14 h-14 bg-[#1a1a1a] border-2 border-amber-500 rounded-full flex items-center justify-center"
              style={{ boxShadow: "0 0 24px rgba(245,158,11,0.3)" }}
            >
              <span className="text-[9px] font-mono text-amber-500 uppercase tracking-wider text-center leading-tight">
                Plan
              </span>
            </div>
          </div>
        </div>

        {/* Copy */}
        <div className="flex flex-col gap-8">
          <div className="flex flex-col gap-4">
            <div className="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-5">
              <span className="text-[10px] font-mono text-amber-500 uppercase tracking-widest block mb-2">Positioning</span>
              <p className="text-sm text-zinc-400 italic">
                "This campaign is positioned too broadly. We need to narrow to our top segment before spending on ads."
              </p>
            </div>
            <div className="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-5">
              <span className="text-[10px] font-mono text-amber-500 uppercase tracking-widest block mb-2">Growth</span>
              <p className="text-sm text-zinc-400 italic">
                "Disagree. This is a reach phase. Broad now, narrow at Month 2 when we have conversion data."
              </p>
            </div>
            <div className="bg-[#1a1a1a] border border-amber-500/20 rounded-xl p-5" style={{ boxShadow: "0 0 20px rgba(245,158,11,0.06)" }}>
              <span className="text-[10px] font-mono text-amber-500 uppercase tracking-widest block mb-2">Synthesis</span>
              <p className="text-sm text-white">
                Run broad for 2 weeks with a performance trigger. If CPL exceeds ₹420, narrow segment automatically.
              </p>
            </div>
          </div>
        </div>
      </div>
    </LandingSection>
  );
}
