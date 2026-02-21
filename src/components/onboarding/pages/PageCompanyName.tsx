"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Info, Building2 } from "lucide-react";

interface PageCompanyNameProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

export function PageCompanyName({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageCompanyNameProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);
  const underlineRef = useRef<HTMLDivElement>(null);
  const charCountRef = useRef<HTMLSpanElement>(null);
  const isValid = value.trim().length > 0;
  const [isFocused, setIsFocused] = useState(false);

  // Auto-focus with elegant delay
  useEffect(() => {
    const t = setTimeout(() => {
      inputRef.current?.focus();
      // Focus animation
      gsap.fromTo(inputRef.current,
        { opacity: 0.7 },
        { opacity: 1, duration: 0.3 }
      );
    }, 500);
    return () => clearTimeout(t);
  }, []);

  // Content entrance animation
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".ob-content-item",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  // Auto-capitalize first letter
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    const capitalized = raw.length > 0 ? raw.charAt(0).toUpperCase() + raw.slice(1) : raw;
    onChange(capitalized);

    // Animate underline fill
    if (underlineRef.current) {
      const fillPercent = Math.min((capitalized.trim().length / 30) * 100, 100);
      gsap.to(underlineRef.current, {
        width: `${fillPercent}%`,
        duration: 0.3,
        ease: "power2.out"
      });
    }

    // Animate character count
    if (charCountRef.current && capitalized.length > 0) {
      gsap.fromTo(charCountRef.current,
        { scale: 1.2, color: "var(--rf-charcoal)" },
        { scale: 1, color: "var(--ink-3)", duration: 0.2 }
      );
    }
  }, [onChange]);

  // Focus animations
  const handleFocus = useCallback(() => {
    setIsFocused(true);
    if (wrapperRef.current) {
      gsap.to(wrapperRef.current, {
        scale: 1.01,
        duration: 0.2,
        ease: "power2.out"
      });
    }
  }, []);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    if (wrapperRef.current) {
      gsap.to(wrapperRef.current, {
        scale: 1,
        duration: 0.2,
        ease: "power2.out"
      });
    }
  }, []);

  // Shake animation on invalid Enter
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "Enter") return;
      if (isValid) {
        // Success feedback
        gsap.to(wrapperRef.current, {
          scale: 0.98,
          duration: 0.1,
          yoyo: true,
          repeat: 1,
          ease: "power2.inOut",
          onComplete: () => onNext()
        });
      } else {
        // Shake animation
        const tl = gsap.timeline();
        tl.to(wrapperRef.current, { x: -8, duration: 0.06 })
          .to(wrapperRef.current, { x: 8, duration: 0.06 })
          .to(wrapperRef.current, { x: -6, duration: 0.06 })
          .to(wrapperRef.current, { x: 6, duration: 0.06 })
          .to(wrapperRef.current, { x: 0, duration: 0.1, ease: "power2.out" });
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isValid, onNext]);

  // Preview reveal animation
  useEffect(() => {
    if (previewRef.current) {
      if (isValid) {
        gsap.fromTo(previewRef.current,
          { opacity: 0, y: 10, height: 0 },
          { opacity: 1, y: 0, height: "auto", duration: 0.35, ease: "power2.out" }
        );
      } else {
        gsap.to(previewRef.current, {
          opacity: 0,
          y: -10,
          height: 0,
          duration: 0.2
        });
      }
    }
  }, [isValid]);

  const fillPercent = Math.min((value.trim().length / 30) * 100, 100);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="What's your company called?"
      stepDescription="This will become the name tied to your marketing cockpit."
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      {/* Hero input */}
      <div ref={wrapperRef} className="ob-content-item ob-animate-in mt-2">
        <div className="relative">
          <Building2 
            size={24} 
            className={`absolute left-0 top-1/2 -translate-y-1/2 transition-colors duration-200 ${isFocused ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)]"}`}
          />
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="e.g. RaptorFlow"
            maxLength={60}
            autoComplete="organization"
            className="w-full bg-transparent border-none outline-none text-[32px] md:text-[42px] font-bold text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/30 tracking-[-0.02em] leading-tight pl-10"
          />
        </div>
        {/* Animated underline */}
        <div className="h-[3px] bg-[var(--border-2)] mt-4 rounded-full overflow-hidden">
          <div
            ref={underlineRef}
            className="h-full bg-[var(--rf-charcoal)] rounded-full"
            style={{ width: `${fillPercent}%` }}
          />
        </div>
        <div className="flex justify-between mt-2">
          <span ref={charCountRef} className="text-[11px] font-mono text-[var(--ink-3)]">
            {value.length}/60
          </span>
          {value.length >= 30 && (
            <span className="text-[11px] font-mono text-[var(--status-success)]">
              Looking good
            </span>
          )}
        </div>
      </div>

      {/* Live brand preview */}
      <div
        ref={previewRef}
        className="ob-content-item ob-animate-in mt-6 overflow-hidden"
        style={{ height: isValid ? "auto" : 0, opacity: isValid ? 1 : 0 }}
      >
        <div className="p-4 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)] relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-[var(--rf-charcoal)] to-transparent" />
          <p className="text-[14px] text-[var(--ink-2)]">
            Welcome to{" "}
            <span className="font-semibold text-[var(--ink-1)]">{value.trim()}</span>
            &rsquo;s marketing cockpit.
          </p>
        </div>
      </div>

      {/* Keyboard hint with pulse */}
      <div className="ob-content-item ob-animate-in mt-5 flex items-center gap-2">
        <kbd
          className={`px-2.5 py-1.5 text-[11px] font-mono rounded border transition-all duration-300 ${isValid
              ? "border-[var(--rf-charcoal)] text-[var(--ink-1)] bg-[var(--bg-surface)]"
              : "border-[var(--border-1)] text-[var(--ink-3)] bg-transparent"
            }`}
        >
          ↵ Enter
        </kbd>
        <span className="text-[11px] text-[var(--ink-3)]">to continue</span>
        {isValid && (
          <span className="ml-auto text-[11px] text-[var(--status-success)] font-medium animate-pulse">
            Ready
          </span>
        )}
      </div>

      {/* Info box */}
      <div className="ob-content-item ob-animate-in mt-8 flex items-start gap-3 p-4 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)] hover:border-[var(--border-2)] transition-colors">
        <Info size={16} className="text-[var(--ink-3)] mt-0.5 flex-shrink-0" />
        <p className="text-[13px] text-[var(--ink-3)] leading-relaxed">
          Your company name anchors every piece of content. It appears in brand voice calibration, outreach templates, and content headers.
        </p>
      </div>
    </OnboardingLayout>
  );
}
