'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
    FoundationData,
    emptyFoundation,
    saveFoundation,
    loadFoundation,
} from '@/lib/foundation';
import {
    QUESTIONS,
    SECTIONS,
    Section,
    getSectionForQuestionIndex,
    isFirstQuestionOfSection,
    getTotalQuestions,
} from '@/lib/questionFlowData';
import styles from './QuestionFlow.module.css';
import { ReviewScreen } from './ReviewScreen';
import { QuestionInput } from './QuestionInput';
import { ArrowRight, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ClarityScore } from './ClarityScore';
import { useIcpStore } from '@/lib/icp-store';

// =====================================
// Types
// =====================================

interface SectionTransitionState {
    isActive: boolean;
    isExiting: boolean;
    section: Section | null;
}

// =====================================
// Main Component
// =====================================

export function QuestionFlowWizard() {
    const router = useRouter();
    const [data, setData] = useState<FoundationData>(emptyFoundation);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isLoaded, setIsLoaded] = useState(false);
    const [showReview, setShowReview] = useState(false);
    const [showWelcome, setShowWelcome] = useState(true);
    const [showCelebration, setShowCelebration] = useState(false);
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
    const [sectionTransition, setSectionTransition] = useState<SectionTransitionState>({
        isActive: false,
        isExiting: false,
        section: null,
    });
    const [isShaking, setIsShaking] = useState(false);

    const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Load saved data on mount
    useEffect(() => {
        const saved = loadFoundation();
        setData(saved);
        const savedStep = saved.currentStep || 0;

        // If already completed, redirect to dashboard
        // User should start fresh or edit from settings if needed
        if (saved.completedAt) {
            router.push('/');
            return;
        }

        // Simple mapping won't work perfectly with conditions, better to just load index if possible
        // For now, robustly default to 0 if mapping fails
        const stepToQuestionMap: Record<number, number> = {
            0: 0, 1: 5, 2: 10, 3: 15, 4: 20, 5: 0,
        };
        // If we saved an exact question index, that would happen here, but we save section index.
        setCurrentIndex(stepToQuestionMap[savedStep] || 0);
        setIsLoaded(true);

        if (saved.business?.name || savedStep > 0) {
            setShowWelcome(false);
        }
    }, [router]);

    const jumpToSection = (sectionId: string) => {
        const idx = QUESTIONS.findIndex(q => q.sectionId === sectionId);
        if (idx >= 0) {
            setCurrentIndex(idx);
            setShowReview(false);
        }
    };

    // Save logic
    useEffect(() => {
        if (isLoaded && !showWelcome) {
            setSaveStatus('saving');
            if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);

            saveTimeoutRef.current = setTimeout(() => {
                const currentSection = getSectionForQuestionIndex(currentIndex);
                const sectionIndex = SECTIONS.findIndex(s => s.id === currentSection?.id);
                saveFoundation({ ...data, currentStep: sectionIndex >= 0 ? sectionIndex : 0 });
                setSaveStatus('saved');
                setTimeout(() => setSaveStatus('idle'), 2000);
            }, 800);
        }
        return () => { if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current); };
    }, [data, currentIndex, isLoaded, showWelcome]);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (showWelcome || sectionTransition.isActive || showCelebration) return;
            if (e.key === 'Escape' && currentIndex > 0) {
                e.preventDefault();
                goBack();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [currentIndex, showWelcome, sectionTransition.isActive, showCelebration]);

    // Data helpers
    const getValue = useCallback((path: string): any => {
        const parts = path.split('.');
        let value: any = data;
        for (const part of parts) { value = value?.[part]; }

        // Handle array fields - return empty array if undefined
        const arrayFields = [
            'revenueModel', 'customerType', 'contextFiles', 'primaryDrivers',
            'buyerRoleChips', 'primaryRegions', 'languages', 'constraints',
            'currentChannels', 'currentTools', 'proofTypes'
        ];
        const fieldName = parts[parts.length - 1];
        if (arrayFields.includes(fieldName) && !value) {
            return [];
        }
        return value ?? '';
    }, [data]);

    const setValue = useCallback((path: string, value: any) => {
        const parts = path.split('.');
        setData(prev => {
            const newData = { ...prev };
            let obj: any = newData;
            for (let i = 0; i < parts.length - 1; i++) {
                obj[parts[i]] = { ...obj[parts[i]] };
                obj = obj[parts[i]];
            }
            obj[parts[parts.length - 1]] = value;
            return newData;
        });
    }, []);

    // Render helpers (Hoisted for dependencies)
    const currentQuestion = QUESTIONS[currentIndex];
    const currentSection = getSectionForQuestionIndex(currentIndex);
    const currentValue = getValue(currentQuestion?.field || '');

    const hasValue = Array.isArray(currentValue)
        ? currentValue.length > 0
        : (typeof currentValue === 'string' ? currentValue.length > 0 : !!currentValue);

    // Navigation Helper: Find next valid question index
    const getNextValidIndex = (startIndex: number, direction: 'forward' | 'backward'): number => {
        let index = startIndex;
        const limit = direction === 'forward' ? QUESTIONS.length : -1;
        const step = direction === 'forward' ? 1 : -1;

        index += step;

        while (index !== limit) {
            const question = QUESTIONS[index];
            if (!question.condition || question.condition(data)) {
                return index;
            }
            index += step;
        }
        return limit; // Indicates end of flow or start
    };

    // Navigation
    const goNext = useCallback(() => {
        const nextIndex = getNextValidIndex(currentIndex, 'forward');

        if (nextIndex < QUESTIONS.length) {
            // Check for section transition
            // We use the raw next index to detect section boundaries
            if (isFirstQuestionOfSection(nextIndex)) {
                const nextSection = getSectionForQuestionIndex(nextIndex);
                if (nextSection && nextSection.id !== 'review') {
                    setSectionTransition({ isActive: true, isExiting: false, section: nextSection });
                    setTimeout(() => {
                        setSectionTransition(prev => ({ ...prev, isExiting: true }));
                        setTimeout(() => {
                            setSectionTransition({ isActive: false, isExiting: false, section: null });
                            setCurrentIndex(nextIndex);
                        }, 500);
                    }, 2000);
                    return;
                }
            }
            setCurrentIndex(nextIndex);
        } else {
            // Blocked?
            const question = QUESTIONS[currentIndex];
            if (question.required && !hasValue) {
                setIsShaking(true);
                setTimeout(() => setIsShaking(false), 500);
                return;
            }
            setShowReview(true);
        }
    }, [currentIndex, data, hasValue]); // Add data dependency for condition checking

    const goBack = useCallback(() => {
        if (showReview) { setShowReview(false); return; }
        const prevIndex = getNextValidIndex(currentIndex, 'backward');
        if (prevIndex >= 0) setCurrentIndex(prevIndex);
    }, [currentIndex, showReview, data]);

    const generateFromFoundation = useIcpStore(state => state.generateFromFoundation);

    const handleComplete = useCallback(() => {
        setShowCelebration(true);

        // Auto-generate ICPs from Foundation data
        generateFromFoundation(data);

        setTimeout(() => {
            const completedData = { ...data, completedAt: new Date().toISOString(), currentStep: SECTIONS.length - 1 };
            saveFoundation(completedData);
            router.push('/');
        }, 3000);
    }, [data, router, generateFromFoundation]);



    // Welcome Screen
    if (showWelcome) {
        return (
            <div className={styles.welcomeContainer}>
                <div className="text-center max-w-[460px]">
                    <div className="text-6xl mb-6">🧱</div>
                    <h1 className="font-serif text-5xl mb-4 text-foreground">Build Your Foundation</h1>
                    <p className="font-sans text-lg text-muted-foreground leading-relaxed mb-10">
                        We're about to build the core operating system for your marketing.
                        Invest 10 minutes now to save 100 hours later.
                    </p>
                    <Button
                        size="lg"
                        className={`${styles.continueBtn} w-full justify-center`}
                        onClick={() => setShowWelcome(false)}
                    >
                        Start Building <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            </div>
        );
    }

    // Celebration Screen
    if (showCelebration) {
        // Robust fallback for business name
        const rawName = data.business?.name;
        const businessName = (rawName && rawName.trim().length > 0) ? rawName : 'Your Business';

        return (
            <div className="min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0f1419] to-[#0a0a0f] flex items-center justify-center relative overflow-hidden">
                {/* Animated stars background */}
                <div className="absolute inset-0">
                    {Array.from({ length: 80 }).map((_, i) => (
                        <div
                            key={i}
                            className="absolute rounded-full bg-white animate-pulse"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                                width: `${1 + Math.random() * 2}px`,
                                height: `${1 + Math.random() * 2}px`,
                                opacity: Math.random() * 0.8,
                                animationDuration: `${2 + Math.random() * 4}s`,
                                animationDelay: `${Math.random() * 2}s`
                            }}
                        />
                    ))}
                </div>

                {/* Glow effect */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse" />
                </div>

                {/* Content card */}
                <div className="relative z-10 max-w-md mx-auto text-center">
                    {/* Rocket icon with glow */}
                    <div className="relative inline-block mb-8">
                        <div className="absolute inset-0 bg-primary/30 rounded-full blur-2xl scale-150" />
                        <div className="relative text-7xl animate-bounce">
                            🚀
                        </div>
                    </div>

                    <h1 className="font-serif text-5xl font-medium text-white mb-4 tracking-tight">
                        Ready for Liftoff
                    </h1>

                    <p className="text-lg text-gray-300 leading-relaxed mb-8 max-w-sm mx-auto">
                        <span className="text-white font-semibold">{businessName}</span> is equipped with a solid marketing foundation.
                    </p>

                    <p className="text-sm text-gray-500 mb-8">
                        Welcome to RaptorFlow.
                    </p>

                    <Button
                        size="lg"
                        onClick={() => router.push('/')}
                        className="bg-white text-black hover:bg-gray-100 font-medium px-8 py-6 text-base rounded-xl shadow-2xl shadow-white/10 transition-all hover:scale-105"
                    >
                        Go to Dashboard <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                </div>
            </div>
        );
    }

    if (!isLoaded) return <div />;

    return (
        <div className={styles.flowContainer}>
            {/* Left Panel: Context & Navigation */}
            <div className={styles.leftPanel}>
                <div className="w-full h-full flex flex-col">
                    <div className={styles.logoArea}>
                        <div className="w-6 h-6 bg-white rounded flex-shrink-0" />
                        <span className={styles.logoText}>RAPTORFLOW</span>
                    </div>

                    <div className={styles.sectionInfo}>
                        <span className={styles.sectionLabel}>Chapter {SECTIONS.findIndex(s => s.id === currentSection?.id) + 1}</span>
                        <h2 className={styles.sectionTitleMain}>{currentSection?.title}</h2>
                        <p className={styles.sectionDescription}>{currentSection?.subtitle}</p>
                    </div>

                    <div className={styles.progressSteps}>
                        {SECTIONS.filter(s => s.id !== 'review').map((section, idx) => {
                            const currentSectionIdx = SECTIONS.findIndex(s => s.id === currentSection?.id);
                            const isActive = idx === currentSectionIdx;
                            const isCompleted = idx < currentSectionIdx;

                            return (
                                <div
                                    key={section.id}
                                    className={`${styles.progressStep} ${isActive ? styles.active : ''} ${isCompleted ? styles.completed : ''} ${(isCompleted || isActive) ? 'cursor-pointer hover:opacity-80' : 'cursor-not-allowed opacity-50'}`}
                                    onClick={() => { if (isCompleted || isActive) jumpToSection(section.id); }}
                                >
                                    <div className={styles.stepDot} />
                                    <span className={styles.stepLabel}>{section.name}</span>
                                </div>
                            );
                        })}
                    </div>

                    <div className={styles.footerMeta}>
                        <div className={styles.saveStatus}>
                            {saveStatus === 'saving' ? (
                                <>
                                    <div className={styles.savingPulse} />
                                    Saving...
                                </>
                            ) : (
                                <span className="text-green-600 font-medium flex items-center animate-in fade-in duration-300">
                                    <ArrowRight className="h-3 w-3 mr-1" /> Saved
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Panel: Content Canvas */}
            <div className={styles.rightPanel}>
                <div className={styles.topNavigation}>
                    <Button variant="outline" size="icon" className="w-10 h-10 rounded-xl" onClick={() => router.push('/')}>
                        <X className="h-5 w-5" />
                    </Button>
                </div>

                <div className={styles.panelContent}>
                    {showReview ? (
                        <ReviewScreen
                            data={data}
                            onBack={() => setShowReview(false)}
                            onComplete={handleComplete}
                            onEditSection={(id: string) => {
                                const idx = QUESTIONS.findIndex(q => q.sectionId === id);
                                if (idx >= 0) { setShowReview(false); setCurrentIndex(idx); }
                            }}
                        />
                    ) : (
                        <div
                            className={`${styles.questionWrapper} ${isShaking ? 'animate-shake' : ''}`}
                            key={currentQuestion.id}
                        >
                            <div className={styles.questionHeader}>
                                <span className={styles.qNumber}>Question {currentIndex + 1} of {getTotalQuestions()}</span>
                                <h2 className={styles.qText}>{currentQuestion.question}</h2>
                                {currentQuestion.hint && <p className={styles.qHint}>{currentQuestion.hint}</p>}
                            </div>

                            <div className={styles.inputArea}>
                                <QuestionInput
                                    question={currentQuestion}
                                    value={currentValue}
                                    onChange={(val) => setValue(currentQuestion.field, val)}
                                    onEnter={goNext}
                                />
                            </div>

                            <div className={styles.actionArea}>
                                <div className={styles.keyboardHint}>
                                    {currentIndex > 0 && (
                                        <Button variant="ghost" onClick={goBack} className="mr-4 px-0 hover:bg-transparent hover:text-foreground">
                                            Back
                                        </Button>
                                    )}
                                    <span className={styles.key}>Enter ↵</span> to continue
                                </div>
                                <div className="flex gap-4 items-center">
                                    {!currentQuestion.required && !hasValue && (
                                        <Button variant="ghost" onClick={goNext}>Skip</Button>
                                    )}
                                    <Button
                                        onClick={goNext}
                                        disabled={currentQuestion.required && !hasValue}
                                        className={styles.continueBtn}
                                    >
                                        {/* Dynamic Label */}
                                        {currentQuestion.type === 'textarea' ? 'Submit' : 'Next'}
                                        <ArrowRight className="ml-2 h-4 w-4" />
                                    </Button>
                                    {!currentQuestion.required && !hasValue ? null : (
                                        <div className={`text-xs text-muted-foreground transition-opacity duration-300 ${!currentQuestion.required || hasValue ? 'opacity-100' : 'opacity-0'}`}>
                                            Press Enter ↵
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}


