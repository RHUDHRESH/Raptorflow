"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Sparkles, Loader2, ArrowLeft, ArrowRight } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

/**
 * Auto-expanding inline input component
 */
function AutoWidthInput({ 
  value, 
  onChange, 
  placeholder, 
  minWidth = 120 
}: { 
  value: string; 
  onChange: (v: string) => void; 
  placeholder: string;
  minWidth?: number;
}) {
  const spanRef = useRef<HTMLSpanElement>(null);
  const [width, setWidth] = useState(minWidth);

  useEffect(() => {
    if (spanRef.current) {
      const extraPadding = 8;
      setWidth(Math.max(spanRef.current.offsetWidth + extraPadding, minWidth));
    }
  }, [value, minWidth]);

  return (
    <div className="inline-block relative">
      <span 
        ref={spanRef} 
        className="invisible absolute whitespace-pre text-xl font-medium px-1"
      >
        {value || placeholder}
      </span>
      <input
        className="bg-transparent border-b-2 border-[#f59e0b] text-[#2A2622] text-xl px-1 py-0 outline-none transition-all placeholder:text-[#9A948C] focus:border-white"
        style={{ width: `${width}px` }}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

/**
 * Foundation Screen 10: Positioning Statement
 * The "X for Y" core strategy.
 */
export default function FoundationStep10() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [mode, setMode] = useState<"builder" | "manual">("builder");
  const [slots, setSlots] = useState({
    icp: "",
    businessName: "",
    category: "",
    differentiator: "",
    proof: "",
  });
  const [manualText, setManualText] = useState("");
  const [isHelping, setIsHelping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setStep(10);
    
    // Initial Hydration
    const existing = sectionData.positioning;
    if (existing) {
      if (existing.slots) setSlots(existing.slots);
      if (existing.manualText) setManualText(existing.manualText);
      setMode(existing.mode || "builder");
    } else {
      // Pre-fill from store
      const icpName = sectionData.icp?.primaryICP?.name || "";
      const bizName = sectionData.scan_results?.businessName || "";
      setSlots(prev => ({ ...prev, icp: icpName, businessName: bizName }));
    }
  }, [setStep, sectionData]);

  const assembledStatement = `For ${slots.icp || "[ICP]"}, ${slots.businessName || "[Business Name]"} is the ${slots.category || "[category]"} that ${slots.differentiator || "[differentiator]"} because ${slots.proof || "[proof]"}.`;

  const handleHelp = () => {
    setIsHelping(true);
    setTimeout(() => {
      setIsHelping(false);
      setShowSuggestions(true);
    }, 1500);
  };

  const useSuggestion = (suggestedSlots: typeof slots) => {
    setSlots(suggestedSlots);
    setMode("builder");
    setShowSuggestions(false);
  };

  const validate = () => {
    if (mode === "builder") {
      const allFilled = Object.values(slots).every(v => v.trim().length > 0);
      if (!allFilled) {
        setError("Please fill in all blanks to complete your positioning statement.");
        return false;
      }
    } else {
      if (manualText.trim().length < 40) {
        setError("Your positioning statement needs a bit more detail (at least 40 characters).");
        return false;
      }
    }
    return true;
  };

  const handleContinue = async () => {
    if (!validate()) return;

    setIsSubmitting(true);
    const data = {
      mode,
      positioningStatement: mode === "builder" ? assembledStatement : manualText,
      slots: mode === "builder" ? slots : null,
      manualText: mode === "manual" ? manualText : null,
    };

    try {
      const token = await getToken();
      setSectionData("positioning", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/positioning`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/11");
    } catch (err) {
      console.error("[Foundation10] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[640px] space-y-10">
        
        {/* HEADER */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-[#2A2622] leading-tight">
            How do you want to be known?
          </h1>
          <p className="text-base text-[#6B655E]">
            One sentence. The most important sentence in marketing.
          </p>
        </div>

        {/* BUILDER AREA */}
        {mode === "builder" ? (
          <div className="space-y-12">
            <div className="text-xl leading-[2.2] text-[#9A948C]">
              For <AutoWidthInput value={slots.icp} onChange={(v) => setSlots({...slots, icp: v})} placeholder="[audience]" minWidth={160} />,{" "}
              <AutoWidthInput value={slots.businessName} onChange={(v) => setSlots({...slots, businessName: v})} placeholder="[Business Name]" minWidth={160} />{" "}
              is the <AutoWidthInput value={slots.category} onChange={(v) => setSlots({...slots, category: v})} placeholder="[category]" />{" "}
              that <AutoWidthInput value={slots.differentiator} onChange={(v) => setSlots({...slots, differentiator: v})} placeholder="[uniquity]" minWidth={220} />{" "}
              because <AutoWidthInput value={slots.proof} onChange={(v) => setSlots({...slots, proof: v})} placeholder="[proof]" minWidth={180} />.
            </div>

            {/* PREVIEW PANEL */}
            <div className="bg-[#FBF8F2] p-5 rounded-xl border border-[#E5DED4] space-y-3">
              <label className="text-[10px] uppercase font-bold tracking-widest text-[#6B655E]">Your positioning statement:</label>
              <p className="text-base font-medium text-[#2A2622] italic leading-relaxed">
                &quot;{assembledStatement}&quot;
              </p>
            </div>

            <button
              onClick={() => setMode("manual")}
              className="text-sm text-[#6B655E] hover:text-[#2A2622] transition-colors underline decoration-zinc-800"
            >
              Prefer to write it in your own words →
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <textarea
              autoFocus
              rows={5}
              className="w-full bg-[#262626] border border-[#D5CBC0] rounded-xl px-5 py-4 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-[#f59e0b] resize-y"
              placeholder="For [who], we are the [what] that [how] because [why]."
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
            />
            <button
              onClick={() => setMode("builder")}
              className="text-sm text-[#6B655E] hover:text-[#2A2622] transition-colors"
            >
              Use the builder instead ←
            </button>
          </div>
        )}

        {/* AI SUGGESTIONS SECTION */}
        <div className="space-y-6 pt-4">
          {!showSuggestions ? (
            <button
              disabled={isHelping}
              onClick={handleHelp}
              className="flex items-center gap-2 text-[#f59e0b] hover:opacity-80 transition-opacity disabled:opacity-50 text-sm"
            >
              {isHelping ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
              <span>Show me 3 positioning options</span>
            </button>
          ) : (
            <div className="space-y-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
              {[
                { icp: "Small Business Owners", businessName: slots.businessName, category: "financial guard", differentiator: "automates GST filing in 3 minutes", proof: "we integrate directly with both Tally and bank feeds" },
                { icp: "High-Growth Shopify Stores", businessName: slots.businessName, category: "performance partner", differentiator: "scales your ad spend without increasing CAC", proof: "our AI updates creative every 24 hours based on real sales data" },
                { icp: "Operations Managers", businessName: slots.businessName, category: "visibility tool", differentiator: "predicts stock-outs 14 days in advance", proof: "we process over 1M purchase data points from your vertical baseline" }
              ].map((s, i) => (
                <div key={i} className="p-4 bg-[#262626] border border-[#D5CBC0] rounded-xl flex items-start justify-between gap-4 group">
                  <p className="text-sm text-[#6B655E] leading-relaxed italic">
                    &quot;For {s.icp}, {s.businessName || "RaptorFlow"} is the {s.category} that {s.differentiator} because {s.proof}.&quot;
                  </p>
                  <button 
                    onClick={() => useSuggestion(s as any)}
                    className="shrink-0 text-[10px] font-bold uppercase tracking-widest text-[#f59e0b] hover:underline"
                  >
                    Use this
                  </button>
                </div>
              ))}
              <button onClick={() => setShowSuggestions(false)} className="text-xs text-[#9A948C] hover:text-[#6B655E]">Hide suggestions</button>
            </div>
          )}
        </div>

        {/* CTA */}
        <div className="space-y-4 pt-6">
          {error && <p className="text-center text-sm text-red-500 animate-in fade-in duration-200">{error}</p>}
          <button
            onClick={handleContinue}
            disabled={isSubmitting}
            className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
          >
            {isSubmitting ? "Saving Strategy..." : "Continue"}
          </button>
        </div>

      </div>
    </div>
  );
}
