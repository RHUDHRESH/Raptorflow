import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft, Upload, FileText, Check, AlertCircle, Loader2 } from 'lucide-react';
import { LuxeHeading, LuxeCard, LuxeButton, LuxeInput, LuxeTextArea, LuxeBadge } from '../ui/PremiumUI';
import PositioningMap from './PositioningMap';

const Act1Mirror = ({ onComplete }) => {
    const [step, setStep] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        // Step 1: Story
        story: '',
        why: '',
        stakes: '',
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

    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleNext = () => {
        setStep(prev => prev + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleBack = () => {
        setStep(prev => prev - 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const analyzeMirrorStep = async () => {
        setIsLoading(true);
        // Simulate AI analysis
        await new Promise(resolve => setTimeout(resolve, 2000));

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
            coordinates: { x: 65, y: 40 } // Mock coordinates for the map
        });

        setIsLoading(false);
        handleNext();
    };

    const renderStep1 = () => (
        <div className="max-w-3xl mx-auto space-y-8">
            <div className="text-center mb-12">
                <LuxeBadge variant="outline" className="mb-4">Step 1 of 4</LuxeBadge>
                <LuxeHeading level={2}>Who are you and why this?</LuxeHeading>
                <p className="text-neutral-500 mt-2">The best positioning starts with the founder's truth.</p>
            </div>

            <LuxeCard className="space-y-8 p-8">
                <LuxeTextArea
                    label="What's your story?"
                    placeholder="I was running a marketing agency when I realized..."
                    helperText="The moments that led you here."
                    value={formData.story}
                    onChange={(e) => handleInputChange('story', e.target.value)}
                    rows={4}
                />
                <LuxeTextArea
                    label="Why does this problem matter to you personally?"
                    placeholder="I watched my clients waste millions on..."
                    helperText="The emotional hook."
                    value={formData.why}
                    onChange={(e) => handleInputChange('why', e.target.value)}
                    rows={3}
                />
                <LuxeTextArea
                    label="What happens if you fail?"
                    placeholder="Small businesses will continue to be crushed by..."
                    helperText="The stakes. Who loses if you don't win?"
                    value={formData.stakes}
                    onChange={(e) => handleInputChange('stakes', e.target.value)}
                    rows={3}
                />
            </LuxeCard>

            <div className="flex justify-end">
                <LuxeButton
                    onClick={handleNext}
                    disabled={!formData.story && !formData.why && !formData.stakes}
                    size="lg"
                >
                    Next Step <ArrowRight className="ml-2 w-4 h-4" />
                </LuxeButton>
            </div>
        </div>
    );

    const renderStep2 = () => (
        <div className="max-w-3xl mx-auto space-y-8">
            <div className="text-center mb-12">
                <LuxeBadge variant="outline" className="mb-4">Step 2 of 4</LuxeBadge>
                <LuxeHeading level={2}>Let's get the facts straight.</LuxeHeading>
                <p className="text-neutral-500 mt-2">The physics of your business model.</p>
            </div>

            <LuxeCard className="space-y-8 p-8">
                <LuxeInput
                    label="Company Name"
                    value={formData.companyName}
                    onChange={(e) => handleInputChange('companyName', e.target.value)}
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-neutral-900">Category</label>
                        <select
                            className="w-full p-3 bg-white border border-neutral-200 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all"
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
                        <label className="text-sm font-medium text-neutral-900">Business Model</label>
                        <select
                            className="w-full p-3 bg-white border border-neutral-200 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all"
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
                        <label className="text-sm font-medium text-neutral-900">Typical ACV / Price</label>
                        <select
                            className="w-full p-3 bg-white border border-neutral-200 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all"
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
                        <label className="text-sm font-medium text-neutral-900">Sales Cycle</label>
                        <select
                            className="w-full p-3 bg-white border border-neutral-200 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all"
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
    );

    const renderStep3 = () => (
        <div className="max-w-3xl mx-auto space-y-8">
            <div className="text-center mb-12">
                <LuxeBadge variant="outline" className="mb-4">Step 3 of 4</LuxeBadge>
                <LuxeHeading level={2}>Your Messy Truth</LuxeHeading>
                <p className="text-neutral-500 mt-2">Don't edit. Just dump everything you have.</p>
            </div>

            <LuxeCard className="space-y-8 p-8">
                <LuxeTextArea
                    label="Paste any messy copy"
                    placeholder="Investor updates, website copy, random slack messages, your current pitch..."
                    helperText="We'll extract the gold from this."
                    value={formData.messyCopy}
                    onChange={(e) => handleInputChange('messyCopy', e.target.value)}
                    rows={8}
                />
                <LuxeInput
                    label="Website URL (Optional)"
                    placeholder="https://..."
                    value={formData.url}
                    onChange={(e) => handleInputChange('url', e.target.value)}
                />

                <div className="space-y-2">
                    <label className="text-sm font-medium text-neutral-900">Upload Documents</label>
                    <div className="border-2 border-dashed border-neutral-200 rounded-xl p-8 text-center hover:bg-neutral-50 transition-colors cursor-pointer group">
                        <div className="w-12 h-12 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-white group-hover:shadow-sm transition-all">
                            <Upload className="w-6 h-6 text-neutral-400 group-hover:text-black" />
                        </div>
                        <p className="text-sm font-medium text-neutral-900">Click to upload or drag and drop</p>
                        <p className="text-xs text-neutral-500 mt-1">PDF, DOCX, or Images (Max 10MB)</p>
                        {/* TODO: Implement file upload and OCR */}
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
    );

    const renderStep4 = () => (
        <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
                <LuxeBadge variant="outline" className="mb-4">Analysis Complete</LuxeBadge>
                <LuxeHeading level={2}>Here's where you stand.</LuxeHeading>
                <p className="text-neutral-500 mt-2">Based on your story, business model, and current messaging.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                {/* Left: Map */}
                <div className="space-y-6">
                    <LuxeCard className="p-6 h-[500px] flex flex-col">
                        <h3 className="font-serif text-lg font-bold mb-4">Market Position</h3>
                        <div className="flex-1 relative rounded-lg border border-neutral-100 bg-neutral-50 overflow-hidden">
                            <PositioningMap
                                initialX={analysis?.coordinates?.x || 50}
                                initialY={analysis?.coordinates?.y || 50}
                                readOnly={true}
                            />
                        </div>
                        <p className="text-xs text-neutral-400 mt-4 text-center">
                            This is where the AI places you based on your inputs.
                        </p>
                    </LuxeCard>
                </div>

                {/* Right: Classifications */}
                <div className="space-y-6">
                    <LuxeCard className="p-6 border-l-4 border-l-black">
                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-2">Market Reality</h4>
                        <h3 className="font-serif text-xl font-bold text-neutral-900 mb-2">{analysis?.marketReality?.title}</h3>
                        <p className="text-neutral-600 leading-relaxed">{analysis?.marketReality?.description}</p>
                    </LuxeCard>

                    <LuxeCard className="p-6 border-l-4 border-l-neutral-400">
                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-2">Founder Arc</h4>
                        <h3 className="font-serif text-xl font-bold text-neutral-900 mb-2">{analysis?.founderArc?.title}</h3>
                        <p className="text-neutral-600 leading-relaxed">{analysis?.founderArc?.description}</p>
                    </LuxeCard>

                    <LuxeCard className="p-6 border-l-4 border-l-neutral-200">
                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-2">Messaging Pattern</h4>
                        <h3 className="font-serif text-xl font-bold text-neutral-900 mb-2">{analysis?.messagingPattern?.title}</h3>
                        <p className="text-neutral-600 leading-relaxed">{analysis?.messagingPattern?.description}</p>
                    </LuxeCard>

                    <div className="flex gap-4 pt-4">
                        <LuxeButton
                            variant="outline"
                            className="flex-1"
                            onClick={() => setStep(3)} // Go back to fix
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
                </div>
            </div>
        </div>
    );

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full"
        >
            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}
            {step === 4 && renderStep4()}
        </motion.div>
    );
};

export default Act1Mirror;
