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

    return (
        <div className="min-h-screen bg-white text-neutral-900 font-sans selection:bg-neutral-900 selection:text-white">
            {/* Header */}
            <header className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-md border-b border-neutral-100 z-50 flex items-center justify-between px-6 lg:px-12">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-neutral-900 rounded-full flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-bold tracking-widest uppercase text-sm">RaptorFlow</span>
                </div>

                {/* Progress */}
                <div className="flex items-center gap-4 text-xs font-bold uppercase tracking-widest">
                    <span className={act >= 1 ? "text-neutral-900" : "text-neutral-300"}>Act I: The Mirror</span>
                    <span className="w-8 h-px bg-neutral-200" />
                    <span className={act >= 2 ? "text-neutral-900" : "text-neutral-300"}>Act II: The Battlefield</span>
                    <span className="w-8 h-px bg-neutral-200" />
                    <span className={act >= 3 ? "text-neutral-900" : "text-neutral-300"}>Act III: The Tribes</span>
                </div>

                <div className="w-24 text-right text-xs text-neutral-400">
                    {act === 1 && "7 mins left"}
                    {act === 2 && "4 mins left"}
                    {act === 3 && "2 mins left"}
                </div>
            </header>

            {/* Main Content */}
            <main className="pt-32 pb-24 px-6">
                <AnimatePresence mode="wait">
                    {act === 1 && (
                        <Act1Mirror key="act1" onComplete={handleAct1Complete} />
                    )}
                    {act === 2 && (
                        <Act2Battlefield
                            key="act2"
                            positioning={onboardingData.positioning}
                            onComplete={handleAct2Complete}
                        />
                    )}
                    {act === 3 && (
                        <Act3Tribes
                            key="act3"
                            positioning={onboardingData.positioning}
                            strategy={onboardingData.strategy}
                            onComplete={handleAct3Complete}
                        />
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
};

export default OnboardingLuxe;
