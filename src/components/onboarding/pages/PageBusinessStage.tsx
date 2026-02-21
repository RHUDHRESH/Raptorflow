"use client";

import { useEffect, useCallback, useRef, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Rocket, TrendingUp, Building, Briefcase, Landmark } from "lucide-react";

interface PageBusinessStageProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const STAGES = [
  { label: "Idea", tagline: "Validating the concept", detail: "Scrappy, low-budget, fast-learning moves", icon: Rocket },
  { label: "MVP", tagline: "First users in, learning fast", detail: "Trust-building and early-adopter content", icon: TrendingUp },
  { label: "Growth", tagline: "Found PMF, now scaling", detail: "Multi-channel, data-driven content", icon: Building },
  { label: "Scale", tagline: "Established and optimising", detail: "Brand authority and retention plays", icon: Briefcase },
  { label: "Enterprise", tagline: "Large org, multi-product", detail: "Account-based, relationship-first motion", icon: Landmark },
];

export function PageBusinessStage({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageBusinessStageProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const detailRef = useRef<HTMLDivElement>(null);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // Entrance animation with stagger
  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });
      
      tl.fromTo(".stage-node",
        { opacity: 0, y: 30, scale: 0.9 },
        { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.1 }
      )
      .fromTo(".stage-label",
        { opacity: 0 },
        { opacity: 1, duration: 0.3, stagger: 0.08 },
        "-=0.3"
      );
    }, containerRef);
    return () => ctx.revert();
  }, []);

  // Track fill animation
  const selectedIdx = STAGES.findIndex(s => s.label === value);
  const fillPercent = selectedIdx >= 0 ? (selectedIdx / (STAGES.length - 1)) * 100 : 0;

  useEffect(() => {
    if (trackRef.current) {
      gsap.to(trackRef.current, {
        width: `${fillPercent}%`,
        duration: 0.6,
        ease: "power2.inOut"
      });
    }
  }, [fillPercent]);

  // Selection handler with animation
  const handleSelect = useCallback((label: string, idx: number) => {
    onChange(label);
    
    // Node animation
    const node = document.querySelector(`[data-stage="${label}"]`);
    if (node) {
      gsap.fromTo(node,
        { scale: 0.9 },
        { scale: 1.1, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out" }
      );
    }

    // Detail card animation
    if (detailRef.current) {
      gsap.fromTo(detailRef.current,
        { opacity: 0, y: 20, height: 0 },
        { opacity: 1, y: 0, height: "auto", duration: 0.4, ease: "power2.out" }
      );
    }

    // Note: User must click Continue or press Enter to advance
  }, [onChange]);

  // Detail card update animation
  useEffect(() => {
    if (detailRef.current && value) {
      gsap.fromTo(detailRef.current,
        { opacity: 0.7, scale: 0.98 },
        { opacity: 1, scale: 1, duration: 0.25, ease: "power2.out" }
      );
    }
  }, [value]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && value) { 
        onNext(); 
        return; 
      }
      const idx = STAGES.findIndex(s => s.label === value);
      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        const newIdx = Math.min(idx + 1, STAGES.length - 1);
        onChange(STAGES[newIdx].label);
      }
      if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        const newIdx = Math.max(idx - 1, 0);
        onChange(STAGES[newIdx].label);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [value, onNext, onChange]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="What stage is your business at?"
      stepDescription="This shapes the type and ambition of strategies we propose."
      onBack={onBack}
      onNext={onNext}
      canGoNext={!!value}
      showBack={!!onBack}
    >
      <div ref={containerRef} className="ob-content-item ob-animate-in">
        <p className="text-[11px] font-mono text-[var(--ink-3)] mb-8 flex items-center gap-2">
          <span className="flex gap-1">
            <kbd className="px-1.5 py-0.5 rounded bg-[var(--bg-surface)] border border-[var(--border-2)]">←</kbd>
            <kbd className="px-1.5 py-0.5 rounded bg-[var(--bg-surface)] border border-[var(--border-2)]">→</kbd>
          </span>
          navigate · click to select
        </p>

        {/* Timeline */}
        <div className="relative px-4">
          {/* Track background */}
          <div className="absolute top-[28px] left-8 right-8 h-[4px] bg-[var(--border-1)] rounded-full overflow-hidden">
            {/* Animated fill */}
            <div
              ref={trackRef}
              className="h-full bg-[var(--rf-charcoal)] rounded-full"
              style={{ width: "0%" }}
            />
          </div>

          {/* Nodes */}
          <div className="flex justify-between relative">
            {STAGES.map((stage, i) => {
              const isSelected = value === stage.label;
              const isPast = selectedIdx >= 0 && i < selectedIdx;
              const isHovered = hoveredIdx === i;
              const Icon = stage.icon;

              return (
                <button
                  key={stage.label}
                  data-stage={stage.label}
                  onClick={() => handleSelect(stage.label, i)}
                  onMouseEnter={() => setHoveredIdx(i)}
                  onMouseLeave={() => setHoveredIdx(null)}
                  className="stage-node flex flex-col items-center gap-4 group focus:outline-none"
                  style={{ width: `${100 / STAGES.length}%` }}
                >
                  {/* Node circle */}
                  <div 
                    className={`relative z-10 transition-transform duration-300 ${isSelected ? "scale-110" : isHovered ? "scale-105" : ""}`}
                  >
                    <div className={`w-14 h-14 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${isSelected
                        ? "bg-[var(--rf-charcoal)] border-[var(--rf-charcoal)] shadow-lg shadow-black/20"
                        : isPast
                          ? "bg-[var(--rf-charcoal)]/20 border-[var(--rf-charcoal)]/40"
                          : "bg-[var(--bg-surface)] border-[var(--border-2)] group-hover:border-[var(--ink-2)]"
                      }`}
                    >
                      <Icon 
                        size={22} 
                        className={`transition-colors ${isSelected ? "text-[var(--rf-ivory)]" : isPast ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)] group-hover:text-[var(--ink-2)]"}`}
                      />
                    </div>
                    
                    {/* Selection ring */}
                    {isSelected && (
                      <div className="absolute inset-[-6px] rounded-full border-2 border-[var(--rf-charcoal)]/20 animate-ping-once" />
                    )}

                    {/* Hover glow */}
                    {isHovered && !isSelected && (
                      <div className="absolute inset-[-4px] rounded-full bg-[var(--rf-charcoal)]/5 -z-10" />
                    )}
                  </div>

                  {/* Label */}
                  <div className="stage-label text-center">
                    <span className={`text-[13px] font-semibold block transition-colors ${isSelected ? "text-[var(--ink-1)]" : "text-[var(--ink-3)] group-hover:text-[var(--ink-2)]"}`}>
                      {stage.label}
                    </span>
                    <span className={`text-[10px] leading-snug hidden sm:block transition-all mt-1 max-w-[90px] mx-auto ${isSelected ? "text-[var(--ink-2)] opacity-100" : "text-[var(--ink-3)]/60 opacity-0 group-hover:opacity-100"}`}>
                      {stage.tagline}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Contextual detail card */}
        {value && (
          <div
            ref={detailRef}
            className="mt-10 p-5 rounded-[var(--radius-lg)] bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] relative overflow-hidden"
          >
            {/* Subtle gradient accent */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
            
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                {(() => {
                  const stage = STAGES.find(s => s.label === value);
                  const Icon = stage?.icon || Rocket;
                  return <Icon size={16} className="opacity-60" />;
                })()}
                <p className="text-[11px] font-mono text-white/40 tracking-wider">{value.toUpperCase()}</p>
              </div>
              <p className="text-[16px] font-medium leading-relaxed">
                {STAGES.find(s => s.label === value)?.detail}
              </p>
            </div>
          </div>
        )}
      </div>
    </OnboardingLayout>
  );
}
