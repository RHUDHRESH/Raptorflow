import React, { useMemo, useState } from "react";
import {
  ArrowDownToLine,
  ArrowUpRight,
  BookOpen,
  CheckCircle2,
  ChevronsUpDown,
  Circle,
  FileText,
  Flame,
  Layers,
  Link as LinkIcon,
  MoveRight,
  Palette,
  PenSquare,
  Repeat,
  Sparkles,
  Target,
  Wand2,
} from "lucide-react";
import { Link } from "react-router-dom";

const cn = (...classes) => classes.filter(Boolean).join(" ");

const WEEK_OPTIONS = ["This week (24–30 Nov)", "Next week (1–7 Dec)", "Custom"];
const BRANDS = ["Altivox – Main", "Altivox – SMB", "Sandbox"];
const MODEL_ROUTES = ["Auto", "Cheap", "Premium"];

const MOVES = [
  {
    id: "m1",
    name: "Weekend Booking Engine",
    cohorts: ["Weekend Foodies", "High-intent Dine-in"],
    channels: ["IG", "WA", "LI"],
    progress: "3/5 ready",
  },
  {
    id: "m2",
    name: "Office Lunch Upsell",
    cohorts: ["Office Lunch Crowd"],
    channels: ["IG", "WA"],
    progress: "2/4 ready",
  },
];

const COHORTS = [
  { name: "Weekend Foodies", note: "Reels + scarcity working" },
  { name: "Office Lunch Crowd", note: "Stories > Posts" },
  { name: "High-intent Dine-in", note: "Proof + scarcity" },
];

const VOICE = ["Blunt", "No cringe", "Data-backed", "Founder-first"];

const ASSETS = [
  {
    id: "a1",
    title: 'IG Carousel – "Stop Discounting Your Time"',
    channel: "IG",
    type: "Carousel",
    status: "Draft",
    move: "Weekend Booking Engine",
    cohorts: ["Weekend Foodies"],
    tags: ["Hook: Story", "Angle: Founder mistake", "Objective: Book calls"],
  },
  {
    id: "a2",
    title: 'LI Post – "Founder Pricing Math"',
    channel: "LI",
    type: "Post",
    status: "In review",
    move: "Office Lunch Upsell",
    cohorts: ["Office Lunch Crowd"],
    tags: ["Hook: Spiky", "Angle: Proof", "Objective: Book demos"],
  },
  {
    id: "a3",
    title: 'Email – "Stop the Discounts"',
    channel: "Email",
    type: "Email",
    status: "Ready",
    move: "Weekend Booking Engine",
    cohorts: ["Weekend Foodies"],
    tags: ["Hook: Proof", "Objective: Rebook", "CTA: Book call"],
  },
];

const INSIGHTS = [
  "Reels with face close-up: 3.1x saves vs food-only",
  "Story-led hooks > contrarian for “Weekend Foodies”",
  "WA broadcasts Fri–Sun drive 70% of bookings",
];

const IDEA_STACK = [
  {
    id: "h1",
    text: `"Your discount isn’t generosity. It’s self-sabotage."`,
    tags: ["Hook: Spiky", "Cohort: Indie SaaS"],
  },
  {
    id: "h2",
    text: `"Stop trying to win on price. Win on being irreplaceable."`,
    tags: ["Hook: Pricing", "Cohort: DTC"],
  },
];

const STATUS_COLORS = {
  Draft: "bg-neutral-100 text-neutral-800 border-neutral-200",
  "In review": "bg-amber-100 text-amber-900 border-amber-200",
  Ready: "bg-emerald-100 text-emerald-900 border-emerald-200",
  Published: "bg-blue-100 text-blue-900 border-blue-200",
};

const Pill = ({ children, className }) => (
  <span className={cn("inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-semibold", className)}>
    {children}
  </span>
);

const SectionCard = ({ title, subtitle, children, actions, className }) => (
  <div className={cn("runway-card border border-neutral-200 bg-white shadow-sm p-4 rounded-2xl", className)}>
    {(title || actions) && (
      <div className="mb-3 flex items-center justify-between gap-2">
        <div>
          {title && <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-neutral-400">{title}</p>}
          {subtitle && <p className="text-sm font-semibold text-neutral-900">{subtitle}</p>}
        </div>
        {actions}
      </div>
    )}
    {children}
  </div>
);

const SummaryCard = ({ label, value, helper, accent }) => (
  <div className="rounded-3xl border border-neutral-200 bg-gradient-to-br from-white to-neutral-100 p-4 shadow-sm">
    <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-neutral-400">{label}</p>
    <p className="text-3xl font-semibold text-neutral-900">{value}</p>
    {helper && <p className="text-xs text-neutral-500">{helper}</p>}
    {accent && <span className="mt-2 inline-flex rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white">{accent}</span>}
  </div>
);

export default function Muse() {
  const [week, setWeek] = useState(WEEK_OPTIONS[0]);
  const [brand, setBrand] = useState(BRANDS[0]);
  const [modelRoute] = useState(MODEL_ROUTES[0]);
  const [statusFilter, setStatusFilter] = useState("All");
  const [channelFilter, setChannelFilter] = useState("All");
  const [view, setView] = useState("home"); // home | workspace | repurpose | hooks

  const filteredAssets = useMemo(() => {
    return ASSETS.filter((asset) => {
      const statusMatch = statusFilter === "All" || asset.status === statusFilter;
      const channelMatch = channelFilter === "All" || asset.channel === channelFilter;
      return statusMatch && channelMatch;
    });
  }, [statusFilter, channelFilter]);

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Top bar */}
      <div className="border-b border-neutral-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-neutral-400">Muse</p>
            <p className="text-sm text-neutral-600">Content factory for this week’s Moves</p>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <button className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-2 text-neutral-800 hover:border-neutral-300">
              <Sparkles size={14} /> Model: {modelRoute}
            </button>
            <button className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-2 text-neutral-800 hover:border-neutral-300">
              <ChevronsUpDown size={14} /> {week}
            </button>
            <button className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-2 text-neutral-800 hover:border-neutral-300">
              <Palette size={14} /> {brand}
            </button>
          </div>
        </div>
      </div>

      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-6">
        {/* Top navigation for Muse modes */}
        <div className="flex flex-wrap gap-2 text-sm font-semibold">
          {[
            { id: "home", label: "Muse Home" },
            { id: "workspace", label: "Draft Workspace" },
            { id: "repurpose", label: "Repurpose Studio" },
            { id: "hooks", label: "Hooks Lab" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setView(tab.id)}
              className={cn(
                "rounded-full px-4 py-2 border transition",
                view === tab.id
                  ? "bg-neutral-900 text-white border-neutral-900"
                  : "bg-white text-neutral-700 border-neutral-200 hover:border-neutral-400"
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>
        {view === "home" && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <SummaryCard label="Active Move" value={MOVES[0].name} helper="Tied to 3 assets" accent="Focus" />
              <SummaryCard label="Current draft" value="IG Carousel – Pricing" helper="In review" accent="In review" />
              <SummaryCard label="Signal" value="Face-led hooks" helper="Impact: Medium" accent="Live" />
            </div>

            <div className="grid gap-6 lg:grid-cols-[minmax(0,320px)_minmax(0,1fr)_minmax(0,320px)]">
          {/* Left: context */}
          <div className="space-y-4">
            <SectionCard title="This Week’s Moves">
              <div className="space-y-3">
                {MOVES.map((move) => (
                  <div key={move.id} className="rounded-xl border border-neutral-200 p-3 bg-white">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-semibold text-neutral-900">{move.name}</p>
                        <div className="mt-1 flex flex-wrap gap-1 text-[11px] text-neutral-600">
                          {move.cohorts.map((c) => (
                            <Pill key={c} className="bg-neutral-100 text-neutral-700 border border-neutral-200">
                              {c}
                            </Pill>
                          ))}
                        </div>
                      </div>
                      <Pill className="bg-neutral-900 text-white">{move.progress}</Pill>
                    </div>
                    <div className="mt-2 flex gap-2 text-[11px] text-neutral-500">
                      {move.channels.map((ch) => (
                        <span key={ch} className="rounded-full bg-neutral-100 px-2 py-1 font-semibold">
                          {ch}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="Cohorts in Focus">
              <div className="space-y-2">
                {COHORTS.map((cohort) => (
                  <div key={cohort.name} className="rounded-xl border border-neutral-200 bg-white px-3 py-2">
                    <p className="text-sm font-semibold text-neutral-900">{cohort.name}</p>
                    <p className="text-xs text-neutral-600">{cohort.note}</p>
                  </div>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="Brand Voice">
              <div className="flex flex-wrap gap-2">
                {VOICE.map((tag) => (
                  <Pill key={tag} className="bg-neutral-100 text-neutral-800 border border-neutral-200">
                    {tag}
                  </Pill>
                ))}
              </div>
            </SectionCard>
          </div>

          {/* Center: workbench */}
          <div className="space-y-5">
            <SectionCard title="Primary Actions">
              <div className="grid gap-3 sm:grid-cols-3">
                <button className="group relative flex h-full flex-col items-start justify-between rounded-2xl border border-neutral-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
                  <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
                    <PenSquare size={16} /> Draft for a Move
                  </div>
                  <p className="text-xs text-neutral-500">Create content linked to a Move & KPI</p>
                  <MoveRight className="text-neutral-400 group-hover:text-neutral-900" size={16} />
                </button>
                <button className="group relative flex h-full flex-col items-start justify-between rounded-2xl border border-neutral-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
                  <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
                    <Repeat size={16} /> Repurpose content
                  </div>
                  <p className="text-xs text-neutral-500">Turn longform into assets</p>
                  <MoveRight className="text-neutral-400 group-hover:text-neutral-900" size={16} />
                </button>
                <button className="group relative flex h-full flex-col items-start justify-between rounded-2xl border border-neutral-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg">
                  <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
                    <Sparkles size={16} /> Explore hooks & angles
                  </div>
                  <p className="text-xs text-neutral-500">Mine and test hooks for your cohorts</p>
                  <MoveRight className="text-neutral-400 group-hover:text-neutral-900" size={16} />
                </button>
              </div>
            </SectionCard>

            <SectionCard
              title="This week’s assets"
              actions={
                <div className="flex items-center gap-2 text-xs">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="rounded-full border border-neutral-200 px-3 py-1 font-semibold text-neutral-700"
                  >
                    {["All", "Draft", "In review", "Ready", "Published"].map((s) => (
                      <option key={s}>{s}</option>
                    ))}
                  </select>
                  <div className="flex gap-1">
                    {["All", "IG", "LI", "Email", "WA", "LP"].map((ch) => (
                      <button
                        key={ch}
                        onClick={() => setChannelFilter(ch)}
                        className={cn(
                          "rounded-full px-3 py-1 text-[11px] font-semibold border",
                          channelFilter === ch
                            ? "bg-neutral-900 text-white border-neutral-900"
                            : "bg-neutral-100 text-neutral-700 border-neutral-200"
                        )}
                      >
                        {ch}
                      </button>
                    ))}
                  </div>
                </div>
              }
            >
              <div className="space-y-3">
                {filteredAssets.map((asset) => (
                  <div key={asset.id} className="rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm hover:shadow-md transition">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2 text-xs font-semibold text-neutral-500">
                        <Pill className="bg-neutral-100 text-neutral-800 border border-neutral-200">{asset.channel}</Pill>
                        <span className="text-neutral-700">{asset.type}</span>
                        <span className={cn("rounded-full px-2 py-1 text-[11px] font-semibold border", STATUS_COLORS[asset.status] || STATUS_COLORS.Draft)}>
                          {asset.status}
                        </span>
                      </div>
                      <div className="flex gap-2 text-xs">
                        <Link
                          to={`/moves/${asset.id}`}
                          className="inline-flex items-center gap-1 rounded-full border border-neutral-200 px-3 py-1 font-semibold text-neutral-700 hover:border-neutral-300"
                        >
                          Open <ArrowUpRight size={12} />
                        </Link>
                        <button className="inline-flex items-center gap-1 rounded-full border border-neutral-200 px-3 py-1 font-semibold text-neutral-700 hover:border-neutral-300">
                          <LinkIcon size={12} /> Canva
                        </button>
                      </div>
                    </div>
                    <p className="mt-2 text-base font-semibold text-neutral-900">{asset.title}</p>
                    <div className="mt-1 flex flex-wrap gap-2 text-xs text-neutral-600">
                      <span className="font-semibold text-neutral-800">{asset.move}</span>
                      {asset.cohorts.map((c) => (
                        <Pill key={c} className="bg-neutral-100 text-neutral-700 border border-neutral-200">
                          {c}
                        </Pill>
                      ))}
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-neutral-600">
                      {asset.tags.map((t) => (
                        <span key={t} className="rounded-full bg-neutral-100 px-2 py-1 border border-neutral-200">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>

          {/* Right: intelligence */}
          <div className="space-y-4">
            <SectionCard title="Insights from Matrix">
              <div className="space-y-2">
                {INSIGHTS.map((insight) => (
                  <div key={insight} className="flex items-start justify-between rounded-xl border border-neutral-200 bg-white p-3">
                    <div className="text-sm text-neutral-800">{insight}</div>
                    <button className="text-[11px] font-semibold text-neutral-600 hover:text-neutral-900">Apply</button>
                  </div>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="Idea Stack" subtitle="Hooks & angles">
              <div className="space-y-2">
                {IDEA_STACK.map((idea) => (
                  <div key={idea.id} className="rounded-xl border border-neutral-200 bg-white p-3">
                    <p className="text-sm text-neutral-900">{idea.text}</p>
                    <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-neutral-600">
                      {idea.tags.map((tag) => (
                        <span key={tag} className="rounded-full bg-neutral-100 px-2 py-1 border border-neutral-200">
                          {tag}
                        </span>
                      ))}
                    </div>
                    <div className="mt-3 flex gap-2 text-xs">
                      <button className="inline-flex items-center gap-1 rounded-full bg-neutral-900 px-3 py-1 font-semibold text-white">
                        Use for new asset
                      </button>
                      <button className="inline-flex items-center gap-1 rounded-full border border-neutral-200 px-3 py-1 font-semibold text-neutral-700 hover:border-neutral-300">
                        Archive
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>
        </div>
      </>
        )}

        {view === "workspace" && (
          <div className="grid gap-6 lg:grid-cols-[minmax(0,300px)_minmax(0,1fr)_minmax(0,320px)]">
            <div className="space-y-4">
              <SectionCard title="Context" subtitle="Brief snapshot">
                <div className="space-y-2 text-sm text-neutral-800">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">Move:</span>
                    <Link to="/moves/m1" className="text-neutral-900 underline">
                      Weekend Booking Engine
                    </Link>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {["Weekend Foodies", "High-intent Dine-in"].map((c) => (
                      <Pill key={c} className="bg-neutral-100 text-neutral-700 border border-neutral-200">
                        {c}
                      </Pill>
                    ))}
                  </div>
                  <div className="flex flex-col gap-1 text-xs text-neutral-600">
                    <span>Channel: Instagram – Carousel</span>
                    <span>Objective: Book calls</span>
                    <span>Tone: Blunt, Data-backed, Founder-first</span>
                    <span>Constraints: ≤120 chars/slide, No emoji</span>
                  </div>
                </div>
              </SectionCard>
              <SectionCard title="Checklist">
                <div className="space-y-2 text-sm text-neutral-700">
                  {[
                    "Hook tested vs previous winners",
                    "Clear CTA with next step",
                    "Objection addressed",
                  ].map((item) => (
                    <label key={item} className="flex items-center gap-2">
                      <input type="checkbox" className="h-4 w-4 rounded border-neutral-300" />
                      <span>{item}</span>
                    </label>
                  ))}
                </div>
              </SectionCard>
            </div>

            <div className="space-y-4">
              <SectionCard title="Draft Workspace" subtitle="Tabbed editor">
                <div className="mb-3 flex flex-wrap gap-2 text-xs font-semibold">
                  {["Brief", "Skeleton", "Draft", "Variants"].map((tab) => (
                    <button
                      key={tab}
                      className="rounded-full border border-neutral-200 px-3 py-1 hover:border-neutral-400"
                    >
                      {tab}
                    </button>
                  ))}
                </div>
                <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-neutral-400">Section</p>
                        <h3 className="text-lg font-semibold text-neutral-900">Slide 1: Hook</h3>
                      </div>
                      <div className="flex gap-2 text-xs">
                        <button className="rounded-full border border-neutral-200 px-3 py-1 hover:border-neutral-300">Rewrite</button>
                        <button className="rounded-full border border-neutral-200 px-3 py-1 hover:border-neutral-300">Shorter</button>
                      </div>
                    </div>
                    <textarea className="min-h-[140px] w-full rounded-2xl border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm focus:border-neutral-300 focus:outline-none">
Hook: Your discount isn’t generosity. It’s self-sabotage.
                    </textarea>
                    <div className="rounded-xl border border-neutral-100 bg-neutral-50 p-3 text-sm text-neutral-700">
                      <p className="font-semibold text-neutral-900">Preview</p>
                      <p className="mt-2">
                        Slide 1: Hook · Slide 2: What you usually do · Slide 3: Why it fails · Slide 4: Better option · Slide 5: Proof · Slide 6: CTA
                      </p>
                    </div>
                  </div>
                  <div className="rounded-2xl border border-neutral-200 bg-white p-3 text-sm text-neutral-800 shadow-sm">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.3em] text-neutral-400">Status</p>
                    <div className="mt-2 flex flex-col gap-2">
                      <Pill className="bg-amber-100 text-amber-900 border border-amber-200">In review</Pill>
                      <span className="text-xs text-neutral-600">Last edited 2h ago by Bossman</span>
                    </div>
                    <div className="mt-4 space-y-2">
                      <button className="w-full rounded-full bg-neutral-900 px-3 py-2 text-xs font-semibold text-white hover:bg-neutral-800">
                        Ask for critique
                      </button>
                      <button className="w-full rounded-full border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-800 hover:border-neutral-300">
                        Mark ready
                      </button>
                    </div>
                  </div>
                </div>
              </SectionCard>
            </div>

            <div className="space-y-4">
              <SectionCard title="Critique" subtitle="AI feedback">
                <ul className="space-y-2 text-sm text-neutral-700">
                  <li>Hook too generic; compare against top 3 winners.</li>
                  <li>CTA doesn’t specify what “book a call” gives them.</li>
                </ul>
                <div className="mt-3 flex flex-wrap gap-2 text-xs">
                  <button className="rounded-full border border-neutral-200 px-3 py-1 hover:border-neutral-300">Fix this section</button>
                  <button className="rounded-full border border-neutral-200 px-3 py-1 hover:border-neutral-300">Compare winners</button>
                </div>
              </SectionCard>

              <SectionCard title="Performance expectations">
                <div className="space-y-2 text-sm text-neutral-700">
                  <div className="flex items-center justify-between">
                    <span>Saves</span>
                    <span className="font-semibold text-neutral-900">+2.3x</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>CTR</span>
                    <span className="font-semibold text-neutral-900">+18%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Replies</span>
                    <span className="font-semibold text-neutral-900">+11%</span>
                  </div>
                </div>
              </SectionCard>
            </div>
          </div>
        )}

        {view === "repurpose" && (
          <div className="grid gap-6 lg:grid-cols-[minmax(0,360px)_minmax(0,1fr)]">
            <div className="space-y-4">
              <SectionCard title="Input" subtitle="Drop longform">
                <div className="rounded-xl border border-dashed border-neutral-300 bg-neutral-50 p-6 text-center">
                  <p className="text-sm text-neutral-700">Drag & drop file, paste URL, or paste raw text.</p>
                  <button className="mt-3 rounded-full border border-neutral-900 px-4 py-2 text-xs font-semibold text-neutral-900 hover:bg-neutral-900 hover:text-white">
                    Upload or paste
                  </button>
                </div>
                <div className="mt-4 text-sm text-neutral-700">
                  <p className="font-semibold text-neutral-900">Detected</p>
                  <p>Title: “Pricing as a moat”</p>
                  <p>Topics: Pricing math, Scarcity, Proof</p>
                  <p>Duration: 18m transcript</p>
                </div>
              </SectionCard>
            </div>
            <div className="space-y-4">
              <SectionCard title="Plan repurposed assets">
                <div className="space-y-3">
                  {[
                    "LinkedIn Thread – “5 silent killers of pricing”",
                    "IG Carousel – “Stop undercharging”",
                    "Email – “The real cost of discounts”",
                    "WA broadcast – “Price increase announcement”",
                  ].map((item) => (
                    <div key={item} className="flex items-start justify-between rounded-xl border border-neutral-200 bg-white p-3">
                      <div className="text-sm text-neutral-800">{item}</div>
                      <input type="checkbox" className="h-4 w-4 rounded border-neutral-300" defaultChecked />
                    </div>
                  ))}
                </div>
                <button className="mt-4 w-full rounded-full bg-neutral-900 px-4 py-2 text-xs font-semibold text-white hover:bg-neutral-800">
                  Create briefs for selected
                </button>
              </SectionCard>
            </div>
          </div>
        )}

        {view === "hooks" && (
          <div className="grid gap-6 lg:grid-cols-[minmax(0,320px)_minmax(0,1fr)]">
            <SectionCard title="Patterns" subtitle="Hook performance">
              <div className="space-y-3 text-sm text-neutral-800">
                <div className="rounded-xl border border-neutral-200 bg-white p-3">
                  <p className="font-semibold text-neutral-900">Story-led hooks</p>
                  <p className="text-neutral-600">CTR +2.3x vs baseline • Sample: 19 assets • Weekend Foodies</p>
                </div>
                <div className="rounded-xl border border-neutral-200 bg-white p-3">
                  <p className="font-semibold text-neutral-900">Contrarian hooks</p>
                  <p className="text-neutral-600">Mixed results • Good: Indie SaaS • Avoid: Enterprise CMOs</p>
                </div>
              </div>
            </SectionCard>
            <SectionCard title="Hook library">
              <div className="space-y-2">
                {[
                  { text: `“Your 10% discount isn’t generous. It’s self-sabotage.”`, tags: ["Spiky", "Pricing", "Indie SaaS"] },
                  { text: `“Stop trying to win on price. Win on being irreplaceable.”`, tags: ["Pricing", "Story", "DTC"] },
                ].map((hook, idx) => (
                  <div key={idx} className="rounded-xl border border-neutral-200 bg-white p-3">
                    <p className="text-sm text-neutral-900">{hook.text}</p>
                    <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-neutral-600">
                      {hook.tags.map((t) => (
                        <span key={t} className="rounded-full bg-neutral-100 px-2 py-1 border border-neutral-200">
                          {t}
                        </span>
                      ))}
                    </div>
                    <div className="mt-3 flex gap-2 text-xs">
                      <button className="inline-flex items-center gap-1 rounded-full bg-neutral-900 px-3 py-1 font-semibold text-white">
                        Use
                      </button>
                      <button className="inline-flex items-center gap-1 rounded-full border border-neutral-200 px-3 py-1 font-semibold text-neutral-700 hover:border-neutral-300">
                        Clone & tweak
                      </button>
                      <button className="inline-flex items-center gap-1 rounded-full border border-neutral-200 px-3 py-1 font-semibold text-neutral-700 hover:border-neutral-300">
                        Mute
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>
        )}
      </div>
    </div>
  );
}
