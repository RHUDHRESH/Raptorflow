import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWorkspace } from '../context/WorkspaceContext';
import { positioningService } from '../services/positioningService';
import { PositioningFormSchema, PositioningFormValues, validatePositioningForm } from '../lib/validation/positioning';
import {
    Sparkles,
    ArrowRight,
    ArrowLeft,
    Save,
    CheckCircle2,
    AlertCircle,
    Loader2,
    Target,
    Users,
    Zap,
    MessageSquare
} from 'lucide-react';
import { LuxeCard, LuxeButton, LuxeHeading } from '../components/ui/PremiumUI';
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
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-obsidian-200 -z-10" />
            <div
                className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-neon-green transition-all duration-500 -z-10"
                style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
            />
            {steps.map((step, index) => {
                const isCompleted = index < currentStep;
                const isCurrent = index === currentStep;
                const Icon = step.icon;

                return (
                    <div key={step.id} className="flex flex-col items-center gap-2 bg-obsidian p-2 rounded-lg">
                        <div
                            className={`
                w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300
                ${isCompleted ? 'bg-neon-green border-neon-green text-obsidian-900' :
                                    isCurrent ? 'bg-obsidian-100 border-neon-green text-neon-green shadow-[0_0_15px_rgba(74,222,128,0.3)]' :
                                        'bg-obsidian-100 border-obsidian-300 text-obsidian-400'}
              `}
                        >
                            {isCompleted ? <CheckCircle2 className="w-6 h-6" /> : <Icon className="w-5 h-5" />}
                        </div>
                        <span className={`text-xs font-medium ${isCurrent ? 'text-neon-green' : 'text-obsidian-400'}`}>
                            {step.label}
                        </span>
                    </div>
                );
            })}
        </div>
    );
};

const FormField = ({
    label,
    error,
    children,
    optional = false
}: {
    label: string;
    error?: string;
    children: React.ReactNode;
    optional?: boolean;
}) => (
    <div className="space-y-2">
        <div className="flex justify-between">
            <label className="text-sm font-medium text-obsidian-300">
                {label} {optional && <span className="text-obsidian-500 font-normal">(Optional)</span>}
            </label>
            {error && <span className="text-xs text-neon-red">{error}</span>}
        </div>
        {children}
    </div>
);

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
                    // Merge with initial values to ensure all fields exist
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
        }, 2000); // 2s debounce

        return () => clearTimeout(timeoutId);
    }, [formValues, currentWorkspace?.id, isLoading]);

    const handleChange = (field: keyof PositioningFormValues, value: string) => {
        setFormValues(prev => ({ ...prev, [field]: value }));
        // Clear error for this field
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

        // Map Zod errors to fields
        result.error.issues.forEach(issue => {
            const field = issue.path[0] as keyof PositioningFormValues;

            // Only care about errors relevant to current step
            const isRelevant = (() => {
                switch (stepIndex) {
                    case 0: return ['founder_name', 'brand_name', 'category'].includes(field);
                    case 1: return ['audience_summary', 'core_pain'].includes(field);
                    case 2: return ['core_promise', 'differentiator'].includes(field);
                    case 3: return false; // Narrative fields are optional/generated
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
                <Loader2 className="w-8 h-8 text-neon-green animate-spin" />
            </div>
        );
    }

    const currentStep = STEPS[currentStepIndex];

    return (
        <div className="max-w-6xl mx-auto pb-20">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <LuxeHeading level={1}>Positioning Engine</LuxeHeading>
                    <p className="text-obsidian-400">Define your strategic foundation</p>
                </div>
                <div className="flex items-center gap-3 text-sm text-obsidian-400">
                    {isSaving ? (
                        <span className="flex items-center gap-2 text-neon-green">
                            <Loader2 className="w-3 h-3 animate-spin" /> Saving...
                        </span>
                    ) : lastSaved ? (
                        <span className="flex items-center gap-2">
                            <CheckCircle2 className="w-3 h-3" /> Saved {lastSaved.toLocaleTimeString()}
                        </span>
                    ) : null}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Wizard Form */}
                <div className="lg:col-span-2 space-y-6">
                    <StepIndicator currentStep={currentStepIndex} steps={STEPS} />

                    <LuxeCard>
                        <div className="mb-6">
                            <h2 className="text-2xl font-display font-bold text-white mb-2">{currentStep.label}</h2>
                            <p className="text-obsidian-400">{currentStep.description}</p>
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
                                                <FormField label="Founder Name" error={errors.founder_name}>
                                                    <input
                                                        type="text"
                                                        value={formValues.founder_name}
                                                        onChange={(e) => handleChange('founder_name', e.target.value)}
                                                        className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors"
                                                        placeholder="e.g. Elon Musk"
                                                    />
                                                </FormField>
                                                <FormField label="Brand Name" error={errors.brand_name}>
                                                    <input
                                                        type="text"
                                                        value={formValues.brand_name}
                                                        onChange={(e) => handleChange('brand_name', e.target.value)}
                                                        className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors"
                                                        placeholder="e.g. Tesla"
                                                    />
                                                </FormField>
                                            </div>
                                            <FormField label="Category" error={errors.category}>
                                                <input
                                                    type="text"
                                                    value={formValues.category}
                                                    onChange={(e) => handleChange('category', e.target.value)}
                                                    className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors"
                                                    placeholder="e.g. Electric Vehicle Manufacturer"
                                                />
                                            </FormField>
                                            <FormField label="Founder Background" optional>
                                                <textarea
                                                    value={formValues.founder_background}
                                                    onChange={(e) => handleChange('founder_background', e.target.value)}
                                                    className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors min-h-[100px]"
                                                    placeholder="Brief context about why you started this..."
                                                />
                                            </FormField>
                                        </>
                                    )}

                                    {currentStep.id === 'audience_pain' && (
                                        <>
                                            <FormField label="Target Audience" error={errors.audience_summary}>
                                                <textarea
                                                    value={formValues.audience_summary}
                                                    onChange={(e) => handleChange('audience_summary', e.target.value)}
                                                    className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors min-h-[100px]"
                                                    placeholder="Who are you serving? Be specific."
                                                />
                                            </FormField>
                                            <FormField label="Core Pain Point" error={errors.core_pain}>
                                                <textarea
                                                    value={formValues.core_pain}
                                                    onChange={(e) => handleChange('core_pain', e.target.value)}
                                                    className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors min-h-[100px]"
                                                    placeholder="What keeps them up at night?"
                                                />
                                            </FormField>
                                        </>
                                    )}

                                    {currentStep.id === 'promise_diff' && (
                                        <>
                                            <FormField label="Core Promise" error={errors.core_promise}>
                                                <textarea
                                                    value={formValues.core_promise}
                                                    onChange={(e) => handleChange('core_promise', e.target.value)}
                                                    className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors min-h-[100px]"
                                                    placeholder="What is the main benefit you deliver?"
                                                />
                                            </FormField>
                                            <FormField label="Differentiator" error={errors.differentiator}>
                                                <textarea
                                                    value={formValues.differentiator}
                                                    onChange={(e) => handleChange('differentiator', e.target.value)}
                                                    className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors min-h-[100px]"
                                                    placeholder="Why you? What makes you unique?"
                                                />
                                            </FormField>
                                        </>
                                    )}

                                    {currentStep.id === 'strategic_narrative' && (
                                        <>
                                            <div className="bg-neon-green/10 border border-neon-green/20 rounded-lg p-4 mb-6">
                                                <div className="flex gap-3">
                                                    <Sparkles className="w-5 h-5 text-neon-green shrink-0 mt-0.5" />
                                                    <div>
                                                        <h4 className="font-bold text-white text-sm mb-1">AI Suggestion</h4>
                                                        <p className="text-xs text-obsidian-300">
                                                            Based on your inputs, here is a draft positioning statement. Feel free to refine it.
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                            <FormField label="Positioning Statement" optional>
                                                <textarea
                                                    value={formValues.positioning_statement}
                                                    onChange={(e) => handleChange('positioning_statement', e.target.value)}
                                                    className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors min-h-[120px]"
                                                    placeholder="For [Target Audience] who [Pain], [Brand] is a [Category] that [Promise]. Unlike [Competitor], we [Differentiator]."
                                                />
                                            </FormField>
                                            <FormField label="Origin Story" optional>
                                                <textarea
                                                    value={formValues.origin_story}
                                                    onChange={(e) => handleChange('origin_story', e.target.value)}
                                                    className="w-full bg-obsidian-100 border border-obsidian-300 rounded-lg px-4 py-3 text-white focus:border-neon-green focus:outline-none transition-colors min-h-[100px]"
                                                    placeholder="How did this start?"
                                                />
                                            </FormField>
                                        </>
                                    )}
                                </motion.div>
                            </AnimatePresence>

                            <div className="flex justify-between pt-6 border-t border-obsidian-300 mt-8">
                                <button
                                    onClick={handleBack}
                                    disabled={currentStepIndex === 0}
                                    className="px-6 py-2 text-obsidian-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                                >
                                    <ArrowLeft className="w-4 h-4" /> Back
                                </button>

                                {currentStepIndex === STEPS.length - 1 ? (
                                    <LuxeButton onClick={() => toast.success('Positioning saved successfully!')} icon={Save}>
                                        Finish & Save
                                    </LuxeButton>
                                ) : (
                                    <LuxeButton onClick={handleNext} icon={ArrowRight}>
                                        Next Step
                                    </LuxeButton>
                                )}
                            </div>
                        </form>
                    </LuxeCard>
                </div>

                {/* Right Column: Live Preview */}
                <div className="lg:col-span-1">
                    <div className="sticky top-8">
                        <LuxeCard className="bg-obsidian-100 border-obsidian-300">
                            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-obsidian-200">
                                <Sparkles className="w-4 h-4 text-neon-purple" />
                                <h3 className="font-display font-bold text-white">Live Preview</h3>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <label className="text-xs uppercase tracking-wider text-obsidian-500 font-bold mb-1 block">Brand Identity</label>
                                    <div className="text-white font-display text-xl">
                                        {formValues.brand_name || <span className="text-obsidian-600 italic">Brand Name</span>}
                                    </div>
                                    <div className="text-neon-green text-sm">
                                        {formValues.category || <span className="text-obsidian-600 italic">Category</span>}
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs uppercase tracking-wider text-obsidian-500 font-bold mb-1 block">For</label>
                                    <p className="text-obsidian-300 text-sm">
                                        {formValues.audience_summary || <span className="text-obsidian-600 italic">Target Audience...</span>}
                                    </p>
                                </div>

                                <div>
                                    <label className="text-xs uppercase tracking-wider text-obsidian-500 font-bold mb-1 block">Who Need</label>
                                    <p className="text-obsidian-300 text-sm">
                                        {formValues.core_pain || <span className="text-obsidian-600 italic">Core Pain Point...</span>}
                                    </p>
                                </div>

                                <div>
                                    <label className="text-xs uppercase tracking-wider text-obsidian-500 font-bold mb-1 block">The Promise</label>
                                    <p className="text-white text-sm font-medium">
                                        {formValues.core_promise || <span className="text-obsidian-600 italic">Core Promise...</span>}
                                    </p>
                                </div>

                                {formValues.differentiator && (
                                    <div className="bg-neon-green/5 border border-neon-green/20 rounded p-3">
                                        <label className="text-xs uppercase tracking-wider text-neon-green font-bold mb-1 block">The Edge</label>
                                        <p className="text-obsidian-300 text-xs">
                                            {formValues.differentiator}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </LuxeCard>
                    </div>
                </div>
            </div>
        </div>
    );
}
