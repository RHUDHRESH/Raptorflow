"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Package, Sparkles, ArrowRight } from "lucide-react";

interface PagePrimaryOfferProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const EXAMPLES = [
  { label: "SaaS", text: "AI-powered analytics platform for e-commerce" },
  { label: "Service", text: "Fractional CMO services for Series A startups" },
  { label: "Product", text: "Premium organic skincare subscription" },
];

export function PagePrimaryOffer({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PagePrimaryOfferProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const isValid = value.trim().length >= 5;

  // Auto-focus
  useEffect(() => {
    const t = setTimeout(() => inputRef.current?.focus(), 400);
    return () => clearTimeout(t);
  }, []);

  // Entrance animation
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".ob-content-item",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  // Preview animation
  useEffect(() => {
    if (previewRef.current) {
      if (isValid) {
        gsap.fromTo(previewRef.current,
          { opacity: 0, y: 10 },
          { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }
        );
      }
    }
  }, [isValid]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  }, [onChange]);

  const handleExampleClick = useCallback((text: string) => {
    onChange(text);
    inputRef.current?.focus();
    gsap.fromTo(inputRef.current,
      { opacity: 0.6 },
      { opacity: 1, duration: 0.3 }
    );
  }, [onChange]);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);

  // Enter key handler
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
      stepTitle="What's your main product or service?"
      stepDescription="The one thing you sell that everything else revolves around."
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-content-item ob-animate-in">
        <div className={`flex items-center gap-3 px-4 py-4 rounded-[var(--radius-md)] border bg-[var(--bg-surface)] transition-all duration-200 ${isFocused ? "border-[var(--rf-charcoal)] ring-2 ring-[var(--rf-charcoal)]/10" : "border-[var(--border-2)]"}`}>
          <Package size={18} className={`flex-shrink-0 transition-colors ${isFocused ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)]"}`} />
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="e.g. AI-powered content platform"
            className="flex-1 bg-transparent border-none outline-none text-[16px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40"
          />
        </div>

        {/* Live preview */}
        {isValid && (
          <div ref={previewRef} className="mt-4 p-4 rounded-[var(--radius-md)] bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-white/5 rounded-full blur-2xl" />
            <div className="relative flex items-start gap-3">
              <Sparkles size={16} className="mt-0.5 flex-shrink-0 opacity-60" />
              <div>
                <p className="text-[11px] font-mono opacity-50 mb-1">YOUR OFFER</p>
                <p className="text-[15px] font-medium">{value.trim()}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Examples */}
      {!isValid && (
        <div className="ob-content-item ob-animate-in mt-6">
          <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3">EXAMPLES</p>
          <div className="space-y-2">
            {EXAMPLES.map(example => (
              <button
                key={example.label}
                onClick={() => handleExampleClick(example.text)}
                className="w-full flex items-center justify-between p-3 rounded-[var(--radius-md)] border border-[var(--border-2)] hover:border-[var(--rf-charcoal)]/30 hover:bg-[var(--bg-surface)] transition-all text-left group"
              >
                <div className="flex items-center gap-3">
                  <span className="text-[11px] font-mono text-[var(--ink-3)] w-16">{example.label}</span>
                  <span className="text-[13px] text-[var(--ink-2)]">{example.text}</span>
                </div>
                <ArrowRight size={14} className="text-[var(--ink-3)] opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            ))}
          </div>
        </div>
      )}
    </OnboardingLayout>
  );
}
