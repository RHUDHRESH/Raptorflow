"use client";

import * as React from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { use, useState, useEffect, useCallback } from "react";
import { useFoundation, useSaveFoundation } from "@/features/foundation/hooks/useFoundation";
import { foundationApi } from "@/lib/api";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { CheckCircle2, ArrowLeftIcon } from "lucide-react";
import Link from "next/link";

const SECTION_CONFIG: Record<string, {
  title: string;
  description: string;
  fields: { key: string; label: string; type: "text" | "textarea" | "select" | "slider" }[];
}> = {
  identity: {
    title: "Identity",
    description: "Your company's core identifying information.",
    fields: [
      { key: "companyName", label: "Company Name", type: "text" },
      { key: "legalName", label: "Legal Name", type: "text" },
      { key: "companyUrl", label: "Website URL", type: "text" },
      { key: "yearFounded", label: "Year Founded", type: "text" },
      { key: "companyStage", label: "Business Stage", type: "select" },
    ],
  },
  mission: {
    title: "Mission & Position",
    description: "Your mission, value proposition, and the problem you solve.",
    fields: [
      { key: "missionStatement", label: "Mission Statement", type: "textarea" },
      { key: "valueProposition", label: "Value Proposition", type: "textarea" },
      { key: "problemStatement", label: "Problem Statement", type: "textarea" },
    ],
  },
  "brand-voice": {
    title: "Brand Voice",
    description: "How your brand communicates.",
    fields: [
      { key: "brandVoice", label: "Brand Voice Description", type: "textarea" },
      { key: "brandVoiceSliders", label: "Voice Sliders", type: "textarea" },
      { key: "brandVoiceDescriptors", label: "Voice Descriptors", type: "textarea" },
    ],
  },
  icp: {
    title: "Ideal Customer Profile",
    description: "Your primary target customer.",
    fields: [
      { key: "targetAudience", label: "Target Audience (ICP)", type: "textarea" },
    ],
  },
  competitors: {
    title: "Competitors",
    description: "Your competitive landscape.",
    fields: [
      { key: "competitors", label: "Competitor List", type: "textarea" },
    ],
  },
  positioning: {
    title: "Positioning",
    description: "Your market position and unique value.",
    fields: [
      { key: "positioning", label: "Positioning Statement", type: "textarea" },
    ],
  },
  channels: {
    title: "Channels",
    description: "Your marketing channels.",
    fields: [
      { key: "channelPerformance", label: "Channel Performance", type: "textarea" },
    ],
  },
  products: {
    title: "Products",
    description: "Your product or service catalog.",
    fields: [
      { key: "productCatalog", label: "Product Catalog", type: "textarea" },
    ],
  },
  content: {
    title: "Content",
    description: "Your content territories.",
    fields: [
      { key: "contentTerritories", label: "Content Territories", type: "textarea" },
    ],
  },
  seo: {
    title: "SEO & Keywords",
    description: "Your search and keyword strategy.",
    fields: [
      { key: "seoKeywords", label: "SEO Keywords", type: "textarea" },
    ],
  },
  assets: {
    title: "Assets",
    description: "Your existing brand and marketing assets.",
    fields: [
      { key: "assetInventory", label: "Asset Inventory", type: "textarea" },
    ],
  },
  goals: {
    title: "Goals & KPIs",
    description: "Your business goals and success metrics.",
    fields: [
      { key: "primaryGoal", label: "Primary Goal", type: "textarea" },
      { key: "budget", label: "Budget", type: "textarea" },
      { key: "timeAvailability", label: "Time Availability", type: "text" },
    ],
  },
  "voice-tone": {
    title: "Voice & Tone",
    description: "The voice and tone of your brand.",
    fields: [
      { key: "toneFormal", label: "Formality (1=Casual, 5=Formal)", type: "slider" },
      { key: "toneSerious", label: "Tone (1=Playful, 5=Serious)", type: "slider" },
    ],
  },
  evidence: {
    title: "Evidence & Proof",
    description: "Results, proof points, and writing samples.",
    fields: [
      { key: "evidence", label: "Evidence & Results", type: "textarea" },
      { key: "writingSamples", label: "Writing Samples", type: "textarea" },
    ],
  },
  references: {
    title: "References & Frustrations",
    description: "Reference brands and current frustrations.",
    fields: [
      { key: "referenceBrands", label: "Reference Brands", type: "textarea" },
      { key: "frustrations", label: "Current Frustrations", type: "textarea" },
    ],
  },
  team: {
    title: "Strategist & Team",
    description: "Your AI strategist configuration.",
    fields: [
      { key: "strategistName", label: "Strategist Name", type: "text" },
      { key: "strategistPersonality", label: "Strategist Personality", type: "textarea" },
      { key: "founderName", label: "Founder Name", type: "text" },
    ],
  },
  market: {
    title: "Market",
    description: "Your target market geography and language.",
    fields: [
      { key: "primaryMarket", label: "Primary Market", type: "text" },
      { key: "language", label: "Primary Language", type: "text" },
      { key: "location", label: "Location", type: "text" },
    ],
  },
};

type SectionSlug = keyof typeof SECTION_CONFIG;

function isValidSlug(s: string): s is SectionSlug {
  return s in SECTION_CONFIG;
}

export default function FoundationSectionPage({
  params,
}: {
  params: Promise<{ section: string }>;
}): React.ReactElement {
  const router = useRouter();
  const { section } = use(params);
  const slug = isValidSlug(section) ? section : "identity";

  const { data: foundation, isLoading } = useFoundation();
  const saveMutation = useSaveFoundation();

  const config = SECTION_CONFIG[slug];

  const [values, setValues] = useState<Record<string, string>>({});
  const [hasChanged, setHasChanged] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [saveTimer, setSaveTimer] = useState<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (foundation?.sections) {
      const initial: Record<string, string> = {};
      for (const field of config.fields) {
        const raw = foundation.sections[field.key];
        initial[field.key] = typeof raw === "string" ? raw : JSON.stringify(raw);
      }
      setValues(initial);
    }
  }, [foundation, config.fields, slug]);

  const save = useCallback(
    async (newValues: Record<string, string>) => {
      try {
        const parsed: Record<string, unknown> = {};
        for (const [key, value] of Object.entries(newValues)) {
          try { parsed[key] = JSON.parse(value); } catch { parsed[key] = value; }
        }
        await saveMutation.mutateAsync(parsed);
        setLastSaved(new Date());
        setHasChanged(false);
      } catch (err) {
        console.error(`[Section ${slug}] Save failed:`, err);
      }
    },
    [slug, saveMutation],
  );

  const handleChange = (key: string, newValue: string) => {
    setValues((prev) => ({ ...prev, [key]: newValue }));
    setHasChanged(true);

    if (saveTimer) clearTimeout(saveTimer);
    const timer = setTimeout(() => save({ [key]: newValue }), 800);
    setSaveTimer(timer);
  };

  const handleSaveAll = async () => {
    if (saveTimer) clearTimeout(saveTimer);
    await save(values);
  };

  const isSaving = saveMutation.isPending;

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-[var(--muted-foreground)]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--background)] flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-[var(--background)]/90 backdrop-blur border-b border-[var(--border)] px-6 py-4 flex items-center gap-6">
        <Link
          href="/app/foundation"
          className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
        >
          <ArrowLeftIcon className="w-4 h-4" />
          Foundation
        </Link>
        <div className="h-4 border-l border-[var(--border)]" />
        <div>
          <h1 className="font-[family-name:var(--font-display)] text-lg">{config.title}</h1>
        </div>
        <div className="ml-auto flex items-center gap-3 text-xs font-mono">
          {isSaving ? (
            <span className="text-[var(--muted-foreground)] animate-pulse">Saving...</span>
          ) : hasChanged ? (
            <span className="text-amber-600">Unsaved changes</span>
          ) : lastSaved ? (
            <span className="text-green-600 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              Saved
            </span>
          ) : null}
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 flex flex-col items-center py-12 px-6">
        <GsapBridge stagger={true} className="w-full max-w-2xl space-y-8">
          <div className="gsap-reveal">
            <p className="text-[var(--muted-foreground)] text-base leading-relaxed">
              {config.description}
            </p>
          </div>

          <div className="gsap-reveal space-y-6">
            {config.fields.map((field) => (
              <div key={field.key} className="space-y-2">
                <label className="text-xs uppercase tracking-widest font-mono text-[var(--muted-foreground)] block">
                  {field.label}
                </label>

                {field.type === "textarea" ? (
                  <textarea
                    value={values[field.key] ?? ""}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    className="w-full min-h-[120px] bg-transparent border border-[var(--border)] p-4 focus:outline-none focus:ring-1 focus:ring-[var(--primary)] text-sm leading-relaxed resize-y transition-shadow"
                    placeholder={`Enter ${field.label.toLowerCase()}...`}
                  />
                ) : field.type === "slider" ? (
                  <div className="flex items-center gap-4 pt-2">
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={Number(values[field.key]) || 3}
                      onChange={(e) => handleChange(field.key, e.target.value)}
                      className="flex-1 accent-[var(--primary)]"
                    />
                    <span className="text-xs font-mono w-4 text-right">
                      {values[field.key] ?? "3"}
                    </span>
                  </div>
                ) : (
                  <input
                    type="text"
                    value={values[field.key] ?? ""}
                    onChange={(e) => handleChange(field.key, e.target.value)}
                    className="w-full h-12 bg-transparent border border-[var(--border)] px-4 focus:outline-none focus:ring-1 focus:ring-[var(--primary)] text-sm transition-shadow"
                    placeholder={`Enter ${field.label.toLowerCase()}...`}
                  />
                )}
              </div>
            ))}
          </div>

          {/* Save All button */}
          <div className="gsap-reveal flex justify-end gap-3 pt-4">
            <button
              onClick={handleSaveAll}
              disabled={isSaving || !hasChanged}
              className="px-8 py-3 bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 disabled:opacity-40 text-xs font-mono uppercase tracking-widest transition-opacity"
            >
              {isSaving ? "Saving..." : "Save All"}
            </button>
          </div>
        </GsapBridge>
      </main>
    </div>
  );
}

function Loader2({ className }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className ?? ""}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}
