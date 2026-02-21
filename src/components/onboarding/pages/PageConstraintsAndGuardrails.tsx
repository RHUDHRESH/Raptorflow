"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Shield, Plus, X, AlertTriangle, CheckCircle, Lock } from "lucide-react";

interface PageConstraintsAndGuardrailsProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const SUGGESTED = [
  "No competitor mentions",
  "No pricing discussions",
  "No legal/medical claims",
  "Avoid specific client names",
  "Keep under 280 characters",
  "No discounts or promos",
];

export function PageConstraintsAndGuardrails({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageConstraintsAndGuardrailsProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const summaryRef = useRef<HTMLDivElement>(null);
  const [inputValue, setInputValue] = useState("");
  const items = value ? value.split(",").map(s => s.trim()).filter(Boolean) : [];
  const isValid = items.length >= 1;

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
    if (items.length > 0) {
      gsap.fromTo(".constraint-item",
        { opacity: 0, scale: 0.9, x: -10 },
        { opacity: 1, scale: 1, x: 0, duration: 0.25, stagger: 0.05, ease: "back.out(1.5)" }
      );
    }
  }, [items.length]);

  // Summary animation on valid
  useEffect(() => {
    if (summaryRef.current && isValid) {
      gsap.fromTo(summaryRef.current,
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }
      );
    }
  }, [isValid]);

  const handleAdd = useCallback(() => {
    if (!inputValue.trim()) return;
    const newItems = [...items, inputValue.trim()];
    onChange(newItems.join(", "));
    setInputValue("");
    inputRef.current?.focus();
  }, [inputValue, items, onChange]);

  const handleRemove = useCallback((index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    onChange(newItems.join(", "));
  }, [items, onChange]);

  const handleSuggestedClick = useCallback((text: string) => {
    if (items.includes(text)) return;
    const newItems = [...items, text];
    onChange(newItems.join(", "));
  }, [items, onChange]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAdd();
    }
  }, [handleAdd]);

  // Complete button animation
  const handleComplete = useCallback(() => {
    if (isValid) {
      gsap.to(wrapperRef.current, {
        scale: 0.98,
        duration: 0.1,
        yoyo: true,
        repeat: 1,
        onComplete: () => onNext()
      });
    }
  }, [isValid, onNext]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="Constraints & guardrails"
      stepDescription="Rules for our AI: things to avoid, requirements to follow, boundaries to respect."
      onBack={onBack}
      onNext={handleComplete}
      canGoNext={isValid}
      showBack={!!onBack}
      nextLabel="Complete Setup"
    >
      <div ref={wrapperRef} className="ob-animate-in">
        {/* Input */}
        <div className="ob-content-item ob-interactive flex gap-2">
          <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] border border-[var(--border-2)] bg-[var(--bg-surface)] focus-within:border-[var(--rf-charcoal)] focus-within:ring-2 focus-within:ring-[var(--rf-charcoal)]/10 transition-all">
            <Shield size={16} className="text-[var(--ink-3)]" />
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Add a constraint or rule..."
              className="flex-1 bg-transparent border-none outline-none text-[15px] text-[var(--ink-1)] placeholder:text-[var(--ink-3)]/40"
            />
          </div>
          <button
            onClick={handleAdd}
            disabled={!inputValue.trim()}
            className="px-4 py-3 rounded-[var(--radius-md)] bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] disabled:opacity-40 transition-opacity"
          >
            <Plus size={18} />
          </button>
        </div>

        {/* Items list */}
        {items.length > 0 && (
          <div className="ob-content-item ob-interactive mt-4 flex flex-wrap gap-2">
            {items.map((item, i) => (
              <div
                key={i}
                className="constraint-item group flex items-center gap-2 px-3 py-2 rounded-full bg-[var(--rf-charcoal)] text-[var(--rf-ivory)]"
              >
                <Lock size={12} className="opacity-60" />
                <span className="text-[13px]">{item}</span>
                <button
                  onClick={() => handleRemove(i)}
                  className="w-5 h-5 rounded-full flex items-center justify-center text-white/50 hover:bg-white/10 hover:text-white transition-colors"
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Suggested */}
        {items.length < 6 && (
          <div className="ob-content-item ob-interactive mt-6">
            <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3 flex items-center gap-1.5">
              <AlertTriangle size={12} />
              COMMON GUARDRAILS
            </p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED.filter(s => !items.includes(s)).map(text => (
                <button
                  key={text}
                  onClick={() => handleSuggestedClick(text)}
                  className="group flex items-center gap-1 px-3 py-1.5 text-[12px] rounded-full border border-[var(--border-2)] text-[var(--ink-2)] hover:border-[var(--rf-charcoal)]/40 hover:text-[var(--ink-1)] hover:bg-[var(--bg-surface)] transition-all"
                >
                  <Plus size={12} className="opacity-50 group-hover:opacity-100" />
                  {text}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Summary card */}
        {isValid && (
          <div ref={summaryRef} className="ob-content-item ob-animate-in mt-8 p-5 rounded-[var(--radius-lg)] bg-[var(--bg-surface)] border border-[var(--border-1)]">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-[var(--status-success)]/10 flex items-center justify-center flex-shrink-0">
                <CheckCircle size={18} className="text-[var(--status-success)]" />
              </div>
              <div>
                <p className="text-[14px] font-semibold text-[var(--ink-1)]">Your marketing foundation is almost ready</p>
                <p className="text-[13px] text-[var(--ink-3)] mt-1">
                  {items.length} guardrail{items.length !== 1 ? "s" : ""} set. Click &ldquo;Complete Setup&rdquo; to finish.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Count */}
        <p className="mt-4 text-[11px] text-[var(--ink-3)]">
          {items.length} guardrail{items.length !== 1 ? "s" : ""} added
          {items.length >= 2 && <span className="text-[var(--status-success)] ml-2">✓ Good coverage</span>}
        </p>
      </div>
    </OnboardingLayout>
  );
}
