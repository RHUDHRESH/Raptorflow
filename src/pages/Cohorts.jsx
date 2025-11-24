import React, { useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle,
  Layout,
  Mail,
  MessageSquare,
  PenTool,
  Plus,
  RefreshCw,
  Sparkles,
  Trash2,
  UploadCloud,
  Users,
  Zap,
  X,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const INITIAL_COHORTS = [
  {
    id: "c1",
    name: "Founders – Early SaaS",
    role: "CEO / Founder",
    pain: "Scared of wasting budget, wants predictable pipeline.",
    values: ["ROI", "Speed", "No-fluff"],
    fears: ["Burning cash", "Looking amateur", "Missing market window"],
    patterns: ["Responds to raw data", "Hates generic agency talk"],
    channels: ["linkedin", "email"],
    stats: { conversion: "2.4%", status: "healthy", engagementScore: 85 },
  },
  {
    id: "c2",
    name: "Weekend Foodies",
    role: "Local Diner",
    pain: "Novelty-seeking, fear of missing out (FOMO).",
    values: ["Aesthetics", "Social Status", "Taste"],
    fears: ["Bad experience", "Boring weekend"],
    patterns: ["Loves staff BTS", "Ignores static food photos"],
    channels: ["instagram", "tiktok"],
    stats: { conversion: "5.1%", status: "healthy", engagementScore: 92 },
  },
  {
    id: "c3",
    name: "Office Lunch Crowd",
    role: "Corporate Manager",
    pain: "Stressful mornings, needs reliable healthy fuel.",
    values: ["Speed", "Consistency", "Health"],
    fears: ["Late for meeting", "Post-lunch crash", "Queueing"],
    patterns: ['Responds to "Skip the queue"', 'Clicks "Healthy Combo" offers'],
    channels: ["whatsapp", "email"],
    stats: { conversion: "0.8%", status: "dead", engagementScore: 12 },
  },
];

const statusStyles = {
  healthy: "bg-emerald-50 text-emerald-700 border-emerald-100",
  new: "bg-blue-50 text-blue-700 border-blue-100",
  dead: "bg-rose-50 text-rose-700 border-rose-100",
};

const cn = (...c) => c.filter(Boolean).join(" ");

const WizardWrapper = ({ title, steps, step, onClose, onNext, children }) => (
  <div className="fixed inset-0 z-50 flex justify-end bg-black/50 backdrop-blur">
    <div className="flex h-full w-full max-w-xl flex-col border-l border-neutral-200 bg-white shadow-2xl">
      <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-neutral-400">
            Wizard
          </p>
          <h2 className="text-xl font-semibold text-neutral-900">{title}</h2>
        </div>
        <button
          onClick={onClose}
          className="rounded-full border border-neutral-200 p-2 text-neutral-500 hover:text-neutral-900"
        >
          <X size={18} />
        </button>
      </div>
      <div className="h-1 bg-neutral-100">
        <div
          className="h-1 bg-neutral-900 transition-all"
          style={{ width: `${((step + 1) / steps.length) * 100}%` }}
        />
      </div>
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mb-6 text-sm font-mono text-neutral-500">
          0{step + 1} / 0{steps.length}
        </div>
        <h3 className="mb-4 text-2xl font-light text-neutral-900">
          {steps[step].title}
        </h3>
        {children}
      </div>
      <div className="flex items-center justify-between border-t border-neutral-200 px-6 py-4">
        <button
          onClick={onClose}
          className="text-sm font-semibold text-neutral-600 hover:text-neutral-900"
        >
          Cancel
        </button>
        <button
          onClick={onNext}
          className="inline-flex items-center gap-2 rounded-full bg-neutral-900 px-4 py-2 text-sm font-semibold text-white hover:bg-neutral-800"
        >
          {step === steps.length - 1 ? "Save Cohort" : "Next Step"}{" "}
          <ArrowRight size={14} />
        </button>
      </div>
    </div>
  </div>
);

const CohortWizard = ({ onClose, onComplete }) => {
  const [step, setStep] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [raw, setRaw] = useState({ who: "", want: "", frustration: "" });
  const [profile, setProfile] = useState(null);

  const simulateAI = () => {
    if (!raw.who) return;
    setIsAnalyzing(true);
    setStep(1);
    setTimeout(() => {
      setProfile({
        name: raw.who,
        role: "Target Audience",
        pain: `${raw.frustration || "Pain point"}... wants ${raw.want || "Outcome"}...`,
        values: ["Speed", "Value", "Efficiency"],
        fears: ["Wasting time", "Overpaying", "Disappointment"],
        channels: ["instagram", "linkedin"],
        patterns: ["Responds to 'Skip the Queue'", "Loves daily specials"],
        stats: { conversion: "0%", status: "new", engagementScore: 0 },
      });
      setIsAnalyzing(false);
      setStep(2);
    }, 1200);
  };

  const steps = [
    { title: "The Raw Input" },
    { title: "Building Psychographics..." },
    { title: "Review & Tweak" },
  ];

  const next = () => {
    if (step === 0) simulateAI();
    else if (step === 2) onComplete(profile);
  };

  return (
    <WizardWrapper title="Create Cohort" steps={steps} step={step} onClose={onClose} onNext={next}>
      {step === 0 && (
        <div className="space-y-6">
          <p className="rounded-lg bg-neutral-50 p-3 text-sm text-neutral-700">
            Describe the people in plain language. We’ll extract the psychology.
          </p>
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Who is this?
              </label>
              <input
                value={raw.who}
                onChange={(e) => setRaw({ ...raw, who: e.target.value })}
                className="mt-2 w-full rounded-lg border border-neutral-200 px-3 py-2 text-sm focus:border-neutral-400 focus:outline-none"
                placeholder="e.g. Stressed office workers nearby"
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
                  What do they want?
                </label>
                <textarea
                  value={raw.want}
                  onChange={(e) => setRaw({ ...raw, want: e.target.value })}
                  className="mt-2 h-28 w-full rounded-lg border border-neutral-200 px-3 py-2 text-sm focus:border-neutral-400 focus:outline-none"
                  placeholder="e.g. Affordable lunch, quick service, healthy but not boring..."
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
                  What frustrates them?
                </label>
                <textarea
                  value={raw.frustration}
                  onChange={(e) => setRaw({ ...raw, frustration: e.target.value })}
                  className="mt-2 h-28 w-full rounded-lg border border-neutral-200 px-3 py-2 text-sm focus:border-neutral-400 focus:outline-none"
                  placeholder="e.g. Waiting in line, greasy food, rude staff..."
                />
              </div>
            </div>
            <div className="flex items-center gap-2 rounded-lg border border-dashed border-neutral-300 px-4 py-3 text-sm text-neutral-600">
              <UploadCloud size={18} /> Optional: Upload photo/review snippet
            </div>
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
          <div className="relative">
            <div className="h-24 w-24 animate-spin rounded-full border-2 border-neutral-200 border-t-neutral-900" />
            <Sparkles className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-neutral-900" />
          </div>
          <div>
            <h4 className="text-xl font-semibold">Synthesizing Identity</h4>
            <p className="text-sm text-neutral-500">Extracting fears, channels, and triggers...</p>
          </div>
        </div>
      )}

      {step === 2 && profile && (
        <div className="space-y-6">
          <div className="rounded-xl border border-neutral-200 bg-neutral-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
                AI Constructed Profile
              </p>
              <button
                onClick={simulateAI}
                className="inline-flex items-center gap-1 text-xs font-semibold text-neutral-600 hover:text-neutral-900"
              >
                <RefreshCw size={12} /> Regenerate
              </button>
            </div>
            <label className="text-xs font-semibold text-neutral-500">Cohort Handle</label>
            <input
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              className="mt-1 w-full border-b border-neutral-200 px-1 pb-1 text-xl font-semibold focus:border-neutral-400 focus:outline-none"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <EditableTags
              title="Core Values"
              color="emerald"
              tags={profile.values}
              onChange={(tags) => setProfile({ ...profile, values: tags })}
            />
            <EditableTags
              title="Deep Fears"
              color="rose"
              tags={profile.fears}
              onChange={(tags) => setProfile({ ...profile, fears: tags })}
            />
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
              Engagement Triggers
            </p>
            <div className="mt-2 space-y-2">
              {profile.patterns.map((p, i) => (
                <div key={i} className="flex items-center gap-2">
                  <button
                    className="text-neutral-400 hover:text-rose-500"
                    onClick={() =>
                      setProfile({
                        ...profile,
                        patterns: profile.patterns.filter((_, idx) => idx !== i),
                      })
                    }
                  >
                    <Trash2 size={14} />
                  </button>
                  <input
                    defaultValue={p}
                    className="flex-1 rounded-md border border-neutral-200 px-3 py-2 text-sm focus:border-neutral-400 focus:outline-none"
                  />
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
              Primary Habitats
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {profile.channels.map((ch, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 rounded-full bg-neutral-100 px-3 py-1 text-xs font-semibold text-neutral-700"
                >
                  {ch}
                </span>
              ))}
              <button className="rounded-full border border-dashed border-neutral-300 px-3 py-1 text-xs font-semibold text-neutral-600 hover:border-neutral-400">
                + Add
              </button>
            </div>
          </div>
        </div>
      )}
    </WizardWrapper>
  );
};

const EditableTags = ({ title, color, tags, onChange }) => (
  <div>
    <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">{title}</p>
    <div className="mt-2 flex flex-wrap gap-2">
      {tags.map((tag, idx) => (
        <span
          key={idx}
          className={cn(
            "inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold",
            color === "emerald" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
          )}
        >
          {tag}
          <button
            className="text-neutral-500 hover:text-neutral-900"
            onClick={() => onChange(tags.filter((_, i) => i !== idx))}
          >
            <X size={12} />
          </button>
        </span>
      ))}
      <button
        className="rounded-full border border-neutral-200 px-3 py-1 text-xs font-semibold text-neutral-700 hover:border-neutral-300"
        onClick={() => onChange([...tags, "New item"])}
      >
        + Add
      </button>
    </div>
  </div>
);

const CohortCard = ({ cohort, onUseMoves, onDraftMuse }) => (
  <div className="flex h-full flex-col rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm transition hover:border-neutral-300">
    <div className="mb-3 flex items-start justify-between">
      <div>
        <p className="text-[11px] uppercase tracking-wide text-neutral-500">{cohort.role}</p>
        <h3 className="text-lg font-semibold text-neutral-900">{cohort.name}</h3>
      </div>
      <span
        className={cn(
          "rounded-full border px-2 py-1 text-[11px] font-semibold uppercase tracking-wide",
          statusStyles[cohort.stats.status] || statusStyles.dead
        )}
      >
        {cohort.stats.status}
      </span>
    </div>
    <p className="mb-4 text-sm text-neutral-600 italic">"{cohort.pain}"</p>
    <div className="mb-4 flex flex-wrap gap-2">
      {cohort.values.slice(0, 5).map((v, i) => (
        <span key={i} className="rounded-full bg-neutral-100 px-2 py-1 text-[11px] font-semibold text-neutral-700">
          {v}
        </span>
      ))}
    </div>
    <div className="mt-auto space-y-2">
      <div className="flex items-center justify-between text-xs text-neutral-500">
        <div className="flex items-center gap-2">
          <Users size={14} /> {cohort.stats.conversion}
        </div>
        <div className="flex items-center gap-1 text-neutral-700">
          <CheckCircle size={14} className="text-emerald-600" /> {cohort.stats.engagementScore}
        </div>
      </div>
      <div className="flex items-center gap-2 text-xs text-neutral-500">
        {cohort.channels.includes("linkedin") && <MessageSquare size={14} />}
        {cohort.channels.includes("email") && <Mail size={14} />}
        {cohort.channels.includes("instagram") && <MessageSquare size={14} />}
        {cohort.channels.includes("whatsapp") && <MessageSquare size={14} />}
      </div>
      <div className="grid grid-cols-2 gap-2 pt-2">
        <button
          onClick={onUseMoves}
          className="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-700 hover:border-neutral-300"
        >
          Use in Moves
        </button>
        <button
          onClick={onDraftMuse}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-neutral-900 px-3 py-2 text-xs font-semibold text-white hover:bg-neutral-800"
        >
          <PenTool size={12} /> Draft in Muse
        </button>
      </div>
    </div>
  </div>
);

export default function Cohorts() {
  const navigate = useNavigate();
  const [cohorts, setCohorts] = useState(INITIAL_COHORTS);
  const [showWizard, setShowWizard] = useState(false);

  const addCohort = (profile) => {
    if (!profile) return;
    const newCohort = { id: `c${cohorts.length + 1}`, ...profile };
    setCohorts([newCohort, ...cohorts]);
    setShowWizard(false);
  };

  return (
    <div className="flex min-h-screen flex-col bg-white text-neutral-900">
      <header className="border-b border-neutral-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-neutral-400">
              ICPs
            </p>
            <h1 className="text-2xl font-semibold">Cohorts</h1>
            <p className="text-sm text-neutral-500">The 3–9 groups your moves point to.</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="rounded-full border border-neutral-200 px-3 py-1 text-xs font-semibold text-neutral-700">
              {cohorts.length} / 9 slots
            </div>
            <button
              onClick={() => setShowWizard(true)}
              className="inline-flex items-center gap-2 rounded-full bg-neutral-900 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-neutral-800"
            >
              <Plus size={16} /> New Cohort
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-6 py-6">
        <div className="flex items-start gap-2 rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-3 text-sm text-neutral-700">
          <AlertCircle size={16} className="text-neutral-500" />
          <span>
            Every Move, Muse draft, and Matrix insight should point to a real cohort. If a cohort is
            vague, rewrite or kill it.
          </span>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {cohorts.map((c) => (
            <CohortCard
              key={c.id}
              cohort={c}
              onUseMoves={() => navigate(`/moves?cohortId=${c.id}`)}
              onDraftMuse={() => navigate(`/muse?cohortId=${c.id}`)}
            />
          ))}
        </div>
      </main>

      {showWizard && <CohortWizard onClose={() => setShowWizard(false)} onComplete={addCohort} />}
    </div>
  );
}
