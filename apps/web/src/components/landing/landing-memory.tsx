"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { memorySignals } from "@/lib/landing-copy";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

// Memory lattice node positions
const PAST_NODES = [
  { cx: 70, cy: 80 },
  { cx: 140, cy: 50 },
  { cx: 200, cy: 110 },
  { cx: 280, cy: 70 },
  { cx: 80, cy: 160 },
  { cx: 170, cy: 190 },
];

const FUTURE_NODES = [
  { cx: 360, cy: 90 },
  { cx: 420, cy: 140 },
];

const LINKS = [
  [0, 1], [1, 2], [2, 3], [0, 4], [4, 5], [5, 2], [3, 6], [2, 6], [5, 7], [6, 7],
];

export function LandingMemory() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Past nodes reveal
      gsap.from(".memory-past-node", {
        scale: 0,
        opacity: 0,
        duration: 0.45,
        stagger: 0.08,
        ease: "back.out(1.7)",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 78%",
          once: true,
        },
      });

      // Links draw
      gsap.fromTo(
        ".memory-link",
        { strokeDashoffset: 200 },
        {
          strokeDashoffset: 0,
          duration: 0.6,
          stagger: 0.06,
          ease: "power2.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 75%",
            once: true,
          },
        }
      );

      // Future nodes brighten last
      gsap.from(".memory-future-node", {
        scale: 0,
        opacity: 0,
        duration: 0.7,
        stagger: 0.15,
        delay: 0.8,
        ease: "back.out(2)",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 73%",
          once: true,
        },
      });

      // Future node glow pulse
      gsap.to(".memory-future-node", {
        filter: "drop-shadow(0 0 12px rgba(245,158,11,0.8))",
        duration: 1.4,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        delay: 1.5,
      });
    },
    { scope: sectionRef }
  );

  const allNodes = [...PAST_NODES, ...FUTURE_NODES];

  return (
    <LandingSection
      id="memory"
      eyebrow="Compounding memory"
      title="Every campaign teaches the next one."
      description="RaptorFlow remembers what worked, what failed, what was predicted, and what actually happened. The longer it works with you, the less generic it becomes."
      className="bg-[#0f0f0f] border-t border-zinc-900"
    >
      <div ref={sectionRef} className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">

        {/* Memory lattice SVG */}
        <div className="relative">
          <svg
            viewBox="0 0 480 250"
            className="w-full max-w-lg"
            fill="none"
            aria-hidden="true"
          >
            {/* Links */}
            {LINKS.map(([a, b], i) => {
              const nodeA = allNodes[a];
              const nodeB = allNodes[b];
              if (!nodeA || !nodeB) return null;
              const isFutureLink = a >= PAST_NODES.length || b >= PAST_NODES.length;
              return (
                <line
                  key={i}
                  className="memory-link"
                  x1={nodeA.cx}
                  y1={nodeA.cy}
                  x2={nodeB.cx}
                  y2={nodeB.cy}
                  stroke={isFutureLink ? "rgba(245,158,11,0.5)" : "rgba(161,161,170,0.2)"}
                  strokeWidth="1"
                  strokeDasharray="200"
                />
              );
            })}

            {/* Past nodes */}
            {PAST_NODES.map((node, i) => (
              <circle
                key={i}
                className="memory-past-node"
                cx={node.cx}
                cy={node.cy}
                r="8"
                fill="#262626"
                stroke="rgba(113,113,122,0.5)"
                strokeWidth="1"
              />
            ))}

            {/* Future nodes */}
            {FUTURE_NODES.map((node, i) => (
              <circle
                key={i}
                className="memory-future-node"
                cx={node.cx}
                cy={node.cy}
                r={i === 1 ? 13 : 10}
                fill={i === 1 ? "rgba(245,158,11,0.15)" : "#1a1a1a"}
                stroke={i === 1 ? "rgba(245,158,11,0.9)" : "rgba(245,158,11,0.5)"}
                strokeWidth="1.5"
              />
            ))}

            {/* Node labels */}
            {PAST_NODES.map((node, i) => (
              <text
                key={i}
                x={node.cx}
                y={node.cy + 20}
                textAnchor="middle"
                className="memory-past-node"
                style={{ fontSize: 7, fill: "rgba(113,113,122,0.7)", fontFamily: "monospace", textTransform: "uppercase" }}
              >
                {memorySignals[i]?.label ?? ""}
              </text>
            ))}
            <text
              x={FUTURE_NODES[0]!.cx}
              y={FUTURE_NODES[0]!.cy + 20}
              textAnchor="middle"
              className="memory-future-node"
              style={{ fontSize: 7, fill: "rgba(245,158,11,0.6)", fontFamily: "monospace", textTransform: "uppercase" }}
            >
              Q3 Prediction
            </text>
            <text
              x={FUTURE_NODES[1]!.cx}
              y={FUTURE_NODES[1]!.cy + 22}
              textAnchor="middle"
              className="memory-future-node"
              style={{ fontSize: 7, fill: "rgba(245,158,11,0.9)", fontFamily: "monospace", textTransform: "uppercase", fontWeight: 700 }}
            >
              Next Rec
            </text>
          </svg>

          <div className="flex items-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-zinc-600" />
              <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest">Past outcomes</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-amber-500" />
              <span className="text-[10px] font-mono text-amber-600 uppercase tracking-widest">Future recommendations</span>
            </div>
          </div>
        </div>

        {/* Right: copy */}
        <div className="flex flex-col gap-6">
          <div className="flex flex-col gap-4">
            {[
              {
                title: "Month 1",
                body: "RaptorFlow learns your business from Foundation. Generic at first.",
              },
              {
                title: "Month 3",
                body: "Three campaigns in. Patterns emerge. Channel preferences solidify.",
              },
              {
                title: "Month 6",
                body: "The system knows what won, what failed, and how your audience shifted.",
              },
              {
                title: "Month 12",
                body: "Every recommendation carries 12 months of compounding context.",
              },
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-4">
                <div className="w-px h-full bg-zinc-800 shrink-0 self-stretch mt-1" />
                <div>
                  <span className="text-xs font-mono text-amber-500 uppercase tracking-widest block mb-1">
                    {item.title}
                  </span>
                  <p className="text-sm text-zinc-500 leading-6">{item.body}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-5 mt-2">
            <p className="text-sm text-zinc-300 leading-6">
              <span className="text-amber-400 font-semibold">Your business deserves marketing memory.</span>{" "}
              Stop rebuilding context every Monday.
            </p>
          </div>
        </div>
      </div>
    </LandingSection>
  );
}
