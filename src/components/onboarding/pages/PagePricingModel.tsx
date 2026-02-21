"use client";

import { useEffect, useRef, useCallback } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { DollarSign, Tag, CreditCard, Building2, Users, ArrowRight } from "lucide-react";

interface PagePricingModelProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const MODELS = [
  { label: "SaaS / Subscription", icon: CreditCard, desc: "Monthly or annual recurring" },
  { label: "One-time Purchase", icon: Tag, desc: "Perpetual license or product" },
  { label: "Enterprise / Custom", icon: Building2, desc: "Deal-based pricing" },
  { label: "Usage-based", icon: DollarSign, desc: "Pay as you go" },
  { label: "Freemium", icon: Users, desc: "Free tier with upgrades" },
];

export function PagePricingModel({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PagePricingModelProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".pricing-card",
        { opacity: 0, y: 25 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  const handleSelect = useCallback((label: string) => {
    onChange(label);
    const card = document.querySelector(`[data-pricing="${label}"]`);
    if (card) {
      gsap.fromTo(card,
        { scale: 0.95 },
        { scale: 1.03, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out" }
      );
    }
    // Note: User must click Continue or press Enter to advance
  }, [onChange]);

  // Enter to skip
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Enter" && !value) {
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
  }, [value, onNext]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="Pricing model (optional)"
      stepDescription="How do customers pay for your product or service?"
      onBack={onBack}
      onNext={onNext}
      canGoNext={true}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in ob-interactive grid grid-cols-1 gap-3">
        {MODELS.map((model) => {
          const Icon = model.icon;
          const isSelected = value === model.label;
          return (
            <button
              key={model.label}
              data-pricing={model.label}
              onClick={() => handleSelect(model.label)}
              className={`pricing-card flex items-center gap-4 p-4 rounded-[var(--radius-md)] border transition-all text-left ${isSelected
                  ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)]"
                  : "bg-[var(--bg-surface)] border-[var(--border-1)] hover:border-[var(--border-2)]"
                }`}
            >
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${isSelected ? "bg-white/10" : "bg-[var(--border-1)]"}`}>
                <Icon size={20} className={isSelected ? "text-[var(--rf-ivory)]" : "text-[var(--ink-3)]"} />
              </div>
              <div className="flex-1">
                <p className={`text-[15px] font-semibold ${isSelected ? "text-[var(--rf-ivory)]" : "text-[var(--ink-1)]"}`}>
                  {model.label}
                </p>
                <p className={`text-[12px] mt-0.5 ${isSelected ? "text-white/50" : "text-[var(--ink-3)]"}`}>
                  {model.desc}
                </p>
              </div>
              <ArrowRight size={16} className={`transition-transform ${isSelected ? "translate-x-1 opacity-60" : "opacity-0"}`} />
            </button>
          );
        })}
      </div>

      {/* Skip hint */}
      <div className="ob-animate-in mt-6 flex items-center gap-2 p-3 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-dashed border-[var(--border-2)]">
        <ArrowRight size={14} className="text-[var(--ink-3)]" />
        <span className="text-[13px] text-[var(--ink-2)]">Press Enter to skip</span>
      </div>
    </OnboardingLayout>
  );
}
