import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { setSecureLocalStorage } from '../utils/sanitize';
import Act1Mirror from '../components/onboarding/Act1Mirror';
import Act2Battlefield from '../components/onboarding/Act2Battlefield';
import Act3Tribes from '../components/onboarding/Act3Tribes';
import { Sparkles } from 'lucide-react';

const OnboardingLuxe = () => {
    const navigate = useNavigate();
    const [act, setAct] = useState(1);
    const [onboardingData, setOnboardingData] = useState({
        positioning: null,
        strategy: null,
        icps: null
    });

    const handleAct1Complete = (data) => {
        setOnboardingData(prev => ({ ...prev, positioning: data }));
        setAct(2);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleAct2Complete = (data) => {
        setOnboardingData(prev => ({ ...prev, strategy: data }));
        setAct(3);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleAct2Back = () => {
        setAct(1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleAct3Complete = (data) => {
        // Save everything
        const finalData = {
            ...onboardingData,
            icps: data,
            completedAt: new Date().toISOString()
        };

        setSecureLocalStorage('onboardingData', finalData);
        setSecureLocalStorage('onboardingCompleted', 'true');

        // Navigate to Dashboard
        navigate('/dashboard');
    };

    const handleAct3Back = () => {
        setAct(2);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <div className="min-h-screen font-sans selection:bg-neutral-900 selection:text-white" style={{ backgroundColor: 'var(--bg-app)', color: 'var(--ink-strong)' }}>
            {/* Header */}
            <header className="fixed top-0 left-0 right-0 h-16 backdrop-blur-md border-b z-50 flex items-center justify-between px-6 lg:px-12" style={{ backgroundColor: 'rgba(250, 247, 242, 0.8)', borderColor: 'var(--border-subtle)' }}>
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--ink-strong)' }}>
                        <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-bold tracking-widest uppercase text-sm" style={{ fontFamily: 'var(--font-body)' }}>RaptorFlow</span>
                </div>

                {/* Progress */}
                <div className="hidden md:flex items-center gap-4 text-xs font-bold uppercase tracking-widest">
                    <span style={{ color: act >= 1 ? 'var(--ink-strong)' : 'var(--ink-soft)', opacity: act >= 1 ? 1 : 0.3 }}>Act I: The Mirror</span>
                    <span className="w-8 h-px" style={{ backgroundColor: 'var(--border-subtle)' }} />
                    <span style={{ color: act >= 2 ? 'var(--ink-strong)' : 'var(--ink-soft)', opacity: act >= 2 ? 1 : 0.3 }}>Act II: The Battlefield</span>
                    <span className="w-8 h-px" style={{ backgroundColor: 'var(--border-subtle)' }} />
                    <span style={{ color: act >= 3 ? 'var(--ink-strong)' : 'var(--ink-soft)', opacity: act >= 3 ? 1 : 0.3 }}>Act III: The Tribes</span>
                </div>

                <div className="w-24 text-right text-xs" style={{ color: 'var(--ink-soft)' }}>
                    {act === 1 && "7 mins left"}
                    {act === 2 && "4 mins left"}
                    {act === 3 && "2 mins left"}
                </div>
            </header>

            {/* Main Content */}
            <main className="pt-24 pb-24 px-6">
                <AnimatePresence mode="wait">
                    {act === 1 && (
                        <Act1Mirror key="act1" onComplete={handleAct1Complete} />
                    )}
                    {act === 2 && (
                        <Act2Battlefield
                            key="act2"
                            positioning={onboardingData.positioning}
                            onComplete={handleAct2Complete}
                            onBack={handleAct2Back}
                        />
                    )}
                    {act === 3 && (
                        <Act3Tribes
                            key="act3"
                            positioning={onboardingData.positioning}
                            strategy={onboardingData.strategy}
                            onComplete={handleAct3Complete}
                            onBack={handleAct3Back}
                        />
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
};

export default OnboardingLuxe;
