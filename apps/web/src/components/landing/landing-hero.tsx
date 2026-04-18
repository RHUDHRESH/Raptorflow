"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { SectionLabel, AmberButton, GhostButton } from "./landing-ui-primitives";
import { LandingCommandVisual } from "./landing-command-visual";
import { ArrowRightIcon } from "@radix-ui/react-icons";
import { referralSignupHref } from "@/lib/referrals";

export function LandingHero() {
  const rootRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      tl.from(".hero-kicker", { y: 18, opacity: 0, duration: 0.5 })
        .from(".hero-word", { y: 54, opacity: 0, stagger: 0.055, duration: 0.8 }, "-=0.2")
        .from(".hero-copy", { y: 24, opacity: 0, duration: 0.65 }, "-=0.35")
        .from(".hero-trust", { y: 14, opacity: 0, duration: 0.5 }, "-=0.3")
        .from(".hero-cta", { y: 18, opacity: 0, stagger: 0.1, duration: 0.5 }, "-=0.4")
        .from(".command-card", { y: 28, opacity: 0, scale: 0.96, stagger: 0.09, duration: 0.7 }, "-=0.5")
        .from(".command-line", { scaleX: 0, transformOrigin: "left center", stagger: 0.06, duration: 0.55, ease: "power2.inOut" }, "-=0.45");
    },
    { scope: rootRef }
  );

  const headlineWords = ["Stop", "guessing", "what", "to", "do", "next", "in", "marketing."];

  return (
    <section
      id="hero"
      ref={rootRef}
      className="relative min-h-screen flex items-center pt-16 overflow-hidden"
    >
      {/* Background grid */}
      <div
        className="absolute inset-0 landing-grid opacity-50 pointer-events-none"
        aria-hidden="true"
      />
      {/* Radial amber glow */}
      <div
        className="absolute top-1/3 right-[8%] w-[480px] h-[480px] pointer-events-none"
        style={{
          background:
            "radial-gradient(circle at center, rgba(245,158,11,0.07) 0%, transparent 70%)",
        }}
        aria-hidden="true"
      />
      {/* Noise texture */}
      <div className="absolute inset-0 landing-noise opacity-40 pointer-events-none" aria-hidden="true" />

      <div className="relative mx-auto max-w-7xl px-6 lg:px-8 py-20 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        {/* Left: Copy */}
        <div className="flex flex-col gap-8">
          <SectionLabel className="hero-kicker">
            AI-native marketing execution for Indian SMBs
          </SectionLabel>

          <h1 className="text-5xl md:text-7xl lg:text-8xl tracking-tight font-semibold text-white leading-[1.0] overflow-hidden flex flex-wrap gap-x-4 gap-y-1">
            {headlineWords.map((word, i) => (
              <span
                key={i}
                className={`hero-word inline-block ${
                  word === "marketing." ? "text-amber-400" : ""
                }`}
              >
                {word}
              </span>
            ))}
          </h1>

          <p className="hero-copy text-base md:text-lg text-zinc-400 leading-7 max-w-xl">
            RaptorFlow understands your business, plans campaigns, watches competitor
            signals, and turns every day into one clear action.
          </p>

          <p className="hero-trust text-xs font-mono text-zinc-600 uppercase tracking-widest max-w-lg">
            Built for Indian SMBs that need strategy, execution, intelligence, and
            memory in one system.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 mt-2">
            <AmberButton href={referralSignupHref("LOKI")} className="hero-cta text-base px-8 py-4">
              Start now <ArrowRightIcon className="w-4 h-4" />
            </AmberButton>
            <GhostButton href="#system" className="hero-cta text-base px-8 py-4">
              See how it works
            </GhostButton>
          </div>
        </div>

        {/* Right: Command Visual */}
        <div className="hidden lg:block">
          <LandingCommandVisual />
        </div>
      </div>
    </section>
  );
}
