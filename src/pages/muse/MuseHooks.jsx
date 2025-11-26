import React, { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
    Sparkles,
    Heart,
    TrendingUp,
    Zap,
    Star,
    Copy,
    RefreshCw,
    Filter,
    Search,
    Plus
} from "lucide-react";
import { MuseHeader } from "./components/MuseHeader";
import { cn } from "../../utils/cn";

const HOOK_CATEGORIES = [
    { id: 'all', label: 'All Hooks' },
    { id: 'curiosity', label: 'Curiosity' },
    { id: 'controversy', label: 'Controversy' },
    { id: 'story', label: 'Story' },
    { id: 'question', label: 'Question' },
    { id: 'stat', label: 'Stat/Fact' },
];

const MOCK_HOOKS = [
    {
        id: 1,
        text: "I spent $50,000 learning this lesson so you don't have to:",
        category: 'curiosity',
        score: 92,
        saves: 1247,
        cohort: 'Founders'
    },
    {
        id: 2,
        text: "Everyone talks about product-market fit. Nobody talks about founder-market fit.",
        category: 'controversy',
        score: 88,
        saves: 892,
        cohort: 'Startup Founders'
    },
    {
        id: 3,
        text: "3 years ago, I was broke. Today, I run a 7-figure business. Here's what changed:",
        category: 'story',
        score: 95,
        saves: 2103,
        cohort: 'Entrepreneurs'
    },
    {
        id: 4,
        text: "What if I told you that your biggest weakness is actually your biggest strength?",
        category: 'question',
        score: 85,
        saves: 654,
        cohort: 'All'
    },
    {
        id: 5,
        text: "87% of marketers fail because they skip this one step:",
        category: 'stat',
        score: 90,
        saves: 1456,
        cohort: 'Marketers'
    },
    {
        id: 6,
        text: "The uncomfortable truth about scaling that nobody wants to hear:",
        category: 'controversy',
        score: 91,
        saves: 1789,
        cohort: 'CEOs'
    },
];

export default function MuseHooks() {
    const [week, setWeek] = useState("Week 42");
    const [brand, setBrand] = useState("RaptorFlow");
    const [activeCategory, setActiveCategory] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [favorites, setFavorites] = useState([]);
    const [generatingNew, setGeneratingNew] = useState(false);

    const filteredHooks = MOCK_HOOKS.filter(hook => {
        const matchesCategory = activeCategory === 'all' || hook.category === activeCategory;
        const matchesSearch = hook.text.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesCategory && matchesSearch;
    });

    const toggleFavorite = (hookId) => {
        setFavorites(prev =>
            prev.includes(hookId)
                ? prev.filter(id => id !== hookId)
                : [...prev, hookId]
        );
    };

    const handleGenerateNew = () => {
        setGeneratingNew(true);
        setTimeout(() => {
            setGeneratingNew(false);
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-[#FAFAFA]">
            <MuseHeader
                week={week} setWeek={setWeek}
                brand={brand} setBrand={setBrand}
                modelRoute="GPT-4o"
                title="Hooks Lab"
                subtitle="Discover and test high-performing hooks for your content"
            />

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Navigation Tabs */}
                <div className="flex items-center gap-1 rounded-full bg-white p-1 shadow-sm border border-black/5 w-fit mb-8">
                    <Link to="/muse" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Muse Home</Link>
                    <Link to="/muse/workspace" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Draft Workspace</Link>
                    <Link to="/muse/repurpose" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Repurpose Studio</Link>
                    <Link to="/muse/hooks" className="rounded-full bg-black px-5 py-2 text-sm font-medium text-white shadow-sm">Hooks Lab</Link>
                </div>

                {/* Controls */}
                <div className="flex flex-col md:flex-row gap-4 mb-8">
                    <div className="flex-1 relative">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                        <input
                            type="text"
                            placeholder="Search hooks..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-12 pr-4 py-3 rounded-lg border border-neutral-200 bg-white focus:outline-none focus:border-neutral-900 transition-all"
                        />
                    </div>
                    <button
                        onClick={handleGenerateNew}
                        disabled={generatingNew}
                        className="flex items-center gap-2 bg-neutral-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-neutral-800 disabled:opacity-50 transition-all"
                    >
                        {generatingNew ? (
                            <>
                                <RefreshCw className="w-5 h-5 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5" />
                                Generate New Hooks
                            </>
                        )}
                    </button>
                </div>

                {/* Category Filters */}
                <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
                    {HOOK_CATEGORIES.map(category => (
                        <button
                            key={category.id}
                            onClick={() => setActiveCategory(category.id)}
                            className={cn(
                                "px-4 py-2 rounded-lg border-2 whitespace-nowrap transition-all",
                                activeCategory === category.id
                                    ? "border-neutral-900 bg-neutral-900 text-white"
                                    : "border-neutral-200 text-neutral-600 hover:border-neutral-400"
                            )}
                        >
                            {category.label}
                        </button>
                    ))}
                </div>

                {/* Hooks Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredHooks.map((hook, index) => (
                        <motion.div
                            key={hook.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="bg-white rounded-2xl border border-neutral-200 p-6 shadow-sm hover:shadow-md transition-all group"
                        >
                            {/* Hook Text */}
                            <div className="mb-4">
                                <p className="font-serif text-lg text-neutral-900 leading-relaxed italic">
                                    "{hook.text}"
                                </p>
                            </div>

                            {/* Metadata */}
                            <div className="flex items-center gap-3 mb-4 text-xs text-neutral-600">
                                <span className="px-2 py-1 bg-neutral-100 rounded-md font-medium">
                                    {hook.category}
                                </span>
                                <span className="px-2 py-1 bg-neutral-100 rounded-md font-medium">
                                    {hook.cohort}
                                </span>
                            </div>

                            {/* Stats */}
                            <div className="flex items-center gap-4 mb-4 text-sm">
                                <div className="flex items-center gap-1">
                                    <TrendingUp className="w-4 h-4 text-green-600" />
                                    <span className="font-medium text-neutral-900">{hook.score}</span>
                                    <span className="text-neutral-500">score</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <Star className="w-4 h-4 text-amber-500" />
                                    <span className="font-medium text-neutral-900">{hook.saves}</span>
                                    <span className="text-neutral-500">saves</span>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2">
                                <button
                                    onClick={() => toggleFavorite(hook.id)}
                                    className={cn(
                                        "flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg border-2 transition-all",
                                        favorites.includes(hook.id)
                                            ? "border-red-500 bg-red-50 text-red-600"
                                            : "border-neutral-200 text-neutral-600 hover:border-neutral-400"
                                    )}
                                >
                                    <Heart className={cn("w-4 h-4", favorites.includes(hook.id) && "fill-current")} />
                                    <span className="text-sm font-medium">
                                        {favorites.includes(hook.id) ? 'Saved' : 'Save'}
                                    </span>
                                </button>
                                <button className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg border-2 border-neutral-200 text-neutral-600 hover:border-neutral-400 transition-all">
                                    <Copy className="w-4 h-4" />
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Empty State */}
                {filteredHooks.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <div className="w-16 h-16 rounded-full bg-neutral-100 flex items-center justify-center mb-4">
                            <Search className="w-8 h-8 text-neutral-400" />
                        </div>
                        <h3 className="font-serif text-xl text-neutral-900 mb-2">No Hooks Found</h3>
                        <p className="text-sm text-neutral-600 max-w-sm">
                            Try adjusting your search or category filter
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
