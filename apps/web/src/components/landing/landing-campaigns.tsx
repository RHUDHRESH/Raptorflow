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
        boxShadow: "0 0 32px rgba(217,119,87,0.5)",
        borderColor: "rgba(217,119,87,0.9)",
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
      className="bg-[#FBF8F2] border-t border-[#E5DED4]"
    >
      <div ref={sectionRef}>

        {/* Horizontal timeline */}
        <div className="relative">
          {/* Connector line behind nodes */}
          <div className="hidden lg:flex absolute top-[52px] left-[6%] right-[6%] items-center">
            <div className="campaign-connector h-px bg-[#D97757]/25 flex-1 origin-left" />
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
                        ? "campaign-final-node border-[#D97757] bg-[#FBE9DE] text-[#D97757]"
                        : "border-[#D5CBC0] bg-white text-[#9A948C]"
                    }`}
                  >
                    {step.step}
                  </div>

                  {/* Card */}
                  <div
                    className={`w-full bg-white border rounded-2xl p-6 hover:border-[#D5CBC0] transition-colors duration-200 ${
                      isLast ? "border-[#D97757]/30" : "border-[#E5DED4]"
                    }`}
                  >
                    <h3
                      className={`text-base font-semibold mb-3 ${
                        isLast ? "text-[#D97757]" : "text-[#2A2622]"
                      }`}
                    >
                      {step.title}
                    </h3>
                    <p className="text-sm text-[#6B655E] leading-6">{step.body}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Summary line */}
        <div className="mt-14 pt-10 border-t border-[#E5DED4]">
          <p className="text-sm font-mono text-[#9A948C] uppercase tracking-widest">
            Goal → Move → Task → Signal → Replan. The cycle never stops.
          </p>
        </div>
      </div>
    </LandingSection>
  );
}
