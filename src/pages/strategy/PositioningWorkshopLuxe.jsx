/**
 * Positioning Workshop Luxe
 * 
 * 6-step wizard for creating strategic positioning statements.
 * This is the foundation that everything else builds on.
 */

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    ArrowLeft,
    ArrowRight,
    CheckCircle2,
    Users,
    Target,
    Lightbulb,
    Shield,
    MessageSquare,
    Eye,
    Save,
    Sparkles,
    AlertCircle,
    Plus,
    X
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { createPositioning, createMessageArchitecture, generatePositioningSuggestions, generateMessageArchitecture } from '../../lib/services/positioningService';

// Mock cohorts for selection
const MOCK_COHORTS = [
    { id: 'c1', name: 'Enterprise CTOs', description: 'Tech leaders at large companies' },
    { id: 'c2', name: 'Startup Founders', description: 'Early-stage company builders' },
    { id: 'c3', name: 'Marketing Directors', description: 'Marketing leaders at mid-market' },
];

export default function PositioningWorkshopLuxe() {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(1);
    const totalSteps = 6;

    // Positioning data
    const [positioning, setPositioning] = useState({
        name: '',
        for_cohort_id: '',
        problem_statement: '',
        category_frame: '',
        differentiator: '',
        reason_to_believe: '',
        competitive_alternative: '',
    });

    // Message architecture data
    const [messageArch, setMessageArch] = useState({
        primary_claim: '',
        tagline: '',
        elevator_pitch: '',
        proof_points: [],
    });

    // UI state
    const [saving, setSaving] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [suggestions, setSuggestions] = useState(null);

    // Validation
    const stepValidation = useMemo(() => ({
        1: !!positioning.for_cohort_id && !!positioning.problem_statement,
        2: !!positioning.category_frame,
        3: !!positioning.differentiator,
        4: !!positioning.reason_to_believe,
        5: !!messageArch.primary_claim && messageArch.proof_points.length >= 3,
        6: !!positioning.name,
    }), [positioning, messageArch]);

    const canProceed = stepValidation[currentStep];
    const overallProgress = Object.values(stepValidation).filter(Boolean).length / totalSteps * 100;

    // Handlers
    const updatePositioning = (updates) => {
        setPositioning(prev => ({ ...prev, ...updates }));
    };

    const updateMessageArch = (updates) => {
        setMessageArch(prev => ({ ...prev, ...updates }));
    };

    const addProofPoint = () => {
        const newProofPoint = {
            id: `pp-${Date.now()}`,
            claim: '',
            evidence: '',
            priority: messageArch.proof_points.length + 1,
            for_journey_stage: 'problem_aware'
        };
        updateMessageArch({ proof_points: [...messageArch.proof_points, newProofPoint] });
    };

    const updateProofPoint = (id, updates) => {
        updateMessageArch({
            proof_points: messageArch.proof_points.map(pp =>
                pp.id === id ? { ...pp, ...updates } : pp
            )
        });
    };

    const removeProofPoint = (id) => {
        updateMessageArch({
            proof_points: messageArch.proof_points.filter(pp => pp.id !== id)
        });
    };

    const handleGenerateSuggestions = async () => {
        setGenerating(true);
        try {
            const suggestions = await generatePositioningSuggestions(positioning.for_cohort_id);
            setSuggestions(suggestions);
        } catch (error) {
            console.error('Failed to generate suggestions:', error);
        } finally {
            setGenerating(false);
        }
    };

    const handleGenerateMessageArch = async () => {
        setGenerating(true);
        try {
            // First save positioning to get ID
            const savedPositioning = await createPositioning({
                ...positioning,
                workspace_id: 'workspace-1', // TODO: Get from context
            });

            const generated = await generateMessageArchitecture(savedPositioning.id);
            updateMessageArch(generated);
        } catch (error) {
            console.error('Failed to generate message architecture:', error);
        } finally {
            setGenerating(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // Save positioning
            const savedPositioning = await createPositioning({
                ...positioning,
                workspace_id: 'workspace-1', // TODO: Get from context
            });

            // Save message architecture
            await createMessageArchitecture({
                positioning_id: savedPositioning.id,
                ...messageArch,
            });

            navigate('/strategy');
        } catch (error) {
            console.error('Failed to save:', error);
        } finally {
            setSaving(false);
        }
    };

    const selectedCohort = MOCK_COHORTS.find(c => c.id === positioning.for_cohort_id);

    return (
        <div className="min-h-screen bg-gradient-to-b from-neutral-50 to-white">
            {/* Header */}
            <div className="border-b border-neutral-200 bg-white sticky top-0 z-20">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link
                                to="/strategy"
                                className="flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                <span className="text-sm">Back to Strategy</span>
                            </Link>
                            <div className="h-6 w-px bg-neutral-200" />
                            <div>
                                <h1 className="font-serif text-xl text-black">Positioning Workshop</h1>
                                <p className="text-xs text-neutral-500">Step {currentStep} of {totalSteps}</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            {/* Progress */}
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
                                disabled={saving || !stepValidation[6]}
                                className="flex items-center gap-2 px-4 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50 disabled:opacity-50"
                            >
                                {saving ? <Sparkles className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                Save
                            </button>
                        </div>
                    </div>

                    {/* Step indicators */}
                    <div className="flex gap-1 mt-4">
                        {[
                            { step: 1, label: 'Target', icon: Users },
                            { step: 2, label: 'Category', icon: Target },
                            { step: 3, label: 'Differentiator', icon: Lightbulb },
                            { step: 4, label: 'Proof', icon: Shield },
                            { step: 5, label: 'Messages', icon: MessageSquare },
                            { step: 6, label: 'Review', icon: Eye },
                        ].map(({ step, label, icon: Icon }) => (
                            <button
                                key={step}
                                onClick={() => setCurrentStep(step)}
                                className={cn(
                                    "flex-1 py-2 px-3 text-xs font-medium rounded-lg transition-colors flex items-center justify-center gap-1",
                                    currentStep === step
                                        ? "bg-neutral-900 text-white"
                                        : stepValidation[step]
                                            ? "bg-green-100 text-green-700 hover:bg-green-200"
                                            : "bg-neutral-100 text-neutral-500 hover:bg-neutral-200"
                                )}
                            >
                                <Icon className="w-3 h-3" />
                                <span className="hidden sm:inline">{label}</span>
                                {stepValidation[step] && currentStep !== step && (
                                    <CheckCircle2 className="w-3 h-3 ml-1" />
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-4xl mx-auto px-6 py-8">
                <AnimatePresence mode="wait">
                    {/* Step 1: Target Selection */}
                    {currentStep === 1 && (
                        <motion.div
                            key="step1"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Who is this positioning for?</h2>
                                <p className="text-neutral-600">Select the primary cohort and define their core problem or desire.</p>
                            </div>

                            {/* Cohort Selection */}
                            <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                <label className="block text-sm font-medium text-neutral-700 mb-3">Primary Cohort</label>
                                <div className="grid grid-cols-1 gap-3">
                                    {MOCK_COHORTS.map((cohort) => (
                                        <button
                                            key={cohort.id}
                                            onClick={() => updatePositioning({ for_cohort_id: cohort.id })}
                                            className={cn(
                                                "text-left p-4 rounded-lg border-2 transition-all",
                                                positioning.for_cohort_id === cohort.id
                                                    ? "border-neutral-900 bg-neutral-50"
                                                    : "border-neutral-200 hover:border-neutral-300"
                                            )}
                                        >
                                            <div className="font-semibold text-neutral-900">{cohort.name}</div>
                                            <div className="text-sm text-neutral-600">{cohort.description}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Problem Statement */}
                            {positioning.for_cohort_id && (
                                <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                        What problem do they have? (or desire they want)
                                    </label>
                                    <textarea
                                        value={positioning.problem_statement}
                                        onChange={(e) => updatePositioning({ problem_statement: e.target.value })}
                                        placeholder="e.g., They're drowning in marketing chaos with no strategic framework..."
                                        rows={3}
                                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none"
                                    />
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Step 2: Category Frame */}
                    {currentStep === 2 && (
                        <motion.div
                            key="step2"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">What category are you in?</h2>
                                <p className="text-neutral-600">Define the category frame - how you want to be perceived.</p>
                            </div>

                            <div className="bg-white border border-neutral-200 rounded-xl p-6 space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                        Category Frame
                                    </label>
                                    <input
                                        type="text"
                                        value={positioning.category_frame}
                                        onChange={(e) => updatePositioning({ category_frame: e.target.value })}
                                        placeholder="e.g., the strategic marketing command center"
                                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                    />
                                    <p className="text-xs text-neutral-500 mt-2">
                                        Format: "the [category]" - be specific and ownable
                                    </p>
                                </div>

                                <button
                                    onClick={handleGenerateSuggestions}
                                    disabled={generating}
                                    className="flex items-center gap-2 px-4 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50"
                                >
                                    {generating ? <Sparkles className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                                    Generate Suggestions
                                </button>

                                {suggestions && (
                                    <div className="space-y-2">
                                        <p className="text-xs text-neutral-500">AI Suggestions:</p>
                                        {suggestions.category_frames?.map((frame, i) => (
                                            <button
                                                key={i}
                                                onClick={() => updatePositioning({ category_frame: frame })}
                                                className="block w-full text-left p-3 bg-neutral-50 rounded-lg text-sm hover:bg-neutral-100"
                                            >
                                                {frame}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}

                    {/* Step 3: Differentiator */}
                    {currentStep === 3 && (
                        <motion.div
                            key="step3"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">What makes you different?</h2>
                                <p className="text-neutral-600">Your key differentiator - why choose you over alternatives.</p>
                            </div>

                            <div className="bg-white border border-neutral-200 rounded-xl p-6 space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                        Differentiator
                                    </label>
                                    <input
                                        type="text"
                                        value={positioning.differentiator}
                                        onChange={(e) => updatePositioning({ differentiator: e.target.value })}
                                        placeholder="e.g., that turns scattered activities into coordinated campaigns"
                                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                    />
                                    <p className="text-xs text-neutral-500 mt-2">
                                        Format: "that [does this unique thing]"
                                    </p>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                        Competitive Alternative (Optional)
                                    </label>
                                    <input
                                        type="text"
                                        value={positioning.competitive_alternative}
                                        onChange={(e) => updatePositioning({ competitive_alternative: e.target.value })}
                                        placeholder="e.g., unlike scattered marketing tools"
                                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                    />
                                </div>

                                {suggestions && (
                                    <div className="space-y-2">
                                        <p className="text-xs text-neutral-500">AI Suggestions:</p>
                                        {suggestions.differentiators?.map((diff, i) => (
                                            <button
                                                key={i}
                                                onClick={() => updatePositioning({ differentiator: diff })}
                                                className="block w-full text-left p-3 bg-neutral-50 rounded-lg text-sm hover:bg-neutral-100"
                                            >
                                                {diff}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}

                    {/* Step 4: Reason to Believe */}
                    {currentStep === 4 && (
                        <motion.div
                            key="step4"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Why should they believe you?</h2>
                                <p className="text-neutral-600">Your reason to believe - the proof that backs up your claim.</p>
                            </div>

                            <div className="bg-white border border-neutral-200 rounded-xl p-6 space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                        Reason to Believe
                                    </label>
                                    <input
                                        type="text"
                                        value={positioning.reason_to_believe}
                                        onChange={(e) => updatePositioning({ reason_to_believe: e.target.value })}
                                        placeholder="e.g., because we combine AI-powered cohort intelligence with battle-tested frameworks"
                                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                    />
                                    <p className="text-xs text-neutral-500 mt-2">
                                        Format: "because [credible proof]"
                                    </p>
                                </div>

                                {suggestions && (
                                    <div className="space-y-2">
                                        <p className="text-xs text-neutral-500">AI Suggestions:</p>
                                        {suggestions.reasons_to_believe?.map((rtb, i) => (
                                            <button
                                                key={i}
                                                onClick={() => updatePositioning({ reason_to_believe: rtb })}
                                                className="block w-full text-left p-3 bg-neutral-50 rounded-lg text-sm hover:bg-neutral-100"
                                            >
                                                {rtb}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Preview */}
                            <div className="bg-neutral-900 text-white rounded-xl p-6">
                                <p className="text-xs uppercase tracking-wider text-neutral-400 mb-3">Positioning Preview</p>
                                <p className="font-serif text-lg">
                                    For <span className="text-neutral-300">{selectedCohort?.name}</span> who{' '}
                                    <span className="text-neutral-300">{positioning.problem_statement || '___'}</span>,{' '}
                                    RaptorFlow is <span className="text-neutral-300">{positioning.category_frame || '___'}</span>{' '}
                                    <span className="text-neutral-300">{positioning.differentiator || '___'}</span>,{' '}
                                    <span className="text-neutral-300">{positioning.reason_to_believe || '___'}</span>.
                                </p>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 5: Message Architecture */}
                    {currentStep === 5 && (
                        <motion.div
                            key="step5"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Message Architecture</h2>
                                <p className="text-neutral-600">Define your primary claim and supporting proof points.</p>
                            </div>

                            <div className="bg-white border border-neutral-200 rounded-xl p-6 space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                        Primary Claim (The ONE thing)
                                    </label>
                                    <input
                                        type="text"
                                        value={messageArch.primary_claim}
                                        onChange={(e) => updateMessageArch({ primary_claim: e.target.value })}
                                        placeholder="e.g., Ship campaigns 3x faster with half the chaos"
                                        className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                    />
                                </div>

                                <button
                                    onClick={handleGenerateMessageArch}
                                    disabled={generating}
                                    className="flex items-center gap-2 px-4 py-2 border border-neutral-200 rounded-lg text-sm font-medium hover:bg-neutral-50"
                                >
                                    {generating ? <Sparkles className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                                    Generate Message Architecture
                                </button>

                                <div>
                                    <div className="flex items-center justify-between mb-3">
                                        <label className="block text-sm font-medium text-neutral-700">
                                            Proof Points (3-5)
                                        </label>
                                        <button
                                            onClick={addProofPoint}
                                            className="flex items-center gap-1 text-sm text-neutral-600 hover:text-neutral-900"
                                        >
                                            <Plus className="w-4 h-4" />
                                            Add Proof Point
                                        </button>
                                    </div>

                                    <div className="space-y-3">
                                        {messageArch.proof_points.map((pp, index) => (
                                            <div key={pp.id} className="border border-neutral-200 rounded-lg p-4">
                                                <div className="flex items-start justify-between mb-3">
                                                    <span className="text-xs text-neutral-500">Proof Point {index + 1}</span>
                                                    <button
                                                        onClick={() => removeProofPoint(pp.id)}
                                                        className="text-neutral-400 hover:text-red-600"
                                                    >
                                                        <X className="w-4 h-4" />
                                                    </button>
                                                </div>
                                                <input
                                                    type="text"
                                                    value={pp.claim}
                                                    onChange={(e) => updateProofPoint(pp.id, { claim: e.target.value })}
                                                    placeholder="Proof point claim..."
                                                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm mb-2"
                                                />
                                                <input
                                                    type="text"
                                                    value={pp.evidence}
                                                    onChange={(e) => updateProofPoint(pp.id, { evidence: e.target.value })}
                                                    placeholder="Evidence/support..."
                                                    className="w-full px-3 py-2 border border-neutral-200 rounded-lg text-sm"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 6: Review & Save */}
                    {currentStep === 6 && (
                        <motion.div
                            key="step6"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div>
                                <h2 className="font-serif text-2xl text-neutral-900 mb-2">Review & Save</h2>
                                <p className="text-neutral-600">Review your positioning and give it a name.</p>
                            </div>

                            <div className="bg-white border border-neutral-200 rounded-xl p-6">
                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                    Positioning Name
                                </label>
                                <input
                                    type="text"
                                    value={positioning.name}
                                    onChange={(e) => updatePositioning({ name: e.target.value })}
                                    placeholder="e.g., Primary Positioning 2024"
                                    className="w-full px-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
                                />
                            </div>

                            {/* Complete Preview */}
                            <div className="bg-neutral-900 text-white rounded-xl p-6 space-y-6">
                                <div>
                                    <p className="text-xs uppercase tracking-wider text-neutral-400 mb-2">Positioning Statement</p>
                                    <p className="font-serif text-lg">
                                        For <span className="text-neutral-300">{selectedCohort?.name}</span> who{' '}
                                        <span className="text-neutral-300">{positioning.problem_statement}</span>,{' '}
                                        RaptorFlow is <span className="text-neutral-300">{positioning.category_frame}</span>{' '}
                                        <span className="text-neutral-300">{positioning.differentiator}</span>,{' '}
                                        <span className="text-neutral-300">{positioning.reason_to_believe}</span>.
                                    </p>
                                </div>

                                <div className="border-t border-neutral-800 pt-6">
                                    <p className="text-xs uppercase tracking-wider text-neutral-400 mb-3">Message Architecture</p>
                                    <div className="space-y-4">
                                        <div>
                                            <p className="text-xs text-neutral-400">Primary Claim</p>
                                            <p className="font-semibold">{messageArch.primary_claim}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs text-neutral-400 mb-2">Proof Points</p>
                                            <div className="space-y-2">
                                                {messageArch.proof_points.map((pp, i) => (
                                                    <div key={pp.id} className="bg-neutral-800 rounded-lg p-3">
                                                        <p className="text-sm font-medium">{i + 1}. {pp.claim}</p>
                                                        <p className="text-xs text-neutral-400 mt-1">{pp.evidence}</p>
                                                    </div>
                                                ))}
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
                        className="flex items-center gap-2 px-4 py-2 text-neutral-600 hover:text-neutral-900 disabled:opacity-50"
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
                            onClick={handleSave}
                            disabled={!stepValidation[6] || saving}
                            className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
                        >
                            {saving ? <Sparkles className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                            Save Positioning
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
