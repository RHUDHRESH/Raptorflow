/**
 * Campaign Builder
 * 
 * The strategic campaign creation and management center.
 * Campaigns sit above Moves and orchestrate all marketing activities.
 * 
 * Flow:
 * 1. Link to positioning and message architecture
 * 2. Define objective and success metrics
 * 3. Select and configure target cohorts
 * 4. Design channel strategy
 * 5. Auto-generate move recommendations
 * 6. Launch and track
 */

import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
    Target,
    Users,
    Megaphone,
    BarChart3,
    Calendar,
    DollarSign,
    ArrowRight,
    ArrowLeft,
    Plus,
    X,
    CheckCircle2,
    AlertCircle,
    Sparkles,
    Play,
    Pause,
    TrendingUp,
    TrendingDown,
    Zap,
    Layers,
    Settings,
    Eye,
    Save,
    RefreshCw,
    ChevronRight,
    Clock,
    Mail,
    MessageSquare,
    Globe,
    Phone,
    Instagram,
    Linkedin,
    Twitter
} from 'lucide-react';
import { cn } from '../../utils/cn';

// =============================================================================
// CONSTANTS & MOCK DATA
// =============================================================================

const CAMPAIGN_OBJECTIVES = [
    {
        id: 'awareness',
        label: 'Awareness',
        description: 'Get on their radar',
        icon: Megaphone,
        color: 'purple',
        metrics: ['Impressions', 'Reach', 'Brand mentions', 'Share of voice'],
        recommended_duration: '4-8 weeks',
    },
    {
        id: 'consideration',
        label: 'Consideration',
        description: 'Get them evaluating you',
        icon: Target,
        color: 'blue',
        metrics: ['Website visits', 'Content engagement', 'Email signups', 'Time on site'],
        recommended_duration: '4-6 weeks',
    },
    {
        id: 'conversion',
        label: 'Conversion',
        description: 'Get them to act',
        icon: Zap,
        color: 'green',
        metrics: ['Demo requests', 'Trial signups', 'Purchases', 'SQLs'],
        recommended_duration: '2-4 weeks',
    },
    {
        id: 'retention',
        label: 'Retention',
        description: 'Keep them engaged',
        icon: RefreshCw,
        color: 'amber',
        metrics: ['Churn rate', 'NPS', 'Feature adoption', 'Support tickets'],
        recommended_duration: 'Ongoing',
    },
    {
        id: 'advocacy',
        label: 'Advocacy',
        description: 'Get them promoting you',
        icon: Users,
        color: 'pink',
        metrics: ['Referrals', 'Reviews', 'Case studies', 'Social shares'],
        recommended_duration: 'Ongoing',
    },
];

const JOURNEY_STAGES = [
    { id: 'unaware', label: 'Unaware', color: 'neutral' },
    { id: 'problem_aware', label: 'Problem Aware', color: 'amber' },
    { id: 'solution_aware', label: 'Solution Aware', color: 'blue' },
    { id: 'product_aware', label: 'Product Aware', color: 'purple' },
    { id: 'most_aware', label: 'Most Aware', color: 'green' },
];

const CHANNELS = [
    { id: 'linkedin', label: 'LinkedIn', icon: Linkedin, roles: ['reach', 'engage', 'convert'] },
    { id: 'email', label: 'Email', icon: Mail, roles: ['engage', 'convert', 'retain'] },
    { id: 'instagram', label: 'Instagram', icon: Instagram, roles: ['reach', 'engage'] },
    { id: 'twitter', label: 'Twitter/X', icon: Twitter, roles: ['reach', 'engage'] },
    { id: 'website', label: 'Website', icon: Globe, roles: ['engage', 'convert'] },
    { id: 'whatsapp', label: 'WhatsApp', icon: MessageSquare, roles: ['engage', 'convert', 'retain'] },
    { id: 'phone', label: 'Phone/Sales', icon: Phone, roles: ['convert'] },
];

const CHANNEL_ROLES = [
    { id: 'reach', label: 'Reach', description: 'Get attention' },
    { id: 'engage', label: 'Engage', description: 'Build interest' },
    { id: 'convert', label: 'Convert', description: 'Drive action' },
    { id: 'retain', label: 'Retain', description: 'Keep engaged' },
];

// Mock data
const MOCK_POSITIONING = {
    id: 'pos-1',
    name: 'Primary Positioning',
    category_frame: 'RaptorFlow is the strategic marketing command center',
    differentiator: 'that turns scattered activities into coordinated campaigns',
    reason_to_believe: 'because we combine AI-powered cohort intelligence with battle-tested frameworks',
};

const MOCK_MESSAGE_ARCH = {
    id: 'ma-1',
    primary_claim: 'Ship campaigns 3x faster with half the chaos',
    proof_points: [
        { id: 'pp-1', claim: 'AI-powered cohort intelligence', priority: 1 },
        { id: 'pp-2', claim: 'Battle-tested campaign frameworks', priority: 2 },
        { id: 'pp-3', claim: 'Real-time performance insights', priority: 3 },
    ],
};

const MOCK_COHORTS = [
    {
        id: 'c1',
        name: 'Enterprise CTOs',
        description: 'Tech leaders at large companies',
        health_score: 85,
        journey_distribution: {
            unaware: 0.2,
            problem_aware: 0.3,
            solution_aware: 0.25,
            product_aware: 0.15,
            most_aware: 0.1,
        },
    },
    {
        id: 'c2',
        name: 'Startup Founders',
        description: 'Early-stage company builders',
        health_score: 72,
        journey_distribution: {
            unaware: 0.4,
            problem_aware: 0.25,
            solution_aware: 0.2,
            product_aware: 0.1,
            most_aware: 0.05,
        },
    },
    {
        id: 'c3',
        name: 'Marketing Directors',
        description: 'Marketing leaders at mid-market',
        health_score: 91,
        journey_distribution: {
            unaware: 0.15,
            problem_aware: 0.25,
            solution_aware: 0.3,
            product_aware: 0.2,
            most_aware: 0.1,
        },
    },
];

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function CampaignBuilder() {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditing = !!id;

    // Wizard state
    const [currentStep, setCurrentStep] = useState(1);
    const totalSteps = 5;

    // Campaign data
    const [campaign, setCampaign] = useState({
        name: '',
        description: '',
        positioning_id: MOCK_POSITIONING.id,
        message_architecture_id: MOCK_MESSAGE_ARCH.id,
        objective: '',
        objective_statement: '',
        success_definition: '',
        primary_metric: '',
        target_value: '',
        secondary_metrics: [],
        budget: '',
        start_date: '',
        end_date: '',
        target_cohorts: [],
        channel_strategy: [],
        status: 'draft',
    });

    // UI state
    const [saving, setSaving] = useState(false);
    const [showMoveRecommendations, setShowMoveRecommendations] = useState(false);
    const [generatedMoves, setGeneratedMoves] = useState([]);

    // Validation
    const stepValidation = useMemo(() => ({
        1: !!campaign.positioning_id && !!campaign.message_architecture_id,
        2: !!campaign.objective && !!campaign.objective_statement && !!campaign.primary_metric,
        3: campaign.target_cohorts.length > 0 && campaign.target_cohorts.some(c => c.priority === 'primary'),
        4: campaign.channel_strategy.length > 0,
        5: !!campaign.name && !!campaign.start_date && !!campaign.end_date,
    }), [campaign]);

    const canProceed = stepValidation[currentStep];
    const overallProgress = Object.values(stepValidation).filter(Boolean).length / totalSteps * 100;

    // Handlers
    const updateCampaign = (updates) => {
        setCampaign(prev => ({ ...prev, ...updates }));
    };

    const addCohort = (cohortId, priority = 'secondary') => {
        const cohort = MOCK_COHORTS.find(c => c.id === cohortId);
        if (!cohort) return;

        // If setting as primary, demote existing primary
        let updatedCohorts = [...campaign.target_cohorts];
        if (priority === 'primary') {
            updatedCohorts = updatedCohorts.map(c => ({ ...c, priority: 'secondary' }));
        }

        // Check if already added
        const existing = updatedCohorts.find(c => c.cohort_id === cohortId);
        if (existing) {
            updatedCohorts = updatedCohorts.map(c =>
                c.cohort_id === cohortId ? { ...c, priority } : c
            );
        } else {
            updatedCohorts.push({
                cohort_id: cohortId,
                priority,
                journey_stage_current: 'problem_aware',
                journey_stage_target: 'product_aware',
            });
        }

        updateCampaign({ target_cohorts: updatedCohorts });
    };

    const removeCohort = (cohortId) => {
        updateCampaign({
            target_cohorts: campaign.target_cohorts.filter(c => c.cohort_id !== cohortId)
        });
    };

    const updateCohortJourney = (cohortId, field, value) => {
        updateCampaign({
            target_cohorts: campaign.target_cohorts.map(c =>
                c.cohort_id === cohortId ? { ...c, [field]: value } : c
            )
        });
    };

    const toggleChannel = (channelId) => {
        const existing = campaign.channel_strategy.find(c => c.channel === channelId);
        if (existing) {
            updateCampaign({
                channel_strategy: campaign.channel_strategy.filter(c => c.channel !== channelId)
            });
        } else {
            updateCampaign({
                channel_strategy: [
                    ...campaign.channel_strategy,
                    {
                        channel: channelId,
                        role: 'engage',
                        budget_percentage: 0,
                        frequency: '',
                        key_messages: [],
                    }
                ]
            });
        }
    };

    const updateChannelStrategy = (channelId, updates) => {
        updateCampaign({
            channel_strategy: campaign.channel_strategy.map(c =>
                c.channel === channelId ? { ...c, ...updates } : c
            )
        });
    };

    const generateMoveRecommendations = () => {
        const selectedObjective = CAMPAIGN_OBJECTIVES.find(o => o.id === campaign.objective);
        const primaryCohort = campaign.target_cohorts.find(c => c.priority === 'primary');

        // Generate contextual move recommendations
        const moves = [];

        if (campaign.objective === 'awareness') {
            moves.push({
                name: 'Authority Establishment Sprint',
                description: 'Build credibility with thought leadership content',
                journey_from: 'unaware',
                journey_to: 'problem_aware',
                duration: 14,
                channels: campaign.channel_strategy.filter(c => c.role === 'reach').map(c => c.channel),
                proof_point: MOCK_MESSAGE_ARCH.proof_points[0]?.claim,
            });
        }

        if (campaign.objective === 'consideration' || campaign.objective === 'conversion') {
            moves.push({
                name: 'Proof Delivery Campaign',
                description: 'Show evidence with case studies and testimonials',
                journey_from: 'problem_aware',
                journey_to: 'solution_aware',
                duration: 14,
                channels: campaign.channel_strategy.filter(c => c.role === 'engage').map(c => c.channel),
                proof_point: MOCK_MESSAGE_ARCH.proof_points[1]?.claim,
            });
            moves.push({
                name: 'Objection Handling Sequence',
                description: 'Address common concerns proactively',
                journey_from: 'solution_aware',
                journey_to: 'product_aware',
                duration: 7,
                channels: campaign.channel_strategy.filter(c => ['engage', 'convert'].includes(c.role)).map(c => c.channel),
                proof_point: MOCK_MESSAGE_ARCH.proof_points[2]?.claim,
            });
        }

        if (campaign.objective === 'conversion') {
            moves.push({
                name: 'Conversion Sprint',
                description: 'Push for action with urgency and clear CTAs',
                journey_from: 'product_aware',
                journey_to: 'most_aware',
                duration: 7,
                channels: campaign.channel_strategy.filter(c => c.role === 'convert').map(c => c.channel),
                proof_point: 'Clear value + risk reversal',
            });
        }

        if (campaign.objective === 'retention') {
            moves.push({
                name: 'Value Reinforcement Loop',
                description: 'Remind them why they chose you',
                journey_from: 'most_aware',
                journey_to: 'most_aware',
                duration: 28,
                channels: campaign.channel_strategy.filter(c => c.role === 'retain').map(c => c.channel),
                proof_point: 'Success stories and new features',
            });
        }

        setGeneratedMoves(moves);
        setShowMoveRecommendations(true);
    };

    const handleSave = async () => {
        setSaving(true);
        // TODO: Implement actual save
        await new Promise(resolve => setTimeout(resolve, 1000));
        setSaving(false);
        navigate('/campaigns');
    };

    const handleLaunch = async () => {
        updateCampaign({ status: 'active' });
        await handleSave();
    };

    // ==========================================================================
    // RENDER
    // ==========================================================================

    return (
        <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-white">
            {/* Header */}
            <div className="border-b border-neutral-200 bg-white sticky top-0 z-20">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link
                                to="/campaigns"
                                className="flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                <span className="text-sm">Back</span>
                            </Link>
                            <div className="h-6 w-px bg-neutral-200" />
                            <div>
                                <h1 className="font-serif text-xl text-black">
                                    {isEditing ? 'Edit Campaign' : 'New Campaign'}
                                </h1>
                                <p className="text-xs text-neutral-500">
                                    Step {currentStep} of {totalSteps}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            {/* Progress indicator */}
                            <div className="hidden md:flex items-center gap-2">
                                <div className="w-32 h-2 bg-neutral-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-neutral-900 transition-all duration-500"
                                        style={{ width: `${overallProgress}%` }}
                                    />
                                </div>
                                <span className="text-xs text-neutral-500">{Math.round(overallProgress)}%</span>
                            </div>

                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="flex items-center gap-2 px-4 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50"
                            >
                                {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                Save Draft
                            </button>
                        </div>
                    </div>

                    {/* Step indicators */}
                    <div className="flex gap-1 mt-4">
                        {[
                            { step: 1, label: 'Strategy' },
                            { step: 2, label: 'Objective' },
                            { step: 3, label: 'Cohorts' },
                            { step: 4, label: 'Channels' },
                            { step: 5, label: 'Launch' },
                        ].map(({ step, label }) => (
                            <button
                                key={step}
                                onClick={() => setCurrentStep(step)}
                                className={cn(
                                    "flex-1 py-2 px-3 text-xs font-medium rounded-lg transition-colors",
                                    currentStep === step
                                        ? "bg-neutral-900 text-white"
                                        : stepValidation[step]
                                            ? "bg-green-100 text-green-700 hover:bg-green-200"
                                            : "bg-neutral-100 text-neutral-500 hover:bg-neutral-200"
                                )}
                            >
                                {label}
                                {stepValidation[step] && currentStep !== step && (
                                    <CheckCircle2 className="w-3 h-3 inline ml-1" />
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-6xl mx-auto px-6 py-8">
                <AnimatePresence mode="wait">
                    {/* Step 1: Strategic Foundation */}
                    {currentStep === 1 && (
                        <motion.div
                            key="step1"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Strategic Foundation</h2>
                                <p className="text-neutral-600">Link this campaign to your positioning and message architecture.</p>
                            </div>

                            {/* Positioning Selection */}
                            <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <h3 className="font-semibold text-neutral-900">Positioning Statement</h3>
                                        <p className="text-sm text-neutral-500">The strategic foundation for this campaign</p>
                                    </div>
                                    <Link to="/strategy/positioning" className="text-sm text-neutral-500 hover:text-neutral-900">
                                        Edit →
                                    </Link>
                                </div>

                                <div className="bg-neutral-50 rounded-lg p-4">
                                    <p className="font-serif text-neutral-900">
                                        {MOCK_POSITIONING.category_frame} {MOCK_POSITIONING.differentiator}, {MOCK_POSITIONING.reason_to_believe}.
                                    </p>
                                </div>

                                <div className="mt-4 flex items-center gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                                    <span className="text-sm text-green-700">Positioning linked</span>
                                </div>
                            </div>

                            {/* Message Architecture Selection */}
                            <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <h3 className="font-semibold text-neutral-900">Message Architecture</h3>
                                        <p className="text-sm text-neutral-500">The message hierarchy for campaign content</p>
                                    </div>
                                    <Link to="/strategy/positioning" className="text-sm text-neutral-500 hover:text-neutral-900">
                                        Edit →
                                    </Link>
                                </div>

                                <div className="space-y-3">
                                    <div className="bg-neutral-900 text-white rounded-lg p-4">
                                        <span className="text-xs uppercase tracking-wider text-neutral-400">Primary Claim</span>
                                        <p className="font-semibold mt-1">{MOCK_MESSAGE_ARCH.primary_claim}</p>
                                    </div>

                                    <div className="grid grid-cols-3 gap-3">
                                        {MOCK_MESSAGE_ARCH.proof_points.map((pp, i) => (
                                            <div key={pp.id} className="bg-neutral-50 rounded-lg p-3">
                                                <span className="text-xs text-neutral-500">Proof Point {i + 1}</span>
                                                <p className="text-sm font-medium text-neutral-900 mt-1">{pp.claim}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="mt-4 flex items-center gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                                    <span className="text-sm text-green-700">Message architecture linked</span>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 2: Objective */}
                    {currentStep === 2 && (
                        <motion.div
                            key="step2"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Campaign Objective</h2>
                                <p className="text-neutral-600">Define what this campaign should achieve.</p>
                            </div>

                            {/* Objective Selection */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {CAMPAIGN_OBJECTIVES.map((obj) => {
                                    const Icon = obj.icon;
                                    const isSelected = campaign.objective === obj.id;

                                    return (
                                        <button
                                            key={obj.id}
                                            onClick={() => updateCampaign({
                                                objective: obj.id,
                                                primary_metric: obj.metrics[0]
                                            })}
                                            className={cn(
                                                "text-left p-5 rounded-xl border-2 transition-all",
                                                isSelected
                                                    ? "border-neutral-900 bg-neutral-50"
                                                    : "border-neutral-200 hover:border-neutral-300"
                                            )}
                                        >
                                            <div className={cn(
                                                "w-10 h-10 rounded-lg flex items-center justify-center mb-3",
                                                isSelected ? "bg-neutral-900 text-white" : "bg-neutral-100 text-neutral-600"
                                            )}>
                                                <Icon className="w-5 h-5" />
                                            </div>
                                            <h3 className="font-semibold text-neutral-900 mb-1">{obj.label}</h3>
                                            <p className="text-sm text-neutral-600 mb-3">{obj.description}</p>
                                            <div className="flex items-center gap-2 text-xs text-neutral-500">
                                                <Clock className="w-3 h-3" />
                                                {obj.recommended_duration}
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>

                            {/* Objective Statement */}
                            {campaign.objective && (
                                <div className="bg-white border border-neutral-200 rounded-xl p-6 space-y-6">
                                    <div>
                                        <label className="block text-sm font-medium text-neutral-700 mb-2">
                                            Objective Statement
                                        </label>
                                        <textarea
                                            value={campaign.objective_statement}
                                            onChange={(e) => updateCampaign({ objective_statement: e.target.value })}
                                            placeholder={`e.g., "Increase demo requests from Enterprise CTOs by 40% in Q1"`}
                                            rows={2}
                                            className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                        />
                                    </div>

                                    <div className="grid grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                Primary Metric
                                            </label>
                                            <select
                                                value={campaign.primary_metric}
                                                onChange={(e) => updateCampaign({ primary_metric: e.target.value })}
                                                className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                            >
                                                {CAMPAIGN_OBJECTIVES.find(o => o.id === campaign.objective)?.metrics.map(m => (
                                                    <option key={m} value={m}>{m}</option>
                                                ))}
                                            </select>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                Target Value
                                            </label>
                                            <input
                                                type="text"
                                                value={campaign.target_value}
                                                onChange={(e) => updateCampaign({ target_value: e.target.value })}
                                                placeholder="e.g., 50 demos, 1000 signups"
                                                className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-neutral-700 mb-2">
                                            Success Definition
                                        </label>
                                        <textarea
                                            value={campaign.success_definition}
                                            onChange={(e) => updateCampaign({ success_definition: e.target.value })}
                                            placeholder="What does winning look like? How will you know this campaign succeeded?"
                                            rows={2}
                                            className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                        />
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Step 3: Target Cohorts */}
                    {currentStep === 3 && (
                        <motion.div
                            key="step3"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Target Cohorts</h2>
                                <p className="text-neutral-600">Select the cohorts this campaign will target and define journey goals.</p>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                {/* Available Cohorts */}
                                <div>
                                    <h3 className="font-semibold text-neutral-900 mb-4">Available Cohorts</h3>
                                    <div className="space-y-3">
                                        {MOCK_COHORTS.map((cohort) => {
                                            const isAdded = campaign.target_cohorts.some(c => c.cohort_id === cohort.id);
                                            const targetCohort = campaign.target_cohorts.find(c => c.cohort_id === cohort.id);

                                            return (
                                                <div
                                                    key={cohort.id}
                                                    className={cn(
                                                        "border rounded-xl p-4 transition-all",
                                                        isAdded ? "border-neutral-900 bg-neutral-50" : "border-neutral-200"
                                                    )}
                                                >
                                                    <div className="flex items-start justify-between mb-3">
                                                        <div>
                                                            <div className="flex items-center gap-2">
                                                                <h4 className="font-semibold text-neutral-900">{cohort.name}</h4>
                                                                {targetCohort?.priority === 'primary' && (
                                                                    <span className="px-2 py-0.5 text-[10px] bg-neutral-900 text-white rounded">
                                                                        PRIMARY
                                                                    </span>
                                                                )}
                                                            </div>
                                                            <p className="text-sm text-neutral-600">{cohort.description}</p>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <span className={cn(
                                                                "px-2 py-0.5 text-xs rounded",
                                                                cohort.health_score >= 80 ? "bg-green-100 text-green-700" :
                                                                    cohort.health_score >= 60 ? "bg-amber-100 text-amber-700" :
                                                                        "bg-red-100 text-red-700"
                                                            )}>
                                                                {cohort.health_score}% health
                                                            </span>
                                                        </div>
                                                    </div>

                                                    {/* Journey distribution visualization */}
                                                    <div className="mb-3">
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
                                                                />
                                                            ))}
                                                        </div>
                                                        <div className="flex justify-between mt-1 text-[10px] text-neutral-500">
                                                            <span>Unaware</span>
                                                            <span>Most Aware</span>
                                                        </div>
                                                    </div>

                                                    {!isAdded ? (
                                                        <div className="flex gap-2">
                                                            <button
                                                                onClick={() => addCohort(cohort.id, 'primary')}
                                                                className="flex-1 px-3 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium hover:bg-neutral-800"
                                                            >
                                                                Add as Primary
                                                            </button>
                                                            <button
                                                                onClick={() => addCohort(cohort.id, 'secondary')}
                                                                className="flex-1 px-3 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50"
                                                            >
                                                                Add as Secondary
                                                            </button>
                                                        </div>
                                                    ) : (
                                                        <button
                                                            onClick={() => removeCohort(cohort.id)}
                                                            className="w-full px-3 py-2 border border-red-200 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50"
                                                        >
                                                            Remove
                                                        </button>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>

                                {/* Selected Cohorts with Journey Configuration */}
                                <div>
                                    <h3 className="font-semibold text-neutral-900 mb-4">Journey Configuration</h3>
                                    {campaign.target_cohorts.length === 0 ? (
                                        <div className="border-2 border-dashed border-neutral-200 rounded-xl p-8 text-center">
                                            <Users className="w-8 h-8 text-neutral-300 mx-auto mb-3" />
                                            <p className="text-neutral-500 text-sm">Select cohorts to configure their journey goals</p>
                                        </div>
                                    ) : (
                                        <div className="space-y-4">
                                            {campaign.target_cohorts.map((tc) => {
                                                const cohort = MOCK_COHORTS.find(c => c.id === tc.cohort_id);
                                                if (!cohort) return null;

                                                return (
                                                    <div key={tc.cohort_id} className="bg-white border border-neutral-200 rounded-xl p-4">
                                                        <div className="flex items-center justify-between mb-4">
                                                            <div className="flex items-center gap-2">
                                                                <span className="font-semibold text-neutral-900">{cohort.name}</span>
                                                                {tc.priority === 'primary' && (
                                                                    <span className="px-2 py-0.5 text-[10px] bg-neutral-900 text-white rounded">
                                                                        PRIMARY
                                                                    </span>
                                                                )}
                                                            </div>
                                                            {tc.priority !== 'primary' && (
                                                                <button
                                                                    onClick={() => addCohort(tc.cohort_id, 'primary')}
                                                                    className="text-xs text-neutral-500 hover:text-neutral-900"
                                                                >
                                                                    Make Primary
                                                                </button>
                                                            )}
                                                        </div>

                                                        <div className="space-y-4">
                                                            <div>
                                                                <label className="block text-xs text-neutral-500 mb-1">
                                                                    Current Stage (Where they are)
                                                                </label>
                                                                <select
                                                                    value={tc.journey_stage_current}
                                                                    onChange={(e) => updateCohortJourney(tc.cohort_id, 'journey_stage_current', e.target.value)}
                                                                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                                >
                                                                    {JOURNEY_STAGES.map(stage => (
                                                                        <option key={stage.id} value={stage.id}>{stage.label}</option>
                                                                    ))}
                                                                </select>
                                                            </div>

                                                            <div className="flex items-center justify-center">
                                                                <ArrowRight className="w-4 h-4 text-neutral-400" />
                                                            </div>

                                                            <div>
                                                                <label className="block text-xs text-neutral-500 mb-1">
                                                                    Target Stage (Where to move them)
                                                                </label>
                                                                <select
                                                                    value={tc.journey_stage_target}
                                                                    onChange={(e) => updateCohortJourney(tc.cohort_id, 'journey_stage_target', e.target.value)}
                                                                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                                >
                                                                    {JOURNEY_STAGES.map(stage => (
                                                                        <option key={stage.id} value={stage.id}>{stage.label}</option>
                                                                    ))}
                                                                </select>
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 4: Channel Strategy */}
                    {currentStep === 4 && (
                        <motion.div
                            key="step4"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Channel Strategy</h2>
                                <p className="text-neutral-600">Select channels and define their role in the campaign.</p>
                            </div>

                            {/* Channel Selection */}
                            <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                <h3 className="font-semibold text-neutral-900 mb-4">Select Channels</h3>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                    {CHANNELS.map((channel) => {
                                        const Icon = channel.icon;
                                        const isSelected = campaign.channel_strategy.some(c => c.channel === channel.id);

                                        return (
                                            <button
                                                key={channel.id}
                                                onClick={() => toggleChannel(channel.id)}
                                                className={cn(
                                                    "flex items-center gap-3 p-4 rounded-xl border-2 transition-all",
                                                    isSelected
                                                        ? "border-neutral-900 bg-neutral-50"
                                                        : "border-neutral-200 hover:border-neutral-300"
                                                )}
                                            >
                                                <Icon className={cn(
                                                    "w-5 h-5",
                                                    isSelected ? "text-neutral-900" : "text-neutral-400"
                                                )} />
                                                <span className={cn(
                                                    "font-medium",
                                                    isSelected ? "text-neutral-900" : "text-neutral-600"
                                                )}>{channel.label}</span>
                                                {isSelected && (
                                                    <CheckCircle2 className="w-4 h-4 text-green-500 ml-auto" />
                                                )}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Channel Configuration */}
                            {campaign.channel_strategy.length > 0 && (
                                <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                    <h3 className="font-semibold text-neutral-900 mb-4">Configure Channels</h3>
                                    <div className="space-y-4">
                                        {campaign.channel_strategy.map((cs) => {
                                            const channel = CHANNELS.find(c => c.id === cs.channel);
                                            if (!channel) return null;
                                            const Icon = channel.icon;

                                            return (
                                                <div key={cs.channel} className="border border-neutral-200 rounded-lg p-4">
                                                    <div className="flex items-center gap-3 mb-4">
                                                        <Icon className="w-5 h-5 text-neutral-600" />
                                                        <span className="font-medium text-neutral-900">{channel.label}</span>
                                                    </div>

                                                    <div className="grid grid-cols-2 gap-4">
                                                        <div>
                                                            <label className="block text-xs text-neutral-500 mb-1">
                                                                Role in Campaign
                                                            </label>
                                                            <select
                                                                value={cs.role}
                                                                onChange={(e) => updateChannelStrategy(cs.channel, { role: e.target.value })}
                                                                className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                            >
                                                                {CHANNEL_ROLES.filter(r => channel.roles.includes(r.id)).map(role => (
                                                                    <option key={role.id} value={role.id}>
                                                                        {role.label} - {role.description}
                                                                    </option>
                                                                ))}
                                                            </select>
                                                        </div>

                                                        <div>
                                                            <label className="block text-xs text-neutral-500 mb-1">
                                                                Frequency
                                                            </label>
                                                            <select
                                                                value={cs.frequency}
                                                                onChange={(e) => updateChannelStrategy(cs.channel, { frequency: e.target.value })}
                                                                className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                            >
                                                                <option value="">Select frequency...</option>
                                                                <option value="daily">Daily</option>
                                                                <option value="3x_week">3x per week</option>
                                                                <option value="2x_week">2x per week</option>
                                                                <option value="weekly">Weekly</option>
                                                                <option value="biweekly">Bi-weekly</option>
                                                            </select>
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Channel Role Matrix */}
                            {campaign.channel_strategy.length > 0 && (
                                <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-6">
                                    <h3 className="font-semibold text-neutral-900 mb-4">Channel Role Matrix</h3>
                                    <div className="overflow-x-auto">
                                        <table className="w-full">
                                            <thead>
                                                <tr>
                                                    <th className="text-left py-2 px-3 text-xs text-neutral-500">Channel</th>
                                                    {CHANNEL_ROLES.map(role => (
                                                        <th key={role.id} className="text-center py-2 px-3 text-xs text-neutral-500">
                                                            {role.label}
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {campaign.channel_strategy.map((cs) => {
                                                    const channel = CHANNELS.find(c => c.id === cs.channel);
                                                    if (!channel) return null;

                                                    return (
                                                        <tr key={cs.channel} className="border-t border-neutral-200">
                                                            <td className="py-2 px-3 text-sm font-medium text-neutral-900">{channel.label}</td>
                                                            {CHANNEL_ROLES.map(role => (
                                                                <td key={role.id} className="text-center py-2 px-3">
                                                                    {cs.role === role.id ? (
                                                                        <div className="w-4 h-4 bg-neutral-900 rounded-full mx-auto" />
                                                                    ) : (
                                                                        <div className="w-4 h-4 border border-neutral-300 rounded-full mx-auto" />
                                                                    )}
                                                                </td>
                                                            ))}
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Step 5: Launch Configuration */}
                    {currentStep === 5 && (
                        <motion.div
                            key="step5"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Launch Configuration</h2>
                                <p className="text-neutral-600">Final details before launching your campaign.</p>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                {/* Campaign Details */}
                                <div className="space-y-6">
                                    <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                        <h3 className="font-semibold text-neutral-900 mb-4">Campaign Details</h3>

                                        <div className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                    Campaign Name
                                                </label>
                                                <input
                                                    type="text"
                                                    value={campaign.name}
                                                    onChange={(e) => updateCampaign({ name: e.target.value })}
                                                    placeholder="e.g., Q1 Enterprise CTO Conversion Campaign"
                                                    className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                />
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                    Description
                                                </label>
                                                <textarea
                                                    value={campaign.description}
                                                    onChange={(e) => updateCampaign({ description: e.target.value })}
                                                    placeholder="Brief description of the campaign..."
                                                    rows={3}
                                                    className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
                                                />
                                            </div>

                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                        Start Date
                                                    </label>
                                                    <input
                                                        type="date"
                                                        value={campaign.start_date}
                                                        onChange={(e) => updateCampaign({ start_date: e.target.value })}
                                                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                        End Date
                                                    </label>
                                                    <input
                                                        type="date"
                                                        value={campaign.end_date}
                                                        onChange={(e) => updateCampaign({ end_date: e.target.value })}
                                                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                    />
                                                </div>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                                    Budget (Optional)
                                                </label>
                                                <input
                                                    type="text"
                                                    value={campaign.budget}
                                                    onChange={(e) => updateCampaign({ budget: e.target.value })}
                                                    placeholder="e.g., $10,000"
                                                    className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Generate Moves */}
                                    <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <div>
                                                <h3 className="font-semibold text-neutral-900">Move Recommendations</h3>
                                                <p className="text-sm text-neutral-500">AI-generated tactical moves based on your campaign</p>
                                            </div>
                                            <button
                                                onClick={generateMoveRecommendations}
                                                className="flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium hover:bg-neutral-800"
                                            >
                                                <Sparkles className="w-4 h-4" />
                                                Generate
                                            </button>
                                        </div>

                                        {generatedMoves.length > 0 && (
                                            <div className="space-y-3">
                                                {generatedMoves.map((move, i) => (
                                                    <div key={i} className="border border-neutral-200 rounded-lg p-4">
                                                        <div className="flex items-start justify-between mb-2">
                                                            <h4 className="font-medium text-neutral-900">{move.name}</h4>
                                                            <span className="text-xs text-neutral-500">{move.duration} days</span>
                                                        </div>
                                                        <p className="text-sm text-neutral-600 mb-3">{move.description}</p>
                                                        <div className="flex items-center gap-4 text-xs text-neutral-500">
                                                            <span>{move.journey_from.replace('_', ' ')} → {move.journey_to.replace('_', ' ')}</span>
                                                            <span>•</span>
                                                            <span>{move.channels.join(', ')}</span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Campaign Summary */}
                                <div>
                                    <div className="bg-neutral-900 text-white rounded-xl p-6 sticky top-32">
                                        <h3 className="text-xs uppercase tracking-wider text-neutral-400 mb-4">Campaign Summary</h3>

                                        <div className="space-y-4">
                                            <div>
                                                <span className="text-xs text-neutral-400">Objective</span>
                                                <p className="font-semibold">
                                                    {CAMPAIGN_OBJECTIVES.find(o => o.id === campaign.objective)?.label || 'Not set'}
                                                </p>
                                            </div>

                                            <div>
                                                <span className="text-xs text-neutral-400">Target Metric</span>
                                                <p className="font-semibold">
                                                    {campaign.primary_metric} {campaign.target_value && `→ ${campaign.target_value}`}
                                                </p>
                                            </div>

                                            <div>
                                                <span className="text-xs text-neutral-400">Target Cohorts</span>
                                                <div className="flex flex-wrap gap-2 mt-1">
                                                    {campaign.target_cohorts.map((tc) => {
                                                        const cohort = MOCK_COHORTS.find(c => c.id === tc.cohort_id);
                                                        return (
                                                            <span
                                                                key={tc.cohort_id}
                                                                className={cn(
                                                                    "px-2 py-0.5 text-xs rounded",
                                                                    tc.priority === 'primary' ? "bg-white text-neutral-900" : "bg-neutral-800 text-neutral-300"
                                                                )}
                                                            >
                                                                {cohort?.name}
                                                            </span>
                                                        );
                                                    })}
                                                </div>
                                            </div>

                                            <div>
                                                <span className="text-xs text-neutral-400">Channels</span>
                                                <div className="flex flex-wrap gap-2 mt-1">
                                                    {campaign.channel_strategy.map((cs) => (
                                                        <span
                                                            key={cs.channel}
                                                            className="px-2 py-0.5 text-xs bg-neutral-800 text-neutral-300 rounded"
                                                        >
                                                            {CHANNELS.find(c => c.id === cs.channel)?.label}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>

                                            <div>
                                                <span className="text-xs text-neutral-400">Timeline</span>
                                                <p className="font-semibold">
                                                    {campaign.start_date && campaign.end_date
                                                        ? `${new Date(campaign.start_date).toLocaleDateString()} - ${new Date(campaign.end_date).toLocaleDateString()}`
                                                        : 'Not set'
                                                    }
                                                </p>
                                            </div>

                                            <div className="pt-4 border-t border-neutral-800">
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={handleSave}
                                                        disabled={saving}
                                                        className="flex-1 px-4 py-3 bg-neutral-800 text-white rounded-lg text-sm font-medium hover:bg-neutral-700"
                                                    >
                                                        Save as Draft
                                                    </button>
                                                    <button
                                                        onClick={handleLaunch}
                                                        disabled={!Object.values(stepValidation).every(Boolean) || saving}
                                                        className="flex-1 px-4 py-3 bg-white text-neutral-900 rounded-lg text-sm font-medium hover:bg-neutral-100 disabled:opacity-50 flex items-center justify-center gap-2"
                                                    >
                                                        <Play className="w-4 h-4" />
                                                        Launch Campaign
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Navigation */}
                <div className="flex justify-between mt-8 pt-6 border-t border-neutral-200">
                    <button
                        onClick={() => setCurrentStep(prev => Math.max(1, prev - 1))}
                        disabled={currentStep === 1}
                        className="flex items-center gap-2 px-4 py-2 text-neutral-600 hover:text-neutral-900 disabled:opacity-50 disabled:hover:text-neutral-600"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Previous
                    </button>

                    {currentStep < totalSteps ? (
                        <button
                            onClick={() => setCurrentStep(prev => Math.min(totalSteps, prev + 1))}
                            disabled={!canProceed}
                            className="flex items-center gap-2 px-6 py-2 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800 disabled:opacity-50"
                        >
                            Next
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    ) : (
                        <button
                            onClick={handleLaunch}
                            disabled={!Object.values(stepValidation).every(Boolean) || saving}
                            className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
                        >
                            <Play className="w-4 h-4" />
                            Launch Campaign
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
