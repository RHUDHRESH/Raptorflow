"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Target, AlertTriangle, ArrowRight } from "lucide-react";

interface PageCoreProblemProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const TEMPLATES = [
  { label: "Too slow", text: "Teams waste hours on manual tasks that could be automated" },
  { label: "Too expensive", text: "Companies pay 3x more than they should for outdated solutions" },
  { label: "Too complex", text: "Small businesses can't afford enterprise-grade tools" },
];

export function PageCoreProblem({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageCoreProblemProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const isValid = value.trim().length >= 10;

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

  // Card animation on valid
  useEffect(() => {
    if (cardRef.current && isValid) {
      gsap.fromTo(cardRef.current,
        { opacity: 0, x: -20 },
        { opacity: 1, x: 0, duration: 0.4, ease: "power2.out" }
      );
    }
  }, [isValid]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  }, [onChange]);

  const handleTemplateClick = useCallback((text: string) => {
    onChange(text);
    inputRef.current?.focus();
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
      stepTitle="What core problem do you solve?"
      stepDescription="The pain point that keeps your customers up at night."
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-content-item ob-animate-in">
        <div className={`flex items-center gap-3 px-4 py-4 rounded-[var(--radius-md)] border bg-[var(--bg-surface)] transition-all duration-200 ${isFocused ? "border-[var(--rf-charcoal)] ring-2 ring-[var(--rf-charcoal)]/10" : "border-[var(--border-2)]"}`}>
          <Target size={18} className={`flex-shrink-0 transition-colors ${isFocused ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)]"}`} />
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="e.g. Startups struggle to hire senior marketing talent"
            className="flex-1 bg-transparent border-none outline-none text-[16px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40"
          />
        </div>

        {/* Impact preview */}
        {isValid && (
          <div ref={cardRef} className="mt-5 p-4 rounded-[var(--radius-md)] border-l-4 border-[var(--rf-charcoal)] bg-[var(--bg-surface)]">
            <div className="flex items-start gap-3">
              <AlertTriangle size={18} className="text-[var(--rf-charcoal)] mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-[11px] font-mono text-[var(--ink-3)] mb-1">THE PROBLEM</p>
                <p className="text-[15px] text-[var(--ink-1)] font-medium">{value.trim()}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Templates */}
      {!isValid && (
        <div className="ob-content-item ob-animate-in mt-6">
          <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3">COMMON PROBLEM TYPES</p>
          <div className="space-y-2">
            {TEMPLATES.map(template => (
              <button
                key={template.label}
                onClick={() => handleTemplateClick(template.text)}
                className="w-full flex items-center justify-between p-3 rounded-[var(--radius-md)] border border-[var(--border-2)] hover:border-[var(--rf-charcoal)]/30 hover:bg-[var(--bg-surface)] transition-all text-left group"
              >
                <span className="text-[13px] text-[var(--ink-2)]">{template.text}</span>
                <ArrowRight size={14} className="text-[var(--ink-3)] opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            ))}
          </div>
        </div>
      )}
    </OnboardingLayout>
  );
}
