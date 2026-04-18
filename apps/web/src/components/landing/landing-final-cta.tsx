"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { AmberButton, GhostButton } from "./landing-ui-primitives";
import { ArrowRightIcon } from "@radix-ui/react-icons";
import { referralSignupHref } from "@/lib/referrals";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const SCATTERED_CARDS = [
  { label: "Foundation", rotate: -8, tx: -140, ty: -60 },
  { label: "Campaign", rotate: 5, tx: 140, ty: -50 },
  { label: "Intel", rotate: -4, tx: -100, ty: 60 },
  { label: "Memory", rotate: 7, tx: 110, ty: 55 },
  { label: "Daily Wins", rotate: -6, tx: 0, ty: -90 },
];

export function LandingFinalCTA() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 80%",
          once: true,
        },
      });

      // Cards converge from scattered positions to center
      tl.from(".final-scattered-card", {
        x: (i) => SCATTERED_CARDS[i]?.tx ?? 0,
        y: (i) => SCATTERED_CARDS[i]?.ty ?? 0,
        rotation: (i) => SCATTERED_CARDS[i]?.rotate ?? 0,
        opacity: 0,
        scale: 0.9,
        duration: 0.9,
        stagger: 0.08,
        ease: "power3.out",
      });

      // Amber path draws
      tl.fromTo(
        ".final-amber-path",
        { scaleX: 0 },
        {
          scaleX: 1,
          transformOrigin: "left center",
          duration: 0.8,
          ease: "power2.inOut",
        },
        "-=0.3"
      );

      // CTA appears last
      tl.from(
        ".final-cta-group",
        {
          y: 24,
          opacity: 0,
          duration: 0.7,
          ease: "power3.out",
        },
        "-=0.2"
      );
    },
    { scope: sectionRef }
  );

  return (
    <section
      id="final-cta"
      ref={sectionRef}
      className="relative px-6 py-32 lg:px-8 overflow-hidden bg-[#0f0f0f] border-t border-zinc-900"
    >
      {/* Background glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at 50% 100%, rgba(245,158,11,0.06) 0%, transparent 60%)",
        }}
        aria-hidden="true"
      />

      <div className="relative mx-auto max-w-4xl text-center">

        {/* Scattered cards converging */}
        <div className="relative h-40 mb-12 flex items-center justify-center overflow-hidden">
          {SCATTERED_CARDS.map((card, i) => (
            <div
              key={i}
              className="final-scattered-card absolute bg-[#1a1a1a] border border-zinc-800 rounded-xl px-3 py-2"
            >
              <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">
                {card.label}
              </span>
            </div>
          ))}

          {/* Amber convergence path */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-64 h-px">
            <div className="final-amber-path h-full bg-amber-500/50 origin-left" />
          </div>
        </div>

        <h2 className="text-4xl md:text-6xl font-semibold tracking-tight text-white leading-[1.05] mb-6">
          Stop restarting marketing from zero.
        </h2>
        <p className="text-base md:text-lg text-zinc-400 leading-7 max-w-xl mx-auto mb-12">
          Start with Foundation. Build the memory layer. Turn strategy into daily execution.
        </p>

        <div className="final-cta-group flex flex-col sm:flex-row gap-4 justify-center">
          <AmberButton href={referralSignupHref("LOKI")} className="text-base px-10 py-4">
            Start now <ArrowRightIcon className="w-4 h-4" />
          </AmberButton>
          <GhostButton href="/sign-in" className="text-base px-10 py-4">
            Sign in
          </GhostButton>
        </div>

        <p className="mt-8 text-xs font-mono text-zinc-700 uppercase tracking-widest">
          Built for Indian SMBs · No setup fees · Start today
        </p>
      </div>
    </section>
  );
}
