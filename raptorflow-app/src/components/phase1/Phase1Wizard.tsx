'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
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
    getSectionQuestions,
} from '@/lib/questionFlowData';
import styles from './Phase1Wizard.module.css';
import { QuestionInput } from '@/components/onboarding/QuestionInput';
import { WelcomeScreen } from '@/components/onboarding/WelcomeScreen'; // Reuse welcome screen
import { ArrowRight, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import gsap from 'gsap';

export function Phase1Wizard() {
    const router = useRouter();
    const [data, setData] = useState<FoundationData>(emptyFoundation);

    // Filter questions for Phase 1 (Warm Up)
    const phase1Questions = getSectionQuestions('warm-up');

    const [currentLocalIndex, setCurrentLocalIndex] = useState(0);
    const [isLoaded, setIsLoaded] = useState(false);
    const [showWelcome, setShowWelcome] = useState(true);
    const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');
    const [isShaking, setIsShaking] = useState(false);

    const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const questionWrapperRef = useRef<HTMLDivElement>(null);
    const questionNumberRef = useRef<HTMLSpanElement>(null);
    const questionTitleRef = useRef<HTMLHeadingElement>(null);
    const questionHintRef = useRef<HTMLParagraphElement>(null);
    const inputAreaRef = useRef<HTMLDivElement>(null);
    const actionAreaRef = useRef<HTMLDivElement>(null);

    // Current Question Helpers
    const currentQuestion = phase1Questions[currentLocalIndex];
    const currentSection = SECTIONS.find(s => s.id === 'warm-up');

    // Load saved data on mount
    useEffect(() => {
        const fetchInitialData = async () => {
            const saved = await loadFoundationDB();
            setData(saved);

            // Map saved full index to local index if user was returning?
            // Simplified: Start at 0 unless we want complex restoration logic.
            // If completed, maybe redirect?
            // For now, let's just load data.
            setIsLoaded(true);

            if (saved.business?.name) {
                setShowWelcome(false);
            }
        };
        fetchInitialData();
    }, []);

    // GSAP Animation for question transitions
    useEffect(() => {
        if (!isLoaded || showWelcome) return;
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
    }, [currentLocalIndex, isLoaded, showWelcome]);

    // Save logic
    useEffect(() => {
        if (isLoaded && !showWelcome) {
            setSaveStatus('saving');
            if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);

            saveTimeoutRef.current = setTimeout(() => {
                // Map local index to something global if needed, or just save data
                saveFoundation({ ...data });
                setSaveStatus('saved');
                setTimeout(() => setSaveStatus('idle'), 2000);
            }, 800);
        }
        return () => { if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current); };
    }, [data, isLoaded, showWelcome]);

    // Data helpers
    const getValue = useCallback((path: string): any => {
        const parts = path.split('.');
        let value: any = data;
        for (const part of parts) { value = value?.[part]; }
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

    const currentValue = getValue(currentQuestion?.field || '');
    const hasValue = (typeof currentValue === 'string' ? currentValue.length > 0 : !!currentValue);

    const goNext = useCallback(() => {
        if (currentLocalIndex < phase1Questions.length - 1) {
            setCurrentLocalIndex(prev => prev + 1);
        } else {
            // End of Phase 1
            // Ensure required fields
            if (currentQuestion.required && !hasValue) {
                setIsShaking(true);
                setTimeout(() => setIsShaking(false), 500);
                return;
            }
            // Navigate to Phase 1.5
            router.push('/foundation/phase1-5');
        }
    }, [currentLocalIndex, phase1Questions.length, router, currentQuestion, hasValue]);

    const goBack = useCallback(() => {
        if (currentLocalIndex > 0) {
            setCurrentLocalIndex(prev => prev - 1);
        }
    }, [currentLocalIndex]);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (showWelcome) return;
            if (e.key === 'Escape' && currentLocalIndex > 0) {
                e.preventDefault();
                goBack();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [currentLocalIndex, showWelcome, goBack]);


    if (showWelcome) {
        return <WelcomeScreen onStart={() => setShowWelcome(false)} />;
    }

    if (!isLoaded) return <div />;

    return (
        <div className={styles.flowContainer}>
            {/* Left Panel: Context & Navigation */}
            <div className={styles.leftPanel}>
                <div className="w-full h-full flex flex-col">
                    <div className={styles.logoArea}>
                        <div className="relative w-8 h-8 rounded overflow-hidden">
                            <Image
                                src="/logo_primary.png"
                                alt="RaptorFlow"
                                fill
                                className="object-cover"
                            />
                        </div>
                    </div>

                    <div className={styles.sectionInfo}>
                        <span className={styles.sectionLabel}>PHASE 1</span>
                        <h2 className={styles.sectionTitleMain}>{currentSection?.title || 'Warm Up'}</h2>
                        <p className={styles.sectionDescription}>{currentSection?.subtitle || 'Let\'s get started.'}</p>
                    </div>

                    {/* Simplified Progress for Phase 1 */}
                    <div className={styles.progressSteps}>
                        <div className={`${styles.progressStep} ${styles.active}`}>
                            <div className={styles.stepDot} />
                            <span className={styles.stepLabel}>Identity</span>
                        </div>
                        <div className={`${styles.progressStep}`}>
                            <div className={styles.stepDot} />
                            <span className={styles.stepLabel}>Outcomes (Next)</span>
                        </div>
                        <div className={`${styles.progressStep}`}>
                            <div className={styles.stepDot} />
                            <span className={styles.stepLabel}>People (Later)</span>
                        </div>
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
                    <div
                        ref={questionWrapperRef}
                        className={`${styles.questionWrapper} ${isShaking ? 'animate-shake' : ''}`}
                        key={currentQuestion.id}
                    >
                        <div className={styles.questionHeader}>
                            <span ref={questionNumberRef} className={styles.qNumber}>Question {currentLocalIndex + 1} of {phase1Questions.length}</span>
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
                                {currentLocalIndex > 0 && (
                                    <Button variant="ghost" onClick={goBack} className="mr-4 px-0 hover:bg-transparent hover:text-foreground">
                                        Back
                                    </Button>
                                )}
                                <span className={styles.key}>Enter ↵</span> to continue
                            </div>
                            <div className="flex gap-4 items-center">
                                <Button
                                    onClick={goNext}
                                    disabled={currentQuestion.required && !hasValue}
                                    className={styles.continueBtn}
                                >
                                    {currentQuestion.type === 'textarea' ? 'Submit' : 'Next'}
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
