'use client';

import React from 'react';
import styles from './OnboardingProgress.module.css';

interface Step {
    id: string;
    name: string;
    description: string;
}

interface OnboardingProgressProps {
    steps: readonly Step[];
    currentStep: number;
    onStepClick?: (step: number) => void;
}

export function OnboardingProgress({
    steps,
    currentStep,
    onStepClick,
}: OnboardingProgressProps) {
    const progress = ((currentStep + 1) / steps.length) * 100;

    return (
        <div className={styles.container}>
            {/* Progress bar */}
            <div className={styles.progressBar}>
                <div
                    className={styles.progressFill}
                    style={{ width: `${progress}%` }}
                />
            </div>

            {/* Step indicators */}
            <div className={styles.steps}>
                {steps.map((step, index) => {
                    const isCompleted = index < currentStep;
                    const isCurrent = index === currentStep;
                    const isClickable = index <= currentStep;

                    return (
                        <button
                            key={step.id}
                            className={`${styles.step} ${isCompleted ? styles.completed : ''} ${isCurrent ? styles.current : ''}`}
                            onClick={() => isClickable && onStepClick?.(index)}
                            disabled={!isClickable}
                            type="button"
                        >
                            <span className={styles.stepNumber}>
                                {isCompleted ? (
                                    <CheckIcon />
                                ) : (
                                    index + 1
                                )}
                            </span>
                            <span className={styles.stepName}>{step.name}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

function CheckIcon() {
    return (
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M2 7L5.5 10.5L12 4" />
        </svg>
    );
}
