"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Star, ChevronDown } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

interface ChannelConfig {
  name: string;
  icon: string;
  status: string;
  selected: boolean;
  isPriority: boolean;
}

/**
 * Foundation Screen 13: Content Channels
 * Maps where the brand will exist and defines priorities.
 */
export default function FoundationStep13() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [channels, setChannels] = useState<ChannelConfig[]>([
    { name: "Instagram", icon: "📸", status: "Not started", selected: false, isPriority: false },
    { name: "LinkedIn", icon: "💼", status: "Not started", selected: false, isPriority: false },
    { name: "Facebook", icon: "👍", status: "Not started", selected: false, isPriority: false },
    { name: "Twitter / X", icon: "🐦", status: "Not started", selected: false, isPriority: false },
    { name: "YouTube", icon: "📹", status: "Not started", selected: false, isPriority: false },
    { name: "WhatsApp", icon: "💬", status: "Not started", selected: false, isPriority: false },
    { name: "Google Ads", icon: "🔍", status: "Not started", selected: false, isPriority: false },
    { name: "Meta Ads", icon: "📱", status: "Not started", selected: false, isPriority: false },
    { name: "Email", icon: "📧", status: "Not started", selected: false, isPriority: false },
    { name: "Blog", icon: "📝", status: "Not started", selected: false, isPriority: false },
    { name: "Other", icon: "⚙️", status: "Not started", selected: false, isPriority: false }
  ]);

  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(13);
    const existing = sectionData.content_channels;
    if (existing?.channels) {
      setChannels(prev => prev.map(c => {
        const ext = existing.channels.find((e: any) => e.name === c.name);
        return ext ? { ...c, ...ext, selected: true } : c;
      }));
    }
  }, [setStep, sectionData]);

  const toggleSelection = (name: string) => {
    setChannels(prev => prev.map(c => {
      if (c.name === name) {
        return { ...c, selected: !c.selected, isPriority: false };
      }
      return c;
    }));
    setError(null);
  };

  const updateStatus = (name: string, status: string) => {
    setChannels(prev => prev.map(c => c.name === name ? { ...c, status } : c));
  };

  const togglePriority = (name: string) => {
    const priorityCount = channels.filter(c => c.isPriority).length;
    const isCurrentlyPriority = channels.find(c => c.name === name)?.isPriority;

    if (!isCurrentlyPriority && priorityCount >= 2) {
      setError("Maximum 2 priority channels allowed.");
      return;
    }

    setChannels(prev => prev.map(c => c.name === name ? { ...c, isPriority: !c.isPriority } : c));
    setError(null);
  };

  const selectedCount = channels.filter(c => c.selected).length;
  const priorityCount = channels.filter(c => c.isPriority).length;

  const handleContinue = async () => {
    if (selectedCount === 0) return;
    if (priorityCount === 0) {
      setError("Please select at least 1 priority channel.");
      return;
    }

    setIsSubmitting(true);
    const data = {
      channels: channels.filter(c => c.selected).map(c => ({
        name: c.name,
        status: c.status,
        isPriority: c.isPriority
      }))
    };

    try {
      const token = await getToken();
      setSectionData("content_channels", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/content_channels`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/14");
    } catch (err) {
      console.error("[Foundation13] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[640px] space-y-12">
        
        {/* HEADER */}
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold text-[#2A2622]">Where do you want to show up?</h1>
          <p className="text-base text-[#6B655E]">Select every channel that matters to your business.</p>
        </div>

        {/* CHANNEL GRID */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {channels.map((c) => (
            <div
              key={c.name}
              onClick={() => !c.selected && toggleSelection(c.name)}
              className={cn(
                "group relative p-4 rounded-xl border flex flex-col gap-3 transition-all duration-300 cursor-pointer overflow-hidden",
                c.selected ? "border-[#f59e0b] bg-[#f59e0b]/10" : "bg-[#262626] border-[#D5CBC0] hover:border-[#D5CBC0]"
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{c.icon}</span>
                  <span className="text-sm font-medium text-[#2A2622]">{c.name}</span>
                </div>
                {c.selected && (
                  <button 
                    onClick={(e) => { e.stopPropagation(); toggleSelection(c.name); }}
                    className="p-1 text-[#6B655E] hover:text-[#2A2622]"
                  >
                    <Star className={cn("w-3 h-3 transition-colors", c.isPriority ? "fill-[#f59e0b] text-[#f59e0b]" : "")} />
                  </button>
                )}
              </div>

              {/* Status Dropdown */}
              <div className={cn(
                "space-y-1 overflow-hidden transition-all duration-500",
                c.selected ? "max-h-[100px] opacity-100" : "max-h-0 opacity-0"
              )}>
                <label className="text-[10px] uppercase font-bold tracking-widest text-[#f59e0b]/70">You are currently:</label>
                <div className="relative">
                  <select
                    className="w-full bg-black/40 border border-[#f59e0b]/20 rounded-lg px-3 py-1.5 text-[11px] text-[#2A2622] appearance-none focus:outline-none focus:border-[#f59e0b]/50"
                    value={c.status}
                    onChange={(e) => updateStatus(c.name, e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {["Not started", "Just getting going", "Active but inconsistent", "Consistent and performing"].map(opt => (
                      <option key={opt} value={opt} className="bg-[#F5F0E8]">{opt}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-[#6B655E] pointer-events-none" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* PRIORITY RANKING */}
        {selectedCount > 0 && (
          <div className="space-y-6 pt-6 border-t border-[#E5DED4] animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="space-y-1 text-center">
              <h2 className="text-base font-medium text-[#2A2622]">Which 2 channels should we prioritise first?</h2>
              <p className="text-sm text-[#6B655E]">Your AI team will focus their energy here.</p>
            </div>
            
            <div className="flex flex-wrap justify-center gap-2">
              {channels.filter(c => c.selected).map(c => (
                <button
                  key={c.name}
                  onClick={() => togglePriority(c.name)}
                  className={cn(
                    "inline-flex items-center gap-2 px-4 py-2 rounded-full border text-[11px] font-bold uppercase tracking-wider transition-all duration-300",
                    c.isPriority
                      ? "border-[#f59e0b] bg-[#f59e0b]/10 text-[#2A2622] shadow-[0_0_15px_rgba(217,119,87,0.1)]"
                      : "border-[#D5CBC0] bg-transparent text-[#6B655E] hover:border-[#D5CBC0]"
                  )}
                >
                  {c.isPriority && <Star className="w-3 h-3 fill-[#f59e0b] text-[#f59e0b]" />}
                  {c.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <div className="space-y-4 pt-4">
          {error && <p className="text-center text-sm text-red-500 animate-in fade-in duration-200">{error}</p>}
          <button
            onClick={handleContinue}
            disabled={selectedCount === 0 || isSubmitting}
            className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
          >
            {isSubmitting ? "Generating Strategy Assets..." : "Continue"}
          </button>
        </div>

      </div>
    </div>
  );
}
