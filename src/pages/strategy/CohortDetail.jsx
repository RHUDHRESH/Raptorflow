/**
 * Cohort Detail Page (Luxe Edition)
 * 
 * A comprehensive, 6-tab interface for deep customer intelligence.
 * 
 * Tabs:
 * 1. Buying Intelligence - Triggers & Decision Criteria
 * 2. Objections - Objection map & response strategies
 * 3. Channels - Attention windows & receptivity
 * 4. Competitive - Competitive frame & alternatives
 * 5. Journey - Distribution across awareness stages
 * 6. Health - Cohort health score + trends
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useParams, useNavigate } from 'react-router-dom';
import {
    ArrowLeft,
    Zap,
    CheckCircle2,
    Shield,
    MessageSquare,
    Users,
    TrendingUp,
    Target,
    Clock,
    AlertCircle,
    Plus,
    X,
    Save,
    Sparkles,
    Edit2,
    Trash2
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { INITIAL_COHORTS, JOURNEY_STAGES } from '../../data/mockCohorts';

// =============================================================================
// CONSTANTS
// =============================================================================

const TABS = [
    { id: 'buying', label: 'Buying Intelligence', icon: Zap },
    { id: 'objections', label: 'Objections', icon: Shield },
    { id: 'channels', label: 'Channels', icon: MessageSquare },
    { id: 'competitive', label: 'Competitive', icon: Target },
    { id: 'journey', label: 'Journey', icon: Users },
    { id: 'health', label: 'Health', icon: TrendingUp },
];

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function CohortDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('buying');
    const [cohort, setCohort] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        // Simulate fetch
        const foundCohort = INITIAL_COHORTS.find(c => c.id === id);
        if (foundCohort) {
            setCohort(foundCohort);
        } else {
            // Fallback to first one if not found (for demo safety) or redirect
            // setCohort(INITIAL_COHORTS[0]);
        }
        setLoading(false);
    }, [id]);

    // Editing states
    const [editingTrigger, setEditingTrigger] = useState(null);
    const [editingCriterion, setEditingCriterion] = useState(null);
    const [editingObjection, setEditingObjection] = useState(null);

    if (loading) return <div className="min-h-screen bg-neutral-50 flex items-center justify-center">Loading...</div>;
    if (!cohort) return <div className="min-h-screen bg-neutral-50 flex items-center justify-center">Cohort not found</div>;

    // Validation
    const criteriaWeightSum = cohort.decision_criteria.reduce((sum, c) => sum + c.weight, 0);
    const criteriaValid = Math.abs(criteriaWeightSum - 1.0) < 0.01;

    const journeyDistSum = Object.values(cohort.journey_distribution).reduce((sum, v) => sum + v, 0);
    const journeyValid = Math.abs(journeyDistSum - 1.0) < 0.01;

    // Handlers
    const handleSave = async () => {
        setSaving(true);
        // TODO: Implement actual save
        await new Promise(resolve => setTimeout(resolve, 1000));
        setSaving(false);
    };

    const addBuyingTrigger = () => {
        const newTrigger = {
            id: `t${Date.now()}`,
            trigger: '',
            strength: 'medium',
            timing: '',
            signal: ''
        };
        setCohort({
            ...cohort,
            buying_triggers: [...cohort.buying_triggers, newTrigger]
        });
        setEditingTrigger(newTrigger.id);
    };

    const updateBuyingTrigger = (id, updates) => {
        setCohort({
            ...cohort,
            buying_triggers: cohort.buying_triggers.map(t =>
                t.id === id ? { ...t, ...updates } : t
            )
        });
    };

    const removeBuyingTrigger = (id) => {
        setCohort({
            ...cohort,
            buying_triggers: cohort.buying_triggers.filter(t => t.id !== id)
        });
    };

    const addDecisionCriterion = () => {
        const newCriterion = {
            id: `d${Date.now()}`,
            criterion: '',
            weight: 0,
            deal_breaker: false
        };
        setCohort({
            ...cohort,
            decision_criteria: [...cohort.decision_criteria, newCriterion]
        });
        setEditingCriterion(newCriterion.id);
    };

    const updateDecisionCriterion = (id, updates) => {
        setCohort({
            ...cohort,
            decision_criteria: cohort.decision_criteria.map(c =>
                c.id === id ? { ...c, ...updates } : c
            )
        });
    };

    const removeDecisionCriterion = (id) => {
        setCohort({
            ...cohort,
            decision_criteria: cohort.decision_criteria.filter(c => c.id !== id)
        });
    };

    const addObjection = () => {
        const newObjection = {
            id: `o${Date.now()}`,
            objection: '',
            frequency: 'occasional',
            stage: 'product_aware',
            root_cause: '',
            response: '',
            linked_assets: []
        };
        setCohort({
            ...cohort,
            objection_map: [...cohort.objection_map, newObjection]
        });
        setEditingObjection(newObjection.id);
    };

    const updateObjection = (id, updates) => {
        setCohort({
            ...cohort,
            objection_map: cohort.objection_map.map(o =>
                o.id === id ? { ...o, ...updates } : o
            )
        });
    };

    const removeObjection = (id) => {
        setCohort({
            ...cohort,
            objection_map: cohort.objection_map.filter(o => o.id !== id)
        });
    };

    const updateJourneyDistribution = (stage, value) => {
        setCohort({
            ...cohort,
            journey_distribution: {
                ...cohort.journey_distribution,
                [stage]: value
            }
        });
    };

    // ==========================================================================
    // RENDER
    // ==========================================================================

    return (
        <div className="min-h-screen bg-neutral-50">
            {/* Header */}
            <div className="border-b border-neutral-200 bg-white sticky top-0 z-20">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link
                                to="/cohorts"
                                className="flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                <span className="text-sm">Back to Cohorts</span>
                            </Link>
                            <div className="h-6 w-px bg-neutral-200" />
                            <div className="flex items-center gap-3">
                                <span className="text-3xl">{cohort.avatar}</span>
                                <div>
                                    <h1 className="font-serif text-xl text-black">{cohort.name}</h1>
                                    <p className="text-xs text-neutral-500">{cohort.description}</p>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            {/* Health Score */}
                            <div className="flex items-center gap-2 px-3 py-1.5 border border-neutral-200 rounded-lg">
                                <TrendingUp className={cn(
                                    "w-4 h-4",
                                    cohort.health_score >= 80 ? "text-neutral-900" :
                                        cohort.health_score >= 60 ? "text-neutral-600" :
                                            "text-neutral-400"
                                )} />
                                <span className="text-sm font-semibold">{cohort.health_score}%</span>
                            </div>

                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium hover:bg-neutral-800 disabled:opacity-50"
                            >
                                <Save className="w-4 h-4" />
                                {saving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    </div>

                    {/* Tab Navigation */}
                    <div className="flex gap-1 mt-4 overflow-x-auto">
                        {TABS.map((tab) => {
                            const Icon = tab.icon;
                            const isActive = activeTab === tab.id;

                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={cn(
                                        "flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap",
                                        isActive
                                            ? "bg-neutral-900 text-white"
                                            : "bg-neutral-50 text-neutral-600 hover:bg-neutral-100"
                                    )}
                                >
                                    <Icon className="w-4 h-4" />
                                    {tab.label}
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-6xl mx-auto px-6 py-8">
                <AnimatePresence mode="wait">
                    {/* Tab 1: Buying Intelligence */}
                    {activeTab === 'buying' && (
                        <motion.div
                            key="buying"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            {/* Buying Triggers */}
                            <div>
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <h2 className="font-serif text-2xl text-neutral-900">Buying Triggers</h2>
                                        <p className="text-sm text-neutral-600">What makes them act NOW</p>
                                    </div>
                                    <button
                                        onClick={addBuyingTrigger}
                                        className="flex items-center gap-2 px-4 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50"
                                    >
                                        <Plus className="w-4 h-4" />
                                        Add Trigger
                                    </button>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {cohort.buying_triggers.map((trigger) => (
                                        <div key={trigger.id} className="bg-white border border-neutral-200 rounded-xl p-4">
                                            {editingTrigger === trigger.id ? (
                                                <div className="space-y-3">
                                                    <input
                                                        type="text"
                                                        value={trigger.trigger}
                                                        onChange={(e) => updateBuyingTrigger(trigger.id, { trigger: e.target.value })}
                                                        placeholder="Trigger description"
                                                        className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                        autoFocus
                                                    />
                                                    <div className="grid grid-cols-2 gap-3">
                                                        <select
                                                            value={trigger.strength}
                                                            onChange={(e) => updateBuyingTrigger(trigger.id, { strength: e.target.value })}
                                                            className="px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                        >
                                                            <option value="low">Low Strength</option>
                                                            <option value="medium">Medium Strength</option>
                                                            <option value="high">High Strength</option>
                                                        </select>
                                                        <input
                                                            type="text"
                                                            value={trigger.timing}
                                                            onChange={(e) => updateBuyingTrigger(trigger.id, { timing: e.target.value })}
                                                            placeholder="Timing (e.g., Q4)"
                                                            className="px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                        />
                                                    </div>
                                                    <input
                                                        type="text"
                                                        value={trigger.signal}
                                                        onChange={(e) => updateBuyingTrigger(trigger.id, { signal: e.target.value })}
                                                        placeholder="Signal to watch for"
                                                        className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                    />
                                                    <button
                                                        onClick={() => setEditingTrigger(null)}
                                                        className="w-full px-3 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium"
                                                    >
                                                        Done
                                                    </button>
                                                </div>
                                            ) : (
                                                <>
                                                    <div className="flex items-start justify-between mb-3">
                                                        <p className="font-semibold text-neutral-900 flex-1">{trigger.trigger}</p>
                                                        <div className="flex items-center gap-1">
                                                            <button
                                                                onClick={() => setEditingTrigger(trigger.id)}
                                                                className="p-1 text-neutral-400 hover:text-neutral-900"
                                                            >
                                                                <Edit2 className="w-4 h-4" />
                                                            </button>
                                                            <button
                                                                onClick={() => removeBuyingTrigger(trigger.id)}
                                                                className="p-1 text-neutral-400 hover:text-red-600"
                                                            >
                                                                <Trash2 className="w-4 h-4" />
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-3 text-sm">
                                                        <span className={cn(
                                                            "px-2 py-1 border rounded font-medium",
                                                            trigger.strength === 'high' ? "bg-neutral-900 text-white border-neutral-900" :
                                                                trigger.strength === 'medium' ? "bg-neutral-100 text-neutral-900 border-neutral-200" :
                                                                    "bg-white text-neutral-500 border-neutral-200"
                                                        )}>
                                                            {trigger.strength}
                                                        </span>
                                                        <span className="text-neutral-600 flex items-center gap-1">
                                                            <Clock className="w-3 h-3" />
                                                            {trigger.timing}
                                                        </span>
                                                    </div>
                                                    {trigger.signal && (
                                                        <p className="text-xs text-neutral-500 mt-2">Signal: {trigger.signal}</p>
                                                    )}
                                                </>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Decision Criteria */}
                            <div>
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <h2 className="font-serif text-2xl text-neutral-900">Decision Criteria</h2>
                                        <p className="text-sm text-neutral-600">How they evaluate options (weights must sum to 1.0)</p>
                                        {!criteriaValid && (
                                            <p className="text-sm text-red-600 flex items-center gap-1 mt-1">
                                                <AlertCircle className="w-4 h-4" />
                                                Weights sum to {criteriaWeightSum.toFixed(2)} - must equal 1.0
                                            </p>
                                        )}
                                    </div>
                                    <button
                                        onClick={addDecisionCriterion}
                                        className="flex items-center gap-2 px-4 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50"
                                    >
                                        <Plus className="w-4 h-4" />
                                        Add Criterion
                                    </button>
                                </div>

                                <div className="space-y-3">
                                    {cohort.decision_criteria.map((criterion) => (
                                        <div key={criterion.id} className="bg-white border border-neutral-200 rounded-xl p-4 flex items-center gap-4">
                                            {editingCriterion === criterion.id ? (
                                                <div className="flex-1 flex items-center gap-3">
                                                    <input
                                                        type="text"
                                                        value={criterion.criterion}
                                                        onChange={(e) => updateDecisionCriterion(criterion.id, { criterion: e.target.value })}
                                                        placeholder="Criterion description"
                                                        className="flex-1 px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                        autoFocus
                                                    />
                                                    <input
                                                        type="number"
                                                        step="0.05"
                                                        value={criterion.weight}
                                                        onChange={(e) => updateDecisionCriterion(criterion.id, { weight: parseFloat(e.target.value) })}
                                                        placeholder="Weight"
                                                        className="w-24 px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                    />
                                                    <label className="flex items-center gap-2 text-sm">
                                                        <input
                                                            type="checkbox"
                                                            checked={criterion.deal_breaker}
                                                            onChange={(e) => updateDecisionCriterion(criterion.id, { deal_breaker: e.target.checked })}
                                                            className="rounded border-neutral-300 text-neutral-900 focus:ring-neutral-900"
                                                        />
                                                        Deal Breaker
                                                    </label>
                                                    <button
                                                        onClick={() => setEditingCriterion(null)}
                                                        className="px-3 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium"
                                                    >
                                                        Done
                                                    </button>
                                                </div>
                                            ) : (
                                                <>
                                                    <div className="w-16 text-center">
                                                        <p className="text-lg font-bold text-neutral-900">{(criterion.weight * 100).toFixed(0)}%</p>
                                                        <p className="text-[10px] text-neutral-500 uppercase">Weight</p>
                                                    </div>
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2">
                                                            <p className="font-medium text-neutral-900">{criterion.criterion}</p>
                                                            {criterion.deal_breaker && (
                                                                <span className="px-1.5 py-0.5 bg-neutral-900 text-white text-[10px] font-bold uppercase tracking-wider rounded border border-neutral-900">
                                                                    Deal Breaker
                                                                </span>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-1">
                                                        <button
                                                            onClick={() => setEditingCriterion(criterion.id)}
                                                            className="p-1 text-neutral-400 hover:text-neutral-900"
                                                        >
                                                            <Edit2 className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={() => removeDecisionCriterion(criterion.id)}
                                                            className="p-1 text-neutral-400 hover:text-red-600"
                                                        >
                                                            <Trash2 className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Tab 2: Objections */}
                    {activeTab === 'objections' && (
                        <motion.div
                            key="objections"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <h2 className="font-serif text-2xl text-neutral-900">Objection Map</h2>
                                    <p className="text-sm text-neutral-600">Why they say no and how to respond</p>
                                </div>
                                <button
                                    onClick={addObjection}
                                    className="flex items-center gap-2 px-4 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50"
                                >
                                    <Plus className="w-4 h-4" />
                                    Add Objection
                                </button>
                            </div>

                            <div className="grid grid-cols-1 gap-4">
                                {cohort.objection_map.map((obj) => (
                                    <div key={obj.id} className="bg-white border border-neutral-200 rounded-xl p-6">
                                        {editingObjection === obj.id ? (
                                            <div className="space-y-4">
                                                <input
                                                    type="text"
                                                    value={obj.objection}
                                                    onChange={(e) => updateObjection(obj.id, { objection: e.target.value })}
                                                    placeholder="The Objection (e.g., Too expensive)"
                                                    className="w-full px-4 py-2 border border-neutral-200 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                />
                                                <div className="grid grid-cols-2 gap-4">
                                                    <input
                                                        type="text"
                                                        value={obj.root_cause}
                                                        onChange={(e) => updateObjection(obj.id, { root_cause: e.target.value })}
                                                        placeholder="Root Cause (e.g., Budget constraints)"
                                                        className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                    />
                                                    <input
                                                        type="text"
                                                        value={obj.response_strategy}
                                                        onChange={(e) => updateObjection(obj.id, { response_strategy: e.target.value })}
                                                        placeholder="Response Strategy"
                                                        className="w-full px-4 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                    />
                                                </div>
                                                <button
                                                    onClick={() => setEditingObjection(null)}
                                                    className="w-full px-4 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium"
                                                >
                                                    Done
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="flex items-start gap-6">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className="px-2 py-1 bg-neutral-100 text-neutral-900 border border-neutral-200 text-[10px] uppercase font-bold tracking-wider rounded">
                                                            Objection
                                                        </span>
                                                        <h3 className="font-serif text-lg text-neutral-900">{obj.objection}</h3>
                                                    </div>
                                                    <div className="grid grid-cols-2 gap-6 mt-4">
                                                        <div>
                                                            <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Root Cause</p>
                                                            <p className="text-sm text-neutral-700">{obj.root_cause}</p>
                                                        </div>
                                                        <div>
                                                            <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Response Strategy</p>
                                                            <p className="text-sm text-neutral-700">{obj.response_strategy}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex flex-col gap-2">
                                                    <button
                                                        onClick={() => setEditingObjection(obj.id)}
                                                        className="p-2 text-neutral-400 hover:text-neutral-900 hover:bg-neutral-50 rounded-lg transition-colors"
                                                    >
                                                        <Edit2 className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => removeObjection(obj.id)}
                                                        className="p-2 text-neutral-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* Tab 3: Channels */}
                    {activeTab === 'channels' && (
                        <motion.div
                            key="channels"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <h2 className="font-serif text-2xl text-neutral-900 mb-4">Attention Windows</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {cohort.attention_windows.map((window, i) => (
                                    <div key={i} className="bg-white border border-neutral-200 rounded-xl p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-full bg-neutral-100 flex items-center justify-center">
                                                    <MessageSquare className="w-5 h-5 text-neutral-600" />
                                                </div>
                                                <div>
                                                    <h3 className="font-semibold text-neutral-900">{window.channel}</h3>
                                                    <p className="text-xs text-neutral-500">{window.frequency_tolerance}</p>
                                                </div>
                                            </div>
                                            <span className={cn(
                                                "px-2 py-1 text-xs rounded border font-medium",
                                                window.receptivity === 'high' ? "bg-neutral-900 text-white border-neutral-900" :
                                                    "bg-neutral-100 text-neutral-900 border-neutral-200"
                                            )}>
                                                {window.receptivity.toUpperCase()} Receptivity
                                            </span>
                                        </div>
                                        <div className="space-y-2">
                                            <p className="text-xs text-neutral-500 uppercase tracking-wider">Best Times</p>
                                            <div className="flex flex-wrap gap-2">
                                                {window.best_times.map((time, j) => (
                                                    <span key={j} className="px-2 py-1 bg-neutral-50 text-neutral-700 text-sm rounded border border-neutral-100">
                                                        {time}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* Tab 4: Competitive */}
                    {activeTab === 'competitive' && (
                        <motion.div
                            key="competitive"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="text-center py-12"
                        >
                            <Target className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-neutral-900">Competitive Landscape</h3>
                            <p className="text-neutral-500">Coming soon: Competitor matrix and win/loss analysis for this cohort.</p>
                        </motion.div>
                    )}

                    {/* Tab 5: Journey */}
                    {activeTab === 'journey' && (
                        <motion.div
                            key="journey"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Journey Distribution</h2>
                                <p className="text-neutral-600 mb-6">Where are they in the buying journey?</p>

                                {!journeyValid && (
                                    <div className="mb-4 p-3 bg-neutral-50 text-neutral-900 border border-neutral-200 rounded-lg flex items-center gap-2 text-sm">
                                        <AlertCircle className="w-4 h-4" />
                                        Distribution must sum to 100% (Current: {(journeyDistSum * 100).toFixed(0)}%)
                                    </div>
                                )}

                                <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                    <div className="flex h-12 rounded-lg overflow-hidden mb-6">
                                        {Object.entries(cohort.journey_distribution).map(([stage, value]) => {
                                            const stageInfo = JOURNEY_STAGES.find(s => s.id === stage);
                                            return (
                                                <div
                                                    key={stage}
                                                    className={cn("h-full flex items-center justify-center text-white text-[10px] font-bold transition-all", stageInfo?.color)}
                                                    style={{ width: `${value * 100}%` }}
                                                >
                                                    {value > 0.05 && `${(value * 100).toFixed(0)}%`}
                                                </div>
                                            );
                                        })}
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                                        {JOURNEY_STAGES.map((stage) => (
                                            <div key={stage.id} className="space-y-2">
                                                <label className="text-xs font-bold uppercase tracking-wider text-neutral-500">
                                                    {stage.label}
                                                </label>
                                                <div className="flex items-center gap-2">
                                                    <div className={cn("w-3 h-3 rounded-full", stage.color)} />
                                                    <input
                                                        type="number"
                                                        step="0.05"
                                                        min="0"
                                                        max="1"
                                                        value={cohort.journey_distribution[stage.id]}
                                                        onChange={(e) => updateJourneyDistribution(stage.id, parseFloat(e.target.value))}
                                                        className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Tab 6: Health */}
                    {activeTab === 'health' && (
                        <motion.div
                            key="health"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="text-center py-12"
                        >
                            <TrendingUp className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-neutral-900">Cohort Health</h3>
                            <p className="text-neutral-500">Coming soon: Engagement metrics and health trends.</p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
