"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Plus, Minus } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

/**
 * Foundation Screen 4: Primary Product or Service
 * Captures the core value proposition of what the user sells.
 */
export default function FoundationStep4() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [primary, setPrimary] = useState({ name: "", description: "" });
  const [secondary, setSecondary] = useState({ name: "", description: "" });
  const [showSecondary, setShowSecondary] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 1. Initial State & Pre-fill
  useEffect(() => {
    setStep(4);
    
    // Check if we have data from the scan (Step 2)
    const scanResults = sectionData.scan_results;
    if (scanResults?.offering && !primary.name) {
      setPrimary(prev => ({ ...prev, name: scanResults.offering }));
    }

    // Check if we already have data for THIS section (if user navigated back)
    const existingData = sectionData.primary_product;
    if (existingData) {
      setPrimary(existingData.primaryProduct || { name: "", description: "" });
      if (existingData.secondProduct) {
        setSecondary(existingData.secondProduct);
        setShowSecondary(true);
      }
    }
  }, [setStep, sectionData]);

  // 2. Validation
  const validate = () => {
    if (!primary.name.trim()) {
      setError("Please name your primary product.");
      return false;
    }
    if (primary.description.trim().length < 20) {
      setError("Tell us a bit more — this helps your AI team understand what they're selling.");
      return false;
    }
    if (showSecondary) {
      if (!secondary.name.trim()) {
        setError("Please name your second product or remove it.");
        return false;
      }
      if (secondary.description.trim().length < 20) {
        setError("Please give a bit more detail for the second product.");
        return false;
      }
    }
    setError(null);
    return true;
  };

  // 3. Submit
  const handleContinue = async () => {
    if (!validate()) return;

    setIsSubmitting(true);
    const data = {
      primaryProduct: primary,
      secondProduct: showSecondary ? secondary : null,
    };

    try {
      const token = await getToken();
      setSectionData("primary_product", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/primary_product`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/5");
    } catch (err) {
      console.error("[Foundation4] Save Error:", err);
      setError("Failed to save. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[560px] space-y-10">
        
        {/* HEADER */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-white">
            What is the main thing you sell?
          </h1>
          <p className="text-base text-zinc-400">
            Be specific. &quot;Software&quot; is not specific. &quot;CRM software for logistics companies&quot; is.
          </p>
        </div>

        {/* PRIMARY PRODUCT STACK */}
        <div className="space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Name it</label>
            <input
              autoFocus
              className="w-full bg-[#262626] border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#f59e0b] transition-colors"
              placeholder="e.g. Inventory management software for kirana stores"
              value={primary.name}
              onChange={(e) => setPrimary({ ...primary, name: e.target.value })}
            />
          </div>

          <div className="space-y-2 relative">
            <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">What does it do, and why does it matter?</label>
            <textarea
              rows={4}
              maxLength={300}
              className="w-full bg-[#262626] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] resize-y"
              placeholder="Describe it as if explaining to someone who's never heard of you. Not features — what changes for the customer."
              value={primary.description}
              onChange={(e) => setPrimary({ ...primary, description: e.target.value })}
            />
            <div className={cn(
              "absolute bottom-3 right-3 text-[10px] font-mono",
              primary.description.length >= 280 ? "text-red-500" : "text-zinc-500"
            )}>
              {primary.description.length} / 300 characters
            </div>
          </div>
        </div>

        {/* SECONDARY PRODUCT TOGGLE & FIELDS */}
        <div className="space-y-8">
          {!showSecondary ? (
            <button
              onClick={() => setShowSecondary(true)}
              className="group flex items-center gap-2 text-sm text-zinc-400 hover:text-white transition-colors"
            >
              <div className="flex h-5 w-5 items-center justify-center rounded-full border border-zinc-700 group-hover:border-white">
                <Plus className="w-3 h-3" />
              </div>
              <span>Add a second product or service</span>
            </button>
          ) : (
            <div className="space-y-8 pt-6 border-t border-zinc-800 animate-in fade-in slide-in-from-top-4 duration-500">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-zinc-300 uppercase tracking-wider">Second Product or Service</h2>
                <button 
                  onClick={() => { setShowSecondary(false); setSecondary({ name: "", description: "" }); }}
                  className="flex items-center gap-1.5 text-[10px] uppercase tracking-widest text-zinc-500 hover:text-red-400 transition-colors"
                >
                  <Minus className="w-3 h-3" />
                  Remove
                </button>
              </div>

              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Name it</label>
                  <input
                    className="w-full bg-[#262626] border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#f59e0b] transition-colors"
                    placeholder="e.g. Consulting for retail efficiency"
                    value={secondary.name}
                    onChange={(e) => setSecondary({ ...secondary, name: e.target.value })}
                  />
                </div>

                <div className="space-y-2 relative">
                  <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">What does it do?</label>
                  <textarea
                    rows={4}
                    maxLength={300}
                    className="w-full bg-[#262626] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] resize-y"
                    value={secondary.description}
                    onChange={(e) => setSecondary({ ...secondary, description: e.target.value })}
                  />
                  <div className={cn(
                    "absolute bottom-3 right-3 text-[10px] font-mono",
                    secondary.description.length >= 280 ? "text-red-500" : "text-zinc-500"
                  )}>
                    {secondary.description.length} / 300 characters
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ERROR & CTA */}
        <div className="space-y-4 pt-4">
          {error && (
            <p className="text-center text-sm text-red-400 animate-in fade-in zoom-in-95 duration-200">
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
