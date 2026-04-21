"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { useGSAP } from "@gsap/react";
import { Globe, Search, Camera, MessageCircle, Briefcase, FileText } from "lucide-react";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, DrawSVGPlugin);
}

const channels = [
  { label: "Meta Ads", Icon: Globe },
  { label: "Google Ads", Icon: Search },
  { label: "Instagram", Icon: Camera },
  { label: "WhatsApp", Icon: MessageCircle },
  { label: "LinkedIn", Icon: Briefcase },
  { label: "Content / SEO", Icon: FileText },
];

export function LandingGuide() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".channel-icon, .channel-line", { opacity: 1, scale: 1 });
      });

      mm.add("(min-width: 1024px)", () => {
        gsap.from(".channel-icon", {
          scale: 0,
          opacity: 0,
          stagger: { amount: 0.5, from: "start" },
          ease: "back.out(1.5)",
          duration: 0.6,
          scrollTrigger: { trigger: ".guide-section", start: "top 65%", once: true },
        });

        gsap.from(".channel-line", {
          drawSVG: "0%",
          duration: 1.2,
          stagger: 0.1,
          ease: "power2.inOut",
          scrollTrigger: { trigger: ".guide-section", start: "top 65%", once: true },
        });

        gsap.to(".channels-orbit-group", {
          rotation: 360,
          duration: 30,
          ease: "none",
          repeat: -1,
          transformOrigin: "center center",
        });

        gsap.to(".channel-icon", {
          rotation: -360,
          duration: 30,
          ease: "none",
          repeat: -1,
          transformOrigin: "center center",
        });
      });

      mm.add("(max-width: 1023px)", () => {
        gsap.from(".channel-icon", {
          y: 20,
          opacity: 0,
          stagger: 0.08,
          duration: 0.5,
          ease: "power2.out",
          scrollTrigger: { trigger: ".guide-section", start: "top 65%", once: true },
        });
      });

      return () => mm.revert();
    },
    { scope: containerRef },
  );

  return (
    <section
      ref={containerRef}
      className="guide-section relative bg-[#F7F4EE] py-[120px] lg:py-[120px]"
    >
      <div className="mx-auto max-w-[1200px] px-6 lg:px-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* LEFT — copy */}
          <div>
            <div className="font-[family-name:var(--font-mono)] text-[10.5px] tracking-[0.12em] uppercase text-[#E85A2C] mb-5">
              THE SOLUTION
            </div>

            <h2 className="text-[30px] lg:text-[52px] font-extrabold text-[#13141A] tracking-[-0.03em] mb-4">
              Meet RaptorFlow.
            </h2>

            <div className="flex flex-col gap-5 max-w-[480px]">
              <p className="text-[17px] text-[#6B6D78] leading-[1.7]">
                RaptorFlow is a team of 21 AI marketing specialists — built on the frameworks of the
                people who defined modern marketing — that works on your business every single day.
                Not tools. Not templates. Specialists, working.
              </p>
              <p className="text-[17px] text-[#6B6D78] leading-[1.7]">
                Every morning you get a briefing on your market. Every week, campaigns go out. Every
                month, the system knows your business better than it did the month before. You build
                the product. RaptorFlow builds the audience.
              </p>
            </div>

            <a href="/sign-up" className="btn-primary mt-9 inline-flex">
              Start now — ₹5,000/month
            </a>
          </div>

          {/* RIGHT — orbital channel diagram */}
          <div className="relative w-full max-w-[400px] aspect-square mx-auto hidden lg:block">
            <svg
              className="channels-orbit-group absolute inset-0 w-full h-full"
              viewBox="0 0 400 400"
            >
              <g transform="translate(200, 200)">
                <circle r="40" fill="#0E0F13" stroke="rgba(255,255,255,0.07)" strokeWidth="1" />
                <text
                  x="0"
                  y="4"
                  textAnchor="middle"
                  fill="#E85A2C"
                  fontSize="14"
                  fontWeight="700"
                  fontFamily="var(--font-body)"
                >
                  RF
                </text>
              </g>

              {channels.map((_, i) => {
                const angle = ((i * 60 - 90) * Math.PI) / 180;
                const x2 = 200 + Math.cos(angle) * 160;
                const y2 = 200 + Math.sin(angle) * 160;
                return (
                  <line
                    key={`line-${i}`}
                    className="channel-line"
                    x1="200"
                    y1="200"
                    x2={x2}
                    y2={y2}
                    stroke="rgba(232,90,44,0.20)"
                    strokeWidth="1"
                    strokeDasharray="4 6"
                  />
                );
              })}

              {channels.map((channel, i) => {
                const angle = ((i * 60 - 90) * Math.PI) / 180;
                const cx = 200 + Math.cos(angle) * 160;
                const cy = 200 + Math.sin(angle) * 160;

                return (
                  <g key={i} className="channel-icon" transform={`translate(${cx}, ${cy})`}>
                    <circle r="26" fill="white" stroke="rgba(19,20,26,0.10)" strokeWidth="1" />
                    <g transform="translate(-12, -12)">
                      <channel.Icon size={24} strokeWidth={1.5} color="#13141A" />
                    </g>
                    <text
                      y="42"
                      textAnchor="middle"
                      fill="#6B6D78"
                      fontSize="11"
                      fontFamily="var(--font-mono)"
                    >
                      {channel.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Mobile channel grid */}
          <div className="grid grid-cols-3 gap-4 lg:hidden">
            {channels.map((channel, i) => (
              <div key={i} className="channel-icon flex flex-col items-center gap-2">
                <div className="w-[52px] h-[52px] rounded-full bg-white border border-[rgba(19,20,26,0.10)] flex items-center justify-center">
                  <channel.Icon size={24} strokeWidth={1.5} color="#13141A" />
                </div>
                <span className="font-[family-name:var(--font-mono)] text-[11px] text-[#6B6D78]">
                  {channel.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
