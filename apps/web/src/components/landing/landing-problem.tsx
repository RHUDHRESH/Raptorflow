"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { problemCards } from "@/lib/landing-copy";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingProblem() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Amber underline scaleX reveal
      gsap.fromTo(
        ".problem-underline",
        { scaleX: 0 },
        {
          scaleX: 1,
          transformOrigin: "left center",
          duration: 0.9,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 75%",
            once: true,
          },
        }
      );

      // Card stagger reveal
      gsap.from(".problem-card", {
        y: 40,
        opacity: 0,
        duration: 0.7,
        stagger: 0.1,
        ease: "power3.out",
        scrollTrigger: {
          trigger: ".problem-card-grid",
          start: "top 78%",
          once: true,
        },
      });

      // Thesis fade
      gsap.from(".problem-thesis", {
        y: 20,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
        scrollTrigger: {
          trigger: ".problem-thesis",
          start: "top 88%",
          once: true,
        },
      });
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="problem"
      eyebrow="The real problem"
      title="Marketing breaks when the owner has to remember everything."
      description="RaptorFlow is built for operators who are tired of restarting strategy every week."
      className="bg-[#0f0f0f] border-t border-zinc-900"
      innerClassName=""
    >
      <div ref={sectionRef}>
        {/* Amber underline beneath title */}
        <div className="mb-16 -mt-8">
          <div className="problem-underline h-px bg-amber-500/60 w-24 origin-left" />
        </div>

        {/* Problem cards grid */}
        <div className="problem-card-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {problemCards.map((card, i) => (
            <div
              key={i}
              className="problem-card bg-[#1a1a1a] border border-zinc-800 rounded-2xl p-6 flex flex-col gap-3 hover:border-zinc-700 transition-colors duration-200"
            >
              <div className="w-8 h-8 bg-[#262626] border border-zinc-800 rounded-lg flex items-center justify-center">
                <span className="text-xs font-mono text-amber-500 font-bold">
                  {String(i + 1).padStart(2, "0")}
                </span>
              </div>
              <h3 className="text-base font-semibold text-white">{card.title}</h3>
              <p className="text-sm text-zinc-500 leading-6">{card.body}</p>
            </div>
          ))}
        </div>

        {/* Thesis */}
        <div className="problem-thesis mt-16 pt-10 border-t border-zinc-900">
          <p className="text-2xl md:text-3xl font-semibold text-zinc-300 max-w-3xl leading-snug">
            The issue is not effort.{" "}
            <span className="text-amber-400">
              The issue is missing memory.
            </span>
          </p>
          <p className="mt-4 text-sm text-zinc-500 font-mono uppercase tracking-widest">
            You are not lazy. Your marketing system is leaking context.
          </p>
        </div>
      </div>
    </LandingSection>
  );
}
