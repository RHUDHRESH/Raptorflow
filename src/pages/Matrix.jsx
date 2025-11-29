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
  Target,
  Layout
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
import {
  HeroSection,
  StatCard,
  LuxeCard,
  LuxeButton,
  LuxeBadge,
  FilterPills,
  staggerContainer,
  fadeInUp,
  LuxeSkeleton
} from '../components/ui/PremiumUI';
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "../utils/cn";

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

const Progress = ({ current, total }) => {
  const pct = Math.min((current / total) * 100, 100);
  return (
    <div className="h-2 w-full rounded-full bg-neutral-100 overflow-hidden">
      <motion.div
        className="h-full bg-neutral-900"
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 1, ease: "easeOut" }}
      />
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

  const tabs = [
    { value: "moves", label: "Moves" },
    { value: "cohorts", label: "Cohorts" },
    { value: "patterns", label: "Patterns" },
    { value: "pulse", label: "Pulse" }
  ];

  return (
    <motion.div
      className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={staggerContainer}
    >
      {/* Page Title */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="The Matrix"
          subtitle="Cross-campaign intelligence, pattern recognition, and anomaly detection."
          metrics={[
            { label: 'Active Moves', value: CAMPAIGNS.length.toString() },
            { label: 'Cohorts', value: COHORTS.length.toString() },
            { label: 'Signals', value: PATTERNS.length.toString() }
          ]}
        />
      </motion.div>

      {!selectedMove ? (
        <>
          <motion.div variants={fadeInUp} className="flex flex-col md:flex-row justify-between items-center gap-4">
            <FilterPills
              filters={tabs}
              activeFilter={tab}
              onFilterChange={(t) => { setSelectedMove(null); setTab(t); }}
            />

            {tab === "moves" && (
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search moves..."
                    className="pl-9 pr-4 py-2 bg-white border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-neutral-900 w-64"
                  />
                </div>
                <div className="flex gap-2">
                  {["all", "active"].map((s) => (
                    <button
                      key={s}
                      onClick={() => setStatusFilter(s)}
                      className={cn(
                        "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border",
                        statusFilter === s
                          ? "bg-neutral-900 text-white border-neutral-900"
                          : "bg-white text-neutral-600 border-neutral-200 hover:border-neutral-300"
                      )}
                    >
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </motion.div>

          <AnimatePresence mode="wait">
            {tab === "moves" && (
              <motion.div
                key="moves"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="grid grid-cols-1 gap-6 lg:grid-cols-2"
              >
                {filteredMoves.map((move) => (
                  <LuxeCard key={move.id} className="p-6 hover:shadow-md transition-shadow group">
                    <div className="flex items-start justify-between mb-6">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <Link to={`/strategy/campaigns/${move.id}`} className="text-lg font-medium text-neutral-900 hover:text-neutral-700 transition-colors">{move.name}</Link>
                          <LuxeBadge variant={
                            move.status === 'on_track' ? 'success' :
                              move.status === 'at_risk' ? 'warning' :
                                'error'
                          }>
                            {move.status.replace('_', ' ')}
                          </LuxeBadge>
                        </div>
                        <p className="text-sm text-neutral-500">{move.goal}</p>
                      </div>
                      <button className="text-neutral-400 hover:text-neutral-900 transition-colors"><MoreHorizontal size={20} /></button>
                    </div>

                    <div className="grid grid-cols-3 gap-6 mb-6">
                      <div>
                        <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-1">Progress</p>
                        <p className="text-2xl font-display font-medium text-neutral-900 mb-2">{Math.round((move.current / move.target) * 100)}%</p>
                        <Progress current={move.current} total={move.target} />
                      </div>
                      <div>
                        <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-1">Execution</p>
                        <p className="text-2xl font-display font-medium text-neutral-900">{move.tasksDone}/{move.totalTasks}</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-1">Top Channel</p>
                        <p className="text-2xl font-display font-medium text-emerald-600">{move.bestChannelMultiplier}</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-neutral-100">
                      <div className="flex items-center gap-2 text-xs font-medium text-neutral-500">
                        <Users size={14} /> {move.bestCohort}
                      </div>
                      <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <LuxeButton variant="ghost" size="sm">Review</LuxeButton>
                        <LuxeButton size="sm" onClick={() => setSelectedMove(move)}>View Matrix</LuxeButton>
                      </div>
                    </div>
                  </LuxeCard>
                ))}
              </motion.div>
            )}

            {tab === "cohorts" && (
              <motion.div
                key="cohorts"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="grid grid-cols-1 gap-6 md:grid-cols-2"
              >
                {COHORTS.map((c) => (
                  <LuxeCard key={c.id} className="p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-6">
                      <div>
                        <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-1">Cohort</p>
                        <h3 className="text-xl font-display font-medium text-neutral-900">{c.name}</h3>
                      </div>
                      <LuxeBadge variant={c.health === 'healthy' ? 'success' : 'warning'}>
                        {c.health}
                      </LuxeBadge>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div className="p-3 bg-neutral-50 rounded-lg">
                        <span className="text-xs text-neutral-500 block mb-1">Active Moves</span>
                        <span className="text-lg font-medium text-neutral-900">{c.activeMoves}</span>
                      </div>
                      <div className="p-3 bg-neutral-50 rounded-lg">
                        <span className="text-xs text-neutral-500 block mb-1">Response Rate</span>
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-medium text-neutral-900">{c.responseRate}</span>
                          {c.responseTrend === "up" ? (
                            <TrendingUp size={14} className="text-emerald-600" />
                          ) : (
                            <TrendingDown size={14} className="text-rose-500" />
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2 mb-6">
                      <div className="flex items-center gap-3 text-sm p-2 rounded-lg bg-emerald-50/50 border border-emerald-100">
                        <Star size={14} className="text-emerald-600" />
                        <span className="font-medium text-emerald-900">{c.bestPattern}</span>
                      </div>
                      <div className="flex items-center gap-3 text-sm p-2 rounded-lg bg-rose-50/50 border border-rose-100">
                        <Skull size={14} className="text-rose-600" />
                        <span className="font-medium text-rose-900">{c.deadPattern}</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <LuxeButton variant="outline" size="sm">Details</LuxeButton>
                      <LuxeButton size="sm" onClick={() => openMuse({ cohort: c.name, pattern: c.bestPattern })}>
                        Open in Muse
                      </LuxeButton>
                    </div>
                  </LuxeCard>
                ))}
              </motion.div>
            )}

            {tab === "patterns" && (
              <motion.div
                key="patterns"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-4"
              >
                {PATTERNS.map((p, idx) => (
                  <LuxeCard key={p.id} className="p-6 hover:shadow-md transition-shadow flex flex-col md:flex-row md:items-center gap-6">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-neutral-50 text-lg font-display font-medium text-neutral-900">
                      #{idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="text-lg font-medium text-neutral-900">{p.name}</h3>
                        <LuxeBadge variant={p.sentiment === 'positive' ? 'success' : 'error'}>
                          {p.performance > 0 ? '+' : ''}{p.performance}% vs baseline
                        </LuxeBadge>
                      </div>
                    </div>
                    <div className="flex gap-3 w-full md:w-auto">
                      <LuxeButton variant="outline" size="sm" className="flex-1 md:flex-none">See assets</LuxeButton>
                      {p.sentiment === "positive" && (
                        <LuxeButton
                          size="sm"
                          onClick={() => openMuse({ pattern: p.name, sourceName: "Pattern Matrix" })}
                          className="flex-1 md:flex-none"
                        >
                          Scale in Muse
                        </LuxeButton>
                      )}
                    </div>
                  </LuxeCard>
                ))}
              </motion.div>
            )}

            {tab === "pulse" && (
              <motion.div
                key="pulse"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-8"
              >
                <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                  <StatCard label="Moves On Track" value="2" icon={Check} trend="up" />
                  <StatCard label="Moves At Risk" value="1" icon={AlertCircle} trend="down" />
                  <StatCard label="Moves Failing" value="1" icon={X} trend="down" />
                </div>
                <div className="space-y-4">
                  {PULSE.map((a) => (
                    <LuxeCard key={a.id} className="p-6 hover:shadow-md transition-shadow flex flex-col md:flex-row md:items-center justify-between gap-6">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="text-lg font-medium text-neutral-900">{a.title}</h4>
                          <LuxeBadge variant={a.actionType === 'kill' ? 'error' : 'success'}>
                            {a.actionType === 'kill' ? 'High Impact' : 'Opportunity'}
                          </LuxeBadge>
                        </div>
                        <p className="text-neutral-500">{a.reason}</p>
                      </div>
                      <div className="flex gap-3 w-full md:w-auto">
                        <LuxeButton variant="ghost" size="sm" className="flex-1 md:flex-none">Ignore</LuxeButton>
                        <LuxeButton
                          size="sm"
                          onClick={() => setPulseAction(a)}
                          className={cn(
                            "flex-1 md:flex-none",
                            a.actionType === "kill" ? "bg-rose-600 hover:bg-rose-700" : "bg-emerald-600 hover:bg-emerald-700"
                          )}
                        >
                          {a.actionType === "kill" ? "Kill Move" : "Apply"}
                        </LuxeButton>
                      </div>
                    </LuxeCard>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </>
      ) : (
        <Detail move={selectedMove} onBack={() => setSelectedMove(null)} openMuse={openMuse} setAsset={setSelectedAsset} />
      )}

      {selectedAsset && <AssetInspector asset={selectedAsset} onClose={() => setSelectedAsset(null)} onOpenMuse={openMuse} />}
      {pulseAction && <StrategyModal action={pulseAction} onClose={() => setPulseAction(null)} />}
      {museContext && <MuseBridge context={museContext} onClose={() => setMuseContext(null)} />}
    </motion.div>
  );
}

const Detail = ({ move, onBack, openMuse, setAsset }) => (
  <motion.div
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -20 }}
    className="space-y-8"
  >
    <button onClick={onBack} className="inline-flex items-center gap-2 text-sm font-medium text-neutral-500 hover:text-neutral-900 transition-colors">
      <ChevronRight className="-ml-1 rotate-180" size={16} /> Back to Matrix
    </button>

    <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
      <StatCard
        label="Goal Pace"
        value={`${move.current}/${move.target}`}
        icon={Target}
        trend={move.status === 'on_track' ? 'up' : 'down'}
      />
      <StatCard
        label="Execution"
        value={`${Math.round((move.tasksDone / move.totalTasks) * 100)}%`}
        change={`${move.totalTasks - move.tasksDone} tasks remaining`}
        icon={Activity}
      />
      <StatCard
        label="Top Channel"
        value={move.bestChannel}
        change={move.bestChannelMultiplier}
        icon={Zap}
        trend="up"
      />
      <StatCard
        label="Health"
        value={`${move.healthScore}/100`}
        icon={TrendingUp}
        trend={move.healthScore > 80 ? 'up' : 'down'}
      />
    </div>

    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <LuxeCard className="lg:col-span-2 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-1">Channel Breakdown</p>
            <h3 className="text-xl font-display font-medium text-neutral-900">Performance</h3>
          </div>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={CHANNEL_DETAILS} layout="vertical" margin={{ left: 0, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f1f1" horizontal={false} />
              <XAxis type="number" hide />
              <YAxis dataKey="name" type="category" stroke="#9ca3af" width={90} tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "white", borderColor: "#e5e7eb", color: "#111827", borderRadius: "8px", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                cursor={{ fill: "#f9fafb" }}
              />
              <Bar dataKey="impressions" barSize={24} radius={[0, 6, 6, 0]}>
                {CHANNEL_DETAILS.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.sentiment === "positive" ? "#10b981" : entry.sentiment === "negative" ? "#f43f5e" : "#9ca3af"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </LuxeCard>

      <LuxeCard className="p-6 bg-gradient-to-br from-neutral-900 to-neutral-800 text-white border-none">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-white/60 mb-4">
          <Sparkles size={14} /> Live Signals
        </div>
        <p className="text-lg font-medium leading-relaxed mb-8">{move.aiSummary}</p>
        <div className="space-y-3">
          <button onClick={() => openMuse({ sourceName: move.name })} className="flex w-full items-center justify-between rounded-xl bg-white/10 hover:bg-white/20 px-4 py-3 text-sm font-medium transition-colors">
            Open in Muse <ArrowUpRight size={14} />
          </button>
          <button className="flex w-full items-center justify-between rounded-xl bg-white/10 hover:bg-white/20 px-4 py-3 text-sm font-medium transition-colors">
            Auto-create tasks <ArrowUpRight size={14} />
          </button>
        </div>
      </LuxeCard>
    </div>

    <LuxeCard className="overflow-hidden">
      <div className="flex items-center justify-between border-b border-neutral-100 px-6 py-4 bg-neutral-50/50">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-1">Creative Assets</p>
          <h3 className="text-lg font-medium text-neutral-900">Performance by asset</h3>
        </div>
        <LuxeButton variant="outline" size="sm">
          <Filter size={14} className="mr-2" /> Filter
        </LuxeButton>
      </div>
      <div className="divide-y divide-neutral-100">
        {ASSETS.map((asset) => (
          <div key={asset.id} className="flex flex-col gap-4 px-6 py-4 transition hover:bg-neutral-50 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                {asset.sentiment === "winner" && <Star size={14} className="text-amber-500 fill-amber-500" />}
                <p className="text-sm font-medium text-neutral-900">{asset.name}</p>
              </div>
              <p className="text-xs text-neutral-500">{asset.type} • {asset.cohort}</p>
            </div>
            <div className="flex flex-wrap items-center gap-8 text-sm">
              <Mini label="Reach" value={asset.exposures.toLocaleString()} />
              <Mini label="Conv." value={asset.conversions} />
              <Mini label="Score" value={asset.score} />
              <div className="flex gap-2">
                <LuxeButton variant="ghost" size="sm">Winner</LuxeButton>
                <LuxeButton variant="ghost" size="sm">Flop</LuxeButton>
                <LuxeButton size="sm" onClick={() => setAsset(asset)}>Open</LuxeButton>
              </div>
            </div>
          </div>
        ))}
      </div>
    </LuxeCard>
  </motion.div>
);

const Mini = ({ label, value }) => (
  <div>
    <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-0.5">{label}</p>
    <p className="text-sm font-medium text-neutral-900">{value}</p>
  </div>
);

const AssetInspector = ({ asset, onClose, onOpenMuse }) => {
  if (!asset) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-3xl overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-2xl"
      >
        <div className="flex items-center justify-between border-b border-neutral-100 px-6 py-4">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 mb-1">Asset</p>
            <h3 className="text-xl font-display font-medium text-neutral-900">{asset.name}</h3>
            <p className="text-xs text-neutral-500">{asset.type} • {asset.cohort}</p>
          </div>
          <button onClick={onClose} className="rounded-full p-2 text-neutral-400 hover:bg-neutral-100 hover:text-neutral-900 transition-colors">
            <X size={20} />
          </button>
        </div>
        <div className="grid gap-0 md:grid-cols-2">
          <div className="flex flex-col gap-6 p-6">
            <div className="grid grid-cols-3 gap-4">
              <Mini label="Reach" value={asset.exposures.toLocaleString()} />
              <Mini label="Conversions" value={asset.conversions} />
              <Mini label="Score" value={asset.score} />
            </div>
            <div className="p-4 bg-neutral-50 rounded-xl border border-neutral-100">
              <p className="text-sm text-neutral-600 leading-relaxed">
                AI Analysis: This asset is performing 2.4x better than average for the {asset.cohort} cohort.
              </p>
            </div>
          </div>
          <div className="flex flex-col gap-3 border-l border-neutral-100 p-6 bg-neutral-50/30">
            <LuxeButton variant="outline" className="justify-start">Mark as Winner</LuxeButton>
            <LuxeButton variant="outline" className="justify-start">Mark as Flop</LuxeButton>
            <LuxeButton onClick={() => onOpenMuse(asset)} className="justify-start">
              Open in Muse
            </LuxeButton>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

const StrategyModal = ({ action, onClose }) => {
  if (!action) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-lg rounded-2xl border border-neutral-200 bg-white p-6 shadow-2xl"
      >
        <div className="mb-4 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-neutral-500">
          <Brain size={14} /> Strategy Update
        </div>
        <h3 className="text-xl font-display font-medium text-neutral-900 mb-2">{action.title}</h3>
        <p className="text-sm text-neutral-600 leading-relaxed mb-6">{action.reason}</p>

        <div className="space-y-3 rounded-xl border border-neutral-100 bg-neutral-50 p-4 text-sm text-neutral-800 mb-6">
          <div className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center"><Check size={12} className="text-emerald-600" /></div> Auto-create tasks in Moves</div>
          <div className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center"><Check size={12} className="text-emerald-600" /></div> Update forecasts</div>
          <div className="flex items-center gap-3"><div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center"><Check size={12} className="text-emerald-600" /></div> Notify team</div>
        </div>

        <div className="flex gap-3">
          <LuxeButton variant="outline" onClick={onClose} className="flex-1">Cancel</LuxeButton>
          <LuxeButton onClick={onClose} className="flex-1">Confirm & Execute</LuxeButton>
        </div>
      </motion.div>
    </div>
  );
};

const MuseBridge = ({ context, onClose }) => {
  if (!context) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-xl rounded-2xl border border-neutral-200 bg-white p-6 shadow-2xl"
      >
        <div className="mb-4 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-neutral-500">
          <Sparkles size={14} /> Matrix → Muse
        </div>
        <div className="space-y-3 text-sm text-neutral-800 mb-6">
          <Row label="Source" value={context.sourceName || "Move analysis"} />
          <Row label="Cohort" value={context.cohort || "N/A"} />
          <Row label="Pattern" value={context.pattern || context.tag || "N/A"} />
        </div>
        <LuxeButton onClick={onClose} className="w-full">
          Start ideation <ArrowUpRight size={14} className="ml-2" />
        </LuxeButton>
      </motion.div>
    </div>
  );
};

const Row = ({ label, value }) => (
  <div className="flex items-center justify-between rounded-lg border border-neutral-100 bg-neutral-50 px-4 py-3">
    <span className="text-xs font-bold uppercase tracking-wide text-neutral-500">{label}</span>
    <span className="text-sm font-medium text-neutral-900">{value}</span>
  </div>
);
