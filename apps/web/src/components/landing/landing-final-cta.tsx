"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, SplitText);
}

export function LandingFinalCTA() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".final-h2, .final-sub, .final-cta-group", { opacity: 1, y: 0 });
      });

      mm.add("(min-width: 0px)", () => {
        SplitText.create(".final-h2", {
          type: "lines",
          mask: "lines",
          autoSplit: true,
          onSplit(self) {
            gsap.from(self.lines, {
              yPercent: 110,
              duration: 0.8,
              stagger: 0.12,
              ease: "power3.out",
              scrollTrigger: { trigger: ".final-section", start: "top 70%", once: true },
            });
          },
        });

        gsap.from(".final-sub", {
          y: 20,
          opacity: 0,
          duration: 0.7,
          delay: 0.4,
          ease: "power2.out",
          scrollTrigger: { trigger: ".final-section", start: "top 70%", once: true },
        });

        gsap.from(".final-cta-group", {
          y: 20,
          opacity: 0,
          duration: 0.7,
          delay: 0.6,
          ease: "power2.out",
          scrollTrigger: { trigger: ".final-section", start: "top 70%", once: true },
        });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  return (
    <section
      ref={containerRef}
      className="final-section relative bg-[#0E0F13] py-[120px] lg:py-[160px]"
    >
      <div className="mx-auto max-w-[800px] px-6 lg:px-12 text-center">
        <h2 className="final-h2 text-[36px] lg:text-[56px] font-extrabold text-white tracking-[-0.035em] leading-[1.06] mb-7">
          The product exists.
          <br />
          The market needs it.
          <br />
          Now they need to find it.
        </h2>

        <p className="final-sub text-[18px] text-[rgba(255,255,255,0.50)] leading-[1.65] max-w-[560px] mx-auto mb-12">
          Your competitor is not smarter than you. They just showed up more consistently. RaptorFlow
          is the system that makes consistency automatic.
        </p>

        <div className="final-cta-group">
          <a href="/sign-up" className="btn-primary text-[16px] px-10 py-4 inline-flex">
            Start now — ₹5,000/month
          </a>

          <p className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.30)] mt-4">
            2-week 100% cashback · No contracts · raptorflow.in
          </p>
        </div>
      </div>
    </section>
  );
}
