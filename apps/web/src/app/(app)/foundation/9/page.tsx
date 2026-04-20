"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { 
  ShoppingCart, 
  RefreshCw, 
  Briefcase, 
  Handshake, 
  Store, 
  MoreHorizontal, 
  Check 
} from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

/**
 * Foundation Screen 9: Pricing and Business Model
 * Identifies the revenue streams and transaction sizes.
 */
export default function FoundationStep9() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [priceRange, setPriceRange] = useState({ from: "", to: "", varies: false });
  const [ltv, setLtv] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(9);
    const existing = sectionData.pricing_model;
    if (existing) {
      setSelectedModels(existing.businessModels || []);
      setPriceRange(existing.priceRange || { from: "", to: "", varies: false });
      setLtv(existing.ltv || "");
    }
  }, [setStep, sectionData]);

  const MODELS = [
    { id: "one-time",   label: "One-time purchase",      desc: "Customers pay once per product", icon: ShoppingCart },
    { id: "recurring",  label: "Recurring subscription", desc: "Monthly or annual fees",        icon: RefreshCw },
    { id: "project",    label: "Project-based",          desc: "Fixed fee per engagement",      icon: Briefcase },
    { id: "retainer",   label: "Retainer",               desc: "Ongoing monthly relationship",  icon: Handshake },
    { id: "market",     label: "Marketplace",            desc: "Take a cut of transactions",    icon: Store },
    { id: "other",      label: "Other",                  desc: "Something else entirely",       icon: MoreHorizontal },
  ];

  const toggleModel = (id: string) => {
    setSelectedModels(prev => 
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  const handleContinue = async () => {
    if (selectedModels.length === 0) return;

    setIsSubmitting(true);
    const data = {
      businessModels: selectedModels,
      priceRange,
      ltv: ltv,
    };

    try {
      const token = await getToken();
      setSectionData("pricing_model", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/pricing_model`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/10");
    } catch (err) {
      console.error("[Foundation9] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[560px] space-y-10">
        
        {/* HEADER */}
        <h1 className="text-3xl font-bold text-[#2A2622]">
          How does your business make money?
        </h1>

        {/* MODEL SELECTOR */}
        <div className="grid grid-cols-2 gap-3">
          {MODELS.map((model) => {
            const isSelected = selectedModels.includes(model.id);
            return (
              <div
                key={model.id}
                onClick={() => toggleModel(model.id)}
                className={cn(
                  "relative p-4 rounded-xl cursor-pointer border transition-all duration-200",
                  isSelected 
                    ? "border-[#f59e0b] bg-[#f59e0b]/10" 
                    : "bg-[#262626] border-[#D5CBC0] hover:border-[#D5CBC0]"
                )}
              >
                {isSelected && (
                  <div className="absolute top-3 right-3">
                    <Check className="w-4 h-4 text-[#f59e0b]" />
                  </div>
                )}
                <model.icon className={cn("w-5 h-5 mb-3", isSelected ? "text-[#f59e0b]" : "text-[#6B655E]")} />
                <div className="space-y-0.5">
                  <p className="text-sm font-semibold text-[#2A2622] leading-tight">{model.label}</p>
                  <p className="text-[11px] text-[#6B655E] leading-tight">{model.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* PRICE RANGE INPUT (CONDITIONAL) */}
        {selectedModels.length > 0 && (
          <div className="space-y-4 pt-4 animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-[#9A948C] tracking-tight">What does your core offering cost?</label>
              {!priceRange.varies && (
                <span className="text-[10px] text-[#6B655E] uppercase tracking-widest font-bold">In INR (₹)</span>
              )}
            </div>

            {priceRange.varies ? (
              <div className="p-4 bg-[#262626] border border-[#E5DED4] rounded-lg">
                <p className="text-sm text-[#f59e0b] font-medium italic">Pricing varies per customer or project</p>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <div className="relative flex-1">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#6B655E] text-sm">₹</span>
                  <input
                    type="number"
                    className="w-full bg-[#262626] border border-[#D5CBC0] rounded-lg pl-8 pr-4 py-3 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-[#f59e0b] [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                    placeholder="From 0"
                    value={priceRange.from}
                    onChange={(e) => setPriceRange({...priceRange, from: e.target.value})}
                  />
                </div>
                <span className="text-[#9A948C]">–</span>
                <div className="relative flex-1">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#6B655E] text-sm">₹</span>
                  <input
                    type="number"
                    className="w-full bg-[#262626] border border-[#D5CBC0] rounded-lg pl-8 pr-4 py-3 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-[#f59e0b] [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                    placeholder="To 99999"
                    value={priceRange.to}
                    onChange={(e) => setPriceRange({...priceRange, to: e.target.value})}
                  />
                </div>
              </div>
            )}

            <label className="flex items-center gap-2 cursor-pointer group w-fit">
              <input 
                type="checkbox"
                className="accent-[#f59e0b] w-4 h-4"
                checked={priceRange.varies}
                onChange={(e) => setPriceRange({...priceRange, varies: e.target.checked})}
              />
              <span className="text-sm text-[#6B655E] group-hover:text-[#2A2622] transition-colors">Varies widely</span>
            </label>
          </div>
        )}

        {/* LTV INPUT */}
        <div className="space-y-2 pt-4">
          <label className="text-sm text-[#9A948C] font-medium">Average customer lifetime value (optional)</label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#6B655E] text-sm">₹</span>
            <input
              type="number"
              className="w-full bg-[#262626] border border-[#D5CBC0] rounded-lg pl-8 pr-4 py-3 text-[#2A2622] focus:outline-none focus:border-[#f59e0b]"
              placeholder="0"
              value={ltv}
              onChange={(e) => setLtv(e.target.value)}
            />
          </div>
          <p className="text-xs text-[#6B655E]">What does a typical customer spend with you over their entire relationship?</p>
        </div>

        {/* CONTINUE BUTTON */}
        <button
          onClick={handleContinue}
          disabled={selectedModels.length === 0 || isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all mt-8"
        >
          {isSubmitting ? "Saving..." : "Continue"}
        </button>

      </div>
    </div>
  );
}
