/**
 * Enhanced Cohorts Page
 * 
 * Strategic cohort management with deep psychographics,
 * buying triggers, decision criteria, and journey tracking.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    Users,
    Plus,
    Search,
    Filter,
    TrendingUp,
    TrendingDown,
    Target,
    Zap,
    AlertCircle,
    CheckCircle2,
    Clock,
    DollarSign,
    MessageSquare,
    ArrowRight,
    Sparkles,
    BarChart3,
    Eye,
    Edit,
    Trash2,
    MoreVertical
} from 'lucide-react';
import { cn } from '../../utils/cn';

// =============================================================================
// MOCK DATA WITH ENHANCED ATTRIBUTES
// =============================================================================

const MOCK_COHORTS = [
    {
        id: 'c1',
        name: 'Enterprise CTOs',
        description: 'Tech leaders at large companies',
        health_score: 85,
        size: 1250,

        // Journey distribution
        journey_distribution: {
            unaware: 0.2,
            problem_aware: 0.3,
            solution_aware: 0.25,
            product_aware: 0.15,
            most_aware: 0.1,
        },

        // Buying triggers
        buying_triggers: [
            { trigger: 'Q4 budget pressure', strength: 'high', timing: 'Q4' },
            { trigger: 'Competitor launched new feature', strength: 'medium', timing: 'Ongoing' },
            { trigger: 'Board meeting approaching', strength: 'high', timing: 'Quarterly' },
        ],

        // Decision criteria
        decision_criteria: [
            { criterion: 'ROI proven in 90 days', weight: 0.3, deal_breaker: true },
            { criterion: 'Enterprise security', weight: 0.25, deal_breaker: true },
            { criterion: 'Easy integration', weight: 0.2, deal_breaker: false },
            { criterion: 'Vendor stability', weight: 0.15, deal_breaker: false },
            { criterion: 'Support quality', weight: 0.1, deal_breaker: false },
        ],

        // Objections
        objection_map: [
            { objection: "We don't have budget", root_cause: "Unclear ROI", response_strategy: "Show cost of inaction" },
            { objection: "We're locked into competitor", root_cause: "Switching cost fear", response_strategy: "Migration case study" },
            { objection: "Too complex to implement", root_cause: "Resource constraints", response_strategy: "White-glove onboarding" },
        ],

        // Attention windows
        attention_windows: [
            { channel: 'linkedin', best_times: ['Tue 9am', 'Wed 2pm'], receptivity: 'high', frequency_tolerance: '3x_week' },
            { channel: 'email', best_times: ['Mon 8am'], receptivity: 'medium', frequency_tolerance: 'weekly' },
        ],

        // Competitive frame
        competitive_frame: {
            direct_competitors: ['Competitor A', 'Competitor B', 'Competitor C'],
            category_alternatives: ['Doing it manually', 'Hiring an agency'],
            perceived_strengths: ['Price', 'Features'],
            perceived_weaknesses: ['Support', 'Onboarding'],
        },
    },
    {
        id: 'c2',
        name: 'Startup Founders',
        description: 'Early-stage company builders',
        health_score: 72,
        size: 850,

        journey_distribution: {
            unaware: 0.4,
            problem_aware: 0.25,
            solution_aware: 0.2,
            product_aware: 0.1,
            most_aware: 0.05,
        },

        buying_triggers: [
            { trigger: 'Just raised funding', strength: 'high', timing: 'Post-funding' },
            { trigger: 'Scaling pain points', strength: 'medium', timing: 'Ongoing' },
        ],

        decision_criteria: [
            { criterion: 'Speed to value', weight: 0.35, deal_breaker: true },
            { criterion: 'Price', weight: 0.3, deal_breaker: true },
            { criterion: 'Ease of use', weight: 0.25, deal_breaker: false },
            { criterion: 'Flexibility', weight: 0.1, deal_breaker: false },
        ],

        objection_map: [
            { objection: "Too expensive", root_cause: "Limited budget", response_strategy: "Startup pricing tier" },
            { objection: "Don't have time to learn", root_cause: "Time scarcity", response_strategy: "Quick-start templates" },
        ],

        attention_windows: [
            { channel: 'twitter', best_times: ['Daily 7am', 'Daily 6pm'], receptivity: 'high', frequency_tolerance: 'daily' },
            { channel: 'email', best_times: ['Thu 10am'], receptivity: 'medium', frequency_tolerance: '2x_week' },
        ],

        competitive_frame: {
            direct_competitors: ['DIY tools', 'Freelancers'],
            category_alternatives: ['Doing it themselves', 'Not doing marketing'],
            perceived_strengths: ['Low cost', 'Flexibility'],
            perceived_weaknesses: ['Lack of expertise', 'Time consuming'],
        },
    },
    {
        id: 'c3',
        name: 'Marketing Directors',
        description: 'Marketing leaders at mid-market',
        health_score: 91,
        size: 620,

        journey_distribution: {
            unaware: 0.15,
            problem_aware: 0.25,
            solution_aware: 0.3,
            product_aware: 0.2,
            most_aware: 0.1,
        },

        buying_triggers: [
            { trigger: 'Campaign performance review', strength: 'high', timing: 'Monthly' },
            { trigger: 'Team expansion', strength: 'medium', timing: 'Quarterly' },
        ],

        decision_criteria: [
            { criterion: 'Team collaboration features', weight: 0.3, deal_breaker: true },
            { criterion: 'Reporting & analytics', weight: 0.25, deal_breaker: false },
            { criterion: 'Integration with existing stack', weight: 0.25, deal_breaker: false },
            { criterion: 'Training & support', weight: 0.2, deal_breaker: false },
        ],

        objection_map: [
            { objection: "Team won't adopt it", root_cause: "Change resistance", response_strategy: "Change management support" },
            { objection: "Need approval from leadership", root_cause: "Budget authority", response_strategy: "Executive briefing deck" },
        ],

        attention_windows: [
            { channel: 'linkedin', best_times: ['Wed 11am', 'Fri 3pm'], receptivity: 'high', frequency_tolerance: '2x_week' },
            { channel: 'email', best_times: ['Tue 9am'], receptivity: 'high', frequency_tolerance: 'weekly' },
        ],

        competitive_frame: {
            direct_competitors: ['Marketing automation platforms', 'Project management tools'],
            category_alternatives: ['Spreadsheets', 'Multiple disconnected tools'],
            perceived_strengths: ['Comprehensive features', 'Established brands'],
            perceived_weaknesses: ['Complexity', 'High cost'],
        },
    },
];

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function CohortsEnhanced() {
    const navigate = useNavigate();

    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCohort, setSelectedCohort] = useState(null);
    const [viewMode, setViewMode] = useState('grid'); // grid | list
    const [showEnhanceModal, setShowEnhanceModal] = useState(false);

    const filteredCohorts = MOCK_COHORTS.filter(cohort =>
        cohort.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        cohort.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-white">
            {/* Header */}
            <div className="border-b border-neutral-200 bg-white">
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h1 className="font-serif text-3xl text-black mb-2">Strategic Cohorts</h1>
                            <p className="text-neutral-600">Deep customer intelligence for targeted campaigns</p>
                        </div>
                        <Link
                            to="/cohorts/new"
                            className="flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800"
                        >
                            <Plus className="w-5 h-5" />
                            New Cohort
                        </Link>
                    </div>

                    {/* Search & Filters */}
                    <div className="flex items-center gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search cohorts..."
                                className="w-full pl-10 pr-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                            />
                        </div>
                        <button className="flex items-center gap-2 px-4 py-2 border border-neutral-200 rounded-lg hover:bg-neutral-50">
                            <Filter className="w-5 h-5" />
                            Filter
                        </button>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-4 gap-4 mt-6">
                        <div className="bg-neutral-50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-neutral-600">Total Cohorts</span>
                                <Users className="w-4 h-4 text-neutral-400" />
                            </div>
                            <p className="text-2xl font-semibold text-neutral-900">{MOCK_COHORTS.length}</p>
                        </div>
                        <div className="bg-neutral-50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-neutral-600">Total Contacts</span>
                                <Target className="w-4 h-4 text-neutral-400" />
                            </div>
                            <p className="text-2xl font-semibold text-neutral-900">
                                {MOCK_COHORTS.reduce((sum, c) => sum + c.size, 0).toLocaleString()}
                            </p>
                        </div>
                        <div className="bg-neutral-50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-neutral-600">Avg Health Score</span>
                                <BarChart3 className="w-4 h-4 text-neutral-400" />
                            </div>
                            <p className="text-2xl font-semibold text-neutral-900">
                                {Math.round(MOCK_COHORTS.reduce((sum, c) => sum + c.health_score, 0) / MOCK_COHORTS.length)}%
                            </p>
                        </div>
                        <div className="bg-neutral-50 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-neutral-600">Active Campaigns</span>
                                <Zap className="w-4 h-4 text-neutral-400" />
                            </div>
                            <p className="text-2xl font-semibold text-neutral-900">5</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Cohorts Grid */}
            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredCohorts.map((cohort) => (
                        <motion.div
                            key={cohort.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-neutral-200 rounded-xl p-6 hover:shadow-lg transition-shadow cursor-pointer"
                            onClick={() => setSelectedCohort(cohort)}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="font-semibold text-lg text-neutral-900 mb-1">{cohort.name}</h3>
                                    <p className="text-sm text-neutral-600">{cohort.description}</p>
                                </div>
                                <div className={cn(
                                    "px-2 py-1 text-xs font-medium rounded",
                                    cohort.health_score >= 80 ? "bg-green-100 text-green-700" :
                                        cohort.health_score >= 60 ? "bg-amber-100 text-amber-700" :
                                            "bg-red-100 text-red-700"
                                )}>
                                    {cohort.health_score}%
                                </div>
                            </div>

                            {/* Journey Distribution */}
                            <div className="mb-4">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-xs text-neutral-500">Journey Distribution</span>
                                    <span className="text-xs text-neutral-500">{cohort.size.toLocaleString()} contacts</span>
                                </div>
                                <div className="flex gap-0.5 h-2 rounded-full overflow-hidden">
                                    {Object.entries(cohort.journey_distribution).map(([stage, value]) => (
                                        <div
                                            key={stage}
                                            className={cn(
                                                "h-full",
                                                stage === 'unaware' ? "bg-neutral-300" :
                                                    stage === 'problem_aware' ? "bg-amber-400" :
                                                        stage === 'solution_aware' ? "bg-blue-400" :
                                                            stage === 'product_aware' ? "bg-purple-400" :
                                                                "bg-green-400"
                                            )}
                                            style={{ width: `${value * 100}%` }}
                                            title={`${stage}: ${Math.round(value * 100)}%`}
                                        />
                                    ))}
                                </div>
                            </div>

                            {/* Key Metrics */}
                            <div className="grid grid-cols-2 gap-3 mb-4">
                                <div className="bg-neutral-50 rounded-lg p-3">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Zap className="w-3 h-3 text-neutral-500" />
                                        <span className="text-xs text-neutral-500">Buying Triggers</span>
                                    </div>
                                    <p className="text-sm font-semibold text-neutral-900">{cohort.buying_triggers.length}</p>
                                </div>
                                <div className="bg-neutral-50 rounded-lg p-3">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Target className="w-3 h-3 text-neutral-500" />
                                        <span className="text-xs text-neutral-500">Decision Criteria</span>
                                    </div>
                                    <p className="text-sm font-semibold text-neutral-900">{cohort.decision_criteria.length}</p>
                                </div>
                            </div>

                            {/* Top Buying Trigger */}
                            <div className="border-t border-neutral-100 pt-3">
                                <span className="text-xs text-neutral-500">Top Trigger:</span>
                                <p className="text-sm text-neutral-900 mt-1">{cohort.buying_triggers[0]?.trigger}</p>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2 mt-4">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        navigate(`/strategy/campaigns/new?cohort=${cohort.id}`);
                                    }}
                                    className="flex-1 px-3 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium hover:bg-neutral-800"
                                >
                                    Create Campaign
                                </button>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setSelectedCohort(cohort);
                                    }}
                                    className="px-3 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50"
                                >
                                    <Eye className="w-4 h-4" />
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Cohort Detail Modal */}
            <AnimatePresence>
                {selectedCohort && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-6"
                        onClick={() => setSelectedCohort(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {/* Modal Header */}
                            <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
                                <div>
                                    <h2 className="font-serif text-2xl text-neutral-900">{selectedCohort.name}</h2>
                                    <p className="text-sm text-neutral-600">{selectedCohort.description}</p>
                                </div>
                                <button
                                    onClick={() => setSelectedCohort(null)}
                                    className="p-2 hover:bg-neutral-100 rounded-lg"
                                >
                                    <ArrowRight className="w-5 h-5 rotate-45" />
                                </button>
                            </div>

                            {/* Modal Content */}
                            <div className="p-6 space-y-6">
                                {/* Buying Triggers */}
                                <div>
                                    <h3 className="font-semibold text-neutral-900 mb-3">Buying Triggers</h3>
                                    <div className="space-y-2">
                                        {selectedCohort.buying_triggers.map((trigger, i) => (
                                            <div key={i} className="bg-neutral-50 rounded-lg p-4">
                                                <div className="flex items-start justify-between mb-2">
                                                    <p className="font-medium text-neutral-900">{trigger.trigger}</p>
                                                    <span className={cn(
                                                        "px-2 py-0.5 text-xs rounded",
                                                        trigger.strength === 'high' ? "bg-red-100 text-red-700" :
                                                            trigger.strength === 'medium' ? "bg-amber-100 text-amber-700" :
                                                                "bg-blue-100 text-blue-700"
                                                    )}>
                                                        {trigger.strength}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-neutral-600">Timing: {trigger.timing}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Decision Criteria */}
                                <div>
                                    <h3 className="font-semibold text-neutral-900 mb-3">Decision Criteria</h3>
                                    <div className="space-y-2">
                                        {selectedCohort.decision_criteria.map((criterion, i) => (
                                            <div key={i} className="bg-neutral-50 rounded-lg p-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <p className="font-medium text-neutral-900">{criterion.criterion}</p>
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-sm text-neutral-600">{Math.round(criterion.weight * 100)}%</span>
                                                        {criterion.deal_breaker && (
                                                            <span className="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded">
                                                                Deal Breaker
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="w-full bg-neutral-200 rounded-full h-1.5">
                                                    <div
                                                        className="bg-neutral-900 h-1.5 rounded-full"
                                                        style={{ width: `${criterion.weight * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Objection Map */}
                                <div>
                                    <h3 className="font-semibold text-neutral-900 mb-3">Common Objections</h3>
                                    <div className="space-y-2">
                                        {selectedCohort.objection_map.map((objection, i) => (
                                            <div key={i} className="bg-neutral-50 rounded-lg p-4">
                                                <p className="font-medium text-neutral-900 mb-2">"{objection.objection}"</p>
                                                <div className="grid grid-cols-2 gap-4 text-sm">
                                                    <div>
                                                        <span className="text-neutral-500">Root Cause:</span>
                                                        <p className="text-neutral-900">{objection.root_cause}</p>
                                                    </div>
                                                    <div>
                                                        <span className="text-neutral-500">Response:</span>
                                                        <p className="text-neutral-900">{objection.response_strategy}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Attention Windows */}
                                <div>
                                    <h3 className="font-semibold text-neutral-900 mb-3">Attention Windows</h3>
                                    <div className="space-y-2">
                                        {selectedCohort.attention_windows.map((window, i) => (
                                            <div key={i} className="bg-neutral-50 rounded-lg p-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <p className="font-medium text-neutral-900 capitalize">{window.channel}</p>
                                                    <span className={cn(
                                                        "px-2 py-0.5 text-xs rounded",
                                                        window.receptivity === 'high' ? "bg-green-100 text-green-700" :
                                                            window.receptivity === 'medium' ? "bg-amber-100 text-amber-700" :
                                                                "bg-neutral-100 text-neutral-700"
                                                    )}>
                                                        {window.receptivity} receptivity
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-4 text-sm text-neutral-600">
                                                    <span>Best times: {window.best_times.join(', ')}</span>
                                                    <span>•</span>
                                                    <span>Max frequency: {window.frequency_tolerance}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
