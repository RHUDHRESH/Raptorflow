"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { Check } from "lucide-react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const features = [
  "21 AI specialists working on your business daily",
  "Morning briefings: your market, your competitors, your actions",
  "Weekly campaigns and content recommendations",
  "Competitor monitoring across web, ads, and social",
  "Positioning and messaging help built-in",
  "2-week 100% cashback — no questions asked",
  "No contracts. Cancel anytime.",
];

const comparisons = [
  { option: "Senior marketing hire", cost: "₹80,000–₹1,50,000" },
  { option: "Boutique agency retainer", cost: "₹40,000–₹1,00,000" },
  { option: "Freelance GTM consultant", cost: "₹20,000–₹50,000" },
  { option: "RaptorFlow", cost: "₹5,000", highlight: true },
];

export function LandingPricing() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".pricing-card, .feature-item, .price-number", { opacity: 1, x: 0 });
      });

      mm.add("(min-width: 0px)", () => {
        // Price counter animation
        const obj = { val: 0 };
        gsap.to(obj, {
          val: 5000,
          duration: 1.5,
          ease: "power2.out",
          onUpdate: () => {
            const el = document.querySelector(".price-number");
            if (el) {
              el.textContent = "₹" + Math.floor(obj.val).toLocaleString("en-IN");
            }
          },
          scrollTrigger: { trigger: ".pricing-section", start: "top 65%", once: true },
        });

        gsap.from(".feature-item", {
          x: -20,
          opacity: 0,
          stagger: 0.08,
          duration: 0.5,
          ease: "power2.out",
          scrollTrigger: { trigger: ".pricing-card", start: "top 65%", once: true },
        });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  return (
    <section
      ref={containerRef}
      className="pricing-section relative bg-[#F7F4EE] py-[120px] lg:py-[120px]"
    >
      <div className="mx-auto max-w-[1200px] px-6 lg:px-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
          {/* LEFT — Pricing card */}
          <div className="pricing-card bg-[#0E0F13] rounded-[20px] border border-[rgba(255,255,255,0.08)] p-10 lg:p-11">
            <div className="flex items-baseline gap-1">
              <span className="price-number text-[64px] font-extrabold text-white tracking-[-0.04em]">
                ₹0
              </span>
              <span className="text-[18px] text-[rgba(255,255,255,0.40)]">/month</span>
            </div>

            <div className="h-px bg-[rgba(255,255,255,0.07)] my-6" />

            <div className="flex flex-col">
              {features.map((feature, i) => (
                <div
                  key={i}
                  className="feature-item flex items-start gap-3 py-2.5 border-b border-[rgba(255,255,255,0.05)]"
                >
                  <Check className="w-4 h-4 text-[#3FA66A] shrink-0 mt-0.5" />
                  <span className="text-[14px] text-[rgba(255,255,255,0.70)]">{feature}</span>
                </div>
              ))}
            </div>

            <a
              href="/sign-up"
              className="btn-primary w-full mt-8 text-center justify-center inline-flex"
            >
              Start now — ₹5,000/month
            </a>

            <p className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.30)] text-center mt-3.5">
              Pay via UPI · Cards · Net Banking · GST invoice included
            </p>
          </div>

          {/* RIGHT — Comparison */}
          <div className="pt-4">
            <div className="font-[family-name:var(--font-mono)] text-[10.5px] tracking-[0.12em] uppercase text-[#6B6D78] mb-5">
              vs. the alternative
            </div>

            <div className="flex flex-col">
              {/* Header */}
              <div className="grid grid-cols-2 py-3 border-b border-[rgba(19,20,26,0.08)]">
                <span className="font-[family-name:var(--font-mono)] text-[11px] text-[#6B6D78]">
                  Option
                </span>
                <span className="font-[family-name:var(--font-mono)] text-[11px] text-[#6B6D78] text-right">
                  Monthly cost
                </span>
              </div>

              {/* Rows */}
              {comparisons.map((row, i) => (
                <div
                  key={i}
                  className={`grid grid-cols-2 py-3.5 border-b border-[rgba(19,20,26,0.08)] ${
                    row.highlight ? "bg-[rgba(232,90,44,0.07)] -mx-4 px-4 rounded" : ""
                  }`}
                >
                  <span
                    className={`text-[14px] ${
                      row.highlight ? "text-[#E85A2C] font-semibold" : "text-[#13141A]"
                    }`}
                  >
                    {row.option}
                  </span>
                  <span
                    className={`text-[14px] text-right ${
                      row.highlight ? "text-[#E85A2C] font-semibold" : "text-[#6B6D78]"
                    }`}
                  >
                    {row.cost}
                  </span>
                </div>
              ))}
            </div>

            <p className="text-[15px] text-[#6B6D78] mt-6 italic">
              Less than one consultant hour per week.
              <br />
              More than any of the above can actually deliver.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
