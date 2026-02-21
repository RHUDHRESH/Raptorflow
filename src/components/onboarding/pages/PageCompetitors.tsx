"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Swords, Plus, X, Building2 } from "lucide-react";

interface PageCompetitorsProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

export function PageCompetitors({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageCompetitorsProps) {
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

  useEffect(() => {
    if (items.length > 0) {
      gsap.fromTo(".competitor-item",
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
      stepTitle="Who are your main competitors?"
      stepDescription="Direct and indirect alternatives your customers consider."
      onBack={onBack}
      onNext={onNext}
      canGoNext={isValid}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in">
        {/* Input */}
        <div className="ob-content-item ob-interactive flex gap-2">
          <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] border border-[var(--border-2)] bg-[var(--bg-surface)] focus-within:border-[var(--rf-charcoal)] focus-within:ring-2 focus-within:ring-[var(--rf-charcoal)]/10 transition-all">
            <Swords size={16} className="text-[var(--ink-3)]" />
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Add a competitor..."
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
                className="competitor-item group flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--bg-surface)] border border-[var(--border-2)] hover:border-[var(--rf-charcoal)]/30 transition-colors"
              >
                <Building2 size={14} className="text-[var(--ink-3)]" />
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

        {/* Count */}
        <p className="mt-4 text-[11px] text-[var(--ink-3)]">
          {items.length} competitor{items.length !== 1 ? "s" : ""} added
          {items.length >= 2 && <span className="text-[var(--status-success)] ml-2">✓ Good coverage</span>}
        </p>
      </div>
    </OnboardingLayout>
  );
}
