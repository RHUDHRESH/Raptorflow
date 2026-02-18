"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";

interface StepChannelsMarketProps {
  data: {
    channel_priorities: string;
    geographic_focus: string;
    pricing_model: string;
    proof_points: string;
  };
  onChange: (data: Partial<StepChannelsMarketProps["data"]>) => void;
}

const CHANNEL_OPTIONS = [
  { id: "linkedin", label: "LinkedIn", icon: "💼" },
  { id: "email", label: "Email", icon: "📧" },
  { id: "youtube", label: "YouTube", icon: "▶️" },
  { id: "twitter", label: "Twitter/X", icon: "🐦" },
  { id: "content", label: "Content/SEO", icon: "📝" },
  { id: "podcast", label: "Podcast", icon: "🎙️" },
  { id: "events", label: "Events", icon: "🎪" },
  { id: "partnerships", label: "Partnerships", icon: "🤝" },
  { id: "ads", label: "Paid Ads", icon: "📢" },
  { id: "community", label: "Community", icon: "👥" },
];

const GEO_SUGGESTIONS = [
  "United States",
  "North America",
  "Europe",
  "United States and EU",
  "Global",
  "APAC",
  "LATAM",
];

const PRICING_OPTIONS = [
  "Per-seat monthly SaaS",
  "Usage-based",
  "Tiered plans",
  "Enterprise only",
  "Freemium",
  "One-time purchase",
  "Hybrid",
];

export function StepChannelsMarket({
  data,
  onChange,
}: StepChannelsMarketProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [channels, setChannels] = useState<string[]>([]);
  const [proofPreview, setProofPreview] = useState<string[]>([]);

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

  // Parse channels
  useEffect(() => {
    const chs = data.channel_priorities
      .split(/[,;\n]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    setChannels(chs);
  }, [data.channel_priorities]);

  // Parse proof points
  useEffect(() => {
    const proofs = data.proof_points
      .split(/[,;\n]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    setProofPreview(proofs);
  }, [data.proof_points]);

  const toggleChannel = (channelLabel: string) => {
    const newChannels = channels.includes(channelLabel)
      ? channels.filter((c) => c !== channelLabel)
      : [...channels, channelLabel];
    onChange({ channel_priorities: newChannels.join(", ") });
  };

  const reorderChannel = (index: number, direction: "up" | "down") => {
    if (direction === "up" && index > 0) {
      const newChannels = [...channels];
      [newChannels[index - 1], newChannels[index]] = [
        newChannels[index],
        newChannels[index - 1],
      ];
      onChange({ channel_priorities: newChannels.join(", ") });
    } else if (direction === "down" && index < channels.length - 1) {
      const newChannels = [...channels];
      [newChannels[index], newChannels[index + 1]] = [
        newChannels[index + 1],
        newChannels[index],
      ];
      onChange({ channel_priorities: newChannels.join(", ") });
    }
  };

  const getPriorityLabel = (index: number) => {
    if (index === 0) return { text: "Primary", class: "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)]" };
    if (index <= 2) return { text: "Secondary", class: "bg-[var(--ink-2)] text-white" };
    return { text: "Experimental", class: "bg-[var(--border-2)] text-[var(--ink-2)]" };
  };

  const isValid = channels.length > 0;

  return (
    <div ref={containerRef} className="space-y-8">
      {/* Channel Selection */}
      <div className="form-field">
        <label className="rf-label">Priority channels *</label>
        <p className="rf-hint mb-4">Select channels, then reorder by priority</p>
        
        {/* Channel Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-6">
          {CHANNEL_OPTIONS.map((channel) => (
            <button
              key={channel.id}
              onClick={() => toggleChannel(channel.label)}
              className={`p-3 rounded-[var(--radius-sm)] border text-center transition-all duration-200 ${
                channels.includes(channel.label)
                  ? "bg-[var(--rf-charcoal)] text-[var(--rf-ivory)] border-[var(--rf-charcoal)]"
                  : "bg-[var(--bg-surface)] border-[var(--border-2)] hover:border-[var(--border-1)]"
              }`}
            >
              <div className="text-xl mb-1">{channel.icon}</div>
              <div className="text-xs font-medium">{channel.label}</div>
            </button>
          ))}
        </div>

        {/* Priority Order */}
        {channels.length > 0 && (
          <div className="rf-surface p-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-[var(--ink-3)] mb-3">
              Priority Order
            </div>
            <div className="space-y-2">
              {channels.map((channel, index) => {
                const priority = getPriorityLabel(index);
                return (
                  <div
                    key={channel}
                    className="flex items-center gap-3 p-3 bg-[var(--bg-canvas)] rounded-[var(--radius-sm)]"
                  >
                    <span className="rf-mono text-sm text-[var(--ink-3)] w-6">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <span className="flex-1 font-medium text-sm">{channel}</span>
                    <span className={`text-[10px] px-2 py-1 rounded-full font-semibold ${priority.class}`}>
                      {priority.text}
                    </span>
                    <div className="flex gap-1">
                      <button
                        onClick={() => reorderChannel(index, "up")}
                        disabled={index === 0}
                        className="p-1 rounded hover:bg-[var(--border-1)] disabled:opacity-30 transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                        </svg>
                      </button>
                      <button
                        onClick={() => reorderChannel(index, "down")}
                        disabled={index === channels.length - 1}
                        className="p-1 rounded hover:bg-[var(--border-1)] disabled:opacity-30 transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Geographic Focus */}
      <div className="form-field">
        <label className="rf-label">Geographic focus</label>
        <input
          type="text"
          value={data.geographic_focus}
          onChange={(e) => onChange({ geographic_focus: e.target.value })}
          placeholder="United States and EU"
          list="geo-suggestions"
          className="rf-input"
        />
        <datalist id="geo-suggestions">
          {GEO_SUGGESTIONS.map((geo) => (
            <option key={geo} value={geo} />
          ))}
        </datalist>
        <p className="rf-hint">Primary markets you serve</p>
      </div>

      {/* Pricing Model */}
      <div className="form-field">
        <label className="rf-label">Pricing model</label>
        <select
          value={data.pricing_model}
          onChange={(e) => onChange({ pricing_model: e.target.value })}
          className="rf-input cursor-pointer appearance-none bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%235C565B%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-[right_12px_center] bg-no-repeat pr-10"
        >
          <option value="">Select pricing model...</option>
          {PRICING_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>

      {/* Proof Points */}
      <div className="form-field">
        <label className="rf-label">Proof points</label>
        <textarea
          value={data.proof_points}
          onChange={(e) => onChange({ proof_points: e.target.value })}
          placeholder="2.1M ARR, 40% MoM growth, NPS 62, 500+ customers..."
          className="rf-textarea"
          rows={2}
        />
        <p className="rf-hint">Metrics, traction, testimonials, or awards</p>
        
        {proofPreview.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {proofPreview.map((proof, i) => (
              <span
                key={i}
                className="rf-pill bg-green-50 border-green-200 text-green-700"
              >
                <svg className="w-3 h-3 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                {proof}
              </span>
            ))}
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
              ? "Go-to-market defined"
              : "Select at least one channel"}
          </span>
        </div>
      </div>
    </div>
  );
}
