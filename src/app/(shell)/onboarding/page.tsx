"use client";

import { useEffect, useMemo, useState } from "react";
import { notify } from "@/lib/notifications";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import {
  workspacesService,
  type OnboardingStep,
} from "@/services/workspaces.service";

const SPLIT_RE = /[\n,;]+/g;

function toTextValue(value: unknown, kind: OnboardingStep["kind"]): string {
  if (kind === "list") {
    if (Array.isArray(value)) {
      return value.map((item) => String(item).trim()).filter(Boolean).join("\n");
    }
    return typeof value === "string" ? value : "";
  }
  return value == null ? "" : String(value);
}

function toPayloadValue(rawValue: string, kind: OnboardingStep["kind"]): string | string[] {
  if (kind !== "list") {
    return rawValue.trim();
  }
  return rawValue
    .split(SPLIT_RE)
    .map((item) => item.trim())
    .filter(Boolean);
}

function hasAnswer(rawValue: string, kind: OnboardingStep["kind"]): boolean {
  if (kind !== "list") {
    return rawValue.trim().length > 0;
  }
  return rawValue
    .split(SPLIT_RE)
    .map((item) => item.trim())
    .filter(Boolean).length > 0;
}

export default function OnboardingPage() {
  const { workspaceId, workspace, onboardingStatus, refreshOnboarding } = useWorkspace();
  const [steps, setSteps] = useState<OnboardingStep[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isLoadingSteps, setIsLoadingSteps] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHydratedFromStatus, setIsHydratedFromStatus] = useState(false);

  useEffect(() => {
    let mounted = true;
    async function loadSteps() {
      setIsLoadingSteps(true);
      setError(null);
      try {
        const response = await workspacesService.getOnboardingSteps();
        if (!mounted) return;
        setSteps(response.steps || []);
      } catch (e: any) {
        if (!mounted) return;
        setError(e?.message || "Failed to load onboarding schema");
      } finally {
        if (mounted) setIsLoadingSteps(false);
      }
    }
    void loadSteps();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (isHydratedFromStatus) return;
    if (!steps.length) return;

    const statusAnswers = onboardingStatus?.answers || {};
    const seeded: Record<string, string> = {};
    for (const step of steps) {
      seeded[step.id] = toTextValue(statusAnswers[step.id], step.kind);
    }
    setAnswers(seeded);
    setIsHydratedFromStatus(true);
  }, [onboardingStatus?.answers, steps, isHydratedFromStatus]);

  const missingRequired = useMemo(() => {
    const missing: string[] = [];
    for (const step of steps) {
      if (!step.required) continue;
      if (!hasAnswer(answers[step.id] || "", step.kind)) {
        missing.push(step.id);
      }
    }
    return missing;
  }, [answers, steps]);

  const completionPct = onboardingStatus?.completion_pct ?? 0;

  async function submitOnboarding() {
    if (!workspaceId) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const payloadAnswers: Record<string, unknown> = {};
      for (const step of steps) {
        const rawValue = answers[step.id] || "";
        payloadAnswers[step.id] = toPayloadValue(rawValue, step.kind);
      }

      await workspacesService.completeOnboarding(workspaceId, {
        answers: payloadAnswers,
      });
      await refreshOnboarding();
      notify.success("Onboarding completed. BCM generated and activated.");
    } catch (e: any) {
      const message = e?.message || "Failed to complete onboarding";
      setError(message);
      notify.error(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoadingSteps) {
    return (
      <div className="max-w-4xl mx-auto px-8 py-10">
        <p className="text-sm text-[var(--ink-muted)]">Loading onboarding workflow...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-8 py-10 space-y-8">
      <header className="space-y-2">
        <h1 className="font-serif text-3xl text-[var(--ink)]">BCM Onboarding</h1>
        <p className="text-sm text-[var(--ink-muted)]">
          Complete this once to generate canonical <span className="font-mono">business_context.json</span>
          {" "}and seed the workspace BCM through LangGraph.
        </p>
        <div className="text-xs text-[var(--ink-muted)]">
          Workspace: <span className="font-mono text-[var(--ink)]">{workspace?.name || workspaceId || "unknown"}</span>
        </div>
      </header>

      <section className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--paper)] p-5 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-[var(--ink)]">Completion</span>
          <span className="text-xs text-[var(--ink-muted)]">{completionPct}%</span>
        </div>
        <div className="h-2 rounded-full bg-[var(--surface)] overflow-hidden">
          <div
            className="h-full bg-[var(--ink)] transition-all"
            style={{ width: `${Math.max(0, Math.min(100, completionPct))}%` }}
          />
        </div>
        <p className="text-xs text-[var(--ink-muted)]">
          Required missing: {missingRequired.length}
        </p>
      </section>

      <section className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--paper)] p-5 space-y-6">
        {steps.map((step, index) => (
          <div key={step.id} className="space-y-2">
            <label className="block space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-[var(--ink-muted)]">STEP {String(index + 1).padStart(2, "0")}</span>
                {step.required ? (
                  <span className="text-[10px] px-2 py-0.5 rounded-full border border-[var(--border)] text-[var(--ink-muted)]">
                    REQUIRED
                  </span>
                ) : (
                  <span className="text-[10px] px-2 py-0.5 rounded-full border border-[var(--border)] text-[var(--ink-muted)]">
                    OPTIONAL
                  </span>
                )}
              </div>
              <div className="text-sm font-medium text-[var(--ink)]">{step.label}</div>
              <div className="text-xs text-[var(--ink-muted)]">{step.description}</div>
            </label>

            {step.kind === "long_text" || step.kind === "list" ? (
              <textarea
                rows={step.kind === "list" ? 3 : 5}
                value={answers[step.id] || ""}
                onChange={(event) =>
                  setAnswers((prev) => ({
                    ...prev,
                    [step.id]: event.target.value,
                  }))
                }
                className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] text-[var(--ink)]"
                placeholder={step.placeholder || ""}
              />
            ) : (
              <input
                type={step.kind === "url" ? "url" : "text"}
                value={answers[step.id] || ""}
                onChange={(event) =>
                  setAnswers((prev) => ({
                    ...prev,
                    [step.id]: event.target.value,
                  }))
                }
                className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] text-[var(--ink)]"
                placeholder={step.placeholder || ""}
              />
            )}

            {step.kind === "list" ? (
              <p className="text-[11px] text-[var(--ink-muted)]">
                Use comma, semicolon, or newline-separated values.
              </p>
            ) : null}
          </div>
        ))}
      </section>

      {error ? (
        <section className="rounded-[var(--radius-lg)] border border-red-500/30 bg-red-500/5 p-4 text-sm text-red-700">
          {error}
        </section>
      ) : null}

      <footer className="flex items-center gap-3">
        <button
          onClick={() => void submitOnboarding()}
          disabled={isSubmitting || !workspaceId}
          className="px-5 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium disabled:opacity-50"
        >
          {isSubmitting ? "Generating BCM..." : "Complete Onboarding and Seed BCM"}
        </button>
        <span className="text-xs text-[var(--ink-muted)]">
          This writes onboarding settings, business context, and BCM manifests.
        </span>
      </footer>
    </div>
  );
}
