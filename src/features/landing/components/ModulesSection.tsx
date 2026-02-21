"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { useLandingStore } from "./LandingClient";

const MODULES = [
  {
    id: "foundation",
    label: "FOUNDATION",
    title: "Brand Context Map",
    description: "Capture your positioning, ICPs, and voice once. Every module reads it — always.",
    span: "col-span-2",
    accent: false,
    icon: (
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" className="module-icon">
        <rect className="icon-stroke" x="4" y="8" width="24" height="3" rx="1.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <rect className="icon-stroke" x="4" y="14.5" width="18" height="3" rx="1.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <rect className="icon-stroke" x="4" y="21" width="12" height="3" rx="1.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
    preview: (
      <div className="space-y-2 mt-4">
        {[{ label: "Brand Voice", status: "LOCKED", color: "bg-[var(--status-success)]" }, { label: "ICP Matrix", status: "3 ACTIVE", color: "bg-[var(--status-info)]" }, { label: "Positioning", status: "IN REVIEW", color: "bg-[var(--status-warning)]" }].map((row) => (
          <div key={row.label} className="flex items-center gap-2.5 p-2 rounded-[6px] bg-[var(--bg-canvas)] border border-[var(--border-1)]">
            <span className={`w-1.5 h-1.5 rounded-full ${row.color}`} />
            <span className="text-[11px] font-medium text-[var(--ink-1)] flex-1">{row.label}</span>
            <span className="text-[9px] font-mono text-[var(--ink-3)]">{row.status}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: "moves",
    label: "MOVES",
    title: "Marketing Initiatives",
    description: "From quick wins to 90-day sieges — orchestrate every initiative in one place.",
    span: "",
    accent: false,
    icon: (
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" className="module-icon">
        <circle className="icon-stroke" cx="16" cy="16" r="11" stroke="currentColor" strokeWidth="1.8" />
        <path className="icon-stroke" d="M11 16l4 4 7-8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    preview: (
      <div className="space-y-2 mt-4">
        {[{ name: "Q1 LinkedIn Push", tag: "RUNNING" }, { name: "Webinar Blitz", tag: "DRAFT" }].map((m) => (
          <div key={m.name} className="flex items-center gap-2 p-2 rounded-[6px] bg-[var(--bg-canvas)] border border-[var(--border-1)]">
            <span className="text-[11px] font-medium text-[var(--ink-1)] flex-1 truncate">{m.name}</span>
            <span className="text-[9px] font-mono text-[var(--ink-3)]">{m.tag}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: "campaigns",
    label: "CAMPAIGNS",
    title: "Campaign Engine",
    description: "Siege planning, cross-channel execution, and performance tracking unified.",
    span: "",
    accent: false,
    icon: (
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" className="module-icon">
        <path className="icon-stroke" d="M6 22L6 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <path className="icon-stroke" d="M12 22V8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <path className="icon-stroke" d="M18 22V14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <path className="icon-stroke" d="M24 22V10" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
    preview: (
      <div className="space-y-2 mt-4">
        <div className="flex items-end gap-1 h-14 px-1">
          {[55, 70, 40, 85, 60, 90, 75].map((h, i) => (
            <div key={i} className="flex-1 rounded-t-sm" style={{ height: `${h}%`, backgroundColor: i === 5 ? "var(--rf-charcoal)" : "var(--border-2)" }} />
          ))}
        </div>
      </div>
    ),
  },
  {
    id: "muse",
    label: "MUSE",
    title: "AI Collaborator",
    description: "An AI that knows your brand, writes in your voice, and never goes off-script.",
    span: "",
    accent: false,
    icon: (
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" className="module-icon">
        <path className="icon-stroke" d="M8 10C8 8.9 8.9 8 10 8h12c1.1 0 2 .9 2 2v8c0 1.1-.9 2-2 2h-4l-4 4v-4H10c-1.1 0-2-.9-2-2V10z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
        <path className="icon-stroke" d="M12 14h8M12 17h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
    preview: (
      <div className="mt-4 rounded-[6px] bg-[var(--bg-canvas)] border border-[var(--border-1)] p-3">
        <div className="text-[10px] font-mono text-[var(--ink-3)] mb-1">Generating...</div>
        <div className="space-y-1">
          <div className="h-2 rounded bg-[var(--border-2)] w-full" />
          <div className="h-2 rounded bg-[var(--border-2)] w-4/5" />
          <div className="h-2 rounded bg-[var(--border-2)] w-3/5" />
        </div>
      </div>
    ),
  },
  {
    id: "matrix",
    label: "MATRIX",
    title: "Intelligence Hub",
    description: "Competitive analysis and market signals that feed every decision you make.",
    span: "",
    accent: false,
    icon: (
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" className="module-icon">
        <rect className="icon-stroke" x="6" y="6" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.8" />
        <rect className="icon-stroke" x="18" y="6" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.8" />
        <rect className="icon-stroke" x="6" y="18" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.8" />
        <rect className="icon-stroke" x="18" y="18" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    ),
    preview: (
      <div className="mt-4 grid grid-cols-2 gap-2">
        {[{ l: "Signals", v: "24" }, { l: "Tracked", v: "8" }, { l: "Rivals", v: "6" }, { l: "Alerts", v: "3" }].map((s) => (
          <div key={s.l} className="p-2 rounded-[6px] bg-[var(--bg-canvas)] border border-[var(--border-1)]">
            <div className="text-[16px] font-bold font-mono text-[var(--ink-1)]">{s.v}</div>
            <div className="text-[9px] text-[var(--ink-3)]">{s.l}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: "blackbox",
    label: "BLACKBOX",
    title: "Decision Vault",
    description: "Every decision logged, every outcome tracked. The operator's flight recorder.",
    span: "col-span-2",
    accent: true,
    icon: (
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" className="module-icon">
        <rect className="icon-stroke" x="6" y="6" width="20" height="20" rx="3" stroke="currentColor" strokeWidth="1.8" />
        <path className="icon-stroke" d="M11 16h10M16 11v10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity=".5" />
        <rect className="icon-stroke" x="12" y="12" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    ),
    preview: (
      <div className="flex gap-4 mt-4">
        {[{ label: "Decisions", val: "142" }, { label: "Win rate", val: "78%" }, { label: "Saved hrs", val: "320" }].map((s) => (
          <div key={s.label} className="flex-1">
            <div className="text-[20px] font-bold font-mono text-[var(--rf-ivory)]">{s.val}</div>
            <div className="text-[10px] text-white/40 mt-0.5">{s.label}</div>
          </div>
        ))}
      </div>
    ),
  },
];

export function ModulesSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const { isReducedMotion } = useLandingStore();

  useEffect(() => {
    if (!sectionRef.current || isReducedMotion) return;

    const ctx = gsap.context(() => {
      gsap.from(".modules-header > *", {
        scrollTrigger: {
          trigger: ".modules-header",
          start: "top 85%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.7,
        stagger: 0.1,
        ease: "power3.out",
      });

      gsap.from(".module-card", {
        scrollTrigger: {
          trigger: ".modules-bento",
          start: "top 80%",
          toggleActions: "play none none none",
        },
        y: 40,
        opacity: 0,
        duration: 0.7,
        stagger: {
          grid: [2, 3],
          from: "start",
          amount: 0.6,
        },
        ease: "power3.out",
      });

      const mm = gsap.matchMedia();
      mm.add("(min-width: 1024px)", () => {
        const cards = sectionRef.current?.querySelectorAll(".module-card");
        cards?.forEach((card) => {
          card.addEventListener("mouseenter", () => {
            gsap.to(card, { y: -6, duration: 0.3, ease: "power2.out" });
            const paths = card.querySelectorAll(".icon-stroke");
            paths.forEach((p, i) => {
              const el = p as SVGElement;
              const len = (el as SVGGeometryElement).getTotalLength?.() ?? 100;
              gsap.set(el, { strokeDasharray: len, strokeDashoffset: len });
              gsap.to(el, { strokeDashoffset: 0, duration: 0.5, delay: i * 0.1, ease: "power2.out" });
            });
          });
          card.addEventListener("mouseleave", () => {
            gsap.to(card, { y: 0, duration: 0.3, ease: "power2.out" });
          });
        });
        return () => {};
      });

      return () => mm.revert();
    }, sectionRef);

    return () => ctx.revert();
  }, [isReducedMotion]);

  return (
    <section id="modules" ref={sectionRef} className="py-32 px-6 bg-[var(--bg-surface)]">
      <div className="max-w-[var(--shell-max-w)] mx-auto">
        <div className="modules-header text-center mb-16">
          <span className="rf-label text-[var(--rf-charcoal)]/40 tracking-[0.15em] mb-5 block">
            THE SYSTEM
          </span>
          <h2 className="text-[clamp(28px,4.5vw,48px)] font-bold text-[var(--rf-charcoal)] leading-tight tracking-[-0.02em]">
            Six modules. One cockpit.
          </h2>
          <p className="mt-5 text-[17px] text-[var(--ink-2)] max-w-lg mx-auto leading-relaxed">
            Every module shares the same context. What one learns, all know.
          </p>
        </div>

        <div
          className="modules-bento grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
          style={{ gridAutoRows: "minmax(260px, auto)" }}
        >
          {MODULES.map((mod) => (
            <div
              key={mod.id}
              className={`module-card will-change-transform rounded-[var(--radius-md)] border p-7 flex flex-col cursor-default ${mod.span} ${
                mod.accent
                  ? "bg-[var(--rf-charcoal)] border-[var(--rf-charcoal)] text-[var(--rf-ivory)]"
                  : "bg-[var(--bg-raised)] border-[var(--border-1)] hover:border-[var(--border-2)] text-[var(--ink-1)]"
              }`}
            >
              <div className={mod.accent ? "text-[var(--rf-ivory)]/80" : "text-[var(--rf-charcoal)]"}>
                {mod.icon}
              </div>

              <div className={`mt-4 text-[10px] font-semibold tracking-[0.12em] uppercase ${mod.accent ? "text-white/30" : "text-[var(--ink-3)]"}`}>
                {mod.label}
              </div>

              <h3 className={`mt-2 text-[20px] font-bold leading-tight ${mod.accent ? "text-[var(--rf-ivory)]" : "text-[var(--rf-charcoal)]"}`}>
                {mod.title}
              </h3>

              <p className={`mt-2 text-[13px] leading-relaxed ${mod.accent ? "text-white/50" : "text-[var(--ink-2)]"}`}>
                {mod.description}
              </p>

              <div className="flex-1">
                {mod.preview}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
