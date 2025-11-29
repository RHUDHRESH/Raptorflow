import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    Plus,
    Search,
    ArrowRight,
    Eye,
    Loader2
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { INITIAL_COHORTS, JOURNEY_STAGES } from '../../data/mockCohorts';
import { PageHeader, LuxeHeading, LuxeButton, LuxeCard, LuxeInput, LuxeBadge, LuxeModal } from '../../components/ui/PremiumUI';
import { pageTransition, fadeInUp, staggerContainer } from '../../utils/animations';

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
            className="space-y-8 animate-fade-in p-6 max-w-7xl mx-auto"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
        >
            {/* Page Title (Task 22) */}
            <PageHeader
                backUrl="/strategy"
                title="Enhanced Cohorts"
                subtitle="Deep customer intelligence with buying triggers, decision criteria, and strategic insights"
                action={
                    <LuxeButton
                        onClick={() => setShowNewCohortModal(true)}
                        icon={Plus}
                    >
                        New Cohort
                    </LuxeButton>
                }
            />

            {/* Search */}
            <div className="max-w-md">
                <LuxeInput
                    icon={Search}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search cohorts..."
                />
            </div>

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
                            className="h-full flex flex-col hover:border-neutral-400 cursor-pointer group"
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

                                <LuxeBadge variant={
                                    cohort.health_score >= 80 ? "dark" :
                                        cohort.health_score >= 60 ? "neutral" : "danger"
                                }>
                                    {cohort.health_score}%
                                </LuxeBadge>
                            </div>

                            {/* Journey Distribution */}
                            <div className="mb-6 flex-1">
                                <p className="text-[10px] uppercase tracking-wider text-neutral-400 mb-2">Journey Distribution</p>
                                <div className="flex gap-0.5 h-2 rounded-full overflow-hidden">
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
                                <div className="flex justify-between mt-2 text-[10px] text-neutral-500">
                                    <span>Unaware</span>
                                    <span>Most Aware</span>
                                </div>
                            </div>

                            {/* Buying Signals Preview (Task 22) */}
                            <div className="mb-6">
                                <p className="text-[10px] uppercase tracking-wider text-neutral-400 mb-2">Buying Signals</p>
                                <div className="flex flex-wrap gap-2">
                                    {cohort.buying_triggers?.slice(0, 3).map((trigger, i) => (
                                        <span key={i} className="px-2 py-1 rounded-md bg-neutral-50 border border-neutral-100 text-[10px] font-medium text-neutral-600">
                                            {trigger.trigger}
                                        </span>
                                    ))}
                                    {(cohort.buying_triggers?.length || 0) > 3 && (
                                        <span className="px-2 py-1 rounded-md bg-neutral-50 text-[10px] text-neutral-400">
                                            +{cohort.buying_triggers.length - 3} more
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Quick Stats */}
                            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-neutral-100 mt-auto">
                                <div>
                                    <p className="text-xs text-neutral-500 uppercase tracking-wider">Size</p>
                                    <p className="font-semibold text-neutral-900">{cohort.size.toLocaleString()}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-neutral-500 uppercase tracking-wider">Triggers</p>
                                    <p className="font-semibold text-neutral-900">{cohort.buying_triggers?.length || 0}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-2 mt-4 text-xs font-medium text-neutral-400 group-hover:text-neutral-900 transition-colors">
                                <Eye className="w-4 h-4" />
                                View Strategic Intelligence
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
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
                <div className="space-y-4">
                    <LuxeInput
                        label="Cohort Name"
                        value={newCohort.name}
                        onChange={(e) => setNewCohort({ ...newCohort, name: e.target.value })}
                        placeholder="e.g., Enterprise CTOs"
                        autoFocus
                    />
                    <div>
                        <label className="block text-sm font-medium text-neutral-700 mb-1">Description</label>
                        <textarea
                            value={newCohort.description}
                            onChange={(e) => setNewCohort({ ...newCohort, description: e.target.value })}
                            placeholder="Who are they?"
                            rows={3}
                            className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none bg-neutral-50"
                        />
                    </div>
                    <LuxeInput
                        label="Avatar (Emoji)"
                        value={newCohort.avatar}
                        onChange={(e) => setNewCohort({ ...newCohort, avatar: e.target.value })}
                    />

                    <div className="flex gap-3 mt-8 pt-4">
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
                            className="flex-1"
                            icon={Plus}
                        >
                            Create Cohort
                        </LuxeButton>
                    </div>
                </div>
            </LuxeModal>
        </motion.div>
    );
}
