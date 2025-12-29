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
import styles from './Phase2Wizard.module.css';
import { QuestionInput } from '@/components/onboarding/QuestionInput';
import { ArrowLeft, ArrowRight, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { deriveFromFoundation } from '@/lib/derivation-engine';
import { useIcpStore } from '@/lib/icp-store';
import { Icp } from '@/types/icp-types';
import { toast } from 'sonner';
import gsap from 'gsap';

export function Phase2Wizard() {
  const router = useRouter();
  const [data, setData] = useState<FoundationData>(emptyFoundation);

  // Filter questions for Phase 2 (People)
  const phase2Questions = getSectionQuestions('people');

  const [currentLocalIndex, setCurrentLocalIndex] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>(
    'idle'
  );
  const [isShaking, setIsShaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<string>(
    'Initializing Synthesis...'
  );

  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const questionWrapperRef = useRef<HTMLDivElement>(null);
  const questionNumberRef = useRef<HTMLSpanElement>(null);
  const questionTitleRef = useRef<HTMLHeadingElement>(null);
  const questionHintRef = useRef<HTMLParagraphElement>(null);
  const inputAreaRef = useRef<HTMLDivElement>(null);
  const actionAreaRef = useRef<HTMLDivElement>(null);

  // Current Question Helpers
  const currentQuestion = phase2Questions[currentLocalIndex];

  // Enable ICP processing
  const generateFromFoundation = useIcpStore(
    (state) => state.generateFromFoundation
  );

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
    if (!isLoaded || isProcessing) return;
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
  }, [currentLocalIndex, isLoaded, isProcessing]);

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

  const handleComplete = useCallback(async () => {
    setIsProcessing(true);
    setProcessingStatus('Synthesizing your business DNA...');

    try {
      // Run the derivation engine
      setProcessingStatus('Extracting compact objects...');
      const derived = await deriveFromFoundation(data);

      setProcessingStatus('Generating ICP profiles...');
      await new Promise((r) => setTimeout(r, 1000));

      // Sync generated ICPs to store
      if (derived.icps) {
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
            redFlags: [],
            dealBreakers: [],
            excludedCompanyTypes: [],
            excludedGeographies: [],
            excludedBehaviors: [],
          },
        }));

        useIcpStore.setState({
          icps: convertedIcps,
          activeIcpId:
            convertedIcps.find((i: Icp) => i.priority === 'primary')?.id ||
            convertedIcps[0]?.id ||
            null,
          lastGeneratedAt: new Date().toISOString(),
        });
      }

      // Save completed foundation with derived data
      const completedData = {
        ...data,
        completedAt: new Date().toISOString(),
        derived: derived,
      };
      await saveFoundation(completedData);

      // Directly redirect to Phase 3
      setIsProcessing(false);
      router.push('/foundation/phase3');
    } catch (error) {
      console.error('Derivation error:', error);
      setProcessingStatus('Fallback engine is drafting ICPs...');
      generateFromFoundation(data);
      toast('Synthesis offline', {
        description:
          'Using the local generator until credentials are configured.',
      });
      await new Promise((r) => setTimeout(r, 800));

      // Still save and redirect on error
      const completedData = { ...data, completedAt: new Date().toISOString() };
      await saveFoundation(completedData);
      setIsProcessing(false);
      router.push('/foundation/phase3');
    }
  }, [data, router, generateFromFoundation]);

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
    if (currentLocalIndex < phase2Questions.length - 1) {
      setCurrentLocalIndex((prev) => prev + 1);
    } else {
      if (currentQuestion.required && !hasValue) {
        setIsShaking(true);
        setTimeout(() => setIsShaking(false), 500);
        return;
      }
      // End of Phase 2 -> Processing -> Phase 3
      handleComplete();
    }
  }, [
    currentLocalIndex,
    phase2Questions.length,
    currentQuestion,
    hasValue,
    handleComplete,
  ]);

  const goBack = useCallback(() => {
    if (currentLocalIndex > 0) {
      setCurrentLocalIndex((prev) => prev - 1);
    } else {
      router.push('/foundation/phase1-5');
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

  if (isProcessing) {
    return (
      <div className="min-h-screen bg-black flex flex-col items-center justify-center p-8 text-center">
        <div className="relative mb-12">
          {/* Professional, minimal dual-ring spinner */}
          <div className="absolute inset-0 border-4 border-zinc-800 rounded-full"></div>
          <div className="w-24 h-24 border-4 border-emerald-500 rounded-full animate-spin border-t-transparent border-l-transparent" />
        </div>
        <h2 className="font-display text-3xl text-white mb-4 tracking-tight animate-pulse">
          {processingStatus}
        </h2>
        <p className="text-zinc-500 font-mono text-xs tracking-[0.2em] uppercase opacity-80">
          RaptorFlow Synthesis Engine
        </p>
      </div>
    );
  }

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
            <span className={styles.sectionLabel}>PHASE 2</span>
            <h2 className={styles.sectionTitleMain}>People</h2>
            <p className={styles.sectionDescription}>
              Who uses it, who buys it.
            </p>
          </div>

          <div className={styles.progressSteps}>
            <div className={`${styles.progressStep} ${styles.completed}`}>
              <div className={styles.stepDot} />
              <span className={styles.stepLabel}>Identity</span>
            </div>
            <div className={`${styles.progressStep} ${styles.completed}`}>
              <div className={styles.stepDot} />
              <span className={styles.stepLabel}>Outcomes & Offer</span>
            </div>
            <div className={`${styles.progressStep} ${styles.active}`}>
              <div className={styles.stepDot} />
              <span className={styles.stepLabel}>People</span>
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
                Question {currentLocalIndex + 1} of {phase2Questions.length}
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
