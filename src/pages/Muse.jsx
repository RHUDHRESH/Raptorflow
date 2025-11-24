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
];

const PROMPTS = [
  {
    id: "sharpen",
    label: "Sharpen Hook",
    helper: "Make it impossible to ignore in 3s",
    fn: (task) =>
      `Sharpen the hook for ${task?.channel || "this channel"} so the audience stops scrolling. Keep it concise for ${task?.cohort ||
        "the cohort"}.`,
  },
  {
    id: "proof",
    label: "Layer Proof",
    helper: "Add one convincing evidence point",
    fn: (task) =>
      `Add one proof detail (number, quote, artifact) relevant to ${task?.cohort ||
        "this cohort"} while keeping tone in line with ${task?.goal}.`,
  },
  {
    id: "cta",
    label: "Tighten CTA",
    helper: "Make the next step frictionless",
    fn: (task) =>
      `Rewrite the CTA so it's one clear action, ties back to ${task?.goal}, and uses the natural language of ${task?.channel ||
        "the channel"}.`,
  },
];

const VARIATIONS = [
  {
    id: "direct",
    label: "Direct & ROI",
    body:
      "Cut ops drag by 30% in 14 days. If it misses, we pay. Reply 'show me' and I’ll share the teardown.",
  },
  {
    id: "story",
    label: "Story & Proof",
    body:
      "We turned a stalled pipeline into 17 meetings in 10 days by swapping the opener. Want the before/after?",
  },
];

const SIGNALS = [
  {
    id: "s1",
    title: "Face-led hooks",
    detail: "Human faces are pulling 2.3x replies vs text-only hooks this week.",
    confidence: "high",
    impact: "medium",
  },
  {
    id: "s2",
    title: "DM follow-through",
    detail: "Sending proof assets within 4h of a DM block lifts conversion +18%.",
    confidence: "medium",
    impact: "high",
  },
];

const CANVA_LINK = "https://www.canva.com";

const STATUS_FILTERS = [
  { id: "all", label: "All" },
  { id: "today", label: "Today" },
  { id: "upcoming", label: "Upcoming" },
];

const SummaryCard = ({ label, value, helper, accent }) => (
  <div className="rounded-3xl border border-neutral-200 bg-gradient-to-br from-white to-neutral-100 p-4 shadow-sm">
    <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-neutral-400">{label}</p>
    <p className="text-3xl font-semibold text-neutral-900">{value}</p>
    {helper && <p className="text-xs text-neutral-500">{helper}</p>}
    {accent && <span className="mt-2 inline-flex rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white">{accent}</span>}
  </div>
);

const SectionCard = ({ title, subtitle, accent, className, children }) => (
  <div className={cn("runway-card border border-neutral-200 bg-white shadow-sm p-4", className)}>
    {(title || subtitle || accent) && (
      <div className="flex items-center justify-between mb-3">
        <div>
          {title && <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-neutral-400">{title}</p>}
          {subtitle && <h3 className="text-base font-semibold text-neutral-900">{subtitle}</h3>}
        </div>
        {accent && (
          <span className="text-[10px] font-semibold uppercase tracking-[0.25em] text-neutral-500">{accent}</span>
        )}
      </div>
    )}
    {children}
  </div>
);

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

  useEffect(() => {
    const moveId = searchParams.get("moveId");
    const cohortId = searchParams.get("cohortId");
    if (cohortId) {
      setActiveTask((prev) => ({ ...prev, cohort: cohortId }));
    }
    if (moveId) {
      setDraft((prev) => `${prev}\n\nContext from Move ${moveId}`);
    }
  }, [searchParams]);

  return (
    <div className="flex min-h-screen flex-col bg-neutral-50">
      <div className="border-b border-neutral-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex flex-col gap-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.4em] text-neutral-400">Creative</p>
            <h1 className="text-2xl font-semibold text-neutral-900">Muse</h1>
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
            <button className="inline-flex items-center gap-2 rounded-full bg-black px-4 py-2 text-sm font-semibold text-white transition hover:bg-neutral-900">
              <Sparkles size={16} /> New from brief
            </button>
          </div>
        </div>
      </div>

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <SummaryCard label="Active task" value={activeTask.title} helper={activeTask.channel} accent={activeTask.status} />
          <SummaryCard label="Draft quality" value="High" helper="Thanks to on-brand proof" accent="Updated" />
          <SummaryCard label="Signal" value={selectedSignal.title} helper={`Impact: ${selectedSignal.impact}`} accent={selectedSignal.confidence} />
        </div>
        <main className="grid gap-6 lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)_minmax(0,320px)]">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,300px)_minmax(0,1fr)_minmax(0,320px)]">
          {/* Left column */}
          <div className="space-y-4">
            <SectionCard title="From Moves" subtitle="Queue">
              <div className="flex flex-wrap gap-2 mb-3">
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
              <div className="divide-y divide-neutral-100">
                {filteredTasks.map((task) => (
                  <button
                    key={task.id}
                    onClick={() => handleTaskSelect(task)}
                    className={cn(
                      "w-full px-4 py-3 text-left transition-colors",
                      activeTask?.id === task.id ? "bg-neutral-50" : "hover:bg-neutral-50"
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-[11px] font-semibold text-neutral-500">
                        <Layers size={14} />
                        <span>{task.goal}</span>
                      </div>
                      <span className="text-[11px] font-semibold uppercase text-neutral-400">{task.status}</span>
                    </div>
                    <p className="mt-2 text-sm font-semibold text-neutral-900">{task.title}</p>
                    <p className="mt-1 text-xs text-neutral-500">
                      {task.channel} • {task.cohort}
                    </p>
                  </button>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="Signals" subtitle="From Matrix" accent="Live">
              <p className="text-sm text-neutral-700 mb-2">{selectedSignal.detail}</p>
              <div className="flex flex-wrap gap-2 text-[11px] font-semibold uppercase text-neutral-400">
                <span>Impact: {selectedSignal.impact}</span>
                <span>Confidence: {selectedSignal.confidence}</span>
              </div>
              <div className="mt-4 flex flex-col gap-2 text-sm">
                {SIGNALS.map((signal) => (
                  <button
                    key={signal.id}
                    onClick={() => setSelectedSignal(signal)}
                    className={cn(
                      "text-left text-sm font-semibold transition-colors",
                      selectedSignal?.id === signal.id ? "text-neutral-900" : "text-neutral-500 hover:text-neutral-900"
                    )}
                  >
                    {signal.title}
                  </button>
                ))}
              </div>
            </SectionCard>
          </div>

          {/* Center workspace */}
          <div className="space-y-4">
            <SectionCard title="Workspace" subtitle="Live Draft">
              <div className="flex flex-wrap gap-3 text-xs text-neutral-500 mb-4">
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

              <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-neutral-400">Draft</p>
                      <h2 className="text-lg font-semibold text-neutral-900">{activeTask.title}</h2>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => navigator.clipboard?.writeText(draft || "")}
                        className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-700 hover:border-neutral-300"
                      >
                        <Copy size={14} /> Copy
                      </button>
                      <button className="inline-flex items-center gap-2 rounded-full bg-emerald-600 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-500">
                        <CheckCircle size={14} /> Mark ready
                      </button>
                    </div>
                  </div>
                  <textarea
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    className="min-h-[260px] w-full rounded-2xl border border-neutral-200 bg-neutral-50 px-4 py-3 text-sm text-neutral-900 shadow-inner focus:border-neutral-300 focus:outline-none"
                  />
                  <div className="flex flex-wrap gap-2">
                    {PROMPTS.map((prompt) => (
                      <button
                        key={prompt.id}
                        onClick={() => applyPrompt(prompt)}
                        className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-800 hover:border-neutral-300"
                      >
                        <Wand2 size={14} /> {prompt.label}
                        <span className="text-[11px] font-normal text-neutral-500">{prompt.helper}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="rounded-2xl border border-neutral-100 bg-neutral-50 p-3">
                    <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
                      <Brain size={14} /> Variations
                    </div>
                    <div className="mt-3 space-y-2">
                      {VARIATIONS.map((variation) => (
                        <button
                          key={variation.id}
                          onClick={() => handleVariation(variation.body)}
                          className="w-full rounded-xl border border-transparent bg-white px-3 py-2 text-left text-sm text-neutral-800 shadow-sm transition hover:border-neutral-200"
                        >
                          <div className="flex items-center gap-2 text-xs font-semibold text-neutral-500">
                            <Sparkles size={14} /> {variation.label}
                          </div>
                          <p className="mt-2 text-sm leading-snug text-neutral-800">{variation.body}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                  <SectionCard title="Active Signal" subtitle={selectedSignal.title}>
                    <p className="text-sm text-neutral-700">{selectedSignal.detail}</p>
                    <div className="flex flex-wrap gap-2 text-[11px] font-semibold uppercase text-neutral-400 mt-2">
                      <span>Impact: {selectedSignal.impact}</span>
                      <span>Confidence: {selectedSignal.confidence}</span>
                    </div>
                  </SectionCard>
                </div>
              </div>
            </SectionCard>
          </div>

          {/* Right column */}
          <div className="space-y-4">
            <SectionCard title="Templates" subtitle="Ready-made">
              <div className="space-y-3">
                {MOCK_TASKS.slice(0, 3).map((task) => (
                  <button
                    key={task.id}
                    onClick={() => setDraft(task.prompt)}
                    className="flex w-full items-center justify-between rounded-xl border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-800 hover:border-neutral-300"
                  >
                    {task.title}
                    <ArrowRight size={14} />
                  </button>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="Production" subtitle="Assets">
              <p className="text-sm text-neutral-700">
                Plan inside RaptorFlow, craft in Canva for polished output.
              </p>
              <a
                href={CANVA_LINK}
                target="_blank"
                rel="noreferrer"
                className="mt-3 inline-flex items-center gap-2 rounded-full bg-black px-3 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-neutral-900"
              >
                Open Canva
                <ArrowUpRight size={14} />
              </a>
            </SectionCard>

            <SectionCard title="Guardrails">
              <ul className="space-y-2 text-sm text-neutral-700">
                <li>Stay within the cohort tone—no jargon bloat.</li>
                <li>One CTA per asset; remove extra links.</li>
                <li>Proof over promises. Call out a number or artifact.</li>
              </ul>
            </SectionCard>
          </div>
        </div>
      </main>
    </div>
  );
}
