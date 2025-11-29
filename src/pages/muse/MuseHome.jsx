import React, { useState, useMemo, useEffect } from "react";
import { Link } from "react-router-dom";
import { PenSquare, Repeat, Sparkles, MoveRight, ArrowUpRight, Link as LinkIcon } from "lucide-react";
import { MuseHeader } from "./components/MuseHeader";
import { SectionCard } from "./components/SectionCard";
import { SummaryCard } from "./components/SummaryCard";
import { Pill } from "./components/Pill";
import { WEEK_OPTIONS, BRANDS, MODEL_ROUTES, MOVES, COHORTS, VOICE, INSIGHTS, IDEA_STACK, STATUS_COLORS } from "./data";
import { cn } from "../../utils/cn";
import { museService } from "../../services/museService";
import { useWorkspace } from "../../context/WorkspaceContext";
import { toast } from "../../components/Toast";

export default function MuseHome() {
    const { currentWorkspace } = useWorkspace();
    const [week, setWeek] = useState(WEEK_OPTIONS[0]);
    const [brand, setBrand] = useState(BRANDS[0]);
    const [modelRoute] = useState(MODEL_ROUTES[0]);
    const [statusFilter, setStatusFilter] = useState("All");
    const [channelFilter, setChannelFilter] = useState("All");
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (currentWorkspace?.id) {
            loadAssets();
        }
    }, [currentWorkspace?.id]);

    const loadAssets = async () => {
        try {
            setLoading(true);
            const data = await museService.getAssets(currentWorkspace.id);
            setAssets(data);
        } catch (error) {
            console.error("Error loading assets:", error);
            toast.error("Failed to load assets");
        } finally {
            setLoading(false);
        }
    };

    const filteredAssets = useMemo(() => {
        return assets.filter((asset) => {
            const statusMatch = statusFilter === "All" || asset.status === statusFilter;
            const channelMatch = channelFilter === "All" || asset.type === channelFilter; // Mapping channel to type for now
            return statusMatch && channelMatch;
        });
    }, [assets, statusFilter, channelFilter]);

    return (
        <div className="min-h-screen bg-[#FAFAFA]"> {/* Very light grey/cream */}
            <MuseHeader
                week={week} setWeek={setWeek}
                brand={brand} setBrand={setBrand}
                modelRoute={modelRoute}
                subtitle="Content factory for this week’s Moves"
            />

            <div className="mx-auto flex max-w-[1600px] flex-col gap-8 px-6 py-8">

                {/* Navigation Tabs (Visual only here, actual nav via Link) */}
                <div className="flex items-center gap-1 rounded-full bg-white p-1 shadow-sm border border-black/5 w-fit">
                    <Link to="/muse" className="rounded-full bg-black px-5 py-2 text-sm font-medium text-white shadow-sm">Muse Home</Link>
                    <Link to="/muse/workspace" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Draft Workspace</Link>
                    <Link to="/muse/repurpose" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Repurpose Studio</Link>
                    <Link to="/muse/hooks" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Hooks Lab</Link>
                </div>

                {/* Summary Cards */}
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    <SummaryCard label="Active Move" value={MOVES[0].name} helper="Tied to 3 assets" accent="Focus" />
                    <SummaryCard label="Current draft" value="IG Carousel – Pricing" helper="In review" accent="In review" />
                    <SummaryCard label="Signal" value="Face-led hooks" helper="Impact: Medium" accent="Live" />
                </div>

                {/* Main 3-Column Layout */}
                <div className="grid gap-8 lg:grid-cols-[320px_1fr_320px] items-start">

                    {/* Left: Context */}
                    <div className="space-y-6">
                        <SectionCard title="This Week’s Moves">
                            <div className="space-y-4">
                                {MOVES.map((move) => (
                                    <div key={move.id} className="group rounded-2xl border border-neutral-100 bg-neutral-50/50 p-4 transition-colors hover:bg-white hover:shadow-sm">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <p className="text-sm font-bold text-neutral-900">{move.name}</p>
                                                <div className="mt-2 flex flex-wrap gap-1.5">
                                                    {move.cohorts.map((c) => (
                                                        <Pill key={c} className="bg-white text-neutral-600 border border-neutral-200/50 shadow-sm">
                                                            {c}
                                                        </Pill>
                                                    ))}
                                                </div>
                                            </div>
                                            <Pill className="bg-black text-white">{move.progress}</Pill>
                                        </div>
                                        <div className="mt-3 flex items-center gap-2">
                                            {move.channels.map((ch) => (
                                                <span key={ch} className="flex h-6 w-6 items-center justify-center rounded-full bg-white text-[10px] font-bold text-neutral-600 shadow-sm border border-neutral-100">
                                                    {ch}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </SectionCard>

                        <SectionCard title="Cohorts in Focus">
                            <div className="space-y-3">
                                {COHORTS.map((cohort) => (
                                    <div key={cohort.name} className="rounded-2xl border border-neutral-100 bg-neutral-50/50 p-4 transition-colors hover:bg-white hover:shadow-sm">
                                        <p className="text-sm font-bold text-neutral-900">{cohort.name}</p>
                                        <p className="mt-1 text-xs font-medium text-neutral-500">{cohort.note}</p>
                                    </div>
                                ))}
                            </div>
                        </SectionCard>

                        <SectionCard title="Brand Voice">
                            <div className="flex flex-wrap gap-2">
                                {VOICE.map((tag) => (
                                    <Pill key={tag} className="bg-white text-neutral-700 border border-neutral-200/50 shadow-sm">
                                        {tag}
                                    </Pill>
                                ))}
                            </div>
                        </SectionCard>
                    </div>

                    {/* Center: Workbench */}
                    <div className="space-y-8">
                        <div className="grid gap-4 sm:grid-cols-3">
                            <Link to="/moves" className="group relative flex flex-col justify-between rounded-3xl border border-black/5 bg-white p-6 text-left shadow-sm transition-all hover:-translate-y-1 hover:shadow-md">
                                <div className="flex items-center gap-3 text-sm font-bold text-neutral-900">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-100 text-neutral-900 group-hover:bg-black group-hover:text-white transition-colors">
                                        <PenSquare size={16} />
                                    </div>
                                    Draft for a Move
                                </div>
                                <div className="mt-4">
                                    <p className="text-xs font-medium text-neutral-500">Create content linked to a Move & KPI</p>
                                </div>
                                <div className="absolute right-4 top-4 opacity-0 transition-opacity group-hover:opacity-100">
                                    <MoveRight size={16} className="text-neutral-400" />
                                </div>
                            </Link>
                            <button className="group relative flex flex-col justify-between rounded-3xl border border-black/5 bg-white p-6 text-left shadow-sm transition-all hover:-translate-y-1 hover:shadow-md">
                                <div className="flex items-center gap-3 text-sm font-bold text-neutral-900">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-100 text-neutral-900 group-hover:bg-black group-hover:text-white transition-colors">
                                        <Repeat size={16} />
                                    </div>
                                    Repurpose content
                                </div>
                                <div className="mt-4">
                                    <p className="text-xs font-medium text-neutral-500">Turn podcasts, threads, and blogs into assets</p>
                                </div>
                                <div className="absolute right-4 top-4 opacity-0 transition-opacity group-hover:opacity-100">
                                    <MoveRight size={16} className="text-neutral-400" />
                                </div>
                            </button>
                            <button className="group relative flex flex-col justify-between rounded-3xl border border-black/5 bg-white p-6 text-left shadow-sm transition-all hover:-translate-y-1 hover:shadow-md">
                                <div className="flex items-center gap-3 text-sm font-bold text-neutral-900">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-100 text-neutral-900 group-hover:bg-black group-hover:text-white transition-colors">
                                        <Sparkles size={16} />
                                    </div>
                                    Explore hooks
                                </div>
                                <div className="mt-4">
                                    <p className="text-xs font-medium text-neutral-500">Mine and test hooks for your cohorts</p>
                                </div>
                                <div className="absolute right-4 top-4 opacity-0 transition-opacity group-hover:opacity-100">
                                    <MoveRight size={16} className="text-neutral-400" />
                                </div>
                            </button>
                        </div>

                        <SectionCard
                            title="This week’s assets"
                            actions={
                                <div className="flex items-center gap-3">
                                    <select
                                        value={statusFilter}
                                        onChange={(e) => setStatusFilter(e.target.value)}
                                        className="h-8 rounded-full border border-neutral-200 bg-white px-3 text-xs font-semibold text-neutral-700 focus:border-black focus:outline-none"
                                    >
                                        {["All", "Draft", "In review", "Ready", "Published"].map((s) => (
                                            <option key={s}>{s}</option>
                                        ))}
                                    </select>
                                    <div className="flex gap-1 rounded-full bg-neutral-100 p-1">
                                        {["All", "IG", "LI", "Email", "WA", "LP"].map((ch) => (
                                            <button
                                                key={ch}
                                                onClick={() => setChannelFilter(ch)}
                                                className={cn(
                                                    "rounded-full px-3 py-1 text-[10px] font-bold transition-all",
                                                    channelFilter === ch
                                                        ? "bg-white text-black shadow-sm"
                                                        : "text-neutral-500 hover:text-neutral-900"
                                                )}
                                            >
                                                {ch}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            }
                        >
                            <div className="grid gap-4">
                                {filteredAssets.map((asset) => (
                                    <div key={asset.id} className="group relative flex flex-col gap-4 rounded-2xl border border-neutral-100 bg-neutral-50/50 p-5 transition-all hover:bg-white hover:shadow-md">
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center gap-3">
                                                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-xs font-bold text-neutral-900 shadow-sm border border-neutral-100">
                                                    {asset.channel}
                                                </span>
                                                <div className="flex flex-col">
                                                    <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">{asset.type}</span>
                                                    <h4 className="font-bold text-neutral-900">{asset.title}</h4>
                                                </div>
                                            </div>
                                            <Pill className={cn("shadow-sm", STATUS_COLORS[asset.status] || STATUS_COLORS.Draft)}>
                                                {asset.status}
                                            </Pill>
                                        </div>

                                        <div className="flex items-center gap-2 text-xs text-neutral-500">
                                            <span className="font-medium text-neutral-900">{asset.move}</span>
                                            <span className="h-1 w-1 rounded-full bg-neutral-300"></span>
                                            {asset.cohorts.map((c) => (
                                                <span key={c}>{c}</span>
                                            ))}
                                        </div>

                                        <div className="flex items-center justify-between border-t border-neutral-100 pt-4">
                                            <div className="flex flex-wrap gap-2">
                                                {asset.tags.map((t) => (
                                                    <span key={t} className="rounded-md bg-white px-2 py-1 text-[10px] font-medium text-neutral-600 border border-neutral-100">
                                                        {t}
                                                    </span>
                                                ))}
                                            </div>
                                            <div className="flex gap-2 opacity-0 transition-opacity group-hover:opacity-100">
                                                <Link
                                                    to={`/muse/assets/${asset.id}`}
                                                    className="inline-flex items-center gap-1.5 rounded-full bg-black px-4 py-1.5 text-[11px] font-bold text-white shadow-sm hover:bg-neutral-800"
                                                >
                                                    Open <ArrowUpRight size={12} />
                                                </Link>
                                                <button className="inline-flex items-center gap-1.5 rounded-full border border-neutral-200 bg-white px-4 py-1.5 text-[11px] font-bold text-neutral-700 shadow-sm hover:border-neutral-300">
                                                    <LinkIcon size={12} /> Canva
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </SectionCard>
                    </div>

                    {/* Right: Intelligence */}
                    <div className="space-y-6">
                        <SectionCard title="Insights from Matrix">
                            <div className="space-y-3">
                                {INSIGHTS.map((insight, i) => (
                                    <div key={i} className="flex flex-col gap-3 rounded-2xl border border-neutral-100 bg-neutral-50/50 p-4 transition-colors hover:bg-white hover:shadow-sm">
                                        <p className="text-sm font-medium text-neutral-800 leading-relaxed">{insight}</p>
                                        <button className="self-start text-[11px] font-bold uppercase tracking-wider text-purple-600 hover:text-purple-700">Apply Insight</button>
                                    </div>
                                ))}
                            </div>
                        </SectionCard>

                        <SectionCard title="Idea Stack" subtitle="Hook & idea stash">
                            <div className="space-y-3">
                                {IDEA_STACK.map((idea) => (
                                    <div key={idea.id} className="group rounded-2xl border border-neutral-100 bg-neutral-50/50 p-4 transition-colors hover:bg-white hover:shadow-sm">
                                        <p className="text-sm font-medium text-neutral-900 italic">"{idea.text.replace(/"/g, '')}"</p>
                                        <div className="mt-3 flex flex-wrap gap-1.5">
                                            {idea.tags.map((tag) => (
                                                <span key={tag} className="rounded-md bg-white px-2 py-1 text-[10px] font-medium text-neutral-500 border border-neutral-100">
                                                    {tag}
                                                </span>
                                            ))}
                                        </div>
                                        <div className="mt-4 flex gap-2 opacity-0 transition-opacity group-hover:opacity-100">
                                            <button className="flex-1 rounded-full bg-black px-3 py-1.5 text-[10px] font-bold text-white hover:bg-neutral-800">
                                                Use
                                            </button>
                                            <button className="rounded-full border border-neutral-200 bg-white px-3 py-1.5 text-[10px] font-bold text-neutral-600 hover:border-neutral-300">
                                                Archive
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </SectionCard>
                    </div>

                </div>
            </div>
        </div>
    );
}
