"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { ArrowRight, ArrowDown, Info } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";
import { getApiBaseUrl } from "@/lib/api";

/**
 * Foundation Screen 7: The Transformation Promise
 * Defines the value of the product via Before/After states.
 */
export default function FoundationStep7() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [before, setBefore] = useState("");
  const [after, setAfter] = useState("");
  const [showTip, setShowTip] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setStep(7);
    const existing = sectionData.transformation;
    if (existing) {
      setBefore(existing.before || "");
      setAfter(existing.after || "");
    }
  }, [setStep, sectionData]);

  const handleContinue = async () => {
    if (before.trim().length < 20 || after.trim().length < 20) {
      setError(
        "Please provide at least 20 characters for both the Before and After states to ensure clarity.",
      );
      return;
    }

    setIsSubmitting(true);
    const data = { before, after };

    try {
      const token = await getToken();
      setSectionData("transformation", data);

      await fetch(`${getApiBaseUrl()}/api/v1/foundation/section/transformation`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/8");
    } catch (err) {
      console.error("[Foundation7] Save Error:", err);
      setError("Failed to save. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[580px] space-y-10">
        {/* HEADER */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-[#2A2622]">
            What does life look like after working with you?
          </h1>
          <p className="text-base text-[#6B655E]">
            Not your features. The actual before and after. What is measurably or emotionally
            different for your customer?
          </p>
        </div>

        {/* TRANSFORMATION GRID */}
        <div className="relative group">
          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-center">
            {/* BEFORE CARD */}
            <div className="bg-[#262626] border border-[#E5DED4] rounded-2xl p-5 space-y-4">
              <div className="inline-block px-2 py-0.5 bg-red-400/10 rounded-full">
                <span className="text-[10px] font-mono font-bold tracking-widest text-red-400 uppercase">
                  Before
                </span>
              </div>
              <div className="space-y-2">
                <label className="text-sm text-[#6B655E]">
                  What their life looked like before you
                </label>
                <textarea
                  rows={4}
                  className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-red-400 transition-colors resize-none"
                  placeholder="Manually updating spreadsheets every evening, missing stock errors, losing sales..."
                  value={before}
                  onChange={(e) => setBefore(e.target.value)}
                />
              </div>
            </div>

            {/* ARROW DIVIDER */}
            <div className="flex justify-center md:h-full md:items-center py-2 md:py-0">
              <ArrowRight className="hidden md:block w-6 h-6 text-[#9A948C] group-hover:text-[#f59e0b] transition-colors" />
              <ArrowDown className="md:hidden w-6 h-6 text-[#9A948C]" />
            </div>

            {/* AFTER CARD */}
            <div className="bg-[#262626] border border-[#E5DED4] rounded-2xl p-5 space-y-4">
              <div className="inline-block px-2 py-0.5 bg-green-400/10 rounded-full">
                <span className="text-[10px] font-mono font-bold tracking-widest text-green-400 uppercase">
                  After
                </span>
              </div>
              <div className="space-y-2">
                <label className="text-sm text-[#6B655E]">
                  What their life looks like after you
                </label>
                <textarea
                  rows={4}
                  className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-green-400 transition-colors resize-none"
                  placeholder="Real-time inventory visibility on their phone, stockouts down 80%, Sunday evenings free..."
                  value={after}
                  onChange={(e) => setAfter(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>

        {/* AI TIP PANEL */}
        <div className="space-y-4">
          {!showTip ? (
            <button
              onClick={() => setShowTip(true)}
              className="group flex items-center gap-2 text-sm text-[#6B655E] hover:text-[#2A2622] transition-colors"
            >
              <Info className="w-4 h-4 text-[#6B655E]" />
              <span>Not sure how to phrase the after? Let your product do the talking →</span>
            </button>
          ) : (
            <div className="bg-[#FBF8F2] border-l-2 border-[#f59e0b]/20 p-4 rounded-r-lg space-y-2 animate-in fade-in slide-in-from-left-2 duration-300">
              <p className="text-sm font-bold text-[#9A948C] uppercase tracking-widest flex items-center gap-2">
                <span className="text-[#f59e0b]">Pro Tip</span>
              </p>
              <p className="text-sm text-[#6B655E] leading-relaxed">
                The best &quot;after&quot; statements are specific and measurable.{" "}
                <span className="text-[#4A4540] font-medium italic">&quot;Save time&quot;</span> is
                weak.{" "}
                <span className="text-green-400 font-medium italic">
                  &quot;Two fewer hours per day on reporting&quot;
                </span>{" "}
                is strong.{" "}
                <span className="text-[#4A4540] font-medium italic">
                  &quot;Feel less stressed&quot;
                </span>{" "}
                is weak.{" "}
                <span className="text-green-400 font-medium italic">
                  &quot;Know exactly what to post three days ahead&quot;
                </span>{" "}
                is strong.
              </p>
            </div>
          )}
        </div>

        {/* ERROR & CTA */}
        <div className="space-y-4 pt-4">
          {error && (
            <p className="text-center text-sm text-red-500 animate-in fade-in duration-200">
              {error}
            </p>
          )}
          <button
            onClick={handleContinue}
            disabled={isSubmitting}
            className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
          >
            {isSubmitting ? "Saving..." : "Continue"}
          </button>
        </div>
      </div>
    </div>
  );
}
