"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { intelSignals } from "@/lib/landing-copy";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingIntel() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Radar sweep rotation
      gsap.to(".intel-radar-sweep", {
        rotation: 360,
        duration: 6,
        repeat: -1,
        ease: "none",
        transformOrigin: "center center",
      });

      // Signal dots reveal and ping on entry
      gsap.from(".intel-signal-dot", {
        scale: 0,
        opacity: 0,
        duration: 0.5,
        stagger: 0.2,
        ease: "back.out(1.7)",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 78%",
          once: true,
        },
      });

      // Amber alert node pulse
      gsap.to(".intel-alert-node", {
        boxShadow: "0 0 32px rgba(245,158,11,0.6)",
        scale: 1.08,
        duration: 1.2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });

      // Signal cards stagger in
      gsap.from(".intel-signal-card", {
        x: 20,
        opacity: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: "power3.out",
        scrollTrigger: {
          trigger: ".intel-signals-list",
          start: "top 80%",
          once: true,
        },
      });
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="intel"
      eyebrow="Intel"
      title="Competitor signals before they become surprises."
      description="RaptorFlow watches market changes and turns useful signals into campaign response paths."
      className="bg-[#121212] border-t border-zinc-900"
    >
      <div ref={sectionRef} className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

        {/* Radar visual */}
        <div className="flex items-center justify-center">
          <div className="relative w-64 h-64 sm:w-80 sm:h-80">
            {/* Concentric rings */}
            {[1, 2, 3].map((r) => (
              <div
                key={r}
                className="absolute rounded-full border border-zinc-800"
                style={{
                  inset: `${(r - 1) * 22}%`,
                }}
              />
            ))}

            {/* Sweep arm */}
            <div
              className="intel-radar-sweep absolute inset-0 flex items-center justify-center"
              style={{ transformOrigin: "center center" }}
            >
              <div
                className="absolute w-1/2 h-px origin-left"
                style={{
                  left: "50%",
                  background: "linear-gradient(to right, rgba(245,158,11,0.7), transparent)",
                  boxShadow: "0 0 8px rgba(245,158,11,0.3)",
                }}
              />
            </div>

            {/* Center dot */}
            <div
              className="intel-alert-node absolute inset-[49%] rounded-full bg-amber-500"
              style={{ boxShadow: "0 0 20px rgba(245,158,11,0.5)" }}
            />

            {/* Signal dots at various points */}
            <div className="intel-signal-dot absolute w-3 h-3 rounded-full border-2 border-red-500 bg-red-500/20" style={{ top: "18%", left: "68%" }} />
            <div className="intel-signal-dot absolute w-2.5 h-2.5 rounded-full border-2 border-amber-400 bg-amber-400/20" style={{ top: "62%", left: "78%" }} />
            <div className="intel-signal-dot absolute w-2 h-2 rounded-full border-2 border-green-500 bg-green-500/20" style={{ top: "75%", left: "32%" }} />
            <div className="intel-signal-dot absolute w-2.5 h-2.5 rounded-full border-2 border-amber-500 bg-amber-500/20" style={{ top: "30%", left: "20%" }} />

            {/* Labels for dots */}
            <div className="absolute text-[9px] font-mono text-red-400 uppercase tracking-wider" style={{ top: "10%", left: "72%" }}>Critical</div>
            <div className="absolute text-[9px] font-mono text-amber-400 uppercase tracking-wider" style={{ top: "65%", left: "83%" }}>Watch</div>
            <div className="absolute text-[9px] font-mono text-green-500 uppercase tracking-wider" style={{ top: "80%", left: "22%" }}>Low</div>
          </div>
        </div>

        {/* Signal cards */}
        <div className="intel-signals-list flex flex-col gap-3">
          <p className="text-xs font-mono text-zinc-600 uppercase tracking-widest mb-2">
            Active signals → Response paths
          </p>
          {intelSignals.map((signal, i) => (
            <div
              key={i}
              className="intel-signal-card bg-[#1a1a1a] border border-zinc-800 rounded-xl p-4 flex items-center gap-4 hover:border-zinc-700 transition-colors duration-200 group"
            >
              <div
                className="w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: signal.color, boxShadow: `0 0 8px ${signal.color}60` }}
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-zinc-300 group-hover:text-white transition-colors duration-200">
                  {signal.label}
                </p>
              </div>
              <div className="text-[10px] font-mono text-zinc-700 uppercase tracking-widest">
                → Response path
              </div>
            </div>
          ))}

          <div className="mt-4 bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse shrink-0" />
            <p className="text-xs text-zinc-400 leading-5">
              Every signal is tagged with strategic implication, not just raw data.
            </p>
          </div>
        </div>
      </div>
    </LandingSection>
  );
}
