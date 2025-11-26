import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    Users,
    Plus,
    Search,
    Target,
    TrendingUp,
    AlertCircle,
    CheckCircle2,
    X,
    Sparkles,
    ArrowRight,
    Clock,
    Zap,
    Shield,
    Eye,
    MessageSquare,
    Loader2
} from 'lucide-react';
import { cn } from '../../utils/cn';
import cohortService from '../../lib/services/cohortService';

import { INITIAL_COHORTS, JOURNEY_STAGES } from '../../data/mockCohorts';

export default function CohortsEnhancedLuxe() {
    const navigate = useNavigate();
    const [cohorts, setCohorts] = useState(INITIAL_COHORTS);
    const [searchTerm, setSearchTerm] = useState('');
    // New Cohort State
    const [showNewCohortModal, setShowNewCohortModal] = useState(false);
    const [newCohort, setNewCohort] = useState({ name: '', description: '', avatar: '👥' });
    const [isCreating, setIsCreating] = useState(false);

    const filteredCohorts = cohorts.filter(cohort =>
        cohort.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        cohort.description.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleCreateCohort = async () => {
        if (!newCohort.name) return;
        setIsCreating(true);

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 800));

        const createdCohort = {
            id: `c${Date.now()}`,
            ...newCohort,
            health_score: 100,
            size: 0,
            journey_distribution: { unaware: 1, problem_aware: 0, solution_aware: 0, product_aware: 0, most_aware: 0 },
            buying_triggers: [],
            decision_criteria: [],
            objection_map: [],
            attention_windows: [],
        };

        setCohorts([createdCohort, ...cohorts]);
        setIsCreating(false);
        setShowNewCohortModal(false);
        setNewCohort({ name: '', description: '', avatar: '👥' });

        // Navigate to the new cohort
        navigate(`/cohorts/${createdCohort.id}`);
    };

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Hero Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="runway-card relative overflow-hidden p-10"
            >
                <div className="absolute inset-0 bg-gradient-to-r from-white via-neutral-50 to-white" />
                <div className="relative z-10">
                    <Link
                        to="/strategy"
                        className="inline-flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors mb-4"
                    >
                        <ArrowRight className="w-4 h-4 rotate-180" />
                        <span className="text-sm">Back to Strategy</span>
                    </Link>

                    <div className="flex items-center gap-3 mb-4">
                        <span className="micro-label tracking-[0.5em]">Strategic Intelligence</span>
                        <span className="h-px w-16 bg-neutral-200" />
                    </div>

                    <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased mb-4">
                        Enhanced Cohorts
                    </h1>

                    <p className="text-neutral-600 max-w-2xl">
                        Deep customer intelligence with buying triggers, decision criteria, and strategic insights
                    </p>
                </div>
            </motion.div>

            {/* Search & Actions */}
            <div className="flex items-center gap-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Search cohorts..."
                        className="w-full pl-12 pr-4 py-3 border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
                    />
                </div>

                <button
                    onClick={() => setShowNewCohortModal(true)}
                    className="flex items-center gap-2 px-5 py-3 bg-neutral-900 text-white hover:bg-neutral-800 font-mono text-sm uppercase tracking-[0.2em]"
                >
                    <Plus className="w-4 h-4" />
                    New Cohort
                </button>
            </div>

            {/* Cohorts Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCohorts.map((cohort, index) => (
                    <motion.div
                        key={cohort.id}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                    >
                        <button
                            onClick={() => navigate(`/cohorts/${cohort.id}`)}
                            className="w-full runway-card p-5 hover:shadow-xl transition-all text-left group h-full flex flex-col"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="text-3xl">{cohort.avatar}</div>
                                    <div>
                                        <h3 className="font-serif text-xl text-neutral-900 group-hover:text-neutral-700 transition-colors">
                                            {cohort.name}
                                        </h3>
                                        <p className="text-sm text-neutral-600 line-clamp-1">{cohort.description}</p>
                                    </div>
                                </div>

                                <span className={cn(
                                    "px-2 py-1 text-xs border font-medium",
                                    cohort.health_score >= 80 ? "bg-neutral-900 text-white border-neutral-900" :
                                        cohort.health_score >= 60 ? "bg-neutral-100 text-neutral-900 border-neutral-200" :
                                            "bg-white text-neutral-500 border-neutral-200"
                                )}>
                                    {cohort.health_score}%
                                </span>
                            </div>

                            {/* Journey Distribution */}
                            <div className="mb-3 flex-1">
                                <p className="text-[10px] uppercase tracking-wider text-neutral-400 mb-1.5">Journey Distribution</p>
                                <div className="flex gap-0.5 h-1.5 rounded-full overflow-hidden">
                                    {Object.entries(cohort.journey_distribution).map(([stage, value]) => {
                                        const stageInfo = JOURNEY_STAGES.find(s => s.id === stage);
                                        return (
                                            <div
                                                key={stage}
                                                className={cn("h-full", stageInfo?.color)}
                                                style={{ width: `${value * 100}%` }}
                                            />
                                        );
                                    })}
                                </div>
                                <div className="flex justify-between mt-1 text-[10px] text-neutral-500">
                                    <span>Unaware</span>
                                    <span>Most Aware</span>
                                </div>
                            </div>

                            {/* Quick Stats */}
                            <div className="grid grid-cols-2 gap-4 pt-3 border-t border-neutral-100 mt-auto">
                                <div>
                                    <p className="text-xs text-neutral-500">Size</p>
                                    <p className="font-semibold text-neutral-900">{cohort.size.toLocaleString()}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-neutral-500">Triggers</p>
                                    <p className="font-semibold text-neutral-900">{cohort.buying_triggers?.length || 0}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-2 mt-3 text-xs font-medium text-neutral-400 group-hover:text-neutral-900 transition-colors">
                                <Eye className="w-4 h-4" />
                                View Strategic Intelligence
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </div>
                        </button>
                    </motion.div>
                ))}
            </div>

            {/* New Cohort Modal */}
            <AnimatePresence>
                {showNewCohortModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                        onClick={() => setShowNewCohortModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()}
                            className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6"
                        >
                            <h2 className="font-serif text-2xl text-neutral-900 mb-6">Create New Cohort</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-1">Cohort Name</label>
                                    <input
                                        type="text"
                                        value={newCohort.name}
                                        onChange={(e) => setNewCohort({ ...newCohort, name: e.target.value })}
                                        placeholder="e.g., Enterprise CTOs"
                                        className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                        autoFocus
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-1">Description</label>
                                    <textarea
                                        value={newCohort.description}
                                        onChange={(e) => setNewCohort({ ...newCohort, description: e.target.value })}
                                        placeholder="Who are they?"
                                        rows={3}
                                        className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-1">Avatar</label>
                                    <input
                                        type="text"
                                        value={newCohort.avatar}
                                        onChange={(e) => setNewCohort({ ...newCohort, avatar: e.target.value })}
                                        className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                    />
                                </div>
                            </div>

                            <div className="flex gap-3 mt-8">
                                <button
                                    onClick={() => setShowNewCohortModal(false)}
                                    className="flex-1 px-4 py-2 border border-neutral-200 text-neutral-600 rounded-lg hover:bg-neutral-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleCreateCohort}
                                    disabled={!newCohort.name || isCreating}
                                    className="flex-1 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 disabled:opacity-50 flex items-center justify-center gap-2"
                                >
                                    {isCreating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                                    Create Cohort
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
