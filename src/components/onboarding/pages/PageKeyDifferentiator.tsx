"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Star, Sparkles } from "lucide-react";

interface PageKeyDifferentiatorProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

export function PageKeyDifferentiator({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageKeyDifferentiatorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const isValid = value.trim().length >= 10;

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

  useEffect(() => {
    if (cardRef.current && isValid) {
      gsap.fromTo(cardRef.current,
        { opacity: 0, scale: 0.95 },
        { opacity: 1, scale: 1, duration: 0.4, ease: "power2.out" }
      );
    }
  }, [isValid]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 140)}px`;
  }, [onChange]);

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
      stepTitle="What makes you different?"
      stepDescription="Your unique edge. Why should customers choose you over alternatives?"
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in">
        <div className="ob-content-item ob-interactive">
          <div className={`relative rounded-[var(--radius-md)] border bg-[var(--bg-surface)] transition-all duration-200 ${isFocused ? "border-[var(--rf-charcoal)] ring-2 ring-[var(--rf-charcoal)]/10" : "border-[var(--border-2)]"}`}>
            <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border-1)]">
              <Star size={16} className={`transition-colors ${isFocused ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)]"}`} />
              <span className="text-[12px] font-medium text-[var(--ink-3)]">Your Differentiator</span>
            </div>
            <textarea
              ref={textareaRef}
              value={value}
              onChange={handleChange}
              onFocus={handleFocus}
              onBlur={handleBlur}
              placeholder="e.g. We're the only platform that combines AI with human expertise, delivering results 10x faster than traditional agencies at 1/10th the cost..."
              className="w-full bg-transparent border-none outline-none px-4 py-3 text-[15px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40 resize-none"
              style={{ minHeight: "100px" }}
            />
          </div>
          <p className="mt-2 text-[11px] text-[var(--ink-3)]">
            {value.length} characters · {isValid ? "Good answer" : "Add more detail"}
          </p>
        </div>

        {/* Preview card */}
        {isValid && (
          <div ref={cardRef} className="ob-content-item ob-animate-in mt-6 p-5 rounded-[var(--radius-lg)] bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-3xl" />
            <div className="relative flex items-start gap-3">
              <Sparkles size={18} className="mt-0.5 flex-shrink-0 opacity-60" />
              <div>
                <p className="text-[11px] font-mono opacity-50 mb-2">YOUR EDGE</p>
                <p className="text-[15px] leading-relaxed">{value.trim()}</p>
              </div>
            </div>
          </div>
        )}

        {/* Keyboard hint */}
        <div className="ob-content-item ob-animate-in mt-6 flex items-center gap-2">
          <kbd className="px-2 py-1 text-[11px] font-mono rounded border border-[var(--border-2)] text-[var(--ink-3)]">
            Ctrl + Enter
          </kbd>
          <span className="text-[11px] text-[var(--ink-3)]">to continue</span>
        </div>
      </div>
    </OnboardingLayout>
  );
}
