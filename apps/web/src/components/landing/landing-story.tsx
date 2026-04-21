"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { ScrambleTextPlugin } from "gsap/ScrambleTextPlugin";
import { useGSAP } from "@gsap/react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, DrawSVGPlugin, ScrambleTextPlugin);
}

const chaosTabs = [
  { label: "Google Analytics", value: "Last opened: 3 days ago", warning: true },
  { label: "Meta Ads Manager", value: "7 campaigns running", sub: "no idea which work" },
  { label: "Semrush (free tier)", value: "Keyword research incomplete" },
  { label: "Notion marketing doc", value: "Last edited: 6 weeks ago" },
  { label: "LinkedIn drafts", value: "11 unpublished posts" },
];

const sliseIntel = [
  "Your competitor ran 3 sponsored posts about 'Zomato pricing tools' — none got traction",
  "The keyword 'dynamic menu pricing India' has 890 monthly searches, zero good content",
  "Two cloud kitchen chains in Pune just raised funding — they'll need this soon",
];

function ChaosDashboard() {
  return (
    <div className="bg-[#161820] rounded-2xl border border-[rgba(255,255,255,0.07)] p-6 w-full max-w-[400px]">
      <div className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.30)] mb-4">
        Arjun's tabs right now
      </div>
      {chaosTabs.map((tab, i) => (
        <div
          key={i}
          className="flex justify-between items-center py-2.5 border-b border-[rgba(255,255,255,0.05)]"
        >
          <span className="text-[13px] text-[rgba(255,255,255,0.70)]">{tab.label}</span>
          <div className="text-right">
            <span className="text-[12px] font-[family-name:var(--font-mono)] text-[rgba(255,255,255,0.35)]">
              {tab.value}
            </span>
            {tab.sub && (
              <span className="block text-[10px] font-[family-name:var(--font-mono)] text-[#E85A2C]">
                {tab.sub}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function BriefingCardSlise() {
  return (
    <div className="bg-[#161820] rounded-2xl border border-[rgba(255,255,255,0.07)] p-6 w-full max-w-[400px]">
      <div className="font-[family-name:var(--font-mono)] text-[11px] text-[#3FA66A] mb-3">
        Good morning, Arjun — Wednesday, 8:04 AM
      </div>
      <div className="text-[15px] font-semibold text-white tracking-tight mb-4">
        Slise · Your market this week
      </div>
      <div className="flex flex-col gap-3">
        {sliseIntel.map((text, i) => (
          <div key={i} className="flex gap-2.5 items-start">
            <div className="w-[5px] h-[5px] rounded-full bg-[#E85A2C] shrink-0 mt-[5px]" />
            <div
              id={`slise-intel-${i}`}
              className="text-[12.5px] leading-[1.55] text-[rgba(255,255,255,0.60)]"
            >
              {text}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 font-[family-name:var(--font-mono)] text-[11px] text-[#E85A2C]">
        Your move: publish the Swiggy commission explainer first. →
      </div>
    </div>
  );
}

function GrowthChart() {
  return (
    <div className="bg-[#161820] rounded-2xl border border-[rgba(255,255,255,0.07)] p-6 w-full max-w-[400px]">
      <div className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.30)] mb-4">
        Slise · Organic visibility growth
      </div>

      <svg viewBox="0 0 340 160" className="w-full">
        {/* Grid lines */}
        {[0, 1, 2, 3].map((i) => (
          <line
            key={i}
            x1="0"
            y1={40 + i * 30}
            x2="340"
            y2={40 + i * 30}
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="0.5"
          />
        ))}

        {/* Area fill */}
        <path d="M0,140 Q85,130 170,90 T340,30 L340,160 L0,160 Z" fill="rgba(232,90,44,0.08)" />

        {/* Growth line */}
        <path
          className="growth-path"
          d="M0,140 Q85,130 170,90 T340,30"
          fill="none"
          stroke="#E85A2C"
          strokeWidth="2"
        />

        {/* Month labels */}
        {["Mo 1", "Mo 2", "Mo 3"].map((label, i) => (
          <text
            key={label}
            x={i * 170}
            y="155"
            fill="rgba(255,255,255,0.25)"
            fontSize="10"
            fontFamily="var(--font-mono)"
          >
            {label}
          </text>
        ))}
      </svg>

      <div className="flex items-center gap-3 mt-4 font-[family-name:var(--font-mono)] text-[11px] text-[#3FA66A]">
        <span>↑ 340% organic reach</span>
        <span className="text-[rgba(255,255,255,0.20)]">·</span>
        <span>12 pieces published</span>
        <span className="text-[rgba(255,255,255,0.20)]">·</span>
        <span>2 inbound demos</span>
      </div>
    </div>
  );
}

export function LandingStory() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".story-panel", { opacity: 1 });
      });

      mm.add("(min-width: 1024px)", () => {
        const panels = gsap.utils.toArray<HTMLElement>(".story-panel");
        const totalWidth = panels.length * window.innerWidth;

        const scrollTween = gsap.to(".story-panels-inner", {
          x: -(totalWidth - window.innerWidth),
          ease: "none",
          scrollTrigger: {
            trigger: ".story-section",
            pin: true,
            scrub: 1,
            end: () => "+=" + (totalWidth - window.innerWidth),
            invalidateOnRefresh: true,
            snap: {
              snapTo: 1 / (panels.length - 1),
              duration: 0.4,
              ease: "power1.inOut",
            },
          },
        });

        // Typewriter on panel 2
        sliseIntel.forEach((text, i) => {
          gsap.to(`#slise-intel-${i}`, {
            scrambleText: {
              text,
              chars: "█▓░ ",
              speed: 0.8,
            },
            duration: 1.8,
            ease: "none",
            scrollTrigger: {
              trigger: ".story-panel-2",
              containerAnimation: scrollTween,
              start: "left center",
              once: true,
            },
          });
        });

        // DrawSVG on growth chart
        gsap.from(".growth-path", {
          drawSVG: "0%",
          duration: 2,
          ease: "power2.inOut",
          scrollTrigger: {
            trigger: ".story-panel-3",
            containerAnimation: scrollTween,
            start: "left 60%",
            once: true,
          },
        });
      });

      mm.add("(max-width: 1023px)", () => {
        gsap.utils.toArray<HTMLElement>(".story-panel").forEach((panel) => {
          gsap.from(panel, {
            y: 40,
            opacity: 0,
            duration: 0.7,
            ease: "power2.out",
            scrollTrigger: { trigger: panel, start: "top 75%", once: true },
          });
        });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  const panels = [
    {
      step: "01 / 03",
      title: (
        <>
          Arjun built Slise. 34 customers. Zero churn.
          <br />
          And nobody outside those 34 had ever heard of it.
        </>
      ),
      body: "His competitor — funded, worse product, better brand — kept showing up when restaurant owners Googled the problem. Arjun wrote one LinkedIn post a month and felt vaguely humiliated by it. His website explained the features correctly and the value not at all.",
      visual: <ChaosDashboard />,
      className: "story-panel-1",
    },
    {
      step: "02 / 03",
      title: (
        <>
          He connected everything on Monday.
          <br />
          By Wednesday morning, he had his first briefing.
        </>
      ),
      body: "Not a dashboard. Not a report. A briefing — written for him, about his market, with three specific things to do today. The kind of thing a senior marketing hire would produce after a week of onboarding. Except it was day two.",
      visual: <BriefingCardSlise />,
      className: "story-panel-2",
    },
    {
      step: "03 / 03",
      title: (
        <>
          By month three, Slise had a marketing system
          <br />
          that ran whether Arjun had a good week or not.
        </>
      ),
      body: "Content going out. Competitors monitored. Pipeline moving. Arjun was building the product. RaptorFlow was building the audience. That's the division of labour that lets a two-person company punch like a ten-person one.",
      visual: <GrowthChart />,
      className: "story-panel-3",
    },
  ];

  return (
    <section ref={containerRef} className="story-section relative bg-[#0E0F13] overflow-hidden">
      {/* Desktop: horizontal scroll */}
      <div className="hidden lg:block">
        <div className="story-panels-inner flex">
          {panels.map((panel, i) => (
            <div
              key={i}
              className={`story-panel ${panel.className} w-screen min-h-[100dvh] flex-shrink-0 flex items-center px-12`}
            >
              <div className="mx-auto max-w-[1200px] w-full grid grid-cols-2 gap-16 items-center">
                <div>
                  <div className="flex items-center gap-4 mb-4">
                    <span className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.30)]">
                      ARJUN · SLISE · BANGALORE
                    </span>
                    <div className="flex gap-2">
                      {[0, 1, 2].map((dot) => (
                        <div
                          key={dot}
                          className={`w-1.5 h-1.5 rounded-full ${
                            dot === i ? "bg-white" : "bg-[rgba(255,255,255,0.20)]"
                          }`}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.30)] mb-4">
                    {panel.step}
                  </div>

                  <h3 className="text-[36px] font-bold text-white tracking-[-0.025em] leading-[1.15] max-w-[520px] mb-6">
                    {panel.title}
                  </h3>

                  <p className="text-[16px] text-[rgba(255,255,255,0.55)] leading-[1.7] max-w-[480px]">
                    {panel.body}
                  </p>
                </div>

                <div className="flex justify-end">{panel.visual}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mobile: vertical stack */}
      <div className="lg:hidden py-[72px]">
        <div className="mx-auto max-w-[1200px] px-6">
          {panels.map((panel, i) => (
            <div key={i} className={`story-panel ${panel.className} mb-16 last:mb-0`}>
              <div className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.30)] mb-4">
                ARJUN · SLISE · BANGALORE
              </div>

              <div className="font-[family-name:var(--font-mono)] text-[11px] text-[rgba(255,255,255,0.30)] mb-4">
                {panel.step}
              </div>

              <h3 className="text-[28px] font-bold text-white tracking-[-0.025em] leading-[1.15] mb-4">
                {panel.title}
              </h3>

              <p className="text-[15px] text-[rgba(255,255,255,0.55)] leading-[1.7] mb-8">
                {panel.body}
              </p>

              <div className="flex justify-center">{panel.visual}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
