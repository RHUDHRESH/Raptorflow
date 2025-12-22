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
    Question,
    Section,
    getSectionForQuestionIndex,
    isFirstQuestionOfSection,
    getTotalQuestions,
} from '@/lib/questionFlowData';
import styles from './QuestionFlow.module.css';

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

    const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Load saved data on mount
    useEffect(() => {
        const saved = loadFoundation();
        setData(saved);
        const savedStep = saved.currentStep || 0;
        const stepToQuestionMap: Record<number, number> = {
            0: 0, 1: 5, 2: 10, 3: 15, 4: 20, 5: 0,
        };
        setCurrentIndex(stepToQuestionMap[savedStep] || 0);
        setIsLoaded(true);

        if (saved.business?.name || savedStep > 0) {
            setShowWelcome(false);
        }
    }, []);

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
    const getValue = useCallback((path: string): string | string[] => {
        const parts = path.split('.');
        let value: unknown = data;
        for (const part of parts) { value = (value as Record<string, unknown>)?.[part]; }
        if (Array.isArray(value)) return value;
        return (value as string) || '';
    }, [data]);

    const setValue = useCallback((path: string, value: string | string[]) => {
        const parts = path.split('.');
        setData(prev => {
            const newData = { ...prev };
            let obj: Record<string, unknown> = newData;
            for (let i = 0; i < parts.length - 1; i++) {
                obj[parts[i]] = { ...(obj[parts[i]] as Record<string, unknown>) };
                obj = obj[parts[i]] as Record<string, unknown>;
            }
            obj[parts[parts.length - 1]] = value;
            return newData as FoundationData;
        });
    }, []);

    // Navigation
    const goNext = useCallback(() => {
        if (currentIndex < QUESTIONS.length - 1) {
            const nextIndex = currentIndex + 1;

            // Check for section transition
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
            setShowReview(true);
        }
    }, [currentIndex]);

    const goBack = useCallback(() => {
        if (showReview) { setShowReview(false); return; }
        if (currentIndex > 0) setCurrentIndex(prev => prev - 1);
    }, [currentIndex, showReview]);

    const handleComplete = useCallback(() => {
        setShowCelebration(true);
        setTimeout(() => {
            const completedData = { ...data, completedAt: new Date().toISOString(), currentStep: SECTIONS.length - 1 };
            saveFoundation(completedData);
            router.push('/');
        }, 3000);
    }, [data, router]);

    // Render helpers
    const currentQuestion = QUESTIONS[currentIndex];
    const currentSection = getSectionForQuestionIndex(currentIndex);
    const currentValue = getValue(currentQuestion?.field || '');
    const hasValue = Array.isArray(currentValue) ? currentValue.length > 0 : currentValue.length > 0;

    // Welcome Screen
    if (showWelcome) {
        return (
            <div className={styles.welcomeContainer}>
                <div style={{ textAlign: 'center', maxWidth: 460 }}>
                    <div style={{ fontSize: 64, marginBottom: 24 }}>🧱</div>
                    <h1 style={{ fontFamily: 'Playfair Display', fontSize: 48, marginBottom: 16 }}>Build Your Foundation</h1>
                    <p style={{ fontFamily: 'Inter', fontSize: 18, color: '#5B5F61', lineHeight: 1.6, marginBottom: 40 }}>
                        We're about to build the core operating system for your marketing.
                        Invest 10 minutes now to save 100 hours later.
                    </p>
                    <button className={styles.continueBtn} style={{ width: '100%', justifyContent: 'center' }} onClick={() => setShowWelcome(false)}>
                        Start Building <ArrowIcon />
                    </button>
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
            <div className={styles.celebrationContainer}>
                {/* Confetti particles */}
                {Array.from({ length: 50 }).map((_, i) => (
                    <div
                        key={i}
                        className={styles.confetti}
                        style={{
                            left: `${Math.random() * 100}%`,
                            animationDuration: `${2 + Math.random() * 3}s`,
                            animationDelay: `${Math.random() * 2}s`
                        }}
                    />
                ))}

                <div className={styles.content}>
                    <div className={styles.launchIcon}>🚀</div>
                    <h1 className={styles.launchTitle}>Ready for Liftoff</h1>
                    <p className={styles.launchText}>
                        <strong>{businessName}</strong> is equipped with a solid marketing foundation.<br />
                        Welcome to RaptorFlow.
                    </p>
                    <button className={styles.launchButton} onClick={() => router.push('/')}>
                        Go to Dashboard <ArrowIcon />
                    </button>
                </div>
            </div>
        );
    }

    if (!isLoaded) return <div />;

    return (
        <div className={styles.flowContainer}>
            {/* Left Panel: Context & Navigation */}
            <div className={styles.leftPanel}>
                <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <div className={styles.logoArea}>
                        <div style={{ width: 24, height: 24, background: 'white', borderRadius: 4 }} />
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
                                <div key={section.id} className={`${styles.progressStep} ${isActive ? styles.active : ''} ${isCompleted ? styles.completed : ''}`}>
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
                                <span style={{ opacity: 0.6 }}>Changes saved</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Panel: Content Canvas */}
            <div className={styles.rightPanel}>
                <div className={styles.topNavigation}>
                    <button className={styles.navAction} onClick={() => router.push('/')}>
                        <CloseIcon />
                    </button>
                </div>

                <div className={styles.panelContent}>
                    {showReview ? (
                        <ReviewScreen
                            data={data}
                            onBack={() => setShowReview(false)}
                            onComplete={handleComplete}
                            onEditSection={(id) => {
                                const idx = QUESTIONS.findIndex(q => q.sectionId === id);
                                if (idx >= 0) { setShowReview(false); setCurrentIndex(idx); }
                            }}
                        />
                    ) : (
                        <div className={styles.questionWrapper} key={currentQuestion.id}>
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
                                        <button className={styles.skipButton} onClick={goBack} style={{ marginRight: 16, padding: 0 }}>
                                            Back
                                        </button>
                                    )}
                                    <span className={styles.key}>Enter ↵</span> to continue
                                </div>
                                <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                                    {!currentQuestion.required && !hasValue && (
                                        <button className={styles.skipButton} onClick={goNext}>Skip</button>
                                    )}
                                    <button
                                        className={styles.continueBtn}
                                        onClick={goNext}
                                        disabled={currentQuestion.required && !hasValue}
                                    >
                                        {/* Dynamic Label */}
                                        {currentQuestion.type === 'textarea' ? 'Submit' : 'Next'}
                                        <ArrowIcon />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// =====================================
// Inputs & Subcomponents
// =====================================

function QuestionInput({ question, value, onChange, onEnter }: { question: Question, value: any, onChange: (v: any) => void, onEnter: () => void }) {
    const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);
    useEffect(() => { setTimeout(() => inputRef.current?.focus(), 150); }, [question.id]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey && question.type !== 'textarea') {
            e.preventDefault();
            onEnter();
        }
    };

    switch (question.type) {
        case 'text':
            return <input ref={inputRef as any} className={styles.textInput} value={value} onChange={e => onChange(e.target.value)} onKeyDown={handleKeyDown} placeholder={question.placeholder} />;
        case 'text-large':
            return <input ref={inputRef as any} className={styles.textInputLarge} value={value} onChange={e => onChange(e.target.value)} onKeyDown={handleKeyDown} placeholder={question.placeholder} />;
        case 'textarea':
            return (
                <div style={{ position: 'relative' }}>
                    <textarea ref={inputRef as any} className={styles.textareaInput} value={value} onChange={e => onChange(e.target.value)} placeholder={question.placeholder} />
                    <span style={{ position: 'absolute', bottom: 16, right: 16, fontSize: 11, color: '#9CA3AF' }}>{(value || '').length} chars</span>
                </div>
            );
        case 'radio-cards':
            const optionCount = question.options?.length || 0;
            let gridClass = styles.radioCardsGrid;
            if (optionCount === 4) gridClass = styles.gridFour;
            if (optionCount >= 5) gridClass = styles.gridFive;

            return (
                <div className={gridClass}>
                    {question.options?.map(opt => (
                        <div key={opt.value} className={`${styles.cardBase} ${value === opt.value ? styles.selected : ''}`} onClick={() => { onChange(opt.value); setTimeout(onEnter, 300); }}>
                            <span className={styles.cardTitle}>{opt.label}</span>
                            {opt.description && <span className={styles.cardDesc}>{opt.description}</span>}
                            <div className={styles.checkmark}><CheckIcon /></div>
                        </div>
                    ))}
                </div>
            );
        case 'choice-cards':
            const cOptionCount = question.options?.length || 0;
            let cGridClass = styles.choiceCardsGrid;
            if (cOptionCount === 4) cGridClass = styles.gridFour;
            if (cOptionCount >= 5) cGridClass = styles.gridFive;

            return (
                <div className={cGridClass}>
                    {question.options?.map(opt => (
                        <div key={opt.value} className={`${styles.cardBase} ${value === opt.value ? styles.selected : ''}`} onClick={() => { onChange(opt.value); setTimeout(onEnter, 300); }}>
                            <div className={styles.checkmark}><CheckIcon /></div>
                            <span className={styles.choiceCardLabel} style={{ fontSize: 18, fontWeight: 600, display: 'block', marginBottom: 8 }}>{opt.label}</span>
                            <span className={styles.cardDesc}>{opt.description}</span>
                        </div>
                    ))}
                </div>
            );
        case 'multi-select':
            const vals = Array.isArray(value) ? value : [];
            const msOptionCount = question.options?.length || 0;
            let msGridClass = styles.multiSelectGrid;
            if (msOptionCount === 4) msGridClass = styles.gridFour;
            if (msOptionCount >= 5) msGridClass = styles.gridFive;

            return (
                <div className={msGridClass}>
                    {question.options?.map(opt => {
                        const isSel = vals.includes(opt.value);
                        return (
                            <div key={opt.value} className={`${styles.cardBase} ${isSel ? styles.selected : ''}`} onClick={() => {
                                const newVals = isSel ? vals.filter(v => v !== opt.value) : [...vals, opt.value];
                                onChange(newVals);
                            }}>
                                <div className={styles.checkmark}><CheckIcon /></div>
                                <span className={styles.cardTitle}>{opt.label}</span>
                                {opt.description && <span className={styles.cardDesc}>{opt.description}</span>}
                            </div>
                        );
                    })}
                </div>
            );
        default: return null;
    }
}

function ReviewScreen({ data, onBack, onComplete, onEditSection }: any) {
    // Simplified Review Screen for the Split Layout - kept clean
    return (
        <div style={{ width: '100%' }}>
            <div style={{ marginBottom: 40, borderBottom: '1px solid #E5E6E3', paddingBottom: 24 }}>
                <h1 style={{ fontFamily: 'Playfair Display', fontSize: 40, marginBottom: 8 }}>Review Foundation</h1>
                <p style={{ fontFamily: 'Inter', color: '#5B5F61' }}>Verify your answers before building the core.</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                {['business', 'cohorts', 'positioning', 'messaging'].map(sec => (
                    <div key={sec} style={{ background: 'white', border: '1px solid #E5E6E3', borderRadius: 12, overflow: 'hidden' }}>
                        <div style={{ padding: '16px 24px', background: '#FAFBF9', borderBottom: '1px solid #E5E6E3', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: 600, textTransform: 'uppercase', fontSize: 12, letterSpacing: '0.05em' }}>{sec}</span>
                            <button onClick={() => onEditSection(sec)} style={{ fontSize: 12, textDecoration: 'underline', border: 'none', background: 'none', cursor: 'pointer' }}>Edit</button>
                        </div>
                        <div style={{ padding: 24 }}>
                            {/* Data dump simplified for layout demo */}
                            <div style={{ fontSize: 14, color: '#2D3538' }}>{sec === 'business' ? data.business.name : 'Completed'}</div>
                        </div>
                    </div>
                ))}
            </div>

            <div style={{ marginTop: 48, display: 'flex', gap: 16 }}>
                <button className={styles.continueBtn} onClick={onComplete} style={{ flex: 1, justifyContent: 'center' }}>
                    Confirm & Launch <ArrowIcon />
                </button>
            </div>
        </div>
    );
}

// Icons
const ArrowIcon = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 8h10m0 0L9 4m4 4l-4 4" /></svg>;
const CheckIcon = () => <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2"><path d="M2 6l3 3 5-5" /></svg>;
const CloseIcon = () => <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 6l8 8m0-8l-8 8" /></svg>;

