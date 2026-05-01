"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import {
  HelpCircle,
  TrendingDown,
  DollarSign,
  Clock,
  BarChart2,
  FileText,
  Eye,
  AlertTriangle,
  ShoppingCart,
  Zap,
  Check,
} from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";
import { getApiBaseUrl } from "@/lib/api";

/**
 * Foundation Screen 18: Current Frustrations
 * Identifies the specific pain points to tailor AI response and prioritization.
 */
export default function FoundationStep18() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [selectedFrustrations, setSelectedFrustrations] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(18);
    const existing = sectionData.frustrations;
    if (existing?.frustrations) {
      setSelectedFrustrations(existing.frustrations);
    }
  }, [setStep, sectionData]);

  const FRUSTRATIONS = [
    {
      id: "no_ideas",
      label: "I don't know what to post",
      desc: "Running out of ideas. Every week is a struggle.",
      icon: HelpCircle,
    },
    {
      id: "no_engagement",
      label: "I post but get no engagement",
      desc: "The content goes out. Nobody reacts.",
      icon: TrendingDown,
    },
    {
      id: "no_ads_roi",
      label: "I run ads but don't see ROI",
      desc: "Money in. Nothing measurable out.",
      icon: DollarSign,
    },
    {
      id: "no_time",
      label: "I know what to do but have no time",
      desc: "The strategy is clear. The execution never happens.",
      icon: Clock,
    },
    {
      id: "confused_metrics",
      label: "I don't understand my metrics",
      desc: "Analytics dashboards that tell me nothing useful.",
      icon: BarChart2,
    },
    {
      id: "generic_content",
      label: "My content sounds generic",
      desc: "It could be any brand. Not ours.",
      icon: FileText,
    },
    {
      id: "competitor_blind",
      label: "I have no idea what competitors do",
      desc: "Flying blind while others adapt and react.",
      icon: Eye,
    },
    {
      id: "agency_burn",
      label: "I've tried agencies & been burned",
      desc: "Money spent. Results not delivered. Trust broken.",
      icon: AlertTriangle,
    },
    {
      id: "lead_conv",
      label: "I can't convert leads I have",
      desc: "People know us. They're not buying.",
      icon: ShoppingCart,
    },
    {
      id: "starting_zero",
      label: "I'm starting from scratch",
      desc: "Zero following. Zero email list. Zero.",
      icon: Zap,
    },
  ];

  const toggleFrustration = (id: string) => {
    setError(null);
    setSelectedFrustrations((prev) =>
      prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id],
    );
  };

  const handleContinue = async () => {
    if (selectedFrustrations.length === 0) {
      setError("Select at least one. This shapes how your AI team works.");
      return;
    }

    setIsSubmitting(true);
    const data = { frustrations: selectedFrustrations };

    try {
      const token = await getToken();
      setSectionData("frustrations", data);

      await fetch(`${getApiBaseUrl()}/api/v1/foundation/section/frustrations`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/19");
    } catch (err) {
      console.error("[Foundation18] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[600px] space-y-10">
        {/* HEADER */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-[#2A2622] leading-tight text-center md:text-left">
            What&apos;s your biggest marketing frustration right now?
          </h1>
          <p className="text-base text-[#6B655E] text-center md:text-left">
            Select all that apply.
          </p>
        </div>

        {/* FRUSTRATION GRID */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {FRUSTRATIONS.map((f) => {
            const isSelected = selectedFrustrations.includes(f.id);
            return (
              <div
                key={f.id}
                onClick={() => toggleFrustration(f.id)}
                className={cn(
                  "relative p-4 rounded-xl border flex items-start gap-3 transition-all duration-200 cursor-pointer overflow-hidden",
                  isSelected
                    ? "border-[#f59e0b] bg-[#f59e0b]/10 shadow-[0_0_15px_rgba(217,119,87,0.1)]"
                    : "bg-[#262626] border-[#D5CBC0] hover:border-[#D5CBC0]",
                )}
              >
                {isSelected && (
                  <div className="absolute top-3 right-3 shrink-0">
                    <Check className="w-4 h-4 text-[#f59e0b]" />
                  </div>
                )}

                <div className="shrink-0 mt-0.5">
                  <f.icon
                    className={cn(
                      "w-5 h-5 transition-colors",
                      isSelected ? "text-[#f59e0b]" : "text-[#6B655E]",
                    )}
                  />
                </div>

                <div className="space-y-1 pr-4">
                  <p className="text-sm font-bold text-[#2A2622] leading-tight">{f.label}</p>
                  <p className="text-[11px] text-[#6B655E] leading-tight font-medium">{f.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* CTA */}
        <div className="space-y-4 pt-6">
          {error && <p className="text-center text-sm text-red-500 animate-pulse">{error}</p>}
          <button
            onClick={handleContinue}
            disabled={isSubmitting}
            className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all shadow-xl"
          >
            {isSubmitting ? "Calibrating AI Response..." : "Continue"}
          </button>
        </div>
      </div>
    </div>
  );
}
