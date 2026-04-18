"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { campaignSteps } from "@/lib/landing-copy";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingCampaigns() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Step nodes stagger in
      gsap.from(".campaign-step", {
        y: 36,
        opacity: 0,
        duration: 0.7,
        stagger: 0.12,
        ease: "power3.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 78%",
          once: true,
        },
      });

      // Connector lines draw left to right
      gsap.fromTo(
        ".campaign-connector",
        { scaleX: 0 },
        {
          scaleX: 1,
          transformOrigin: "left center",
          duration: 1,
          ease: "power2.inOut",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 75%",
            once: true,
          },
        }
      );

      // Last node glows amber
      gsap.to(".campaign-final-node", {
        boxShadow: "0 0 32px rgba(245,158,11,0.5)",
        borderColor: "rgba(245,158,11,0.9)",
        duration: 1.5,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        delay: 0.8,
      });
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="campaigns"
      eyebrow="Campaign execution"
      title="Campaigns become living systems, not forgotten plans."
      description="RaptorFlow turns a goal into moves, tasks, content actions, performance checks, and response loops."
      className="bg-[#121212] border-t border-zinc-900"
    >
      <div ref={sectionRef}>

        {/* Horizontal timeline */}
        <div className="relative">
          {/* Connector line behind nodes */}
          <div className="hidden lg:flex absolute top-[52px] left-[6%] right-[6%] items-center">
            <div className="campaign-connector h-px bg-amber-500/25 flex-1 origin-left" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {campaignSteps.map((step, i) => {
              const isLast = i === campaignSteps.length - 1;
              return (
                <div key={i} className="campaign-step flex flex-col items-start gap-4">
                  {/* Node */}
                  <div
                    className={`campaign-node w-10 h-10 rounded-full border flex items-center justify-center text-xs font-mono font-bold transition-all ${
                      isLast
                        ? "campaign-final-node border-amber-500 bg-amber-500/10 text-amber-500"
                        : "border-zinc-700 bg-[#1a1a1a] text-zinc-500"
                    }`}
                  >
                    {step.step}
                  </div>

                  {/* Card */}
                  <div
                    className={`w-full bg-[#1a1a1a] border rounded-2xl p-6 hover:border-zinc-700 transition-colors duration-200 ${
                      isLast ? "border-amber-500/30" : "border-zinc-800"
                    }`}
                  >
                    <h3
                      className={`text-base font-semibold mb-3 ${
                        isLast ? "text-amber-400" : "text-white"
                      }`}
                    >
                      {step.title}
                    </h3>
                    <p className="text-sm text-zinc-500 leading-6">{step.body}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Summary line */}
        <div className="mt-14 pt-10 border-t border-zinc-900">
          <p className="text-sm font-mono text-zinc-600 uppercase tracking-widest">
            Goal → Move → Task → Signal → Replan. The cycle never stops.
          </p>
        </div>
      </div>
    </LandingSection>
  );
}
