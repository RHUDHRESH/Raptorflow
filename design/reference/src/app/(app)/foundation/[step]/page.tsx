"use client";

import * as React from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { use, useState, useEffect } from "react";
import { useFoundation, useUpdateFoundationSection } from "@/hooks/use-foundation";
import { FoundationShell } from "@/components/foundation/foundation-shell";

const STEPS = [
  { id: "url", title: "Where Does Your Business Live?", description: "Paste your website URL. We'll scan it to pre-fill the rest of this foundation.", placeholder: "https://yourwebsite.com", section: "url" },
  { id: "identity-confirmation", title: "Tell Me About Your Business", description: "Confirm your core identity so our agents understand who they represent.", section: "identity" },
  { id: "business-stage-and-team", title: "Business Stage & Capacity", description: "Our agents calibrate their campaign ambition to your actual bandwidth.", section: "business_stage" },
  { id: "what-you-actually-sell", title: "What Do You Offer?", description: "List your main offerings. Focus on the customer outcome, not just features.", section: "what_you_sell" },
  { id: "the-problem-you-solve", title: "What Problem Do You Solve?", description: "The most important question: what was your customer's situation before they found you?", section: "problem_solved" },
  { id: "primary-icp", title: "Your Primary Ideal Customer Profile", description: "Define the primary target customer in depth.", section: "primary_icp" },
  { id: "secondary-icps", title: "Secondary Customer Profiles (Optional)", description: "Do you serve other distinct customer groups?", section: "secondary_icps" },
  { id: "competitive-landscape", title: "Who Are Your Competitors?", description: "List the competitors your customers choose between when deciding to buy.", section: "competitive_landscape" },
  { id: "competitive-differentiation", title: "Your Clear Differentiation", description: "Why do buyers choose you over the alternatives listed previously?", section: "differentiation" },
  { id: "positioning-statement", title: "Your Strategic Position", description: "How you occupy a distinct place in your market.", section: "positioning" },
  { id: "brand-personality", title: "Brand Voice & Personality", description: "The consistent voice, tone, and character of your brand.", section: "brand_personality" },
  { id: "voice-in-practice", title: "Give Us An Example", description: "Paste concrete examples of your brand voice in real content.", section: "voice_practice" },
  { id: "content-territories", title: "Content Territories", description: "The thematic areas your content explores and owns.", section: "content_territories" },
  { id: "marketing-channels", title: "Proven Channels", description: "The channels that actually work to reach your ICP.", section: "channels" },
  { id: "goals-and-kpis", title: "Hard Goals & KPIs", description: "The business outcomes you are optimizing marketing toward.", section: "goals_kpis" },
  { id: "keywords-and-seo", title: "Discoverability", description: "Search terms and organic visibility targets.", section: "keywords_seo" },
  { id: "existing-assets", title: "Your Core Assets", description: "Collateral, content, and materials you already have.", section: "existing_assets" },
  { id: "current-frustrations", title: "The Handbrake", description: "What is broken, slow, or failing in your current marketing.", section: "frustrations" },
  { id: "existing-tools", title: "The Tech Stack", description: "Your current marketing stack and how it is used.", section: "tools" },
  { id: "reference-brands", title: "Reference Brands", description: "Brands you admire or aspire to — for tone, style, or strategy.", section: "reference_brands" },
  { id: "campaign-strategist", title: "Your Campaign Strategist", description: "Configure your primary AI architect's briefing style and priorities.", section: "campaign_strategist" },
] as const;

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

