import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Upload, FileText, Check, AlertCircle, Loader2 } from 'lucide-react';
import { LuxeHeading, LuxeCard, LuxeButton, LuxeInput, LuxeTextarea, LuxeBadge } from '../ui/PremiumUI';
import PositioningMap from './PositioningMap';

const Act1Mirror = ({ onComplete }) => {
    const [stepIndex, setStepIndex] = useState(0); // 0: Story, 1: Business, 2: Messy Truth, 3: Analysis
    const [storySubstep, setStorySubstep] = useState(0); // 0-2 for the three story questions
    const [isLoading, setIsLoading] = useState(false);

    const [formData, setFormData] = useState({
        // Step 1: Story (3 substeps)
        founderStory: '',
        personalWhy: '',
        failureStakes: '',
        // Step 2: Business
        companyName: '',
        category: '',
        model: '',
        acv: '',
        salesCycle: '',
        // Step 3: Messy Truth
        messyCopy: '',
        url: '',
        files: []
    });

    const [analysis, setAnalysis] = useState(null);
    const [showFeedback, setShowFeedback] = useState(false);
    const [feedback, setFeedback] = useState('');

    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleStoryNext = () => {
        if (storySubstep < 2) {
            setStorySubstep(prev => prev + 1);
        } else {
            setStepIndex(1);
            setStorySubstep(0);
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleStoryBack = () => {
        if (storySubstep > 0) {
            setStorySubstep(prev => prev - 1);
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleNext = () => {
        setStepIndex(prev => prev + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleBack = () => {
        if (stepIndex === 1) {
            setStepIndex(0);
            setStorySubstep(2); // Go back to last story question
        } else {
            setStepIndex(prev => prev - 1);
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const analyzeMirrorStep = async () => {
        setIsLoading(true);
        // Simulate AI analysis
        await new Promise(resolve => setTimeout(resolve, 2500));

        setAnalysis({
            marketReality: {
                title: "Crowded Mid-Tier SaaS",
                description: "You're fighting in a red ocean with generic feature claims. Competitors are well-funded but slow."
            },
            founderArc: {
                title: "The Visionary Operator",
                description: "You've lived the problem, but your pitch is too technical. You need to elevate to the emotional outcome."
            },
            messagingPattern: {
                title: "Feature-Led & Safe",
                description: "Your current copy plays it safe. It lacks a 'villain' and a clear cost of inaction."
            },
            coordinates: { x: 65, y: 40 }
        });

        setIsLoading(false);
        setStepIndex(3);
    };

    const storyQuestions = [
        {
            label: "What's your story?",
            placeholder: "I was running a marketing agency when I realized...",
            field: 'founderStory'
        },
        {
            label: "Why does this problem matter to you personally?",
            placeholder: "I watched my clients waste millions on...",
            field: 'personalWhy'
        },
        {
            label: "What happens if you fail?",
            placeholder: "Small businesses will continue to be crushed by...",
            field: 'failureStakes'
        }
    ];

    // Step 1: Story (one question at a time)
    const renderStep1 = () => {
        const currentQuestion = storyQuestions[storySubstep];
        const currentValue = formData[currentQuestion.field];

        return (
            <div className="min-h-[70vh] flex flex-col items-center justify-center">
                <div className="w-full max-w-[720px] mx-auto space-y-8">
                    {/* Header */}
                    <div className="text-center space-y-4">
                        <LuxeBadge variant="outline" className="mb-4">Step 1 of 4</LuxeBadge>
                        <h1 className="font-display text-4xl lg:text-5xl" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                            Who are you and why this?
                        </h1>
                        <p className="text-lg" style={{ color: 'var(--ink-soft)' }}>
                            The best positioning starts with the founder's truth.
                        </p>
                    </div>

                    {/* Question Card */}
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={storySubstep}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.3 }}
                        >
                            <LuxeCard className="p-8 space-y-6">
                                <div className="text-center space-y-6">
                                    <p className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--ink-soft)' }}>
                                        Question {storySubstep + 1} of 3
                                    </p>
                                    <h2 className="font-display text-2xl mb-6" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                                        {currentQuestion.label}
                                    </h2>
                                </div>

                                {/* Over-engineered Textarea */}
                                <div className="relative">
                                    <textarea
                                        value={currentValue}
                                        onChange={(e) => {
                                            handleInputChange(currentQuestion.field, e.target.value);
                                            // Auto-resize
                                            e.target.style.height = 'auto';
                                            e.target.style.height = e.target.scrollHeight + 'px';
                                        }}
                                        placeholder={currentQuestion.placeholder}
                                        className="w-full px-0 py-4 bg-transparent text-lg leading-relaxed outline-none resize-none transition-all duration-200"
                                        style={{
                                            border: 'none',
                                            borderBottom: '2px solid var(--border-subtle)',
                                            color: 'var(--ink-strong)',
                                            fontFamily: 'var(--font-body)',
                                            minHeight: '200px',
                                            lineHeight: '1.8'
                                        }}
                                        onFocus={(e) => {
                                            e.target.style.borderBottomColor = 'var(--ink-strong)';
                                        }}
                                        onBlur={(e) => {
                                            e.target.style.borderBottomColor = 'var(--border-subtle)';
                                        }}
                                    />

                                    {/* Character count and typing indicator */}
                                    <div className="flex items-center justify-between mt-3">
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: currentValue.length > 0 ? 1 : 0 }}
                                            className="flex items-center gap-2"
                                        >
                                            <div className="flex gap-1">
                                                <motion.div
                                                    animate={{ scale: [1, 1.2, 1] }}
                                                    transition={{ duration: 1, repeat: Infinity }}
                                                    className="w-1 h-1 rounded-full"
                                                    style={{ backgroundColor: 'var(--ink-soft)' }}
                                                />
                                                <motion.div
                                                    animate={{ scale: [1, 1.2, 1] }}
                                                    transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                                                    className="w-1 h-1 rounded-full"
                                                    style={{ backgroundColor: 'var(--ink-soft)' }}
                                                />
                                                <motion.div
                                                    animate={{ scale: [1, 1.2, 1] }}
                                                    transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                                                    className="w-1 h-1 rounded-full"
                                                    style={{ backgroundColor: 'var(--ink-soft)' }}
                                                />
                                            </div>
                                            <span className="text-xs" style={{ color: 'var(--ink-soft)' }}>
                                                {currentValue.length} characters
                                            </span>
                                        </motion.div>

                                        <motion.div
                                            initial={{ opacity: 0, scale: 0.8 }}
                                            animate={{
                                                opacity: currentValue.trim().length > 20 ? 1 : 0,
                                                scale: currentValue.trim().length > 20 ? 1 : 0.8
                                            }}
                                            className="text-xs font-medium flex items-center gap-1"
                                            style={{ color: 'var(--ink-strong)' }}
                                        >
                                            <Check className="w-3 h-3" />
                                            Looking good
                                        </motion.div>
                                    </div>
                                </div>
                            </LuxeCard>
                        </motion.div>
                    </AnimatePresence>

                    {/* Navigation */}
                    <div className="flex justify-between items-center">
                        {storySubstep > 0 ? (
                            <LuxeButton variant="ghost" onClick={handleStoryBack}>
                                <ArrowLeft className="mr-2 w-4 h-4" /> Back
                            </LuxeButton>
                        ) : (
                            <div></div>
                        )}
                        <LuxeButton
                            onClick={handleStoryNext}
                            disabled={!currentValue.trim()}
                            size="lg"
                        >
                            {storySubstep < 2 ? 'Next Question' : 'Continue'} <ArrowRight className="ml-2 w-4 h-4" />
                        </LuxeButton>
                    </div>
                </div>
            </div>
        );
    };

    // Step 2: Business Facts
    const renderStep2 = () => (
        <div className="min-h-[70vh] flex flex-col items-center justify-center">
            <div className="w-full max-w-[720px] mx-auto space-y-8">
                <div className="text-center space-y-4 mb-8">
                    <LuxeBadge variant="outline" className="mb-4">Step 2 of 4</LuxeBadge>
                    <h1 className="font-display text-4xl lg:text-5xl" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                        Let's get the facts straight.
                    </h1>
                    <p className="text-lg" style={{ color: 'var(--ink-soft)' }}>
                        The physics of your business model.
                    </p>
                </div>

                <LuxeCard className="p-8 space-y-6">
                    <LuxeInput
                        label="Company Name"
                        value={formData.companyName}
                        onChange={(e) => handleInputChange('companyName', e.target.value)}
                    />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-semibold" style={{ color: 'var(--ink-strong)' }}>Category</label>
                            <select
                                className="w-full p-3 bg-white rounded-lg focus:ring-2 focus:ring-black outline-none transition-all"
                                style={{ border: '1px solid var(--border-subtle)', color: 'var(--ink-strong)' }}
                                value={formData.category}
                                onChange={(e) => handleInputChange('category', e.target.value)}
                            >
                                <option value="">Select Category...</option>
                                <option value="b2b">B2B Software</option>
                                <option value="b2c">B2C App</option>
                                <option value="agency">Agency / Service</option>
                                <option value="marketplace">Marketplace</option>
                                <option value="ecommerce">E-commerce</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-semibold" style={{ color: 'var(--ink-strong)' }}>Business Model</label>
                            <select
                                className="w-full p-3 bg-white rounded-lg focus:ring-2 focus:ring-black outline-none transition-all"
                                style={{ border: '1px solid var(--border-subtle)', color: 'var(--ink-strong)' }}
                                value={formData.model}
                                onChange={(e) => handleInputChange('model', e.target.value)}
                            >
                                <option value="">Select Model...</option>
                                <option value="saas">SaaS (Subscription)</option>
                                <option value="transactional">Transactional</option>
                                <option value="retainer">Retainer</option>
                                <option value="usage">Usage-based</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-semibold" style={{ color: 'var(--ink-strong)' }}>Typical ACV / Price</label>
                            <select
                                className="w-full p-3 bg-white rounded-lg focus:ring-2 focus:ring-black outline-none transition-all"
                                style={{ border: '1px solid var(--border-subtle)', color: 'var(--ink-strong)' }}
                                value={formData.acv}
                                onChange={(e) => handleInputChange('acv', e.target.value)}
                            >
                                <option value="">Select Price Band...</option>
                                <option value="low">Low ($10 - $100/mo)</option>
                                <option value="mid">Mid ($100 - $1k/mo)</option>
                                <option value="high">High ($1k - $10k/mo)</option>
                                <option value="enterprise">Enterprise ($10k+/mo)</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-semibold" style={{ color: 'var(--ink-strong)' }}>Sales Cycle</label>
                            <select
                                className="w-full p-3 bg-white rounded-lg focus:ring-2 focus:ring-black outline-none transition-all"
                                style={{ border: '1px solid var(--border-subtle)', color: 'var(--ink-strong)' }}
                                value={formData.salesCycle}
                                onChange={(e) => handleInputChange('salesCycle', e.target.value)}
                            >
                                <option value="">Select Cycle...</option>
                                <option value="self-serve">Self-serve (Instant)</option>
                                <option value="days">Days (1-14 days)</option>
                                <option value="weeks">Weeks (2-8 weeks)</option>
                                <option value="months">Months (3+ months)</option>
                            </select>
                        </div>
                    </div>
                </LuxeCard>

                <div className="flex justify-between">
                    <LuxeButton variant="ghost" onClick={handleBack}>
                        <ArrowLeft className="mr-2 w-4 h-4" /> Back
                    </LuxeButton>
                    <LuxeButton onClick={handleNext} size="lg">
                        Next Step <ArrowRight className="ml-2 w-4 h-4" />
                    </LuxeButton>
                </div>
            </div>
        </div>
    );

    // Step 3: Messy Truth (compact, no scroll)
    const renderStep3 = () => (
        <div className="min-h-[70vh] flex flex-col items-center justify-center">
            <div className="w-full max-w-[720px] mx-auto space-y-6">
                <div className="text-center space-y-4 mb-6">
                    <LuxeBadge variant="outline" className="mb-4">Step 3 of 4</LuxeBadge>
                    <h1 className="font-display text-4xl lg:text-5xl" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                        Your Messy Truth
                    </h1>
                    <p className="text-lg" style={{ color: 'var(--ink-soft)' }}>
                        Don't edit. Just dump everything you have.
                    </p>
                </div>

                <LuxeCard className="p-8 space-y-5">
                    <LuxeTextarea
                        label="Paste any messy copy"
                        placeholder="Investor updates, website copy, random slack messages, your current pitch..."
                        helperText="We'll extract the gold from this."
                        value={formData.messyCopy}
                        onChange={(e) => handleInputChange('messyCopy', e.target.value)}
                        rows={6}
                    />
                    <LuxeInput
                        label="Website URL (Optional)"
                        placeholder="https://..."
                        value={formData.url}
                        onChange={(e) => handleInputChange('url', e.target.value)}
                    />

                    <div className="space-y-2">
                        <label className="text-sm font-semibold" style={{ color: 'var(--ink-strong)' }}>Upload Documents</label>
                        <div className="border-2 border-dashed rounded-xl p-6 text-center hover:bg-neutral-50 transition-colors cursor-pointer group" style={{ borderColor: 'var(--border-subtle)' }}>
                            <div className="w-10 h-10 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:bg-white group-hover:shadow-sm transition-all">
                                <Upload className="w-5 h-5" style={{ color: 'var(--ink-soft)' }} />
                            </div>
                            <p className="text-sm font-medium" style={{ color: 'var(--ink-strong)' }}>Click to upload or drag and drop</p>
                            <p className="text-xs mt-1" style={{ color: 'var(--ink-soft)' }}>PDF, DOCX, or Images (Max 10MB)</p>
                        </div>
                    </div>
                </LuxeCard>

                <div className="flex justify-between">
                    <LuxeButton variant="ghost" onClick={handleBack}>
                        <ArrowLeft className="mr-2 w-4 h-4" /> Back
                    </LuxeButton>
                    <LuxeButton onClick={analyzeMirrorStep} size="lg" disabled={isLoading}>
                        {isLoading ? (
                            <>
                                <Loader2 className="mr-2 w-4 h-4 animate-spin" /> Analyzing...
                            </>
                        ) : (
                            <>
                                Make Sense of This <ArrowRight className="ml-2 w-4 h-4" />
                            </>
                        )}
                    </LuxeButton>
                </div>
            </div>
        </div>
    );

    // Loading State
    if (isLoading && stepIndex === 2) {
        return (
            <div className="fixed inset-0 flex items-center justify-center" style={{ backgroundColor: 'var(--bg-app)' }}>
                <div className="text-center space-y-6">
                    <Loader2 className="w-12 h-12 animate-spin mx-auto" style={{ color: 'var(--ink-strong)' }} />
                    <div>
                        <h2 className="font-display text-3xl mb-2" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                            Making sense of the chaos…
                        </h2>
                        <p className="text-base" style={{ color: 'var(--ink-soft)' }}>
                            We're mapping your story, numbers, and copy into the positioning grid.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    // Step 4: Analysis Results
    const renderStep4 = () => {
        return (
            <div className="w-full max-w-7xl mx-auto">
                <div className="text-center mb-12">
                    <LuxeBadge variant="outline" className="mb-4">Analysis Complete</LuxeBadge>
                    <h1 className="font-display text-4xl lg:text-5xl mb-3" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                        Here's where you stand.
                    </h1>
                    <p className="text-lg" style={{ color: 'var(--ink-soft)' }}>
                        Based on your story, business model, and current messaging.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Left: Map */}
                    <div className="space-y-6">
                        <LuxeCard className="p-6 aspect-square flex flex-col">
                            <h3 className="font-semibold text-lg mb-4" style={{ color: 'var(--ink-strong)' }}>Market Position</h3>
                            <div className="flex-1 relative rounded-lg bg-neutral-50 overflow-hidden" style={{ border: '1px solid var(--border-subtle)' }}>
                                <PositioningMap
                                    initialX={analysis?.coordinates?.x || 50}
                                    initialY={analysis?.coordinates?.y || 50}
                                    readOnly={true}
                                />
                            </div>
                            <p className="text-xs mt-4 text-center" style={{ color: 'var(--ink-soft)' }}>
                                This map shows how your current positioning stacks up on price vs service model.
                            </p>
                        </LuxeCard>
                    </div>

                    {/* Right: Classifications */}
                    <div className="space-y-6">
                        <LuxeCard className="p-6 border-l-4" style={{ borderLeftColor: 'var(--ink-strong)' }}>
                            <h4 className="text-xs font-bold uppercase tracking-widest mb-2" style={{ color: 'var(--ink-soft)' }}>Market Reality</h4>
                            <h3 className="font-display text-xl font-medium mb-2" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                                {analysis?.marketReality?.title}
                            </h3>
                            <p className="leading-relaxed" style={{ color: 'var(--ink-soft)' }}>{analysis?.marketReality?.description}</p>
                        </LuxeCard>

                        <LuxeCard className="p-6 border-l-4 border-l-neutral-400">
                            <h4 className="text-xs font-bold uppercase tracking-widest mb-2" style={{ color: 'var(--ink-soft)' }}>Founder Arc</h4>
                            <h3 className="font-display text-xl font-medium mb-2" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                                {analysis?.founderArc?.title}
                            </h3>
                            <p className="leading-relaxed" style={{ color: 'var(--ink-soft)' }}>{analysis?.founderArc?.description}</p>
                        </LuxeCard>

                        <LuxeCard className="p-6 border-l-4 border-l-neutral-200">
                            <h4 className="text-xs font-bold uppercase tracking-widest mb-2" style={{ color: 'var(--ink-soft)' }}>Messaging Pattern</h4>
                            <h3 className="font-display text-xl font-medium mb-2" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                                {analysis?.messagingPattern?.title}
                            </h3>
                            <p className="leading-relaxed" style={{ color: 'var(--ink-soft)' }}>{analysis?.messagingPattern?.description}</p>
                        </LuxeCard>

                        <div className="space-y-4 pt-4">
                            <div className="flex gap-4">
                                <LuxeButton
                                    variant="outline"
                                    className="flex-1"
                                    onClick={() => setShowFeedback(!showFeedback)}
                                >
                                    This feels off
                                </LuxeButton>
                                <LuxeButton
                                    className="flex-1"
                                    onClick={() => onComplete({ ...formData, analysis })}
                                >
                                    This feels right <Check className="ml-2 w-4 h-4" />
                                </LuxeButton>
                            </div>

                            {showFeedback && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    className="space-y-3"
                                >
                                    <LuxeTextarea
                                        label="What feels wrong about this?"
                                        placeholder="Tell us what doesn't match reality so we can adjust your profile."
                                        value={feedback}
                                        onChange={(e) => setFeedback(e.target.value)}
                                        rows={3}
                                    />
                                    <LuxeButton
                                        variant="secondary"
                                        size="sm"
                                        onClick={() => {
                                            // Save feedback
                                            console.log('Feedback:', feedback);
                                            setShowFeedback(false);
                                            // Show toast or confirmation
                                        }}
                                    >
                                        Send feedback & revisit later
                                    </LuxeButton>
                                </motion.div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full py-12"
        >
            {stepIndex === 0 && renderStep1()}
            {stepIndex === 1 && renderStep2()}
            {stepIndex === 2 && renderStep3()}
            {stepIndex === 3 && renderStep4()}
        </motion.div>
    );
};

export default Act1Mirror;
