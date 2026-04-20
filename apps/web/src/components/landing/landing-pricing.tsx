"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { LandingSection } from "./landing-section";
import { usePrefersReducedMotion } from "./landing-gsap-provider";
import { pricingPlans } from "@/lib/landing-copy";
import { CheckIcon } from "@radix-ui/react-icons";
import { referralSignupHref } from "@/lib/referrals";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export function LandingPricing() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const reducedMotion = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;

      // Plan cards stagger upward
      gsap.from(".pricing-card", {
        y: 48,
        opacity: 0,
        duration: 0.8,
        stagger: 0.12,
        ease: "power3.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 78%",
          once: true,
        },
      });

      // Features reveal inside cards
      gsap.from(".pricing-feature", {
        x: -12,
        opacity: 0,
        duration: 0.4,
        stagger: 0.04,
        delay: 0.5,
        ease: "power2.out",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top 75%",
          once: true,
        },
      });
    },
    { scope: sectionRef }
  );

  return (
    <LandingSection
      id="pricing"
      eyebrow="Pricing"
      title="Pricing built for Indian SMBs."
      description="No fake free tier. No agency retainer shock. Choose the operating level your business needs."
      centered
      className="bg-[#FBF8F2] border-t border-[#E5DED4]"
    >
      <div ref={sectionRef} className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
        {pricingPlans.map((plan, i) => (
          <div
            key={i}
            className={`pricing-card relative flex flex-col rounded-2xl border p-8 ${
              plan.featured
                ? "border-[#D97757]/60 bg-white shadow-[0_0_48px_rgba(217,119,87,0.12)]"
                : "border-[#E5DED4] bg-white"
            }`}
          >
            {plan.featured && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <div className="bg-[#D97757] text-[#2A2622] text-[10px] font-bold uppercase tracking-[0.2em] px-4 py-1">
                  Recommended
                </div>
              </div>
            )}

            <div className="mb-6">
              <p className="text-xs font-mono text-[#9A948C] uppercase tracking-widest mb-2">
                {plan.name}
              </p>
              <div className="flex items-end gap-1 mb-3">
                <span className={`text-4xl font-semibold ${plan.featured ? "text-[#D97757]" : "text-[#2A2622]"}`}>
                  {plan.price}
                </span>
                <span className="text-[#9A948C] text-sm mb-1">{plan.cadence}</span>
              </div>
              <p className="text-sm text-[#6B655E] leading-6">{plan.line}</p>
            </div>

            <div className="flex-1 flex flex-col gap-3 mb-8">
              {plan.features.map((feature, j) => (
                <div key={j} className="pricing-feature flex items-start gap-3">
                  <CheckIcon
                    className={`w-4 h-4 mt-0.5 shrink-0 ${plan.featured ? "text-[#D97757]" : "text-[#9A948C]"}`}
                  />
                  <span className="text-sm text-[#6B655E]">{feature}</span>
                </div>
              ))}
            </div>

            <a
              href={referralSignupHref(plan.referralCode)}
              className={`w-full text-center py-3 text-sm font-semibold transition-colors duration-200 ${
                plan.featured
                  ? "bg-[#D97757] text-[#2A2622] hover:bg-[#C46A4D]"
                  : "border border-[#E5DED4] text-[#6B655E] hover:bg-[#F5F0E8] hover:border-[#D5CBC0]"
              }`}
            >
              {plan.cta}
            </a>
          </div>
        ))}
      </div>

      <p className="mt-10 text-xs font-mono text-[#BAB0A0] uppercase tracking-widest text-center">
        All plans include Foundation setup · No credit card required to start
      </p>
    </LandingSection>
  );
}
