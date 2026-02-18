"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface PageIndustryProps {
  value: string;
  onChange: (value: string) => void;
  onNext: () => void;
  onBack?: () => void;
  totalPages?: number;
  currentPage?: number;
}

const INDUSTRIES = [
  { id: "saas", label: "SaaS", description: "Software as a Service" },
  { id: "fintech", label: "FinTech", description: "Financial Technology" },
  { id: "ecommerce", label: "E-commerce", description: "Online retail & marketplaces" },
  { id: "healthcare", label: "Healthcare", description: "Health & medical technology" },
  { id: "ai", label: "AI / ML", description: "Artificial Intelligence" },
  { id: "devtools", label: "DevTools", description: "Developer tools" },
  { id: "cybersecurity", label: "Cybersecurity", description: "Security & privacy" },
  { id: "edtech", label: "EdTech", description: "Education technology" },
  { id: "marketplace", label: "Marketplace", description: "Multi-sided platforms" },
  { id: "consumer", label: "Consumer", description: "B2C applications" },
  { id: "enterprise", label: "Enterprise", description: "B2B software" },
  { id: "other", label: "Other", description: "Something else" },
];

export function PageIndustry({
  value, onChange, onNext, onBack, totalPages = 21, currentPage = 3,
}: PageIndustryProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedId, setSelectedId] = useState<string>(value);

  const isValid = selectedId.length > 0;

  useEffect(() => setSelectedId(value), [value]);

  // Clean entrance - subtle fades only
  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });

      tl.fromTo(".grain", { opacity: 0 }, { opacity: 0.03, duration: 2 });
      tl.fromTo(".compass", { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.8 }, "-=1.5");
      tl.fromTo(".step", { opacity: 0 }, { opacity: 1, duration: 0.6 }, "-=0.6");
      tl.fromTo(".progress", { scaleX: (currentPage - 1) / totalPages }, { scaleX: currentPage / totalPages, duration: 1.5 }, "-=0.4");
      tl.fromTo(".qnum", { opacity: 0 }, { opacity: 1, duration: 0.5 }, "-=1.2");
      tl.fromTo(".headline", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7 }, "-=0.8");
      tl.fromTo(".card", { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.04 }, "-=0.4");
      tl.fromTo(".nav", { opacity: 0 }, { opacity: 1, duration: 0.5 }, "-=0.3");
    }, containerRef);

    return () => ctx.revert();
  }, [currentPage, totalPages]);

  // Selection - simple state change
  const selectIndustry = useCallback((id: string) => {
    setSelectedId(id);
    onChange(id);
  }, [onChange]);

  // Submit - clean fade
  const submit = useCallback(() => {
    if (!isValid) return;
    gsap.to(".page", { opacity: 0, x: -30, duration: 0.4, onComplete: onNext });
  }, [isValid, onNext]);

  const progressPct = Math.round((currentPage / totalPages) * 100);

  return (
    <div ref={containerRef} className="min-h-screen w-full bg-[var(--bg-canvas)] relative overflow-hidden">
      <div className="grain absolute inset-0 pointer-events-none z-0 opacity-0" 
        style={{backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`, backgroundSize: "256px"}} />

      <div className="page relative z-20 min-h-screen flex flex-col">
        <header className="flex items-center justify-between px-12 md:px-24 py-10">
          <div className="compass"><CompassLogo size={40} variant="compact" className="text-[var(--rf-charcoal)]" /></div>
          <div className="step flex items-center gap-4">
            <span className="rf-mono text-[10px] uppercase tracking-[0.3em] text-[var(--ink-3)]">Step</span>
            <div className="flex items-baseline">
              <span className="rf-mono text-lg font-semibold text-[var(--ink-1)]">{String(currentPage).padStart(2, "0")}</span>
              <span className="text-[var(--ink-3)] mx-1.5">/</span>
              <span className="rf-mono text-sm text-[var(--ink-3)]">{String(totalPages).padStart(2, "0")}</span>
            </div>
          </div>
          <button className="text-[10px] uppercase tracking-[0.2em] text-[var(--ink-3)] hover:text-[var(--ink-1)] transition-colors">Save & Exit</button>
        </header>

        <div className="px-12 md:px-24 mb-12">
          <div className="max-w-lg mx-auto">
            <div className="relative h-px bg-[var(--border-1)]">
              <div className="progress absolute inset-y-0 left-0 bg-[var(--rf-charcoal)] origin-left" style={{transform: "scaleX(0)"}} />
            </div>
            <div className="flex justify-between mt-3">
              <span className="rf-mono text-[9px] uppercase tracking-[0.2em] text-[var(--ink-3)]">Start</span>
              <span className="rf-mono text-[9px] uppercase tracking-[0.2em] text-[var(--ink-1)]">{progressPct}%</span>
            </div>
          </div>
        </div>

        <main className="flex-1 flex flex-col items-center px-12 md:px-24 pb-32">
          <div className="qnum mb-10">
            <span className="rf-mono text-[10px] uppercase tracking-[0.4em] text-[var(--ink-3)]">Question {String(currentPage).padStart(2, "0")}</span>
          </div>

          <h1 className="headline text-center mb-14">
            <span className="block text-[clamp(40px,8vw,72px)] leading-[1] font-bold text-[var(--ink-1)] tracking-[-0.03em]">What industry</span>
            <span className="block text-[clamp(40px,8vw,72px)] leading-[1] font-bold text-[var(--ink-1)] tracking-[-0.03em] mt-2">are you in<span className="text-[var(--ink-3)]">?</span></span>
          </h1>

          <div className="w-full max-w-4xl grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {INDUSTRIES.map((industry) => {
              const isSelected = selectedId === industry.id;
              return (
                <button
                  key={industry.id}
                  onClick={() => selectIndustry(industry.id)}
                  className={`card relative p-5 rounded-[16px] text-left border transition-all duration-200 ${
                    isSelected
                      ? "bg-[var(--rf-charcoal)] border-[var(--rf-charcoal)] text-[var(--rf-ivory)]"
                      : "bg-[var(--bg-raised)] border-[var(--border-1)] text-[var(--ink-1)] hover:border-[var(--ink-2)]"
                  }`}
                >
                  {isSelected && (
                    <div className="absolute top-3 right-3">
                      <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  )}
                  <span className="block font-semibold text-sm mb-1">{industry.label}</span>
                  <span className={`block text-xs ${isSelected ? "text-[var(--rf-ivory)]/60" : "text-[var(--ink-3)]"}`}>{industry.description}</span>
                </button>
              );
            })}
          </div>

          <p className="mt-10 text-sm text-[var(--ink-3)] text-center max-w-md">Select your primary market category</p>
        </main>

        <footer className="nav fixed bottom-0 left-0 right-0 border-t border-[var(--border-1)] bg-[var(--bg-surface)] z-30">
          <div className="max-w-4xl mx-auto px-12 md:px-24 py-6 flex items-center justify-between">
            <button onClick={onBack} className="flex items-center gap-2 text-sm font-medium text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
              Back
            </button>
            <button onClick={submit} disabled={!isValid} className="flex items-center gap-3 px-8 py-4 bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] rounded-[14px] font-semibold text-sm hover:bg-[#3d363b] transition-colors disabled:opacity-30">
              Continue
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
