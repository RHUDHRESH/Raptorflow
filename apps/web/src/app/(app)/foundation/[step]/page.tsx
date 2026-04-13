"use client";

import * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { use, useState } from "react";
import { useFoundation, useUpdateFoundationSection } from "@/hooks/use-foundation";
import { RouteShell } from "@/components/layout/route-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const STEPS = [
  { id: "url", title: "URL", description: "Your website URL — used for automated research and foundation scanning.", placeholder: "https://yourcompany.com", section: "url" },
  { id: "identity-confirmation", title: "Identity Confirmation", description: "Confirm your company name, tagline, and brand identity signals.", section: "identity" },
  { id: "business-stage-and-team", title: "Business Stage and Team", description: "Help agents calibrate their advice to your current scale and resources.", section: "business_stage" },
  { id: "what-you-actually-sell", title: "What You Actually Sell", description: "The concrete product or service you deliver — not the marketing version.", section: "what_you_sell" },
  { id: "the-problem-you-solve", title: "The Problem You Solve", description: "The specific pain point your customers hire you to fix.", section: "problem_solved" },
  { id: "primary-icp", title: "Primary ICP", description: "Your primary Ideal Customer Profile — the buyer archetype you target most.", section: "primary_icp" },
  { id: "secondary-icps", title: "Secondary ICPs", description: "Additional buyer personas that are secondary but still valuable.", section: "secondary_icps" },
  { id: "competitive-landscape", title: "Competitive Landscape", description: "Direct and indirect competitors your buyers consider.", section: "competitive_landscape" },
  { id: "competitive-differentiation", title: "Competitive Differentiation", description: "What makes you meaningfully different from alternatives.", section: "differentiation" },
  { id: "positioning-statement", title: "Positioning Statement", description: "How you occupy a distinct place in your market.", section: "positioning" },
  { id: "brand-personality", title: "Brand Personality", description: "The consistent voice, tone, and character of your brand.", section: "brand_personality" },
  { id: "voice-in-practice", title: "Voice in Practice", description: "Concrete examples of your brand voice in real content.", section: "voice_practice" },
  { id: "content-territories", title: "Content Territories", description: "The thematic areas your content explores and owns.", section: "content_territories" },
  { id: "marketing-channels", title: "Marketing Channels", description: "The channels you use to reach and engage your ICP.", section: "channels" },
  { id: "goals-and-kpis", title: "Goals and KPIs", description: "The business outcomes you are optimizing marketing toward.", section: "goals_kpis" },
  { id: "keywords-and-seo", title: "Keywords and SEO", description: "Search terms and organic visibility targets.", section: "keywords_seo" },
  { id: "existing-assets", title: "Existing Assets", description: "Collateral, content, and materials you already have.", section: "existing_assets" },
  { id: "current-frustrations", title: "Current Frustrations", description: "What is broken, slow, or failing in your current marketing.", section: "frustrations" },
  { id: "existing-tools", title: "Existing Tools", description: "Your current marketing stack and how it is used.", section: "tools" },
  { id: "reference-brands", title: "Reference Brands", description: "Brands you admire or aspire to — for tone, style, or strategy.", section: "reference_brands" },
  { id: "campaign-strategist", title: "Campaign Strategist", description: "Your AI campaign architect — configure its briefing style and priorities.", section: "campaign_strategist" },
] as const;

function getStep(id: string) {
  return STEPS.find((s) => s.id === id) ?? STEPS[0];
}

function getStepIndex(id: string) {
  return STEPS.findIndex((s) => s.id === id);
}

type Step = typeof STEPS[number];

export default function FoundationStepPage({
  params
}: {
  params: Promise<{ step: string }>;
}): React.ReactElement {
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
  const [saveError, setSaveError] = useState<string | null>(null);

  React.useEffect(() => {
    if (foundation?.sections?.[currentStep.section] !== undefined) {
      setValue(foundation.sections[currentStep.section] as string);
    }
  }, [foundation, currentStep.section]);

  const sectionValue = foundation?.sections?.[currentStep.section] as string | undefined;
  const isSaving = updateSection.isPending;
  const hasChanges = value !== (sectionValue ?? "");

  const handleSave = async () => {
    setSaveError(null);
    try {
      await updateSection.mutateAsync({ section: currentStep.section, value });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Failed to save");
    }
  };

  return (
    <RouteShell
      eyebrow={`Foundation · Step ${stepIndex + 1} of ${STEPS.length}`}
      title={currentStep.title}
      description={currentStep.description}
      tags={[currentStep.section, "foundation"]}
      backHref={"/foundation" as Route}
      backLabel="Back to Foundation"
    >
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-[var(--muted-foreground)]">
          <span>Step {stepIndex + 1} of {STEPS.length}</span>
          <span>{currentStep.id.replace(/-/g, " ")}</span>
        </div>
        <div className="h-1.5 w-full rounded-full bg-[var(--muted)]">
          <div
            className="h-1.5 rounded-full bg-[var(--accent)] transition-all duration-300"
            style={{ width: `${((stepIndex + 1) / STEPS.length) * 100}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between gap-4">
        {prevStep ? (
          <Button asChild variant="ghost" size="sm">
            <Link href={`/foundation/${prevStep.id}` as Route}>← {prevStep.title}</Link>
          </Button>
        ) : <div />}
        {nextStep && (
          <Button asChild variant="ghost" size="sm">
            <Link href={`/foundation/${nextStep.id}` as Route}>{nextStep.title} →</Link>
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">{currentStep.title}</CardTitle>
            {isLoading && <span className="text-xs text-[var(--muted-foreground)]">Loading...</span>}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            className="w-full rounded-lg border border-[var(--border)] bg-white p-4 text-sm placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
            rows={6}
            placeholder={("placeholder" in currentStep ? (currentStep as { placeholder?: string }).placeholder : undefined) ?? `Enter your ${currentStep.title.toLowerCase()}...`}
            value={value}
            onChange={(e) => { setValue(e.target.value); setSaved(false); }}
          />
          <div className="flex items-center justify-between">
            <p className="text-xs text-[var(--muted-foreground)]">
              {sectionValue
                ? `Saved: "${(sectionValue ?? "").slice(0, 40)}${sectionValue.length > 40 ? "…" : ""}"`
                : "Not yet saved"}
            </p>
            <div className="flex items-center gap-2">
              {saveError && <span className="text-xs text-red-600">{saveError}</span>}
              {saved && <span className="text-xs text-green-600">✓ Saved</span>}
              <Button size="sm" onClick={handleSave} disabled={isSaving || !hasChanges}>
                {isSaving ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-amber-200 bg-amber-50/50">
        <CardHeader>
          <CardTitle className="text-base">📝 What to implement next</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-amber-800">
          <p><strong>Form field:</strong> Use structured inputs per step type — URL needs validated input with reachability check, ICP steps need structured forms (company size, industry, role, budget).</p>
          <p><strong>Autosave:</strong> Debounced save 2s after last keystroke. Show inline "Saving..." → "Saved ✓".</p>
          <p><strong>Validation:</strong> Per-step validation — URL must be reachable, goals must be SMART.</p>
          <p><strong>AI enrichment:</strong> After save, call Muse AI to suggest improvements or probe ambiguities.</p>
          <p><strong>Navigation guard:</strong> Warn on unsaved changes using beforeunload or Next.js router events.</p>
          <p><strong>Diff view:</strong> Show changes vs last snapshot when content has been modified.</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">All Foundation steps</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2">
            {STEPS.map((s, i) => {
              const hasContent = !!foundation?.sections?.[s.section];
              return (
                <Link
                  key={s.id}
                  href={`/foundation/${s.id}` as Route}
                  className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-xs transition-colors ${
                    s.id === step
                      ? "border-[var(--accent)] bg-accent/10 text-[var(--accent)]"
                      : hasContent
                      ? "border-green-200 bg-green-50 text-green-700"
                      : "border-[var(--border)] bg-white text-[var(--muted-foreground)] hover:border-[var(--accent)]"
                  }`}
                >
                  <span className="font-medium">{i + 1}.</span>
                  <span className="truncate">{s.title}</span>
                  {hasContent && <span className="ml-auto">✓</span>}
                </Link>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
