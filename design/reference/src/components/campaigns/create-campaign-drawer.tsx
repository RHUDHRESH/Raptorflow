"use client";

import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  X, 
  Radio, 
  Users, 
  ShoppingCart, 
  Heart, 
  RefreshCcw,
  Plus,
  Loader2,
  CheckCircle2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";

interface DrawerProps {
  open: boolean;
  onClose: () => void;
}

const STEPS = {
  1: "New campaign",
  2: "Reviewing your brief...",
  3: "Your campaign is ready"
} as const;

export function CreateCampaignDrawer({ open, onClose }: DrawerProps) {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [step, setStep] = useState<1 | 2 | 3>(1);

  // Step 1 State
  const [goalType, setGoalType] = useState<string>("");
  const [goalStatement, setGoalStatement] = useState("");
  const [timelineMode, setTimelineMode] = useState<string>("30");
  const [customDays, setCustomDays] = useState("");
  const [budgetRange, setBudgetRange] = useState("");
  const [notes, setNotes] = useState("");

  // System State
  const [campaignId, setCampaignId] = useState<string | null>(null);
  const [briefStatus, setBriefStatus] = useState<string>("evaluating");
  const [agentsVisible, setAgentsVisible] = useState<number>(0);
  const [revisionMode, setRevisionMode] = useState(false);
  const [revisionNotes, setRevisionNotes] = useState("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Helper: Strategist Initials
  const strategistName = typeof window !== 'undefined' ? localStorage.getItem("strategist_name") || "S" : "S";

  // Reset State
  const handleClose = () => {
    setStep(1);
    setGoalType("");
    setGoalStatement("");
    setTimelineMode("30");
    setCustomDays("");
    setBudgetRange("");
    setNotes("");
    setCampaignId(null);
    setBriefStatus("evaluating");
    setAgentsVisible(0);
    setRevisionMode(false);
    setRevisionNotes("");
    onClose();
  };

  // ─── Mutations ───────────────────────────────────────────────

  const createBrief = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const timeline_days = timelineMode === "Custom" ? parseInt(customDays) : parseInt(timelineMode);
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/brief`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          goal_type: goalType,
          goal_statement: goalStatement,
          timeline_days,
          budget_range: budgetRange,
          notes
        })
      });
      if (!res.ok) throw new Error("Brief submission failed");
      return res.json() as Promise<{ campaign_id: string }>;
    },
    onSuccess: (data) => {
      setCampaignId(data.campaign_id);
      setStep(2);
    }
  });

  const { data: campaignData, isLoading: isCampaignLoading } = useQuery({
    queryKey: ["campaign_detail", campaignId],
    enabled: step === 3 && !!campaignId,
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.json();
    }
  });

  const approveCampaign = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/approve`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      showToast("Campaign activated ✓");
      handleClose();
    }
  });

  const reviseCampaign = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/revise`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ revision_notes: revisionNotes })
      });
      return res.json();
    },
    onSuccess: () => {
      setStep(2);
      setBriefStatus("evaluating");
      setRevisionMode(false);
      setRevisionNotes("");
    }
  });

  // ─── Step 2 Polling ──────────────────────────────────────────

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (step === 2 && campaignId) {
      interval = setInterval(async () => {
        try {
          const token = await getToken();
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/brief-status`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          const data = await res.json();
          setBriefStatus(data.status);

          if (data.status === "pending_approval") {
            setStep(3);
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 3000);
    }

    return () => clearInterval(interval);
  }, [step, campaignId]);

  // Agent Visibility Delay
  useEffect(() => {
    if (briefStatus === "council_session") {
      const timerIds = [400, 800, 1200, 1600, 2000].map((delay, idx) => 
        setTimeout(() => setAgentsVisible(idx + 1), delay)
      );
      return () => timerIds.forEach(clearTimeout);
    } else {
      setAgentsVisible(0);
    }
  }, [briefStatus]);

  // Toast Helper
  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  // ─── Rendering Helpers ───────────────────────────────────────

  const timeline_days = timelineMode === "Custom" ? parseInt(customDays) : parseInt(timelineMode);
  const step1Valid = !!goalType && goalStatement.length > 10 && timeline_days > 0 && !!budgetRange;

  const agentActivity = [
    { name: "Ogilvy", action: "reviewing positioning..." },
    { name: "Patel", action: "analysing channel mix..." },
    { name: "Vaynerchuk", action: "evaluating reach strategy..." },
    { name: "Analytics Director", action: "projecting outcomes..." },
    { name: "Hopkins", action: "stress-testing conversion logic..." }
  ];

  const goalOptions = [
    { id: "awareness", icon: Radio, title: "Build awareness", desc: "Expand reach and brand recognition" },
    { id: "leads", icon: Users, title: "Generate leads", desc: "Fill the pipeline with qualified prospects" },
    { id: "conversion", icon: ShoppingCart, title: "Drive conversions", desc: "Turn leads into customers" },
    { id: "retention", icon: Heart, title: "Retain customers", desc: "Reduce churn, increase loyalty" },
    { id: "re_engagement", icon: RefreshCcw, title: "Re-engage audience", desc: "Wake up a cold audience" },
  ];

  return (
    <>
      <div className={cn("fixed inset-0 z-50 pointer-events-none", open && "pointer-events-auto")}>
        {/* Backdrop */}
        <div 
          className={cn(
            "fixed inset-0 bg-black/60 transition-opacity duration-300",
            open ? "opacity-100" : "opacity-0 pointer-events-none"
          )}
          onClick={handleClose}
        />

        {/* Panel */}
        <div 
          className={cn(
            "fixed right-0 top-0 h-full w-[480px] max-w-full bg-[#1a1a1a] border-l border-zinc-800 flex flex-col transition-transform duration-300 ease-in-out",
            open ? "translate-x-0" : "translate-x-full"
          )}
        >
          {/* Header */}
          <div className="flex-shrink-0 px-6 py-5 border-b border-zinc-800 flex justify-between items-center">
            <h2 className="text-xl font-semibold text-white tracking-tight">{STEPS[step]}</h2>
            <button onClick={handleClose} className="text-zinc-400 hover:text-white transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Stepper Dots */}
          <div className="px-6 pt-4 flex-shrink-0 flex gap-2">
            {[1, 2, 3].map(i => (
              <div key={i} className={cn("w-2 h-2 rounded-full transition-colors", step >= i ? "bg-amber-500" : "bg-zinc-700")} />
            ))}
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto px-6 py-5 scrollbar-hide">
            {step === 1 && (
              <div className="animate-in fade-in slide-in-from-right-2 duration-300">
                <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">What's the goal?</p>
                <div className="space-y-2 mb-6">
                  {goalOptions.map(opt => {
                    const isSelected = goalType === opt.id;
                    const Icon = opt.icon;
                    return (
                      <div 
                        key={opt.id}
                        onClick={() => setGoalType(opt.id)}
                        className={cn(
                          "flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition-all",
                          isSelected ? "border-amber-500 bg-amber-500/10" : "border-zinc-700 bg-[#262626] hover:border-zinc-500"
                        )}
                      >
                         <Icon className={cn("w-5 h-5", isSelected ? "text-amber-500" : "text-zinc-400")} />
                         <div>
                            <p className="text-sm text-white font-mediumLeading-none mb-1">{opt.title}</p>
                            <p className="text-xs text-zinc-400">{opt.desc}</p>
                         </div>
                      </div>
                    );
                  })}
                </div>

                {goalType && (
                  <div className="animate-in fade-in duration-500 slide-in-from-top-2">
                    <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Describe what you want to achieve</p>
                    <textarea 
                      rows={4}
                      className="bg-[#0f0f0f] border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:border-amber-500 focus:outline-none w-full mb-6 resize-none"
                      placeholder="e.g. 50 qualified leads from LinkedIn in 60 days targeting founder-stage D2C brands."
                      value={goalStatement}
                      onChange={(e) => setGoalStatement(e.target.value)}
                    />

                    <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Timeline</p>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {["30", "60", "90", "Custom"].map(t => (
                        <button
                          key={t}
                          onClick={() => setTimelineMode(t)}
                          className={cn(
                            "px-4 py-2 rounded-full border text-sm transition-all",
                            timelineMode === t ? "border-amber-500 text-white bg-amber-500/10" : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                          )}
                        >
                          {t}{t !== "Custom" ? " days" : ""}
                        </button>
                      ))}
                    </div>
                    {timelineMode === "Custom" && (
                      <input 
                        type="number"
                        className="bg-[#0f0f0f] border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white w-full mb-6 placeholder-zinc-600 focus:border-amber-500 focus:outline-none"
                        placeholder="Number of days"
                        value={customDays}
                        onChange={(e) => setCustomDays(e.target.value)}
                      />
                    )}

                    <div className="mt-6">
                      <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Budget for this campaign</p>
                      <div className="space-y-2 mb-6">
                        {["₹0 — Organic only", "₹10,000 – ₹50,000", "₹50,00,00 – ₹2,00,000", "₹2,00,000 – ₹10,00,000", "₹10,00,000+"].map(b => (
                          <div 
                            key={b}
                            onClick={() => setBudgetRange(b)}
                            className={cn(
                              "p-4 rounded-xl border cursor-pointer transition-all text-sm",
                              budgetRange === b ? "border-amber-500 bg-amber-500/10 text-white" : "border-zinc-700 bg-[#262626] text-zinc-400 hover:border-zinc-500"
                            )}
                          >
                            {b}
                          </div>
                        ))}
                      </div>
                    </div>

                    <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Anything else the Council should know? (optional)</p>
                    <textarea 
                      rows={2}
                      className="bg-[#0f0f0f] border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:border-amber-500 focus:outline-none w-full mb-6 resize-none"
                      placeholder="Context, constraints, or specific direction..."
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </div>
                )}
              </div>
            )}

            {step === 2 && (
              <div className="h-full flex flex-col justify-center animate-in fade-in duration-700">
                {briefStatus === "evaluating" && (
                  <div className="flex flex-col items-center gap-4 py-12">
                    <div className="w-12 h-12 rounded-full bg-amber-500/10 flex items-center justify-center text-amber-500 font-bold border border-amber-500/20 text-xl font-serif">
                       {strategistName.charAt(0)}
                    </div>
                    <p className="text-base text-white font-medium">Reviewing your brief...</p>
                    <div className="flex gap-2">
                       <span className="bg-amber-500 w-2 h-2 rounded-full animate-bounce [animation-delay:0ms]" />
                       <span className="bg-amber-500 w-2 h-2 rounded-full animate-bounce [animation-delay:150ms]" />
                       <span className="bg-amber-500 w-2 h-2 rounded-full animate-bounce [animation-delay:300ms]" />
                    </div>
                  </div>
                )}

                {briefStatus === "council_session" && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-base text-white font-medium mb-1 tracking-tight">The Council is deliberating</h3>
                      <p className="text-sm text-zinc-400">This typically takes 1–3 minutes.</p>
                    </div>
                    <div className="space-y-4 pt-4">
                       {agentActivity.map((agent, i) => (
                         <div 
                          key={agent.name}
                          className={cn(
                            "flex items-center gap-3 transition-opacity duration-500",
                            agentsVisible > i ? "opacity-100" : "opacity-0"
                          )}
                         >
                            <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse flex-shrink-0" />
                            <p className="text-sm text-zinc-300">
                              <span className="font-bold">{agent.name}</span> — {agent.action}
                            </p>
                         </div>
                       ))}
                    </div>
                  </div>
                )}

                {briefStatus === "failed" && (
                  <div className="text-center space-y-4">
                    <p className="text-sm text-red-500 bg-red-500/10 border border-red-500/20 px-4 py-3 rounded-lg">
                      The Council couldn't complete this session. Please refine your brief.
                    </p>
                    <Button variant="ghost" className="text-zinc-400" onClick={() => setStep(1)}>
                      Try again
                    </Button>
                  </div>
                )}
              </div>
            )}

            {step === 3 && (
              <div className="animate-in fade-in slide-in-from-bottom-2 duration-500 pb-20">
                {isCampaignLoading ? (
                  <div className="space-y-8">
                     <Skeleton className="h-32 rounded-xl" />
                     <Skeleton className="h-8 w-48" />
                     <div className="space-y-4">
                        <Skeleton className="h-16 rounded-lg" />
                        <Skeleton className="h-16 rounded-lg" />
                     </div>
                  </div>
                ) : campaignData && (
                  <>
                    <div className="bg-[#0f0f0f] rounded-xl p-4 border-l-4 border-amber-500 mb-6">
                      <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest mb-2">Council synthesis</p>
                      <p className="text-sm text-zinc-300 italic leading-relaxed">
                        "{campaignData.council_rationale?.synthesis}"
                      </p>
                    </div>

                    <h3 className="text-xl text-white font-bold mb-6 tracking-tight leading-none">{campaignData.name}</h3>

                    <p className="text-xs text-zinc-500 uppercase font-bold tracking-widest mb-3">Campaign structure</p>
                    <div className="space-y-1 mb-8">
                       {campaignData.moves?.map((move: any, idx: number) => (
                         <div key={move.move_id} className="flex items-start gap-4 py-4 border-b border-zinc-900 last:border-0 grow">
                            <div className="w-7 h-7 rounded-full bg-[#262626] border border-zinc-700 flex items-center justify-center text-[10px] text-zinc-400 font-mono font-bold flex-shrink-0">
                               {idx + 1}
                            </div>
                            <div className="flex-1 min-w-0">
                               <p className="text-sm text-white font-medium mb-1 truncate">{move.name}</p>
                               <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">
                                 {move.type} · {move.duration_days} days
                               </p>
                            </div>
                         </div>
                       ))}
                    </div>

                    {campaignData.outcome_projection && (
                      <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-4 mb-4">
                        <p className="text-[10px] text-green-500 uppercase font-bold tracking-widest mb-1.5 leading-none">Projected outcome</p>
                        <p className="text-sm text-green-300 font-medium">
                          {campaignData.outcome_projection}
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex-shrink-0 px-6 py-5 border-t border-zinc-800 bg-[#1a1a1a]">
            {step === 1 && (
              <Button 
                className="w-full bg-amber-500 text-black rounded-lg h-12 font-bold uppercase tracking-widest flex items-center justify-center gap-2"
                disabled={!step1Valid || createBrief.isPending}
                onClick={() => createBrief.mutate()}
              >
                {createBrief.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <>Submit brief <Plus className="w-4 h-4" /></>}
              </Button>
            )}

            {step === 3 && (
              <div className="space-y-4">
                <div className="flex gap-3">
                  <Button 
                    className="flex-1 bg-amber-500 text-black h-12 font-bold uppercase tracking-widest"
                    disabled={approveCampaign.isPending}
                    onClick={() => approveCampaign.mutate()}
                  >
                    {approveCampaign.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Approve →"}
                  </Button>
                  <Button 
                    variant="outline"
                    className="flex-1 border-zinc-700 text-zinc-300 h-12 hover:border-zinc-500 hover:text-white uppercase font-bold tracking-widest text-xs"
                    onClick={() => setRevisionMode(!revisionMode)}
                  >
                    Request changes
                  </Button>
                </div>
                
                {revisionMode && (
                  <div className="space-y-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <textarea 
                      className="w-full bg-[#0f0f0f] border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder:text-zinc-600 focus:border-amber-500 focus:outline-none resize-none"
                      rows={3}
                      placeholder="What would you like changed?"
                      value={revisionNotes}
                      onChange={(e) => setRevisionNotes(e.target.value)}
                    />
                    <Button 
                      className="w-full bg-amber-500 text-black h-10 font-bold uppercase tracking-widest text-xs"
                      onClick={() => reviseCampaign.mutate()}
                      disabled={!revisionNotes.trim() || reviseCampaign.isPending}
                    >
                      {reviseCampaign.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Send revision"}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Persistence Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-[100] bg-amber-500 text-black px-6 py-3 rounded-xl font-bold border border-white/20 shadow-2xl animate-in fade-in slide-in-from-right-4 duration-300">
          {toastMessage}
        </div>
      )}
    </>
  );
}
