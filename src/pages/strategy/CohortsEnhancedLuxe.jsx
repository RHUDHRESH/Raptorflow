import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    Plus,
    Search,
    ArrowRight,
    Eye,
    Loader2,
    Users,
    Target,
    Brain,
    Sparkles
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { INITIAL_COHORTS, JOURNEY_STAGES } from '../../data/mockCohorts';
import {
    HeroSection,
    StatCard,
    LuxeCard,
    LuxeButton,
    LuxeBadge,
    LuxeModal,
    LuxeInput,
    staggerContainer,
    fadeInUp
} from '../../components/ui/PremiumUI';

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
                    title="Cohorts Intelligence"
                    subtitle="Deep customer intelligence with buying triggers, decision criteria, and strategic insights."
                    metrics={[
                        { label: 'Total Cohorts', value: cohorts.length.toString() },
                        { label: 'Avg Health', value: '87%' },
                        { label: 'Total Reach', value: '12.5k' }
                    ]}
                    actions={
                        <LuxeButton
                            onClick={() => setShowNewCohortModal(true)}
                            className="bg-white text-neutral-900 hover:bg-neutral-100 border-none"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            New Cohort
                        </LuxeButton>
                    }
                />
            </motion.div>

            {/* Search and Filter */}
            <motion.div variants={fadeInUp} className="flex flex-col md:flex-row justify-between items-center gap-4">
                <div className="relative w-full md:w-96">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                    <input
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Search cohorts..."
                        className="w-full pl-9 pr-4 py-2 bg-white border border-neutral-200 rounded-xl text-sm focus:outline-none focus:ring-1 focus:ring-neutral-900"
                    />
                </div>
            </motion.div>

            {/* Cohorts Overview */}
            <motion.div
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                variants={staggerContainer}
            >
                {filteredCohorts.map((cohort, index) => (
                    <motion.div
                        key={cohort.id}
                        variants={fadeInUp}
                    >
                        <LuxeCard
                            onClick={() => navigate(`/cohorts/${cohort.id}`)}
                            className="h-full flex flex-col hover:shadow-lg transition-all cursor-pointer group p-6"
                        >
                            <div className="flex items-start justify-between mb-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-neutral-50 flex items-center justify-center text-2xl shadow-sm border border-neutral-100">
                                        {cohort.avatar}
                                    </div>
                                    <div>
                                        <h3 className="font-display text-xl font-medium text-neutral-900 group-hover:text-neutral-700 transition-colors">
                                            {cohort.name}
                                        </h3>
                                        <p className="text-sm text-neutral-500 line-clamp-1">{cohort.description}</p>
                                    </div>
                                </div>

                                <LuxeBadge variant={
                                    cohort.health_score >= 80 ? "success" :
                                        cohort.health_score >= 60 ? "warning" : "error"
                                }>
                                    {cohort.health_score}%
                                </LuxeBadge>
                            </div>

                            {/* Journey Distribution */}
                            <div className="mb-8 flex-1">
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold">Journey Distribution</p>
                                </div>
                                <div className="flex gap-1 h-2 rounded-full overflow-hidden bg-neutral-100">
                                    {Object.entries(cohort.journey_distribution).map(([stage, value]) => {
                                        const stageInfo = JOURNEY_STAGES.find(s => s.id === stage);
                                        return (
                                            <div
                                                key={stage}
                                                className={cn("h-full transition-all duration-500", stageInfo?.color)}
                                                style={{ width: `${value * 100}%` }}
                                            />
                                        );
                                    })}
                                </div>
                                <div className="flex justify-between mt-2 text-[10px] font-medium text-neutral-400">
                                    <span>Unaware</span>
                                    <span>Most Aware</span>
                                </div>
                            </div>

                            {/* Buying Signals Preview */}
                            <div className="mb-8">
                                <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-3">Buying Signals</p>
                                <div className="flex flex-wrap gap-2">
                                    {cohort.buying_triggers?.slice(0, 3).map((trigger, i) => (
                                        <span key={i} className="px-2.5 py-1 rounded-lg bg-neutral-50 border border-neutral-100 text-[11px] font-medium text-neutral-600">
                                            {trigger.trigger}
                                        </span>
                                    ))}
                                    {(cohort.buying_triggers?.length || 0) > 3 && (
                                        <span className="px-2.5 py-1 rounded-lg bg-neutral-50 text-[11px] font-medium text-neutral-400">
                                            +{cohort.buying_triggers.length - 3} more
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Quick Stats */}
                            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-neutral-100 mt-auto">
                                <div>
                                    <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-1">Size</p>
                                    <div className="flex items-center gap-2">
                                        <Users className="w-4 h-4 text-neutral-400" />
                                        <p className="font-medium text-neutral-900">{cohort.size.toLocaleString()}</p>
                                    </div>
                                </div>
                                <div>
                                    <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold mb-1">Triggers</p>
                                    <div className="flex items-center gap-2">
                                        <Target className="w-4 h-4 text-neutral-400" />
                                        <p className="font-medium text-neutral-900">{cohort.buying_triggers?.length || 0}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between mt-6 pt-4 border-t border-neutral-100">
                                <span className="text-xs font-medium text-neutral-400 group-hover:text-neutral-900 transition-colors flex items-center gap-2">
                                    <Brain className="w-3 h-3" />
                                    Strategic Intelligence
                                </span>
                                <div className="w-8 h-8 rounded-full bg-neutral-50 flex items-center justify-center text-neutral-400 group-hover:bg-neutral-900 group-hover:text-white transition-all">
                                    <ArrowRight className="w-4 h-4" />
                                </div>
                            </div>
                        </LuxeCard>
                    </motion.div>
                ))}
            </motion.div>

            {/* New Cohort Modal */}
            <LuxeModal
                isOpen={showNewCohortModal}
                onClose={() => setShowNewCohortModal(false)}
                title="Create New Cohort"
            >
                <div className="space-y-6">
                    <LuxeInput
                        label="Cohort Name"
                        value={newCohort.name}
                        onChange={(e) => setNewCohort({ ...newCohort, name: e.target.value })}
                        placeholder="e.g., Enterprise CTOs"
                        autoFocus
                    />
                    <div>
                        <label className="block text-sm font-medium text-neutral-900 mb-2">Description</label>
                        <textarea
                            value={newCohort.description}
                            onChange={(e) => setNewCohort({ ...newCohort, description: e.target.value })}
                            placeholder="Who are they? What defines them?"
                            rows={4}
                            className="w-full px-4 py-3 bg-neutral-50 border border-neutral-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-neutral-900 focus:bg-white transition-all resize-none text-sm"
                        />
                    </div>
                    <LuxeInput
                        label="Avatar (Emoji)"
                        value={newCohort.avatar}
                        onChange={(e) => setNewCohort({ ...newCohort, avatar: e.target.value })}
                        placeholder="👥"
                    />

                    <div className="flex gap-3 mt-8 pt-4 border-t border-neutral-100">
                        <LuxeButton
                            variant="ghost"
                            onClick={() => setShowNewCohortModal(false)}
                            className="flex-1"
                        >
                            Cancel
                        </LuxeButton>
                        <LuxeButton
                            onClick={handleCreateCohort}
                            disabled={!newCohort.name || isCreating}
                            isLoading={isCreating}
                            className="flex-1 bg-neutral-900 text-white hover:bg-neutral-800"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Create Cohort
                        </LuxeButton>
                    </div>
                </div>
            </LuxeModal>
        </motion.div>
    );
}
