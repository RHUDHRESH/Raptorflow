"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { X, Plus, Zap, Check } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

interface CompetitorSlot {
  url: string;
  notes: string;
  error: string | null;
  isValidated: boolean;
}

/**
 * Foundation Screen 8: Competitors
 * Captures URLs of competitors for automated intelligence monitoring.
 */
export default function FoundationStep8() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [slots, setSlots] = useState<CompetitorSlot[]>(
    Array.from({ length: 5 }, () => ({ url: "", notes: "", error: null, isValidated: false }))
  );
  const [visibleSlots, setVisibleSlots] = useState(3);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(8);
    const existing = sectionData.competitors;
    if (existing?.competitors) {
      const merged = slots.map((s, i) => {
        const ext = existing.competitors[i];
        if (ext) return { ...s, url: ext.url, notes: ext.notes || "", isValidated: true };
        return s;
      });
      setSlots(merged);
      if (existing.competitors.length > 3) setVisibleSlots(existing.competitors.length);
    }
  }, [setStep, sectionData]);

  const suggestions = sectionData.scan_results?.competitor_suggestions || [];

  /**
   * URL Validation on Blur
   */
  const handleBlur = (index: number) => {
    const slot = slots[index];
    if (!slot.url.trim()) {
      updateSlot(index, { error: null, isValidated: false });
      return;
    }

    // Must be valid URL format
    const urlPattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/i;
    if (!urlPattern.test(slot.url)) {
      updateSlot(index, { error: "Enter a valid URL like https://competitor.com", isValidated: false });
    } else {
      updateSlot(index, { error: null, isValidated: true });
    }
  };

  const updateSlot = (index: number, updates: Partial<CompetitorSlot>) => {
    setSlots(prev => prev.map((s, i) => (i === index ? { ...s, ...updates } : s)));
  };

  const addFromSuggestion = (url: string) => {
    const emptyIndex = slots.findIndex(s => !s.url);
    if (emptyIndex !== -1 && emptyIndex < 5) {
      if (emptyIndex >= visibleSlots) setVisibleSlots(emptyIndex + 1);
      updateSlot(emptyIndex, { url, isValidated: true, error: null });
    }
  };

  const clearSlot = (index: number) => {
    updateSlot(index, { url: "", notes: "", error: null, isValidated: false });
  };

  const hasValidEntry = slots.some(s => s.url && !s.error);

  const handleContinue = async (skip = false) => {
    setIsSubmitting(true);
    const validCompetitors = skip ? [] : slots.filter(s => s.url && !s.error).map(s => ({ url: s.url, notes: s.notes }));

    try {
      const token = await getToken();
      setSectionData("competitors", { competitors: validCompetitors });

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/competitors`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ competitors: validCompetitors }),
      });

      router.push("/foundation/9");
    } catch (err) {
      console.error("[Foundation8] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[600px] space-y-10">
        
        {/* HEADER */}
        <div className="space-y-4">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-white">Who are you competing against?</h1>
            <p className="text-base text-zinc-400">Add their URLs. Your AI team will start monitoring them immediately.</p>
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#f59e0b]/10 rounded-full border border-[#f59e0b]/20">
            <Zap className="w-3 h-3 text-[#f59e0b] fill-[#f59e0b]" />
            <span className="text-[10px] font-bold text-[#f59e0b] uppercase tracking-wider">
              Intel tracking starts immediately
            </span>
          </div>
        </div>

        {/* SUGGESTIONS (from Scan Results) */}
        {suggestions.length > 0 && slots.every(s => s.url) === false && (
          <div className="space-y-3 animate-in fade-in duration-700">
            <p className="text-[10px] uppercase font-bold tracking-widest text-zinc-500">Suggested from your website scan:</p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s: string) => (
                <button
                  key={s}
                  onClick={() => addFromSuggestion(s)}
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 rounded-full text-xs transition-colors"
                >
                  {s.replace(/^https?:\/\//, "")}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* COMPETITOR SLOTS */}
        <div className="space-y-4">
          {slots.slice(0, visibleSlots).map((slot, index) => (
            <div key={index} className="space-y-1.5 group animate-in slide-in-from-top-2 duration-300">
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-zinc-600 w-5 tracking-tighter">0{index + 1}</span>
                
                <div className={cn(
                  "flex-1 relative border transition-all duration-300",
                  slot.error ? "border-red-500/50" : slot.isValidated ? "border-green-500/30" : "border-zinc-700 focus-within:border-[#f59e0b]"
                )}>
                  <input
                    className="w-full bg-[#262626] px-4 py-3 text-sm text-white focus:outline-none"
                    placeholder="https://competitor.com"
                    value={slot.url}
                    onChange={(e) => updateSlot(index, { url: e.target.value })}
                    onBlur={() => handleBlur(index)}
                  />
                  {slot.url && (
                    <button 
                      onClick={() => clearSlot(index)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-600 hover:text-white transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {slot.url && !slot.error && (
                  <div className="w-48 animate-in slide-in-from-right-4 duration-300">
                    <input
                      className="w-full bg-[#1a1a1a] border border-zinc-800 rounded-lg px-3 py-3 text-[11px] text-zinc-400 focus:outline-none focus:border-zinc-600"
                      placeholder="What do they do better?"
                      value={slot.notes}
                      onChange={(e) => updateSlot(index, { notes: e.target.value })}
                    />
                  </div>
                )}
              </div>
              
              {slot.error && (
                <p className="pl-8 text-[10px] text-red-500 font-medium">{slot.error}</p>
              )}
            </div>
          ))}

          {visibleSlots < 5 && (
            <button
              onClick={() => setVisibleSlots(v => v + 1)}
              className="flex items-center gap-2 pl-8 text-sm text-zinc-500 hover:text-white transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add another competitor</span>
            </button>
          )}
        </div>

        {/* CTA SECTION */}
        <div className="space-y-4 pt-4">
          <button
            onClick={() => handleContinue()}
            disabled={!hasValidEntry || isSubmitting}
            className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-700 disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
          >
            {isSubmitting ? "Activating Intel..." : "Continue"}
          </button>
          
          <div className="flex flex-col items-center gap-4">
            <button
              onClick={() => handleContinue(true)}
              className="text-sm text-zinc-500 hover:text-white transition-colors"
            >
              Skip for now
            </button>
            <p className="text-[10px] text-zinc-600 uppercase tracking-widest">
              You can add competitors later from the Intel page
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
