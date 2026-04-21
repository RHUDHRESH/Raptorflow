"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import { ScrambleTextPlugin } from "gsap/ScrambleTextPlugin";
import { useGSAP } from "@gsap/react";
import { HeroMesh } from "./hero-mesh";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, SplitText, ScrambleTextPlugin);
}

function BriefingCard() {
  const cardRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".intel-line", { opacity: 1 });
      });

      mm.add("(min-width: 0px)", () => {
        const lines = [
          {
            id: "#intel-0",
            text: "MenuIQ ran 4 Google ads targeting 'menu pricing Zomato India' this week",
          },
          {
            id: "#intel-1",
            text: "3 cloud kitchen operators searched for dynamic pricing tools in the last 24h",
          },
          { id: "#intel-2", text: "Your best content angle: how Swiggy commission actually works" },
        ];

        lines.forEach((line, i) => {
          gsap.to(line.id, {
            duration: 1.6,
            scrambleText: {
              text: line.text,
              chars: "█▓░▒ ",
              revealDelay: 0.2,
              speed: 0.8,
            },
            delay: 1.2 + i * 1.0,
            ease: "none",
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
      className="briefing-card relative w-full max-w-[480px] rounded-[20px] border border-[rgba(255,255,255,0.07)] bg-[#0E0F13] p-7 overflow-hidden"
    >
      <div className="shimmer-line absolute top-0 left-0 right-0 h-px" />

      <div className="font-[family-name:var(--font-mono)] text-[11px] tracking-wide text-[#3FA66A]">
        Good morning, Arjun — Tuesday, 8:04 AM
      </div>

      <div className="h-px bg-[rgba(255,255,255,0.07)] my-3.5" />

      <div className="text-[15px] font-semibold text-white tracking-tight mb-3">
        Your market. Right now.
      </div>

      <div className="flex flex-col gap-3">
        {[
          "MenuIQ ran 4 Google ads targeting 'menu pricing Zomato India' this week",
          "3 cloud kitchen operators searched for dynamic pricing tools in the last 24h",
          "Your best content angle: how Swiggy commission actually works",
        ].map((text, i) => (
          <div key={i} className="flex gap-2.5 items-start">
            <div className="w-[5px] h-[5px] rounded-full bg-[#E85A2C] shrink-0 mt-[5px]" />
            <div
              id={`intel-${i}`}
              className="intel-line text-[12.5px] leading-[1.55] text-[rgba(255,255,255,0.60)]"
            >
              {text}
            </div>
          </div>
        ))}
      </div>

      <div className="h-px bg-[rgba(255,255,255,0.07)] my-4" />

      <div className="font-[family-name:var(--font-mono)] text-[11px] tracking-wide text-[#E85A2C]">
        3 actions ready for you today →
      </div>

      <div className="flex flex-wrap gap-2 mt-4">
        {["Content", "SEO", "Competitive intel"].map((tag) => (
          <span
            key={tag}
            className="font-[family-name:var(--font-mono)] text-[10px] px-2.5 py-1 rounded-[20px] border border-[rgba(255,255,255,0.10)] text-[rgba(255,255,255,0.40)]"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}

export function LandingHero() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".hero-h1, .hero-eyebrow, .hero-sub, .hero-cta-row, .hero-trust, .briefing-card", {
          opacity: 1,
          y: 0,
          x: 0,
        });
      });

      mm.add("(min-width: 0px)", () => {
        document.fonts.ready.then(() => ScrollTrigger.refresh());

        const split = SplitText.create(".hero-h1", {
          type: "lines",
          mask: "lines",
          autoSplit: true,
          onSplit(self) {
            gsap.from(self.lines, {
              yPercent: 110,
              duration: 0.85,
              stagger: 0.1,
              ease: "power3.out",
              delay: 0.1,
            });
          },
        });

        gsap.from([".hero-eyebrow", ".hero-sub", ".hero-cta-row", ".hero-trust"], {
          y: 20,
          opacity: 0,
          duration: 0.7,
          stagger: 0.1,
          ease: "power2.out",
          delay: 0.5,
        });

        gsap.from(".briefing-card", {
          x: 50,
          opacity: 0,
          duration: 1.0,
          ease: "power3.out",
          delay: 0.25,
        });

        gsap
          .timeline({
            scrollTrigger: {
              trigger: ".hero-section",
              start: "top top",
              end: "+=60%",
              scrub: 1.5,
            },
          })
          .to(".hero-left", { y: -50, opacity: 0, ease: "none" }, 0)
          .to(".briefing-card", { y: -15, ease: "none" }, 0);

        return () => {
          split.revert();
        };
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  return (
    <section
      ref={containerRef}
      className="hero-section relative min-h-[100dvh] flex items-center bg-[#F7F4EE] overflow-hidden"
      style={{ paddingTop: 80, paddingBottom: 100 }}
    >
      <HeroMesh />

      <div className="relative z-10 mx-auto max-w-[1200px] px-6 lg:px-12 grid grid-cols-1 lg:grid-cols-[55%_45%] gap-16 items-center w-full">
        {/* LEFT COLUMN */}
        <div className="hero-left flex flex-col">
          <div className="hero-eyebrow font-[family-name:var(--font-mono)] uppercase tracking-[0.12em] text-[10.5px] text-[#E85A2C] mb-6">
            RAPTORFLOW.IN · MARKETING FOR B2B SAAS FOUNDERS
          </div>

          <h1 className="hero-h1 text-[38px] lg:text-[68px] font-extrabold tracking-[-0.035em] leading-[1.05]">
            <span className="block text-[#13141A]">Your product deserves</span>
            <span className="block text-[#E85A2C]">to be found.</span>
          </h1>

          <p className="hero-sub text-[17px] text-[#6B6D78] max-w-[480px] leading-[1.7] mt-7">
            RaptorFlow is a team of 21 AI marketing specialists that works on your B2B SaaS every
            single day. Morning briefings. Weekly campaigns. A system that gets sharper as it learns
            your market.
          </p>

          <div className="hero-cta-row flex flex-wrap items-center gap-4 mt-10">
            <a href="/sign-up" className="btn-primary">
              Start now — ₹5,000/month
            </a>
            <a
              href="#how-it-works"
              className="text-[14px] font-medium text-[#6B6D78] hover:text-[#13141A] transition-colors"
            >
              See how it works ↓
            </a>
          </div>

          <p className="hero-trust font-[family-name:var(--font-mono)] text-[11px] text-[#6B6D78] tracking-[0.04em] mt-3.5">
            2-week 100% cashback · No contracts · Pay via UPI or card
          </p>
        </div>

        {/* RIGHT COLUMN */}
        <div className="hidden lg:flex justify-end">
          <BriefingCard />
        </div>
      </div>
    </section>
  );
}
