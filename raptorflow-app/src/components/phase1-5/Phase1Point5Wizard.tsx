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
import { getSectionQuestions, Question } from '@/lib/questionFlowData';
import styles from './Phase1Point5Wizard.module.css';
import { QuestionInput } from '@/components/onboarding/QuestionInput';
import { ArrowLeft, ArrowRight, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import gsap from 'gsap';

export function Phase1Point5Wizard() {
  const router = useRouter();
  const [data, setData] = useState<FoundationData>(emptyFoundation);

  // Filter questions for Phase 1.5 (Outcomes and Offer)
  const outcomesQuestions = getSectionQuestions('outcomes');
  const offerQuestions = getSectionQuestions('offer');
  const phase1Point5Questions: Question[] = [
    ...outcomesQuestions,
    ...offerQuestions,
  ];

  const [currentLocalIndex, setCurrentLocalIndex] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>(
    'idle'
  );
  const [isShaking, setIsShaking] = useState(false);

  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const questionWrapperRef = useRef<HTMLDivElement>(null);
  const questionNumberRef = useRef<HTMLSpanElement>(null);
  const questionTitleRef = useRef<HTMLHeadingElement>(null);
  const questionHintRef = useRef<HTMLParagraphElement>(null);
  const inputAreaRef = useRef<HTMLDivElement>(null);
  const actionAreaRef = useRef<HTMLDivElement>(null);

  // Current Question Helpers
  const currentQuestion = phase1Point5Questions[currentLocalIndex];
  // Simple section detection
  const currentSectionName = outcomesQuestions.find(
    (q) => q.id === currentQuestion?.id
  )
    ? 'Outcomes'
    : 'Offer';

  // Load saved data on mount
  useEffect(() => {
    const fetchInitialData = async () => {
      const saved = await loadFoundationDB();
      setData(saved);
      setIsLoaded(true);
    };
    fetchInitialData();
  }, []);

  // GSAP Animation
  useEffect(() => {
    if (!isLoaded) return;
    if (!questionWrapperRef.current) return;

    const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

    gsap.set(
      [
        questionNumberRef.current,
        questionTitleRef.current,
        questionHintRef.current,
        inputAreaRef.current,
        actionAreaRef.current,
      ],
      {
        opacity: 0,
        y: 30,
      }
    );

    tl.to(questionNumberRef.current, { opacity: 1, y: 0, duration: 0.4 }, 0)
      .to(questionTitleRef.current, { opacity: 1, y: 0, duration: 0.5 }, 0.1)
      .to(questionHintRef.current, { opacity: 1, y: 0, duration: 0.4 }, 0.2)
      .to(inputAreaRef.current, { opacity: 1, y: 0, duration: 0.5 }, 0.3)
      .to(actionAreaRef.current, { opacity: 1, y: 0, duration: 0.4 }, 0.5);

    return () => {
      tl.kill();
    };
  }, [currentLocalIndex, isLoaded]);

  // Save logic
  useEffect(() => {
    if (isLoaded) {
      setSaveStatus('saving');
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);

      saveTimeoutRef.current = setTimeout(() => {
        saveFoundation({ ...data });
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 2000);
      }, 800);
    }
    return () => {
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    };
  }, [data, isLoaded]);

  // Data helpers
  const getValue = useCallback(
    (path: string): any => {
      const parts = path.split('.');
      let value: any = data;
      for (const part of parts) {
        value = value?.[part];
      }
      return value ?? '';
    },
    [data]
  );

  const setValue = useCallback((path: string, value: any) => {
    const parts = path.split('.');
    setData((prev) => {
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
  const hasValue = Array.isArray(currentValue)
    ? currentValue.length > 0
    : typeof currentValue === 'string'
      ? currentValue.length > 0
      : !!currentValue;

  const goNext = useCallback(() => {
    if (currentLocalIndex < phase1Point5Questions.length - 1) {
      setCurrentLocalIndex((prev) => prev + 1);
    } else {
      if (currentQuestion.required && !hasValue) {
        setIsShaking(true);
        setTimeout(() => setIsShaking(false), 500);
        return;
      }
      router.push('/foundation/phase2');
    }
  }, [
    currentLocalIndex,
    phase1Point5Questions.length,
    router,
    currentQuestion,
    hasValue,
  ]);

  const goBack = useCallback(() => {
    if (currentLocalIndex > 0) {
      setCurrentLocalIndex((prev) => prev - 1);
    } else {
      router.push('/foundation/phase1');
    }
  }, [currentLocalIndex, router]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        goBack();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goBack]);

  if (!isLoaded) return <div />;

  return (
    <div className={styles.flowContainer}>
      {/* Left Panel */}
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
            <span className={styles.sectionLabel}>PHASE 1.5</span>
            <h2 className={styles.sectionTitleMain}>{currentSectionName}</h2>
            <p className={styles.sectionDescription}>
              Defining what you sell and why it matters.
            </p>
          </div>

          <div className={styles.progressSteps}>
            <div className={`${styles.progressStep} ${styles.completed}`}>
              <div className={styles.stepDot} />
              <span className={styles.stepLabel}>Identity</span>
            </div>
            <div className={`${styles.progressStep} ${styles.active}`}>
              <div className={styles.stepDot} />
              <span className={styles.stepLabel}>Outcomes & Offer</span>
            </div>
            <div className={`${styles.progressStep}`}>
              <div className={styles.stepDot} />
              <span className={styles.stepLabel}>People (Next)</span>
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

      {/* Right Panel */}
      <div className={styles.rightPanel}>
        <div className={styles.topNavigation}>
          <Button
            variant="outline"
            size="icon"
            className="w-10 h-10 rounded-xl"
            onClick={() => router.push('/')}
          >
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
              <span ref={questionNumberRef} className={styles.qNumber}>
                Question {currentLocalIndex + 1} of{' '}
                {phase1Point5Questions.length}
              </span>
              <h2 ref={questionTitleRef} className={styles.qText}>
                {currentQuestion.question}
              </h2>
              {currentQuestion.hint && (
                <p ref={questionHintRef} className={styles.qHint}>
                  {currentQuestion.hint}
                </p>
              )}
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
                <Button
                  variant="ghost"
                  onClick={goBack}
                  className="mr-4 px-0 hover:bg-transparent hover:text-foreground"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" /> Back
                </Button>
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
