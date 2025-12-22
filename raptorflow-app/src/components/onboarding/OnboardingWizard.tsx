'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
    FoundationData,
    emptyFoundation,
    saveFoundation,
    loadFoundation,
    ONBOARDING_STEPS,
} from '@/lib/foundation';
import { OnboardingProgress } from './OnboardingProgress';
import { StepBusinessBasics } from './steps/StepBusinessBasics';
import { StepConfession } from './steps/StepConfession';
import { StepCohorts } from './steps/StepCohorts';
import { StepPositioning } from './steps/StepPositioning';
import { StepMessaging } from './steps/StepMessaging';
import { StepReview } from './steps/StepReview';
import styles from './OnboardingWizard.module.css';

export function OnboardingWizard() {
    const router = useRouter();
    const [data, setData] = useState<FoundationData>(emptyFoundation);
    const [currentStep, setCurrentStep] = useState(0);
    const [isLoaded, setIsLoaded] = useState(false);

    // Load saved data on mount
    useEffect(() => {
        const saved = loadFoundation();
        setData(saved);
        setCurrentStep(saved.currentStep || 0);
        setIsLoaded(true);
    }, []);

    // Save data whenever it changes
    useEffect(() => {
        if (isLoaded) {
            saveFoundation({ ...data, currentStep });
        }
    }, [data, currentStep, isLoaded]);

    const updateData = useCallback(<K extends keyof FoundationData>(
        section: K,
        value: FoundationData[K]
    ) => {
        setData((prev) => ({ ...prev, [section]: value }));
    }, []);

    const goNext = useCallback(() => {
        if (currentStep < ONBOARDING_STEPS.length - 1) {
            setCurrentStep((prev) => prev + 1);
        }
    }, [currentStep]);

    const goBack = useCallback(() => {
        if (currentStep > 0) {
            setCurrentStep((prev) => prev - 1);
        }
    }, [currentStep]);

    const goToStep = useCallback((step: number) => {
        if (step >= 0 && step < ONBOARDING_STEPS.length) {
            setCurrentStep(step);
        }
    }, []);

    const handleComplete = useCallback(() => {
        const completedData = {
            ...data,
            completedAt: new Date().toISOString(),
            currentStep: ONBOARDING_STEPS.length - 1,
        };
        saveFoundation(completedData);
        router.push('/');
    }, [data, router]);

    if (!isLoaded) {
        return (
            <div className={styles.loading}>
                <span>Loading...</span>
            </div>
        );
    }

    const renderStep = () => {
        const stepProps = {
            data,
            updateData,
            onNext: goNext,
            onBack: goBack,
        };

        switch (currentStep) {
            case 0:
                return <StepBusinessBasics {...stepProps} />;
            case 1:
                return <StepConfession {...stepProps} />;
            case 2:
                return <StepCohorts {...stepProps} />;
            case 3:
                return <StepPositioning {...stepProps} />;
            case 4:
                return <StepMessaging {...stepProps} />;
            case 5:
                return (
                    <StepReview
                        data={data}
                        updateData={updateData}
                        onBack={goBack}
                        onComplete={handleComplete}
                        goToStep={goToStep}
                    />
                );
            default:
                return null;
        }
    };

    return (
        <div className={styles.wizard}>
            <header className={styles.header}>
                <h1 className={styles.title}>Foundation</h1>
                <p className={styles.subtitle}>
                    Build your marketing foundation in 6 steps
                </p>
            </header>

            <OnboardingProgress
                steps={ONBOARDING_STEPS}
                currentStep={currentStep}
                onStepClick={goToStep}
            />

            <main className={styles.content}>
                {renderStep()}
            </main>
        </div>
    );
}
