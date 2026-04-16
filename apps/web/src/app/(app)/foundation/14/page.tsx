"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { 
  Video, 
  FileText, 
  Mail, 
  TrendingUp, 
  Users, 
  Share2, 
  Monitor, 
  Mic, 
  Package,
  Check
} from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

/**
 * Foundation Screen 14: Content History
 * Historical assessment of marketing efforts to avoid duplication.
 */
export default function FoundationStep14() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [details, setDetails] = useState<Record<string, { worked: string; didntWork: string }>>({});
  const [combinedSummary, setCombinedSummary] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(14);
    const existing = sectionData.content_history;
    if (existing) {
      setSelectedTypes(existing.triedTypes || []);
      setDetails(existing.detailsByType || {});
      setCombinedSummary(existing.combinedSummary || "");
    }
  }, [setStep, sectionData]);

  const CONTENT_TYPES = [
    { id: "video",      label: "Short-form video",   desc: "Reels, Shorts, TikTok",  icon: Video },
    { id: "blog",       label: "Articles or blogs",  desc: "Long-form written",    icon: FileText },
    { id: "email",      label: "Email newsletters",  desc: "Direct-to-inbox",        icon: Mail },
    { id: "ads",        label: "Paid ads",           desc: "Google, Meta",           icon: TrendingUp },
    { id: "influencer", label: "Influencer",         desc: "Partnerships",           icon: Users },
    { id: "social",     label: "Organic social",     desc: "Standard posts",         icon: Share2 },
    { id: "events",     label: "Webinars/Events",     desc: "Live engagement",        icon: Monitor },
    { id: "podcast",    label: "Podcast",            desc: "Audio content",          icon: Mic },
    { id: "none",       label: "None yet",           desc: "Starting from scratch",  icon: Package },
  ];

  const toggleType = (id: string) => {
    setSelectedTypes((prev) => {
      if (id === "none") return ["none"];
      const next = prev.includes(id) ? prev.filter((t) => t !== id) : [...prev.filter((t) => t !== "none"), id];
      return next;
    });
  };

  const updateDetail = (id: string, field: "worked" | "didntWork", val: string) => {
    setDetails((prev) => ({
      ...prev,
      [id]: { ...prev[id], [field]: val },
    }));
  };

  const handleContinue = async () => {
    setIsSubmitting(true);
    const data = {
      triedTypes: selectedTypes,
      detailsByType: details,
      combinedSummary: selectedTypes.length > 3 ? combinedSummary : null,
    };

    try {
      const token = await getToken();
      setSectionData("content_history", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/content_history`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/15");
    } catch (err) {
      console.error("[Foundation14] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const realSelected = selectedTypes.filter((t) => t !== "none");

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[600px] space-y-12">
        
        {/* HEADER */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-white leading-tight">
            What have you already tried?
          </h1>
          <p className="text-base text-zinc-400">
            This stops your AI team from recommending things that haven&apos;t worked.
          </p>
        </div>

        {/* CONTENT TYPE GRID */}
        <div className="grid grid-cols-2 gap-3">
          {CONTENT_TYPES.map((type) => {
            const isSelected = selectedTypes.includes(type.id);
            return (
              <div
                key={type.id}
                onClick={() => toggleType(type.id)}
                className={cn(
                  "relative p-4 rounded-xl cursor-pointer border transition-all duration-200",
                  isSelected 
                    ? "border-[#f59e0b] bg-[#f59e0b]/10 shadow-[0_0_15px_rgba(245,158,11,0.1)]" 
                    : "bg-[#262626] border-zinc-700 hover:border-zinc-500"
                )}
              >
                {isSelected && (
                  <div className="absolute top-3 right-3 shrink-0">
                    <Check className="w-4 h-4 text-[#f59e0b]" />
                  </div>
                )}
                <div className="flex flex-col gap-2">
                  <type.icon className={cn("w-5 h-5", isSelected ? "text-[#f59e0b]" : "text-zinc-500")} />
                  <div className="space-y-0.5">
                    <p className="text-sm font-bold text-white leading-tight">{type.label}</p>
                    <p className="text-[11px] text-zinc-400 leading-tight">{type.desc}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* CONDITIONAL EXPANSION */}
        <div className="space-y-10 animate-in fade-in slide-in-from-top-4 duration-500">
          {realSelected.length > 0 && realSelected.length <= 3 && (
            <div className="space-y-10">
              {realSelected.map((typeId) => {
                const label = CONTENT_TYPES.find((t) => t.id === typeId)?.label;
                const fieldData = details[typeId] || { worked: "", didntWork: "" };
                return (
                  <div key={typeId} className="space-y-6">
                    <div className="flex items-center gap-4">
                      <div className="h-[1px] flex-1 bg-zinc-800" />
                      <span className="text-[10px] uppercase font-bold tracking-widest text-[#f59e0b]/60">{label} History</span>
                      <div className="h-[1px] flex-1 bg-zinc-800" />
                    </div>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">What worked?</label>
                        <textarea
                          rows={2}
                          className="w-full bg-[#262626] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] transition-colors resize-none"
                          placeholder="What got results, even small ones?"
                          value={fieldData.worked}
                          onChange={(e) => updateDetail(typeId, "worked", e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">What didn&apos;t?</label>
                        <textarea
                          rows={2}
                          className="w-full bg-[#262626] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] transition-colors resize-none"
                          placeholder="What flopped, or what you stopped doing and why?"
                          value={fieldData.didntWork}
                          onChange={(e) => updateDetail(typeId, "didntWork", e.target.value)}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {realSelected.length > 3 && (
            <div className="space-y-4 p-5 bg-[#262626]/50 border border-zinc-800 rounded-xl">
              <label className="text-sm font-bold text-zinc-300">You&apos;ve tried a lot. Give us the highlights — what worked, what didn&apos;t?</label>
              <textarea
                rows={5}
                className="w-full bg-[#1a1a1a] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] transition-colors resize-y"
                placeholder="Summarise your learnings across these channels..."
                value={combinedSummary}
                onChange={(e) => setCombinedSummary(e.target.value)}
              />
            </div>
          )}
        </div>

        {/* CTA */}
        <button
          onClick={handleContinue}
          disabled={isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-700 disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
        >
          {isSubmitting ? "Updating Market Memory..." : "Continue"}
        </button>

      </div>
    </div>
  );
}
