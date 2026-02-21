"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Trophy, Plus, X, Award, Star, TrendingUp, Users } from "lucide-react";

interface PageProofPointsProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const SUGGESTED = [
  { icon: Trophy, text: "Industry awards" },
  { icon: Star, text: "Customer testimonials" },
  { icon: TrendingUp, text: "Growth metrics" },
  { icon: Users, text: "Customer count" },
  { icon: Award, text: "Certifications" },
];

export function PageProofPoints({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageProofPointsProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [inputValue, setInputValue] = useState("");
  const items = value ? value.split(",").map(s => s.trim()).filter(Boolean) : [];

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
      gsap.fromTo(".proof-item",
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

  // Enter to skip
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && !inputValue) {
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
  }, [inputValue, onNext]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="Proof points (optional)"
      stepDescription="Evidence that builds trust: testimonials, metrics, awards, case studies."
      onBack={onBack}
      onNext={onNext}
      canGoNext={true}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in">
        {/* Input */}
        <div className="ob-content-item ob-interactive flex gap-2">
          <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-[var(--radius-md)] border border-[var(--border-2)] bg-[var(--bg-surface)] focus-within:border-[var(--rf-charcoal)] focus-within:ring-2 focus-within:ring-[var(--rf-charcoal)]/10 transition-all">
            <Trophy size={16} className="text-[var(--ink-3)]" />
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Add a proof point..."
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
                className="proof-item group flex items-center gap-2 px-3 py-2 rounded-full bg-amber-50 border border-amber-200 text-amber-800 hover:bg-amber-100 transition-colors"
              >
                <Award size={12} />
                <span className="text-[13px]">{item}</span>
                <button
                  onClick={() => handleRemove(i)}
                  className="w-5 h-5 rounded-full flex items-center justify-center opacity-50 hover:opacity-100 transition-opacity"
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Suggested */}
        <div className="ob-content-item ob-interactive mt-6">
          <p className="text-[11px] font-mono text-[var(--ink-3)] mb-3">COMMON PROOF POINTS</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED.filter(s => !items.includes(s.text)).map(s => {
              const Icon = s.icon;
              return (
                <button
                  key={s.text}
                  onClick={() => handleSuggestedClick(s.text)}
                  className="group flex items-center gap-1.5 px-3 py-1.5 text-[12px] rounded-full border border-[var(--border-2)] text-[var(--ink-2)] hover:border-amber-200 hover:text-amber-700 hover:bg-amber-50 transition-all"
                >
                  <Icon size={12} className="opacity-50 group-hover:opacity-100" />
                  {s.text}
                </button>
              );
            })}
          </div>
        </div>

        {/* Count */}
        {items.length > 0 && (
          <p className="mt-4 text-[11px] text-[var(--ink-3)]">
            {items.length} proof point{items.length !== 1 ? "s" : ""} added
          </p>
        )}
      </div>
    </OnboardingLayout>
  );
}
