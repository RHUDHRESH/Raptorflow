"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { AlertCircle, Plus, X, ArrowRight } from "lucide-react";

interface PageTopPainPointsProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const SUGGESTED = [
  "Too time-consuming",
  "Too expensive",
  "Poor quality results",
  "Hard to implement",
  "Lack of expertise",
  "Overwhelming complexity",
];

export function PageTopPainPoints({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageTopPainPointsProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
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

  // Animate items when added/removed
  useEffect(() => {
    if (items.length > 0) {
      gsap.fromTo(".pain-point-item",
        { opacity: 0, scale: 0.9, x: -10 },
        { opacity: 1, scale: 1, x: 0, duration: 0.25, stagger: 0.05, ease: "back.out(1.5)" }
      );
    }
  }, [items.length]);

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

  const handleSuggestedClick = useCallback((painPoint: string) => {
    if (items.includes(painPoint)) return;
    const newItems = [...items, painPoint];
    onChange(newItems.join(", "));
  }, [items, onChange]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAdd();
    }
  }, [handleAdd]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="What are your customers' top pain points?"
      stepDescription="The frustrations that make them search for solutions like yours."
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in">
        {/* Input */}
        <div className="ob-content-item ob-interactive flex gap-2">
          <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] border border-[var(--border-2)] bg-[var(--bg-surface)] focus-within:border-[var(--rf-charcoal)] focus-within:ring-2 focus-within:ring-[var(--rf-charcoal)]/10 transition-all">
            <AlertCircle size={16} className="text-[var(--ink-3)]" />
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Add a pain point..."
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
                className="pain-point-item group flex items-center gap-2 px-3 py-2 rounded-full bg-[var(--bg-surface)] border border-[var(--border-2)] hover:border-[var(--rf-charcoal)]/30 transition-colors"
              >
                <span className="text-[13px] text-[var(--ink-1)]">{item}</span>
                <button
                  onClick={() => handleRemove(i)}
                  className="w-5 h-5 rounded-full flex items-center justify-center text-[var(--ink-3)] hover:bg-[var(--border-1)] hover:text-[var(--ink-1)] transition-colors"
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Suggested */}
        {items.length < 5 && (
          <div className="ob-content-item ob-interactive mt-6">
            <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3">SUGGESTED</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED.filter(s => !items.includes(s)).map(painPoint => (
                <button
                  key={painPoint}
                  onClick={() => handleSuggestedClick(painPoint)}
                  className="group flex items-center gap-1 px-3 py-1.5 text-[12px] rounded-full border border-[var(--border-2)] text-[var(--ink-2)] hover:border-[var(--rf-charcoal)]/40 hover:text-[var(--ink-1)] hover:bg-[var(--bg-surface)] transition-all"
                >
                  <Plus size={12} className="opacity-50 group-hover:opacity-100" />
                  {painPoint}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Count */}
        <p className="mt-4 text-[11px] text-[var(--ink-3)]">
          {items.length} pain point{items.length !== 1 ? "s" : ""} added
          {items.length >= 3 && <span className="text-[var(--status-success)] ml-2">✓ Great coverage</span>}
        </p>
      </div>
    </OnboardingLayout>
  );
}
