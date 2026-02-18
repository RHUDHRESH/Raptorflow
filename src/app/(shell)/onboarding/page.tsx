"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { notify } from "@/lib/notifications";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { OnboardingStep, workspacesService } from "@/services/workspaces.service";
import { FieldValue, isRequiredValuePresent, serializeValue } from "./utils";

type OnboardingField = OnboardingStep["fields"][number];

function OnboardingFieldInput({
  field,
  value,
  onChange,
}: {
  field: OnboardingField;
  value: FieldValue;
  onChange: (next: FieldValue) => void;
}) {
  if (field.kind === "long_text") {
    return (
      <textarea
        value={typeof value === "string" ? value : ""}
        onChange={(event) => onChange(event.target.value)}
        placeholder={field.placeholder || ""}
        className="w-full min-h-44 rounded-xl border border-[var(--border-2)] bg-white px-4 py-3"
      />
    );
  }

  if (field.kind === "list") {
    return (
      <textarea
        value={Array.isArray(value) ? value.join("\n") : ""}
        onChange={(event) => onChange(serializeValue("list", event.target.value))}
        placeholder={field.placeholder || "Enter one item per line"}
        className="w-full min-h-44 rounded-xl border border-[var(--border-2)] bg-white px-4 py-3"
      />
    );
  }

  const inputType = field.kind === "url" ? "url" : "text";

  return (
    <input
      type={inputType}
      value={typeof value === "string" ? value : ""}
      onChange={(event) => onChange(event.target.value)}
      placeholder={field.placeholder || ""}
      className="w-full rounded-xl border border-[var(--border-2)] bg-white px-4 py-3"
    />
  );
}

export default function OnboardingPage() {
  const router = useRouter();
  const { workspaceId, refreshOnboarding } = useWorkspace();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [schemaVersion, setSchemaVersion] = useState("");
  const [requiredStepIds, setRequiredStepIds] = useState<string[]>([]);
  const [steps, setSteps] = useState<OnboardingStep[]>([]);
  const [answers, setAnswers] = useState<Record<string, FieldValue>>({});
  const [missingRequiredSteps, setMissingRequiredSteps] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);

  const currentStep = steps[currentStepIndex];
  const isLastStep = currentStepIndex === steps.length - 1;

  const hydrate = useCallback(async () => {
    if (!workspaceId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    try {
      const [schemaResponse, status] = await Promise.all([
        workspacesService.getOnboardingSteps(),
        workspacesService.getOnboardingStatus(workspaceId),
      ]);

      if (status.completed) {
        router.push("/");
        return;
      }

      setSchemaVersion(schemaResponse.schema_version);
      setRequiredStepIds(schemaResponse.required_steps);
      setSteps(schemaResponse.steps);

      const nextAnswers: Record<string, FieldValue> = {};
      schemaResponse.steps.forEach((step) => {
        step.fields.forEach((field) => {
          nextAnswers[field.id] = serializeValue(field.kind, status.answers[field.id]);
        });
      });

      setAnswers(nextAnswers);
      setMissingRequiredSteps(status.missing_required_steps);
      if (status.next_step_id) {
        const idx = schemaResponse.steps.findIndex((step) => step.id === status.next_step_id);
        if (idx >= 0) setCurrentStepIndex(idx);
      }
    } catch (error) {
      console.error(error);
      notify.error("Failed to load onboarding");
    } finally {
      setIsLoading(false);
    }
  }, [workspaceId, router]);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  const currentStepSatisfied = useMemo(() => {
    if (!currentStep) return false;
    return currentStep.fields.every((field) => {
      if (!field.required) return true;
      const value = answers[field.id];
      return isRequiredValuePresent(value ?? (field.kind === "list" ? [] : ""));
    });
  }, [answers, currentStep]);

  const saveAnswers = useCallback(async () => {
    if (!workspaceId || !schemaVersion) return;
    setIsSaving(true);
    try {
      const status = await workspacesService.upsertOnboardingAnswers(workspaceId, {
        schema_version: schemaVersion,
        answers,
      });
      setMissingRequiredSteps(status.missing_required_steps);
    } catch (error: any) {
      notify.error(error?.message || "Failed to save onboarding answers");
      throw error;
    } finally {
      setIsSaving(false);
    }
  }, [workspaceId, schemaVersion, answers]);

  const goNext = useCallback(async () => {
    if (!currentStepSatisfied) {
      notify.error("Please complete required fields for this step.");
      return;
    }

    await saveAnswers();
    if (!isLastStep) {
      setCurrentStepIndex((index) => Math.min(index + 1, steps.length - 1));
    }
  }, [currentStepSatisfied, saveAnswers, isLastStep, steps.length]);

  const complete = useCallback(async () => {
    if (!workspaceId || !schemaVersion) return;
    setIsCompleting(true);
    try {
      const response = await workspacesService.completeOnboarding(workspaceId, {
        schema_version: schemaVersion,
        answers,
      });
      setMissingRequiredSteps(response.onboarding.missing_required_steps);
      await refreshOnboarding();
      if (response.onboarding.missing_required_steps.length > 0) {
        notify.error("Complete all required steps before finishing onboarding.");
        return;
      }
      notify.success("Welcome to RaptorFlow! Your marketing foundation is ready.");
      router.push("/onboarding/success");
    } catch (error: any) {
      notify.error(error?.message || "Failed to complete onboarding");
    } finally {
      setIsCompleting(false);
    }
  }, [workspaceId, schemaVersion, answers, refreshOnboarding, router]);

  if (isLoading) {
    return <div className="p-8">Loading onboarding...</div>;
  }

  if (!currentStep) {
    return <div className="p-8">No onboarding steps available.</div>;
  }

  return (
    <div className="mx-auto max-w-3xl p-8 space-y-6">
      <div>
        <p className="text-sm text-[var(--ink-3)]">
          Step {currentStepIndex + 1} of {steps.length} • Required steps: {requiredStepIds.length}
        </p>
        <h1 className="text-3xl font-semibold text-[var(--rf-charcoal)]">{currentStep.title}</h1>
        {currentStep.description && (
          <p className="text-[var(--ink-3)] mt-1">{currentStep.description}</p>
        )}
      </div>

      {currentStep.fields.map((field) => (
        <div key={field.id} className="space-y-2">
          <label className="text-sm font-medium text-[var(--ink-2)]">
            {field.label} {field.required ? <span className="text-red-600">*</span> : null}
          </label>
          <OnboardingFieldInput
            field={field}
            value={answers[field.id] ?? (field.kind === "list" ? [] : "")}
            onChange={(nextValue) =>
              setAnswers((prev) => ({
                ...prev,
                [field.id]: nextValue,
              }))
            }
          />
          {field.help ? <p className="text-xs text-[var(--ink-3)]">{field.help}</p> : null}
        </div>
      ))}

      {missingRequiredSteps.length > 0 && (
        <p className="text-sm text-red-600">
          Missing required steps: {missingRequiredSteps.join(", ")}
        </p>
      )}

      <div className="flex items-center gap-3">
        <button
          type="button"
          className="rounded-lg border px-4 py-2"
          onClick={() => setCurrentStepIndex((index) => Math.max(0, index - 1))}
          disabled={currentStepIndex === 0 || isSaving || isCompleting}
        >
          Back
        </button>

        {!isLastStep ? (
          <button
            type="button"
            className="rounded-lg bg-[var(--rf-charcoal)] px-4 py-2 text-white"
            onClick={goNext}
            disabled={isSaving || isCompleting}
          >
            {isSaving ? "Saving..." : "Save & Next"}
          </button>
        ) : (
          <button
            type="button"
            className="rounded-lg bg-[var(--rf-charcoal)] px-4 py-2 text-white"
            onClick={complete}
            disabled={isSaving || isCompleting || missingRequiredSteps.length > 0}
          >
            {isCompleting ? "Completing..." : "Complete Onboarding"}
          </button>
        )}
      </div>
    </div>
  );
}
