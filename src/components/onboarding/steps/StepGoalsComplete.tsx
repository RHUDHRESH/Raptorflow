"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface StepGoalsCompleteProps {
  data: {
    acquisition_goal: string;
    constraints_and_guardrails: string;
  };
  onChange: (data: Partial<StepGoalsCompleteProps["data"]>) => void;
  onComplete: () => void;
  isSubmitting: boolean;
}

const CONSTRAINT_SUGGESTIONS = [
  "No legal claims without proof",
  "No competitor bashing",
  "Always include specific metrics",
  "Lead with customer pain point",
  "Avoid hyperbole",
  "Keep emails under 150 words",
  "No discounts in messaging",
];

export function StepGoalsComplete({
  data,
  onChange,
  onComplete,
  isSubmitting,
}: StepGoalsCompleteProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [constraintsPreview, setConstraintsPreview] = useState<string[]>([]);
  const [showSummary, setShowSummary] = useState(false);

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

  // Parse constraints
  useEffect(() => {
    const constraints = data.constraints_and_guardrails
      .split(/[\n,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);
    setConstraintsPreview(constraints);
  }, [data.constraints_and_guardrails]);

  const isValid = data.acquisition_goal.trim().length > 0;

  return (
    <div ref={containerRef} className="space-y-8">
      {/* Acquisition Goal */}
      <div className="form-field">
        <label className="rf-label">Primary acquisition goal *</label>
        <input
          type="text"
          value={data.acquisition_goal}
          onChange={(e) => onChange({ acquisition_goal: e.target.value })}
          placeholder="Generate 60 SQLs per month"
          className="rf-input"
        />
        <p className="rf-hint">
          One clear metric the system should optimize toward
        </p>
      </div>

      {/* Constraints */}
      <div className="form-field">
        <label className="rf-label">Constraints & guardrails *</label>
        <textarea
          value={data.constraints_and_guardrails}
          onChange={(e) =>
            onChange({ constraints_and_guardrails: e.target.value })
          }
          placeholder="No legal claims without proof, no competitor bashing, always include specific metrics..."
          className="rf-textarea"
          rows={3}
        />
        <p className="rf-hint">
          Hard rules for messaging and execution
        </p>

        {/* Quick add suggestions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-xs text-[var(--ink-3)] mr-2">Quick add:</span>
          {CONSTRAINT_SUGGESTIONS.map((constraint) => (
            <button
              key={constraint}
              onClick={() => {
                const current = data.constraints_and_guardrails
                  .split(/[\n,;]+/)
                  .map((s) => s.trim())
                  .filter(Boolean);
                if (!current.includes(constraint)) {
                  onChange({
                    constraints_and_guardrails: [...current, constraint].join(", "),
                  });
                }
              }}
              className="text-xs px-2 py-1 rounded bg-[var(--border-1)] text-[var(--ink-2)] hover:bg-[var(--border-2)] transition-colors"
            >
              + {constraint}
            </button>
          ))}
        </div>

        {constraintsPreview.length > 0 && (
          <div className="mt-4 p-4 rounded-[var(--radius-sm)] bg-amber-50 border border-amber-200">
            <span className="text-xs font-semibold uppercase tracking-wide text-amber-800 block mb-2">
              Active Guardrails
            </span>
            <ul className="space-y-1">
              {constraintsPreview.map((constraint, i) => (
                <li key={i} className="text-sm text-amber-900 flex items-start gap-2">
                  <span className="text-amber-600 mt-0.5">⚠</span>
                  {constraint}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Summary Preview */}
      <div className="form-field">
        <button
          onClick={() => setShowSummary(!showSummary)}
          className="flex items-center gap-2 text-sm font-medium text-[var(--ink-2)] hover:text-[var(--ink-1)] transition-colors"
        >
          <svg
            className={`w-4 h-4 transition-transform ${showSummary ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
          Preview what we&apos;re building
        </button>

        {showSummary && (
          <div className="mt-4 p-6 rounded-[var(--radius-md)] bg-[var(--bg-surface)] border border-[var(--border-1)]">
            <div className="flex items-center gap-3 mb-4">
              <CompassLogo size={32} variant="compact" className="text-[var(--rf-charcoal)]" />
              <div>
                <div className="font-semibold text-[var(--ink-1)]">Your Marketing Foundation</div>
                <div className="text-xs text-[var(--ink-3)]">
                  Business Context Manifest (BCM)
                </div>
              </div>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex gap-3">
                <span className="text-[var(--ink-3)] w-24 shrink-0">Goal:</span>
                <span className="text-[var(--ink-1)] font-medium">
                  {data.acquisition_goal || "Not set"}
                </span>
              </div>
              <div className="flex gap-3">
                <span className="text-[var(--ink-3)] w-24 shrink-0">Guardrails:</span>
                <span className="text-[var(--ink-1)]">
                  {constraintsPreview.length > 0
                    ? `${constraintsPreview.length} active constraints`
                    : "None set"}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-[var(--border-1)] text-xs text-[var(--ink-3)]">
              After completion, we&apos;ll generate your Business Context Manifest
              and seed your workspace with AI-powered marketing intelligence.
            </div>
          </div>
        )}
      </div>

      {/* Complete CTA */}
      <div className="form-field pt-6 border-t border-[var(--border-1)]">
        <button
          onClick={onComplete}
          disabled={!isValid || isSubmitting}
          className="w-full rf-btn-primary py-4 text-base flex items-center justify-center gap-3 shadow-lg shadow-[var(--rf-charcoal)]/10 disabled:shadow-none"
        >
          {isSubmitting ? (
            <>
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Generating your marketing foundation...
            </>
          ) : (
            <>
              <CompassLogoStatic size={24} variant="micro" className="text-[var(--rf-ivory)]" />
              Complete Onboarding & Generate BCM
            </>
          )}
        </button>
        
        <div className="mt-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div
              className={`w-2 h-2 rounded-full transition-colors duration-300 ${
                isValid ? "bg-green-600" : "bg-amber-500"
              }`}
            />
            <span className="text-sm text-[var(--ink-3)]">
              {isValid
                ? "Ready to generate your Business Context Manifest"
                : "Set your acquisition goal to continue"}
            </span>
          </div>
          <p className="text-xs text-[var(--ink-3)]">
            You can edit all of this later in your Foundation settings
          </p>
        </div>
      </div>
    </div>
  );
}

// Static compass for the CTA button
function CompassLogoStatic({
  size = 24,
  className = "",
  variant = "micro",
}: {
  size?: number;
  className?: string;
  variant?: "micro" | "default" | "compact";
}) {
  const viewBox = variant === "micro" ? "0 0 32 32" : "0 0 100 100";
  const center = variant === "micro" ? 16 : 50;
  const radius = variant === "micro" ? 14 : 40;
  const strokeWidth = variant === "micro" ? 1.5 : 2;

  return (
    <svg
      width={size}
      height={size}
      viewBox={viewBox}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <circle
        cx={center}
        cy={center}
        r={radius}
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeOpacity={0.9}
        fill="none"
      />
      <g>
        <path
          d={`M${center} ${center - 10} L${center + 3} ${center} L${center} ${center + 8} L${center - 3} ${center} Z`}
          fill="currentColor"
        />
        <circle
          cx={center}
          cy={center}
          r={2}
          fill="var(--bg-canvas, #EFEDE6)"
          stroke="currentColor"
          strokeWidth={strokeWidth}
        />
        <circle cx={center} cy={center} r={1} fill="currentColor" />
      </g>
    </svg>
  );
}
