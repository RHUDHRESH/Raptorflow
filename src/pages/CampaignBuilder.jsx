import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
    ArrowRight,
    ArrowLeft,
    Check,
    Target,
    Users,
    Zap,
    Calendar,
    DollarSign,
    Layout,
    Rocket
} from 'lucide-react';
import { LuxeHeading, LuxeButton, LuxeCard, LuxeInput, LuxeBadge } from '../components/ui/PremiumUI';
import { campaignService } from '../services/campaignService';
import { useWorkspace } from '../context/WorkspaceContext';
import { toast } from '../components/Toast';

const STEPS = [
    { id: 1, title: 'Strategic Foundation', icon: Target },
    { id: 2, title: 'Objective & Goal', icon: Check },
    { id: 3, title: 'Cohorts & Targeting', icon: Users },
    { id: 4, title: 'Channels & Roles', icon: Zap },
    { id: 5, title: 'Move Plan', icon: Layout },
];

export default function CampaignBuilder() {
    const navigate = useNavigate();
    const { activeWorkspace } = useWorkspace();
    const [currentStep, setCurrentStep] = useState(1);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        name: '',
        positioning_id: '',
        objective_type: 'conversion', // awareness, consideration, conversion, retention, advocacy
        objective: '',
        target_metric: '',
        target_value: 0,
        budget: 0,
        start_date: '',
        end_date: '',
        cohorts: [], // { cohort_id, journey_stage_target, priority }
        channels: [], // { channel, role, budget_allocation }
    });

    const handleNext = () => {
        if (currentStep < STEPS.length) {
            setCurrentStep(prev => prev + 1);
        } else {
            handleSubmit();
        }
    };

    const handleBack = () => {
        if (currentStep > 1) {
            setCurrentStep(prev => prev - 1);
        }
    };

    const handleSubmit = async () => {
        if (!activeWorkspace) return;
        setIsSubmitting(true);
        try {
            const { data, error } = await campaignService.createCampaign(formData);
            if (data) {
                toast.success('Campaign created successfully!');
                // Trigger auto-plan if requested or by default
                await campaignService.autoplanMoves(data.id);
                navigate(`/campaigns/${data.id}`);
            } else {
                toast.error('Failed to create campaign');
                console.error(error);
            }
        } catch (error) {
            console.error(error);
            toast.error('An error occurred');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto px-6 py-8 flex gap-8 h-[calc(100vh-100px)]">
            {/* Left Sidebar - Stepper */}
            <div className="w-64 flex-shrink-0 space-y-6">
                <div className="mb-8">
                    <LuxeHeading level={3}>New Campaign</LuxeHeading>
                    <p className="text-sm text-neutral-500 mt-2">Design your winning strategy.</p>
                </div>
                
                <div className="space-y-1 relative">
                    <div className="absolute left-[15px] top-4 bottom-4 w-0.5 bg-neutral-100 -z-10" />
                    {STEPS.map((step, index) => {
                        const isActive = step.id === currentStep;
                        const isCompleted = step.id < currentStep;
                        const Icon = step.icon;

                        return (
                            <div key={step.id} className="flex items-center gap-3 py-3 relative bg-white">
                                <div className={`
                                    w-8 h-8 rounded-none flex items-center justify-center border-2 transition-colors
                                    ${isActive ? 'border-neutral-900 bg-neutral-900 text-white' : 
                                      isCompleted ? 'border-green-500 bg-green-500 text-white' : 'border-neutral-200 text-neutral-400'}
                                `}>
                                    {isCompleted ? <Check className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                                </div>
                                <span className={`text-sm font-medium transition-colors ${isActive ? 'text-neutral-900' : 'text-neutral-500'}`}>
                                    {step.title}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Right Content - Form Area */}
            <div className="flex-1 flex flex-col">
                <div className="flex-1 overflow-y-auto pr-4 pb-8">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentStep}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.3 }}
                        >
                            {currentStep === 1 && (
                                <div className="space-y-6">
                                    <LuxeHeading level={4} className="mb-4">Strategic Foundation</LuxeHeading>
                                    {/* Positioning Selector Mock */}
                                    <LuxeCard className="p-6 border-l-4 border-l-neutral-900">
                                        <h3 className="text-lg font-bold mb-2">Current Positioning: Enterprise Leader</h3>
                                        <p className="text-neutral-600 mb-4">
                                            "For Enterprise CTOs who struggle with tool sprawl, RaptorFlow is the Strategic OS that unifies execution..."
                                        </p>
                                        <LuxeBadge>Change Positioning (Coming Soon)</LuxeBadge>
                                    </LuxeCard>
                                    
                                    <div className="space-y-4">
                                        <label className="block text-sm font-medium text-neutral-700">Which proof points will we lean on?</label>
                                        <div className="flex gap-3">
                                            {['ROI Case Studies', 'Security Compliance', 'Integration Speed'].map(p => (
                                                <button key={p} className="px-4 py-2 border border-neutral-200 rounded-none hover:border-neutral-900 transition-colors focus:bg-neutral-50 font-medium uppercase tracking-wider text-xs">
                                                    {p}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {currentStep === 2 && (
                                <div className="space-y-6">
                                    <LuxeHeading level={4} className="mb-4">Objective & Goal</LuxeHeading>
                                    
                                    <LuxeInput 
                                        label="Campaign Name"
                                        value={formData.name}
                                        onChange={e => setFormData({...formData, name: e.target.value})}
                                        placeholder="e.g., Q1 Enterprise Expansion"
                                    />

                                    <div>
                                        <label className="block text-sm font-medium text-neutral-700 mb-2">Objective Type</label>
                                        <div className="flex gap-2">
                                            {['awareness', 'consideration', 'conversion', 'retention'].map(type => (
                                                <button
                                                    key={type}
                                                    onClick={() => setFormData({...formData, objective_type: type})}
                                                    className={`px-4 py-2 rounded-none border uppercase tracking-wider text-xs font-bold transition-all ${
                                                        formData.objective_type === type 
                                                        ? 'bg-neutral-900 text-white border-neutral-900' 
                                                        : 'bg-white text-neutral-600 border-neutral-200 hover:border-neutral-400'
                                                    }`}
                                                >
                                                    {type}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <LuxeInput 
                                        label="One-line Objective"
                                        value={formData.objective}
                                        onChange={e => setFormData({...formData, objective: e.target.value})}
                                        placeholder="e.g., Increase demo requests from Enterprise CTOs by 40%"
                                    />

                                    <div className="grid grid-cols-2 gap-4">
                                        <LuxeInput 
                                            label="Target Metric"
                                            value={formData.target_metric}
                                            onChange={e => setFormData({...formData, target_metric: e.target.value})}
                                            placeholder="e.g., Demo Requests"
                                        />
                                        <LuxeInput 
                                            label="Target Value"
                                            type="number"
                                            value={formData.target_value}
                                            onChange={e => setFormData({...formData, target_value: Number(e.target.value)})}
                                        />
                                    </div>
                                    
                                    <div className="grid grid-cols-2 gap-4">
                                        <LuxeInput 
                                            label="Start Date"
                                            type="date"
                                            value={formData.start_date}
                                            onChange={e => setFormData({...formData, start_date: e.target.value})}
                                        />
                                        <LuxeInput 
                                            label="End Date"
                                            type="date"
                                            value={formData.end_date}
                                            onChange={e => setFormData({...formData, end_date: e.target.value})}
                                        />
                                    </div>
                                </div>
                            )}

                            {currentStep === 3 && (
                                <div className="space-y-6">
                                    <LuxeHeading level={4} className="mb-4">Target Cohorts</LuxeHeading>
                                    <p className="text-neutral-600">Select who this campaign is for and where we want to move them.</p>
                                    
                                    <div className="border border-neutral-200 rounded-none p-4 flex items-center gap-4 bg-neutral-50">
                                        <div className="w-10 h-10 rounded-none bg-white flex items-center justify-center border border-neutral-200 text-xl">🎯</div>
                                        <div className="flex-1">
                                            <h4 className="font-bold">Enterprise CTOs</h4>
                                            <p className="text-xs text-neutral-500">Buying Trigger: Fiscal year planning • Barrier: Security audit</p>
                                        </div>
                                        <LuxeButton size="sm" variant="secondary">Selected</LuxeButton>
                                    </div>
                                    
                                    {/* Journey Stage Selector Mock */}
                                    <div className="bg-white p-4 border border-neutral-200 rounded-none">
                                        <div className="flex justify-between text-sm mb-2">
                                            <span>Current: Problem Aware</span>
                                            <ArrowRight className="w-4 h-4 text-neutral-400" />
                                            <span className="font-bold text-green-600">Target: Most Aware</span>
                                        </div>
                                        <div className="h-2 bg-neutral-100 rounded-none overflow-hidden">
                                            <div className="h-full bg-gradient-to-r from-neutral-400 to-green-500 w-3/4 ml-auto rounded-none opacity-50" />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {currentStep === 4 && (
                                <div className="space-y-6">
                                    <LuxeHeading level={4} className="mb-4">Channel Strategy</LuxeHeading>
                                    <div className="grid grid-cols-2 gap-4">
                                        {['LinkedIn', 'Email', 'Web', 'Events'].map(channel => (
                                            <div key={channel} className="border border-neutral-200 rounded-none p-4 hover:border-neutral-900 cursor-pointer transition-colors">
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="font-bold">{channel}</span>
                                                    <LuxeBadge>Reach</LuxeBadge>
                                                </div>
                                                <p className="text-xs text-neutral-500">Estimated Budget: $5,000</p>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="mt-4">
                                        <LuxeInput 
                                            label="Total Budget"
                                            type="number"
                                            value={formData.budget}
                                            onChange={e => setFormData({...formData, budget: Number(e.target.value)})}
                                            icon={DollarSign}
                                        />
                                    </div>
                                </div>
                            )}

                            {currentStep === 5 && (
                                <div className="space-y-6">
                                    <LuxeHeading level={4} className="mb-4">Plan Preview</LuxeHeading>
                                    <div className="bg-neutral-900 text-white p-6 rounded-none mb-6">
                                        <h3 className="text-xl font-bold mb-2">{formData.name || 'Untitled Campaign'}</h3>
                                        <p className="text-neutral-400">{formData.objective || 'No objective set'}</p>
                                        <div className="mt-4 flex gap-4 text-sm">
                                            <span>Metric: {formData.target_metric}</span>
                                            <span>Target: {formData.target_value}</span>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <h4 className="font-bold text-neutral-900 flex items-center gap-2 uppercase tracking-wider text-sm">
                                            <Rocket className="w-4 h-4" />
                                            Recommended Move Sequence
                                        </h4>
                                        <div className="border-l-2 border-neutral-200 pl-4 space-y-6">
                                            {[
                                                { name: 'Authority Sprint', type: 'Authority', desc: 'Establish expertise' },
                                                { name: 'Consideration Phase', type: 'Consideration', desc: 'Show ROI & Proof' },
                                                { name: 'Objection Crusher', type: 'Objection', desc: 'Address key blockers' },
                                                { name: 'Conversion Push', type: 'Conversion', desc: 'Drive final action' }
                                            ].map((move, i) => (
                                                <div key={i} className="relative">
                                                    <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-none bg-neutral-300 border-2 border-white" />
                                                    <div className="bg-white border border-neutral-200 rounded-none p-3">
                                                        <div className="flex justify-between items-center">
                                                            <span className="font-bold text-sm">{move.name}</span>
                                                            <LuxeBadge size="sm">{move.type}</LuxeBadge>
                                                        </div>
                                                        <p className="text-xs text-neutral-500 mt-1">{move.desc}</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Footer Actions */}
                <div className="py-4 border-t border-neutral-200 flex justify-between items-center bg-white">
                    <LuxeButton 
                        variant="secondary" 
                        onClick={handleBack}
                        disabled={currentStep === 1}
                        icon={ArrowLeft}
                    >
                        Back
                    </LuxeButton>
                    
                    {currentStep === 5 ? (
                        <LuxeButton 
                            onClick={handleSubmit}
                            isLoading={isSubmitting}
                            icon={Rocket}
                        >
                            Launch Campaign
                        </LuxeButton>
                    ) : (
                        <LuxeButton 
                            onClick={handleNext}
                            icon={ArrowRight}
                        >
                            Next Step
                        </LuxeButton>
                    )}
                </div>
            </div>
            
            {/* Right Panel - Narrative Summary (Sticky) */}
            <div className="w-80 flex-shrink-0 hidden xl:block">
                <div className="bg-neutral-50 border border-neutral-200 rounded-none p-6 sticky top-8">
                    <LuxeHeading level={5} className="mb-4">Campaign Narrative</LuxeHeading>
                    <div className="space-y-4 text-sm text-neutral-600">
                        <p>
                            You're planning a <span className="font-bold text-neutral-900 uppercase">{formData.objective_type}</span> campaign 
                            targeting <span className="font-bold text-neutral-900">Enterprise CTOs</span>.
                        </p>
                        <p>
                            The goal is to hit <span className="font-bold text-neutral-900">{formData.target_value} {formData.target_metric}</span> 
                            by {formData.end_date || 'the deadline'}.
                        </p>
                        <p>
                            We'll use <span className="font-bold text-neutral-900">LinkedIn & Email</span> to move them from 
                            <span className="italic"> Problem Aware</span> to <span className="italic">Most Aware</span>.
                        </p>
                        <div className="pt-4 border-t border-neutral-200 mt-4">
                            <p className="text-xs text-neutral-400 italic">
                                "Strategy without tactics is the slowest route to victory. Tactics without strategy is the noise before defeat."
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
