"use client";

import { useEffect, useRef, useCallback } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Target, Users, Zap, BarChart3, Rocket, ArrowRight, Check } from "lucide-react";

interface PageAcquisitionGoalProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const GOALS = [
  { label: "Lead Generation", icon: Users, desc: "Build a pipeline of qualified prospects" },
  { label: "Brand Awareness", icon: Zap, desc: "Get known in your target market" },
  { label: "Customer Acquisition", icon: Target, desc: "Convert prospects to paying customers" },
  { label: "Revenue Growth", icon: BarChart3, desc: "Drive measurable revenue increase" },
  { label: "Market Expansion", icon: Rocket, desc: "Enter new markets or segments" },
];

export function PageAcquisitionGoal({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageAcquisitionGoalProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".goal-card",
        { opacity: 0, y: 30, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.08, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  const handleSelect = useCallback((label: string) => {
    onChange(label);
    const card = document.querySelector(`[data-goal="${label}"]`);
    if (card) {
      gsap.fromTo(card,
        { scale: 0.95 },
        { scale: 1.03, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out" }
      );
    }
    // Note: User must click Continue or press Enter to advance
  }, [onChange]);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="What's your primary acquisition goal?"
      stepDescription="The main outcome you want from your marketing efforts."
      onBack={onBack}
      onNext={onNext}
      canGoNext={!!value}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in ob-interactive space-y-3">
        {GOALS.map((goal) => {
          const Icon = goal.icon;
          const isSelected = value === goal.label;
          return (
            <button
              key={goal.label}
              data-goal={goal.label}
              onClick={() => handleSelect(goal.label)}
              className={`goal-card w-full flex items-center gap-4 p-4 rounded-[var(--radius-lg)] border transition-all text-left ${isSelected
                  ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)] scale-[1.01]"
                  : "bg-[var(--bg-surface)] border-[var(--border-1)] hover:border-[var(--border-2)]"
                }`}
            >
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${isSelected ? "bg-white/10" : "bg-[var(--border-1)]"}`}>
                <Icon size={22} className={isSelected ? "text-[var(--rf-ivory)]" : "text-[var(--ink-3)]"} />
              </div>
              <div className="flex-1">
                <p className={`text-[16px] font-semibold ${isSelected ? "text-[var(--rf-ivory)]" : "text-[var(--ink-1)]"}`}>
                  {goal.label}
                </p>
                <p className={`text-[13px] mt-0.5 ${isSelected ? "text-white/50" : "text-[var(--ink-3)]"}`}>
                  {goal.desc}
                </p>
              </div>
              {isSelected ? (
                <Check size={20} className="opacity-60" />
              ) : (
                <ArrowRight size={18} className="opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
              )}
            </button>
          );
        })}
      </div>
    </OnboardingLayout>
  );
}
