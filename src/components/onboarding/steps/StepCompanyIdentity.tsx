"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";

interface StepCompanyIdentityProps {
  data: {
    company_name: string;
    company_website: string;
    industry: string;
    business_stage: string;
    company_description: string;
    primary_offer: string;
  };
  onChange: (data: Partial<StepCompanyIdentityProps["data"]>) => void;
}

const BUSINESS_STAGES = [
  { value: "", label: "Select your stage" },
  { value: "Pre-seed", label: "Pre-seed" },
  { value: "Seed", label: "Seed" },
  { value: "Series A", label: "Series A" },
  { value: "Series B", label: "Series B" },
  { value: "Series C+", label: "Series C+" },
  { value: "Growth", label: "Growth" },
  { value: "Enterprise", label: "Enterprise" },
];

const INDUSTRY_SUGGESTIONS = [
  "SaaS",
  "FinTech",
  "E-commerce",
  "Healthcare",
  "AI/ML",
  "DevTools",
  "Cybersecurity",
  "EdTech",
  "Marketplace",
  "Consumer Apps",
];

export function StepCompanyIdentity({
  data,
  onChange,
}: StepCompanyIdentityProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [focusedField, setFocusedField] = useState<string | null>(null);

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

  // Animate field focus
  useEffect(() => {
    if (focusedField) {
      gsap.to(`.field-${focusedField}`, {
        scale: 1.01,
        duration: 0.2,
        ease: "power2.out",
      });
    }
  }, [focusedField]);

  const isValid =
    data.company_name.trim().length >= 2 &&
    data.industry.trim().length > 0 &&
    data.business_stage.trim().length > 0 &&
    data.company_description.trim().length >= 50 &&
    data.primary_offer.trim().length > 0;

  return (
    <div ref={containerRef} className="space-y-8">
      {/* Company Name */}
      <div className={`form-field field-company_name`}>
        <label className="rf-label">Company Name *</label>
        <input
          type="text"
          value={data.company_name}
          onChange={(e) => onChange({ company_name: e.target.value })}
          onFocus={() => setFocusedField("company_name")}
          onBlur={() => setFocusedField(null)}
          placeholder="Acme Labs"
          className="rf-input"
        />
        <p className="rf-hint">Legal or public-facing name of your business</p>
      </div>

      {/* Website (optional) */}
      <div className="form-field field-company_website">
        <label className="rf-label">Company Website</label>
        <input
          type="url"
          value={data.company_website}
          onChange={(e) => onChange({ company_website: e.target.value })}
          onFocus={() => setFocusedField("company_website")}
          onBlur={() => setFocusedField(null)}
          placeholder="https://acme.com"
          className="rf-input"
        />
        <p className="rf-hint">Optional — helps us understand your brand</p>
      </div>

      {/* Industry & Stage Grid */}
      <div className="form-field grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="field-industry">
          <label className="rf-label">Industry *</label>
          <input
            type="text"
            value={data.industry}
            onChange={(e) => onChange({ industry: e.target.value })}
            onFocus={() => setFocusedField("industry")}
            onBlur={() => setFocusedField(null)}
            placeholder="SaaS / FinTech / E-commerce"
            list="industry-suggestions"
            className="rf-input"
          />
          <datalist id="industry-suggestions">
            {INDUSTRY_SUGGESTIONS.map((ind) => (
              <option key={ind} value={ind} />
            ))}
          </datalist>
          <p className="rf-hint">Your primary market category</p>
        </div>

        <div className="field-business_stage">
          <label className="rf-label">Business Stage *</label>
          <select
            value={data.business_stage}
            onChange={(e) => onChange({ business_stage: e.target.value })}
            onFocus={() => setFocusedField("business_stage")}
            onBlur={() => setFocusedField(null)}
            className="rf-input cursor-pointer appearance-none bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%235C565B%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-[right_12px_center] bg-no-repeat pr-10"
          >
            {BUSINESS_STAGES.map((stage) => (
              <option key={stage.value} value={stage.value}>
                {stage.label}
              </option>
            ))}
          </select>
          <p className="rf-hint">Current maturity stage</p>
        </div>
      </div>

      {/* Company Description */}
      <div className="form-field field-company_description">
        <label className="rf-label">What does your company do? *</label>
        <textarea
          value={data.company_description}
          onChange={(e) => onChange({ company_description: e.target.value })}
          onFocus={() => setFocusedField("company_description")}
          onBlur={() => setFocusedField(null)}
          placeholder="Describe what your company does and why it exists. What problem are you solving?"
          className="rf-textarea"
          minLength={50}
          maxLength={500}
        />
        <div className="flex justify-between items-center mt-2">
          <p className="rf-hint">Minimum 50 characters for best results</p>
          <span
            className={`rf-mono text-xs ${
              data.company_description.length >= 50
                ? "text-[var(--ink-3)]"
                : "text-amber-600"
            }`}
          >
            {data.company_description.length}/500
          </span>
        </div>
      </div>

      {/* Primary Offer */}
      <div className="form-field field-primary_offer">
        <label className="rf-label">Primary Offer *</label>
        <input
          type="text"
          value={data.primary_offer}
          onChange={(e) => onChange({ primary_offer: e.target.value })}
          onFocus={() => setFocusedField("primary_offer")}
          onBlur={() => setFocusedField(null)}
          placeholder="AI-powered project management platform"
          className="rf-input"
        />
        <p className="rf-hint">
          Main product or service you sell to customers
        </p>
      </div>

      {/* Validation indicator */}
      <div className="pt-4 border-t border-[var(--border-1)]">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full transition-colors duration-300 ${
              isValid ? "bg-green-600" : "bg-amber-500"
            }`}
          />
          <span className="text-sm text-[var(--ink-3)]">
            {isValid
              ? "All required fields complete"
              : "Complete all required fields to continue"}
          </span>
        </div>
      </div>
    </div>
  );
}
