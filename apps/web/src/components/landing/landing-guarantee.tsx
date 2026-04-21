"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingGuarantee() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".guarantee-content", { opacity: 1, y: 0 });
      });

      mm.add("(min-width: 0px)", () => {
        gsap.from(".guarantee-content", {
          y: 40,
          opacity: 0,
          duration: 0.8,
          ease: "power2.out",
          scrollTrigger: { trigger: ".guarantee-section", start: "top 70%", once: true },
        });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  return (
    <section
      ref={containerRef}
      className="guarantee-section relative bg-[#0E0F13] py-[120px] lg:py-[120px]"
    >
      <div className="guarantee-content mx-auto max-w-[760px] px-6 lg:px-12 text-center">
        <div className="font-[family-name:var(--font-mono)] text-[10.5px] tracking-[0.12em] uppercase text-[rgba(255,255,255,0.30)] mb-5">
          THE GUARANTEE
        </div>

        <h2 className="text-[30px] lg:text-[48px] font-extrabold text-white tracking-[-0.03em] leading-[1.1] mb-6">
          If it doesn't feel worth it in two weeks,
          <br />
          you get every rupee back.
        </h2>

        <p className="text-[18px] text-[rgba(255,255,255,0.55)] leading-[1.7] max-w-[600px] mx-auto">
          No questions. No 'tell us why you're leaving'. No retention call. If you spend two weeks
          with RaptorFlow and don't feel like your marketing finally has a brain, 100% cashback.
          That's how confident we are in the first briefing alone.
        </p>

        <div className="flex flex-wrap justify-center gap-4 mt-10">
          {[
            { big: "100%", small: "cashback if unsatisfied" },
            { big: "0", small: "contracts or lock-ins" },
            { big: "14 days", small: "to see real value" },
          ].map((chip, i) => (
            <div
              key={i}
              className="bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.10)] rounded-lg px-6 py-4 text-center"
            >
              <div className="text-[28px] font-bold text-white">{chip.big}</div>
              <div className="font-[family-name:var(--font-mono)] text-[12px] text-[rgba(255,255,255,0.40)]">
                {chip.small}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
