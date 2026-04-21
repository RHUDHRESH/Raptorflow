"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const painCards = [
  {
    title: "The silence",
    body: "You have a great product and nobody finds it. Your competitor has a worse one and they're everywhere.",
    angle: -90,
  },
  {
    title: "No repeatable channel",
    body: "LinkedIn post. 40 likes. Mostly college friends. No system that works while you sleep.",
    angle: 0,
  },
  {
    title: "The content paralysis",
    body: "You open a blank doc. You know you should be writing. You close it. This has happened 60 times.",
    angle: 90,
  },
  {
    title: "Runway burning",
    body: "You keep saying 'fix marketing next month.' There are only so many next months before there aren't any.",
    angle: 180,
  },
];

export function LandingProblem() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".pain-card", { opacity: 1, scale: 1 });
      });

      mm.add("(min-width: 1024px)", () => {
        // Cards start invisible, scattered, then converge onto orbit positions
        gsap.from(".pain-card", {
          scale: 0,
          opacity: 0,
          stagger: { amount: 0.6, from: "random" },
          duration: 0.7,
          ease: "back.out(1.4)",
          scrollTrigger: {
            trigger: ".orbital-section",
            start: "top 70%",
            once: true,
          },
        });

        // Continuous slow orbit rotation
        gsap.to(".orbit-ring-svg", {
          rotation: 360,
          duration: 40,
          ease: "none",
          repeat: -1,
          transformOrigin: "center center",
        });

        // Counter-rotate cards to keep them upright
        gsap.to(".pain-card", {
          rotation: -360,
          duration: 40,
          ease: "none",
          repeat: -1,
          transformOrigin: "center center",
        });

        // On scroll scrub: cards drift inward
        gsap.to(".pain-card", {
          scale: 0.85,
          opacity: 0,
          stagger: 0.05,
          scrollTrigger: {
            trigger: ".orbital-section",
            start: "bottom 60%",
            end: "bottom 20%",
            scrub: 1,
          },
        });
      });

      mm.add("(max-width: 1023px)", () => {
        gsap.from(".pain-card", {
          y: 30,
          opacity: 0,
          stagger: 0.1,
          duration: 0.6,
          ease: "power2.out",
          scrollTrigger: {
            trigger: ".orbital-section",
            start: "top 70%",
            once: true,
          },
        });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  return (
    <section
      ref={containerRef}
      className="orbital-section relative bg-[#0E0F13] py-[140px] lg:py-[140px]"
    >
      <div className="mx-auto max-w-[1200px] px-6 lg:px-12">
        <div className="text-center mb-16">
          <div className="font-[family-name:var(--font-mono)] text-[10.5px] tracking-[0.12em] uppercase text-[rgba(255,255,255,0.30)] mb-5">
            THE PROBLEM
          </div>
          <h2 className="text-[30px] lg:text-[52px] font-extrabold text-white tracking-[-0.03em] leading-[1.08] max-w-[700px] mx-auto mb-4">
            You built something real.
            <br />
            Nobody knows it exists.
          </h2>
          <p className="text-[17px] text-[rgba(255,255,255,0.45)] max-w-[520px] mx-auto leading-[1.65]">
            You have a great product, real users, zero churn. The problem isn't the product. It's
            the silence between your product and everyone who needs it.
          </p>
        </div>

        {/* ORBITAL DIAGRAM */}
        <div className="relative w-full max-w-[600px] aspect-square mx-auto hidden lg:block">
          {/* SVG Rings */}
          <svg className="orbit-ring-svg absolute inset-0 w-full h-full" viewBox="0 0 600 600">
            <circle
              cx="300"
              cy="300"
              r="170"
              fill="none"
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="1"
            />
            <circle
              cx="300"
              cy="300"
              r="240"
              fill="none"
              stroke="rgba(255,255,255,0.03)"
              strokeWidth="1"
            />
          </svg>

          {/* Center circle */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[130px] h-[130px] rounded-full bg-[#1D1F27] border border-[rgba(232,90,44,0.25)] flex flex-col items-center justify-center gap-1">
            <span className="font-[family-name:var(--font-mono)] text-[9px] text-[rgba(255,255,255,0.35)] tracking-[0.15em]">
              YOUR
            </span>
            <span className="font-[family-name:var(--font-mono)] text-[11px] text-[#E85A2C] tracking-wide font-medium">
              STARTUP
            </span>
          </div>

          {/* Pain cards positioned around orbit */}
          {painCards.map((card, i) => {
            const radius = 220;
            const rad = ((card.angle - 90) * Math.PI) / 180;
            const x = 300 + Math.cos(rad) * radius;
            const y = 300 + Math.sin(rad) * radius;

            return (
              <div
                key={i}
                className="pain-card absolute bg-[#161820] border border-[rgba(255,255,255,0.08)] rounded-[14px] p-[18px_20px] w-[175px]"
                style={{
                  left: x,
                  top: y,
                  transform: "translate(-50%, -50%)",
                }}
              >
                <div className="w-2 h-2 rounded-full bg-[#E85A2C] mb-2.5" />
                <div className="text-[13px] font-semibold text-white tracking-tight mb-1.5">
                  {card.title}
                </div>
                <div className="text-[12px] text-[rgba(255,255,255,0.45)] leading-[1.55]">
                  {card.body}
                </div>
              </div>
            );
          })}
        </div>

        {/* Mobile: stacked cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 lg:hidden">
          {painCards.map((card, i) => (
            <div
              key={i}
              className="pain-card bg-[#161820] border border-[rgba(255,255,255,0.08)] rounded-[14px] p-5"
            >
              <div className="w-2 h-2 rounded-full bg-[#E85A2C] mb-2.5" />
              <div className="text-[13px] font-semibold text-white tracking-tight mb-1.5">
                {card.title}
              </div>
              <div className="text-[12px] text-[rgba(255,255,255,0.45)] leading-[1.55]">
                {card.body}
              </div>
            </div>
          ))}
        </div>

        {/* Kicker line */}
        <div className="mt-20 text-center">
          <p className="text-[24px] lg:text-[32px] font-bold text-white tracking-[-0.03em]">
            You're not behind. The tools are.
          </p>
        </div>
      </div>
    </section>
  );
}
