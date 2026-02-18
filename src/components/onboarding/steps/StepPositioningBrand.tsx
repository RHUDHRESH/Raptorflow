"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";

interface StepPositioningBrandProps {
  data: {
    key_differentiator: string;
    competitors: string;
    brand_tone: string;
    banned_phrases: string;
  };
  onChange: (data: Partial<StepPositioningBrandProps["data"]>) => void;
}

const TONE_OPTIONS = [
  { value: "Direct", label: "Direct", desc: "Straight to the point" },
  { value: "Confident", label: "Confident", desc: "Bold and assured" },
  { value: "Practical", label: "Practical", desc: "Actionable advice" },
  { value: "Technical", label: "Technical", desc: "Precise and detailed" },
  { value: "Friendly", label: "Friendly", desc: "Approachable and warm" },
  { value: "Bold", label: "Bold", desc: "Challenger brand" },
  { value: "Professional", label: "Professional", desc: "Polished and refined" },
  { value: "Casual", label: "Casual", desc: "Conversational" },
];

const BANNED_SUGGESTIONS = [
  "Revolutionary",
  "Game-changing",
  "Synergy",
  "Disruptive",
  "Seamless",
  "Magic",
  "Innovative",
  "World-class",
  "Cutting-edge",
  "Best-in-class",
];

export function StepPositioningBrand({
  data,
  onChange,
}: StepPositioningBrandProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedTones, setSelectedTones] = useState<string[]>([]);
  const [bannedPreview, setBannedPreview] = useState<string[]>([]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".form-field",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, ease: "power2.out" }
      );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  // Parse tones from string
  useEffect(() => {
    const tones = data.brand_tone
      .split(/[,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    setSelectedTones(tones);
  }, [data.brand_tone]);

  // Parse banned phrases
  useEffect(() => {
    const banned = data.banned_phrases
      .split(/[\n,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    setBannedPreview(banned);
  }, [data.banned_phrases]);

  const toggleTone = (tone: string) => {
    const newTones = selectedTones.includes(tone)
      ? selectedTones.filter((t) => t !== tone)
      : [...selectedTones, tone];
    onChange({ brand_tone: newTones.join(", ") });
  };

  const isValid =
    data.key_differentiator.trim().length >= 20 &&
    data.competitors.trim().length > 0 &&
    selectedTones.length > 0;

  return (
    <div ref={containerRef} className="space-y-8">
      {/* Differentiator */}
      <div className="form-field">
        <label className="rf-label">What makes you different? *</label>
        <textarea
          value={data.key_differentiator}
          onChange={(e) => onChange({ key_differentiator: e.target.value })}
          placeholder="Our mechanism that competitors cannot easily replicate. What unique approach, technology, or insight do you bring?"
          className="rf-textarea"
          minLength={20}
        />
        <p className="rf-hint">
          Your unfair advantage — the thing only you can claim
        </p>
      </div>

      {/* Competitors */}
      <div className="form-field">
        <label className="rf-label">Who are your main competitors? *</label>
        <textarea
          value={data.competitors}
          onChange={(e) => onChange({ competitors: e.target.value })}
          placeholder="Tableau, Looker, Google Analytics, Mixpanel..."
          className="rf-textarea"
          rows={2}
        />
        <p className="rf-hint">Separate with commas or new lines</p>
      </div>

      {/* Brand Tone - Visual Selector */}
      <div className="form-field">
        <label className="rf-label">Brand Tone *</label>
        <p className="rf-hint mb-4">Select all that describe how you want to sound</p>
        
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {TONE_OPTIONS.map((tone) => (
            <button
              key={tone.value}
              onClick={() => toggleTone(tone.value)}
              className={`p-4 rounded-[var(--radius-sm)] border text-left transition-all duration-200 ${
                selectedTones.includes(tone.value)
                  ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)]"
                  : "bg-[var(--bg-surface)] border-[var(--border-2)] hover:border-[var(--border-1)]"
              }`}
            >
              <div className="font-semibold text-sm mb-1">{tone.label}</div>
              <div
                className={`text-xs ${
                  selectedTones.includes(tone.value)
                    ? "text-[var(--rf-ivory)]/70"
                    : "text-[var(--ink-3)]"
                }`}
              >
                {tone.desc}
              </div>
            </button>
          ))}
        </div>
        
        {selectedTones.length > 0 && (
          <div className="mt-4 flex items-center gap-2">
            <span className="text-xs text-[var(--ink-3)]">Selected:</span>
            <span className="text-sm font-medium text-[var(--ink-1)]">
              {selectedTones.join(" + ")}
            </span>
          </div>
        )}
      </div>

      {/* Banned Phrases */}
      <div className="form-field">
        <label className="rf-label">Words to never use</label>
        <textarea
          value={data.banned_phrases}
          onChange={(e) => onChange({ banned_phrases: e.target.value })}
          placeholder="Revolutionary, game-changing, synergy, disruptive..."
          className="rf-textarea"
          rows={2}
        />
        <p className="rf-hint">Phrases that don&apos;t fit your brand voice</p>
        
        {/* Quick add suggestions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-xs text-[var(--ink-3)] mr-2">Quick add:</span>
          {BANNED_SUGGESTIONS.map((phrase) => (
            <button
              key={phrase}
              onClick={() => {
                const current = data.banned_phrases
                  .split(/[\n,;]+/)
                  .map((s) => s.trim())
                  .filter(Boolean);
                if (!current.includes(phrase)) {
                  onChange({
                    banned_phrases: [...current, phrase].join(", "),
                  });
                }
              }}
              className="text-xs px-2 py-1 rounded bg-[var(--border-1)] text-[var(--ink-2)] hover:bg-[var(--border-2)] transition-colors"
            >
              + {phrase}
            </button>
          ))}
        </div>

        {bannedPreview.length > 0 && (
          <div className="mt-4 p-4 rounded-[var(--radius-sm)] bg-red-50 border border-red-200">
            <span className="text-xs font-semibold uppercase tracking-wide text-red-700 block mb-2">
              Will be blocked
            </span>
            <div className="flex flex-wrap gap-2">
              {bannedPreview.map((phrase, i) => (
                <span
                  key={i}
                  className="text-xs px-2 py-1 rounded bg-red-100 text-red-700 line-through"
                >
                  {phrase}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Validation */}
      <div className="pt-4 border-t border-[var(--border-1)]">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full transition-colors duration-300 ${
              isValid ? "bg-green-600" : "bg-amber-500"
            }`}
          />
          <span className="text-sm text-[var(--ink-3)]">
            {isValid
              ? "Positioning defined"
              : "Define your positioning and voice"}
          </span>
        </div>
      </div>
    </div>
  );
}
