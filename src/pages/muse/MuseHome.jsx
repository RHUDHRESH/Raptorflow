import React, { useState, useMemo, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { PenSquare, Repeat, Sparkles, MoveRight, ArrowUpRight, Link as LinkIcon, Zap, Target, Users, Layout } from "lucide-react";
import { WEEK_OPTIONS, BRANDS, MODEL_ROUTES, MOVES, COHORTS, VOICE, INSIGHTS, IDEA_STACK, STATUS_COLORS } from "./data";
import { cn } from "../../utils/cn";
import { museService } from "../../services/museService";
import { useWorkspace } from "../../context/WorkspaceContext";
import { toast } from "../../components/Toast";
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
} from "../../components/ui/PremiumUI";
import { motion } from "framer-motion";

export default function MuseHome() {
    const { currentWorkspace } = useWorkspace();
    const navigate = useNavigate();
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

    const channelFilters = [
        { value: "All", label: "All Channels" },
        { value: "IG", label: "Instagram" },
        { value: "LI", label: "LinkedIn" },
        { value: "Email", label: "Email" },
        { value: "WA", label: "WhatsApp" },
        { value: "LP", label: "Landing Page" }
    ];

    return (
        <motion.div
            className="max-w-[1600px] mx-auto px-6 py-8 space-y-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={staggerContainer}
        >
            {/* Header */}
            <motion.div variants={fadeInUp}>
                <HeroSection
                    title="Muse Content Factory"
                    subtitle="Orchestrate your content strategy for this week's Moves."
                    metrics={[
                        { label: 'Active Assets', value: assets.length.toString() },
                        { label: 'Drafts', value: assets.filter(a => a.status === 'Draft').length.toString() },
                        { label: 'Published', value: assets.filter(a => a.status === 'Published').length.toString() }
                    ]}
                    actions={
                        <div className="flex gap-3">
                            <LuxeButton onClick={() => navigate('/muse/workspace')}>
                                <PenSquare className="w-4 h-4 mr-2" />
                                New Draft
                            </LuxeButton>
                            <LuxeButton variant="outline" onClick={() => navigate('/muse/repurpose')}>
                                <Repeat className="w-4 h-4 mr-2" />
                                Repurpose
                            </LuxeButton>
                        </div>
                    }
                />
            </motion.div>

            {/* Summary Cards */}
            <motion.div
                className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
                variants={staggerContainer}
            >
                <StatCard
                    label="Active Move"
                    value={MOVES[0].name}
                    change="Tied to 3 assets"
                    icon={Target}
                    trend="up"
                />
                <StatCard
                    label="Current Draft"
                    value="IG Carousel"
                    change="In review"
                    icon={PenSquare}
                    trend="neutral"
                />
                <StatCard
                    label="Top Signal"
                    value="Face-led hooks"
                    change="Impact: Medium"
                    icon={Zap}
                    trend="up"
                />
            </motion.div>

            {/* Main 3-Column Layout */}
            <div className="grid gap-8 lg:grid-cols-[320px_1fr_320px] items-start">

                {/* Left: Context */}
                <motion.div variants={fadeInUp} className="space-y-6">
                    <LuxeCard title="This Week's Moves">
                        <div className="space-y-4">
                            {MOVES.map((move) => (
                                <div key={move.id} className="group rounded-xl border border-neutral-100 bg-neutral-50/50 p-4 transition-colors hover:bg-white hover:shadow-sm">
                                    <div className="flex items-start justify-between mb-2">
                                        <div>
                                            <p className="text-sm font-medium text-neutral-900">{move.name}</p>
                                            <div className="mt-2 flex flex-wrap gap-1.5">
                                                {move.cohorts.map((c) => (
                                                    <LuxeBadge key={c} variant="neutral" className="text-[10px] py-0.5 px-2">
                                                        {c}
                                                    </LuxeBadge>
                                                ))}
                                            </div>
                                        </div>
                                        <LuxeBadge variant="dark" className="text-[10px] py-0.5 px-2">{move.progress}</LuxeBadge>
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
                    </LuxeCard>

                    <LuxeCard title="Cohorts in Focus">
                        <div className="space-y-3">
                            {COHORTS.map((cohort) => (
                                <div key={cohort.name} className="rounded-xl border border-neutral-100 bg-neutral-50/50 p-4 transition-colors hover:bg-white hover:shadow-sm">
                                    <p className="text-sm font-medium text-neutral-900">{cohort.name}</p>
                                    <p className="mt-1 text-xs text-neutral-500">{cohort.note}</p>
                                </div>
                            ))}
                        </div>
                    </LuxeCard>

                    <LuxeCard title="Brand Voice">
                        <div className="flex flex-wrap gap-2">
                            {VOICE.map((tag) => (
                                <LuxeBadge key={tag} variant="neutral">
                                    {tag}
                                </LuxeBadge>
                            ))}
                        </div>
                    </LuxeCard>
                </motion.div>

                {/* Center: Workbench */}
                <motion.div variants={fadeInUp} className="space-y-8">
                    <div className="grid gap-4 sm:grid-cols-3">
                        <Link to="/muse/workspace" className="group relative flex flex-col justify-between rounded-2xl border border-neutral-200 bg-white p-6 text-left shadow-sm transition-all hover:-translate-y-1 hover:shadow-md hover:border-neutral-300">
                            <div className="flex items-center gap-3 text-sm font-medium text-neutral-900">
                                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-neutral-100 text-neutral-900 group-hover:bg-neutral-900 group-hover:text-white transition-colors">
                                    <PenSquare size={18} />
                                </div>
                                Draft for a Move
                            </div>
                            <div className="mt-4">
                                <p className="text-xs text-neutral-500">Create content linked to a Move & KPI</p>
                            </div>
                        </Link>
                        <Link to="/muse/repurpose" className="group relative flex flex-col justify-between rounded-2xl border border-neutral-200 bg-white p-6 text-left shadow-sm transition-all hover:-translate-y-1 hover:shadow-md hover:border-neutral-300">
                            <div className="flex items-center gap-3 text-sm font-medium text-neutral-900">
                                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-neutral-100 text-neutral-900 group-hover:bg-neutral-900 group-hover:text-white transition-colors">
                                    <Repeat size={18} />
                                </div>
                                Repurpose content
                            </div>
                            <div className="mt-4">
                                <p className="text-xs text-neutral-500">Turn podcasts, threads, and blogs into assets</p>
                            </div>
                        </Link>
                        <Link to="/muse/hooks" className="group relative flex flex-col justify-between rounded-2xl border border-neutral-200 bg-white p-6 text-left shadow-sm transition-all hover:-translate-y-1 hover:shadow-md hover:border-neutral-300">
                            <div className="flex items-center gap-3 text-sm font-medium text-neutral-900">
                                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-neutral-100 text-neutral-900 group-hover:bg-neutral-900 group-hover:text-white transition-colors">
                                    <Sparkles size={18} />
                                </div>
                                Explore hooks
                            </div>
                            <div className="mt-4">
                                <p className="text-xs text-neutral-500">Mine and test hooks for your cohorts</p>
                            </div>
                        </Link>
                    </div>

                    <LuxeCard className="p-6">
                        <div className="flex flex-col gap-6">
                            <div className="flex items-center justify-between">
                                <h3 className="font-display text-xl font-medium text-neutral-900">This Week's Assets</h3>
                                <div className="flex items-center gap-4">
                                    <select
                                        value={statusFilter}
                                        onChange={(e) => setStatusFilter(e.target.value)}
                                        className="h-9 rounded-lg border border-neutral-200 bg-white px-3 text-sm font-medium text-neutral-700 focus:border-neutral-900 focus:ring-1 focus:ring-neutral-900 outline-none"
                                    >
                                        {["All", "Draft", "In review", "Ready", "Published"].map((s) => (
                                            <option key={s}>{s}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <FilterPills
                                filters={channelFilters}
                                activeFilter={channelFilter}
                                onFilterChange={setChannelFilter}
                            />

                            <div className="grid gap-4">
                                {loading ? (
                                    <div className="space-y-4">
                                        {[1, 2, 3].map(i => (
                                            <LuxeSkeleton key={i} className="h-32 w-full rounded-xl" />
                                        ))}
                                    </div>
                                ) : filteredAssets.length === 0 ? (
                                    <div className="text-center py-12 border-2 border-dashed border-neutral-100 rounded-xl">
                                        <PenSquare className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
                                        <h3 className="text-lg font-medium text-neutral-900 mb-2">No assets found</h3>
                                        <p className="text-neutral-500">Try adjusting your filters or create a new draft.</p>
                                    </div>
                                ) : (
                                    filteredAssets.map((asset) => (
                                        <div key={asset.id} className="group relative flex flex-col gap-4 rounded-xl border border-neutral-100 bg-neutral-50/50 p-6 transition-all hover:bg-white hover:shadow-md hover:border-neutral-200">
                                            <div className="flex items-start justify-between">
                                                <div className="flex items-center gap-4">
                                                    <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-xs font-bold text-neutral-900 shadow-sm border border-neutral-100">
                                                        {asset.channel}
                                                    </span>
                                                    <div className="flex flex-col">
                                                        <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 mb-1">{asset.type}</span>
                                                        <h4 className="font-medium text-lg text-neutral-900">{asset.title}</h4>
                                                    </div>
                                                </div>
                                                <LuxeBadge variant={
                                                    asset.status === 'Published' ? 'dark' :
                                                        asset.status === 'Ready' ? 'success' :
                                                            'neutral'
                                                }>
                                                    {asset.status}
                                                </LuxeBadge>
                                            </div>

                                            <div className="flex items-center gap-2 text-xs text-neutral-500 ml-14">
                                                <span className="font-medium text-neutral-900">{asset.move}</span>
                                                <span className="h-1 w-1 rounded-full bg-neutral-300"></span>
                                                {asset.cohorts.map((c) => (
                                                    <span key={c}>{c}</span>
                                                ))}
                                            </div>

                                            <div className="flex items-center justify-between border-t border-neutral-100 pt-4 mt-2 ml-14">
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
                                                        className="inline-flex items-center gap-1.5 rounded-lg bg-neutral-900 px-4 py-2 text-xs font-medium text-white shadow-sm hover:bg-neutral-800 transition-colors"
                                                    >
                                                        Open <ArrowUpRight size={14} />
                                                    </Link>
                                                    <button className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-4 py-2 text-xs font-medium text-neutral-700 shadow-sm hover:border-neutral-300 transition-colors">
                                                        <LinkIcon size={14} /> Canva
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </LuxeCard>
                </motion.div>

                {/* Right: Intelligence */}
                <motion.div variants={fadeInUp} className="space-y-6">
                    <LuxeCard title="Insights from Matrix">
                        <div className="space-y-3">
                            {INSIGHTS.map((insight, i) => (
                                <div key={i} className="flex flex-col gap-3 rounded-xl border border-neutral-100 bg-neutral-50/50 p-4 transition-colors hover:bg-white hover:shadow-sm">
                                    <p className="text-sm text-neutral-700 leading-relaxed">{insight}</p>
                                    <button className="self-start text-[10px] font-bold uppercase tracking-wider text-neutral-900 hover:text-neutral-600 transition-colors">Apply Insight</button>
                                </div>
                            ))}
                        </div>
                    </LuxeCard>

                    <LuxeCard title="Idea Stack" subtitle="Hook & idea stash">
                        <div className="space-y-3">
                            {IDEA_STACK.map((idea) => (
                                <div key={idea.id} className="group rounded-xl border border-neutral-100 bg-neutral-50/50 p-4 transition-colors hover:bg-white hover:shadow-sm">
                                    <p className="text-sm font-medium text-neutral-900 italic">"{idea.text.replace(/"/g, '')}"</p>
                                    <div className="mt-3 flex flex-wrap gap-1.5">
                                        {idea.tags.map((tag) => (
                                            <span key={tag} className="rounded-md bg-white px-2 py-1 text-[10px] font-medium text-neutral-500 border border-neutral-100">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                    <div className="mt-4 flex gap-2 opacity-0 transition-opacity group-hover:opacity-100">
                                        <button className="flex-1 rounded-lg bg-neutral-900 px-3 py-1.5 text-[10px] font-bold text-white hover:bg-neutral-800 transition-colors">
                                            Use
                                        </button>
                                        <button className="rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-[10px] font-bold text-neutral-600 hover:border-neutral-300 transition-colors">
                                            Archive
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </LuxeCard>
                </motion.div>

            </div>
        </motion.div>
    );
}
