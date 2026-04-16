"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

/**
 * Custom Styled Slider
 */
function BrandSlider({ 
  labelLeft, 
  labelRight, 
  value, 
  onChange 
}: { 
  labelLeft: string; 
  labelRight: string; 
  value: number; 
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex items-center gap-6 w-full py-4">
      <span className="w-20 text-right text-xs font-bold uppercase tracking-widest text-zinc-500 whitespace-nowrap">
        {labelLeft}
      </span>
      <div className="relative flex-1 h-1 flex items-center">
        {/* Background Track */}
        <div className="absolute inset-0 bg-zinc-800 rounded-full" />
        {/* Fill Track */}
        <div 
          className="absolute inset-y-0 left-0 bg-[#f59e0b] rounded-full transition-all duration-75"
          style={{ width: `${value}%` }} 
        />
        <input
          type="range"
          min="0"
          max="100"
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          className="absolute inset-0 w-full opacity-0 cursor-grab active:cursor-grabbing z-10"
        />
        {/* Thumb Overlay */}
        <div 
          className="absolute w-5 h-5 bg-[#f59e0b] border-2 border-amber-400 rounded-full shadow-lg pointer-events-none transition-all duration-75"
          style={{ left: `calc(${value}% - 10px)` }}
        />
      </div>
      <span className="w-20 text-left text-xs font-bold uppercase tracking-widest text-zinc-500 whitespace-nowrap">
        {labelRight}
      </span>
    </div>
  );
}

/**
 * Foundation Screen 11: Brand Personality
 * Uses interactive sliders to define the brand's tone of voice.
 */
export default function FoundationStep11() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [sliders, setSliders] = useState({
    formalCasual: 50,
    seriousPlayful: 50,
    reservedBold: 50,
  });
  const [neverSay, setNeverSay] = useState("");
  const [previewText, setPreviewText] = useState("");
  const [isFading, setIsFading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(11);
    const existing = sectionData.brand_personality;
    if (existing) {
      setSliders(existing.sliders || { formalCasual: 50, seriousPlayful: 50, reservedBold: 50 });
      setNeverSay(existing.neverSay || "");
    }
  }, [setStep, sectionData]);

  // Handle Voice Preview Logic
  useEffect(() => {
    const { formalCasual: f, seriousPlayful: s, reservedBold: b } = sliders;
    
    let nextText = "We help businesses like yours grow faster — without the guesswork. Here's what that looks like in practice.";

    if (f < 30 && s < 30 && b < 30) {
      nextText = "Hey! So honestly, we've been heads-down building something for people like you, and the results? Kind of wild.";
    } else if (f < 40 && s < 40 && b > 70) {
      nextText = "We're not here to be your average agency. We're here to 3x your pipeline. Let's go.";
    } else if (f > 70 && s > 70 && b < 30) {
      nextText = "We partner with organisations seeking measurable, sustained growth through disciplined marketing strategy.";
    } else if (f > 70 && s > 70 && b > 70) {
      nextText = "We deliver results. Across 200+ engagements, our clients average 47% improvement in qualified lead generation within 90 days.";
    } else if (f < 30 && s > 70 && b < 40) {
      nextText = "Building a brand is a long game. Here's what the data says about where to start.";
    }

    // Fade Transition
    setIsFading(true);
    const timeout = setTimeout(() => {
      setPreviewText(nextText);
      setIsFading(false);
    }, 200);

    return () => clearTimeout(timeout);
  }, [sliders]);

  const traits = [
    sliders.formalCasual > 50 ? "Conversational" : "Professional",
    sliders.seriousPlayful > 50 ? "Energetic" : "Data-driven",
    sliders.reservedBold > 50 ? "Direct" : "Measured"
  ];

  const handleContinue = async () => {
    setIsSubmitting(true);
    const data = {
      sliders,
      voiceTraits: traits,
      neverSay,
    };

    try {
      const token = await getToken();
      setSectionData("brand_personality", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/brand_personality`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/12");
    } catch (err) {
      console.error("[Foundation11] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#1a1a1a]">
      <div className="w-full max-w-[600px] space-y-12">
        
        {/* HEADER */}
        <h1 className="text-3xl font-bold text-white">
          What should your brand sound and feel like?
        </h1>

        {/* SLIDERS SECTION */}
        <div className="space-y-4">
          <BrandSlider 
            labelLeft="Formal" 
            labelRight="Casual" 
            value={sliders.formalCasual} 
            onChange={(v) => setSliders({...sliders, formalCasual: v})} 
          />
          <BrandSlider 
            labelLeft="Serious" 
            labelRight="Playful" 
            value={sliders.seriousPlayful} 
            onChange={(v) => setSliders({...sliders, seriousPlayful: v})} 
          />
          <BrandSlider 
            labelLeft="Reserved" 
            labelRight="Bold" 
            value={sliders.reservedBold} 
            onChange={(v) => setSliders({...sliders, reservedBold: v})} 
          />
        </div>

        {/* VOICE PREVIEW PANEL */}
        <div className="space-y-4 pt-4">
          <label className="text-[10px] uppercase font-bold tracking-widest text-zinc-500">Your brand sounds like this:</label>
          <div className="bg-[#1e1e1e] border border-zinc-800 rounded-xl p-6 min-h-[140px] shadow-2xl transition-all duration-300">
            <p className={cn(
              "text-lg text-white leading-relaxed italic transition-opacity duration-300",
              isFading ? "opacity-0" : "opacity-100"
            )}>
              &quot;{previewText}&quot;
            </p>
            
            <div className="flex flex-wrap gap-2 mt-6">
              {traits.map(t => (
                <span key={t} className="px-3 py-1 bg-zinc-800 text-zinc-300 border border-zinc-700 rounded-full text-[10px] font-bold uppercase tracking-wider">
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* NEVER SAY FIELD */}
        <div className="space-y-3 pt-4">
          <div className="space-y-1">
            <label className="text-sm font-medium text-zinc-300 tracking-tight">One thing your brand would never say:</label>
            <p className="text-xs text-zinc-500 tracking-tight">(Optional, but powerful — this trains your AI team on brand guardrails)</p>
          </div>
          <input
            className="w-full bg-[#262626] border border-zinc-700 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:border-[#f59e0b] transition-colors"
            placeholder="e.g. 'Synergize your go-to-market learnings to unlock growth'"
            value={neverSay}
            onChange={(e) => setNeverSay(e.target.value)}
          />
        </div>

        {/* CTA */}
        <button
          onClick={handleContinue}
          disabled={isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-zinc-700 disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all mt-8"
        >
          {isSubmitting ? "Saving Brand Persona..." : "Continue"}
        </button>

      </div>
    </div>
  );
}
