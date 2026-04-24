"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

/**
 * Foundation Screen 3: Business Stage and Team Size
 * Standardizes the user's operational scale.
 */
export default function FoundationStep3() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { setSectionData, setStep } = useFoundationStore();

  const [selectedStage, setSelectedStage] = useState<string | null>(null);
  const [selectedTeamSize, setSelectedTeamSize] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(3);
  }, [setStep]);

  const STAGES = [
    { id: "pre-revenue", title: "Pre-revenue", desc: "Building something, not yet selling" },
    { id: "early-revenue", title: "Early revenue", desc: "Annual sales under ₹10 lakh" },
    { id: "growing", title: "Growing", desc: "₹10 lakh to ₹1 crore in annual sales" },
    { id: "scaling", title: "Scaling", desc: "₹1 crore to ₹10 crore in annual sales" },
    { id: "established", title: "Established", desc: "Above ₹10 crore in annual sales" },
  ];

  const TEAM_SIZES = ["Just me", "2–3 people", "Small team (4–10)", "Larger team (10+)"];

  const handleContinue = async () => {
    if (!selectedStage || !selectedTeamSize) return;

    setIsSubmitting(true);
    const data = { stage: selectedStage, teamSize: selectedTeamSize };

    try {
      const token = await getToken();
      
      // Save locally
      setSectionData("business_stage", data);

      // Save to backend
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/business_stage`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/4");
    } catch (err) {
      console.error("[Foundation3] Error saving stage:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[560px] space-y-10">
        
        {/* HEADER */}
        <h1 className="text-3xl font-bold text-white">
          Where are you in your growth journey?
        </h1>

        {/* STAGE SELECTOR */}
        <div className="flex flex-col gap-3">
          {STAGES.map((stage, index) => {
            const isSelected = selectedStage === stage.id;
            return (
              <div
                key={stage.id}
                onClick={() => setSelectedStage(stage.id)}
                className={cn(
                  "flex items-center gap-4 p-5 rounded-xl cursor-pointer border transition-all duration-200",
                  isSelected 
                    ? "border-[#f59e0b] bg-[#f59e0b]/10" 
                    : "bg-[#262626] border-zinc-700 hover:border-zinc-500"
                )}
              >
                {/* Number Badge */}
                <div className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-mono transition-colors",
                  isSelected 
                    ? "bg-[#f59e0b] text-black" 
                    : "bg-zinc-700 text-zinc-400"
                )}>
                  {index + 1}
                </div>
                
                <div className="flex flex-col">
                  <span className="font-medium text-white">{stage.title}</span>
                  <span className="text-sm text-zinc-400">{stage.desc}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* TEAM SIZE SELECTOR */}
        <div className="space-y-4 pt-4">
          <label className="text-base text-zinc-300 font-medium">
            How many people work on marketing?
          </label>
          <div className="flex flex-wrap gap-2">
            {TEAM_SIZES.map((size) => {
              const isSelected = selectedTeamSize === size;
              return (
                <button
                  key={size}
                  onClick={() => setSelectedTeamSize(size)}
                  className={cn(
                    "px-4 py-2 rounded-full border text-sm transition-all duration-200",
                    isSelected
                      ? "border-[#f59e0b] bg-[#f59e0b]/10 text-white"
                      : "border-zinc-700 bg-transparent text-zinc-300 hover:border-zinc-500"
                  )}
                >
                  {size}
                </button>
              );
            })}
          </div>
        </div>

        {/* CONTINUE BUTTON */}
        <button
          onClick={handleContinue}
          disabled={!selectedStage || !selectedTeamSize || isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-700 disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
        >
          {isSubmitting ? "Saving..." : "Continue"}
        </button>

      </div>
    </div>
  );
}
