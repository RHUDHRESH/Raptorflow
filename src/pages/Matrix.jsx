import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertCircle,
  ArrowUpRight,
  BarChart2,
  Brain,
  Check,
  ChevronRight,
  Filter,
  MoreHorizontal,
  Search,
  Skull,
  Sparkles,
  Star,
  TrendingDown,
  TrendingUp,
  Users,
  Zap,
  X,
} from "lucide-react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import { PageHeader, LuxeHeading, LuxeButton, LuxeCard, LuxeBadge, LuxeStat } from '../components/ui/PremiumUI';

const cn = (...c) => c.filter(Boolean).join(" ");

// Mock data
const CAMPAIGNS = [
  {
    id: 1,
    name: "Weekend Table Fill",
    status: "at_risk",
    goal: "30 Bookings",
    current: 18,
    target: 30,
    tasksDone: 21,
    totalTasks: 28,
    bestChannel: "IG Reels",
    bestChannelMultiplier: "2.3x",
    bestCohort: "Office Workers",
    healthScore: 45,
    aiSummary: "Reels with faces drive 70% of bookings; static menus flop.",
  },
  {
    id: 2,
    name: "200 New Followers Sprint",
    status: "on_track",
    goal: "200 Followers",
    current: 165,
    target: 200,
    tasksDone: 18,
    totalTasks: 28,
    bestChannel: "IG Stories",
    bestChannelMultiplier: "4.1x",
    bestCohort: "Weekend Foodies",
    healthScore: 92,
    aiSummary: "Collab post on Day 3 caused the spike; keep collaborating.",
  },
];

const CHANNEL_DETAILS = [
  { name: "IG Reels", impressions: 12500, sentiment: "positive" },
  { name: "IG Stories", impressions: 3400, sentiment: "neutral" },
  { name: "WhatsApp", impressions: 850, sentiment: "negative" },
];

const ASSETS = [
  { id: 101, name: "Lunch rush staff reel", type: "IG Reel", cohort: "Office Workers", exposures: 4520, conversions: 8, score: 92, sentiment: "winner" },
  { id: 102, name: "Static menu poster", type: "IG Post", cohort: "All", exposures: 890, conversions: 0, score: 12, sentiment: "flop" },
  { id: 103, name: "Chef rant", type: "IG Reel", cohort: "Foodies", exposures: 8900, conversions: 12, score: 98, sentiment: "winner" },
];

const COHORTS = [
  { id: "c1", name: "Office Workers", health: "healthy", activeMoves: 2, responseRate: "6.2%", responseTrend: "up", bestPattern: "Weekday hacks", deadPattern: "Long essays" },
  { id: "c2", name: "Weekend Foodies", health: "weak", activeMoves: 1, responseRate: "2.1%", responseTrend: "down", bestPattern: "Scarcity offers", deadPattern: "Discount coupons" },
];

const PATTERNS = [
  { id: "p1", name: "Educational Reels", performance: 210, sentiment: "positive" },
  { id: "p2", name: "Short WhatsApp offers", performance: 120, sentiment: "positive" },
  { id: "p3", name: "Long essays", performance: -80, sentiment: "negative" },
];

const PULSE = [
  { id: "a1", title: "Kill Night Owl Happy Hours", reason: "0.4% response rate; save ~$500/week.", actionType: "kill" },
  { id: "a2", title: "Scale Weekday Lunch Reels", reason: "Reels 3x baseline; add 3 more this week.", actionType: "scale" },
];

const statusStyles = {
  on_track: "bg-emerald-50 text-emerald-700 border-emerald-100",
  at_risk: "bg-amber-50 text-amber-700 border-amber-100",
  off_track: "bg-rose-50 text-rose-700 border-rose-100",
  healthy: "bg-emerald-50 text-emerald-700 border-emerald-100",
  weak: "bg-amber-50 text-amber-700 border-amber-100",
  dead: "bg-neutral-100 text-neutral-600 border-neutral-200",
};

const StatusPill = ({ status, text }) => (
  <span className={cn("inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide", statusStyles[status] || statusStyles.dead)}>
    {text || status}
  </span>
);

const Progress = ({ current, total }) => {
  const pct = Math.min((current / total) * 100, 100);
  return (
    <div className="h-1.5 w-full rounded-full bg-neutral-100">
      <div className="h-1.5 rounded-full bg-neutral-900" style={{ width: `${pct}%` }} />
    </div>
  );
};

export default function Matrix() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [tab, setTab] = useState("moves");
  const [selectedMove, setSelectedMove] = useState(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [pulseAction, setPulseAction] = useState(null);
  const [museContext, setMuseContext] = useState(null);
  const [selectedAsset, setSelectedAsset] = useState(null);

  const filteredMoves = useMemo(() => {
    return CAMPAIGNS.filter((m) => {
      if (statusFilter === "active" && !["on_track", "at_risk", "off_track"].includes(m.status)) return false;
      if (search && !m.name.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [statusFilter, search]);

  const openMuse = (context) => {
    setMuseContext(context);
    const params = new URLSearchParams();
    params.set("source", "matrix");
    if (context?.cohort) params.set("cohortId", context.cohort);
    if (context?.pattern) params.set("pattern", context.pattern);
    if (context?.id) params.set("assetId", context.id);
    navigate(`/muse?${params.toString()}`);
  };

  // hydrate move from query (e.g., from Moves)
  useEffect(() => {
    const moveId = searchParams.get("moveId");
    if (moveId) {
      const found = CAMPAIGNS.find((m) => String(m.id) === String(moveId));
      if (found) setSelectedMove(found);
    }
  }, [searchParams]);

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-6">
      {/* Page Title (Task 24) */}
      <PageHeader
        title="The Matrix"
        subtitle="Cross-campaign intelligence, pattern recognition, and anomaly detection."
        action={
            <nav className="hidden gap-1 md:flex p-1 bg-neutral-100 rounded-lg">
            {["moves", "cohorts", "patterns", "pulse"].map((t) => (
                <button
                key={t}
                onClick={() => { setSelectedMove(null); setTab(t); }}
                className={cn(
                    "rounded-md px-4 py-2 text-sm font-medium capitalize transition-all", 
                    tab === t ? "bg-white text-neutral-900 shadow-sm" : "text-neutral-500 hover:text-neutral-900"
                )}
                >
                {t}
                </button>
            ))}
            </nav>
        }
      />
      {!selectedMove ? (
        <>
          {tab === "moves" && (
            <div className="space-y-6">
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div className="flex flex-1 items-center gap-2 rounded-full border border-neutral-200 px-3 py-2">
                  <Search size={16} className="text-neutral-400" />
                  <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search moves..." className="w-full bg-transparent text-sm outline-none placeholder:text-neutral-400" />
                </div>
                <div className="flex gap-2">
                  {["all", "active"].map((s) => (
                    <button key={s} onClick={() => setStatusFilter(s)} className={cn("rounded-full border px-3 py-1 text-xs font-semibold", statusFilter === s ? "border-neutral-900 bg-neutral-900 text-white" : "border-neutral-200 text-neutral-600")}>
                      {s}
                    </button>
                  ))}
                  <div className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-1 text-xs font-semibold text-neutral-600">
                    <Filter size={14} /> Filters
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                {filteredMoves.map((move) => (
                  <div key={move.id} className="group relative overflow-hidden rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm transition hover:border-neutral-300">
                    <div className="absolute left-0 top-0 h-full w-1 bg-neutral-900" />
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="mb-2 flex items-center gap-2">
                          <Link to={`/strategy/campaigns/${move.id}`} className="text-lg font-semibold hover:underline">{move.name}</Link>
                          <StatusPill status={move.status} />
                        </div>
                        <p className="text-sm text-neutral-500">{move.goal}</p>
                      </div>
                      <button className="text-neutral-400 hover:text-neutral-700"><MoreHorizontal size={18} /></button>
                    </div>

                    <div className="mt-4 grid grid-cols-3 gap-3 text-sm">
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-neutral-500">Progress</p>
                        <p className="text-lg font-semibold">{Math.round((move.current / move.target) * 100)}%</p>
                        <Progress current={move.current} total={move.target} />
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-neutral-500">Execution</p>
                        <p className="text-lg font-semibold">{move.tasksDone}/{move.totalTasks}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-neutral-500">Top channel</p>
                        <p className="text-lg font-semibold text-emerald-700">{move.bestChannelMultiplier}</p>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between border-t border-neutral-100 pt-3">
                      <div className="flex items-center gap-2 text-xs text-neutral-500">
                        <Users size={12} /> {move.bestCohort}
                      </div>
                      <div className="flex gap-2">
                        <button className="rounded-full px-3 py-1 text-xs font-semibold text-neutral-600 hover:text-neutral-900">Review</button>
                        <button onClick={() => setSelectedMove(move)} className="rounded-full bg-neutral-900 px-3 py-1 text-xs font-semibold text-white">View Matrix</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tab === "cohorts" && (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {COHORTS.map((c) => (
                <div key={c.id} className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm transition hover:border-neutral-300">
                  <div className="mb-3 flex items-start justify-between">
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-neutral-500">Cohort</p>
                      <h3 className="text-lg font-semibold">{c.name}</h3>
                    </div>
                    <StatusPill status={c.health} />
                  </div>
                  <div className="space-y-2 text-sm text-neutral-600">
                    <div className="flex justify-between"><span>Active moves</span><span className="font-semibold text-neutral-900">{c.activeMoves}</span></div>
                    <div className="flex items-center justify-between">
                      <span>Response rate</span>
                      <span className="flex items-center gap-1 font-semibold text-neutral-900">
                        {c.responseRate}
                        {c.responseTrend === "up" && <TrendingUp size={14} className="text-emerald-600" />}
                        {c.responseTrend === "down" && <TrendingDown size={14} className="text-rose-500" />}
                      </span>
                    </div>
                  </div>
                  <div className="mt-3 space-y-1 rounded-xl bg-neutral-50 p-3 text-sm">
                    <div className="flex items-start gap-2 text-emerald-700"><Star size={14} /> {c.bestPattern}</div>
                    <div className="flex items-start gap-2 text-rose-600"><Skull size={14} /> {c.deadPattern}</div>
                  </div>
                  <div className="mt-4 grid grid-cols-3 gap-2">
                    <button className="rounded-lg border border-neutral-200 px-3 py-2 text-xs font-semibold text-neutral-700 hover:border-neutral-300">Details</button>
                    <button onClick={() => openMuse({ cohort: c.name, pattern: c.bestPattern })} className="col-span-2 rounded-lg bg-neutral-900 px-3 py-2 text-xs font-semibold text-white hover:bg-neutral-800">Open in Muse</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === "patterns" && (
            <div className="space-y-3">
              {PATTERNS.map((p, idx) => (
                <div key={p.id} className="flex flex-col gap-3 rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm transition hover:border-neutral-300 md:flex-row md:items-center">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full border border-neutral-200 text-sm font-semibold text-neutral-700">#{idx + 1}</div>
                  <div className="flex-1">
                    <div className="mb-1 flex items-center gap-2">
                      <h3 className="text-lg font-semibold">{p.name}</h3>
                      <StatusPill status={p.sentiment === "positive" ? "healthy" : "off_track"} text={`${p.performance}% vs baseline`} />
                    </div>
                  </div>
                  <div className="flex w-full gap-2 md:w-auto">
                    <button className="flex-1 rounded-lg border border-neutral-200 px-4 py-2 text-xs font-semibold text-neutral-700 hover:border-neutral-300">See assets</button>
                    {p.sentiment === "positive" && (
                      <button onClick={() => openMuse({ pattern: p.name, sourceName: "Pattern Matrix" })} className="flex-1 rounded-lg bg-neutral-900 px-4 py-2 text-xs font-semibold text-white hover:bg-neutral-800">Scale in Muse</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === "pulse" && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                <LuxeStat label="Moves On Track" value="2" icon={Check} />
                <LuxeStat label="Moves At Risk" value="1" icon={AlertCircle} />
                <LuxeStat label="Moves Failing" value="1" icon={X} />
              </div>
              <div className="space-y-4">
                {PULSE.map((a) => (
                  <div key={a.id} className="flex flex-col gap-3 rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm transition hover:border-neutral-300 md:flex-row md:items-center md:justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-base font-semibold">{a.title}</h4>
                        <StatusPill status={a.actionType === "kill" ? "off_track" : "healthy"} text={`${a.impact || ""} Impact`} />
                      </div>
                      <p className="text-sm text-neutral-600">{a.reason}</p>
                    </div>
                    <div className="flex w-full gap-2 md:w-auto">
                      <button className="flex-1 rounded-lg border border-neutral-200 px-4 py-2 text-xs font-semibold text-neutral-700 hover:border-neutral-300">Ignore</button>
                      <button onClick={() => setPulseAction(a)} className={cn("flex-1 rounded-lg px-4 py-2 text-xs font-semibold text-white", a.actionType === "kill" ? "bg-rose-600 hover:bg-rose-500" : "bg-emerald-600 hover:bg-emerald-500")}>
                        {a.actionType === "kill" ? "Kill Move" : "Apply"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <Detail move={selectedMove} onBack={() => setSelectedMove(null)} openMuse={openMuse} setAsset={setSelectedAsset} />
      )}

      {selectedAsset && <AssetInspector asset={selectedAsset} onClose={() => setSelectedAsset(null)} onOpenMuse={openMuse} />}
      {pulseAction && <StrategyModal action={pulseAction} onClose={() => setPulseAction(null)} />}
      {museContext && <MuseBridge context={museContext} onClose={() => setMuseContext(null)} />}
    </div>
  );
}

const Detail = ({ move, onBack, openMuse, setAsset }) => (
  <div className="space-y-6">
    <button onClick={onBack} className="inline-flex items-center gap-2 text-sm font-semibold text-neutral-600 hover:text-neutral-900">
      <ChevronRight className="-ml-1 rotate-180" size={16} /> Back
    </button>

    <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
      <InfoCard label="Goal Pace" value={`${move.current}/${move.target}`} pill={<StatusPill status={move.status} />} />
      <InfoCard label="Execution" value={`${Math.round((move.tasksDone / move.totalTasks) * 100)}%`} sub={`${move.totalTasks - move.tasksDone} tasks remaining`} />
      <InfoCard label="Top Channel" value={move.bestChannel} sub={move.bestChannelMultiplier} />
      <InfoCard label="Health" value={`${move.healthScore}/100`} icon={<TrendingUp size={14} className="text-emerald-600" />} />
    </div>

    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2 rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[11px] uppercase tracking-wide text-neutral-500">Channel Breakdown</p>
            <h3 className="text-lg font-semibold">Performance</h3>
          </div>
        </div>
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={CHANNEL_DETAILS} layout="vertical" margin={{ left: 0, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f1f1" horizontal={false} />
              <XAxis type="number" hide />
              <YAxis dataKey="name" type="category" stroke="#9ca3af" width={90} tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ backgroundColor: "white", borderColor: "#e5e7eb", color: "#111827" }} cursor={{ fill: "#f9fafb" }} />
              <Bar dataKey="impressions" barSize={18} radius={[0, 6, 6, 0]}>
                {CHANNEL_DETAILS.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.sentiment === "positive" ? "#10b981" : entry.sentiment === "negative" ? "#f43f5e" : "#6b7280"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-2xl border border-neutral-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
          <BarChart2 size={14} /> Live Signals
        </div>
        <p className="mt-2 text-sm text-neutral-600">{move.aiSummary}</p>
        <div className="mt-4 space-y-2">
          <button onClick={() => openMuse({ sourceName: move.name })} className="flex w-full items-center justify-between rounded-lg border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-800 hover:border-neutral-300">
            Open in Muse <ArrowUpRight size={14} />
          </button>
          <button className="flex w-full items-center justify-between rounded-lg border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-800 hover:border-neutral-300">
            Auto-create tasks <ArrowUpRight size={14} />
          </button>
        </div>
      </div>
    </div>

    <div className="rounded-2xl border border-neutral-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-neutral-100 px-5 py-4">
        <div>
          <p className="text-[11px] uppercase tracking-wide text-neutral-500">Creative Assets</p>
          <h3 className="text-lg font-semibold">Performance by asset</h3>
        </div>
        <div className="flex gap-2 text-neutral-500">
          <button className="inline-flex items-center gap-2 rounded-full border border-neutral-200 px-3 py-1 text-xs font-semibold hover:border-neutral-300">
            <Filter size={14} /> Filter
          </button>
        </div>
      </div>
      <div className="divide-y divide-neutral-100">
        {ASSETS.map((asset) => (
          <div key={asset.id} className="flex flex-col gap-3 px-5 py-4 transition hover:bg-neutral-50 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center gap-2">
                {asset.sentiment === "winner" && <Star size={14} className="text-amber-500" />}
                <p className="text-sm font-semibold">{asset.name}</p>
              </div>
              <p className="text-xs text-neutral-500">{asset.type} • {asset.cohort}</p>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <Mini label="Reach" value={asset.exposures.toLocaleString()} />
              <Mini label="Conv." value={asset.conversions} />
              <Mini label="Score" value={asset.score} />
              <div className="flex gap-2">
                <button className="rounded-full border border-neutral-200 px-3 py-1 text-xs font-semibold text-neutral-700 hover:border-neutral-300">Winner</button>
                <button className="rounded-full border border-neutral-200 px-3 py-1 text-xs font-semibold text-neutral-700 hover:border-neutral-300">Flop</button>
                <button onClick={() => setAsset(asset)} className="rounded-full bg-neutral-900 px-3 py-1 text-xs font-semibold text-white hover:bg-neutral-800">Open</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const InfoCard = ({ label, value, sub, pill, icon }) => (
  <div className="rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm">
    <div className="mb-1 flex items-start justify-between">
      <p className="text-[11px] uppercase tracking-wide text-neutral-500">{label}</p>
      {pill}
    </div>
    <div className="text-2xl font-semibold text-neutral-900">{value}</div>
    {sub && <p className="text-xs text-neutral-500">{sub}</p>}
    {icon && <div className="mt-2 text-neutral-500">{icon}</div>}
  </div>
);

const Mini = ({ label, value }) => (
  <div>
    <p className="text-[11px] uppercase tracking-wide text-neutral-500">{label}</p>
    <p className="text-sm font-semibold text-neutral-900">{value}</p>
  </div>
);

const PulseStat = ({ label, value, tone }) => {
  const tones = {
    emerald: "bg-emerald-50 text-emerald-700 border-emerald-100",
    amber: "bg-amber-50 text-amber-700 border-amber-100",
    rose: "bg-rose-50 text-rose-700 border-rose-100",
  };
  return (
    <div className={cn("rounded-xl border p-4", tones[tone] || "bg-neutral-50 text-neutral-700 border-neutral-100")}>
      <div className="text-3xl font-semibold">{value}</div>
      <div className="text-xs font-semibold uppercase tracking-wide">{label}</div>
    </div>
  );
};

const AssetInspector = ({ asset, onClose, onOpenMuse }) => {
  if (!asset) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur">
      <div className="w-full max-w-3xl overflow-hidden rounded-3xl border border-neutral-200 bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-neutral-100 px-5 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">Asset</p>
            <h3 className="text-lg font-semibold">{asset.name}</h3>
            <p className="text-xs text-neutral-500">{asset.type} • {asset.cohort}</p>
          </div>
          <button onClick={onClose} className="rounded-full border border-neutral-200 p-2 text-neutral-500">
            <X size={16} />
          </button>
        </div>
        <div className="grid gap-0 md:grid-cols-2">
          <div className="flex flex-col gap-2 p-5 text-sm text-neutral-700">
            <Mini label="Reach" value={asset.exposures.toLocaleString()} />
            <Mini label="Conversions" value={asset.conversions} />
            <Mini label="Score" value={asset.score} />
          </div>
          <div className="flex flex-col gap-2 border-l border-neutral-100 p-5">
            <button className="rounded-lg border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-700 hover:border-neutral-300">Mark winner</button>
            <button className="rounded-lg border border-neutral-200 px-3 py-2 text-sm font-semibold text-neutral-700 hover:border-neutral-300">Mark flop</button>
            <button onClick={() => onOpenMuse(asset)} className="rounded-lg bg-neutral-900 px-3 py-2 text-sm font-semibold text-white hover:bg-neutral-800">
              Open in Muse
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const StrategyModal = ({ action, onClose }) => {
  if (!action) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur">
      <div className="w-full max-w-lg rounded-3xl border border-neutral-200 bg-white p-6 shadow-2xl">
        <div className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
          <Brain size={14} /> Strategy Update
        </div>
        <h3 className="text-xl font-semibold text-neutral-900">{action.title}</h3>
        <p className="mt-2 text-sm text-neutral-600">{action.reason}</p>
        <div className="mt-4 space-y-2 rounded-xl border border-neutral-100 bg-neutral-50 p-4 text-sm text-neutral-800">
          <div className="flex items-center gap-2"><Check size={14} className="text-emerald-600" /> Auto-create tasks in Moves</div>
          <div className="flex items-center gap-2"><Check size={14} className="text-emerald-600" /> Update forecasts</div>
          <div className="flex items-center gap-2"><Check size={14} className="text-emerald-600" /> Notify team</div>
        </div>
        <div className="mt-6 flex gap-3">
          <button onClick={onClose} className="flex-1 rounded-lg border border-neutral-200 px-4 py-2 text-sm font-semibold text-neutral-700 hover:border-neutral-300">Cancel</button>
          <button onClick={onClose} className="flex-1 rounded-lg bg-neutral-900 px-4 py-2 text-sm font-semibold text-white hover:bg-neutral-800">Confirm & Execute</button>
        </div>
      </div>
    </div>
  );
};

const MuseBridge = ({ context, onClose }) => {
  if (!context) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur">
      <div className="w-full max-w-xl rounded-3xl border border-neutral-200 bg-white p-6 shadow-2xl">
        <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-neutral-500">
          <Sparkles size={14} /> Matrix → Muse
        </div>
        <div className="space-y-2 text-sm text-neutral-800">
          <Row label="Source" value={context.sourceName || "Move analysis"} />
          <Row label="Cohort" value={context.cohort || "N/A"} />
          <Row label="Pattern" value={context.pattern || context.tag || "N/A"} />
        </div>
        <button onClick={onClose} className="mt-4 inline-flex items-center justify-center gap-2 rounded-lg bg-neutral-900 px-4 py-2 text-sm font-semibold text-white hover:bg-neutral-800">
          Start ideation <ArrowUpRight size={14} />
        </button>
      </div>
    </div>
  );
};

const Row = ({ label, value }) => (
  <div className="flex items-center justify-between rounded-lg border border-neutral-100 bg-neutral-50 px-3 py-2">
    <span className="text-xs font-semibold uppercase tracking-wide text-neutral-500">{label}</span>
    <span className="text-sm font-semibold text-neutral-900">{value}</span>
  </div>
);
