"use client";

import { useEffect, useMemo, useState } from "react";
import type { RICP } from "@/types/foundation";
import { cohortsService } from "@/services/cohorts.service";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { MoveCategory, MoveBriefData, ExecutionDay, MOVE_CATEGORIES } from "./types";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { ArrowRight, Check, Clock, Sparkles, Target, Users } from "lucide-react";
import { cn } from "@/lib/utils";
import { MoveCategoryIcon } from "./MoveCategoryIcon";

interface MoveCreateWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (data: {
    category: MoveCategory;
    context: string;
    brief: MoveBriefData;
    execution: ExecutionDay[];
  }) => void;
}

type WizardStep = "objective" | "context" | "clarify" | "preview";

type CohortChoice = {
  id: string;
  name: string;
  description: string;
  ricp?: RICP;
};

const GENERAL_AUDIENCE_ID = "__general__";

const CLARIFICATION_QUESTIONS = [
  {
    id: "resistance",
    question: "Why haven't they bought yet?",
    placeholder: "e.g. They think it's too expensive...",
  },
  {
    id: "offer",
    question: "What is the core offer for this move?",
    placeholder: "e.g. Free audit call...",
  },
  {
    id: "outcome",
    question: "What is the ideal outcome?",
    placeholder: "e.g. 10 qualified demos booked...",
  },
];

export function MoveCreateWizard({ isOpen, onClose, onComplete }: MoveCreateWizardProps) {
  const { workspaceId } = useWorkspace();

  const [step, setStep] = useState<WizardStep>("objective");
  const [category, setCategory] = useState<MoveCategory | null>(null);
  const [contextDesc, setContextDesc] = useState("");
  const [selectedCohort, setSelectedCohort] = useState<string>(GENERAL_AUDIENCE_ID);
  const [timeCommitment, setTimeCommitment] = useState<string | null>(null);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [customAnswer, setCustomAnswer] = useState("");
  const [brief, setBrief] = useState<MoveBriefData | null>(null);
  const [execution, setExecution] = useState<ExecutionDay[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [cohorts, setCohorts] = useState<CohortChoice[]>([]);
  const [cohortsLoading, setCohortsLoading] = useState(false);
  const [cohortsError, setCohortsError] = useState<string | null>(null);

  const cohortChoices = useMemo<CohortChoice[]>(
    () => [
      {
        id: GENERAL_AUDIENCE_ID,
        name: "General Audience",
        description: "No cohort selected (create ICPs in Foundation when ready).",
      },
      ...cohorts,
    ],
    [cohorts]
  );

  // Reset wizard state when closing.
  useEffect(() => {
    if (isOpen) return;
    setStep("objective");
    setCategory(null);
    setContextDesc("");
    setSelectedCohort(GENERAL_AUDIENCE_ID);
    setTimeCommitment(null);
    setCurrentQ(0);
    setAnswers({});
    setCustomAnswer("");
    setBrief(null);
    setExecution([]);
    setIsLoading(false);
    setCohortsError(null);
  }, [isOpen]);

  // Load cohorts (ICPs) when the wizard opens.
  useEffect(() => {
    if (!isOpen) return;

    if (!workspaceId) {
      setCohorts([]);
      setCohortsError("Workspace not initialized");
      return;
    }

    let cancelled = false;
    setCohortsLoading(true);
    setCohortsError(null);

    void cohortsService
      .list(workspaceId)
      .then((ricps) => {
        if (cancelled) return;
        const choices: CohortChoice[] = (ricps || []).map((r) => ({
          id: r.id,
          name: r.name || "Untitled ICP",
          description: formatRicpShortDescription(r),
          ricp: r,
        }));
        setCohorts(choices);
      })
      .catch((e: any) => {
        if (cancelled) return;
        setCohorts([]);
        setCohortsError(e?.message || "Failed to load cohorts");
      })
      .finally(() => {
        if (cancelled) return;
        setCohortsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isOpen, workspaceId]);

  const handleNext = async () => {
    if (step === "objective" && category) {
      setStep("context");
      return;
    }

    if (step === "context" && contextDesc.trim()) {
      setStep("clarify");
      return;
    }

    if (step === "clarify") {
      const q = CLARIFICATION_QUESTIONS[currentQ];
      const ans = (answers[q.id] || customAnswer).trim();
      if (!ans) return;

      const nextAnswers = { ...answers, [q.id]: ans };
      setAnswers(nextAnswers);
      setCustomAnswer("");

      if (currentQ < CLARIFICATION_QUESTIONS.length - 1) {
        setCurrentQ((prev) => prev + 1);
        return;
      }

      setIsLoading(true);
      try {
        const selected = cohortChoices.find((c) => c.id === selectedCohort);
        const icpName = selected?.name || "General Audience";

        const b = buildTemplateBrief({
          category: category!,
          context: contextDesc,
          icpName,
          answers: nextAnswers,
          timeCommitment,
        });
        const exec = buildTemplateExecution({
          brief: b,
          context: contextDesc,
          icpName,
          answers: nextAnswers,
          timeCommitment,
        });

        setBrief(b);
        setExecution(exec);
        setStep("preview");
      } finally {
        setIsLoading(false);
      }

      return;
    }

    if (step === "preview") {
      onComplete({ category: category!, context: contextDesc, brief: brief!, execution });
      onClose();
    }
  };

  const handleBack = () => {
    if (step === "context") setStep("objective");
    else if (step === "clarify") {
      if (currentQ > 0) {
        setCurrentQ((p) => p - 1);
        setCustomAnswer(answers[CLARIFICATION_QUESTIONS[currentQ - 1].id] || "");
      } else {
        setStep("context");
      }
    } else if (step === "preview") {
      setStep("clarify");
      setCurrentQ(CLARIFICATION_QUESTIONS.length - 1);
    }
  };

  const isNextDisabled = () => {
    if (step === "objective") return !category;
    if (step === "context") return contextDesc.trim().length <= 3;
    if (step === "clarify") {
      return !customAnswer.trim() && !(answers[CLARIFICATION_QUESTIONS[currentQ].id] || "").trim();
    }
    return false;
  };

  return (
    <BlueprintModal
      isOpen={isOpen}
      onClose={onClose}
      title={
        step === "objective"
          ? "Select Move Type"
          : step === "context"
            ? "Target and Context"
            : step === "clarify"
              ? "Refine Strategy"
              : "Ready to Launch"
      }
      size="lg"
      className="backdrop-blur-sm"
      footer={
        <div className="flex items-center justify-between w-full">
          <div className="flex gap-1">
            {["objective", "context", "clarify", "preview"].map((s, i) => {
              const currentIdx = ["objective", "context", "clarify", "preview"].indexOf(step);
              return (
                <div
                  key={s}
                  className={cn(
                    "w-2 h-2 rounded-full transition-colors",
                    i <= currentIdx ? "bg-[var(--ink)]" : "bg-[var(--surface-subtle)]"
                  )}
                />
              );
            })}
          </div>

          <div className="flex gap-3">
            {step !== "objective" && (
              <button
                onClick={handleBack}
                className="px-4 py-2 text-sm text-[var(--muted)] hover:text-[var(--ink)] transition-colors"
              >
                Back
              </button>
            )}
            <button
              onClick={handleNext}
              disabled={isNextDisabled() || isLoading}
              className={cn(
                "flex items-center gap-2 px-6 py-2 rounded-[var(--radius)] text-sm font-medium transition-all",
                isNextDisabled() || isLoading
                  ? "bg-[var(--surface-subtle)] text-[var(--muted)] cursor-not-allowed"
                  : "bg-[var(--ink)] text-white hover:bg-[var(--ink)]/90 shadow-md"
              )}
            >
              {isLoading ? (
                <>Processing...</>
              ) : step === "preview" ? (
                <>
                  <Check size={16} /> Launch Move
                </>
              ) : (
                <>
                  <span className="mr-1">Next</span> <ArrowRight size={16} />
                </>
              )}
            </button>
          </div>
        </div>
      }
    >
      <div className="min-h-[400px]">
        {/* STEP 1: OBJECTIVE */}
        {step === "objective" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(Object.keys(MOVE_CATEGORIES) as MoveCategory[]).map((catId) => {
              const cat = MOVE_CATEGORIES[catId];
              const isSelected = category === catId;
              return (
                <div
                  key={catId}
                  onClick={() => setCategory(catId)}
                  className={cn(
                    "relative p-4 rounded-[var(--radius)] border cursor-pointer transition-all duration-200 group",
                    isSelected
                      ? "border-[var(--ink)] bg-[var(--surface-subtle)] ring-1 ring-[var(--ink)]"
                      : "border-[var(--border)] hover:border-[var(--ink)] hover:shadow-md"
                  )}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="text-2xl">
                      <MoveCategoryIcon category={catId} size={24} />
                    </div>
                    {isSelected && <Check size={16} className="text-[var(--ink)]" />}
                  </div>
                  <h3 className="font-semibold text-[var(--ink)] mb-1">{cat.name}</h3>
                  <p className="text-xs text-[var(--muted)] mb-3">{cat.tagline}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {cat.useFor.slice(0, 2).map((tag, i) => (
                      <span
                        key={i}
                        className="px-1.5 py-0.5 rounded text-[10px] bg-[var(--paper)] border border-[var(--border)] text-[var(--muted)]"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* STEP 2: CONTEXT & ICP SELECTION */}
        {step === "context" && (
          <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
            {/* ICP Selection */}
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-3">
                Who specifically do you need to reach?
              </label>
              <div className="grid grid-cols-1 gap-3 max-h-[160px] overflow-y-auto pr-2 custom-scrollbar">
                {cohortChoices.map((cohort) => (
                  <button
                    key={cohort.id}
                    onClick={() => setSelectedCohort(cohort.id)}
                    className={cn(
                      "flex items-center justify-between p-3 rounded-[var(--radius)] border text-left transition-all",
                      selectedCohort === cohort.id
                        ? "border-[var(--ink)] bg-[var(--surface-subtle)] ring-1 ring-[var(--ink)]"
                        : "border-[var(--border)] bg-[var(--paper)] hover:border-[var(--blueprint)]"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-[var(--surface)] flex items-center justify-center text-[var(--muted)]">
                        <Users size={14} />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-[var(--ink)]">{cohort.name}</div>
                        <div className="text-xs text-[var(--muted)]">{cohort.description}</div>
                      </div>
                    </div>
                    {selectedCohort === cohort.id && <Check size={16} className="text-[var(--ink)]" />}
                  </button>
                ))}
              </div>
              <div className="mt-2 text-xs text-[var(--muted)]">
                {cohortsLoading && "Loading cohorts from Foundation..."}
                {!cohortsLoading && cohortsError && (
                  <span className="text-[var(--error)]">{cohortsError}</span>
                )}
              </div>
            </div>

            {/* Situation/Context */}
            <div>
              <label className="block text-sm font-medium text-[var(--ink)] mb-2">What's the situation?</label>
              <textarea
                value={contextDesc}
                onChange={(e) => setContextDesc(e.target.value)}
                placeholder="e.g. We are launching a new feature next week and need to build hype..."
                className="w-full h-24 p-4 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--paper)] focus:outline-none focus:border-[var(--ink)] text-sm resize-none"
              />
            </div>

            {/* Time Commitment */}
            <div className="flex items-center gap-4 p-4 rounded-[var(--radius)] bg-[var(--surface-subtle)] border border-[var(--border)]">
              <Clock className="text-[var(--muted)]" />
              <div>
                <h4 className="text-sm font-medium text-[var(--ink)]">Time Commitment</h4>
                <p className="text-xs text-[var(--muted)]">How much time can you dedicate daily?</p>
              </div>
              <div className="flex gap-2 ml-auto">
                {["15m", "30m", "1h+"].map((t) => (
                  <button
                    key={t}
                    onClick={() => setTimeCommitment(t)}
                    className={cn(
                      "px-3 py-1.5 text-xs font-medium rounded transition-colors",
                      timeCommitment === t
                        ? "bg-[var(--ink)] text-white"
                        : "bg-[var(--paper)] border border-[var(--border)] hover:border-[var(--ink)]"
                    )}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: CLARIFY */}
        {step === "clarify" && (
          <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-[var(--surface-subtle)] flex items-center justify-center shrink-0">
                <Sparkles size={18} className="text-[var(--ink-secondary)]" />
              </div>
              <div className="space-y-4 flex-1">
                <div className="bg-[var(--surface-subtle)] p-4 rounded-[var(--radius)] rounded-tl-none relative">
                  <p className="text-sm text-[var(--ink)] font-medium">{CLARIFICATION_QUESTIONS[currentQ].question}</p>
                  <div className="absolute -left-2 top-4 w-2 h-2 bg-[var(--surface-subtle)] [clip-path:polygon(100%_0,0_0,100%_100%)]" />
                </div>
                <input
                  type="text"
                  value={customAnswer}
                  onChange={(e) => setCustomAnswer(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && customAnswer.trim() && handleNext()}
                  placeholder={CLARIFICATION_QUESTIONS[currentQ].placeholder}
                  className="w-full p-3 border-b-2 border-[var(--border)] bg-transparent focus:outline-none focus:border-[var(--ink)] transition-colors"
                  autoFocus
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: PREVIEW */}
        {step === "preview" && brief && (
          <div className="space-y-6 animate-in zoom-in-95 duration-300">
            <div className="text-center mb-8">
              <div className="w-16 h-16 rounded-full bg-[var(--success)]/10 flex items-center justify-center mx-auto mb-4 border border-[var(--success)]/20 shadow-lg shadow-[var(--success)]/10">
                <span className="text-3xl">
                  <MoveCategoryIcon category={brief.category} size={32} />
                </span>
              </div>
              <h2 className="text-2xl font-serif text-[var(--ink)] mb-2">{brief.name}</h2>
              <p className="text-[var(--muted)] max-w-md mx-auto">{brief.goal}</p>
            </div>

            {/* Strategy Card */}
            <div className="p-4 border border-[var(--border)] rounded-[var(--radius)] bg-[var(--paper)] mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Target size={14} className="text-[var(--blueprint)]" />
                <span className="text-xs font-bold uppercase tracking-wider text-[var(--blueprint)]">Strategy Lock</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium text-[var(--ink)]">Targeting {brief.icp}</div>
                <div className="text-xs text-[var(--muted)]">{brief.duration} Days Execution</div>
              </div>
            </div>

            {/* Plan Preview */}
            <div className="bg-[var(--surface-subtle)] rounded-[var(--radius)] border border-[var(--border)] overflow-hidden">
              <div className="px-4 py-3 border-b border-[var(--border)] flex justify-between items-center bg-[var(--surface)]">
                <div className="text-xs font-medium text-[var(--ink)] uppercase tracking-wider">Execution Plan Generated</div>
                <div className="text-[10px] text-[var(--success)] font-bold flex items-center gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)]" />
                  READY
                </div>
              </div>
              <div className="p-2 space-y-1">
                {execution.slice(0, 3).map((day, i) => (
                  <div key={i} className="flex items-center gap-3 p-2 text-xs">
                    <div className="w-6 text-[var(--muted)] font-medium">Day {day.day}</div>
                    <div className="flex-1 truncate text-[var(--ink)]">{day.pillarTask.title}</div>
                  </div>
                ))}
                {execution.length > 3 && (
                  <div className="px-2 py-1 text-[10px] text-[var(--muted)] italic text-center">
                    + {execution.length - 3} more days planned
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </BlueprintModal>
  );
}

function formatRicpShortDescription(ricp: RICP): string {
  const bits: string[] = [];
  if (ricp.demographics?.role) bits.push(ricp.demographics.role);
  if (ricp.demographics?.stage) bits.push(ricp.demographics.stage);
  if (ricp.demographics?.location) bits.push(ricp.demographics.location);
  return bits.length ? bits.join(" | ") : "Foundation ICP";
}

type BriefTemplateInput = {
  category: MoveCategory;
  context: string;
  icpName: string;
  answers: Record<string, string>;
  timeCommitment: string | null;
};

function buildTemplateBrief(input: BriefTemplateInput): MoveBriefData {
  const outcome = (input.answers.outcome || "").trim();
  const offer = (input.answers.offer || "").trim();
  const resistance = (input.answers.resistance || "").trim();

  const defaultGoal = MOVE_CATEGORIES[input.category].goal;
  const goal = outcome || defaultGoal;

  const name = outcome
    ? `${MOVE_CATEGORIES[input.category].name}: ${truncate(outcome, 42)}`
    : `${MOVE_CATEGORIES[input.category].name} Sprint`;

  const metricsByCategory: Record<MoveCategory, string[]> = {
    ignite: ["Reach", "Signups", "Demo requests"],
    capture: ["Leads", "Meetings booked", "Conversion rate"],
    authority: ["Profile views", "Inbound mentions", "Newsletter subscribers"],
    repair: ["Sentiment shift", "Support volume", "Churn risk"],
    rally: ["Activation", "Referrals", "Repeat usage"],
  };

  return {
    name,
    category: input.category,
    goal,
    tone: "Professional & Direct",
    duration: 7,
    icp: input.icpName,
    strategy: [
      `Target: ${input.icpName}.`,
      offer ? `Offer: ${offer}.` : null,
      resistance ? `Address: ${truncate(resistance, 70)}.` : null,
      `Context: ${truncate(input.context, 90)}.`,
    ]
      .filter(Boolean)
      .join(" "),
    metrics: metricsByCategory[input.category],
  };
}

type ExecutionTemplateInput = {
  brief: MoveBriefData;
  context: string;
  icpName: string;
  answers: Record<string, string>;
  timeCommitment: string | null;
};

function buildTemplateExecution(input: ExecutionTemplateInput): ExecutionDay[] {
  const offer = (input.answers.offer || "").trim();
  const resistance = (input.answers.resistance || "").trim();
  const outcome = (input.answers.outcome || "").trim();

  const phases = ["Setup", "Asset", "Launch", "Distribution", "Follow-up", "Optimize", "Review"];

  const pillarTitlesByCategory: Record<MoveCategory, string[]> = {
    ignite: [
      "Define the hook and single CTA",
      "Draft the flagship post + 2 teaser cuts",
      "Launch: publish the flagship + pin it",
      "Repurpose into 5 micro-cuts and schedule",
      "Partner push: 10 targeted outreaches",
      "Objection handling: FAQ + replies",
      "Review results and lock the next sprint",
    ],
    capture: [
      "Define ICP + qualification and target list",
      `Build the offer page${offer ? `: ${truncate(offer, 32)}` : ""}`,
      "Write the outbound sequence (3 touches)",
      "Send 25 outreaches and log responses",
      "Follow up + book calls (calendar link)",
      "Tighten the pitch based on replies",
      "Review pipeline + double down on what hit",
    ],
    authority: [
      "Pick a POV angle and proof points",
      "Write a long-form post (with a sharp claim)",
      "Publish + engage with comments for 30 mins",
      "Turn the POV into a carousel/thread",
      "Secure 3 distribution partners (shares)",
      "Publish a case-style breakdown",
      "Review signals + outline next topics",
    ],
    repair: [
      "Write the truth statement (what happened, what changes)",
      "Create the remediation plan checklist",
      "Publish update + link to remediation",
      "Reach out to 10 affected users personally",
      "Collect feedback + close the loop publicly",
      "Monitor sentiment + address new objections",
      "Review impact + set prevention guardrails",
    ],
    rally: [
      "Define the win moment and retention hook",
      "Create the activation nudge (email/DM/post)",
      "Run a community touchpoint (prompt/event)",
      "Spotlight 3 user wins and tag them",
      "Launch a referral/UGC ask with incentive",
      "Follow-up to high-intent responders",
      "Review engagement + set next loop",
    ],
  };

  const clusterCount = input.timeCommitment === "15m" ? 1 : input.timeCommitment === "1h+" ? 3 : 2;

  const buildClusterActions = (day: number): { title: string; channel: string }[] => {
    const base: { title: string; channel: string }[] = [
      { title: `Prep supporting asset for Day ${day}`, channel: "content" },
      { title: "Distribute to your primary channel", channel: "linkedin" },
      { title: "Log results + note what to tweak", channel: "ops" },
    ];
    return base.slice(0, clusterCount);
  };

  const buildNetworkAction = (day: number): { title: string; channel: string } => {
    const target = input.icpName || "prospects";
    const msg = resistance ? ` addressing "${truncate(resistance, 48)}"` : "";
    return {
      title: `DM 5 ${target}${msg} (Day ${day})`,
      channel: "dm",
    };
  };

  return Array.from({ length: input.brief.duration }).map((_, i) => {
    const day = i + 1;
    const phase = phases[i] || "Execution";
    const pillarTitle = pillarTitlesByCategory[input.brief.category][i] || `Execute Day ${day}`;

    const headerBits = [
      outcome ? `Outcome: ${truncate(outcome, 52)}` : null,
      offer ? `Offer: ${truncate(offer, 52)}` : null,
    ]
      .filter(Boolean)
      .join(" | ");

    const network = buildNetworkAction(day);

    return {
      day,
      phase,
      pillarTask: {
        id: `pillar-${day}`,
        title: pillarTitle,
        description: headerBits || truncate(input.context, 120),
        status: "pending",
      },
      clusterActions: buildClusterActions(day).map((t, idx) => ({
        id: `cluster-${day}-${idx + 1}`,
        title: t.title,
        description: "",
        status: "pending",
        channel: t.channel,
      })),
      networkAction: {
        id: `network-${day}`,
        title: network.title,
        description: "",
        status: "pending",
        channel: network.channel,
      },
    };
  });
}

function truncate(value: string, max: number): string {
  const v = value.trim();
  if (v.length <= max) return v;
  return v.slice(0, Math.max(0, max - 3)).trimEnd() + "...";
}

export default MoveCreateWizard;
