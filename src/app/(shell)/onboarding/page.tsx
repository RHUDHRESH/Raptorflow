"use client";

import { useEffect, useState, useCallback } from "react";
import { gsap } from "gsap";
import { useRouter } from "next/navigation";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { workspacesService } from "@/services/workspaces.service";
import { notify } from "@/lib/notifications";
import { PageCompanyName } from "@/components/onboarding/pages/PageCompanyName";
import { PageCompanyWebsite } from "@/components/onboarding/pages/PageCompanyWebsite";
import { PageIndustry } from "@/components/onboarding/pages/PageIndustry";
import { PageBusinessStage } from "@/components/onboarding/pages/PageBusinessStage";
import { PageCompanyDescription } from "@/components/onboarding/pages/PageCompanyDescription";
import { PagePrimaryOffer } from "@/components/onboarding/pages/PagePrimaryOffer";
import { PageCoreProblem } from "@/components/onboarding/pages/PageCoreProblem";
import { PageIdealCustomerTitle } from "@/components/onboarding/pages/PageIdealCustomerTitle";
import { PageIdealCustomerProfile } from "@/components/onboarding/pages/PageIdealCustomerProfile";
import { PageTopPainPoints } from "@/components/onboarding/pages/PageTopPainPoints";
import { PageTopGoals } from "@/components/onboarding/pages/PageTopGoals";
import { PageKeyDifferentiator } from "@/components/onboarding/pages/PageKeyDifferentiator";
import { PageCompetitors } from "@/components/onboarding/pages/PageCompetitors";
import { PageBrandTone } from "@/components/onboarding/pages/PageBrandTone";
import { PageBannedPhrases } from "@/components/onboarding/pages/PageBannedPhrases";
import { PageChannelPriorities } from "@/components/onboarding/pages/PageChannelPriorities";
import { PageGeographicFocus } from "@/components/onboarding/pages/PageGeographicFocus";
import { PagePricingModel } from "@/components/onboarding/pages/PagePricingModel";
import { PageProofPoints } from "@/components/onboarding/pages/PageProofPoints";
import { PageAcquisitionGoal } from "@/components/onboarding/pages/PageAcquisitionGoal";
import { PageConstraintsAndGuardrails } from "@/components/onboarding/pages/PageConstraintsAndGuardrails";

// All 21 onboarding fields
const ONBOARDING_FIELDS = [
  { id: "company_name", required: true },
  { id: "company_website", required: false },
  { id: "industry", required: true },
  { id: "business_stage", required: true },
  { id: "company_description", required: true },
  { id: "primary_offer", required: true },
  { id: "core_problem", required: true },
  { id: "ideal_customer_title", required: true },
  { id: "ideal_customer_profile", required: true },
  { id: "top_pain_points", required: true },
  { id: "top_goals", required: true },
  { id: "key_differentiator", required: true },
  { id: "competitors", required: true },
  { id: "brand_tone", required: true },
  { id: "banned_phrases", required: false },
  { id: "channel_priorities", required: true },
  { id: "geographic_focus", required: false },
  { id: "pricing_model", required: false },
  { id: "proof_points", required: false },
  { id: "acquisition_goal", required: true },
  { id: "constraints_and_guardrails", required: true },
];

// Initial form state
const INITIAL_DATA: Record<string, string> = {
  company_name: "",
  company_website: "",
  industry: "",
  business_stage: "",
  company_description: "",
  primary_offer: "",
  core_problem: "",
  ideal_customer_title: "",
  ideal_customer_profile: "",
  top_pain_points: "",
  top_goals: "",
  key_differentiator: "",
  competitors: "",
  brand_tone: "",
  banned_phrases: "",
  channel_priorities: "",
  geographic_focus: "",
  pricing_model: "",
  proof_points: "",
  acquisition_goal: "",
  constraints_and_guardrails: "",
};

export default function OnboardingPage() {
  const router = useRouter();
  const { workspaceId, refreshOnboarding } = useWorkspace();
  const [currentPage, setCurrentPage] = useState(0);
  const [formData, setFormData] = useState(INITIAL_DATA);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const totalPages = ONBOARDING_FIELDS.length;
  const currentField = ONBOARDING_FIELDS[currentPage];

  // Check if onboarding is already complete
  useEffect(() => {
    const checkStatus = async () => {
      if (!workspaceId) {
        setIsLoading(false);
        return;
      }

      try {
        const status = await workspacesService.getOnboardingStatus(workspaceId);
        if (status.completed) {
          router.push("/");
          return;
        }

        // Pre-fill any existing answers
        if (status.answers && Object.keys(status.answers).length > 0) {
          const prefilled: Record<string, string> = {};
          Object.entries(status.answers).forEach(([key, val]) => {
            if (Array.isArray(val)) {
              prefilled[key] = val.join(", ");
            } else if (typeof val === "string") {
              prefilled[key] = val;
            }
          });
          setFormData((prev) => ({ ...prev, ...prefilled }));

          // Jump to first empty required field
          const firstEmptyIndex = ONBOARDING_FIELDS.findIndex(
            (f) => f.required && !prefilled[f.id]
          );
          if (firstEmptyIndex > 0) {
            setCurrentPage(firstEmptyIndex);
          }
        }
      } catch (error) {
        console.error("Failed to check onboarding status:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkStatus();
  }, [workspaceId, router]);

  // Handle field changes
  const updateField = useCallback((fieldId: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [fieldId]: value,
    }));
  }, []);

  // Navigation handlers with animations
  const goToNext = useCallback(() => {
    if (currentPage < totalPages - 1) {
      setCurrentPage((prev) => prev + 1);
    } else {
      // Complete onboarding
      handleComplete();
    }
  }, [currentPage, totalPages]);

  const goToPrev = useCallback(() => {
    if (currentPage > 0) {
      setCurrentPage((prev) => prev - 1);
    }
  }, [currentPage]);

  // Submit onboarding
  const handleComplete = useCallback(async () => {
    if (!workspaceId) {
      notify.error("No workspace selected");
      return;
    }

    setIsSubmitting(true);

    try {
      // Convert form data to proper format
      const payloadAnswers: Record<string, string | string[]> = {};

      Object.entries(formData).forEach(([key, value]) => {
        const listFields = [
          "top_pain_points",
          "top_goals",
          "competitors",
          "brand_tone",
          "banned_phrases",
          "channel_priorities",
          "proof_points",
          "constraints_and_guardrails",
        ];

        if (listFields.includes(key)) {
          payloadAnswers[key] = value
            .split(/[\n,;]+/)
            .map((s) => s.trim())
            .filter(Boolean);
        } else {
          payloadAnswers[key] = value;
        }
      });

      await workspacesService.completeOnboarding(workspaceId, {
        answers: payloadAnswers,
      });

      await refreshOnboarding();

      notify.success("Welcome to RaptorFlow! Your marketing foundation is ready.");

      // Redirect to success page
      router.push("/onboarding/success");
    } catch (error: any) {
      notify.error(error?.message || "Failed to complete onboarding");
      setIsSubmitting(false);
    }
  }, [workspaceId, formData, refreshOnboarding, router]);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--bg-canvas)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-[var(--border-2)] border-t-[var(--rf-charcoal)] rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-[var(--ink-3)]">Loading...</p>
        </div>
      </div>
    );
  }

  // Render appropriate page based on current field
  const renderPage = () => {
    const commonProps = {
      totalPages,
      currentPage: currentPage + 1,
      onNext: goToNext,
      onBack: currentPage > 0 ? goToPrev : undefined,
    };

    switch (currentField.id) {
      case "company_name":
        return (
          <PageCompanyName
            value={formData.company_name}
            onChange={(val) => updateField("company_name", val)}
            {...commonProps}
          />
        );
      case "company_website":
        return (
          <PageCompanyWebsite
            value={formData.company_website}
            onChange={(val) => updateField("company_website", val)}
            {...commonProps}
          />
        );
      case "industry":
        return (
          <PageIndustry
            value={formData.industry}
            onChange={(val) => updateField("industry", val)}
            {...commonProps}
          />
        );
      case "business_stage":
        return (
          <PageBusinessStage
            value={formData.business_stage}
            onChange={(val) => updateField("business_stage", val)}
            {...commonProps}
          />
        );
      case "company_description":
        return (
          <PageCompanyDescription
            value={formData.company_description}
            onChange={(val) => updateField("company_description", val)}
            {...commonProps}
          />
        );
      case "primary_offer":
        return (
          <PagePrimaryOffer
            value={formData.primary_offer}
            onChange={(val) => updateField("primary_offer", val)}
            {...commonProps}
          />
        );
      case "core_problem":
        return (
          <PageCoreProblem
            value={formData.core_problem}
            onChange={(val) => updateField("core_problem", val)}
            {...commonProps}
          />
        );
      case "ideal_customer_title":
        return (
          <PageIdealCustomerTitle
            value={formData.ideal_customer_title}
            onChange={(val) => updateField("ideal_customer_title", val)}
            {...commonProps}
          />
        );
      case "ideal_customer_profile":
        return (
          <PageIdealCustomerProfile
            value={formData.ideal_customer_profile}
            onChange={(val) => updateField("ideal_customer_profile", val)}
            {...commonProps}
          />
        );
      case "top_pain_points":
        return (
          <PageTopPainPoints
            value={formData.top_pain_points}
            onChange={(val) => updateField("top_pain_points", val)}
            {...commonProps}
          />
        );
      case "top_goals":
        return (
          <PageTopGoals
            value={formData.top_goals}
            onChange={(val) => updateField("top_goals", val)}
            {...commonProps}
          />
        );
      case "key_differentiator":
        return (
          <PageKeyDifferentiator
            value={formData.key_differentiator}
            onChange={(val) => updateField("key_differentiator", val)}
            {...commonProps}
          />
        );
      case "competitors":
        return (
          <PageCompetitors
            value={formData.competitors}
            onChange={(val) => updateField("competitors", val)}
            {...commonProps}
          />
        );
      case "brand_tone":
        return (
          <PageBrandTone
            value={formData.brand_tone}
            onChange={(val) => updateField("brand_tone", val)}
            {...commonProps}
          />
        );
      case "banned_phrases":
        return (
          <PageBannedPhrases
            value={formData.banned_phrases}
            onChange={(val) => updateField("banned_phrases", val)}
            {...commonProps}
          />
        );
      case "channel_priorities":
        return (
          <PageChannelPriorities
            value={formData.channel_priorities}
            onChange={(val) => updateField("channel_priorities", val)}
            {...commonProps}
          />
        );
      case "geographic_focus":
        return (
          <PageGeographicFocus
            value={formData.geographic_focus}
            onChange={(val) => updateField("geographic_focus", val)}
            {...commonProps}
          />
        );
      case "pricing_model":
        return (
          <PagePricingModel
            value={formData.pricing_model}
            onChange={(val) => updateField("pricing_model", val)}
            {...commonProps}
          />
        );
      case "proof_points":
        return (
          <PageProofPoints
            value={formData.proof_points}
            onChange={(val) => updateField("proof_points", val)}
            {...commonProps}
          />
        );
      case "acquisition_goal":
        return (
          <PageAcquisitionGoal
            value={formData.acquisition_goal}
            onChange={(val) => updateField("acquisition_goal", val)}
            {...commonProps}
          />
        );
      case "constraints_and_guardrails":
        return (
          <PageConstraintsAndGuardrails
            value={formData.constraints_and_guardrails}
            onChange={(val) => updateField("constraints_and_guardrails", val)}
            {...commonProps}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="relative">
      {renderPage()}
    </div>
  );
}
