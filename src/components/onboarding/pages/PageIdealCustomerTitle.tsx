"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { User, Users, Briefcase, Building2, ArrowRight } from "lucide-react";

interface PageIdealCustomerTitleProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const PERSONAS = [
  { icon: Users, label: "Founders", desc: "CEOs & founders of early-stage companies" },
  { icon: Briefcase, label: "Marketing Leaders", desc: "CMOs, VPs, and Heads of Marketing" },
  { icon: Building2, label: "Enterprise", desc: "Large org decision makers" },
  { icon: User, label: "Operators", desc: "Day-to-day practitioners" },
];

export function PageIdealCustomerTitle({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageIdealCustomerTitleProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const isValid = value.trim().length >= 2;

  useEffect(() => {
    const t = setTimeout(() => inputRef.current?.focus(), 400);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".ob-content-item",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  }, [onChange]);

  const handlePersonaClick = useCallback((label: string) => {
    onChange(label);
    // Animate selection but don't auto-advance
    gsap.to(wrapperRef.current, {
      scale: 0.98,
      duration: 0.1,
      yoyo: true,
      repeat: 1,
      ease: "power2.out"
    });
    // Note: User must click Continue or press Enter to advance
  }, [onChange]);

  const handleFocus = useCallback(() => setIsFocused(true), []);
  const handleBlur = useCallback(() => setIsFocused(false), []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && isValid) {
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
  }, [isValid, onNext]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="Who is your ideal customer?"
      stepDescription="Job title or role. Be specific — 'CTO at Series B startups' beats 'tech people'."
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-content-item ob-animate-in">
        <div className={`flex items-center gap-3 px-4 py-4 rounded-[var(--radius-md)] border bg-[var(--bg-surface)] transition-all duration-200 ${isFocused ? "border-[var(--rf-charcoal)] ring-2 ring-[var(--rf-charcoal)]/10" : "border-[var(--border-2)]"}`}>
          <User size={18} className={`flex-shrink-0 transition-colors ${isFocused ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)]"}`} />
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="e.g. VP of Engineering at mid-market SaaS"
            className="flex-1 bg-transparent border-none outline-none text-[16px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40"
          />
        </div>
      </div>

      {/* Quick personas */}
      <div className="ob-content-item ob-interactive mt-6">
        <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3">QUICK SELECT</p>
        <div className="grid grid-cols-2 gap-3">
          {PERSONAS.map(persona => {
            const Icon = persona.icon;
            const isSelected = value === persona.label;
            return (
              <button
                key={persona.label}
                onClick={() => handlePersonaClick(persona.label)}
                className={`p-4 rounded-[var(--radius-md)] border text-left transition-all ${isSelected
                    ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)]"
                    : "bg-[var(--bg-surface)] border-[var(--border-2)] hover:border-[var(--border-1)]"
                  }`}
              >
                <Icon size={18} className={`mb-2 ${isSelected ? "text-[var(--rf-ivory)]" : "text-[var(--ink-3)]"}`} />
                <p className={`text-[13px] font-semibold ${isSelected ? "text-[var(--rf-ivory)]" : "text-[var(--ink-1)]"}`}>
                  {persona.label}
                </p>
                <p className={`text-[11px] mt-1 ${isSelected ? "text-white/60" : "text-[var(--ink-3)]"}`}>
                  {persona.desc}
                </p>
              </button>
            );
          })}
        </div>
      </div>
    </OnboardingLayout>
  );
}
