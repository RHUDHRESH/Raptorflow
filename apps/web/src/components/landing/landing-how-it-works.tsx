"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, DrawSVGPlugin);
}

const steps = [
  {
    num: "01",
    title: "Tell us about your business",
    body: "21 focused screens. Your product, your customer, your competitors, your market. Takes 20 minutes. The system never asks again.",
  },
  {
    num: "02",
    title: "Your team goes to work",
    body: "Immediately. Not 'within 24 hours'. Right now. Researching your competitors, identifying your content angles, building your first briefing.",
  },
  {
    num: "03",
    title: "Wake up to a briefing",
    body: "Every morning: what happened in your market, what your competitors did, what to do today. Every week: campaigns. Every month: sharper than the last.",
  },
];

export function LandingHowItWorks() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".step-card, .connector-line", { opacity: 1, y: 0 });
      });

      mm.add("(min-width: 1024px)", () => {
        gsap.from(".connector-line", {
          drawSVG: "0%",
          duration: 1.0,
          stagger: 0.3,
          ease: "power2.inOut",
          scrollTrigger: { trigger: ".steps-section", start: "top 60%", once: true },
        });

        gsap.from(".step-card", {
          y: 40,
          opacity: 0,
          stagger: 0.15,
          duration: 0.7,
          ease: "power2.out",
          scrollTrigger: { trigger: ".steps-section", start: "top 65%", once: true },
        });
      });

      mm.add("(max-width: 1023px)", () => {
        gsap.from(".step-card", {
          y: 30,
          opacity: 0,
          stagger: 0.1,
          duration: 0.6,
          ease: "power2.out",
          scrollTrigger: { trigger: ".steps-section", start: "top 65%", once: true },
        });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  return (
    <section
      ref={containerRef}
      id="how-it-works"
      className="steps-section relative bg-[#F7F4EE] py-[120px] lg:py-[120px]"
    >
      <div className="mx-auto max-w-[1200px] px-6 lg:px-12">
        <div className="text-center mb-20">
          <div className="font-[family-name:var(--font-mono)] text-[10.5px] tracking-[0.12em] uppercase text-[#E85A2C] mb-5">
            THE PLAN
          </div>

          <h2 className="text-[30px] lg:text-[52px] font-extrabold text-[#13141A] tracking-[-0.03em] leading-[1.1] max-w-[680px] mx-auto mb-4">
            Live in one day.
            <br />
            Compounding from week one.
          </h2>

          <p className="text-[17px] text-[#6B6D78] leading-[1.65] max-w-[520px] mx-auto">
            Three steps. No meetings, no onboarding calls, no agency contracts.
          </p>
        </div>

        {/* Steps grid */}
        <div className="relative grid grid-cols-1 lg:grid-cols-3 gap-8 lg:gap-0">
          {steps.map((step, i) => (
            <React.Fragment key={i}>
              <div className="step-card relative px-4 lg:px-8">
                <div className="font-[family-name:var(--font-mono)] text-[48px] font-medium text-[rgba(19,20,26,0.08)] leading-none mb-5">
                  {step.num}
                </div>
                <h3 className="text-[22px] font-bold text-[#13141A] tracking-[-0.02em] mb-3">
                  {step.title}
                </h3>
                <p className="text-[15px] text-[#6B6D78] leading-[1.65]">{step.body}</p>
              </div>

              {/* Connector line between steps */}
              {i < steps.length - 1 && (
                <div className="hidden lg:flex items-center justify-center relative">
                  <svg width="60" height="2" className="absolute top-[60px]">
                    <line
                      className="connector-line"
                      x1="0"
                      y1="1"
                      x2="60"
                      y2="1"
                      stroke="#E85A2C"
                      strokeWidth="1.5"
                      strokeDasharray="4 4"
                    />
                  </svg>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
}
