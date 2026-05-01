"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { IndianRupee, Check, ChevronDown } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";
import { getApiBaseUrl } from "@/lib/api";

/**
 * Foundation Screen 16: Marketing Budget
 * Sets the financial constraints for AI-driven marketing strategies.
 */
export default function FoundationStep16() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [selectedRange, setSelectedRange] = useState<string | null>(null);
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [breakdown, setBreakdown] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(16);
    const existing = sectionData.budget;
    if (existing) {
      setSelectedRange(existing.budgetRange || null);
      setBreakdown(existing.perChannelBreakdown || {});
      if (Object.keys(existing.perChannelBreakdown || {}).length > 0) {
        setShowBreakdown(true);
      }
    }
  }, [setStep, sectionData]);

  const ranges = [
    {
      id: "0",
      label: "₹0",
      subtext: "Organic only. Every rupee goes to time and effort, not spend.",
    },
    {
      id: "10k-50k",
      label: "₹10,000 – ₹50,000",
      subtext: "Test one channel with small paid experiments.",
    },
    {
      id: "50k-200k",
      label: "₹50,000 – ₹2,00,000",
      subtext: "Run a focused multi-channel paid campaign.",
    },
    {
      id: "200k-1M",
      label: "₹2,00,000 – ₹10,00,000",
      subtext: "Serious paid scale across 2–3 channels.",
    },
    {
      id: "1M+",
      label: "₹10,00,000+",
      subtext: "Full-funnel execution with significant channel presence.",
    },
  ];

  const selectedChannels = sectionData.content_channels?.channels || [];

  const handleBreakdownChange = (channelName: string, value: string) => {
    setBreakdown((prev) => ({ ...prev, [channelName]: value }));
  };

  const totalAllocated = Object.values(breakdown).reduce((acc, val) => acc + (Number(val) || 0), 0);

  const formatINR = (val: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(val);
  };

  const handleContinue = async () => {
    if (!selectedRange) return;

    setIsSubmitting(true);
    const data = {
      budgetRange: selectedRange,
      perChannelBreakdown: breakdown,
    };

    try {
      const token = await getToken();
      setSectionData("budget", data);

      await fetch(`${getApiBaseUrl()}/api/v1/foundation/section/budget`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/17");
    } catch (err) {
      console.error("[Foundation16] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[560px] space-y-10">
        {/* HEADER */}
        <div className="space-y-4">
          <div className="space-y-2 text-center">
            <h1 className="text-3xl font-bold text-[#2A2622]">
              What&apos;s your marketing budget for the next 90 days?
            </h1>
            <p className="text-base text-[#6B655E]">
              This is for ads, content production, and tools — not for RaptorFlow.
            </p>
          </div>
          <p className="text-sm text-[#6B655E] italic text-center">
            Your AI team will only recommend tactics that fit this budget.
          </p>
        </div>

        {/* BUDGET CARDS */}
        <div className="flex flex-col gap-3">
          {ranges.map((range) => {
            const isSelected = selectedRange === range.id;
            return (
              <div
                key={range.id}
                onClick={() => setSelectedRange(range.id)}
                className={cn(
                  "relative p-5 rounded-xl border flex items-center gap-4 transition-all duration-300 cursor-pointer overflow-hidden",
                  isSelected
                    ? "border-[#f59e0b] bg-[#f59e0b]/10 shadow-[0_0_20px_rgba(217,119,87,0.1)]"
                    : "bg-[#262626] border-[#D5CBC0] hover:border-[#D5CBC0]",
                )}
              >
                {isSelected && (
                  <div className="absolute top-4 right-4 bg-[#f59e0b] rounded-full p-1">
                    <Check className="w-3 h-3 text-black" />
                  </div>
                )}

                <div
                  className={cn(
                    "p-3 rounded-full border transition-colors",
                    isSelected
                      ? "bg-[#f59e0b]/20 border-[#f59e0b]/30 text-[#f59e0b]"
                      : "bg-[#E5DED4] border-[#D5CBC0] text-[#6B655E]",
                  )}
                >
                  <IndianRupee className="w-5 h-5" />
                </div>

                <div className="space-y-0.5">
                  <h3
                    className={cn(
                      "text-lg font-bold tracking-tight",
                      isSelected ? "text-[#2A2622]" : "text-[#9A948C]",
                    )}
                  >
                    {range.label}
                  </h3>
                  <p className="text-xs text-[#6B655E] leading-relaxed">{range.subtext}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* BREAKDOWN TOGGLE */}
        {selectedRange && selectedChannels.length > 0 && (
          <div className="space-y-6 pt-4">
            <button
              onClick={() => setShowBreakdown(!showBreakdown)}
              className="flex items-center gap-2 text-sm text-[#6B655E] hover:text-[#2A2622] transition-colors mx-auto"
            >
              <span>Want to break this down by channel? (optional)</span>
            </button>

            <div
              className={cn(
                "overflow-hidden transition-all duration-500",
                showBreakdown ? "max-h-[600px] opacity-100" : "max-h-0 opacity-0",
              )}
            >
              <div className="bg-[#FBF8F2] border border-[#E5DED4] rounded-2xl p-6 space-y-6 shadow-2xl">
                <div className="space-y-4">
                  {selectedChannels.map((c: any) => (
                    <div key={c.name} className="flex items-center justify-between gap-4">
                      <span className="text-sm font-medium text-[#9A948C]">{c.name}</span>
                      <div className="relative w-40">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9A948C] text-xs font-mono">
                          ₹
                        </span>
                        <input
                          type="number"
                          className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg pl-6 pr-3 py-2 text-sm text-[#2A2622] focus:outline-none focus:border-[#f59e0b]"
                          placeholder="0"
                          value={breakdown[c.name] || ""}
                          onChange={(e) => handleBreakdownChange(c.name, e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-4 border-t border-[#E5DED4] flex justify-between items-center">
                  <span className="text-xs font-bold uppercase tracking-widest text-[#6B655E]">
                    Total Allocated:
                  </span>
                  <span className="text-lg font-bold text-[#f59e0b]">
                    {formatINR(totalAllocated)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* CTA */}
        <button
          onClick={handleContinue}
          disabled={!selectedRange || isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all mt-8 shadow-[0_5px_15px_rgba(0,0,0,0.3)]"
        >
          {isSubmitting ? "Allocating Resources..." : "Continue"}
        </button>
      </div>
    </div>
  );
}
