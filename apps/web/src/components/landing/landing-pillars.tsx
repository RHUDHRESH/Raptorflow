"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ScrambleTextPlugin } from "gsap/ScrambleTextPlugin";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, ScrambleTextPlugin, DrawSVGPlugin);
}

const competitors = [
  { name: "MenuIQ", activity: "Published 'Zomato pricing guide 2024'", time: "2 days ago" },
  { name: "Pricewell", activity: "Started Google Ads on 'menu management'", time: "4 days ago" },
  { name: "FoodOps", activity: "LinkedIn post: 5k impressions", time: "6 days ago" },
];

function CompetitorCard() {
  return (
    <div className="bg-[#161820] rounded-[14px] border border-[rgba(255,255,255,0.07)] p-5 w-full max-w-[380px]">
      <div className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.25)] mb-4">
        Competitors · Last 7 days
      </div>
      <div className="flex flex-col gap-3">
        {competitors.map((c, i) => (
          <div key={i} className="flex items-start justify-between gap-4">
            <div>
              <div className="text-[13px] font-medium text-white">{c.name}</div>
              <div className="text-[12px] text-[rgba(255,255,255,0.40)]">{c.activity}</div>
            </div>
            <div className="font-[family-name:var(--font-mono)] text-[10px] text-[rgba(255,255,255,0.25)] shrink-0">
              {c.time}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function RecommendationCard() {
  const cardRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".rec-card-text", { opacity: 1 });
      });

      mm.add("(min-width: 0px)", () => {
        gsap.to(".rec-card-text", {
          scrambleText: {
            text: "The keyword 'dynamic menu pricing India' has 890 monthly searches and zero good content ranking for it. Write a 1,200-word explainer. Publish Tuesday. You'll rank in 6 weeks. Your competitor hasn't touched this.",
            chars: "█▓░ ",
            speed: 0.7,
            revealDelay: 0.2,
          },
          duration: 3,
          ease: "none",
          scrollTrigger: { trigger: ".pillar-2", start: "top 60%", once: true },
        });
      });

      return () => mm.revert();
    },
    { scope: cardRef },
  );

  return (
    <div
      ref={cardRef}
      className="bg-[#161820] rounded-[14px] border border-[rgba(255,255,255,0.07)] p-5 w-full max-w-[380px]"
    >
      <div className="font-[family-name:var(--font-mono)] text-[11px] text-[#E85A2C] mb-4">
        Recommended action · Right now
      </div>
      <div className="rec-card-text text-[13px] text-[rgba(255,255,255,0.70)] leading-[1.65] mb-4">
        The keyword 'dynamic menu pricing India' has 890 monthly searches and zero good content
        ranking for it. Write a 1,200-word explainer. Publish Tuesday. You'll rank in 6 weeks. Your
        competitor hasn't touched this.
      </div>
      <div
        className="inline-block font-[family-name:var(--font-mono)] text-[11px] px-3 py-1.5 rounded-[20px]"
        style={{
          background: "rgba(63,166,106,0.12)",
          border: "1px solid rgba(63,166,106,0.25)",
          color: "#3FA66A",
        }}
      >
        Estimated 40–60 organic visits/month at position 3
      </div>
    </div>
  );
}

function GrowthMetricsCard() {
  const cardRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".pillar-growth-path, .counter-value", { opacity: 1 });
      });

      mm.add("(min-width: 0px)", () => {
        gsap.from(".pillar-growth-path", {
          drawSVG: "0%",
          duration: 2.2,
          ease: "power2.inOut",
          scrollTrigger: { trigger: ".pillar-3", start: "top 65%", once: true },
        });

        const counters = [
          { sel: ".counter-coverage", end: 67, suffix: "%" },
          { sel: ".counter-content", end: 24, suffix: "" },
          { sel: ".counter-alerts", end: 340, suffix: "" },
        ];

        counters.forEach((c) => {
          const obj = { val: 0 };
          gsap.to(obj, {
            val: c.end,
            duration: 1.8,
            ease: "power2.out",
            onUpdate: () => {
              const el = document.querySelector(c.sel);
              if (el) el.textContent = Math.floor(obj.val) + c.suffix;
            },
            scrollTrigger: { trigger: ".pillar-3", start: "top 65%", once: true },
          });
        });
      });

      return () => mm.revert();
    },
    { scope: cardRef },
  );

  return (
    <div
      ref={cardRef}
      className="bg-[#161820] rounded-[14px] border border-[rgba(255,255,255,0.07)] p-5 w-full max-w-[380px]"
    >
      <svg viewBox="0 0 300 120" className="w-full mb-4">
        {/* X-axis labels */}
        {["M1", "M2", "M3", "M4", "M5", "M6"].map((label, i) => (
          <text
            key={label}
            x={i * 50 + 10}
            y="115"
            fill="rgba(255,255,255,0.25)"
            fontSize="10"
            fontFamily="var(--font-mono)"
          >
            {label}
          </text>
        ))}

        {/* Growth line */}
        <path
          className="pillar-growth-path"
          d="M10,100 C60,95 110,80 160,60 S210,30 260,15"
          fill="none"
          stroke="#E85A2C"
          strokeWidth="2"
        />
      </svg>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[10px] text-[rgba(255,255,255,0.35)] mb-1">
            Market coverage
          </div>
          <div className="counter-coverage text-[24px] font-bold text-white">0%</div>
        </div>
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[10px] text-[rgba(255,255,255,0.35)] mb-1">
            Content indexed
          </div>
          <div className="counter-content text-[24px] font-bold text-white">0</div>
        </div>
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[10px] text-[rgba(255,255,255,0.35)] mb-1">
            Competitive alerts
          </div>
          <div className="counter-alerts text-[24px] font-bold text-white">0</div>
        </div>
      </div>
    </div>
  );
}

export function LandingPillars() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".pillar-block", { opacity: 1, y: 0 });
      });

      mm.add("(min-width: 0px)", () => {
        gsap.utils.toArray<HTMLElement>(".pillar-block").forEach((el) => {
          gsap.from(el, {
            y: 60,
            opacity: 0,
            duration: 0.8,
            ease: "power2.out",
            scrollTrigger: { trigger: el, start: "top 70%", once: true },
          });
        });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  const pillars = [
    {
      overline: "01",
      title: "It sees everything.",
      body: "Every competitor move. Every keyword your buyers search. Every content angle your market hasn't covered yet. One briefing, every morning.",
      visual: <CompetitorCard />,
      reversed: false,
    },
    {
      overline: "02",
      title: "It thinks for your business.",
      body: "Not generic tips from a chatbot. Specific, actionable recommendations based on your market, your competitors, your positioning. The kind of thinking you'd pay a senior consultant ₹2L a month for.",
      visual: <RecommendationCard />,
      reversed: true,
      className: "pillar-2",
    },
    {
      overline: "03",
      title: "It never stops learning.",
      body: "The longer it runs, the better it understands your market, your buyers, your seasonality. Day 90 is sharper than day 30. Month 6 is a different product than month 1. That's not a feature. That's the whole point.",
      visual: <GrowthMetricsCard />,
      reversed: false,
      className: "pillar-3",
    },
  ];

  return (
    <section ref={containerRef} className="relative bg-[#0E0F13] py-[120px] lg:py-[120px]">
      <div className="mx-auto max-w-[1200px] px-6 lg:px-12">
        <h2 className="text-[30px] lg:text-[48px] font-extrabold text-white tracking-[-0.03em] text-center mb-24 max-w-[700px] mx-auto leading-[1.1]">
          It sees everything.
          <br />
          It thinks for your business.
          <br />
          It never stops learning.
        </h2>

        <div className="flex flex-col gap-24">
          {pillars.map((pillar, i) => (
            <div
              key={i}
              className={`pillar-block ${pillar.className || ""} grid grid-cols-1 lg:grid-cols-2 gap-12 items-center ${
                pillar.reversed ? "lg:[direction:rtl]" : ""
              }`}
            >
              <div className={`${pillar.reversed ? "lg:[direction:ltr]" : ""}`}>
                <div className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.25)] mb-3">
                  {pillar.overline}
                </div>
                <h3 className="text-[28px] lg:text-[38px] font-bold text-white tracking-[-0.025em] mb-4">
                  {pillar.title}
                </h3>
                <p className="text-[16px] text-[rgba(255,255,255,0.55)] leading-[1.7] max-w-[420px]">
                  {pillar.body}
                </p>
              </div>

              <div
                className={`flex ${
                  pillar.reversed ? "lg:justify-start lg:[direction:ltr]" : "lg:justify-end"
                } justify-center`}
              >
                {pillar.visual}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
