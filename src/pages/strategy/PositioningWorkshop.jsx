/**
 * Positioning Workshop
 * 
 * Strategic foundation for all marketing activities.
 * Helps users define their positioning statement and message architecture.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
    Target,
    Users,
    Zap,
    Shield,
    ArrowRight,
    ArrowLeft,
    Save,
    Sparkles,
    CheckCircle2,
    Lightbulb,
    MessageSquare,
    Award
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { generatePositioning, generateMessageArchitecture } from '../../lib/services/cohortService';
import { LuxeHeading, LuxeButton, LuxeCard, LuxeInput, LuxeBadge } from '../../components/ui/PremiumUI';
import { pageTransition, fadeInUp } from '../../utils/animations';

// =============================================================================
// CONSTANTS & MOCK DATA
// =============================================================================

const MOCK_COHORTS = [
    {
        id: 'c1',
        name: 'Enterprise CTOs',
        description: 'Tech leaders at large companies',
        pain_points: ['Scattered marketing tools', 'No strategic coherence', 'Wasted budget'],
    },
    {
        id: 'c2',
        name: 'Startup Founders',
        description: 'Early-stage company builders',
        pain_points: ['Limited marketing expertise', 'Time constraints', 'Need fast results'],
    },
    {
        id: 'c3',
        name: 'Marketing Directors',
        description: 'Marketing leaders at mid-market',
        pain_points: ['Team coordination', 'Campaign tracking', 'ROI measurement'],
    },
];

const CATEGORY_FRAMES = [
    'The strategic marketing command center',
    'The AI-powered campaign orchestrator',
    'The marketing warfare platform',
    'The cohort-first marketing system',
    'The anti-chaos marketing tool',
];

const DIFFERENTIATORS = [
    'that turns scattered activities into coordinated campaigns',
    'that combines AI-powered cohort intelligence with battle-tested frameworks',
    'that makes every touchpoint ladder up to strategic intent',
    'that learns what works and compounds strategic value',
    'that eliminates guesswork with data-driven positioning',
];

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function PositioningWorkshop() {
    const navigate = useNavigate();

    // Wizard state
    const [currentStep, setCurrentStep] = useState(1);
    const totalSteps = 6;

    // Positioning data
    const [positioning, setPositioning] = useState({
        cohort_id: '',
        problem_desire: '',
        category_frame: '',
        differentiator: '',
        reason_to_believe: '',
        competitive_alternative: '',
    });

    // Generated outputs
    const [generatedPositioning, setGeneratedPositioning] = useState(null);
    const [messageArchitecture, setMessageArchitecture] = useState(null);
    const [generating, setGenerating] = useState(false);
    const [saving, setSaving] = useState(false);

    // Validation
    const stepValidation = {
        1: !!positioning.cohort_id,
        2: !!positioning.problem_desire,
        3: !!positioning.category_frame,
        4: !!positioning.differentiator,
        5: !!positioning.reason_to_believe && !!positioning.competitive_alternative,
        6: !!generatedPositioning && !!messageArchitecture,
    };

    const canProceed = stepValidation[currentStep];
    const overallProgress = Object.values(stepValidation).filter(Boolean).length / totalSteps * 100;

    // Handlers
    const updatePositioning = (updates) => {
        setPositioning(prev => ({ ...prev, ...updates }));
    };

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            const selectedCohort = MOCK_COHORTS.find(c => c.id === positioning.cohort_id);

            // Generate positioning statement
            const positioningResult = await generatePositioning(
                { description: positioning.problem_desire },
                selectedCohort,
                { alternative: positioning.competitive_alternative }
            );
            setGeneratedPositioning(positioningResult);

            // Generate message architecture
            const messageResult = await generateMessageArchitecture(
                positioningResult,
                selectedCohort
            );
            setMessageArchitecture(messageResult);

            setCurrentStep(6);
        } catch (error) {
            console.error('Generation failed:', error);
            // Fallback to manual inputs
            setGeneratedPositioning({
                full_statement: `For ${MOCK_COHORTS.find(c => c.id === positioning.cohort_id)?.name} who ${positioning.problem_desire}, RaptorFlow is ${positioning.category_frame} ${positioning.differentiator}, ${positioning.reason_to_believe}. Unlike ${positioning.competitive_alternative}.`
            });
            setMessageArchitecture({
                primary_claim: "Ship campaigns 3x faster with half the chaos",
                proof_points: [
                    { claim: "AI-powered cohort intelligence", evidence: "Automated psychographic analysis", for_journey_stage: "problem_aware", emotional_hook: "Stop guessing, start knowing" },
                    { claim: "Battle-tested campaign frameworks", evidence: "Based on top agency playbooks", for_journey_stage: "solution_aware", emotional_hook: "Stand on the shoulders of giants" },
                    { claim: "Real-time performance insights", evidence: "Live dashboard with attribution", for_journey_stage: "product_aware", emotional_hook: "See what's working, double down" },
                ]
            });
            setCurrentStep(6);
        } finally {
            setGenerating(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        // TODO: Implement actual save to database
        await new Promise(resolve => setTimeout(resolve, 1000));
        setSaving(false);
        navigate('/strategy');
    };

    // ==========================================================================
    // RENDER
    // ==========================================================================

    return (
        <motion.div
            className="min-h-screen bg-neutral-50"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
        >
            {/* Header */}
            <div className="border-b border-neutral-200 bg-white sticky top-0 z-20">
                <div className="max-w-5xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-4">
                            <Link
                                to="/strategy"
                                className="flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                            </Link>
                            <div className="h-6 w-px bg-neutral-200" />
                            <div>
                                <LuxeHeading level={4} className="text-lg">Positioning Workshop</LuxeHeading>
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

                            {generatedPositioning && (
                                <LuxeButton
                                    onClick={handleSave}
                                    isLoading={saving}
                                    icon={Save}
                                >
                                    Save Positioning
                                </LuxeButton>
                            )}
                        </div>
                    </div>

                    {/* Step indicators */}
                    <div className="flex gap-1 overflow-x-auto pb-2 scrollbar-hide">
                        {[
                            { step: 1, label: 'Cohort', icon: Users },
                            { step: 2, label: 'Problem', icon: Target },
                            { step: 3, label: 'Frame', icon: Award },
                            { step: 4, label: 'Differentiator', icon: Zap },
                            { step: 5, label: 'Proof', icon: Shield },
                            { step: 6, label: 'Messages', icon: MessageSquare },
                        ].map(({ step, label, icon: Icon }) => (
                            <button
                                key={step}
                                onClick={() => step <= currentStep && setCurrentStep(step)}
                                disabled={step > currentStep}
                                className={cn(
                                    "flex-1 py-2 px-3 text-xs font-medium rounded-lg transition-colors flex items-center justify-center gap-1.5 whitespace-nowrap",
                                    currentStep === step
                                        ? "bg-neutral-900 text-white shadow-md"
                                        : stepValidation[step]
                                            ? "bg-green-50 text-green-700 border border-green-200"
                                            : "bg-transparent text-neutral-500 hover:bg-neutral-100 disabled:hover:bg-transparent"
                                )}
                            >
                                <Icon className="w-3 h-3" />
                                {label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-5xl mx-auto px-6 py-8">
                <AnimatePresence mode="wait">
                    {/* Step 1: Select Cohort */}
                    {currentStep === 1 && (
                        <motion.div
                            key="step1"
                            variants={fadeInUp}
                            initial="hidden"
                            animate="show"
                            exit="hidden"
                            className="space-y-6"
                        >
                            <div>
                                <LuxeHeading level={2}>Select Target Cohort</LuxeHeading>
                                <p className="text-neutral-600">Who is this positioning for?</p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {MOCK_COHORTS.map((cohort) => (
                                    <LuxeCard
                                        key={cohort.id}
                                        onClick={() => updatePositioning({ cohort_id: cohort.id })}
                                        className={cn(
                                            "cursor-pointer transition-all",
                                            positioning.cohort_id === cohort.id
                                                ? "ring-2 ring-neutral-900 bg-neutral-50"
                                                : "hover:border-neutral-400"
                                        )}
                                    >
                                        <div className="flex items-center justify-between mb-3">
                                            <h3 className="font-semibold text-neutral-900">{cohort.name}</h3>
                                            {positioning.cohort_id === cohort.id && (
                                                <CheckCircle2 className="w-5 h-5 text-neutral-900" />
                                            )}
                                        </div>
                                        <p className="text-sm text-neutral-600 mb-3">{cohort.description}</p>
                                        <div className="space-y-1">
                                            <span className="text-xs text-neutral-500">Pain Points:</span>
                                            {cohort.pain_points.slice(0, 2).map((pain, i) => (
                                                <p key={i} className="text-xs text-neutral-700">• {pain}</p>
                                            ))}
                                        </div>
                                    </LuxeCard>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    {/* Step 2: Problem/Desire */}
                    {currentStep === 2 && (
                        <motion.div
                            key="step2"
                            variants={fadeInUp}
                            initial="hidden"
                            animate="show"
                            exit="hidden"
                            className="space-y-6"
                        >
                            <div>
                                <LuxeHeading level={2}>Define the Problem or Desire</LuxeHeading>
                                <p className="text-neutral-600">What problem are they trying to solve? What do they want to achieve?</p>
                            </div>

                            <LuxeCard className="p-6">
                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                    Problem/Desire Statement
                                </label>
                                <textarea
                                    value={positioning.problem_desire}
                                    onChange={(e) => updatePositioning({ problem_desire: e.target.value })}
                                    placeholder="e.g., 'struggle with scattered marketing activities that don't ladder up to strategic goals'"
                                    rows={4}
                                    className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none bg-neutral-50/50"
                                />
                                <p className="text-xs text-neutral-500 mt-2">
                                    Tip: Be specific about their pain or aspiration. Use their language.
                                </p>
                            </LuxeCard>

                            {positioning.cohort_id && (
                                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                                    <div className="flex items-start gap-3">
                                        <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5" />
                                        <div>
                                            <h4 className="font-medium text-blue-900 mb-1">Cohort Context</h4>
                                            <p className="text-sm text-blue-700">
                                                {MOCK_COHORTS.find(c => c.id === positioning.cohort_id)?.name} typically struggles with:{' '}
                                                {MOCK_COHORTS.find(c => c.id === positioning.cohort_id)?.pain_points.join(', ')}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Step 3: Category Frame */}
                    {currentStep === 3 && (
                        <motion.div
                            key="step3"
                            variants={fadeInUp}
                            initial="hidden"
                            animate="show"
                            exit="hidden"
                            className="space-y-6"
                        >
                            <div>
                                <LuxeHeading level={2}>Define Your Category Frame</LuxeHeading>
                                <p className="text-neutral-600">What category do you want to own in their mind?</p>
                            </div>

                            <LuxeCard className="p-6">
                                <LuxeInput
                                    label="Category Frame"
                                    value={positioning.category_frame}
                                    onChange={(e) => updatePositioning({ category_frame: e.target.value })}
                                    placeholder="e.g., 'the strategic marketing command center'"
                                />
                                <p className="text-xs text-neutral-500 mt-2 ml-1">
                                    Tip: This should be a category you can own, not a commodity category.
                                </p>
                            </LuxeCard>

                            <div>
                                <h3 className="text-sm font-medium text-neutral-700 mb-3">Suggestions</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {CATEGORY_FRAMES.map((frame, i) => (
                                        <button
                                            key={i}
                                            onClick={() => updatePositioning({ category_frame: frame })}
                                            className={cn(
                                                "text-left p-4 rounded-xl border transition-all",
                                                positioning.category_frame === frame
                                                    ? "border-neutral-900 bg-neutral-50 ring-1 ring-neutral-900"
                                                    : "border-neutral-200 hover:border-neutral-400 bg-white"
                                            )}
                                        >
                                            <p className="text-sm text-neutral-900">{frame}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 4: Differentiator */}
                    {currentStep === 4 && (
                        <motion.div
                            key="step4"
                            variants={fadeInUp}
                            initial="hidden"
                            animate="show"
                            exit="hidden"
                            className="space-y-6"
                        >
                            <div>
                                <LuxeHeading level={2}>Define Your Key Differentiator</LuxeHeading>
                                <p className="text-neutral-600">What makes you different from alternatives?</p>
                            </div>

                            <LuxeCard className="p-6">
                                <label className="block text-sm font-medium text-neutral-700 mb-2">
                                    Differentiator
                                </label>
                                <textarea
                                    value={positioning.differentiator}
                                    onChange={(e) => updatePositioning({ differentiator: e.target.value })}
                                    placeholder="e.g., 'that turns scattered activities into coordinated campaigns'"
                                    rows={3}
                                    className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none bg-neutral-50/50"
                                />
                                <p className="text-xs text-neutral-500 mt-2">
                                    Tip: Focus on the unique mechanism or approach, not just features.
                                </p>
                            </LuxeCard>

                            <div>
                                <h3 className="text-sm font-medium text-neutral-700 mb-3">Suggestions</h3>
                                <div className="space-y-3">
                                    {DIFFERENTIATORS.map((diff, i) => (
                                        <button
                                            key={i}
                                            onClick={() => updatePositioning({ differentiator: diff })}
                                            className={cn(
                                                "w-full text-left p-4 rounded-xl border transition-all",
                                                positioning.differentiator === diff
                                                    ? "border-neutral-900 bg-neutral-50 ring-1 ring-neutral-900"
                                                    : "border-neutral-200 hover:border-neutral-400 bg-white"
                                            )}
                                        >
                                            <p className="text-sm text-neutral-900">{diff}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Step 5: Proof & Alternative */}
                    {currentStep === 5 && (
                        <motion.div
                            key="step5"
                            variants={fadeInUp}
                            initial="hidden"
                            animate="show"
                            exit="hidden"
                            className="space-y-6"
                        >
                            <div>
                                <LuxeHeading level={2}>Establish Proof & Alternative</LuxeHeading>
                                <p className="text-neutral-600">Why should they believe you? What are they comparing you to?</p>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <LuxeCard className="p-6">
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                        Reason to Believe
                                    </label>
                                    <textarea
                                        value={positioning.reason_to_believe}
                                        onChange={(e) => updatePositioning({ reason_to_believe: e.target.value })}
                                        placeholder="e.g., 'because we combine AI-powered cohort intelligence with battle-tested frameworks'"
                                        rows={4}
                                        className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none bg-neutral-50/50"
                                    />
                                    <p className="text-xs text-neutral-500 mt-2">
                                        What proof do you have? What makes your claim credible?
                                    </p>
                                </LuxeCard>

                                <LuxeCard className="p-6">
                                    <label className="block text-sm font-medium text-neutral-700 mb-2">
                                        Competitive Alternative
                                    </label>
                                    <textarea
                                        value={positioning.competitive_alternative}
                                        onChange={(e) => updatePositioning({ competitive_alternative: e.target.value })}
                                        placeholder="e.g., 'generic marketing automation tools that just send emails'"
                                        rows={4}
                                        className="w-full px-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-neutral-900 resize-none bg-neutral-50/50"
                                    />
                                    <p className="text-xs text-neutral-500 mt-2">
                                        What do they use now? What are they comparing you to?
                                    </p>
                                </LuxeCard>
                            </div>

                            <LuxeCard className="p-6 bg-white border-neutral-200">
                                <h3 className="font-semibold text-neutral-900 mb-4">Preview Positioning Statement</h3>
                                <div className="bg-neutral-50 rounded-xl p-6 border border-neutral-100">
                                    <p className="font-serif text-lg text-neutral-900 leading-relaxed">
                                        For <span className="font-semibold">{MOCK_COHORTS.find(c => c.id === positioning.cohort_id)?.name || '[cohort]'}</span>{' '}
                                        who <span className="font-semibold">{positioning.problem_desire || '[problem/desire]'}</span>,{' '}
                                        <span className="font-semibold">RaptorFlow</span> is{' '}
                                        <span className="font-semibold">{positioning.category_frame || '[category]'}</span>{' '}
                                        <span className="font-semibold">{positioning.differentiator || '[differentiator]'}</span>,{' '}
                                        <span className="font-semibold">{positioning.reason_to_believe || '[reason to believe]'}</span>.{' '}
                                        Unlike <span className="font-semibold">{positioning.competitive_alternative || '[alternative]'}</span>.
                                    </p>
                                </div>

                                <LuxeButton
                                    onClick={handleGenerate}
                                    disabled={!stepValidation[5] || generating}
                                    isLoading={generating}
                                    className="w-full mt-6"
                                    icon={Sparkles}
                                >
                                    Generate Message Architecture
                                </LuxeButton>
                            </LuxeCard>
                        </motion.div>
                    )}

                    {/* Step 6: Message Architecture */}
                    {currentStep === 6 && messageArchitecture && (
                        <motion.div
                            key="step6"
                            variants={fadeInUp}
                            initial="hidden"
                            animate="show"
                            exit="hidden"
                            className="space-y-6"
                        >
                            <div>
                                <LuxeHeading level={2}>Message Architecture</LuxeHeading>
                                <p className="text-neutral-600">Your strategic messaging framework</p>
                            </div>

                            {/* Positioning Statement */}
                            <div className="bg-neutral-900 text-white rounded-xl p-8 shadow-xl">
                                <h3 className="text-xs uppercase tracking-wider text-neutral-400 mb-3">Positioning Statement</h3>
                                <p className="font-serif text-xl leading-relaxed">
                                    {generatedPositioning?.full_statement}
                                </p>
                            </div>

                            {/* Primary Claim */}
                            <LuxeCard className="p-8 border-l-4 border-l-neutral-900">
                                <h3 className="text-xs uppercase tracking-wider text-neutral-500 mb-3">Primary Claim</h3>
                                <p className="font-serif text-3xl text-neutral-900">
                                    {messageArchitecture.primary_claim}
                                </p>
                                <p className="text-sm text-neutral-600 mt-4">
                                    This is the ONE thing you want them to believe. Every piece of content should ladder up to this.
                                </p>
                            </LuxeCard>

                            {/* Proof Points */}
                            <div>
                                <h3 className="font-semibold text-neutral-900 mb-4">Proof Points</h3>
                                <div className="space-y-4">
                                    {messageArchitecture.proof_points.map((pp, i) => (
                                        <LuxeCard key={i} className="p-6">
                                            <div className="flex items-start justify-between mb-3">
                                                <div>
                                                    <span className="text-xs text-neutral-500">Proof Point {i + 1}</span>
                                                    <h4 className="font-semibold text-neutral-900 mt-1">{pp.claim}</h4>
                                                </div>
                                                <LuxeBadge variant="info">
                                                    {pp.for_journey_stage?.replace('_', ' ')}
                                                </LuxeBadge>
                                            </div>
                                            <p className="text-sm text-neutral-600 mb-2">{pp.evidence}</p>
                                            <div className="flex items-center gap-2 text-sm text-neutral-500">
                                                <MessageSquare className="w-4 h-4" />
                                                <span className="italic">"{pp.emotional_hook}"</span>
                                            </div>
                                        </LuxeCard>
                                    ))}
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-3 pt-4">
                                <LuxeButton
                                    variant="secondary"
                                    onClick={() => setCurrentStep(5)}
                                    className="flex-1"
                                >
                                    Refine Positioning
                                </LuxeButton>
                                <LuxeButton
                                    onClick={handleSave}
                                    isLoading={saving}
                                    className="flex-1"
                                    icon={Save}
                                >
                                    Save & Continue
                                </LuxeButton>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Navigation */}
                {currentStep < 6 && (
                    <div className="flex justify-between mt-8 pt-6 border-t border-neutral-200">
                        <LuxeButton
                            variant="ghost"
                            onClick={() => setCurrentStep(prev => Math.max(1, prev - 1))}
                            disabled={currentStep === 1}
                            icon={ArrowLeft}
                        >
                            Previous
                        </LuxeButton>

                        {currentStep < 5 && (
                            <LuxeButton
                                onClick={() => setCurrentStep(prev => Math.min(totalSteps, prev + 1))}
                                disabled={!canProceed}
                                icon={ArrowRight}
                            >
                                Next
                            </LuxeButton>
                        )}
                    </div>
                )}
            </div>
        </motion.div>
    );
}
