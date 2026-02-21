"use client";

import React, { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ArrowRight, ChevronRight } from "lucide-react";
import { useLandingStore } from "./LandingClient";

type SvgShapeProps = React.SVGProps<SVGElement>;

const RAIL_ICONS: { paths: { type: string; props: SvgShapeProps }[] }[] = [
  {
    paths: [
      { type: "rect", props: { x: "2", y: "3", width: "10", height: "2", rx: "1", fill: "currentColor", opacity: ".7" } },
      { type: "rect", props: { x: "2", y: "7", width: "8", height: "2", rx: "1", fill: "currentColor", opacity: ".4" } },
      { type: "rect", props: { x: "2", y: "11", width: "6", height: "2", rx: "1", fill: "currentColor", opacity: ".25" } },
    ],
  },
  {
    paths: [
      { type: "circle", props: { cx: "7", cy: "5", r: "2", stroke: "currentColor", strokeWidth: "1.4" } },
      { type: "path", props: { d: "M3 11c0-2.2 1.8-4 4-4s4 1.8 4 4", stroke: "currentColor", strokeWidth: "1.4", strokeLinecap: "round" } },
    ],
  },
  {
    paths: [
      { type: "path", props: { d: "M3 7h8M7 3v8", stroke: "currentColor", strokeWidth: "1.4", strokeLinecap: "round" } },
    ],
  },
  {
    paths: [
      { type: "rect", props: { x: "2", y: "2", width: "4", height: "4", rx: "1", stroke: "currentColor", strokeWidth: "1.3" } },
      { type: "rect", props: { x: "8", y: "2", width: "4", height: "4", rx: "1", stroke: "currentColor", strokeWidth: "1.3" } },
      { type: "rect", props: { x: "2", y: "8", width: "4", height: "4", rx: "1", stroke: "currentColor", strokeWidth: "1.3" } },
      { type: "rect", props: { x: "8", y: "8", width: "4", height: "4", rx: "1", stroke: "currentColor", strokeWidth: "1.3" } },
    ],
  },
  {
    paths: [
      { type: "path", props: { d: "M7 2v10M2 7h10", stroke: "currentColor", strokeWidth: "1.4", strokeLinecap: "round", opacity: ".6" } },
      { type: "circle", props: { cx: "7", cy: "7", r: "2.5", stroke: "currentColor", strokeWidth: "1.3" } },
    ],
  },
  {
    paths: [
      { type: "rect", props: { x: "3", y: "2", width: "8", height: "10", rx: "1.5", stroke: "currentColor", strokeWidth: "1.3" } },
      { type: "path", props: { d: "M5 5h4M5 8h2", stroke: "currentColor", strokeWidth: "1.2", strokeLinecap: "round" } },
    ],
  },
];

function SvgShape({ type, props }: { type: string; props: SvgShapeProps }) {
  if (type === "rect") return <rect {...(props as React.SVGProps<SVGRectElement>)} />;
  if (type === "circle") return <circle {...(props as React.SVGProps<SVGCircleElement>)} />;
  if (type === "path") return <path {...(props as React.SVGProps<SVGPathElement>)} />;
  return null;
}

const BCM_COLUMNS = [
  {
    label: "PROPOSED",
    cards: [
      { tag: "Positioning", title: "Core value prop", dotColor: "var(--status-warning)" },
      { tag: "ICP", title: "Primary persona", dotColor: "var(--ink-3)" },
    ],
  },
  {
    label: "LOCK",
    cards: [
      { tag: "Brand Voice", title: "Tone guidelines", dotColor: "var(--status-success)" },
      { tag: "Messaging", title: "Key narratives", dotColor: "var(--status-success)" },
    ],
  },
  {
    label: "DEPLOY",
    cards: [
      { tag: "Active", title: "Campaign brief", dotColor: "var(--status-info)" },
    ],
  },
];

const DRAWER_ROWS = [
  { label: "BCM Score", value: "94/100" },
  { label: "Active ICPs", value: "3" },
  { label: "Pillars locked", value: "7/9" },
];

const ACTIVITY_ROWS = [
  { label: "ICP updated", time: "2m ago", active: true },
  { label: "Voice locked", time: "1h ago", active: false },
  { label: "Brief exported", time: "3h ago", active: false },
];

export function HeroSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const cockpitRef = useRef<HTMLDivElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      if (!isReducedMotion) {
        const tl = gsap.timeline({ delay: 0.25, defaults: { ease: "power3.out" } });

        tl.from(".hero-label", { y: 28, opacity: 0, duration: 0.6 })
          .from(".hero-word", { y: 80, opacity: 0, duration: 0.9, stagger: 0.08 }, "-=0.3")
          .from(".hero-sub", { opacity: 0, filter: "blur(6px)", duration: 0.7, clearProps: "filter" }, "-=0.45")
          .from(".hero-cta-group > *", { y: 20, opacity: 0, duration: 0.55, stagger: 0.1 }, "-=0.4")
          .from(".hero-trust", { opacity: 0, y: 10, duration: 0.5 }, "-=0.3")
          .from(cockpitRef.current, { scale: 0.94, y: 80, opacity: 0, duration: 1.2 }, "-=0.8")
          .from(".cockpit-rail-icon", { x: -20, opacity: 0, duration: 0.45, stagger: 0.05 }, "-=0.7")
          .from(".cockpit-col", { y: 20, opacity: 0, duration: 0.5, stagger: 0.07 }, "-=0.6")
          .from(".cockpit-drawer-row", { x: 20, opacity: 0, duration: 0.45, stagger: 0.06 }, "-=0.5")
          .from(".cockpit-card", { scale: 0.92, opacity: 0, duration: 0.4, stagger: 0.04 }, "-=0.55");

        gsap.to(cockpitRef.current, {
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top top",
            end: "bottom top",
            scrub: 1,
          },
          y: 80,
          ease: "none",
        });

        gsap.to(".hero-ambient", {
          y: "random(-18, 18)",
          x: "random(-12, 12)",
          duration: "random(3, 5)",
          ease: "sine.inOut",
          yoyo: true,
          repeat: -1,
          stagger: { each: 0.8, from: "random" },
        });

        const mm = gsap.matchMedia();
        mm.add("(min-width: 1024px)", () => {
          const primary = sectionRef.current?.querySelector(".hero-btn-primary");
          if (primary) {
            primary.addEventListener("mouseenter", () =>
              gsap.to(primary, { scale: 1.04, duration: 0.22, ease: "power2.out" })
            );
            primary.addEventListener("mouseleave", () =>
              gsap.to(primary, { scale: 1, duration: 0.22, ease: "power2.out" })
            );
          }
          return () => {};
        });

        return () => mm.revert();
      }
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section
      id="hero"
      ref={sectionRef}
      className="relative min-h-screen pt-20 pb-16 px-6 overflow-hidden bg-[var(--bg-canvas)]"
    >
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="hero-ambient absolute top-[15%] left-[8%] w-[340px] h-[340px] rounded-full bg-[var(--rf-charcoal)]/[0.025] blur-[90px]" />
        <div className="hero-ambient absolute top-[45%] right-[10%] w-[280px] h-[280px] rounded-full bg-[var(--rf-charcoal)]/[0.03] blur-[70px]" />
        <div className="hero-ambient absolute bottom-[15%] left-[35%] w-[220px] h-[220px] rounded-full bg-[var(--rf-charcoal)]/[0.02] blur-[60px]" />
      </div>

      <div className="max-w-[var(--shell-max-w)] mx-auto relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-14 items-center min-h-[calc(100vh-5rem)]">
          <div className="pt-10 lg:pt-0">
            <span className="hero-label inline-flex items-center gap-2 px-3.5 py-1.5 rounded-[var(--radius-full)] bg-[var(--rf-charcoal)]/[0.06] text-[11px] font-semibold tracking-[0.12em] text-[var(--rf-charcoal)]/60 mb-8 uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--rf-accent)] rf-pulse" />
              The Marketing OS for Operators
            </span>

            <h1 className="text-[clamp(46px,8vw,84px)] font-bold text-[var(--rf-charcoal)] leading-[0.93] tracking-[-0.04em] mb-7">
              <span className="hero-word inline-block">The</span>{" "}
              <span className="hero-word inline-block">Marketing</span>{" "}
              <span className="hero-word inline-block">OS</span>
              <br />
              <span className="hero-word inline-block">for</span>{" "}
              <span className="hero-word inline-block">Operators.</span>
            </h1>

            <p className="hero-sub text-[18px] text-[var(--ink-2)] leading-relaxed mb-10 max-w-[420px]">
              One cockpit. Every marketing move. Total control.
            </p>

            <div className="hero-cta-group flex flex-col sm:flex-row gap-4">
              <a
                href="/onboarding"
                className="hero-btn-primary inline-flex items-center justify-center gap-2.5 px-8 py-4 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[var(--radius-sm)] text-[15px] font-semibold will-change-transform"
              >
                Enter the cockpit
                <ArrowRight size={17} />
              </a>
              <a
                href="#control"
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById("control")?.scrollIntoView({ behavior: "smooth" });
                }}
                className="inline-flex items-center justify-center gap-2 px-8 py-4 border border-[var(--border-2)] text-[var(--ink-1)] rounded-[var(--radius-sm)] text-[15px] font-medium hover:bg-[var(--bg-surface)] hover:border-[var(--ink-2)] transition-all duration-200"
              >
                See how it works
                <ChevronRight size={16} className="text-[var(--ink-3)]" />
              </a>
            </div>

            <div className="hero-trust mt-10 flex items-center gap-4">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded-full border-2 border-[var(--bg-canvas)] flex items-center justify-center text-[10px] font-bold text-[var(--rf-ivory)]"
                    style={{ backgroundColor: `hsl(${i * 37 + 12} 20% 35%)` }}
                  >
                    {String.fromCharCode(64 + i)}
                  </div>
                ))}
              </div>
              <p className="text-[13px] text-[var(--ink-3)]">
                500+ operators running their OS
              </p>
            </div>
          </div>

          <div ref={cockpitRef} className="relative hidden lg:block will-change-transform">
            <div
              className="rounded-[var(--radius-lg)] overflow-hidden border border-[var(--border-1)] bg-[var(--rf-charcoal)]"
              style={{ boxShadow: "0 32px 80px rgba(42,37,41,0.18)" }}
            >
              <div className="flex items-center gap-2 px-4 py-3 bg-[var(--rf-charcoal)] border-b border-white/[0.08]">
                <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
                <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
                <div className="w-2.5 h-2.5 rounded-full bg-white/20" />
                <div className="ml-3 flex-1 flex justify-center">
                  <div className="bg-white/[0.08] rounded-[4px] px-4 py-1 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--status-success)", opacity: 0.6 }} />
                    <span className="text-[11px] font-mono text-white/40">app.raptorflow.io/foundation</span>
                  </div>
                </div>
              </div>

              <div className="flex h-[420px]">
                <div className="w-[52px] bg-[#1e1b1d] border-r border-white/[0.06] flex flex-col items-center py-4 gap-3">
                  <div className="cockpit-rail-icon w-8 h-8 rounded-[6px] bg-white/[0.12] flex items-center justify-center mb-2">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <path d="M3 10L7 4L11 10" stroke="var(--rf-ivory)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                      <path d="M5 8H9" stroke="var(--rf-ivory)" strokeWidth="1.2" strokeLinecap="round" />
                    </svg>
                  </div>
                  {RAIL_ICONS.map((icon, i) => (
                    <div
                      key={i}
                      className={`cockpit-rail-icon w-8 h-8 rounded-[6px] flex items-center justify-center ${i === 0 ? "bg-white/[0.1]" : ""}`}
                    >
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 14 14"
                        fill="none"
                        className={i === 0 ? "text-white/80" : "text-white/30"}
                      >
                        {icon.paths.map((p, pi) => (
                          <SvgShape key={pi} type={p.type} props={p.props} />
                        ))}
                      </svg>
                    </div>
                  ))}
                  <div className="mt-auto w-7 h-7 rounded-full bg-white/[0.15] flex items-center justify-center text-[10px] font-bold text-white/60">
                    J
                  </div>
                </div>

                <div className="flex flex-col flex-1 min-w-0">
                  <div className="flex items-center gap-2 px-4 h-10 bg-[var(--bg-surface)] border-b border-[var(--border-1)] flex-shrink-0">
                    <span className="text-[11px] text-[var(--ink-3)]">Foundation</span>
                    <span className="text-[var(--ink-3)] text-[11px]">/</span>
                    <span className="text-[11px] font-semibold text-[var(--ink-1)]">Brand Context Map</span>
                    <div className="ml-auto flex items-center gap-2">
                      <div className="w-5 h-5 rounded-[4px] bg-[var(--border-1)]" />
                      <div className="w-5 h-5 rounded-[4px] bg-[var(--border-1)]" />
                    </div>
                  </div>

                  <div className="flex flex-1 min-h-0">
                    <div className="flex-1 bg-[var(--bg-canvas)] p-4 overflow-hidden">
                      <div className="grid grid-cols-3 gap-3 h-full">
                        {BCM_COLUMNS.map((col) => (
                          <div key={col.label} className="cockpit-col flex flex-col gap-2">
                            <span className="text-[9px] font-semibold tracking-[0.12em] text-[var(--ink-3)] uppercase px-1">
                              {col.label}
                            </span>
                            {col.cards.map((card, ci) => (
                              <div
                                key={ci}
                                className="cockpit-card bg-[var(--bg-surface)] border border-[var(--border-1)] rounded-[6px] p-2.5"
                              >
                                <div className="flex items-center gap-1.5 mb-1.5">
                                  <span
                                    className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                                    style={{ backgroundColor: card.dotColor }}
                                  />
                                  <span className="text-[9px] font-semibold tracking-[0.08em] text-[var(--ink-3)] uppercase">
                                    {card.tag}
                                  </span>
                                </div>
                                <p className="text-[11px] font-semibold text-[var(--ink-1)] leading-tight">
                                  {card.title}
                                </p>
                              </div>
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="w-[170px] bg-[var(--bg-surface)] border-l border-[var(--border-1)] p-3 flex flex-col gap-3 flex-shrink-0">
                      <p className="text-[10px] font-bold text-[var(--ink-1)] tracking-[0.08em] uppercase">
                        Context
                      </p>
                      {DRAWER_ROWS.map((row) => (
                        <div
                          key={row.label}
                          className="cockpit-drawer-row flex justify-between items-center py-1.5 border-b border-[var(--border-1)] last:border-0"
                        >
                          <span className="text-[10px] text-[var(--ink-3)]">{row.label}</span>
                          <span className="text-[10px] font-semibold font-mono text-[var(--ink-1)]">
                            {row.value}
                          </span>
                        </div>
                      ))}
                      <div className="mt-2">
                        <p className="text-[9px] font-semibold tracking-[0.08em] text-[var(--ink-3)] uppercase mb-2">
                          Activity
                        </p>
                        {ACTIVITY_ROWS.map((item) => (
                          <div
                            key={item.label}
                            className="cockpit-drawer-row flex items-center gap-2 py-1"
                          >
                            <span
                              className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                              style={{ backgroundColor: item.active ? "var(--status-success)" : "var(--ink-3)" }}
                            />
                            <span className="text-[10px] text-[var(--ink-2)] flex-1 truncate">
                              {item.label}
                            </span>
                            <span className="text-[9px] text-[var(--ink-3)] font-mono">
                              {item.time}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
