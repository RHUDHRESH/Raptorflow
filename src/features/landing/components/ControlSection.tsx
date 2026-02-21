"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { useLandingStore } from "./LandingClient";

const STEPS = [
  {
    number: "01",
    title: "Define your world",
    description:
      "Build your Brand Context Map — ICPs, positioning, voice, and strategic context. Captured once, shared everywhere forever.",
    side: "left",
  },
  {
    number: "02",
    title: "Choose your move",
    description:
      "From quick tactical wins to 90-day campaign sieges. Select the scope that matches your objective and current quarter.",
    side: "right",
  },
  {
    number: "03",
    title: "Review the work",
    description:
      "AI-generated plans, content, and assets arrive complete. You approve, refine, or regenerate — you stay in command.",
    side: "left",
  },
  {
    number: "04",
    title: "Execute with precision",
    description:
      "Your move goes live across channels. Tracked, measured, and fed back into your BCM for the next operation.",
    side: "right",
  },
];

export function ControlSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const svgLineRef = useRef<SVGLineElement>(null);
  const timelineRef = useRef<HTMLDivElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      if (!isReducedMotion) {
        gsap.from(".control-header > *", {
          scrollTrigger: {
            trigger: ".control-header",
            start: "top 85%",
            toggleActions: "play none none none",
          },
          y: 40,
          opacity: 0,
          duration: 0.7,
          stagger: 0.1,
          ease: "power3.out",
        });

        const steps = sectionRef.current?.querySelectorAll(".timeline-step");
        steps?.forEach((step, i) => {
          const side = i % 2 === 0 ? -50 : 50;
          gsap.from(step, {
            scrollTrigger: {
              trigger: step,
              start: "top 82%",
              toggleActions: "play none none none",
            },
            x: side,
            opacity: 0,
            duration: 0.8,
            ease: "power3.out",
          });
        });

        const circles = sectionRef.current?.querySelectorAll(".timeline-circle");
        circles?.forEach((circle) => {
          gsap.from(circle, {
            scrollTrigger: {
              trigger: circle,
              start: "top 80%",
              toggleActions: "play none none none",
            },
            scale: 0,
            duration: 0.5,
            ease: "back.out(2)",
          });
        });

        if (svgLineRef.current && timelineRef.current) {
          const lineEl = svgLineRef.current;
          const totalH = timelineRef.current.getBoundingClientRect().height;
          const len = totalH;
          gsap.set(lineEl, { strokeDasharray: len, strokeDashoffset: len });
          gsap.to(lineEl, {
            strokeDashoffset: 0,
            ease: "none",
            scrollTrigger: {
              trigger: timelineRef.current,
              start: "top 70%",
              end: "bottom 60%",
              scrub: 1,
            },
          });
        }
      }
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section id="control" ref={sectionRef} className="py-32 px-6 bg-[var(--bg-canvas)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        <div className="control-header text-center mb-24">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-5 block">
            HOW IT WORKS
          </span>
          <h2 className="text-[clamp(32px,5.5vw,52px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.03em]">
            Control the chaos.
          </h2>
          <p className="mt-6 text-[17px] text-[var(--ink-2)] max-w-lg mx-auto leading-relaxed">
            From strategic definition to executed campaign in four intentional steps.
          </p>
        </div>

        <div ref={timelineRef} className="relative max-w-3xl mx-auto">
          <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 hidden lg:block" style={{ width: 2 }}>
            <svg
              className="w-full h-full"
              preserveAspectRatio="none"
              style={{ overflow: "visible" }}
            >
              <line
                x1="1"
                y1="0"
                x2="1"
                y2="100%"
                stroke="var(--border-2)"
                strokeWidth="2"
                strokeLinecap="round"
              />
              <line
                ref={svgLineRef}
                x1="1"
                y1="0"
                x2="1"
                y2="100%"
                stroke="var(--rf-charcoal)"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </div>

          <div className="space-y-20 lg:space-y-24">
            {STEPS.map((step, i) => (
              <div
                key={step.number}
                className={`timeline-step relative grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center will-change-transform`}
              >
                <div className="absolute left-1/2 -translate-x-1/2 top-1/2 -translate-y-1/2 z-10 hidden lg:flex">
                  <div className="timeline-circle w-10 h-10 rounded-full bg-[var(--bg-canvas)] border-2 border-[var(--border-2)] flex items-center justify-center will-change-transform">
                    <span className="text-[10px] font-bold font-mono text-[var(--rf-charcoal)]">{step.number}</span>
                  </div>
                </div>

                <div className={step.side === "right" ? "lg:order-2" : ""}>
                  <div className="lg:hidden flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-full bg-[var(--rf-charcoal)] flex items-center justify-center">
                      <span className="text-[11px] font-bold font-mono text-[var(--rf-ivory)]">{step.number}</span>
                    </div>
                    <div className="h-px flex-1 bg-[var(--border-1)]" />
                  </div>

                  <div className={`relative ${step.side === "left" ? "lg:text-right" : "lg:text-left"}`}>
                    <span className="text-[10px] font-semibold tracking-[0.1em] text-[var(--ink-3)] uppercase block mb-2">
                      Step {step.number}
                    </span>
                    <h3 className="text-[24px] font-bold text-[var(--rf-charcoal)] mb-4 leading-tight tracking-[-0.01em]">
                      {step.title}
                    </h3>
                    <p className="text-[16px] text-[var(--ink-2)] leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                </div>

                <div className={`hidden lg:block ${step.side === "right" ? "lg:order-1" : ""}`} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
