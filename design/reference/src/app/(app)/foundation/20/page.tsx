"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { AlertTriangle, Loader2, Building, X, Check } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

interface BrandSlot {
  name: string;
  color: string;
  admiredFor: string;
  status: "empty" | "identifying" | "filled";
  identified: boolean;
}

/**
 * Foundation Screen 20: Reference Brands
 * Identifies aesthetic and tonal benchmarks from admired brands.
 */
export default function FoundationStep20() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [slots, setSlots] = useState<BrandSlot[]>(
    Array.from({ length: 5 }, () => ({ name: "", color: "", admiredFor: "", status: "empty", identified: false }))
  );
  const [visibleSlots, setVisibleSlots] = useState(2);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConflict, setShowConflict] = useState(false);

  useEffect(() => {
    setStep(20);
    const existing = sectionData.reference_brands;
    if (existing?.referenceBrands) {
      const merged = slots.map((s, i) => {
        const ext = existing.referenceBrands[i];
        if (ext) return { ...s, ...ext, status: "filled" as const };
        return s;
      });
      setSlots(merged);
      if (existing.referenceBrands.length > 2) setVisibleSlots(Math.min(5, existing.referenceBrands.length + 1));
    }
  }, [setStep, sectionData]);

  // Mock Dictionary
  const BRAND_DB: Record<string, string> = {
    apple: "#000000",
    zoho: "#f26d21",
    flipkart: "#2874f0",
    swiggy: "#fc8019",
    zomato: "#e23744",
    freshworks: "#2b88d8",
    nykaa: "#fc2779",
    mamaearth: "#7eb843",
    meesho: "#9b59b6",
    myntra: "#ff3f6c",
  };

  const identifyBrand = (index: number, val: string) => {
    if (!val.trim()) return;
    
    setSlots(prev => prev.map((s, i) => i === index ? { ...s, name: val, status: "identifying" } : s));

    setTimeout(() => {
      const search = val.toLowerCase();
      let foundColor = "";
      let identified = false;

      for (const [key, color] of Object.entries(BRAND_DB)) {
        if (search.includes(key)) {
          foundColor = color;
          identified = true;
          break;
        }
      }

      setSlots(prev => {
        const newSlots = prev.map((s, i) => 
          i === index 
            ? { ...s, color: foundColor, status: "filled" as const, identified } 
            : s
        );
        
        // Progressive reveal
        if (index + 1 === visibleSlots && index + 1 < 5) {
          setVisibleSlots(index + 2);
        }
        
        return newSlots;
      });
    }, 1000);
  };

  // Conflict Detection
  useEffect(() => {
    const filledCount = slots.filter(s => s.status === "filled").length;
    if (filledCount >= 3) {
      const p = sectionData.brand_personality?.sliders;
      if (p) {
        const isPremiumBrand = slots.some(s => 
          s.name.toLowerCase().includes("apple") || s.name.toLowerCase().includes("zoho")
        );
        const isCasualPlayful = p.formalCasual > 60 && p.seriousPlayful > 60;
        
        if (isPremiumBrand && isCasualPlayful) setShowConflict(true);
      }
    }
  }, [slots, sectionData.brand_personality]);

  const removeBrand = (index: number) => {
    setSlots(prev => prev.map((s, i) => i === index ? { name: "", color: "", admiredFor: "", status: "empty", identified: false } : s));
  };

  const handleContinue = async () => {
    const filled = slots.filter(s => s.status === "filled");
    if (filled.length === 0) return;

    setIsSubmitting(true);
    const data = { referenceBrands: filled };

    try {
      const token = await getToken();
      setSectionData("reference_brands", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/reference_brands`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/21");
    } catch (err) {
      console.error("[Foundation20] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[600px] space-y-10">
        
        {/* HEADER */}
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-white leading-tight">Which brands do you admire for their marketing?</h1>
          <p className="text-base text-zinc-400">
            Not brands you think you should name. Brands whose marketing you <span className="italic font-medium text-zinc-200 underline decoration-[#f59e0b]/30">actually</span> respect.
          </p>
        </div>

        {/* INPUT SLOTS */}
        <div className="flex flex-col gap-4">
          {slots.slice(0, visibleSlots).map((slot, index) => (
            <div key={index} className="bg-[#1e1e1e] border border-zinc-800 rounded-xl p-4 space-y-4 shadow-lg transition-all">
              {slot.status === "empty" ? (
                <input
                  className="w-full bg-transparent text-sm text-white placeholder:text-zinc-600 focus:outline-none"
                  placeholder="Enter brand name or website..."
                  onKeyDown={(e) => e.key === "Enter" && identifyBrand(index, (e.target as HTMLInputElement).value)}
                  onBlur={(e) => e.target.value && identifyBrand(index, e.target.value)}
                />
              ) : slot.status === "identifying" ? (
                <div className="flex items-center gap-3 py-1">
                  <Loader2 className="w-5 h-5 text-[#f59e0b] animate-spin" />
                  <span className="text-sm text-zinc-500 font-mono tracking-tighter uppercase">Identifying Brand Landscape...</span>
                </div>
              ) : (
                <div className="space-y-4 animate-in fade-in zoom-in-95 duration-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {slot.identified ? (
                        <div 
                          className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                          style={{ backgroundColor: slot.color }}
                        >
                          {slot.name.charAt(0).toUpperCase()}
                        </div>
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-500">
                          <Building className="w-5 h-5" />
                        </div>
                      )}
                      <span className="text-sm font-bold text-white tracking-tight">{slot.name}</span>
                    </div>
                    <button onClick={() => removeBrand(index)} className="text-zinc-600 hover:text-white transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <input
                    className="w-full bg-[#1a1a1a] border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b]"
                    placeholder="What specifically do you admire? Their voice, design, or content?"
                    value={slot.admiredFor}
                    onChange={(e) => {
                      const newSlots = [...slots];
                      newSlots[index].admiredFor = e.target.value;
                      setSlots(newSlots);
                    }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* CONFLICT PANEL */}
        {showConflict && (
          <div className="bg-[#f59e0b]/10 border border-[#f59e0b]/30 rounded-xl p-5 space-y-4 animate-in slide-in-from-top-4 duration-500">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-[#f59e0b]" />
              <h4 className="text-sm font-bold text-[#f59e0b] uppercase tracking-widest">Brand Voice Mismatch</h4>
            </div>
            <p className="text-sm text-zinc-300 leading-relaxed">
              You admire brands like <span className="text-white font-bold">Apple</span> or <span className="text-white font-bold">Zoho</span> — known for minimal, premium communication. However, your personality sliders are set to <span className="text-[#f59e0b] font-bold">Casual & Playful</span>.
            </p>
            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <button 
                onClick={() => setShowConflict(false)}
                className="px-4 py-2 bg-[#f59e0b]/20 text-[#f59e0b] rounded-lg text-xs font-bold hover:bg-[#f59e0b]/30 transition-all border border-[#f59e0b]/30"
              >
                Keep my slider settings
              </button>
              <button 
                onClick={() => router.push("/foundation/11?returnTo=20")}
                className="px-4 py-2 text-zinc-400 hover:text-white text-xs font-medium transition-colors"
              >
                Let me adjust them →
              </button>
            </div>
          </div>
        )}

        {/* CTA */}
        <button
          onClick={handleContinue}
          disabled={slots.filter(s => s.status === "filled").length === 0 || isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-700 disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all shadow-xl"
        >
          {isSubmitting ? "Syncing Benchmarks..." : "Continue"}
        </button>

      </div>
    </div>
  );
}
