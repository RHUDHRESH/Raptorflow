"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { useFoundationStore } from "@/state/foundation-store";
import { getApiBaseUrl } from "@/lib/api";

/**
 * Foundation Screen 5: The Customer Problem
 * Reframes the product as a solution to a specific pain point.
 */
export default function FoundationStep5() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [problemStatement, setProblemStatement] = useState("");
  const [usedScanSuggestion, setUsedScanSuggestion] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setStep(5);
    const existing = sectionData.customer_problem;
    if (existing) {
      setProblemStatement(existing.problemStatement || "");
      setUsedScanSuggestion(existing.usedScanSuggestion || false);
    }
  }, [setStep, sectionData]);

  const scanProblem = sectionData.scan_results?.problem_statement;
  const scanPrompt = useMemo(() => scanProblem?.trim() ?? "", [scanProblem]);

  const useScanSuggestion = () => {
    if (!scanPrompt) return;
    setProblemStatement(scanPrompt);
    setUsedScanSuggestion(true);
  };

  /**
   * Submit handler
   */
  const handleContinue = async () => {
    if (problemStatement.trim().length < 30) {
      setError("Please describe the problem in a bit more detail (at least 30 characters).");
      return;
    }

    setIsSubmitting(true);
    const data = { problemStatement, usedScanSuggestion };

    try {
      const token = await getToken();
      setSectionData("customer_problem", data);

      await fetch(`${getApiBaseUrl()}/api/v1/foundation/section/customer_problem`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/6");
    } catch (err) {
      console.error("[Foundation5] Save Error:", err);
      setError("Failed to save. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[580px] space-y-10">
        {/* HEADER */}
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-[#2A2622]">What problem do you solve?</h1>
          <p className="text-base text-[#6B655E] leading-relaxed">
            Not a description of your product. The actual pain your customer was living with before
            they found you. The frustration they had at 11pm. The thing that made them search for a
            solution.
          </p>
        </div>

        {/* SCAN SUGGESTION STRIP */}
        {scanProblem && (
          <div className="space-y-2 animate-in fade-in duration-700">
            <label className="text-[10px] font-bold text-[#6B655E] uppercase tracking-widest">
              What your website says you solve:
            </label>
            <div className="p-3 bg-[#FBF8F2] border border-[#E5DED4] rounded-lg">
              <p className="text-sm text-[#6B655E] italic leading-relaxed">
                &quot;{scanProblem}&quot;
              </p>
              <button
                onClick={() => {
                  setProblemStatement(scanProblem);
                  setUsedScanSuggestion(true);
                }}
                className="mt-2 text-xs text-[#6B655E] underline hover:text-[#2A2622] transition-colors"
              >
                Use this as a starting point
              </button>
            </div>
          </div>
        )}

        {/* MAIN TEXTAREA */}
        <div className="space-y-4">
          <textarea
            autoFocus
            rows={6}
            className="w-full bg-[#262626] border border-[#D5CBC0] rounded-xl px-5 py-4 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-[#f59e0b] resize-y transition-colors"
            placeholder="Before they found us, our customers were dealing with..."
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
          />

          <div className="flex items-center justify-between min-h-[20px] gap-3">
            <div className="text-[10px] font-mono">
              {problemStatement.length >= 480 && (
                <span className="text-[#f59e0b]">We&apos;ll use the first 500 characters</span>
              )}
            </div>

            {scanPrompt ? (
              <button
                onClick={useScanSuggestion}
                className="flex items-center gap-2 text-sm text-[#f59e0b] hover:opacity-80 transition-opacity disabled:opacity-50"
              >
                <span>Use scan suggestion →</span>
              </button>
            ) : (
              <span className="text-xs text-[#9A948C]">Write the problem directly.</span>
            )}
          </div>
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
