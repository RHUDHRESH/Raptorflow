'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Check } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useIcpStore } from '@/lib/icp-store';
import { Icp } from '@/types/icp-types';

// Steps
import StepContext from './wizard/StepContext';
import StepProblem from './wizard/StepProblem';
import StepBuyer from './wizard/StepBuyer';
import StepLanguage from './wizard/StepLanguage';
import StepExclusions from './wizard/StepExclusions';
import StepReview from './wizard/StepReview';

const TOTAL_STEPS = 6;

export default function ICPWizard() {
    const router = useRouter();
    const createIcp = useIcpStore((state) => state.createIcp);
    const [currentStep, setCurrentStep] = useState(1);
    const [formData, setFormData] = useState<Partial<Icp>>({
        name: 'New Ideal Customer Profile',
        firmographics: {
            companyType: [],
            geography: [],
            salesMotion: [],
            budgetComfort: [],
            decisionMaker: [],
        },
        painMap: {
            primaryPains: [],
            secondaryPains: [],
            triggerEvents: [],
            urgencyLevel: 'soon',
        },
        psycholinguistics: {
            mindsetTraits: [],
            emotionalTriggers: [],
            tonePreference: [],
            wordsToUse: [],
            wordsToAvoid: [],
            proofPreference: [],
            ctaStyle: [],
        },
        disqualifiers: {
            excludedCompanyTypes: [],
            excludedGeographies: [],
            excludedBehaviors: [],
        },
    });

    const handleNext = () => {
        if (currentStep < TOTAL_STEPS) {
            setCurrentStep(currentStep + 1);
        } else {
            // Final Submit
            createIcp(formData);
            router.push('/target'); // Redirect to dashboard
        }
    };

    const handleBack = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
        }
    };

    const updateFormData = (section: keyof Icp, data: any) => {
        setFormData((prev) => ({
            ...prev,
            [section]: {
                ...(prev[section] as any),
                ...data,
            },
        }));
    };

    return (
        <div className="min-h-screen bg-[#F3F4EE] text-[#2D3538] flex flex-col">
            {/* Header */}
            <header className="px-8 py-6 flex items-center justify-between border-b border-[#C0C1BE]/30">
                <div className="flex items-center gap-4">
                    <div className="h-8 w-8 bg-[#2D3538] rounded-full flex items-center justify-center text-[#F3F4EE] font-serif font-bold">
                        R
                    </div>
                    <span className="font-serif text-xl tracking-tight">RaptorFlow</span>
                </div>
                <div className="text-sm font-medium text-[#5B5F61]">
                    Targeting Setup <span className="opacity-40 mx-2">/</span> Step {currentStep} of {TOTAL_STEPS}
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex flex-col items-center justify-center p-6 relative overflow-hidden">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentStep}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                        className="w-full max-w-2xl"
                    >
                        {currentStep === 1 && (
                            <StepContext
                                data={formData.firmographics!}
                                onChange={(d) => updateFormData('firmographics', d)}
                            />
                        )}
                        {currentStep === 2 && (
                            <StepProblem
                                data={formData.painMap!}
                                onChange={(d) => updateFormData('painMap', d)}
                            />
                        )}
                        {currentStep === 3 && (
                            <StepBuyer
                                firmographics={formData.firmographics!}
                                painMap={formData.painMap!}
                                onChangeFirmographics={(d) => updateFormData('firmographics', d)}
                                onChangePainMap={(d) => updateFormData('painMap', d)}
                            />
                        )}
                        {currentStep === 4 && (
                            <StepLanguage
                                data={formData.psycholinguistics!}
                                onChange={(d) => updateFormData('psycholinguistics', d)}
                            />
                        )}
                        {currentStep === 5 && (
                            <StepExclusions
                                data={formData.disqualifiers!}
                                onChange={(d) => updateFormData('disqualifiers', d)}
                            />
                        )}
                        {currentStep === 6 && (
                            <StepReview
                                data={formData}
                                onChange={(d) => setFormData(p => ({ ...p, ...d }))}
                            />
                        )}
                    </motion.div>
                </AnimatePresence>
            </main>

            {/* Footer Navigation */}
            <footer className="px-8 py-6 border-t border-[#C0C1BE]/30 flex justify-between items-center bg-[#F3F4EE] sticky bottom-0 z-10">
                <button
                    onClick={handleBack}
                    disabled={currentStep === 1}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-colors
            ${currentStep === 1
                            ? 'opacity-0 pointer-events-none'
                            : 'text-[#5B5F61] hover:bg-[#EDEFE9]'
                        }`}
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back
                </button>

                <button
                    onClick={handleNext}
                    className="flex items-center gap-2 px-8 py-3 bg-[#2D3538] text-[#F3F4EE] rounded-xl font-medium shadow-sm hover:translate-y-[-1px] transition-all hover:bg-[#1A1F21]"
                >
                    {currentStep === TOTAL_STEPS ? 'Finish Setup' : 'Continue'}
                    {currentStep === TOTAL_STEPS ? <Check className="w-4 h-4" /> : <ArrowRight className="w-4 h-4" />}
                </button>
            </footer>
        </div>
    );
}
