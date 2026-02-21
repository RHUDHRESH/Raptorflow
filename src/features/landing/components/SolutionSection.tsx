"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLandingStore } from "./LandingClient";

const PILLARS = [
  {
    label: "PILLAR 01",
    title: "Company Memory",
    description:
      "Your positioning, ICPs, and past wins — captured once and shared with every module. No repetition. No context loss. No drift.",
    visual: "bcm",
  },
  {
    label: "PILLAR 02",
    title: "Active Intelligence",
    description:
      "Real-time market research, competitor monitoring, and trend identification that feed directly into your campaigns and moves.",
    visual: "intel",
  },
  {
    label: "PILLAR 03",
    title: "Unified Control",
    description:
      "One cockpit for every marketing channel, campaign, and initiative. The left hand sees exactly what the right is doing — always.",
    visual: "control",
  },
  {
    label: "PILLAR 04",
    title: "Agentic Execution",
    description:
      "AI proposes. You approve. Every move executes in context — scheduling, content, campaigns — with your brand voice baked in.",
    visual: "exec",
  },
];

function BcmVisual() {
  return (
    <div className="space-y-3">
      {[
        { label: "Brand Voice", status: "LOCKED", color: "var(--status-success)" },
        { label: "ICP Matrix", status: "3 ACTIVE", color: "var(--status-info)" },
        { label: "Positioning", status: "IN REVIEW", color: "var(--status-warning)" },
        { label: "Win Stories", status: "12 SAVED", color: "var(--ink-3)" },
      ].map((row) => (
        <div key={row.label} className="flex items-center gap-3 p-3 rounded-[var(--radius-sm)] bg-[var(--bg-canvas)] border border-[var(--border-1)]">
          <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: row.color }} />
          <span className="text-[12px] font-semibold text-[var(--ink-1)]">{row.label}</span>
          <span className="ml-auto text-[10px] font-mono text-[var(--ink-3)]">{row.status}</span>
        </div>
      ))}
    </div>
  );
}

function IntelVisual() {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 mb-3">
        {[{ label: "Market Signals", val: "24" }, { label: "Trends Tracked", val: "8" }, { label: "Competitors", val: "6" }, { label: "Alerts", val: "3" }].map((s) => (
          <div key={s.label} className="p-3 rounded-[var(--radius-sm)] bg-[var(--bg-canvas)] border border-[var(--border-1)]">
            <div className="text-[20px] font-bold font-mono text-[var(--ink-1)]">{s.val}</div>
            <div className="text-[10px] text-[var(--ink-3)] mt-0.5">{s.label}</div>
          </div>
        ))}
      </div>
      <div className="h-16 rounded-[var(--radius-sm)] bg-[var(--bg-canvas)] border border-[var(--border-1)] flex items-end px-3 py-2 gap-1">
        {[40, 55, 35, 70, 50, 80, 65].map((h, i) => (
          <div key={i} className="flex-1 rounded-sm bg-[var(--rf-charcoal)]/20" style={{ height: `${h}%` }} />
        ))}
      </div>
    </div>
  );
}

function ControlVisual() {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-[10px] font-semibold tracking-[0.1em] text-[var(--ink-3)] uppercase">Q1 Campaign Board</span>
        <span className="ml-auto text-[10px] font-mono text-[var(--status-info)]">4 active</span>
      </div>
      {[
        { name: "LinkedIn Siege", status: "RUNNING", prog: 68 },
        { name: "Email Nurture", status: "RUNNING", prog: 45 },
        { name: "Content Push", status: "REVIEW", prog: 90 },
        { name: "Paid Retarget", status: "DRAFT", prog: 12 },
      ].map((row) => (
        <div key={row.name} className="flex items-center gap-3 p-2.5 rounded-[6px] bg-[var(--bg-canvas)] border border-[var(--border-1)]">
          <span className="text-[11px] font-medium text-[var(--ink-1)] flex-1 truncate">{row.name}</span>
          <div className="w-20 h-1.5 rounded-full bg-[var(--border-2)] overflow-hidden">
            <div className="h-full bg-[var(--rf-charcoal)] rounded-full" style={{ width: `${row.prog}%` }} />
          </div>
          <span className="text-[9px] font-mono text-[var(--ink-3)] w-12 text-right">{row.status}</span>
        </div>
      ))}
    </div>
  );
}

function ExecVisual() {
  return (
    <div className="space-y-3">
      <div className="p-3 rounded-[var(--radius-sm)] bg-[var(--rf-charcoal)] border border-white/10">
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--status-success)", opacity: 0.8 }} />
          <span className="text-[11px] font-semibold text-white/80">Agent executing</span>
        </div>
        <p className="text-[11px] text-white/50 leading-snug">Writing 3 LinkedIn posts for Q1 ICP targeting mid-market SaaS...</p>
      </div>
      {[
        { label: "Posts drafted", val: "3/5", done: true },
        { label: "Scheduling", val: "In queue", done: false },
        { label: "Your approval", val: "Required", done: false },
      ].map((item) => (
        <div key={item.label} className="flex items-center gap-3 p-2.5 rounded-[6px] bg-[var(--bg-canvas)] border border-[var(--border-1)]">
          <div className={`w-4 h-4 rounded-full flex items-center justify-center ${item.done ? "bg-[var(--status-success)]/20" : "bg-[var(--border-2)]"}`}>
            {item.done && <div className="w-1.5 h-1.5 rounded-full bg-[var(--status-success)]" />}
          </div>
          <span className="text-[11px] font-medium text-[var(--ink-1)] flex-1">{item.label}</span>
          <span className="text-[10px] font-mono text-[var(--ink-3)]">{item.val}</span>
        </div>
      ))}
    </div>
  );
}

const VISUAL_COMPONENTS: Record<string, React.ComponentType> = {
  bcm: BcmVisual,
  intel: IntelVisual,
  control: ControlVisual,
  exec: ExecVisual,
};

export function SolutionSection() {
  const outerRef = useRef<HTMLDivElement>(null);
  const stickyRef = useRef<HTMLDivElement>(null);
  const pillarRefs = useRef<(HTMLDivElement | null)[]>([]);
  const visualRefs = useRef<(HTMLDivElement | null)[]>([]);
  const progressDotsRef = useRef<(HTMLDivElement | null)[]>([]);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!outerRef.current || !stickyRef.current) return;

    const ctx = gsap.context(() => {
      if (!isReducedMotion) {
        gsap.from(".solution-header-inner > *", {
          scrollTrigger: {
            trigger: ".solution-header-inner",
            start: "top 85%",
            toggleActions: "play none none none",
          },
          y: 40,
          opacity: 0,
          duration: 0.7,
          stagger: 0.1,
          ease: "power3.out",
        });
      }

      const totalPillars = PILLARS.length;

      pillarRefs.current.forEach((el, i) => {
        if (!el) return;
        gsap.set(el, { opacity: i === 0 ? 1 : 0, y: i === 0 ? 0 : 30 });
      });

      visualRefs.current.forEach((el, i) => {
        if (!el) return;
        gsap.set(el, { opacity: i === 0 ? 1 : 0 });
      });

      ScrollTrigger.create({
        trigger: outerRef.current,
        start: "top top",
        end: `+=${window.innerHeight * (totalPillars - 1)}`,
        pin: stickyRef.current,
        pinSpacing: true,
        scrub: false,
        onUpdate: (self) => {
          const progress = self.progress;
          const step = Math.min(Math.floor(progress * totalPillars), totalPillars - 1);

          pillarRefs.current.forEach((el, i) => {
            if (!el) return;
            const isActive = i === step;
            gsap.to(el, {
              opacity: isActive ? 1 : 0,
              y: isActive ? 0 : i < step ? -20 : 30,
              duration: 0.5,
              ease: "power2.out",
              overwrite: "auto",
            });
          });

          visualRefs.current.forEach((el, i) => {
            if (!el) return;
            gsap.to(el, {
              opacity: i === step ? 1 : 0,
              duration: 0.4,
              ease: "power2.out",
              overwrite: "auto",
            });
          });

          progressDotsRef.current.forEach((dot, i) => {
            if (!dot) return;
            dot.style.backgroundColor = i <= step ? "var(--rf-charcoal)" : "var(--border-2)";
          });
        },
      });
    }, outerRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section className="bg-[var(--bg-canvas)]">
      <div className="py-24 px-6">
        <div className="solution-header-inner max-w-[var(--shell-max-w)] mx-auto text-center">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-5 block">
            THE SOLUTION
          </span>
          <h2 className="text-[clamp(32px,5.5vw,52px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.03em]">
            One operating system.
            <br />
            <span className="text-[var(--rf-charcoal)]/45">Every marketing move.</span>
          </h2>
          <p className="mt-6 text-[17px] text-[var(--ink-2)] max-w-xl mx-auto leading-relaxed">
            RaptorFlow replaces your entire marketing stack with a single system built for operators who need precision and scale.
          </p>
        </div>
      </div>

      <div
        ref={outerRef}
        style={{ height: `${PILLARS.length * 100}vh` }}
        className="relative"
      >
        <div ref={stickyRef} className="h-screen overflow-hidden">
          <div className="h-full flex items-center px-6">
            <div className="max-w-[var(--shell-max-w)] mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
              <div className="relative" style={{ minHeight: 320 }}>
                {PILLARS.map((pillar, i) => (
                  <div
                    key={pillar.label}
                    ref={(el) => { pillarRefs.current[i] = el; }}
                    className="absolute inset-0 flex flex-col justify-center"
                    style={{ opacity: i === 0 ? 1 : 0 }}
                  >
                    <span className="rf-mono-xs text-[var(--rf-charcoal)]/40 tracking-[0.12em] uppercase mb-5">
                      {pillar.label}
                    </span>
                    <h3 className="text-[clamp(28px,4vw,40px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em] mb-5">
                      {pillar.title}
                    </h3>
                    <p className="text-[17px] text-[var(--ink-2)] leading-relaxed max-w-md">
                      {pillar.description}
                    </p>
                  </div>
                ))}
              </div>

              <div className="relative" style={{ minHeight: 280 }}>
                {PILLARS.map((pillar, i) => {
                  const VisualComp = VISUAL_COMPONENTS[pillar.visual];
                  return (
                    <div
                      key={pillar.label + "-visual"}
                      ref={(el) => { visualRefs.current[i] = el; }}
                      className="absolute inset-0"
                      style={{ opacity: i === 0 ? 1 : 0 }}
                    >
                      <div className="rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)] p-6">
                        <VisualComp />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="absolute right-8 top-1/2 -translate-y-1/2 flex flex-col gap-3">
            {PILLARS.map((_, i) => (
              <div
                key={i}
                ref={(el) => { progressDotsRef.current[i] = el; }}
                className="w-2 h-2 rounded-full transition-all duration-300"
                style={{ backgroundColor: i === 0 ? "var(--rf-charcoal)" : "var(--border-2)" }}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
