'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
    FoundationData,
    emptyFoundation,
    saveFoundation,
    loadFoundationDB,
} from '@/lib/foundation';
import {
    QUESTIONS,
    SECTIONS,
    Section,
    getSectionForQuestionIndex,
    isFirstQuestionOfSection,
    getTotalQuestions,
} from '@/lib/questionFlowData';
import { triggerAgenticSynthesis } from '@/lib/icp-generator';
import { deriveFromFoundation } from '@/lib/derivation-engine';
import { DerivedData } from '@/lib/foundation';
import styles from './QuestionFlow.module.css';
import { ReviewScreen } from './ReviewScreen';
import { QuestionInput } from './QuestionInput';
import { WelcomeScreen } from './WelcomeScreen';
import { ICPRevealScreen } from './ICPRevealScreen';
import { PositioningRevealScreen } from './PositioningRevealScreen';
import { CompetitorsRevealScreen } from './CompetitorsRevealScreen';
import { MessagingRevealScreen } from './MessagingRevealScreen';
import { MarketRevealScreen } from './MarketRevealScreen';
import { ArrowRight, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ClarityScore } from './ClarityScore';
import { useIcpStore } from '@/lib/icp-store';
import { Icp } from '@/types/icp-types';
import { toast } from 'sonner';
import gsap from 'gsap';

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
    const [isProcessing, setIsProcessing] = useState(false);
    const [processingStatus, setProcessingStatus] = useState<string>('Initializing Synthesis...');
    const [revealStage, setRevealStage] = useState<'none' | 'icps' | 'positioning' | 'competitors' | 'messaging' | 'market'>('none');
    const [derivedData, setDerivedData] = useState<DerivedData | null>(null);

    const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const questionWrapperRef = useRef<HTMLDivElement>(null);
    const questionNumberRef = useRef<HTMLSpanElement>(null);
    const questionTitleRef = useRef<HTMLHeadingElement>(null);
    const questionHintRef = useRef<HTMLParagraphElement>(null);
    const inputAreaRef = useRef<HTMLDivElement>(null);
    const actionAreaRef = useRef<HTMLDivElement>(null);

    // GSAP Animation for question transitions
    useEffect(() => {
        if (!isLoaded || showWelcome || showCelebration || showReview || isProcessing) return;
        if (!questionWrapperRef.current) return;

        const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

        // Set initial states
        gsap.set([questionNumberRef.current, questionTitleRef.current, questionHintRef.current, inputAreaRef.current, actionAreaRef.current], {
            opacity: 0,
            y: 30,
        });

        // Stagger reveal
        tl.to(questionNumberRef.current, { opacity: 1, y: 0, duration: 0.4 }, 0)
            .to(questionTitleRef.current, { opacity: 1, y: 0, duration: 0.5 }, 0.1)
            .to(questionHintRef.current, { opacity: 1, y: 0, duration: 0.4 }, 0.2)
            .to(inputAreaRef.current, { opacity: 1, y: 0, duration: 0.5 }, 0.3)
            .to(actionAreaRef.current, { opacity: 1, y: 0, duration: 0.4 }, 0.5);

        return () => { tl.kill(); };
    }, [currentIndex, isLoaded, showWelcome, showCelebration, showReview, isProcessing]);

    // Load saved data on mount
    useEffect(() => {
        const fetchInitialData = async () => {
            const saved = await loadFoundationDB();
            setData(saved);
            const savedStep = saved.currentStep || 0;

            const isCompleted = Boolean(saved.completedAt);
            if (isCompleted) {
                // Foundation already completed - redirect to Phase 3
                router.push('/foundation/phase3');
                return;
            }

            const stepToQuestionMap: Record<number, number> = {
                0: 0, 1: 5, 2: 10, 3: 15, 4: 20, 5: 0,
            };
            setCurrentIndex(stepToQuestionMap[savedStep] || 0);
            setIsLoaded(true);

            if (saved.business?.name || savedStep > 0 || isCompleted) {
                setShowWelcome(false);
            }
        };
        fetchInitialData();
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
        const step = direction === 'forward' ? 1 : -1;

        index += step;

        while (index >= 0 && index < QUESTIONS.length) {
            const question = QUESTIONS[index];
            if (!question.condition || question.condition(data)) {
                return index;
            }
            index += step;
        }

        // If going forward and no more valid questions, return QUESTIONS.length to trigger completion
        if (direction === 'forward') {
            return QUESTIONS.length;
        }

        // If going backward and no valid question, stay at current
        return startIndex;
    };

    const generateFromFoundation = useIcpStore(state => state.generateFromFoundation);

    const handleComplete = useCallback(async () => {
        setIsProcessing(true);
        setProcessingStatus('Synthesizing your business DNA...');

        try {
            // Run the derivation engine
            setProcessingStatus('Extracting compact objects...');
            const derived = await deriveFromFoundation(data);
            setDerivedData(derived);

            setProcessingStatus('Generating ICP profiles...');
            await new Promise(r => setTimeout(r, 1000));

            // Sync generated ICPs to store
            if (derived.icps) {
                // Convert DerivedICP to Icp format
                const convertedIcps: Icp[] = derived.icps.map((derivedIcp: any) => ({
                    id: derivedIcp.id,
                    workspaceId: 'default',
                    name: derivedIcp.name,
                    priority: derivedIcp.priority as 'primary' | 'secondary',
                    status: 'active' as const,
                    confidenceScore: derivedIcp.confidence || 0.8,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                    firmographics: {
                        companyType: [],
                        geography: [],
                        salesMotion: [],
                        budgetComfort: [],
                        decisionMaker: []
                    },
                    painMap: {
                        primaryPains: [],
                        secondaryPains: [],
                        triggerEvents: [],
                        urgencyLevel: 'soon'
                    },
                    psycholinguistics: {
                        mindsetTraits: [],
                        emotionalTriggers: [],
                        tonePreference: [],
                        wordsToUse: [],
                        wordsToAvoid: [],
                        proofPreference: [],
                        ctaStyle: []
                    },
                    disqualifiers: {
                        redFlags: [],
                        dealBreakers: [],
                        excludedCompanyTypes: [],
                        excludedGeographies: [],
                        excludedBehaviors: []
                    }
                }));

                useIcpStore.setState({
                    icps: convertedIcps,
                    activeIcpId: convertedIcps.find((i: Icp) => i.priority === 'primary')?.id || convertedIcps[0]?.id || null,
                    lastGeneratedAt: new Date().toISOString()
                });
            }

            // Save completed foundation with derived data
            const completedData = {
                ...data,
                completedAt: new Date().toISOString(),
                currentStep: SECTIONS.length - 1,
                derived: derived
            };
            await saveFoundation(completedData);

            // Show reveal screens instead of redirecting
            setIsProcessing(false);
            setRevealStage('icps');

        } catch (error) {
            console.error('Derivation error:', error);
            setProcessingStatus('Fallback engine is drafting ICPs...');
            generateFromFoundation(data);
            toast('Synthesis offline', {
                description: 'Using the local generator until credentials are configured.'
            });
            await new Promise(r => setTimeout(r, 800));

            // Still save and redirect on error
            const completedData = { ...data, completedAt: new Date().toISOString(), currentStep: SECTIONS.length - 1 };
            await saveFoundation(completedData);
            setIsProcessing(false);
            router.push('/foundation/phase3');
        }
    }, [data, router, generateFromFoundation]);

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
            // End of questions - go directly to Phase 3 (skip Review screen)
            const question = QUESTIONS[currentIndex];
            if (question.required && !hasValue) {
                setIsShaking(true);
                setTimeout(() => setIsShaking(false), 500);
                return;
            }
            // Skip review, directly complete and process
            handleComplete();
        }
    }, [currentIndex, data, hasValue, handleComplete]); // Add handleComplete dependency

    const goBack = useCallback(() => {
        if (showReview) { setShowReview(false); return; }
        const prevIndex = getNextValidIndex(currentIndex, 'backward');
        if (prevIndex >= 0) setCurrentIndex(prevIndex);
    }, [currentIndex, showReview, data]);


    // Reveal stage handlers
    const handleRevealContinue = () => {
        switch (revealStage) {
            case 'icps': setRevealStage('positioning'); break;
            case 'positioning': setRevealStage('competitors'); break;
            case 'competitors': setRevealStage('messaging'); break;
            case 'messaging': setRevealStage('market'); break;
            case 'market':
                toast.success('Phase 1 Complete!', {
                    description: 'Now let\'s build your differentiation blueprint.'
                });
                router.push('/foundation/phase3');
                break;
        }
    };



    // Welcome Screen - Premium Cinematic Experience
    if (showWelcome) {
        return <WelcomeScreen onStart={() => setShowWelcome(false)} />;
    }

    // Celebration Screen - Understated Elegance
    if (showCelebration) {
        const rawName = data.business?.name;
        const businessName = (rawName && rawName.trim().length > 0) ? rawName : 'Your Business';

        return (
            <div className="fixed inset-0 bg-[#0E1112] z-50 flex items-center justify-center overflow-hidden">
                {/* Subtle ambient glow */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="w-[800px] h-[800px] bg-white/[0.015] rounded-full blur-[120px]" />
                </div>

                {/* Content */}
                <div className="relative z-10 max-w-[600px] text-center px-8">
                    {/* Minimal success indicator */}
                    <div className="inline-flex items-center gap-2 mb-12 opacity-50">
                        <div className="w-2 h-2 bg-white rounded-full" />
                        <span className="text-[11px] font-mono uppercase tracking-[0.2em] text-white/60">
                            Foundation Complete
                        </span>
                    </div>

                    {/* Typography-focused headline */}
                    <h1 className="font-serif text-[56px] leading-[1.1] text-white tracking-[-0.03em] mb-6">
                        {businessName}
                        <span className="block text-white/40 mt-2">is ready.</span>
                    </h1>

                    {/* Subtle description */}
                    <p className="text-[18px] text-white/40 leading-relaxed mb-16 max-w-[400px] mx-auto">
                        Your marketing foundation will now power everything — positioning, ICPs, messaging, and campaigns.
                    </p>

                    {/* Stats row */}
                    <div className="flex items-center justify-center gap-12 mb-16 text-white/30">
                        <div className="text-center">
                            <span className="block font-serif text-[28px] text-white/70">{data.business?.industry || '—'}</span>
                            <span className="text-[11px] font-mono uppercase tracking-wider">Industry</span>
                        </div>
                        <div className="w-px h-10 bg-white/10" />
                        <div className="text-center">
                            <span className="block font-serif text-[28px] text-white/70">{data.business?.stage || '—'}</span>
                            <span className="text-[11px] font-mono uppercase tracking-wider">Stage</span>
                        </div>
                    </div>

                    {/* Premium CTA */}
                    <button
                        onClick={() => router.push('/foundation/phase3')}
                        className="group inline-flex items-center gap-4 bg-white text-[#0E1112] px-12 py-5 rounded-2xl font-medium text-[16px] transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_60px_rgba(255,255,255,0.15)]"
                    >
                        <span>Continue to Phase 3</span>
                        <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                    </button>
                </div>
            </div>
        );
    }

    if (!isLoaded) return <div />;

    if (isProcessing) {
        return (
            <div className="min-h-screen bg-black flex flex-col items-center justify-center p-8 text-center">
                <div className="relative mb-12">
                    <div className="w-32 h-32 border-4 border-emerald-500/20 rounded-full animate-spin border-t-emerald-500" />
                    <div className="absolute inset-0 flex items-center justify-center text-4xl">
                        {processingStatus.includes('Architect') ? '📐' : processingStatus.includes('Prophet') ? '🔮' : '⚔️'}
                    </div>
                </div>
                <h2 className="font-display text-4xl text-white mb-4 animate-pulse">
                    {processingStatus}
                </h2>
                <p className="text-zinc-500 font-mono text-sm tracking-widest uppercase">
                    RaptorFlow Synthesis Engine v2.0
                </p>
                <div className="mt-12 max-w-xs w-full bg-zinc-900 h-1.5 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-emerald-500 transition-all duration-1000"
                        style={{
                            width: processingStatus.includes('Architect') ? '33%' : processingStatus.includes('Prophet') ? '66%' : '90%'
                        }}
                    />
                </div>
            </div>
        );
    }

    // Reveal Screens (Sequential: ICPs → Positioning → Competitors → Messaging → Market)
    if (revealStage !== 'none' && derivedData) {
        switch (revealStage) {
            case 'icps':
                if (derivedData.icps) {
                    return <ICPRevealScreen icps={derivedData.icps} onContinue={handleRevealContinue} />;
                }
                break;
            case 'positioning':
                if (derivedData.positioning) {
                    return <PositioningRevealScreen positioning={derivedData.positioning} onContinue={handleRevealContinue} />;
                }
                break;
            case 'competitors':
                if (derivedData.competitive) {
                    return <CompetitorsRevealScreen competitive={derivedData.competitive} onContinue={handleRevealContinue} />;
                }
                break;
            case 'messaging':
                if (derivedData.soundbites) {
                    return <MessagingRevealScreen soundbites={derivedData.soundbites} onContinue={handleRevealContinue} />;
                }
                break;
            case 'market':
                if (derivedData.market) {
                    return <MarketRevealScreen market={derivedData.market} onComplete={handleRevealContinue} />;
                }
                break;
        }
    }

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
                            ref={questionWrapperRef}
                            className={`${styles.questionWrapper} ${isShaking ? 'animate-shake' : ''}`}
                            key={currentQuestion.id}
                        >
                            <div className={styles.questionHeader}>
                                <span ref={questionNumberRef} className={styles.qNumber}>Question {currentIndex + 1} of {getTotalQuestions()}</span>
                                <h2 ref={questionTitleRef} className={styles.qText}>{currentQuestion.question}</h2>
                                {currentQuestion.hint && <p ref={questionHintRef} className={styles.qHint}>{currentQuestion.hint}</p>}
                            </div>

                            <div ref={inputAreaRef} className={styles.inputArea}>
                                <QuestionInput
                                    question={currentQuestion}
                                    value={currentValue}
                                    onChange={(val) => setValue(currentQuestion.field, val)}
                                    onEnter={goNext}
                                />
                            </div>

                            <div ref={actionAreaRef} className={styles.actionArea}>
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
                                        <Button
                                            variant="ghost"
                                            onClick={() => {
                                                toast('No problem! We\'ll make our best guess.', {
                                                    description: 'You can refine this later in Settings.',
                                                    duration: 3000,
                                                });
                                                goNext();
                                            }}
                                        >
                                            Skip
                                        </Button>
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
