/**
 * Strategic Insights Dashboard
 * 
 * Displays AI-powered insights from campaign performance, cohort behavior,
 * and positioning validation.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp,
    AlertCircle,
    CheckCircle2,
    Lightbulb,
    Target,
    Users,
    Zap,
    Activity,
    Clock,
    ThumbsUp,
    ThumbsDown,
    X,
    ChevronRight,
    Sparkles
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { LuxeHeading, LuxeButton, LuxeCard, LuxeBadge } from '../../components/ui/PremiumUI';
import { pageTransition, fadeInUp, staggerContainer } from '../../utils/animations';

// =============================================================================
// CONSTANTS
// =============================================================================

const INSIGHT_TYPES = {
    pacing: { icon: Clock, color: 'blue' },
    channel_performance: { icon: Activity, color: 'purple' },
    move_completion: { icon: Zap, color: 'amber' },
    cohort_engagement: { icon: Users, color: 'green' },
    missing_attribute: { icon: AlertCircle, color: 'red' },
    data_freshness: { icon: Clock, color: 'amber' },
    journey_distribution: { icon: TrendingUp, color: 'blue' },
};

// Mock insights data
const MOCK_INSIGHTS = [
    {
        id: 'ins-1',
        type: 'pacing',
        severity: 'positive',
        action: 'maintain',
        message: 'Campaign is ahead of schedule (58% vs 45% expected). Maintain current strategy.',
        campaign_name: 'Q1 Enterprise CTO Conversion',
        created_at: '2025-01-20T10:00:00Z',
        status: 'new',
        data: {
            expected_progress: 0.45,
            actual_progress: 0.58,
            current_value: 29,
            target_value: 50
        }
    },
    {
        id: 'ins-2',
        type: 'move_completion',
        severity: 'warning',
        action: 'accelerate',
        message: 'Only 40% of moves completed. Accelerate execution to stay on track.',
        campaign_name: 'Startup Founder Awareness',
        created_at: '2025-01-19T15:30:00Z',
        status: 'new',
        data: {
            total_moves: 5,
            completed_moves: 2,
            completion_rate: 0.4
        }
    },
    {
        id: 'ins-3',
        type: 'missing_attribute',
        severity: 'warning',
        action: 'add',
        message: 'Add buying triggers to understand what drives urgency for this cohort.',
        cohort_name: 'Marketing Directors',
        created_at: '2025-01-18T09:15:00Z',
        status: 'new',
        data: {
            attribute: 'buying_triggers'
        }
    },
    {
        id: 'ins-4',
        type: 'journey_distribution',
        severity: 'positive',
        action: 'convert',
        message: '35% are most aware. Great opportunity for conversion campaigns.',
        cohort_name: 'Enterprise CTOs',
        created_at: '2025-01-17T14:00:00Z',
        status: 'acted',
        data: {
            most_aware_percentage: 0.35
        }
    },
];

const MOCK_ANALYTICS = {
    campaigns: {
        total: 5,
        active: 2,
        avg_health: 78,
        at_risk: 1
    },
    cohorts: {
        total: 8,
        healthy: 6,
        needs_attention: 2
    },
    moves: {
        total: 15,
        completed: 9,
        completion_rate: 0.6
    }
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function StrategicInsights() {
    const [insights, setInsights] = useState(MOCK_INSIGHTS);
    const [analytics] = useState(MOCK_ANALYTICS);
    const [filterSeverity, setFilterSeverity] = useState('all');
    const [filterStatus, setFilterStatus] = useState('new');

    // Filter insights
    const filteredInsights = insights.filter(insight => {
        const matchesSeverity = filterSeverity === 'all' || insight.severity === filterSeverity;
        const matchesStatus = filterStatus === 'all' || insight.status === filterStatus;
        return matchesSeverity && matchesStatus;
    });

    const handleActOnInsight = (insightId) => {
        setInsights(insights.map(i =>
            i.id === insightId ? { ...i, status: 'acted' } : i
        ));
    };

    const handleDismissInsight = (insightId) => {
        setInsights(insights.map(i =>
            i.id === insightId ? { ...i, status: 'dismissed' } : i
        ));
    };

    return (
        <motion.div
            className="space-y-8 animate-fade-in p-6 max-w-7xl mx-auto"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
        >
            {/* Hero Header */}
            <motion.div
                variants={fadeInUp}
                className="relative overflow-hidden p-10 bg-white border border-neutral-200 rounded-2xl shadow-sm"
            >
                <div className="absolute inset-0 bg-gradient-to-r from-white via-neutral-50 to-white" />
                <div className="relative z-10">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="text-xs font-mono font-medium uppercase tracking-[0.5em] text-neutral-400">Strategic Intelligence</span>
                        <span className="h-px w-16 bg-neutral-200" />
                    </div>

                    <LuxeHeading level={1}>Insights</LuxeHeading>

                    <p className="text-neutral-600 max-w-2xl mt-4">
                        AI-powered recommendations from campaign performance, cohort behavior, and positioning validation
                    </p>
                </div>
            </motion.div>

            {/* Analytics Overview */}
            <motion.div
                className="grid grid-cols-1 md:grid-cols-3 gap-6"
                variants={staggerContainer}
            >
                {/* Campaigns */}
                <motion.div variants={fadeInUp}>
                    <LuxeCard className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold text-neutral-900">Campaigns</h3>
                            <Target className="w-5 h-5 text-neutral-400" />
                        </div>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">Active</span>
                                <span className="text-2xl font-bold text-green-600">{analytics.campaigns.active}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">Avg Health</span>
                                <span className="text-2xl font-bold text-blue-600">{analytics.campaigns.avg_health}%</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">At Risk</span>
                                <span className="text-2xl font-bold text-red-600">{analytics.campaigns.at_risk}</span>
                            </div>
                        </div>
                    </LuxeCard>
                </motion.div>

                {/* Cohorts */}
                <motion.div variants={fadeInUp}>
                    <LuxeCard className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold text-neutral-900">Cohorts</h3>
                            <Users className="w-5 h-5 text-neutral-400" />
                        </div>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">Total</span>
                                <span className="text-2xl font-bold text-neutral-900">{analytics.cohorts.total}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">Healthy</span>
                                <span className="text-2xl font-bold text-green-600">{analytics.cohorts.healthy}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">Needs Attention</span>
                                <span className="text-2xl font-bold text-amber-600">{analytics.cohorts.needs_attention}</span>
                            </div>
                        </div>
                    </LuxeCard>
                </motion.div>

                {/* Moves */}
                <motion.div variants={fadeInUp}>
                    <LuxeCard className="p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold text-neutral-900">Moves</h3>
                            <Zap className="w-5 h-5 text-neutral-400" />
                        </div>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">Total</span>
                                <span className="text-2xl font-bold text-neutral-900">{analytics.moves.total}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">Completed</span>
                                <span className="text-2xl font-bold text-green-600">{analytics.moves.completed}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-neutral-600">Completion Rate</span>
                                <span className="text-2xl font-bold text-blue-600">{Math.round(analytics.moves.completion_rate * 100)}%</span>
                            </div>
                        </div>
                    </LuxeCard>
                </motion.div>
            </motion.div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 bg-white"
                >
                    <option value="all">All Statuses</option>
                    <option value="new">New</option>
                    <option value="acted">Acted Upon</option>
                    <option value="dismissed">Dismissed</option>
                </select>

                <select
                    value={filterSeverity}
                    onChange={(e) => setFilterSeverity(e.target.value)}
                    className="px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 bg-white"
                >
                    <option value="all">All Severities</option>
                    <option value="positive">Positive</option>
                    <option value="neutral">Neutral</option>
                    <option value="warning">Warning</option>
                    <option value="critical">Critical</option>
                </select>
            </div>

            {/* Insights List */}
            <motion.div
                className="space-y-4"
                variants={staggerContainer}
            >
                {filteredInsights.map((insight, index) => {
                    const typeInfo = INSIGHT_TYPES[insight.type] || { icon: Lightbulb, color: 'neutral' };
                    const Icon = typeInfo.icon;

                    return (
                        <motion.div
                            key={insight.id}
                            variants={fadeInUp}
                        >
                            <LuxeCard className={cn(
                                "p-6 border-l-4",
                                insight.severity === 'positive' ? "border-l-green-500" :
                                    insight.severity === 'warning' ? "border-l-amber-500" :
                                        insight.severity === 'critical' ? "border-l-red-500" :
                                            "border-l-blue-500"
                            )}>
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-3">
                                            <div className={cn(
                                                "flex h-10 w-10 items-center justify-center rounded-full",
                                                insight.severity === 'positive' ? "bg-green-100" :
                                                    insight.severity === 'warning' ? "bg-amber-100" :
                                                        insight.severity === 'critical' ? "bg-red-100" :
                                                            "bg-blue-100"
                                            )}>
                                                <Icon className={cn(
                                                    "w-5 h-5",
                                                    insight.severity === 'positive' ? "text-green-600" :
                                                        insight.severity === 'warning' ? "text-amber-600" :
                                                            insight.severity === 'critical' ? "text-red-600" :
                                                                "text-blue-600"
                                                )} />
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <LuxeBadge variant={
                                                        insight.severity === 'positive' ? "success" :
                                                            insight.severity === 'warning' ? "warning" :
                                                                insight.severity === 'critical' ? "danger" : "info"
                                                    }>
                                                        {insight.severity}
                                                    </LuxeBadge>
                                                    <span className="text-xs text-neutral-500">
                                                        {insight.campaign_name || insight.cohort_name}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-neutral-500 mt-1">
                                                    {new Date(insight.created_at).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>

                                        <p className="text-neutral-900 font-medium mb-3">
                                            {insight.message}
                                        </p>

                                        {insight.status === 'new' && (
                                            <div className="flex items-center gap-2">
                                                <LuxeButton
                                                    size="sm"
                                                    onClick={() => handleActOnInsight(insight.id)}
                                                    icon={ThumbsUp}
                                                >
                                                    Act on This
                                                </LuxeButton>
                                                <LuxeButton
                                                    size="sm"
                                                    variant="secondary"
                                                    onClick={() => handleDismissInsight(insight.id)}
                                                    icon={ThumbsDown}
                                                >
                                                    Dismiss
                                                </LuxeButton>
                                            </div>
                                        )}

                                        {insight.status === 'acted' && (
                                            <div className="flex items-center gap-2 text-green-600 text-sm">
                                                <CheckCircle2 className="w-4 h-4" />
                                                <span>Acted upon</span>
                                            </div>
                                        )}

                                        {insight.status === 'dismissed' && (
                                            <div className="flex items-center gap-2 text-neutral-500 text-sm">
                                                <X className="w-4 h-4" />
                                                <span>Dismissed</span>
                                            </div>
                                        )}
                                    </div>

                                    <button className="p-2 text-neutral-400 hover:text-neutral-900 transition-colors">
                                        <ChevronRight className="w-5 h-5" />
                                    </button>
                                </div>
                            </LuxeCard>
                        </motion.div>
                    );
                })}
            </motion.div>

            {/* Empty State */}
            {filteredInsights.length === 0 && (
                <div className="text-center py-12 bg-white border border-neutral-200 rounded-xl">
                    <Sparkles className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-neutral-900 mb-2">No insights found</h3>
                    <p className="text-neutral-600">
                        {filterStatus !== 'all' || filterSeverity !== 'all'
                            ? 'Try adjusting your filters'
                            : 'Insights will appear here as campaigns run and data is collected'}
                    </p>
                </div>
            )}
        </motion.div>
    );
}
