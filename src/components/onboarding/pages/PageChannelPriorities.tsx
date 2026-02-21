"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Radio, Linkedin, Twitter, Mail, BookOpen, Youtube, Instagram, Rss, ArrowUp } from "lucide-react";

interface PageChannelPrioritiesProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const CHANNELS = [
  { label: "LinkedIn", icon: Linkedin, effort: "High signal, high effort" },
  { label: "Email", icon: Mail, effort: "Highest ROI, owned channel" },
  { label: "Twitter / X", icon: Twitter, effort: "Fast feedback, broad reach" },
  { label: "Blog / SEO", icon: BookOpen, effort: "Compound returns over time" },
  { label: "YouTube", icon: Youtube, effort: "Deep authority, high trust" },
  { label: "Instagram", icon: Instagram, effort: "Visual brand awareness" },
  { label: "Newsletter", icon: Rss, effort: "Direct, recurring audience" },
];

export function PageChannelPriorities({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageChannelPrioritiesProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const primaryRef = useRef<HTMLDivElement>(null);
  const items = value ? value.split(",").map(s => s.trim()).filter(Boolean) : [];

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".channel-card",
        { opacity: 0, y: 25, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.05, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  // Primary badge animation
  useEffect(() => {
    if (primaryRef.current && items.length > 0) {
      gsap.fromTo(primaryRef.current,
        { opacity: 0, y: -15, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.5)" }
      );
    }
  }, [items.length]);

  const toggleChannel = useCallback((label: string) => {
    let newItems;
    if (items.includes(label)) {
      newItems = items.filter(c => c !== label);
    } else {
      newItems = [...items, label];
    }
    onChange(newItems.join(", "));
  }, [items, onChange]);

  const primaryChannel = items[0];

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="Which channels matter most?"
      stepDescription="Select all that apply. First selected = primary. We generate content for all of them."
      onBack={onBack}
      onNext={onNext}
      canGoNext={items.length >= 1}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in">
        {/* Primary badge */}
        {primaryChannel && (
          <div ref={primaryRef} className="ob-content-item ob-animate-in mb-5 p-4 rounded-[var(--radius-lg)] bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center">
                <ArrowUp size={18} />
              </div>
              <div>
                <p className="text-[11px] font-mono opacity-50">PRIMARY CHANNEL</p>
                <p className="text-[16px] font-semibold">{primaryChannel}</p>
              </div>
            </div>
            <Radio size={20} className="opacity-40" />
          </div>
        )}

        {/* Channel grid */}
        <div className="ob-interactive grid grid-cols-2 gap-3">
          {CHANNELS.map((ch) => {
            const ChIcon = ch.icon;
            const isSelected = items.includes(ch.label);
            const priority = isSelected ? items.indexOf(ch.label) + 1 : null;

            return (
              <button
                key={ch.label}
                onClick={() => toggleChannel(ch.label)}
                className={`channel-card flex items-start gap-3 p-4 rounded-[var(--radius-md)] border transition-all duration-250 text-left ${isSelected
                    ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)] scale-[1.01]"
                    : "bg-[var(--bg-surface)] border-[var(--border-1)] hover:border-[var(--border-2)]"
                  }`}
              >
                <ChIcon size={18} className="mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <span className="text-[13px] font-semibold block">{ch.label}</span>
                  <span className={`text-[10px] leading-snug ${isSelected ? "text-white/50" : "text-[var(--ink-3)]"}`}>
                    {ch.effort}
                  </span>
                </div>
                {priority && (
                  <span className="text-[11px] font-mono opacity-40 flex-shrink-0">
                    #{priority}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <p className="mt-4 text-[11px] font-mono text-[var(--ink-3)]">
          {items.length} channel{items.length !== 1 ? "s" : ""} selected
          {items.length > 0 && <span className="text-[var(--status-success)] ml-2">✓ Click again to deselect</span>}
        </p>
      </div>
    </OnboardingLayout>
  );
}
