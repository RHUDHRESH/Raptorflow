"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Globe, MapPin, Check, ArrowRight } from "lucide-react";

interface PageGeographicFocusProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const REGIONS = [
  { label: "North America", desc: "US, Canada, Mexico" },
  { label: "Europe", desc: "UK, EU, EEA" },
  { label: "Asia-Pacific", desc: "APAC, ANZ, Southeast Asia" },
  { label: "Global", desc: "No geographic limits" },
];

export function PageGeographicFocus({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageGeographicFocusProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const customRef = useRef<HTMLInputElement>(null);
  const [customValue, setCustomValue] = useState("");
  const [showCustom, setShowCustom] = useState(false);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".region-card",
        { opacity: 0, y: 25 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  const handleSelect = useCallback((label: string) => {
    if (label === "Custom") {
      setShowCustom(true);
      setTimeout(() => customRef.current?.focus(), 100);
    } else {
      onChange(label);
      // Note: User must click Continue or press Enter to advance
    }
  }, [onChange]);

  const handleCustomSubmit = useCallback(() => {
    if (customValue.trim()) {
      onChange(customValue.trim());
      // Note: User must click Continue or press Enter to advance
    }
  }, [customValue, onChange]);

  // Enter to skip (optional)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && !value && !showCustom) {
        gsap.to(wrapperRef.current, {
          scale: 0.98,
          duration: 0.1,
          yoyo: true,
          repeat: 1,
          onComplete: () => onNext()
        });
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [value, showCustom, onNext]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="Geographic focus (optional)"
      stepDescription="Where are your target customers located?"
      onBack={onBack}
      onNext={onNext}
      canGoNext={true}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in">
        {/* Region grid */}
        <div className="ob-interactive grid grid-cols-2 gap-3">
          {REGIONS.map((region) => {
            const isSelected = value === region.label;
            return (
              <button
                key={region.label}
                onClick={() => handleSelect(region.label)}
                className={`region-card flex flex-col items-start gap-2 p-4 rounded-[var(--radius-md)] border transition-all text-left ${isSelected
                    ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)]"
                    : "bg-[var(--bg-surface)] border-[var(--border-1)] hover:border-[var(--border-2)]"
                  }`}
              >
                <Globe size={18} className={isSelected ? "opacity-80" : "text-[var(--ink-3)]"} />
                <div>
                  <p className={`text-[14px] font-semibold ${isSelected ? "text-[var(--rf-ivory)]" : "text-[var(--ink-1)]"}`}>
                    {region.label}
                  </p>
                  <p className={`text-[11px] mt-0.5 ${isSelected ? "text-white/50" : "text-[var(--ink-3)]"}`}>
                    {region.desc}
                  </p>
                </div>
                {isSelected && <Check size={16} className="ml-auto mt-2 opacity-60" />}
              </button>
            );
          })}
        </div>

        {/* Custom input */}
        {showCustom && (
          <div className="ob-content-item ob-interactive mt-4 flex gap-2">
            <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] border border-[var(--border-2)] bg-[var(--bg-surface)] focus-within:border-[var(--rf-charcoal)] transition-all">
              <MapPin size={16} className="text-[var(--ink-3)]" />
              <input
                ref={customRef}
                type="text"
                value={customValue}
                onChange={e => setCustomValue(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleCustomSubmit()}
                placeholder="e.g. UK + Ireland only"
                className="flex-1 bg-transparent border-none outline-none text-[15px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40"
              />
            </div>
            <button
              onClick={handleCustomSubmit}
              disabled={!customValue.trim()}
              className="px-4 py-3 rounded-[var(--radius-md)] bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] disabled:opacity-40 transition-opacity"
            >
              <ArrowRight size={18} />
            </button>
          </div>
        )}

        {/* Skip hint */}
        {!showCustom && (
          <div className="ob-content-item ob-animate-in mt-6 flex items-center gap-2 p-3 rounded-[var(--bg-surface)] border border-dashed border-[var(--border-2)]">
            <ArrowRight size={14} className="text-[var(--ink-3)]" />
            <span className="text-[13px] text-[var(--ink-2)]">Press Enter to skip — we'll assume global</span>
          </div>
        )}
      </div>
    </OnboardingLayout>
  );
}
