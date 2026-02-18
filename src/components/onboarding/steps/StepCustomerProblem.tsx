"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";

interface StepCustomerProblemProps {
  data: {
    core_problem: string;
    ideal_customer_title: string;
    ideal_customer_profile: string;
    top_pain_points: string;
    top_goals: string;
  };
  onChange: (data: Partial<StepCustomerProblemProps["data"]>) => void;
}

const ROLE_SUGGESTIONS = [
  "VP Engineering",
  "CTO",
  "Head of Product",
  "VP Marketing",
  "CEO",
  "Founder",
  "Data Engineer",
  "Product Manager",
  "Marketing Director",
  "Sales Director",
];

export function StepCustomerProblem({
  data,
  onChange,
}: StepCustomerProblemProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [painPointsPreview, setPainPointsPreview] = useState<string[]>([]);
  const [goalsPreview, setGoalsPreview] = useState<string[]>([]);

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

  // Parse list fields for preview
  useEffect(() => {
    const parseList = (val: string) =>
      val
        .split(/[\n,;]+/)
        .map((s) => s.trim())
        .filter(Boolean);
    setPainPointsPreview(parseList(data.top_pain_points).slice(0, 5));
    setGoalsPreview(parseList(data.top_goals).slice(0, 5));
  }, [data.top_pain_points, data.top_goals]);

  const isValid =
    data.core_problem.trim().length >= 30 &&
    data.ideal_customer_title.trim().length > 0 &&
    data.ideal_customer_profile.trim().length >= 20 &&
    painPointsPreview.length > 0 &&
    goalsPreview.length > 0;

  return (
    <div ref={containerRef} className="space-y-8">
      {/* Core Problem */}
      <div className="form-field">
        <label className="rf-label">
          What painful problem do you solve? *
        </label>
        <textarea
          value={data.core_problem}
          onChange={(e) => onChange({ core_problem: e.target.value })}
          onFocus={() => setFocusedField("core_problem")}
          onBlur={() => setFocusedField(null)}
          placeholder="What painful outcome is prevented? Be specific about the before/after transformation your customers experience."
          className="rf-textarea"
          minLength={30}
        />
        <p className="rf-hint">
          Describe the specific pain point and what happens if it&apos;s not solved
        </p>
      </div>

      {/* Ideal Customer Title */}
      <div className="form-field">
        <label className="rf-label">Who is your primary buyer? *</label>
        <input
          type="text"
          value={data.ideal_customer_title}
          onChange={(e) => onChange({ ideal_customer_title: e.target.value })}
          onFocus={() => setFocusedField("ideal_customer_title")}
          onBlur={() => setFocusedField(null)}
          placeholder="VP Engineering"
          list="role-suggestions"
          className="rf-input"
        />
        <datalist id="role-suggestions">
          {ROLE_SUGGESTIONS.map((role) => (
            <option key={role} value={role} />
          ))}
        </datalist>
        <p className="rf-hint">Job title of the person who makes the buying decision</p>
      </div>

      {/* Ideal Customer Profile */}
      <div className="form-field">
        <label className="rf-label">Describe your ideal customer *</label>
        <textarea
          value={data.ideal_customer_profile}
          onChange={(e) => onChange({ ideal_customer_profile: e.target.value })}
          onFocus={() => setFocusedField("ideal_customer_profile")}
          onBlur={() => setFocusedField(null)}
          placeholder="B2B SaaS companies, 20-200 employees, remote teams, engineering-heavy organizations..."
          className="rf-textarea"
          minLength={20}
        />
        <p className="rf-hint">
          Company size, industry, tech stack, or any other defining characteristics
        </p>
      </div>

      {/* Pain Points with Preview */}
      <div className="form-field">
        <label className="rf-label">Top customer pain points *</label>
        <textarea
          value={data.top_pain_points}
          onChange={(e) => onChange({ top_pain_points: e.target.value })}
          onFocus={() => setFocusedField("top_pain_points")}
          onBlur={() => setFocusedField(null)}
          placeholder="Low conversion rates, poor retention, unclear attribution, slow reporting..."
          className="rf-textarea"
          rows={3}
        />
        <p className="rf-hint">Separate with commas, semicolons, or new lines</p>
        
        {painPointsPreview.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {painPointsPreview.map((point, i) => (
              <span
                key={i}
                className="rf-pill rf-pill-active text-xs"
              >
                {point}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Goals with Preview */}
      <div className="form-field">
        <label className="rf-label">What do your customers want to achieve? *</label>
        <textarea
          value={data.top_goals}
          onChange={(e) => onChange({ top_goals: e.target.value })}
          onFocus={() => setFocusedField("top_goals")}
          onBlur={() => setFocusedField(null)}
          placeholder="Increase pipeline velocity, reduce churn, faster decision making..."
          className="rf-textarea"
          rows={3}
        />
        <p className="rf-hint">The outcomes they&apos;re hiring your product to deliver</p>
        
        {goalsPreview.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {goalsPreview.map((goal, i) => (
              <span
                key={i}
                className="rf-pill bg-[var(--bg-canvas)] border-[var(--border-1)] text-[var(--ink-2)]"
              >
                {goal}
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
              ? "Customer profile complete"
              : "Tell us more about your customer"}
          </span>
        </div>
      </div>
    </div>
  );
}
