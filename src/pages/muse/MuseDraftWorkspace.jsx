import React, { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
    ArrowLeft,
    Sparkles,
    Save,
    Send,
    Bot,
    RefreshCw,
    CheckCircle2,
    Target,
    Users,
    MessageSquare,
    Zap,
    ChevronRight,
    Maximize2,
    Minimize2,
    Copy,
    Share2
} from "lucide-react";
import { MuseHeader } from "./components/MuseHeader";
import { cn } from "../../utils/cn";

// --- Mock Data (Simulating Backend) ---
const MOCK_MOVES = [
    {
        id: 'm1',
        name: '14-Day Conversion Sprint',
        goal: 'Conversion',
        journey_from: 'Solution Aware',
        journey_to: 'Product Aware',
        campaign: 'Q4 Enterprise Sprint'
    },
    {
        id: 'm2',
        name: 'Authority Proof Loop',
        goal: 'Authority',
        journey_from: 'Problem Aware',
        journey_to: 'Solution Aware',
        campaign: 'Founder Community Launch'
    }
];

const MOCK_COHORTS = [
    {
        id: 'c1',
        name: 'Enterprise CTOs',
        buying_triggers: ['End of quarter budget', 'Competitor price hike'],
        pain_points: ['Legacy system bloat', 'Vendor lock-in'],
        tone: 'Professional, direct, data-backed'
    },
    {
        id: 'c4',
        name: 'Creators',
        buying_triggers: ['Algorithm changes', 'Burnout'],
        pain_points: ['Inconsistent income', 'Platform risk'],
        tone: 'Authentic, empathetic, high-energy'
    }
];

const MOCK_POSITIONING = {
    statement: "For [Target] who [Problem], RaptorFlow is a [Category] that [Benefit]. Unlike [Competitor], we [Differentiator].",
    proof_points: ["3x faster execution", "AI-powered strategy", "Unified workflow"]
};

export default function MuseDraftWorkspace() {
    const [searchParams] = useSearchParams();
    const [week, setWeek] = useState("Week 42");
    const [brand, setBrand] = useState("RaptorFlow");

    // Context State
    const [moveContext, setMoveContext] = useState(null);
    const [cohortContext, setCohortContext] = useState(null);
    const [loading, setLoading] = useState(true);

    // Editor State
    const [title, setTitle] = useState("");
    const [content, setContent] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);
    const [aiPrompt, setAiPrompt] = useState("");
    const [activeTab, setActiveTab] = useState("write"); // write, preview

    // UI State
    const [sidebarOpen, setSidebarOpen] = useState(true);

    useEffect(() => {
        // Simulate fetching context from URL params
        const moveId = searchParams.get('moveId');
        const cohortId = searchParams.get('cohortId');

        setTimeout(() => {
            if (moveId) {
                const move = MOCK_MOVES.find(m => m.id === moveId);
                setMoveContext(move);
            }
            if (cohortId) {
                const cohort = MOCK_COHORTS.find(c => c.id === cohortId);
                setCohortContext(cohort);
            }
            setLoading(false);
        }, 600);
    }, [searchParams]);

    const handleGenerate = () => {
        if (!aiPrompt && !moveContext) return;
        setIsGenerating(true);

        // Simulate AI generation
        setTimeout(() => {
            const generatedTitle = moveContext
                ? `${moveContext.goal} Post for ${cohortContext?.name || 'Audience'}`
                : "New Strategic Post";

            const generatedContent = `Here is a draft based on your ${moveContext?.name || 'strategy'}...\n\n` +
                `**Hook:** Are you tired of ${cohortContext?.pain_points?.[0] || 'the status quo'}?\n\n` +
                `**Body:** We know that ${cohortContext?.buying_triggers?.[0] || 'timing is everything'}. ` +
                `That's why we built a solution that actually works.\n\n` +
                `**Proof:** ${MOCK_POSITIONING.proof_points[0]}.\n\n` +
                `**CTA:** Comment "READY" to get started.`;

            setTitle(generatedTitle);
            setContent(generatedContent);
            setIsGenerating(false);
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-[#FAFAFA] flex flex-col">
            <MuseHeader
                week={week} setWeek={setWeek}
                brand={brand} setBrand={setBrand}
                modelRoute="GPT-4o"
                title="Draft Workspace"
                subtitle={moveContext ? `Drafting for: ${moveContext.name}` : "New Draft"}
            />

            <div className="flex-1 flex overflow-hidden">
                {/* --- Left Sidebar: Strategic Context --- */}
                <AnimatePresence mode="wait">
                    {sidebarOpen && (
                        <motion.aside
                            initial={{ width: 0, opacity: 0 }}
                            animate={{ width: 320, opacity: 1 }}
                            exit={{ width: 0, opacity: 0 }}
                            className="bg-white border-r border-neutral-200 overflow-y-auto hidden md:block"
                        >
                            <div className="p-6 space-y-8">
                                <div>
                                    <h3 className="micro-label mb-4">Strategic Context</h3>

                                    {loading ? (
                                        <div className="space-y-3 animate-pulse">
                                            <div className="h-20 bg-neutral-100 rounded-lg" />
                                            <div className="h-32 bg-neutral-100 rounded-lg" />
                                        </div>
                                    ) : (
                                        <div className="space-y-6">
                                            {/* Move Card */}
                                            {moveContext ? (
                                                <div className="p-4 rounded-xl bg-neutral-50 border border-neutral-100">
                                                    <div className="flex items-center gap-2 mb-2 text-neutral-900 font-serif font-medium">
                                                        <Target className="w-4 h-4" />
                                                        {moveContext.name}
                                                    </div>
                                                    <div className="space-y-2 text-xs text-neutral-600">
                                                        <div className="flex justify-between">
                                                            <span>Goal</span>
                                                            <span className="font-medium text-neutral-900">{moveContext.goal}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span>Campaign</span>
                                                            <span className="font-medium text-neutral-900 truncate max-w-[120px]">{moveContext.campaign}</span>
                                                        </div>
                                                        <div className="pt-2 border-t border-neutral-200 mt-2">
                                                            <div className="flex items-center gap-2 justify-center">
                                                                <span className="bg-neutral-200 px-1.5 py-0.5 rounded text-[10px]">{moveContext.journey_from}</span>
                                                                <ChevronRight className="w-3 h-3 text-neutral-400" />
                                                                <span className="bg-neutral-900 text-white px-1.5 py-0.5 rounded text-[10px]">{moveContext.journey_to}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="p-4 rounded-xl border border-dashed border-neutral-200 text-center text-sm text-neutral-500">
                                                    No active move selected
                                                </div>
                                            )}

                                            {/* Cohort Card */}
                                            {cohortContext ? (
                                                <div className="p-4 rounded-xl bg-neutral-50 border border-neutral-100">
                                                    <div className="flex items-center gap-2 mb-2 text-neutral-900 font-serif font-medium">
                                                        <Users className="w-4 h-4" />
                                                        {cohortContext.name}
                                                    </div>
                                                    <div className="space-y-3 text-xs">
                                                        <div>
                                                            <span className="text-neutral-500 block mb-1">Buying Triggers</span>
                                                            <div className="flex flex-wrap gap-1">
                                                                {cohortContext.buying_triggers.map(t => (
                                                                    <span key={t} className="px-1.5 py-0.5 bg-white border border-neutral-200 rounded text-neutral-700">
                                                                        {t}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </div>
                                                        <div>
                                                            <span className="text-neutral-500 block mb-1">Pain Points</span>
                                                            <ul className="list-disc list-inside text-neutral-700">
                                                                {cohortContext.pain_points.map(p => (
                                                                    <li key={p}>{p}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                        <div>
                                                            <span className="text-neutral-500 block mb-1">Tone</span>
                                                            <p className="text-neutral-700 italic">{cohortContext.tone}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="p-4 rounded-xl border border-dashed border-neutral-200 text-center text-sm text-neutral-500">
                                                    No cohort selected
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>

                                <div>
                                    <h3 className="micro-label mb-4">Positioning</h3>
                                    <div className="p-4 rounded-xl bg-neutral-900 text-white text-xs leading-relaxed opacity-90">
                                        "{MOCK_POSITIONING.statement}"
                                    </div>
                                </div>
                            </div>
                        </motion.aside>
                    )}
                </AnimatePresence>

                {/* --- Main Editor Area --- */}
                <main className="flex-1 flex flex-col relative bg-white">
                    {/* Toolbar */}
                    <div className="h-14 border-b border-neutral-100 flex items-center justify-between px-6">
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setSidebarOpen(!sidebarOpen)}
                                className="p-2 hover:bg-neutral-50 rounded-lg text-neutral-500 md:block hidden"
                            >
                                {sidebarOpen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                            </button>
                            <div className="h-4 w-px bg-neutral-200 mx-2" />
                            <Link to="/muse" className="flex items-center gap-2 text-sm text-neutral-500 hover:text-neutral-900">
                                <ArrowLeft className="w-4 h-4" />
                                Back
                            </Link>
                        </div>
                        <div className="flex items-center gap-2">
                            <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-50 rounded-lg transition-colors">
                                <Share2 className="w-3.5 h-3.5" />
                                Share
                            </button>
                            <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-50 rounded-lg transition-colors">
                                <Copy className="w-3.5 h-3.5" />
                                Copy
                            </button>
                            <button className="flex items-center gap-2 px-4 py-1.5 bg-neutral-900 text-white text-xs font-bold rounded-lg hover:bg-neutral-800 transition-colors shadow-sm">
                                <Save className="w-3.5 h-3.5" />
                                Save Draft
                            </button>
                        </div>
                    </div>

                    {/* Canvas */}
                    <div className="flex-1 overflow-y-auto">
                        <div className="max-w-3xl mx-auto py-12 px-8">
                            <input
                                type="text"
                                placeholder="Untitled Draft"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="w-full text-4xl font-serif font-medium placeholder:text-neutral-300 border-none focus:ring-0 p-0 mb-8 text-neutral-900 bg-transparent"
                            />
                            <textarea
                                placeholder="Start writing or ask AI to generate..."
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                className="w-full h-[60vh] resize-none text-lg leading-relaxed text-neutral-700 placeholder:text-neutral-300 border-none focus:ring-0 p-0 bg-transparent font-sans"
                            />
                        </div>
                    </div>

                    {/* Floating AI Bar */}
                    <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-full max-w-2xl px-4">
                        <div className="bg-white rounded-2xl shadow-2xl border border-neutral-200 p-2 flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-neutral-100 flex items-center justify-center text-neutral-500">
                                <Sparkles className="w-4 h-4" />
                            </div>
                            <input
                                type="text"
                                value={aiPrompt}
                                onChange={(e) => setAiPrompt(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                                placeholder={moveContext ? `Ask to draft a ${moveContext.goal} post...` : "Ask AI to write something..."}
                                className="flex-1 border-none focus:ring-0 text-sm bg-transparent"
                            />
                            <button
                                onClick={handleGenerate}
                                disabled={isGenerating}
                                className="p-2 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 disabled:opacity-50 transition-colors"
                            >
                                {isGenerating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ArrowLeft className="w-4 h-4 rotate-180" />}
                            </button>
                        </div>
                    </div>
                </main>

                {/* --- Right Sidebar: AI Assistant (Optional/Collapsible) --- */}
                {/* For now, keeping it simple with just the floating bar, but could expand here */}
            </div>
        </div>
    );
}
