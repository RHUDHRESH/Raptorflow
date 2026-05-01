"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Info, Check } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";
import { getApiBaseUrl } from "@/lib/api";

interface ToolUsage {
  id: string;
  name: string;
  usageFrequency: string;
}

/**
 * Foundation Screen 19: Analytics and Tracking
 * Assesses the user's current data maturity and dashboard habits.
 */
export default function FoundationStep19() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [selectedToolIds, setSelectedToolIds] = useState<string[]>([]);
  const [usageMap, setUsageMap] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(19);
    const existing = sectionData.analytics_tracking;
    if (existing?.tools) {
      setSelectedToolIds(existing.tools.map((t: any) => t.id));
      const map: Record<string, string> = {};
      existing.tools.forEach((t: any) => {
        map[t.id] = t.usageFrequency;
      });
      setUsageMap(map);
    }
  }, [setStep, sectionData]);

  const TOOLS = [
    { id: "ga", name: "Google Analytics", icon: "📊", desc: "Website traffic and conversions" },
    {
      id: "meta",
      name: "Meta Business Suite",
      icon: "📱",
      desc: "Facebook and Instagram analytics",
    },
    { id: "gsc", name: "Google Search Console", icon: "🔍", desc: "Search presence and keywords" },
    { id: "hotjar", name: "Hotjar or similar", icon: "🔥", desc: "Heatmaps and recordings" },
    { id: "none", name: "None of these", icon: "❌", desc: "Not tracking anything yet" },
  ];

  const FREQUENCIES = ["Yes, weekly", "Sometimes", "I have access but rarely use it"];

  const toggleTool = (id: string) => {
    setSelectedToolIds((prev) => {
      if (id === "none") return ["none"];
      const filtered = prev.filter((t) => t !== "none");
      return filtered.includes(id) ? filtered.filter((t) => t !== id) : [...filtered, id];
    });
  };

  const handleFrequencySelect = (toolId: string, freq: string) => {
    setUsageMap((prev) => ({ ...prev, [toolId]: freq }));
  };

  const handleContinue = async () => {
    setIsSubmitting(true);
    const data = {
      tools: selectedToolIds.map((id) => ({
        id,
        name: TOOLS.find((t) => t.id === id)?.name || "",
        usageFrequency: usageMap[id] || "Sometimes",
      })),
    };

    try {
      const token = await getToken();
      setSectionData("analytics_tracking", data);

      await fetch(`${getApiBaseUrl()}/api/v1/foundation/section/analytics_tracking`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/20");
    } catch (err) {
      console.error("[Foundation19] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const activeTools = TOOLS.filter((t) => selectedToolIds.includes(t.id) && t.id !== "none");

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[560px] space-y-10">
        {/* HEADER */}
        <h1 className="text-3xl font-bold text-[#2A2622] text-center sm:text-left">
          What are you already tracking?
        </h1>

        {/* TOOL SELECTOR GRID */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {TOOLS.map((tool) => {
            const isSelected = selectedToolIds.includes(tool.id);
            return (
              <div
                key={tool.id}
                onClick={() => toggleTool(tool.id)}
                className={cn(
                  "group relative p-4 rounded-xl border flex flex-col gap-2 transition-all duration-300 cursor-pointer",
                  isSelected
                    ? "border-[#f59e0b] bg-[#f59e0b]/10"
                    : "bg-[#262626] border-[#D5CBC0] hover:border-[#D5CBC0]",
                )}
              >
                {isSelected && (
                  <div className="absolute top-3 right-3 shrink-0">
                    <Check className="w-4 h-4 text-[#f59e0b]" />
                  </div>
                )}
                <span className="text-2xl">{tool.icon}</span>
                <div className="space-y-0.5">
                  <p className="text-sm font-bold text-[#2A2622] leading-tight">{tool.name}</p>
                  <p className="text-[11px] text-[#6B655E] leading-tight">{tool.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* USAGE FREQUENCY (CONDITIONAL EXPANSION) */}
        {activeTools.length > 0 && (
          <div className="space-y-8 animate-in fade-in slide-in-from-top-4 duration-500">
            {activeTools.map((tool) => (
              <div key={tool.id} className="space-y-4">
                <p className="text-sm font-medium text-[#9A948C]">
                  Are you actually looking at{" "}
                  <span className="text-[#2A2622] font-bold">{tool.name}</span> regularly?
                </p>
                <div className="flex flex-wrap gap-2">
                  {FREQUENCIES.map((freq) => {
                    const isSelected = usageMap[tool.id] === freq;
                    return (
                      <button
                        key={freq}
                        onClick={() => handleFrequencySelect(tool.id, freq)}
                        className={cn(
                          "px-4 py-2 rounded-full border text-[11px] font-bold uppercase tracking-wider transition-all",
                          isSelected
                            ? "border-[#f59e0b] bg-[#f59e0b]/10 text-[#2A2622]"
                            : "border-[#D5CBC0] bg-transparent text-[#6B655E] hover:border-[#D5CBC0]",
                        )}
                      >
                        {freq}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* RAPTORFLOW NOTE PANEL */}
        <div className="bg-[#FBF8F2] border border-[#E5DED4] rounded-xl p-5 space-y-3 shadow-xl">
          <div className="flex items-center gap-2 text-[#f59e0b]">
            <Info className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-widest">RaptorFlow Engine</span>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-[#9A948C] leading-relaxed font-medium">
              RaptorFlow will track what matters for your campaigns and surface it in Daily Wins —
              so you don&apos;t need to check dashboards separately.
            </p>
            <p className="text-xs text-[#6B655E] italic">
              We don&apos;t replace these tools. We filter the signal from the noise.
            </p>
          </div>
        </div>

        {/* CTA */}
        <button
          onClick={handleContinue}
          disabled={isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all shadow-xl mt-4"
        >
          {isSubmitting ? "Finalizing Stack..." : "Continue"}
        </button>
      </div>
    </div>
  );
}
