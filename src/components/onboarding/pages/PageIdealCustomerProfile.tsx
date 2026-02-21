"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Users, Check } from "lucide-react";

interface PageIdealCustomerProfileProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const PROMPTS = [
  "Company size: 10-50 employees",
  "Revenue: $1M-$10M ARR",
  "Tech stack: Modern SaaS tools",
  "Location: North America",
  "Decision speed: 1-3 months",
];

export function PageIdealCustomerProfile({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageIdealCustomerProfileProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const isValid = value.trim().length >= 15;

  useEffect(() => {
    const t = setTimeout(() => textareaRef.current?.focus(), 400);
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

  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    // Auto-resize
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  }, [onChange]);

  const handlePromptClick = useCallback((prompt: string) => {
    const current = value.trim();
    const separator = current ? "\n" : "";
    onChange(current + separator + prompt);
    textareaRef.current?.focus();
  }, [value, onChange]);

  const handleFocus = useCallback(() => setIsFocused(true), []);
  const handleBlur = useCallback(() => setIsFocused(false), []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && (e.metaKey || e.ctrlKey) && isValid) {
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
      stepTitle="Describe your ideal customer profile"
      stepDescription="Company size, industry, budget, location — the more specific, the better."
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-content-item ob-animate-in">
        <div className={`relative rounded-[var(--radius-md)] border bg-[var(--bg-surface)] transition-all duration-200 ${isFocused ? "border-[var(--rf-charcoal)] ring-2 ring-[var(--rf-charcoal)]/10" : "border-[var(--border-2)]"}`}>
          <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border-1)]">
            <Users size={16} className={`transition-colors ${isFocused ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)]"}`} />
            <span className="text-[12px] font-medium text-[var(--ink-3)]">Customer Profile</span>
            {isValid && <Check size={14} className="text-[var(--status-success)] ml-auto" />}
          </div>
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="e.g. B2B SaaS companies with 20-100 employees, $2M-$20M ARR, primarily in fintech or healthcare verticals..."
            className="w-full bg-transparent border-none outline-none px-4 py-3 text-[15px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40 resize-none"
            style={{ minHeight: "100px" }}
          />
        </div>
        <p className="mt-2 text-[11px] text-[var(--ink-3)]">
          {value.length} characters · {isValid ? "Good detail" : "Add more detail"}
        </p>
      </div>

      {/* Prompts */}
      <div className="ob-content-item ob-animate-in mt-5">
        <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3">ADD DETAIL</p>
        <div className="flex flex-wrap gap-2">
          {PROMPTS.map(prompt => (
            <button
              key={prompt}
              onClick={() => handlePromptClick(prompt)}
              className="px-3 py-1.5 text-[12px] rounded-full border border-[var(--border-2)] text-[var(--ink-2)] hover:border-[var(--rf-charcoal)]/40 hover:text-[var(--ink-1)] hover:bg-[var(--bg-surface)] transition-all"
            >
              + {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Keyboard hint */}
      <div className="ob-content-item ob-animate-in mt-6 flex items-center gap-2">
        <kbd className="px-2 py-1 text-[11px] font-mono rounded border border-[var(--border-2)] text-[var(--ink-3)]">
          Ctrl + Enter
        </kbd>
        <span className="text-[11px] text-[var(--ink-3)]">to continue</span>
      </div>
    </OnboardingLayout>
  );
}
