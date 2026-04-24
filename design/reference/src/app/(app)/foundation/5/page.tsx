"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Loader2, Sparkles, X, Check } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

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
  const [isHelping, setIsHelping] = useState(false);
  const [showHelperPanel, setShowHelperPanel] = useState(false);
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

  /**
   * Mock AI Articulation helper logic
   */
  const handleAiHelp = () => {
    setIsHelping(true);
    setError(null);
    setTimeout(() => {
      setIsHelping(false);
      setShowHelperPanel(true);
    }, 1500);
  };

  const useAiSuggestion = () => {
    const suggestion = "Difficulty tracking inventory across multiple locations without real-time visibility, causing stock-outs and overstocking.";
    setProblemStatement(suggestion);
    setShowHelperPanel(false);
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

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/customer_problem`, {
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
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[580px] space-y-10">
        
        {/* HEADER */}
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-white">
            What problem do you solve?
          </h1>
          <p className="text-base text-zinc-400 leading-relaxed">
            Not a description of your product. The actual pain your customer was living with before they found you. 
            The frustration they had at 11pm. The thing that made them search for a solution.
          </p>
        </div>

        {/* SCAN SUGGESTION STRIP */}
        {scanProblem && (
          <div className="space-y-2 animate-in fade-in duration-700">
            <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
              What your website says you solve:
            </label>
            <div className="p-3 bg-[#1e1e1e] border border-zinc-800 rounded-lg">
              <p className="text-sm text-zinc-400 italic leading-relaxed">
                &quot;{scanProblem}&quot;
              </p>
              <button
                onClick={() => { setProblemStatement(scanProblem); setUsedScanSuggestion(true); }}
                className="mt-2 text-xs text-zinc-500 underline hover:text-white transition-colors"
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
            className="w-full bg-[#262626] border border-zinc-700 rounded-xl px-5 py-4 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] resize-y transition-colors"
            placeholder="Before they found us, our customers were dealing with..."
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
          />
          
          <div className="flex items-center justify-between min-h-[20px]">
            {/* Char warning */}
            <div className="text-[10px] font-mono">
              {problemStatement.length >= 480 && (
                <span className="text-[#f59e0b]">
                  We&apos;ll use the first 500 characters
                </span>
              )}
            </div>

            {/* AI HELPER BUTTON */}
            {!showHelperPanel && (
              <button
                disabled={isHelping}
                onClick={handleAiHelp}
                className="flex items-center gap-2 text-sm text-[#f59e0b] hover:opacity-80 transition-opacity disabled:opacity-50"
              >
                {isHelping ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                <span>Help me articulate this →</span>
              </button>
            )}
          </div>

          {/* AI SUGGESTION PANEL */}
          {showHelperPanel && (
            <div className="p-4 bg-[#262626] border border-zinc-700 rounded-xl space-y-4 animate-in fade-in zoom-in-95 duration-300 shadow-2xl">
              <div className="space-y-1">
                <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Suggested Framing:</p>
                <p className="text-sm text-zinc-200 leading-relaxed italic">
                  &quot;Based on your product, you might be solving: difficulty tracking inventory across multiple locations without real-time visibility, causing stock-outs and overstocking.&quot;
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={useAiSuggestion}
                  className="flex items-center gap-2 bg-[#f59e0b]/10 border border-[#f59e0b] text-[#f59e0b] px-4 py-2 rounded-lg text-xs font-bold hover:bg-[#f59e0b]/20 transition-all"
                >
                  <Check className="w-3 h-3" />
                  Use this
                </button>
                <button
                  onClick={() => setShowHelperPanel(false)}
                  className="flex items-center gap-2 text-zinc-500 hover:text-white px-2 py-2 text-xs transition-colors"
                >
                  <X className="w-3 h-3" />
                  Not quite, dismiss
                </button>
              </div>
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
            className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-700 disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
          >
            {isSubmitting ? "Saving..." : "Continue"}
          </button>
        </div>

      </div>
    </div>
  );
}
