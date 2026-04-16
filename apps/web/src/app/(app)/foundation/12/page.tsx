"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { X, Plus, AlertCircle } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

interface KeywordEntry {
  text: string;
  competition: "high" | "medium" | "low";
  userAdded: boolean;
}

/**
 * Foundation Screen 12: Keywords and Search Presence
 * Defines the search intent landscape for the brand.
 */
export default function FoundationStep12() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [keywords, setKeywords] = useState<KeywordEntry[]>([]);
  const [newKeyword, setNewKeyword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(12);
    
    // Initial data hydration
    const existing = sectionData.keywords;
    if (existing?.keywords) {
      setKeywords(existing.keywords);
    } else {
      // Pre-populate with scan data or mock
      const suggestions = sectionData.scan_results?.keyword_suggestions || [
        "best logistics software india", "inventory management for retail",
        "supply chain visibility tools", "warehouse automation system",
        "ecommerce shipping api", "real-time stock tracking",
        "kirana store inventory app", "last mile delivery software"
      ];

      const initial = suggestions.map((text: string, i: number) => ({
        text,
        competition: i % 3 === 0 ? "high" : i % 3 === 1 ? "medium" : "low",
        userAdded: false
      }));
      setKeywords(initial);
    }
  }, [setStep, sectionData]);

  const addKeyword = () => {
    const trimmed = newKeyword.trim().toLowerCase();
    if (!trimmed || keywords.some(k => k.text.toLowerCase() === trimmed)) return;
    
    setKeywords(prev => [...prev, { text: trimmed, competition: "medium", userAdded: true }]);
    setNewKeyword("");
  };

  const removeKeyword = (text: string) => {
    setKeywords(prev => prev.filter(k => k.text !== text));
  };

  const hasHighComp = keywords.some(k => k.competition === "high");

  const handleContinue = async () => {
    if (keywords.length < 3) return;

    setIsSubmitting(true);
    const data = { keywords };

    try {
      const token = await getToken();
      setSectionData("keywords", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/keywords`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/13");
    } catch (err) {
      console.error("[Foundation12] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[600px] space-y-10">
        
        {/* HEADER */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-white leading-tight">
            What should you show up for?
          </h1>
          <p className="text-base text-zinc-400">
            The searches your ideal customer is doing right now.
          </p>
        </div>

        {/* KEYWORD CHIP GRID */}
        <div className="space-y-6">
          <div className="flex flex-wrap gap-x-2 gap-y-4">
            {keywords.map((kw) => (
              <div key={kw.text} className="flex items-center gap-2 animate-in fade-in zoom-in-95 duration-200">
                <div className={cn(
                  "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm transition-all shadow-sm",
                  kw.competition === "high" ? "border-red-900 bg-red-950/30 text-red-300" :
                  kw.competition === "medium" ? "border-amber-900 bg-amber-950/30 text-amber-300" :
                  "border-green-900 bg-green-950/30 text-green-300"
                )}>
                  <span>{kw.text}</span>
                  <button 
                    onClick={() => removeKeyword(kw.text)}
                    className="p-0.5 hover:bg-white/10 rounded-full transition-colors"
                  >
                    <X className="w-3 h-3 text-zinc-500 hover:text-white" />
                  </button>
                </div>
                {kw.competition === "high" && (
                  <span className="text-[10px] font-bold uppercase tracking-widest text-red-500 whitespace-nowrap">
                    ↑↑ High competition
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* HIGH COMPETITION NOTE */}
          {hasHighComp && (
            <div className="p-4 bg-red-950/10 border border-red-900/20 rounded-xl space-y-1">
              <p className="text-xs text-zinc-400 leading-relaxed">
                <span className="text-red-400 font-bold inline-flex items-center gap-1.5 mr-1 uppercase tracking-widest">
                  <AlertCircle className="w-3 h-3" /> Note:
                </span>
                Very competitive keywords are valuable but take time. Your AI team will suggest lower-competition long-tail variants soon.
              </p>
            </div>
          )}
        </div>

        {/* ADD KEYWORD INPUT */}
        <div className="space-y-4 pt-4 border-t border-zinc-800">
          <div className="flex gap-2">
            <input
              className="flex-1 bg-[#262626] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] transition-colors"
              placeholder="Add a search term..."
              value={newKeyword}
              onKeyDown={(e) => e.key === "Enter" && addKeyword()}
              onChange={(e) => setNewKeyword(e.target.value)}
            />
            <button
              onClick={addKeyword}
              disabled={!newKeyword.trim()}
              className="px-6 bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-800 disabled:text-zinc-600 text-black font-bold rounded-lg transition-all"
            >
              Add
            </button>
          </div>
          <p className="text-[10px] text-zinc-600 uppercase tracking-widest">At least 3 keywords required to build your SEO profile</p>
        </div>

        {/* CTA */}
        <button
          onClick={handleContinue}
          disabled={keywords.length < 3 || isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-700 disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all mt-8"
        >
          {isSubmitting ? "Building Search Profile..." : "Continue"}
        </button>

      </div>
    </div>
  );
}
