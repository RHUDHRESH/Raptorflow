import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, Check, X, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

interface WizardLayoutProps {
    currentStep: number;
    totalSteps: number;
    canGoBack: boolean;
    onBack: () => void;
    onNext: () => void;
    isLastStep: boolean;
    isNextDisabled?: boolean;
    children: React.ReactNode;
    title?: string;
    lastSaved?: Date;
    stepLabel?: string;
    timeRemaining?: string;
    hint?: string;
}

export default function WizardLayout({
    currentStep,
    totalSteps,
    canGoBack,
    onBack,
    onNext,
    isLastStep,
    isNextDisabled,
    children,
    lastSaved,
    title,
    stepLabel,
    timeRemaining,
    hint
}: WizardLayoutProps) {
    const progress = (currentStep / totalSteps) * 100;
    const [showExitConfirm, setShowExitConfirm] = useState(false);
    const router = useRouter();

    const handleExit = () => {
        // Just redirect if on first step or nothing likely saved yet?
        // But for consistency let's ask.
        setShowExitConfirm(true);
    };

    const confirmExit = () => {
        router.push('/target');
    };

    // Global Hotkeys
    React.useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                if (!isNextDisabled) {
                    onNext();
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [onNext, isNextDisabled]);

    return (
        <div className="min-h-screen bg-[#F3F4EE] text-[#2D3538] flex flex-col relative">
            {/* Exit Confirmation Modal */}
            <AnimatePresence>
                {showExitConfirm && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-[#2D3538]/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                        onClick={() => setShowExitConfirm(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()}
                            className="bg-white rounded-2xl p-8 max-w-sm w-full shadow-2xl space-y-6"
                        >
                            <div className="flex flex-col items-center text-center space-y-2">
                                <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center text-yellow-600 mb-2">
                                    <AlertTriangle className="w-6 h-6" />
                                </div>
                                <h3 className="font-serif text-2xl text-[#2D3538]">Exit Wizard?</h3>
                                <p className="text-[#5B5F61]">Your progress is saved to this device, but it's safer to finish.</p>
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowExitConfirm(false)}
                                    className="flex-1 py-3 px-4 rounded-xl border border-[#C0C1BE] font-medium hover:bg-[#F3F4EE] transition-colors"
                                >
                                    Stay
                                </button>
                                <button
                                    onClick={confirmExit}
                                    className="flex-1 py-3 px-4 rounded-xl bg-[#2D3538] text-white font-medium hover:bg-[#1A1F21] transition-colors"
                                >
                                    Exit
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Header */}
            <header className="px-8 py-6 flex items-center justify-between sticky top-0 z-40 bg-[#F3F4EE]/80 backdrop-blur-md border-b border-[#C0C1BE]/20 transition-all duration-300">
                <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-4">
                        <div className="h-8 w-8 bg-[#2D3538] rounded-full flex items-center justify-center text-[#F3F4EE] font-serif font-bold shadow-lg">
                            R
                        </div>
                        <span className="font-serif text-xl tracking-tight">RaptorFlow</span>
                    </div>
                    {hint && (
                        <motion.div
                            initial={{ opacity: 0, y: -5 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="ml-12 text-xs text-[#5B5F61] font-medium flex items-center gap-2"
                        >
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                            {hint}
                        </motion.div>
                    )}
                </div>

                {/* Exit Button */}
                <button
                    onClick={handleExit}
                    className="p-2 hover:bg-[#E5E7E1] rounded-full transition-colors text-[#5B5F61]"
                >
                    <X className="w-5 h-5" />
                </button>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex flex-col items-center justify-center p-6 relative overflow-hidden">
                <div className="w-full max-w-3xl">
                    {children}
                </div>
            </main>

            {/* Footer Navigation */}
            <footer className="px-8 py-6 flex flex-col gap-6 bg-[#F3F4EE]/90 backdrop-blur sticky bottom-0 z-10 border-t border-[#C0C1BE]/20">
                {/* Progress Bar & Context */}
                <div className="w-full max-w-xl mx-auto space-y-2">
                    <div className="flex items-center justify-between text-xs font-medium text-[#9D9F9F]">
                        <span>{stepLabel || `Step ${currentStep} of ${totalSteps}`}</span>
                        {timeRemaining && <span>{timeRemaining}</span>}
                    </div>

                    <div className="h-1.5 bg-[#C0C1BE]/30 rounded-full overflow-hidden relative">
                        <div
                            className="absolute inset-0 bg-gradient-to-r from-transparent via-[#F3F4EE]/50 to-transparent animate-shimmer z-10"
                            style={{ backgroundSize: '200% 100%' }}
                        />
                        <div
                            className="h-full bg-[#2D3538] transition-all duration-700 ease-[cubic-bezier(0.25,1,0.5,1)] relative z-0"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>

                <div className="flex justify-between items-center w-full max-w-4xl mx-auto">
                    <button
                        onClick={onBack}
                        disabled={!canGoBack}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-colors
                            ${!canGoBack
                                ? 'opacity-0 pointer-events-none'
                                : 'text-[#5B5F61] hover:bg-[#EDEFE9]'
                            } `}
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back
                    </button>

                    <motion.button
                        onClick={() => {
                            if (isNextDisabled) {
                                // Trigger shake
                                const btn = document.getElementById('next-btn');
                                if (btn) {
                                    btn.animate([
                                        { transform: 'translateX(0)' },
                                        { transform: 'translateX(-4px)' },
                                        { transform: 'translateX(4px)' },
                                        { transform: 'translateX(-4px)' },
                                        { transform: 'translateX(0)' }
                                    ], { duration: 300 });
                                }
                            } else {
                                onNext();
                            }
                        }}
                        id="next-btn"
                        // disabled={isNextDisabled} // We remove native disabled to allow click for shake, but handle logic
                        whileHover={{ scale: isNextDisabled ? 1 : 1.02 }}
                        whileTap={{ scale: isNextDisabled ? 1 : 0.98 }}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`flex items-center gap-2 px-8 py-3 rounded-xl font-medium shadow-sm transition-all
                            ${isNextDisabled
                                ? 'bg-[#C0C1BE] text-[#F3F4EE] cursor-not-allowed opacity-80' // Visual disabled looking but clickable
                                : 'bg-[#2D3538] text-[#F3F4EE] hover:bg-[#1A1F21]'
                            }`}
                    >
                        {isLastStep ? 'Complete Profile' : 'Continue'}
                        {!isLastStep && <ArrowRight className="w-4 h-4" />}
                    </motion.button>
                </div>
            </footer >
        </div >
    );
}
