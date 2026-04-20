"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const BRIEFING_ROWS = [
  {
    priority: true,
    label: "Today's move",
    value: "Publish LinkedIn post on product differentiation — draft ready",
    color: "amber",
  },
  {
    priority: false,
    label: "Campaign status",
    value: "Monsoon Expansion • Day 8 of 30 • 3 tasks due",
    color: "zinc",
  },
  {
    priority: false,
    label: "Competitor signal",
    value: "Luminous Brands updated hero messaging yesterday",
    color: "zinc",
  },
  {
    priority: false,
    label: "Performance note",
    value: "LinkedIn CTR up 18% vs last week",
    color: "zinc",
  },
];

export function LandingDailyWins() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Briefing card slides in
      gsap.from(".daily-card", {
        y: 40,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 78%",
          once: true,
        },
      });

      // Priority row expands
      gsap.from(".daily-priority-row", {
        scaleY: 0,
        opacity: 0,
        transformOrigin: "top center",
        duration: 0.6,
        delay: 0.4,
        ease: "power2.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 75%",
          once: true,
        },
      });

      // Context rows stagger
      gsap.from(".daily-context-row", {
        x: -16,
        opacity: 0,
        duration: 0.5,
        stagger: 0.1,
        delay: 0.65,
        ease: "power2.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 75%",
          once: true,
        },
      });
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="daily-wins"
      eyebrow="Daily Wins"
      title="Wake up to one clear marketing move."
      description="Every morning, RaptorFlow turns campaign status, competitor signals, and memory into one focused action."
      className="bg-[#F5F0E8] border-t border-[#E5DED4]"
    >
      <div ref={sectionRef} className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">

        {/* Briefing card */}
        <div className="daily-card bg-white border border-[#E5DED4] rounded-2xl overflow-hidden">
          {/* Card header */}
          <div className="px-6 py-4 border-b border-[#E5DED4] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-[#D97757] animate-pulse" />
              <span className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest">
                Morning Briefing
              </span>
            </div>
            <span className="text-[10px] font-mono text-[#BAB0A0] uppercase tracking-widest">
              Today
            </span>
          </div>

          {/* Rows */}
          <div className="divide-y divide-[#E5DED4]">
            {BRIEFING_ROWS.map((row, i) => (
              <div
                key={i}
                className={`px-6 py-4 flex items-start gap-4 ${
                  row.priority
                    ? "daily-priority-row bg-[#FBE9DE] border-l-2 border-[#D97757]"
                    : "daily-context-row"
                }`}
              >
                <div className="flex flex-col gap-1 min-w-0">
                  <span
                    className={`text-[9px] font-mono uppercase tracking-widest ${
                      row.priority ? "text-[#D97757]" : "text-[#9A948C]"
                    }`}
                  >
                    {row.label}
                  </span>
                  <span
                    className={`text-sm leading-5 ${
                      row.priority ? "text-[#2A2622] font-medium" : "text-[#6B655E]"
                    }`}
                  >
                    {row.value}
                  </span>
                </div>
                {row.priority && (
                  <div className="shrink-0 ml-auto">
                    <span className="bg-[#D97757] text-[#2A2622] text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded">
                      Act
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right: copy */}
        <div className="flex flex-col gap-8 pt-4">
          <div className="flex flex-col gap-4">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-[#FBE9DE] border border-[#D97757]/30 rounded-lg flex items-center justify-center shrink-0 mt-1">
                <span className="text-[#D97757] text-sm">◈</span>
              </div>
              <div>
                <h3 className="text-base font-semibold text-[#2A2622] mb-1">No decision fatigue</h3>
                <p className="text-sm text-[#6B655E] leading-6">
                  One priority row. Context to back it up. You know what to do.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-[#FBE9DE] border border-[#D97757]/30 rounded-lg flex items-center justify-center shrink-0 mt-1">
                <span className="text-[#D97757] text-sm">◆</span>
              </div>
              <div>
                <h3 className="text-base font-semibold text-[#2A2622] mb-1">Built from live signals</h3>
                <p className="text-sm text-[#6B655E] leading-6">
                  Campaign state, competitor movement, and performance data feed the briefing.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-[#FBE9DE] border border-[#D97757]/30 rounded-lg flex items-center justify-center shrink-0 mt-1">
                <span className="text-[#D97757] text-sm">◉</span>
              </div>
              <div>
                <h3 className="text-base font-semibold text-[#2A2622] mb-1">Replaces Monday chaos</h3>
                <p className="text-sm text-[#6B655E] leading-6">
                  Stop rebuilding context every week. The system remembers.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </LandingSection>
  );
}
