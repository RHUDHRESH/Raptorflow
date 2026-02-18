"use client";

import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { CompassLogo } from "@/components/compass/CompassLogo";

interface StepReviewConfirmProps {
  data: {
    company_name: string;
    industry: string;
    business_stage: string;
    company_description: string;
    primary_offer: string;
    core_problem: string;
    ideal_customer_title: string;
    ideal_customer_profile: string;
    top_pain_points: string;
    top_goals: string;
    key_differentiator: string;
    competitors: string;
    brand_tone: string;
    banned_phrases: string;
    channel_priorities: string;
    acquisition_goal: string;
    constraints_and_guardrails: string;
  };
  onEdit: (step: number) => void;
  onConfirm: () => void;
  isSubmitting: boolean;
}

interface ReviewSection {
  id: string;
  title: string;
  stepIndex: number;
  items: { label: string; value: string; type?: "text" | "list" | "long" }[];
}

export function StepReviewConfirm({
  data,
  onEdit,
  onConfirm,
  isSubmitting,
}: StepReviewConfirmProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>(["identity"]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".review-section",
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power2.out" }
      );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  const parseList = (val: string) =>
    val
      .split(/[\n,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);

  const sections: ReviewSection[] = [
    {
      id: "identity",
      title: "Company Identity",
      stepIndex: 1,
      items: [
        { label: "Name", value: data.company_name },
        { label: "Industry", value: data.industry },
        { label: "Stage", value: data.business_stage },
        { label: "What you do", value: data.company_description, type: "long" },
        { label: "Primary offer", value: data.primary_offer },
      ],
    },
    {
      id: "customer",
      title: "Customer & Problem",
      stepIndex: 2,
      items: [
        { label: "Problem solved", value: data.core_problem, type: "long" },
        { label: "Primary buyer", value: data.ideal_customer_title },
        { label: "Ideal customer", value: data.ideal_customer_profile, type: "long" },
        { label: "Pain points", value: data.top_pain_points, type: "list" },
        { label: "Customer goals", value: data.top_goals, type: "list" },
      ],
    },
    {
      id: "positioning",
      title: "Positioning & Brand",
      stepIndex: 3,
      items: [
        { label: "Differentiator", value: data.key_differentiator, type: "long" },
        { label: "Competitors", value: data.competitors, type: "list" },
        { label: "Brand tone", value: data.brand_tone, type: "list" },
        { label: "Banned phrases", value: data.banned_phrases || "None specified", type: "list" },
      ],
    },
    {
      id: "channels",
      title: "Channels & Market",
      stepIndex: 4,
      items: [
        { label: "Priority channels", value: data.channel_priorities, type: "list" },
      ],
    },
    {
      id: "goals",
      title: "Goals & Constraints",
      stepIndex: 5,
      items: [
        { label: "Acquisition goal", value: data.acquisition_goal },
        { label: "Guardrails", value: data.constraints_and_guardrails, type: "list" },
      ],
    },
  ];

  const toggleSection = (id: string) => {
    setExpandedSections((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const renderValue = (item: ReviewSection["items"][0]) => {
    if (item.type === "list") {
      const items = parseList(item.value);
      if (items.length === 0) return <span className="text-[var(--ink-3)] italic">Not specified</span>;
      return (
        <div className="flex flex-wrap gap-2">
          {items.map((val, i) => (
            <span key={i} className="rf-pill rf-pill-active text-xs">
              {val}
            </span>
          ))}
        </div>
      );
    }
    if (item.type === "long") {
      return (
        <p className="text-sm text-[var(--ink-1)] leading-relaxed whitespace-pre-wrap">
          {item.value}
        </p>
      );
    }
    return <span className="text-sm text-[var(--ink-1)] font-medium">{item.value}</span>;
  };

  return (
    <div ref={containerRef} className="space-y-6">
      {/* Intro */}
      <div className="review-section mb-8">
        <div className="flex items-start gap-4 p-6 rounded-[var(--radius-md)] bg-[var(--rf-charcoal)] text-[var(--rf-ivory)]">
          <CompassLogo size={48} variant="compact" className="text-[var(--rf-ivory)] shrink-0" />
          <div>
            <h3 className="text-lg font-semibold mb-1">Review your foundation</h3>
            <p className="text-sm text-[var(--rf-ivory)]/70 leading-relaxed">
              Everything looks good? This information becomes your Business Context Manifest 
              (BCM) — the intelligence that powers all your marketing. You can edit anytime 
              in your Foundation settings.
            </p>
          </div>
        </div>
      </div>

      {/* Sections */}
      <div className="space-y-4">
        {sections.map((section) => {
          const isExpanded = expandedSections.includes(section.id);
          return (
            <div
              key={section.id}
              className="review-section rf-surface overflow-hidden transition-all duration-300"
            >
              {/* Section Header */}
              <button
                onClick={() => toggleSection(section.id)}
                className="w-full flex items-center justify-between p-5 hover:bg-[var(--bg-canvas)]/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-[var(--bg-canvas)] flex items-center justify-center">
                    <span className="rf-mono text-xs font-semibold text-[var(--ink-2)]">
                      {section.stepIndex}
                    </span>
                  </div>
                  <span className="font-semibold text-[var(--ink-1)]">{section.title}</span>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit(section.stepIndex);
                    }}
                    className="text-xs font-medium text-[var(--ink-3)] hover:text-[var(--rf-charcoal)] transition-colors"
                  >
                    Edit
                  </button>
                  <svg
                    className={`w-5 h-5 text-[var(--ink-3)] transition-transform duration-300 ${
                      isExpanded ? "rotate-180" : ""
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              </button>

              {/* Section Content */}
              <div
                className={`overflow-hidden transition-all duration-300 ease-out ${
                  isExpanded ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"
                }`}
              >
                <div className="px-5 pb-5 pt-2 border-t border-[var(--border-1)]">
                  <div className="space-y-4">
                    {section.items.map((item, i) => (
                      <div key={i} className="grid grid-cols-1 md:grid-cols-[140px_1fr] gap-2 md:gap-4">
                        <span className="text-xs font-medium uppercase tracking-wide text-[var(--ink-3)]">
                          {item.label}
                        </span>
                        <div>{renderValue(item)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Confirmation */}
      <div className="review-section pt-6 border-t border-[var(--border-1)]">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-sm text-[var(--ink-2)] mb-1">
              Ready to generate your Business Context Manifest?
            </p>
            <p className="text-xs text-[var(--ink-3)]">
              This will seed your workspace with AI-powered marketing intelligence.
            </p>
          </div>
          <button
            onClick={onConfirm}
            disabled={isSubmitting}
            className="rf-btn-primary px-8 py-4 text-base flex items-center gap-3 shadow-lg shadow-[var(--rf-charcoal)]/10"
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
                Generating BCM...
              </>
            ) : (
              <>
                <CompassLogoStatic size={24} variant="micro" className="text-[var(--rf-ivory)]" />
                Confirm & Generate BCM
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

// Static compass for the button
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
        r={variant === "micro" ? 14 : 40}
        stroke="currentColor"
        strokeWidth={variant === "micro" ? 1.5 : 2}
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
          strokeWidth={1.5}
        />
        <circle cx={center} cy={center} r={1} fill="currentColor" />
      </g>
    </svg>
  );
}
