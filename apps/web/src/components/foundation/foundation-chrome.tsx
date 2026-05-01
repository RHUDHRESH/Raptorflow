"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/cn";

/**
 * FoundationChrome
 * Client component that handles the persistent UI elements
 * like the progress bar, back button, and step counter.
 */
export function FoundationChrome() {
  const router = useRouter();
  const { currentStep, isAutoSaving } = useFoundationStore();

  const progress = (currentStep / 21) * 100;

  return (
    <>
      {/* 1. PROGRESS BAR */}
      <div className="fixed top-0 left-0 right-0 z-50 h-[3px] bg-[#E5DED4] pointer-events-none">
        <div
          className="h-full bg-[#f59e0b] transition-all duration-500 ease-out shadow-[0_0_8px_rgba(217,119,87,0.5)]"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* 2. BACK BUTTON */}
      {currentStep > 1 && (
        <button
          onClick={() => router.back()}
          className="fixed top-4 left-6 z-50 flex items-center gap-2 text-sm text-[#6B655E] hover:text-[#2A2622] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>
      )}

      {/* 3. STEP COUNTER & 4. SAVE INDICATOR */}
      <div className="fixed top-4 right-6 z-50 flex flex-col items-end gap-1">
        {currentStep > 1 && (
          <span className="text-sm text-[#6B655E] font-mono">Step {currentStep} of 21</span>
        )}

        <div
          className={cn(
            "text-[10px] text-[#6B655E] font-mono transition-opacity duration-300",
            isAutoSaving ? "opacity-100" : "opacity-0",
          )}
        >
          Saving...
        </div>
      </div>
    </>
  );
}
