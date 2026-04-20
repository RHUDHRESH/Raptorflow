"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { 
  Radio, 
  Users, 
  ShoppingCart, 
  Heart, 
  RefreshCcw, 
  Check, 
  AlertCircle 
} from "lucide-react";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/utils";

type GoalType = "awareness" | "leads" | "conversion" | "retention" | "re_engagement" | null;

/**
 * Foundation Screen 15: Primary Goal
 * Strategic directional choice that determines future campaign architecture.
 */
export default function FoundationStep15() {
  const router = useRouter();
  const { getToken } = useAuth();
  const { sectionData, setSectionData, setStep } = useFoundationStore();

  const [selectedGoal, setSelectedGoal] = useState<GoalType>(null);
  const [metric, setMetric] = useState("");
  const [showMetricModal, setShowMetricModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setStep(15);
    const existing = sectionData.primary_goal;
    if (existing) {
      setSelectedGoal(existing.goal || null);
      setMetric(existing.successMetric || "");
    }
  }, [setStep, sectionData]);

  const GOALS = [
    { 
      id: "awareness" as GoalType, 
      title: "Build awareness", 
      desc: "More people should know you exist. Expand reach, grow recognition, enter new audiences.", 
      icon: Radio,
      placeholder: "e.g. 50,000 impressions per month, 2,000 new followers"
    },
    { 
      id: "leads" as GoalType, 
      title: "Generate leads", 
      desc: "Turn strangers into prospects. Fill your pipeline with people who are ready to learn more.", 
      icon: Users,
      placeholder: "e.g. 50 qualified leads per month, 10% form conversion rate"
    },
    { 
      id: "conversion" as GoalType, 
      title: "Drive conversions", 
      desc: "Turn leads into customers. People already know you — now get them to buy.", 
      icon: ShoppingCart,
      placeholder: "e.g. 30 new customers, 3× ROAS on paid ads"
    },
    { 
      id: "retention" as GoalType, 
      title: "Retain customers", 
      desc: "Keep the customers you have. Reduce churn, increase repeat purchase, deepen loyalty.", 
      icon: Heart,
      placeholder: "e.g. Reduce churn from 8% to 4%, increase repeat purchases"
    },
    { 
      id: "re_engagement" as GoalType, 
      title: "Re-engage an audience", 
      desc: "You have an audience that has gone cold. Wake them back up.", 
      icon: RefreshCcw,
      placeholder: "e.g. 15% of lapsed customers make a purchase"
    },
  ];

  const handleGoalSelect = (id: GoalType) => {
    setSelectedGoal(id);
  };

  const handleContinue = async (force = false) => {
    if (!selectedGoal) return;
    
    if (!metric.trim() && !force) {
      setShowMetricModal(true);
      return;
    }

    setShowMetricModal(false);
    setIsSubmitting(true);
    const data = { goal: selectedGoal, successMetric: metric };

    try {
      const token = await getToken();
      setSectionData("primary_goal", data);

      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/foundation/section/primary_goal`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      router.push("/foundation/16");
    } catch (err) {
      console.error("[Foundation15] Error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const activeGoalData = GOALS.find(g => g.id === selectedGoal);

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24 min-h-screen bg-[#FBF8F2]">
      <div className="w-full max-w-[600px] space-y-10">
        
        {/* HEADER */}
        <h1 className="text-3xl font-bold text-[#2A2622] leading-tight">
          What are you trying to achieve in the next 90 days?
        </h1>

        {/* GOAL CARDS */}
        <div className="flex flex-col gap-3">
          {GOALS.map((goal) => {
            const isSelected = selectedGoal === goal.id;
            return (
              <div
                key={goal.id}
                onClick={() => handleGoalSelect(goal.id)}
                className={cn(
                  "relative p-5 rounded-xl border flex items-start gap-4 transition-all duration-300 cursor-pointer overflow-hidden group",
                  isSelected 
                    ? "border-[#f59e0b] bg-[#f59e0b]/10 shadow-[0_0_20px_rgba(217,119,87,0.1)]" 
                    : "bg-[#262626] border-[#D5CBC0] hover:border-[#D5CBC0]"
                )}
              >
                {isSelected && (
                  <div className="absolute top-4 right-4 bg-[#f59e0b] rounded-full p-1 animate-in zoom-in-50 duration-300">
                    <Check className="w-3 h-3 text-black" />
                  </div>
                )}
                
                <div className="shrink-0 mt-1">
                  <goal.icon className={cn(
                    "w-7 h-7 transition-colors",
                    isSelected ? "text-[#f59e0b]" : "text-[#6B655E] group-hover:text-[#4A4540]"
                  )} />
                </div>

                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-[#2A2622] tracking-tight">{goal.title}</h3>
                  <p className="text-sm text-[#6B655E] leading-relaxed font-medium">{goal.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* SUCCESS METRIC AREA */}
        <div className={cn(
          "overflow-hidden transition-all duration-500 ease-in-out",
          selectedGoal ? "max-h-[300px] opacity-100" : "max-h-0 opacity-0 pointer-events-none"
        )}>
          <div className="bg-[#FBF8F2] border border-[#E5DED4] rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="space-y-1">
              <label className="text-sm font-bold text-[#2A2622] tracking-tight uppercase tracking-widest text-[10px]">90-Day Target</label>
              <h4 className="text-sm font-medium text-[#9A948C]">In numbers, what does success look like?</h4>
              <p className="text-[10px] text-[#6B655E] uppercase tracking-widest">Be as specific as you can. This is what your AI team will aim for.</p>
            </div>
            
            <textarea
              rows={2}
              className="w-full bg-[#FBF8F2] border border-[#D5CBC0] rounded-xl px-4 py-3 text-[#2A2622] placeholder:text-[#9A948C] focus:outline-none focus:border-[#f59e0b] transition-colors resize-none"
              placeholder={activeGoalData?.placeholder}
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
            />
          </div>
        </div>

        {/* CTA */}
        <button
          onClick={() => handleContinue()}
          disabled={!selectedGoal || isSubmitting}
          className="w-full bg-[#f59e0b] hover:bg-[#d97706] disabled:bg-[#D5CBC0] disabled:opacity-50 text-black font-bold rounded-lg py-4 transition-all mt-6 shadow-[0_5px_15px_rgba(0,0,0,0.3)]"
        >
          {isSubmitting ? "Finalizing Strategic Direction..." : "Continue"}
        </button>

      </div>

      {/* METRIC VALIDATION MODAL */}
      {showMetricModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="w-full max-w-sm bg-[#262626] border border-[#D5CBC0] rounded-2xl p-8 shadow-2xl space-y-6">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-12 h-12 bg-[#FBE9DE] border border-[#D97757] rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-[#D97757]" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-bold text-[#2A2622]">Add a metric?</h3>
                <p className="text-sm text-[#6B655E]">RaptorFlow works significantly better when we have a quantitative target to aim for.</p>
              </div>
            </div>
            
            <div className="flex flex-col gap-3">
              <button 
                onClick={() => setShowMetricModal(false)}
                className="w-full bg-[#f59e0b] hover:bg-[#d97706] text-black font-bold py-3 rounded-lg transition-all"
              >
                Add a metric
              </button>
              <button 
                onClick={() => handleContinue(true)}
                className="w-full text-[#6B655E] hover:text-[#2A2622] text-sm py-2 transition-colors"
              >
                Skip anyway
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
