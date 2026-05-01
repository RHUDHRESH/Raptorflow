"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { CheckCircle2, ChevronRight, Loader2, Sparkles, RefreshCcw } from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { foundationApi, getApiBaseUrl } from "@/lib/api";
import { cn } from "@/lib/utils";

/**
 * Foundation Screen 21: The Campaign Strategist (Final Review & Launch)
 * The ceremonial conclusion to the onboarding journey.
 */
export default function FoundationStep21() {
  const router = useRouter();
  const { getToken } = useAuth();
  const store = useFoundationStore();
  const { sectionData, setSectionData, setStep } = store;

  const [part, setPart] = useState<1 | 2 | 3 | 4>(1);
  const [strategistName, setStrategistName] = useState("");
  const [personality, setPersonality] = useState({
    direct: 50,
    challenger: 50,
    dataDriven: 50,
  });

  const [isBuilding, setIsBuilding] = useState(false);
  const [buildStep, setBuildStep] = useState(0);
  const [buildProgress, setBuildProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setStep(21);
  }, [setStep]);

  // -- PART 4: BUILD ANIMATION LOGIC --
  const buildText = [
    "Initialising your 21-agent team...",
    `Briefing ${strategistName} on your business...`,
    "Setting up competitive intelligence...",
    "Preparing your first Daily Wins briefing...",
    "Building your office...",
  ];

  const startBuild = async () => {
    setPart(4);
    setIsBuilding(true);
    setError(null);

    // 1. API Call
    const apiCall = async () => {
      try {
        const token = await getToken();
        const response = await fetch(`${getApiBaseUrl()}/api/v1/foundation/complete`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            strategistName,
            personality,
            fullStore: sectionData,
          }),
        });
        if (!response.ok) throw new Error("Build failed");
        return true;
      } catch (err) {
        console.error("[Foundation21] Launch Error:", err);
        return false;
      }
    };

    // 2. Parallel minimum 8-second animation + API
    const startTime = Date.now();

    // Animate progress bar over 8s
    const progressInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min((elapsed / 8000) * 100, 100);
      setBuildProgress(progress);

      const step = Math.floor((elapsed / 8000) * buildText.length);
      setBuildStep(Math.min(step, buildText.length - 1));

      if (elapsed >= 8000) clearInterval(progressInterval);
    }, 50);

    const success = await apiCall();

    // Wait for at least 8 seconds
    const remainingTime = 8000 - (Date.now() - startTime);
    setTimeout(
      async () => {
        clearInterval(progressInterval);
        if (success) {
          setIsComplete(true);
          setIsBuilding(false);
          setBuildProgress(100);

          // Trigger foundation quick scan in background — result shown on /app/foundation
          foundationApi
            .triggerQuickScan()
            .catch((e) => console.error("[Foundation21] Quick scan failed:", e));
        } else {
          setError("We couldn't finalize your office. Please check your connection and try again.");
          setIsBuilding(false);
        }
      },
      Math.max(0, remainingTime),
    );
  };

  // -- REUSABLE COMPONENTS --

  const Slider = ({ labelL, labelR, val, setVal }: any) => (
    <div className="flex items-center gap-4 w-full">
      <span className="w-24 text-right text-[10px] font-bold uppercase tracking-widest text-[#6B655E]">
        {labelL}
      </span>
      <input
        type="range"
        min="0"
        max="100"
        value={val}
        onChange={(e) => setVal(parseInt(e.target.value))}
        className="flex-1 h-1 bg-[#E5DED4] rounded-full appearance-none accent-[#f59e0b] cursor-pointer"
      />
      <span className="w-24 text-left text-[10px] font-bold uppercase tracking-widest text-[#6B655E]">
        {labelR}
      </span>
    </div>
  );

  // -- SUMMARY DATA RESOLVER --
  const summary = useMemo(() => {
    const bizName = sectionData.scan_results?.businessName || "your business";
    const icp = sectionData.icp?.primaryICP || { name: "target customer", pain: "specific pain" };
    const problem = sectionData.customer_problem?.problemStatement || "core problem";
    const positioning = sectionData.positioning?.positioningStatement || "marketing strategy";
    const goal = sectionData.primary_goal?.successMetric || "growth targets";
    const comps =
      sectionData.competitors?.competitors
        ?.map((c: any) => c.url.replace(/^https?:\/\//, ""))
        .join(", ") || "the market";
    const voice = sectionData.brand_personality?.voiceTraits?.join(", ") || "professional";

    return (
      <p className="text-lg text-[#2A2622] font-light leading-relaxed">
        &quot;Here is what I understand about{" "}
        <span className="text-[#f59e0b] font-medium">{bizName}</span>. You serve{" "}
        <span className="text-[#2A2622] font-medium">{icp.name}</span> — {icp.pain}. The problem you
        solve is {problem}. Your positioning: {positioning}. Your goal for the next 90 days is{" "}
        <span className="text-[#2A2622] font-medium">{goal}</span>. The competitors I&apos;ll be
        watching are {comps}. And {bizName} should always sound{" "}
        <span className="text-[#2A2622] font-medium">{voice}</span>.&quot;
      </p>
    );
  }, [sectionData]);

  // -- RENDERERS --

  if (part === 4) {
    return (
      <div className="fixed inset-0 bg-[#FBF8F2] z-50 flex flex-col items-center justify-center p-6 transition-all duration-1000">
        {!isComplete && !error && (
          <div className="w-full max-w-lg space-y-12 flex flex-col items-center animate-in fade-in duration-1000">
            <h2 className="text-3xl font-bold text-[#2A2622] tracking-widest uppercase">
              RaptorFlow
            </h2>

            <div className="text-center h-8 relative w-full">
              <p className="text-lg text-[#2A2622] font-medium animate-pulse">
                {buildText[buildStep]}
              </p>
            </div>

            <div className="flex gap-2">
              <div className="w-2 h-2 bg-[#D97757] rounded-full animate-bounce [animation-delay:-0.3s]" />
              <div className="w-2 h-2 bg-[#D97757] rounded-full animate-bounce [animation-delay:-0.15s]" />
              <div className="w-2 h-2 bg-[#D97757] rounded-full animate-bounce" />
            </div>

            <div className="w-full bg-[#F5F0E8] h-[2px] fixed bottom-0 left-0 right-0">
              <div
                className="h-full bg-[#D97757] transition-all duration-300"
                style={{ width: `${buildProgress}%` }}
              />
            </div>
          </div>
        )}

        {error && (
          <div className="text-center space-y-6 animate-in zoom-in-95 duration-500">
            <h3 className="text-xl font-bold text-red-500">Strategic Error</h3>
            <p className="text-[#6B655E] max-w-xs">{error}</p>
            <button
              onClick={startBuild}
              className="px-8 py-3 bg-[#f59e0b] text-black font-bold rounded-lg flex items-center gap-2 mx-auto"
            >
              <RefreshCcw className="w-4 h-4" /> Try again
            </button>
          </div>
        )}

        {isComplete && (
          <div className="w-full max-w-lg space-y-8 flex flex-col items-center animate-in fade-in zoom-in-95 duration-[1200ms]">
            <CheckCircle2 className="w-20 h-20 text-green-500 animate-in bounce-in duration-1000" />
            <div className="text-center space-y-2">
              <h2 className="text-4xl font-bold text-[#2A2622]">Your office is ready.</h2>
              <p className="text-xl text-[#6B655E] font-light italic mt-4">
                &quot;I have everything I need. Let&apos;s build something.&quot;
              </p>
            </div>
            <button
              onClick={() => router.push("/app/foundation")}
              className="mt-8 px-12 py-4 bg-[#f59e0b] hover:bg-white text-black font-bold rounded-full transition-all group flex items-center gap-3"
            >
              Open Foundation
              <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[640px] space-y-12">
        {/* PART 1: NAME */}
        {part >= 1 && (
          <div
            className={cn(
              "space-y-8 animate-in fade-in slide-in-from-top-4 duration-700",
              part > 1 && "opacity-20 pointer-events-none grayscale scale-[0.98]",
            )}
          >
            <div className="space-y-2 text-center">
              <h1 className="text-3xl font-bold text-[#2A2622]">
                Your Campaign Strategist is about to come to life.
              </h1>
              <p className="text-[#6B655E] text-base">What would you like to call them?</p>
            </div>
            <div className="flex flex-col items-center gap-8">
              <input
                autoFocus
                className="text-center text-3xl font-light text-[#2A2622] bg-transparent border-b-2 border-[#f59e0b] outline-none pb-2 px-4 w-full max-w-sm placeholder:text-[#BAB0A0]"
                placeholder="Name your Strategist"
                value={strategistName}
                onChange={(e) => setStrategistName(e.target.value)}
              />
              {part === 1 && (
                <button
                  disabled={!strategistName}
                  onClick={() => setPart(2)}
                  className="px-10 py-3 bg-[#f59e0b] hover:bg-white text-black font-bold rounded-full disabled:opacity-30 disabled:grayscale transition-all"
                >
                  Continue
                </button>
              )}
            </div>
          </div>
        )}

        {/* PART 2: PERSONALITY */}
        {part >= 2 && (
          <div
            className={cn(
              "space-y-8 animate-in fade-in slide-in-from-top-4 duration-700",
              part > 2 && "opacity-20 pointer-events-none grayscale scale-[0.98]",
            )}
          >
            <div className="space-y-1 text-center">
              <h2 className="text-2xl font-bold text-[#2A2622]">Who is {strategistName}?</h2>
              <p className="text-sm text-[#6B655E] uppercase tracking-widest font-bold">
                Shape how they communicate with you
              </p>
            </div>

            <div className="space-y-2 bg-[#FBF8F2] p-8 rounded-2xl border border-[#E5DED4]">
              <Slider
                labelL="Direct"
                labelR="Diplomatic"
                val={personality.direct}
                setVal={(v: any) => setPersonality({ ...personality, direct: v })}
              />
              <Slider
                labelL="Challenger"
                labelR="Conservative"
                val={personality.challenger}
                setVal={(v: any) => setPersonality({ ...personality, challenger: v })}
              />
              <Slider
                labelL="Data-Driven"
                labelR="Intuitive"
                val={personality.dataDriven}
                setVal={(v: any) => setPersonality({ ...personality, dataDriven: v })}
              />

              <div className="mt-8 flex items-center gap-3 bg-black/40 border border-[#E5DED4] rounded-xl p-3">
                <Sparkles className="w-4 h-4 text-[#D97757] shrink-0" />
                <p className="text-xs text-[#6B655E]">
                  Based on your answers, we suggest:{" "}
                  <span className="text-[#2A2622] font-bold">
                    [Direct, Challenger, Data-driven]
                  </span>{" "}
                  — adjust freely.
                </p>
              </div>
            </div>

            {part === 2 && (
              <div className="flex justify-center">
                <button
                  onClick={() => setPart(3)}
                  className="px-10 py-3 bg-[#f59e0b] hover:bg-white text-black font-bold rounded-full transition-all"
                >
                  Confirm Personality
                </button>
              </div>
            )}
          </div>
        )}

        {/* PART 3: REVIEW */}
        {part === 3 && (
          <div className="space-y-8 animate-in fade-in slide-in-from-top-4 duration-1000">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold tracking-widest text-[#6B655E]">
                  {strategistName} speaking:
                </span>
                <span className="text-[10px] uppercase font-bold tracking-widest text-[#f59e0b] flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#f59e0b] animate-pulse" /> Final
                  Strategist Brief
                </span>
              </div>

              <div className="bg-[#FBF8F2] border border-[#D5CBC0]/50 rounded-2xl p-8 relative shadow-2xl overflow-hidden group">
                {/* Visual Accent */}
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#f59e0b]" />

                {summary}

                {/* Edit Links */}
                <div className="mt-8 pt-8 border-t border-[#E5DED4] flex flex-wrap gap-x-6 gap-y-2">
                  {[
                    { label: "Edit Business", to: "/foundation/1" },
                    { label: "Target Customer", to: "/foundation/6" },
                    { label: "Goal", to: "/foundation/15" },
                    { label: "Voice", to: "/foundation/11" },
                  ].map((link) => (
                    <button
                      key={link.label}
                      onClick={() => router.push(`${link.to}?returnTo=21` as never)}
                      className="text-[10px] uppercase tracking-widest text-[#6B655E] hover:text-[#f59e0b] transition-colors font-bold"
                    >
                      {link.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex flex-col items-center gap-6 pt-4">
              <button
                onClick={startBuild}
                className="w-full bg-[#f59e0b] hover:bg-white text-black font-extrabold text-lg rounded-full py-5 transition-all shadow-[0_10px_30px_rgba(217,119,87,0.2)]"
              >
                Looks good — let&apos;s go
              </button>
              <p className="text-xs text-[#6B655E] uppercase tracking-tighter">
                By launching, you authorise your AI team to begin monitoring and strategy work.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
