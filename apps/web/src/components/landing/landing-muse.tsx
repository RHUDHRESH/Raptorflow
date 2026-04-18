"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { museContextLayers } from "@/lib/landing-copy";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingMuse() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Context layers stagger reveal
      gsap.from(".muse-layer", {
        x: -24,
        opacity: 0,
        duration: 0.6,
        stagger: 0.12,
        ease: "power3.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 78%",
          once: true,
        },
      });

      // Recommendation card reveals last
      gsap.from(".muse-result", {
        y: 24,
        opacity: 0,
        scale: 0.97,
        duration: 0.8,
        delay: 0.6,
        ease: "power3.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 75%",
          once: true,
        },
      });

      // Question node path animation
      gsap.fromTo(
        ".muse-path",
        { strokeDashoffset: 200 },
        {
          strokeDashoffset: 0,
          duration: 1.2,
          ease: "power2.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 75%",
            once: true,
          },
        }
      );
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="muse"
      eyebrow="Muse"
      title="Ask with context already attached."
      description="Muse is for tactical and strategic questions when you do not want to explain your business from scratch again."
      className="bg-[#0f0f0f] border-t border-zinc-900"
    >
      <div ref={sectionRef} className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">

        {/* Context flow diagram */}
        <div className="flex flex-col gap-0 relative">
          {/* Question node */}
          <div className="bg-[#1f1f1f] border border-zinc-700 rounded-xl p-4 mb-3 flex items-center gap-3">
            <div className="w-7 h-7 rounded-full bg-amber-500/15 border border-amber-500/40 flex items-center justify-center shrink-0">
              <span className="text-[10px] text-amber-500 font-bold">Q</span>
            </div>
            <p className="text-sm text-zinc-300 italic">
              "Which channel should I double down on this month?"
            </p>
          </div>

          {/* Path SVG */}
          <div className="flex justify-start ml-7 mb-1">
            <svg width="24" height="20" viewBox="0 0 24 20" fill="none" aria-hidden="true">
              <path
                className="muse-path"
                d="M12 0 L12 20"
                stroke="rgba(245,158,11,0.5)"
                strokeWidth="1.5"
                strokeDasharray="200"
              />
            </svg>
          </div>

          {/* Context layers */}
          <div className="flex flex-col gap-2 pl-4 border-l border-amber-500/20 ml-7">
            {museContextLayers.map((layer, i) => (
              <div
                key={i}
                className="muse-layer flex items-start gap-3 bg-[#1a1a1a] border border-zinc-800 rounded-xl p-3 hover:border-zinc-700 transition-colors duration-200"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-amber-500/60 mt-1.5 shrink-0" />
                <div>
                  <span className="text-xs font-mono font-bold text-zinc-400 uppercase tracking-widest block">
                    {layer.label}
                  </span>
                  <span className="text-xs text-zinc-600">{layer.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendation card */}
        <div className="muse-result flex flex-col gap-4">
          <div className="bg-[#1a1a1a] border border-amber-500/30 rounded-2xl p-6 shadow-[0_0_32px_rgba(245,158,11,0.08)]">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span className="text-[10px] font-mono text-amber-500 uppercase tracking-widest">
                Strategic recommendation
              </span>
            </div>
            <h3 className="text-base font-semibold text-white mb-3 leading-snug">
              LinkedIn organic is your highest-performing acquisition channel this quarter.
            </h3>
            <p className="text-sm text-zinc-500 leading-6">
              Based on your Foundation (B2B SaaS, decision-maker ICP), your active campaign
              performance (3.2x engagement vs Email), and Intel signals (competitor reducing
              LinkedIn spend), you should increase posting cadence from 3x to 5x/week.
            </p>
            <div className="mt-5 pt-4 border-t border-zinc-800 flex items-center gap-3">
              <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest">
                Confidence: High · Sources: 4
              </span>
            </div>
          </div>

          <p className="text-xs font-mono text-zinc-700 uppercase tracking-widest text-center">
            Every answer is backed by your context, not a generic model.
          </p>
        </div>
      </div>
    </LandingSection>
  );
}
