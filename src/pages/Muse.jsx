import React, { useMemo, useState, useEffect } from "react";
import {
  Brain,
  Wand2,
  Sparkles,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  CheckCircle,
  CheckCircle2,
  Copy,
  Layers,
  BookOpen,
  PenTool,
  Upload,
  AlertTriangle,
  Zap,
  Clock,
} from "lucide-react";
import { useSearchParams } from "react-router-dom";

// Fallback className joiner to avoid dependency on utils
const cn = (...classes) => classes.filter(Boolean).join(" ");

const MOCK_TASKS = [
  {
    id: "t1",
    title: "DM block: 20 sends",
    channel: "LinkedIn",
    cohort: "Corporate / Enterprise",
    goal: "Conversion & Pipeline",
    status: "today",
    prompt:
      "Write 5 LinkedIn connection request templates for Corporate/Enterprise buyers. Tone: proof-led, respectful, concise. CTA: 'open to a 7-min audit?'",
  },
  {
    id: "t2",
    title: "Short-form video: Problem/Agitate",
    channel: "TikTok",
    cohort: "Early Adopters",
    goal: "Attention & Engagement",
    status: "today",
    prompt:
      "Write a 20s TikTok script that opens with the hidden cost of waiting to implement. Use a sharp hook, one visual cue, one CTA.",
  },
  {
    id: "t3",
    title: "Email: Proof drop",
    channel: "Email",
    cohort: "Brand Loyalists",
    goal: "Authority & Brand Positioning",
    status: "upcoming",
    prompt:
      "Draft an email that shares one proof story with a single CTA to book a slot. Keep under 120 words. Lead with outcome > method.",
  },
  {
    id: "t4",
    title: "Story sequence",
    channel: "Instagram Stories",
    cohort: "Price Sensitive",
    goal: "Retention & Reactivation",
    status: "done",
    prompt:
      "Create a 3-frame story sequence. Frame 1: pain. Frame 2: quick proof. Frame 3: urgency CTA.",
  },
  {
    id: "t5",
    title: "Insight test outline",
    channel: "Blog",
    cohort: "Corporate",
    goal: "Insight & Learning",
    status: "upcoming",
    prompt:
      "Outline an A/B test to learn which positioning lands better: 'risk mitigation' vs 'speed to value'. Include hypothesis, metric, and sample copy.",
  },
];

const PROMPTS = [
  {
    id: "sharpen",
    label: "Sharpen Hook",
    helper: "Make the first 3 seconds impossible to ignore.",
    fn: (task) =>
      `Sharpen the hook for ${task?.channel || "this channel"} so it makes the audience stop in 3 seconds. Keep it concise and specific to ${task?.cohort ||
        "the cohort"}.`,
  },
  {
    id: "proof",
    label: "Add Proof",
    helper: "Inject 1 concrete proof point.",
    fn: (task) =>
      `Add one proof element (number, quote, or artifact) that ${task?.cohort ||
        "this cohort"} will trust. Keep tone aligned to ${task?.goal}.`,
  },
  {
    id: "cta",
    label: "Tighten CTA",
    helper: "Remove friction and make the next step obvious.",
    fn: (task) =>
      `Rewrite the CTA so it's single-step, low-friction, and native to ${task?.channel ||
        "the channel"}. Mention expected outcome in 10 words or less.`,
  },
];

const VARIATIONS = [
  {
    id: "direct",
    label: "Direct & ROI-led",
    body:
      "Cut your ops drag by 30% in 14 days. If we miss, you pay $0. Reply “show me” and I’ll share the teardown.",
  },
  {
    id: "story",
    label: "Story & Proof",
    body:
      "Last quarter we turned a stalled pipeline into 17 meetings in 10 days. They just swapped the opener. Want to see the before/after?",
  },
  {
    id: "urgency",
    label: "Urgency & Scarcity",
    body:
      "Two slots left this week for a 15-min audit. If we don’t find $5k/month to reclaim, we’ll write you a check. Want one?",
  },
];

const SIGNALS = [
  {
    id: "s1",
    title: "Face-led hooks",
    detail: "Hooks with a human face are driving 2.3x replies vs text-only.",
    confidence: "high",
    impact: "medium",
  },
  {
    id: "s2",
    title: "DM follow-through",
    detail: "When a DM block is followed by a proof asset within 4 hours, conversion lifts by +18%.",
    confidence: "medium",
    impact: "high",
  },
];

const CANVA_LINK = "https://www.canva.com";

const STATUS_FILTERS = [
  { id: "all", label: "All" },
  { id: "today", label: "Today" },
  { id: "upcoming", label: "Upcoming" },
  { id: "done", label: "Done" },
];

export default function Muse() {
  const [searchParams] = useSearchParams();
  const [activeTask, setActiveTask] = useState(MOCK_TASKS[0]);
  const [draft, setDraft] = useState(MOCK_TASKS[0].prompt);
  const [statusFilter, setStatusFilter] = useState("today");
  const [selectedSignal, setSelectedSignal] = useState(SIGNALS[0]);

  const filteredTasks = useMemo(() => {
    if (statusFilter === "all") return MOCK_TASKS;
    return MOCK_TASKS.filter((t) => t.status === statusFilter);
  }, [statusFilter]);

  const applyPrompt = (prompt) => {
    const insertion = prompt.fn(activeTask);
    setDraft((prev) => `${prev ? `${prev}\n\n` : ""}${insertion}`);
  };

  const handleVariation = (body) => setDraft(body);

  const handleTaskSelect = (task) => {
    setActiveTask(task);
    setDraft(task.prompt);
  };

  // hydrate context from Matrix/Moves/Cohorts via query params
  useEffect(() => {
    const moveId = searchParams.get("moveId");
    const cohortId = searchParams.get("cohortId");
    const pattern = searchParams.get("pattern");
    if (cohortId) {
      setActiveTask((prev) => ({ ...prev, cohort: cohortId }));
    }
    if (pattern) {
      setDraft((prev) => `${prev}\n\nPattern to scale: ${pattern}`);
    }
    const assetId = searchParams.get("assetId");
    if (moveId) setDraft((prev) => `${prev}\n\nContext from Move ${moveId}`);
    if (assetId) setDraft((prev) => `${prev}\n\nSource asset: ${assetId}`);
  }, [searchParams]);

  return (
    <div className="flex h-full flex-col bg-white">
      <div className="border-b border-neutral-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <button
              className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-neutral-200 text-neutral-500 hover:text-neutral-900"
              aria-label="Back"
            >
              <ArrowLeft size={18} />
            </button>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-neutral-400">
                Creative Workspace
              </p>
              <h1 className="text-xl font-semibold text-neutral-900">Muse</h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a
              href={CANVA_LINK}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-2 text-sm font-medium text-neutral-800 hover:border-neutral-300"
            >
              <PenTool size={16} /> Open Canva
            </a>
            <button className="inline-flex items-center gap-2 rounded-full bg-black px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-neutral-900">
              <Sparkles size={16} /> New from brief
            </button>
          </div>
        </div>
      </div>

      <div className="mx-auto flex w-full max-w-6xl flex-1 gap-6 px-6 py-6">
        {/* Left: Queue + signals */}
        <div className="w-full max-w-sm space-y-4">
          <div className="rounded-2xl border border-neutral-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-neutral-100 px-4 py-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.15em] text-neutral-400">
                  From Moves
                </p>
                <h3 className="text-base font-semibold text-neutral-900">
                  Queue
                </h3>
              </div>
              <div className="flex gap-2">
                {STATUS_FILTERS.map((filter) => (
                  <button
                    key={filter.id}
                    onClick={() => setStatusFilter(filter.id)}
                    className={cn(
                      "rounded-full px-3 py-1 text-xs font-semibold transition-colors",
                      statusFilter === filter.id
                        ? "bg-neutral-900 text-white"
                        : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
                    )}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="divide-y divide-neutral-100">
              {filteredTasks.map((task) => (
                <button
                  key={task.id}
                  onClick={() => handleTaskSelect(task)}
                  className={cn(
                    "w-full px-4 py-3 text-left transition-colors",
                    activeTask?.id === task.id
                      ? "bg-neutral-50"
                      : "hover:bg-neutral-50"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-semibold text-neutral-500">
                      <Layers size={14} />
                      <span>{task.goal}</span>
                    </div>
                    <span className="text-[11px] font-semibold uppercase text-neutral-400">
                      {task.status}
                    </span>
                  </div>
                  <p className="mt-2 text-sm font-semibold text-neutral-900">
                    {task.title}
                  </p>
                  <p className="mt-1 text-xs text-neutral-500">
                    {task.channel} • {task.cohort}
                  </p>
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-neutral-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-neutral-100 px-4 py-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.15em] text-neutral-400">
                  Signals
                </p>
                <h3 className="text-base font-semibold text-neutral-900">
                  From Matrix
                </h3>
              </div>
              <div className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                Live
              </div>
            </div>
            <div className="divide-y divide-neutral-100">
              {SIGNALS.map((signal) => (
                <button
                  key={signal.id}
                  onClick={() => setSelectedSignal(signal)}
                  className={cn(
                    "w-full px-4 py-3 text-left transition-colors",
                    selectedSignal?.id === signal.id
                      ? "bg-emerald-50/60"
                      : "hover:bg-neutral-50"
                  )}
                >
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
                    <CheckCircle2
                      size={14}
                      className={signal.impact === "high" ? "text-emerald-600" : "text-amber-500"}
                    />
                    <span className="text-neutral-500">{signal.title}</span>
                  </div>
                  <p className="mt-2 text-sm text-neutral-800">{signal.detail}</p>
                  <p className="mt-2 text-xs text-neutral-500">
                    Confidence: {signal.confidence} • Impact: {signal.impact}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: workspace */}
        <div className="flex-1 space-y-4">
          <div className="flex flex-wrap gap-2 text-xs text-neutral-500">
            <span className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-3 py-1 font-semibold">
              <Layers size={14} /> {activeTask.goal}
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-3 py-1 font-semibold">
              <BookOpen size={14} /> {activeTask.channel}
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-3 py-1 font-semibold">
              <Zap size={14} /> {activeTask.cohort}
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-3 py-1 font-semibold">
              <Clock size={14} /> Status: {activeTask.status}
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm lg:grid-cols-3">
            <div className="lg:col-span-2 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-neutral-400">
                    Draft
                  </p>
                  <h2 className="text-lg font-semibold text-neutral-900">
                    {activeTask.title}
                  </h2>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => navigator.clipboard?.writeText(draft || "")}
                    className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-700 hover:border-neutral-300"
                  >
                    <Copy size={14} /> Copy
                  </button>
                  <button className="inline-flex items-center gap-2 rounded-full bg-emerald-600 px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-emerald-500">
                    <CheckCircle size={14} /> Mark ready
                  </button>
                </div>
              </div>
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                className="min-h-[260px] w-full rounded-xl border border-neutral-200 bg-neutral-50/80 px-4 py-3 text-sm text-neutral-900 shadow-inner focus:border-neutral-300 focus:outline-none"
              />
              <div className="flex flex-wrap gap-2">
                {PROMPTS.map((prompt) => (
                  <button
                    key={prompt.id}
                    onClick={() => applyPrompt(prompt)}
                    className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-800 hover:border-neutral-300"
                  >
                    <Wand2 size={14} /> {prompt.label}
                    <span className="text-[11px] font-normal text-neutral-500">
                      {prompt.helper}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-col gap-3 rounded-xl border border-neutral-100 bg-neutral-50 p-3">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
                <Brain size={14} /> Variations
              </div>
              {VARIATIONS.map((variation) => (
                <button
                  key={variation.id}
                  onClick={() => handleVariation(variation.body)}
                  className="rounded-lg border border-transparent bg-white px-3 py-2 text-left text-sm text-neutral-800 shadow-sm transition hover:border-neutral-200"
                >
                  <div className="flex items-center gap-2 text-xs font-semibold text-neutral-500">
                    <Sparkles size={14} /> {variation.label}
                  </div>
                  <p className="mt-2 text-sm leading-snug text-neutral-800">
                    {variation.body}
                  </p>
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div className="rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
                <PenTool size={14} /> Templates
              </div>
              <div className="mt-3 space-y-3">
                <button
                  onClick={() => setDraft(MOCK_TASKS[0].prompt)}
                  className="flex w-full items-center justify-between rounded-lg border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-800 hover:border-neutral-300"
                >
                  Short-form video <ArrowRight size={14} />
                </button>
                <button
                  onClick={() => setDraft(MOCK_TASKS[1].prompt)}
                  className="flex w-full items-center justify-between rounded-lg border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-800 hover:border-neutral-300"
                >
                  Outbound DM <ArrowRight size={14} />
                </button>
                <button
                  onClick={() => setDraft(MOCK_TASKS[2].prompt)}
                  className="flex w-full items-center justify-between rounded-lg border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-800 hover:border-neutral-300"
                >
                  Email proof drop <ArrowRight size={14} />
                </button>
              </div>
            </div>

            <div className="rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
                <Upload size={14} /> Assets
              </div>
              <p className="mt-2 text-sm text-neutral-700">
                Planning inside RaptorFlow, production in Canva.
              </p>
              <a
                href={CANVA_LINK}
                target="_blank"
                rel="noreferrer"
                className="mt-3 inline-flex items-center gap-2 rounded-full bg-black px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-neutral-900"
              >
                Open Canva <ArrowUpRight size={14} />
              </a>
            </div>

            <div className="rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
                <AlertTriangle size={14} /> Guardrails
              </div>
              <ul className="mt-3 space-y-2 text-sm text-neutral-700">
                <li>Stay within the cohort tone; avoid jargon bloat.</li>
                <li>One CTA per asset; remove extra links.</li>
                <li>Proof > promises. Name a number or artifact.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
