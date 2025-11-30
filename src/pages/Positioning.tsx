import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWorkspace } from '../context/WorkspaceContext';
import { positioningService } from '../services/positioningService';
import { PositioningFormSchema, PositioningFormValues } from '../lib/validation/positioning';
import {
    Sparkles,
    ArrowRight,
    ArrowLeft,
    Save,
    CheckCircle2,
    Loader2,
    Target,
    Users,
    Zap,
    MessageSquare
} from 'lucide-react';
import {
    HeroSection,
    LuxeCard,
    LuxeButton,
    LuxeInput,
    staggerContainer,
    fadeInUp
} from '../components/ui/PremiumUI';
import { toast } from 'sonner';

// --- Types & Constants ---

type StepId = 'founder_brand' | 'audience_pain' | 'promise_diff' | 'strategic_narrative';

interface StepConfig {
    id: StepId;
    label: string;
    icon: React.ElementType;
    description: string;
}

const STEPS: StepConfig[] = [
    { id: 'founder_brand', label: 'Identity', icon: Target, description: 'Founder & Brand Core' },
    { id: 'audience_pain', label: 'Audience', icon: Users, description: 'Who & Why' },
    { id: 'promise_diff', label: 'Value', icon: Zap, description: 'Promise & Edge' },
    { id: 'strategic_narrative', label: 'Narrative', icon: MessageSquare, description: 'Your Story' },
];

const INITIAL_VALUES: PositioningFormValues = {
    founder_name: '',
    founder_background: '',
    brand_name: '',
    category: '',
    audience_summary: '',
    core_pain: '',
    core_promise: '',
    differentiator: '',
    positioning_statement: '',
    mission_statement: '',
    origin_story: '',
};

// --- Components ---

const StepIndicator = ({ currentStep, steps }: { currentStep: number; steps: StepConfig[] }) => {
    return (
        <div className="flex items-center justify-between mb-8 relative">
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-0.5 bg-neutral-200 -z-10" />
            <div
                className="absolute left-0 top-1/2 -translate-y-1/2 h-0.5 bg-neutral-900 transition-all duration-500 -z-10"
                style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
            />
            {steps.map((step, index) => {
                const isCompleted = index < currentStep;
                const isCurrent = index === currentStep;
                const Icon = step.icon;

                return (
                    <div key={step.id} className="flex flex-col items-center gap-2 bg-white p-2 rounded-xl">
                        <div
                            className={`
                w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300
                ${isCompleted ? 'bg-neutral-900 border-neutral-900 text-white' :
                                    isCurrent ? 'bg-white border-neutral-900 text-neutral-900 shadow-lg' :
                                        'bg-neutral-50 border-neutral-200 text-neutral-400'}
              `}
                        >
                            {isCompleted ? <CheckCircle2 className="w-6 h-6" /> : <Icon className="w-5 h-5" />}
                        </div>
                        <span className={`text-xs font-medium ${isCurrent ? 'text-neutral-900' : 'text-neutral-500'}`}>
                            {step.label}
                        </span>
                    </div>
                );
            })}
        </div>
    );
};

// --- Main Component ---

export default function PositioningWizard() {
    const { currentWorkspace } = useWorkspace();
    const [currentStepIndex, setCurrentStepIndex] = useState(0);
    const [formValues, setFormValues] = useState<PositioningFormValues>(INITIAL_VALUES);
    const [errors, setErrors] = useState<Partial<Record<keyof PositioningFormValues, string>>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [lastSaved, setLastSaved] = useState<Date | null>(null);

    // Load initial data
    useEffect(() => {
        async function loadData() {
            if (!currentWorkspace?.id) return;

            try {
                setIsLoading(true);
                const { data } = await positioningService.getPositioningByWorkspaceId(currentWorkspace.id);
                if (data) {
                    setFormValues(prev => ({ ...prev, ...data }));
                }
            } catch (error) {
                console.error('Failed to load positioning:', error);
                toast.error('Failed to load existing positioning data');
            } finally {
                setIsLoading(false);
            }
        }

        loadData();
    }, [currentWorkspace?.id]);

    // Autosave
    useEffect(() => {
        if (!currentWorkspace?.id || isLoading) return;

        const timeoutId = setTimeout(async () => {
            setIsSaving(true);
            try {
                await positioningService.upsertPositioningForWorkspace(currentWorkspace.id, formValues);
                setLastSaved(new Date());
            } catch (error) {
                console.error('Autosave failed:', error);
            } finally {
                setIsSaving(false);
            }
        }, 2000);

        return () => clearTimeout(timeoutId);
    }, [formValues, currentWorkspace?.id, isLoading]);

    const handleChange = (field: keyof PositioningFormValues, value: string) => {
        setFormValues(prev => ({ ...prev, [field]: value }));
        if (errors[field]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[field];
                return newErrors;
            });
        }
    };

    const validateStep = (stepIndex: number): boolean => {
        const result = PositioningFormSchema.safeParse(formValues);
        if (result.success) return true;

        const stepErrors: Partial<Record<keyof PositioningFormValues, string>> = {};
        let isValid = true;

        result.error.issues.forEach(issue => {
            const field = issue.path[0] as keyof PositioningFormValues;

            const isRelevant = (() => {
                switch (stepIndex) {
                    case 0: return ['founder_name', 'brand_name', 'category'].includes(field);
                    case 1: return ['audience_summary', 'core_pain'].includes(field);
                    case 2: return ['core_promise', 'differentiator'].includes(field);
                    case 3: return false;
                    default: return false;
                }
            })();

            if (isRelevant) {
                stepErrors[field] = issue.message;
                isValid = false;
            }
        });

        setErrors(prev => ({ ...prev, ...stepErrors }));
        return isValid;
    };

    const handleNext = () => {
        if (validateStep(currentStepIndex)) {
            setCurrentStepIndex(prev => Math.min(prev + 1, STEPS.length - 1));
        } else {
            toast.error('Please fix the errors before proceeding');
        }
    };

    const handleBack = () => {
        setCurrentStepIndex(prev => Math.max(prev - 1, 0));
    };

    if (isLoading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-neutral-900 animate-spin" />
            </div>
        );
    }

    const currentStep = STEPS[currentStepIndex];

    return (
        <motion.div
            className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={staggerContainer}
        >
            {/* Header */}
            <motion.div variants={fadeInUp}>
                <HeroSection
                    title="Positioning Workshop"
                    subtitle="Define your strategic foundation in four simple steps."
                    metrics={[
                        { label: 'Step', value: `${currentStepIndex + 1}/${STEPS.length}` },
                        { label: 'Progress', value: `${Math.round(((currentStepIndex + 1) / STEPS.length) * 100)}%` },
                        { label: 'Status', value: isSaving ? 'Saving...' : lastSaved ? 'Saved' : 'Draft' }
                    ]}
                />
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Wizard Form */}
                <div className="lg:col-span-2 space-y-6">
                    <StepIndicator currentStep={currentStepIndex} steps={STEPS} />

                    <motion.div variants={fadeInUp}>
                        <LuxeCard className="p-8">
                            <div className="mb-6">
                                <h2 className="font-display text-2xl font-medium text-neutral-900 mb-2">{currentStep.label}</h2>
                                <p className="text-neutral-600">{currentStep.description}</p>
                            </div>

                            <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={currentStep.id}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -20 }}
                                        transition={{ duration: 0.2 }}
                                        className="space-y-6"
                                    >
                                        {currentStep.id === 'founder_brand' && (
                                            <>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                    <LuxeInput
                                                        label="Founder Name"
                                                        value={formValues.founder_name}
                                                        onChange={(e) => handleChange('founder_name', e.target.value)}
                                                        error={errors.founder_name}
                                                        placeholder="e.g. Elon Musk"
                                                    />
                                                    <LuxeInput
                                                        label="Brand Name"
                                                        value={formValues.brand_name}
                                                        onChange={(e) => handleChange('brand_name', e.target.value)}
                                                        error={errors.brand_name}
                                                        placeholder="e.g. Tesla"
                                                    />
                                                </div>
                                                <LuxeInput
                                                    label="Category"
                                                    value={formValues.category}
                                                    onChange={(e) => handleChange('category', e.target.value)}
                                                    error={errors.category}
                                                    placeholder="e.g. Electric Vehicle Manufacturer"
                                                />
                                                <div>
                                                    <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                                                        Founder Background <span className="text-neutral-400 font-normal">(Optional)</span>
                                                    </label>
                                                    <textarea
                                                        value={formValues.founder_background}
                                                        onChange={(e) => handleChange('founder_background', e.target.value)}
                                                        className="w-full px-4 py-3 border border-neutral-200 rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm min-h-[100px] resize-none"
                                                        placeholder="Brief context about why you started this..."
                                                    />
                                                </div>
                                            </>
                                        )}

                                        {currentStep.id === 'audience_pain' && (
                                            <>
                                                <div>
                                                    <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Target Audience</label>
                                                    <textarea
                                                        value={formValues.audience_summary}
                                                        onChange={(e) => handleChange('audience_summary', e.target.value)}
                                                        className={`w-full px-4 py-3 border rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm min-h-[100px] resize-none ${errors.audience_summary ? 'border-red-500' : 'border-neutral-200'}`}
                                                        placeholder="Who are you serving? Be specific."
                                                    />
                                                    {errors.audience_summary && <p className="text-xs text-red-600 mt-1">{errors.audience_summary}</p>}
                                                </div>
                                                <div>
                                                    <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Core Pain Point</label>
                                                    <textarea
                                                        value={formValues.core_pain}
                                                        onChange={(e) => handleChange('core_pain', e.target.value)}
                                                        className={`w-full px-4 py-3 border rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm min-h-[100px] resize-none ${errors.core_pain ? 'border-red-500' : 'border-neutral-200'}`}
                                                        placeholder="What keeps them up at night?"
                                                    />
                                                    {errors.core_pain && <p className="text-xs text-red-600 mt-1">{errors.core_pain}</p>}
                                                </div>
                                            </>
                                        )}

                                        {currentStep.id === 'promise_diff' && (
                                            <>
                                                <div>
                                                    <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Core Promise</label>
                                                    <textarea
                                                        value={formValues.core_promise}
                                                        onChange={(e) => handleChange('core_promise', e.target.value)}
                                                        className={`w-full px-4 py-3 border rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm min-h-[100px] resize-none ${errors.core_promise ? 'border-red-500' : 'border-neutral-200'}`}
                                                        placeholder="What is the main benefit you deliver?"
                                                    />
                                                    {errors.core_promise && <p className="text-xs text-red-600 mt-1">{errors.core_promise}</p>}
                                                </div>
                                                <div>
                                                    <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Differentiator</label>
                                                    <textarea
                                                        value={formValues.differentiator}
                                                        onChange={(e) => handleChange('differentiator', e.target.value)}
                                                        className={`w-full px-4 py-3 border rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm min-h-[100px] resize-none ${errors.differentiator ? 'border-red-500' : 'border-neutral-200'}`}
                                                        placeholder="Why you? What makes you unique?"
                                                    />
                                                    {errors.differentiator && <p className="text-xs text-red-600 mt-1">{errors.differentiator}</p>}
                                                </div>
                                            </>
                                        )}

                                        {currentStep.id === 'strategic_narrative' && (
                                            <>
                                                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
                                                    <div className="flex gap-3">
                                                        <Sparkles className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                                                        <div>
                                                            <h4 className="font-bold text-neutral-900 text-sm mb-1">AI Suggestion</h4>
                                                            <p className="text-xs text-neutral-600">
                                                                Based on your inputs, here is a draft positioning statement. Feel free to refine it.
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div>
                                                    <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                                                        Positioning Statement <span className="text-neutral-400 font-normal">(Optional)</span>
                                                    </label>
                                                    <textarea
                                                        value={formValues.positioning_statement}
                                                        onChange={(e) => handleChange('positioning_statement', e.target.value)}
                                                        className="w-full px-4 py-3 border border-neutral-200 rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm min-h-[120px] resize-none"
                                                        placeholder="For [Target Audience] who [Pain], [Brand] is a [Category] that [Promise]. Unlike [Competitor], we [Differentiator]."
                                                    />
                                                </div>
                                                <div>
                                                    <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                                                        Origin Story <span className="text-neutral-400 font-normal">(Optional)</span>
                                                    </label>
                                                    <textarea
                                                        value={formValues.origin_story}
                                                        onChange={(e) => handleChange('origin_story', e.target.value)}
                                                        className="w-full px-4 py-3 border border-neutral-200 rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm min-h-[100px] resize-none"
                                                        placeholder="How did this start?"
                                                    />
                                                </div>
                                            </>
                                        )}
                                    </motion.div>
                                </AnimatePresence>

                                <div className="flex justify-between pt-6 border-t border-neutral-200 mt-8">
                                    <button
                                        onClick={handleBack}
                                        disabled={currentStepIndex === 0}
                                        className="px-6 py-2 text-neutral-600 hover:text-neutral-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                                    >
                                        <ArrowLeft className="w-4 h-4" /> Back
                                    </button>

                                    {currentStepIndex === STEPS.length - 1 ? (
                                        <LuxeButton onClick={() => toast.success('Positioning saved successfully!')}>
                                            <Save className="w-4 h-4 mr-2" />
                                            Finish & Save
                                        </LuxeButton>
                                    ) : (
                                        <LuxeButton onClick={handleNext}>
                                            Next Step
                                            <ArrowRight className="w-4 h-4 ml-2" />
                                        </LuxeButton>
                                    )}
                                </div>
                            </form>
                        </LuxeCard>
                    </motion.div>
                </div>

                {/* Right Column: Live Preview */}
                <div className="lg:col-span-1">
                    <div className="sticky top-8">
                        <motion.div variants={fadeInUp}>
                            <LuxeCard className="p-6 bg-neutral-50">
                                <div className="flex items-center gap-2 mb-4 pb-4 border-b border-neutral-200">
                                    <Sparkles className="w-4 h-4 text-neutral-900" />
                                    <h3 className="font-display font-medium text-neutral-900">Live Preview</h3>
                                </div>

                                <div className="space-y-6">
                                    <div>
                                        <label className="text-xs uppercase tracking-wider text-neutral-500 font-bold mb-1 block">Brand Identity</label>
                                        <div className="text-neutral-900 font-display text-xl">
                                            {formValues.brand_name || <span className="text-neutral-400 italic">Brand Name</span>}
                                        </div>
                                        <div className="text-neutral-600 text-sm">
                                            {formValues.category || <span className="text-neutral-400 italic">Category</span>}
                                        </div>
                                    </div>

                                    <div>
                                        <label className="text-xs uppercase tracking-wider text-neutral-500 font-bold mb-1 block">For</label>
                                        <p className="text-neutral-700 text-sm">
                                            {formValues.audience_summary || <span className="text-neutral-400 italic">Target Audience...</span>}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="text-xs uppercase tracking-wider text-neutral-500 font-bold mb-1 block">Who Need</label>
                                        <p className="text-neutral-700 text-sm">
                                            {formValues.core_pain || <span className="text-neutral-400 italic">Core Pain Point...</span>}
                                        </p>
                                    </div>

                                    <div>
                                        <label className="text-xs uppercase tracking-wider text-neutral-500 font-bold mb-1 block">The Promise</label>
                                        <p className="text-neutral-900 text-sm font-medium">
                                            {formValues.core_promise || <span className="text-neutral-400 italic">Core Promise...</span>}
                                        </p>
                                    </div>

                                    {formValues.differentiator && (
                                        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3">
                                            <label className="text-xs uppercase tracking-wider text-emerald-700 font-bold mb-1 block">The Edge</label>
                                            <p className="text-neutral-700 text-xs">
                                                {formValues.differentiator}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </LuxeCard>
                        </motion.div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
