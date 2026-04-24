"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Edit2, Loader2, ChevronDown } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

/**
 * Foundation Screen 2: Business Scan Results
 * Polls the backend for scan results and allows user confirmation/correction.
 */
export default function FoundationStep2() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { scanData, setScanData, setSectionData, setStep } = useFoundationStore();

  // 1. Page State
  const [status, setStatus] = useState<"loading" | "loaded" | "error">("loading");
  const [isEditingName, setIsEditingName] = useState(false);
  const [showMultiProduct, setShowMultiProduct] = useState(false);
  
  // Field data
  const [formData, setFormData] = useState({
    businessName: "",
    industry: "",
    description: "",
    offering: "",
    multiProductDetails: "",
    confidence: "Medium" as "High" | "Medium" | "Low",
  });

  // 2. Scan Polling Logic
  useEffect(() => {
    setStep(2);
    
    // If we already have scan data in store, use it immediately
    if (scanData) {
      setFormData({
        businessName: scanData.business_name || "",
        industry: scanData.industry || "",
        description: scanData.description || "",
        offering: scanData.primary_offering || "",
        multiProductDetails: "",
        confidence: scanData.confidence || "Medium",
      });
      setStatus("loaded");
      return;
    }

    let pollCount = 0;
    const maxPolls = 15; // 30 seconds (15 * 2s)

    const poll = async () => {
      try {
        const token = await getToken();
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/scan/status`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) throw new Error("Status check failed");

        const result = await response.json();

        if (result.status === "complete" && result.data) {
          const extracted = result.data;
          setScanData(extracted);
          setFormData({
            businessName: extracted.business_name || "",
            industry: extracted.industry || "",
            description: extracted.description || "",
            offering: extracted.primary_offering || "",
            multiProductDetails: "",
            confidence: extracted.confidence || "Medium",
          });
          setStatus("loaded");
          clearInterval(pollInterval);
        } else if (result.status === "failed") {
          setStatus("error");
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error("[Foundation2] Polling Error:", err);
      }

      pollCount++;
      if (pollCount >= maxPolls && status === "loading") {
        setStatus("error");
        clearInterval(pollInterval);
      }
    };

    const pollInterval = setInterval(poll, 2000);
    poll(); // Initial poll

    return () => clearInterval(pollInterval);
  }, [scanData, setScanData, setStep, getToken, status]);

  /**
   * Submission handler
   */
  const handleContinue = async () => {
    if (!formData.businessName || !formData.industry) return;

    try {
      const token = await getToken();
      
      // Save to Zustand
      setSectionData("scan_results", formData);

      // Save to Backend
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/scan_results`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      router.push("/foundation/3");
    } catch (err) {
      console.error("[Foundation2] Save Error:", err);
    }
  };

  // ─── RENDER HELPERS ───

  const industries = [
    "D2C / E-commerce", "SaaS / Technology", "Professional Services", "Food & Beverage", 
    "Healthcare & Wellness", "Education & Training", "Real Estate", "Manufacturing", 
    "Retail (Offline)", "Financial Services", "Media & Content", "Events & Hospitality", 
    "Logistics & Supply Chain", "Agriculture & Agritech", "Other"
  ];

  const SkeletonCard = () => (
    <div className="w-full bg-[#262626] border border-zinc-800 rounded-2xl p-6 space-y-8 animate-pulse">
      {[1, 2, 3, 4].map(i => (
        <div key={i} className="space-y-2">
          <div className="h-2 w-20 bg-zinc-700 rounded" />
          <div className="h-8 w-full bg-zinc-800 rounded" />
        </div>
      ))}
    </div>
  );

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[640px] space-y-8">
        
        {/* HEADER */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-white">Here is what we found.</h1>
          <p className="text-zinc-400">
            {status === "error" 
              ? "We couldn't extract data automatically. Fill in what you can — you can always update this later."
              : "We scanned your website. Tell us what's right and what's not."}
          </p>
        </div>

        {/* MAIN CARD STACK */}
        {status === "loading" ? (
          <div className="space-y-4">
            <SkeletonCard />
            <p className="text-center text-sm text-zinc-400">Still scanning your website...</p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="relative w-full bg-[#262626] border border-zinc-700 rounded-2xl p-6 space-y-8 shadow-2xl">
              
              {/* CONFIDENCE BADGE */}
              {status === "loaded" && (
                <div className={cn(
                  "absolute top-6 right-6 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border",
                  formData.confidence === "High" ? "bg-green-500/10 border-green-500 text-green-500" :
                  formData.confidence === "Medium" ? "bg-amber-500/10 border-amber-500 text-amber-500" :
                  "bg-zinc-500/10 border-zinc-500 text-zinc-500"
                )}>
                  Scan confidence: {formData.confidence}
                </div>
              )}

              {/* FIELD 1: BUSINESS NAME */}
              <div className="space-y-1">
                <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Business Name</label>
                <div className="flex items-center gap-2 group min-h-[40px]">
                  {isEditingName ? (
                    <input
                      autoFocus
                      className="w-full bg-transparent border-b border-zinc-600 py-1 text-xl text-white focus:outline-none focus:border-[#f59e0b]"
                      value={formData.businessName}
                      onChange={(e) => setFormData({...formData, businessName: e.target.value})}
                      onBlur={() => setIsEditingName(false)}
                      onKeyDown={(e) => e.key === "Enter" && setIsEditingName(false)}
                    />
                  ) : (
                    <div 
                      onClick={() => setIsEditingName(true)}
                      className="flex items-center gap-3 cursor-pointer"
                    >
                      <h2 className="text-2xl font-bold text-white leading-tight">
                        {formData.businessName || "Click to add name"}
                      </h2>
                      <Edit2 className="w-4 h-4 text-zinc-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  )}
                </div>
              </div>

              {/* FIELD 2: INDUSTRY */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Industry</label>
                <div className="relative">
                  <select
                    className="w-full bg-[#1a1a1a] border border-zinc-700 rounded-lg px-4 py-3 text-white appearance-none focus:outline-none focus:border-[#f59e0b] focus:ring-1 focus:ring-[#f59e0b]"
                    value={formData.industry}
                    onChange={(e) => setFormData({...formData, industry: e.target.value})}
                  >
                    <option value="" disabled>Select an industry</option>
                    {industries.map(ind => <option key={ind} value={ind}>{ind}</option>)}
                  </select>
                  <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none" />
                </div>
              </div>

              {/* FIELD 3: DESCRIPTION */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">What you do</label>
                <textarea
                  rows={2}
                  className="w-full bg-[#1a1a1a] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] resize-y"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="One sentence about your business"
                />
              </div>

              {/* FIELD 4: PRIMARY OFFERING */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Primary product or service</label>
                <input
                  type="text"
                  className="w-full bg-[#1a1a1a] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b]"
                  value={formData.offering}
                  onChange={(e) => setFormData({...formData, offering: e.target.value})}
                  placeholder="Main thing you sell"
                />
              </div>

            </div>

            {/* MULTI PRODUCT OPTION */}
            <div className="space-y-4">
              <button 
                onClick={() => setShowMultiProduct(!showMultiProduct)}
                className="text-sm text-zinc-400 hover:text-white transition-colors"
              >
                {showMultiProduct ? "Hide additional areas ↑" : "This business sells multiple things →"}
              </button>
              
              {showMultiProduct && (
                <div className="p-6 bg-[#262626] border border-zinc-700 rounded-2xl space-y-2">
                  <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Tell us about your other product or service areas</label>
                  <textarea
                    rows={2}
                    className="w-full bg-[#1a1a1a] border border-zinc-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#f59e0b]"
                    value={formData.multiProductDetails}
                    onChange={(e) => setFormData({...formData, multiProductDetails: e.target.value})}
                  />
                </div>
              )}
            </div>

            {/* CTA BLOCK */}
            <div className="space-y-4 pt-4">
              <button
                onClick={handleContinue}
                disabled={!formData.businessName || !formData.industry}
                className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-700 disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
              >
                This looks right — continue
              </button>
              
              <div className="flex justify-center">
                <button 
                  onClick={() => router.push("/foundation/1")}
                  className="text-sm text-zinc-500 hover:text-white transition-colors"
                >
                  ← Go back
                </button>
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
