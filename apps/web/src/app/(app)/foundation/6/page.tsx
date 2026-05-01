"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { Plus, Minus, UserCircle } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";
import { getApiBaseUrl } from "@/lib/api";

/**
 * Foundation Screen 6: Ideal Customer Profile (ICP)
 * Defines the core target audience in high detail.
 */
export default function FoundationStep6() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [primary, setPrimary] = useState({
    name: "",
    industry: "",
    role: "",
    pain: "",
    howTheyFind: [] as string[],
    ownWords: "",
  });

  const [secondary, setSecondary] = useState({
    name: "",
    industry: "",
    pain: "",
  });

  const [showSecondary, setShowSecondary] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setStep(6);
    const existing = sectionData.icp;
    if (existing) {
      if (existing.primaryICP) setPrimary(existing.primaryICP);
      if (existing.secondICP) {
        setSecondary(existing.secondICP);
        setShowSecondary(true);
      }
    }
  }, [setStep, sectionData]);

  const findChannels = [
    "Google search",
    "LinkedIn",
    "Referrals / word of mouth",
    "Industry events",
    "Content / blogs",
    "Ads",
  ];

  const toggleChannel = (channel: string) => {
    setPrimary((prev) => ({
      ...prev,
      howTheyFind: prev.howTheyFind.includes(channel)
        ? prev.howTheyFind.filter((c) => c !== channel)
        : [...prev.howTheyFind, channel],
    }));
  };

  /**
   * Submit logic
   */
  const handleContinue = async () => {
    if (!primary.name || !primary.pain || !primary.ownWords) {
      setError(
        "Please fill in the persona name, their pain, and the description in their own words.",
      );
      return;
    }

    setIsSubmitting(true);
    const data = {
      primaryICP: primary,
      secondICP: showSecondary ? secondary : null,
    };

    try {
      const token = await getToken();
      setSectionData("icp", data);

      await fetch(`${getApiBaseUrl()}/api/v1/foundation/section/icp`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/7");
    } catch (err) {
      console.error("[Foundation6] Save Error:", err);
      setError("Failed to save. Please try again.");
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
            Who is your ideal customer?
          </h1>
          <p className="text-base text-[#6B655E]">
            Not everyone. The one person who needs you most. Give them a name and a life.
          </p>
        </div>

        {/* PRIMARY ICP CARD */}
        <div className="w-full bg-[#262626] border border-[#D5CBC0] rounded-2xl p-6 space-y-8 shadow-xl">
          {/* Persona Name */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-[#6B655E] uppercase tracking-wider flex items-center gap-2">
              <UserCircle className="w-3 h-3" />
              Give this person a name
            </label>
            <input
              autoFocus
              className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] focus:outline-none focus:border-[#f59e0b] transition-colors"
              placeholder="e.g. The Growth-Stage D2C Founder"
              value={primary.name}
              onChange={(e) => setPrimary({ ...primary, name: e.target.value })}
            />
            <p className="text-xs text-[#6B655E] italic">
              A persona name, not a real person&apos;s name.
            </p>
          </div>

          {/* Industry/Type & Role Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#6B655E] uppercase tracking-wider">
                Industry / Type
              </label>
              <input
                className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] focus:outline-none focus:border-[#f59e0b] transition-colors"
                placeholder="e.g. D2C skincare brand"
                value={primary.industry}
                onChange={(e) => setPrimary({ ...primary, industry: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#6B655E] uppercase tracking-wider">
                Their title or role
              </label>
              <input
                className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] focus:outline-none focus:border-[#f59e0b] transition-colors"
                placeholder="e.g. Founder, Head of Marketing"
                value={primary.role}
                onChange={(e) => setPrimary({ ...primary, role: e.target.value })}
              />
            </div>
          </div>

          {/* Their Biggest Pain */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-[#6B655E] uppercase tracking-wider">
              What keeps them up at night?
            </label>
            <textarea
              rows={3}
              className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-[#f59e0b] resize-y transition-colors"
              placeholder="The specific problem they're trying to solve — before they found you."
              value={primary.pain}
              onChange={(e) => setPrimary({ ...primary, pain: e.target.value })}
            />
          </div>

          {/* Multi-select Channel Pills */}
          <div className="space-y-3">
            <label className="text-xs font-bold text-[#6B655E] uppercase tracking-wider">
              How do they look for solutions like yours?
            </label>
            <div className="flex flex-wrap gap-2">
              {findChannels.map((channel) => {
                const isSelected = primary.howTheyFind.includes(channel);
                return (
                  <button
                    key={channel}
                    onClick={() => toggleChannel(channel)}
                    className={cn(
                      "px-4 py-2 rounded-full border text-xs transition-all duration-200",
                      isSelected
                        ? "border-[#f59e0b] bg-[#f59e0b]/10 text-[#2A2622] shadow-[0_0_10px_rgba(217,119,87,0.1)]"
                        : "border-[#D5CBC0] bg-transparent text-[#6B655E] hover:border-[#D5CBC0]",
                    )}
                  >
                    {channel}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* CRITICAL FIELD: OWN WORDS */}
        <div className="rounded-xl bg-[#FBF8F2] p-5 border-l-2 border-[#f59e0b]/50 space-y-4">
          <div className="space-y-1">
            <h3 className="text-base font-medium text-[#2A2622]">In their own words...</h3>
            <p className="text-sm text-[#6B655E] leading-relaxed">
              How would this person describe the problem they have? Use their language, not yours.
            </p>
          </div>
          <textarea
            rows={4}
            className="w-full bg-[#FBF8F2] border border-[#E5DED4] rounded-lg px-4 py-3 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-[#f59e0b] resize-y transition-colors"
            placeholder="I'm spending 3 hours every Monday just trying to figure out what to post this week..."
            value={primary.ownWords}
            onChange={(e) => setPrimary({ ...primary, ownWords: e.target.value })}
          />
        </div>

        {/* SECOND ICP TOGGLE */}
        <div className="space-y-8">
          {!showSecondary ? (
            <button
              onClick={() => setShowSecondary(true)}
              className="flex items-center gap-2 text-sm text-[#6B655E] hover:text-[#2A2622] transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add a second customer type</span>
            </button>
          ) : (
            <div className="p-6 bg-[#262626] border border-[#D5CBC0] rounded-2xl space-y-6 animate-in fade-in slide-in-from-top-4 duration-500">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-[#9A948C] uppercase tracking-widest">
                  Second Customer Persona
                </h3>
                <button
                  onClick={() => {
                    setShowSecondary(false);
                    setSecondary({ name: "", industry: "", pain: "" });
                  }}
                  className="text-[10px] uppercase tracking-widest text-[#6B655E] hover:text-red-400 flex items-center gap-1"
                >
                  <Minus className="w-3 h-3" />
                  Remove
                </button>
              </div>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-[#6B655E] uppercase tracking-wider">
                    Persona Name
                  </label>
                  <input
                    className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] focus:outline-none"
                    value={secondary.name}
                    onChange={(e) => setSecondary({ ...secondary, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold text-[#6B655E] uppercase tracking-wider">
                    Industry
                  </label>
                  <input
                    className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] focus:outline-none"
                    value={secondary.industry}
                    onChange={(e) => setSecondary({ ...secondary, industry: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold text-[#6B655E] uppercase tracking-wider">
                    Their Pain
                  </label>
                  <textarea
                    rows={2}
                    className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-lg px-4 py-3 text-[#2A2622] focus:outline-none"
                    value={secondary.pain}
                    onChange={(e) => setSecondary({ ...secondary, pain: e.target.value })}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ERROR & CTA */}
        <div className="space-y-4 pt-4">
          {error && <p className="text-center text-sm text-red-500">{error}</p>}
          <button
            onClick={handleContinue}
            disabled={isSubmitting}
            className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all"
          >
            {isSubmitting ? "Saving..." : "Continue"}
          </button>
        </div>
      </div>
    </div>
  );
}
