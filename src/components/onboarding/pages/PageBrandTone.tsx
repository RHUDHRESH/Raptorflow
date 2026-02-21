"use client";

import { useEffect, useRef, useCallback } from "react";
import { gsap } from "gsap";
import { OnboardingLayout } from "../OnboardingLayout";
import { Volume2, Quote } from "lucide-react";

interface PageBrandToneProps {
  value: string;
  onChange: (val: string) => void;
  currentPage: number;
  totalPages: number;
  onNext: () => void;
  onBack?: () => void;
  onSaveAndExit?: () => void;
}

const TONES = [
  { label: "Professional", description: "Clear, authoritative, trustworthy", sample: "We partner with leading organizations to deliver measurable outcomes." },
  { label: "Conversational", description: "Friendly, approachable, warm", sample: "Hey — we make this stuff easy. No jargon, just results." },
  { label: "Bold", description: "Assertive, direct, confident", sample: "Stop settling. Ship faster. Win more. Here's how." },
  { label: "Witty", description: "Clever, playful, sharp", sample: "Your content strategy shouldn't give you an existential crisis." },
  { label: "Technical", description: "Precise, data-driven, detailed", sample: "Latency under 50ms across 99th percentile workloads." },
  { label: "Inspirational", description: "Visionary, motivating, aspirational", sample: "The future of marketing is here. Are you ready to lead it?" },
  { label: "Minimal", description: "Sparse, elegant, to the point", sample: "Clear thinking. Better results." },
  { label: "Empathetic", description: "Understanding, human, supportive", sample: "We know how hard this is. We built this for you." },
];

export function PageBrandTone({
  value,
  onChange,
  currentPage,
  totalPages,
  onNext,
  onBack,
}: PageBrandToneProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);

  // Entrance animation with stagger
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(".tone-card",
        { opacity: 0, y: 30, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.06, ease: "power2.out" }
      );
    }, wrapperRef);
    return () => ctx.revert();
  }, []);

  // Selection handler
  const handleSelect = useCallback((label: string) => {
    onChange(label);
    
    // Animate selected card
    const card = document.querySelector(`[data-tone="${label}"]`);
    if (card) {
      gsap.fromTo(card,
        { scale: 0.95 },
        { scale: 1.02, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out" }
      );
    }

    // Animate preview
    if (previewRef.current) {
      gsap.fromTo(previewRef.current,
        { opacity: 0, y: 15, height: 0 },
        { opacity: 1, y: 0, height: "auto", duration: 0.35, ease: "power2.out" }
      );
    }

    // Note: User must click Continue or press Enter to advance
  }, [onChange]);

  const selectedTone = TONES.find(t => t.label === value);

  return (
    <OnboardingLayout
      currentStep={currentPage}
      totalSteps={totalPages}
      stepTitle="What's your brand voice?"
      stepDescription="Pick the tone that best matches how you want to sound."
      onBack={onBack}
      onNext={onNext}
      canGoNext={!!value}
      showBack={!!onBack}
    >
      <div ref={wrapperRef} className="ob-animate-in">
        {/* Sample preview */}
        {selectedTone && (
          <div ref={previewRef} className="ob-content-item ob-animate-in mb-5 p-5 rounded-[var(--radius-lg)] bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-white/5 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-3">
                <Quote size={14} className="opacity-40" />
                <p className="text-[11px] font-mono opacity-40 tracking-wider">{selectedTone.label.toUpperCase()}</p>
              </div>
              <p className="text-[16px] italic leading-relaxed">&ldquo;{selectedTone.sample}&rdquo;</p>
            </div>
          </div>
        )}

        {/* Tone grid */}
        <div className="ob-interactive grid grid-cols-2 gap-3">
          {TONES.map((tone) => {
            const isSelected = value === tone.label;
            return (
              <button
                key={tone.label}
                data-tone={tone.label}
                onClick={() => handleSelect(tone.label)}
                className={`tone-card text-left p-4 rounded-[var(--radius-md)] border transition-all duration-250 ${isSelected
                    ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)] scale-[1.02]"
                    : "bg-[var(--bg-surface)] border-[var(--border-1)] hover:border-[var(--border-2)] hover:bg-[var(--bg-raised)]"
                  }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Volume2 size={14} className={isSelected ? "opacity-60" : "text-[var(--ink-3)]"} />
                  <span className={`text-[14px] font-semibold ${isSelected ? "text-[var(--rf-ivory)]" : "text-[var(--ink-1)]"}`}>
                    {tone.label}
                  </span>
                </div>
                <span className={`text-[11px] leading-snug ${isSelected ? "text-white/50" : "text-[var(--ink-3)]"}`}>
                  {tone.description}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </OnboardingLayout>
  );
}
