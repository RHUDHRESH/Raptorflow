"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { usePrefersReducedMotion } from "./landing-gsap-provider";

const CARDS = [
  { label: "Foundation", x: 0, y: 0, desc: "Business context layer" },
  { label: "Campaign", x: 0, y: 0, desc: "Active execution plan" },
  { label: "Intel", x: 0, y: 0, desc: "Competitor signals" },
  { label: "Daily Action", x: 0, y: 0, desc: "Today's single move" },
  { label: "Memory", x: 0, y: 0, desc: "Compounding knowledge" },
];

export function LandingCommandVisual() {
  const ref = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Pulse the central node
      gsap.to(".command-center-node", {
        boxShadow: "0 0 36px rgba(245,158,11,0.5), 0 0 80px rgba(245,158,11,0.15)",
        scale: 1.06,
        duration: 2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });

      // Animate traveling dot along each line
      gsap.utils.toArray<HTMLElement>(".command-dot").forEach((dot, i) => {
        gsap.fromTo(
          dot,
          { opacity: 0, left: "50%", top: "50%" },
          {
            opacity: 1,
            left: dot.dataset.tx,
            top: dot.dataset.ty,
            duration: 2,
            repeat: -1,
            delay: i * 0.5,
            ease: "power1.inOut",
          }
        );
      });
    },
    { scope: ref }
  );

  return (
    <div ref={ref} className="relative w-full aspect-square max-w-[480px] mx-auto select-none">
      {/* Ambient glow behind center */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(circle at 50% 50%, rgba(245,158,11,0.06) 0%, transparent 65%)",
        }}
      />

      {/* SVG connector lines */}
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 480 480"
        fill="none"
        aria-hidden="true"
      >
        {/* Lines from corners to center */}
        <line className="command-line" x1="80" y1="80" x2="240" y2="240" stroke="rgba(245,158,11,0.25)" strokeWidth="1" strokeDasharray="4 6" />
        <line className="command-line" x1="400" y1="80" x2="240" y2="240" stroke="rgba(245,158,11,0.25)" strokeWidth="1" strokeDasharray="4 6" />
        <line className="command-line" x1="80" y1="400" x2="240" y2="240" stroke="rgba(245,158,11,0.25)" strokeWidth="1" strokeDasharray="4 6" />
        <line className="command-line" x1="400" y1="400" x2="240" y2="240" stroke="rgba(245,158,11,0.25)" strokeWidth="1" strokeDasharray="4 6" />
        <line className="command-line" x1="240" y1="52" x2="240" y2="240" stroke="rgba(245,158,11,0.25)" strokeWidth="1" strokeDasharray="4 6" />
      </svg>

      {/* Central Decision Node */}
      <div
        className="command-center-node absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 bg-[#1a1a1a] border-2 border-amber-500 flex flex-col items-center justify-center z-10 rounded-full"
        style={{ boxShadow: "0 0 24px rgba(245,158,11,0.3)" }}
      >
        <span className="text-[10px] font-mono text-amber-500 uppercase tracking-widest leading-none">Clarity</span>
        <span className="text-[8px] font-mono text-zinc-600 uppercase tracking-widest mt-0.5">Engine</span>
      </div>

      {/* Card: Foundation — top-center */}
      <div className="command-card absolute left-1/2 top-[2%] -translate-x-1/2 bg-[#1a1a1a] border border-zinc-800 rounded-xl p-3 w-36 text-center">
        <span className="text-[10px] font-mono text-amber-500 uppercase tracking-widest block">Foundation</span>
        <span className="text-[9px] text-zinc-600 block mt-0.5">Business context layer</span>
      </div>

      {/* Card: Campaign — top-left */}
      <div className="command-card absolute left-[4%] top-[10%] bg-[#1a1a1a] border border-zinc-800 rounded-xl p-3 w-36">
        <span className="text-[10px] font-mono text-white uppercase tracking-widest block">Campaign</span>
        <span className="text-[9px] text-zinc-600 block mt-0.5">Active execution plan</span>
      </div>

      {/* Card: Intel — top-right */}
      <div className="command-card absolute right-[4%] top-[10%] bg-[#1a1a1a] border border-zinc-800 rounded-xl p-3 w-36">
        <span className="text-[10px] font-mono text-white uppercase tracking-widest block">Intel</span>
        <span className="text-[9px] text-zinc-600 block mt-0.5">Competitor signals</span>
      </div>

      {/* Card: Daily Action — bottom-left */}
      <div className="command-card absolute left-[4%] bottom-[10%] bg-[#1a1a1a] border border-zinc-800 rounded-xl p-3 w-36">
        <span className="text-[10px] font-mono text-white uppercase tracking-widest block">Daily Action</span>
        <span className="text-[9px] text-zinc-600 block mt-0.5">Today's single move</span>
      </div>

      {/* Card: Memory — bottom-right */}
      <div className="command-card absolute right-[4%] bottom-[10%] bg-[#1a1a1a] border border-zinc-800 rounded-xl p-3 w-36">
        <span className="text-[10px] font-mono text-white uppercase tracking-widest block">Memory</span>
        <span className="text-[9px] text-zinc-600 block mt-0.5">Compounding knowledge</span>
      </div>

      {/* Metric pill */}
      <div className="command-card absolute right-[8%] top-1/2 -translate-y-1/2 bg-[#0f0f0f] border border-amber-500/30 rounded-lg px-3 py-2 flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse shrink-0" />
        <span className="text-[9px] font-mono text-amber-500 uppercase tracking-widest whitespace-nowrap">Live Signal</span>
      </div>
    </div>
  );
}
