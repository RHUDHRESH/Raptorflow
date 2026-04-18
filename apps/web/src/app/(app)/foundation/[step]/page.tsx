"use client";

import * as React from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { use, useState, useEffect } from "react";
import { useFoundation, useUpdateFoundationSection } from "@/hooks/use-foundation";
import { FoundationShell } from "@/components/foundation/foundation-shell";

import { FOUNDATION_STEPS as STEPS } from "@/lib/foundation";

function getStep(id: string) {
  return STEPS.find((s) => s.id === id) ?? STEPS[0];
}

function getStepIndex(id: string) {
  return STEPS.findIndex((s) => s.id === id);
}

export default function FoundationStepPage({
  params
}: {
  params: Promise<{ step: string }>;
}): React.ReactElement {
  const router = useRouter();
  const { step } = use(params);
  const currentStep = getStep(step);
  const stepIndex = getStepIndex(step);
  const prevStep = stepIndex > 0 ? STEPS[stepIndex - 1] : null;
  const nextStep = stepIndex < STEPS.length - 1 ? STEPS[stepIndex + 1] : null;

  const { data: foundation, isLoading } = useFoundation();
  const updateSection = useUpdateFoundationSection();

  const [value, setValue] = useState<string>(
    () => (foundation?.sections?.[currentStep.section] as string) ?? ""
  );
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (foundation?.sections?.[currentStep.section] !== undefined) {
      setValue(foundation.sections[currentStep.section] as string);
    }
  }, [foundation, currentStep.section]);

  const isSaving = updateSection.isPending;

  const handleSaveAndContinue = async () => {
    try {
      await updateSection.mutateAsync({ section: currentStep.section, value });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      if (nextStep) {
        router.push(`/foundation/${nextStep.id}`);
      } else {
        router.push("/app");
      }
    } catch (err) {
       console.error("Save failed", err);
    }
  };

  const handleSaveDraft = async () => {
    try {
      await updateSection.mutateAsync({ section: currentStep.section, value });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
       console.error("Save draft failed", err);
    }
  };

  return (
    <FoundationShell
      currentStepIndex={stepIndex}
      totalSteps={STEPS.length}
      stepTitle={currentStep.title}
      stepDescription={currentStep.description}
      isSaving={isLoading || isSaving}
      hasSaved={saved}
      onSaveAndContinue={handleSaveAndContinue}
      onSaveDraft={handleSaveDraft}
      prevHref={prevStep ? `/foundation/${prevStep.id}` as Route : undefined}
      nextHref={nextStep ? `/foundation/${nextStep.id}` as Route : undefined}
    >
      <div className="flex flex-col space-y-4">
        {stepIndex === 0 ? (
          <div>
            <label className="text-xs uppercase tracking-widest font-mono text-[var(--muted-foreground)] mb-3 block">
              Website URL
            </label>
            <input 
              type="url"
              placeholder={"placeholder" in currentStep ? currentStep.placeholder : undefined}
              value={value}
              onChange={(e) => { setValue(e.target.value); setSaved(false); }}
              className="w-full h-16 bg-transparent border border-[var(--border)] px-4 focus:outline-none focus:ring-1 focus:ring-[var(--primary)] font-mono text-lg transition-shadow"
            />
          </div>
        ) : (
          <div>
             <label className="text-xs uppercase tracking-widest font-mono text-[var(--muted-foreground)] mb-3 block">
              Provide Context
            </label>
            <textarea
              className="w-full min-h-[240px] bg-transparent border border-[var(--border)] p-5 focus:outline-none focus:ring-1 focus:ring-[var(--primary)] text-base leading-relaxed resize-y transition-shadow"
              placeholder={`Elaborate on your ${currentStep.title.toLowerCase()}...`}
              value={value}
              onChange={(e) => { setValue(e.target.value); setSaved(false); }}
            />
          </div>
        )}
        
        {/* Minimalist Hint Bar */}
        <div className="border border-[var(--border)] bg-black/5 p-4 flex gap-3 text-sm">
          <span className="font-mono text-[var(--primary)]">✦</span>
          <p className="text-[var(--muted-foreground)]">
            Remember: Be exceptionally clear here. Your strategy outputs are entirely dependent on the quality of these constraints.
          </p>
        </div>
      </div>
    </FoundationShell>
  );
}

