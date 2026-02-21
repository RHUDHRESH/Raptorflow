"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Globe, Check, AlertCircle, ExternalLink } from "lucide-react";

interface PageCompanyWebsiteProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

export function PageCompanyWebsite({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageCompanyWebsiteProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const statusRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [isValid, setIsValid] = useState(false);

  // URL validation
  const validateUrl = useCallback((url: string) => {
    if (!url) return true; // Optional field
    const pattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
    return pattern.test(url);
  }, []);

  useEffect(() => {
    setIsValid(validateUrl(value));
  }, [value, validateUrl]);

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

  // Handle input with animation
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);

    // Animate status indicator
    if (statusRef.current && newValue) {
      const valid = validateUrl(newValue);
      gsap.fromTo(statusRef.current,
        { scale: 0.8, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.2 }
      );
    }
  }, [onChange, validateUrl]);

  // Focus animations
  const handleFocus = useCallback(() => {
    setIsFocused(true);
    gsap.to(wrapperRef.current, { 
      boxShadow: "0 0 0 3px rgba(42, 37, 41, 0.08)",
      duration: 0.2 
    });
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    gsap.to(wrapperRef.current, { 
      boxShadow: "0 0 0 0px rgba(42, 37, 41, 0)",
      duration: 0.2 
    });
  }, []);

  // Skip button animation
  const handleSkip = useCallback(() => {
    gsap.to(wrapperRef.current, {
      opacity: 0.5,
      duration: 0.15,
      yoyo: true,
      repeat: 1,
      onComplete: () => onNext()
    });
  }, [onNext]);

  // Enter key handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        if (!value || isValid) {
          gsap.to(wrapperRef.current, {
            scale: 0.98,
            duration: 0.1,
            yoyo: true,
            repeat: 1,
            onComplete: () => onNext()
          });
        } else {
          // Shake on invalid
          const tl = gsap.timeline();
          tl.to(wrapperRef.current, { x: -5, duration: 0.08 })
            .to(wrapperRef.current, { x: 5, duration: 0.08 })
            .to(wrapperRef.current, { x: -5, duration: 0.08 })
            .to(wrapperRef.current, { x: 5, duration: 0.08 })
            .to(wrapperRef.current, { x: 0, duration: 0.1, ease: "power2.out" });
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [value, isValid, onNext]);

  const hasValue = value.trim().length > 0;
  const canProceed = !hasValue || isValid;

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="Company website (optional)"
      stepDescription="We use this to understand your brand better. Skip if you don't have one yet."
      onBack={onBack}
      onNext={onNext}
      canGoNext={canProceed}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-content-item ob-animate-in">
        <div className={`flex items-center gap-3 px-4 py-4 rounded-[var(--radius-md)] border bg-[var(--bg-surface)] transition-all duration-200 ${isFocused ? "border-[var(--rf-charcoal)]" : "border-[var(--border-2)]"} ${!isValid && hasValue ? "border-red-300" : ""}`}>
          <Globe size={18} className={`flex-shrink-0 transition-colors ${isFocused ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)]"}`} />
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="https://yourcompany.com"
            autoComplete="url"
            className="flex-1 bg-transparent border-none outline-none text-[16px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40"
          />
          {hasValue && (
            <div ref={statusRef}>
              {isValid ? (
                <Check size={18} className="text-[var(--status-success)]" />
              ) : (
                <AlertCircle size={18} className="text-red-400" />
              )}
            </div>
          )}
        </div>

        {/* Validation message */}
        {!isValid && hasValue && (
          <p className="mt-2 text-[12px] text-red-500 flex items-center gap-1">
            <AlertCircle size={12} />
            Please enter a valid URL
          </p>
        )}

        {/* Preview hint */}
        {isValid && hasValue && (
          <div className="mt-3 flex items-center gap-2 text-[12px] text-[var(--ink-3)]">
            <ExternalLink size={12} />
            <span>We'll analyze your site for brand insights</span>
          </div>
        )}
      </div>

      {/* Skip option */}
      <div className="ob-content-item ob-animate-in mt-6">
        <button
          onClick={handleSkip}
          className="group flex items-center gap-3 p-4 rounded-[var(--radius-md)] border border-dashed border-[var(--border-2)] hover:border-[var(--rf-charcoal)]/30 hover:bg-[var(--bg-surface)] transition-all w-full text-left"
        >
          <div className="w-10 h-10 rounded-full bg-[var(--border-1)] flex items-center justify-center group-hover:bg-[var(--rf-charcoal)]/10 transition-colors">
            <span className="text-[14px] text-[var(--ink-3)] group-hover:text-[var(--rf-charcoal)]">→</span>
          </div>
          <div>
            <p className="text-[14px] font-medium text-[var(--ink-1)]">I don't have a website yet</p>
            <p className="text-[12px] text-[var(--ink-3)]">Continue without this info</p>
          </div>
        </button>
      </div>

      {/* Info box */}
      <div className="ob-content-item ob-animate-in mt-6 flex items-start gap-3 p-4 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)]">
        <Globe size={16} className="text-[var(--ink-3)] mt-0.5 flex-shrink-0" />
        <p className="text-[13px] text-[var(--ink-3)] leading-relaxed">
          This helps us understand your visual identity, messaging, and positioning. We'll never scrape or store your content without permission.
        </p>
      </div>
    </OnboardingLayout>
  );
}
