"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { FileText, Lightbulb, Check } from "lucide-react";

interface PageCompanyDescriptionProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const SUGGESTIONS = [
  "What problem do you solve?",
  "Who do you help?",
  "What makes you different?",
];

export function PageCompanyDescription({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageCompanyDescriptionProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const charCountRef = useRef<HTMLSpanElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const isValid = value.trim().length >= 10;

  // Auto-focus
  useEffect(() => {
    const t = setTimeout(() => textareaRef.current?.focus(), 400);
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

  // Auto-resize textarea
  const handleInput = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);

    // Auto-resize
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;

    // Animate progress bar
    if (progressRef.current) {
      const progress = Math.min((newValue.length / 150) * 100, 100);
      gsap.to(progressRef.current, {
        width: `${progress}%`,
        duration: 0.3,
        ease: "power2.out"
      });
    }

    // Animate character count
    if (charCountRef.current) {
      gsap.fromTo(charCountRef.current,
        { scale: 1.1 },
        { scale: 1, duration: 0.15 }
      );
    }
  }, [onChange]);

  // Focus animations
  const handleFocus = useCallback(() => {
    setIsFocused(true);
    gsap.to(wrapperRef.current, {
      boxShadow: "0 0 0 3px rgba(42, 37, 41, 0.06)",
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

  // Enter key handler (Ctrl+Enter to submit)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
        if (isValid) {
          gsap.to(wrapperRef.current, {
            scale: 0.98,
            duration: 0.1,
            yoyo: true,
            repeat: 1,
            onComplete: () => onNext()
          });
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isValid, onNext]);

  const handleSuggestionClick = useCallback((suggestion: string) => {
    const current = value.trim();
    const separator = current ? " " : "";
    const newValue = current + separator + suggestion;
    onChange(newValue);

    // Focus and animate
    textareaRef.current?.focus();
    gsap.fromTo(textareaRef.current,
      { opacity: 0.7 },
      { opacity: 1, duration: 0.3 }
    );
  }, [value, onChange]);

  const progress = Math.min((value.length / 150) * 100, 100);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="Describe what your company does"
      stepDescription="Give us the elevator pitch. What do you do and who do you serve?"
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-content-item ob-animate-in">
        <div className={`relative rounded-[var(--radius-md)] border bg-[var(--bg-surface)] transition-all duration-200 ${isFocused ? "border-[var(--rf-charcoal)]" : "border-[var(--border-2)]"}`}>
          <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border-1)]">
            <FileText size={16} className={`transition-colors ${isFocused ? "text-[var(--rf-charcoal)]" : "text-[var(--ink-3)]"}`} />
            <span className="text-[12px] font-medium text-[var(--ink-3)]">Your description</span>
          </div>
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleInput}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="We help [target audience] achieve [desired outcome] through [your unique approach]..."
            rows={4}
            className="w-full bg-transparent border-none outline-none px-4 py-3 text-[15px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40 resize-none"
            style={{ minHeight: "120px" }}
          />
          {/* Progress bar */}
          <div className="px-4 pb-3">
            <div className="h-[3px] bg-[var(--border-1)] rounded-full overflow-hidden">
              <div
                ref={progressRef}
                className="h-full bg-[var(--rf-charcoal)] rounded-full transition-colors"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>

        {/* Character count */}
        <div className="flex justify-between mt-2">
          <span ref={charCountRef} className="text-[11px] font-mono text-[var(--ink-3)]">
            {value.length} characters
          </span>
          <span className={`text-[11px] font-medium transition-colors ${isValid ? "text-[var(--status-success)]" : "text-[var(--ink-3)]"}`}>
            {isValid ? <span className="flex items-center gap-1"><Check size={11} /> Good length</span> : "Min 10 characters"}
          </span>
        </div>
      </div>

      {/* Suggestions */}
      {!isValid && (
        <div className="ob-content-item ob-animate-in mt-5">
          <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3 flex items-center gap-1.5">
            <Lightbulb size={12} />
            INCLUDE THESE ELEMENTS
          </p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map(suggestion => (
              <button
                key={suggestion}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1.5 text-[12px] rounded-full border border-[var(--border-2)] text-[var(--ink-2)] hover:border-[var(--rf-charcoal)]/40 hover:text-[var(--ink-1)] hover:bg-[var(--bg-surface)] transition-all"
              >
                + {suggestion}
              </button>
            ))}
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
    </OnboardingLayout>
  );
}
