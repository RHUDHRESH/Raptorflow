'use client';

import React from 'react';
import { FoundationData, MessagingData } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import styles from './Steps.module.css';

interface StepProps {
    data: FoundationData;
    updateData: <K extends keyof FoundationData>(section: K, value: FoundationData[K]) => void;
    onNext: () => void;
    onBack: () => void;
}

const HEURISTIC_EXAMPLES = [
    '"No one ever got fired for buying IBM"',
    '"Just do it"',
    '"Because you\'re worth it"',
    '"Have it your way"',
    '"Good things come to those who wait"',
];

export function StepMessaging({ data, updateData, onNext, onBack }: StepProps) {
    const messaging = data.messaging;

    const handleChange = (field: keyof MessagingData, value: string) => {
        updateData('messaging', { ...messaging, [field]: value });
    };

    return (
        <div className={styles.step}>
            <div className={styles.stepHeader}>
                <h2 className={styles.stepTitle}>How You Speak</h2>
                <p className={styles.stepSubtitle}>
                    Create heuristics—mental shortcuts that shut down objections.
                </p>
            </div>

            <div className={styles.form}>
                {/* Primary Heuristic */}
                <div className={styles.field}>
                    <label className={styles.label} htmlFor="heuristic">
                        Your Primary Heuristic
                    </label>
                    <p className={styles.fieldHint}>
                        A 3-6 word phrase that removes fear, grants permission, and shuts down debate.
                    </p>
                    <input
                        id="heuristic"
                        type="text"
                        className={styles.inputLarge}
                        value={messaging.primaryHeuristic}
                        onChange={(e) => handleChange('primaryHeuristic', e.target.value)}
                        placeholder="e.g., Marketing. Finally under control."
                    />
                    <div className={styles.exampleList}>
                        <span className={styles.exampleLabel}>Examples:</span>
                        {HEURISTIC_EXAMPLES.map((ex, i) => (
                            <span key={i} className={styles.example}>{ex}</span>
                        ))}
                    </div>
                </div>

                {/* Three Pillars */}
                <div className={styles.pillarsSection}>
                    <label className={styles.label}>Three Messaging Pillars</label>

                    <div className={styles.pillarCard}>
                        <span className={styles.pillarLabel}>The Belief</span>
                        <span className={styles.pillarPrefix}>We believe...</span>
                        <textarea
                            className={styles.pillarInput}
                            value={messaging.beliefPillar}
                            onChange={(e) => handleChange('beliefPillar', e.target.value)}
                            placeholder="What do you fundamentally believe that others don't?"
                            rows={2}
                        />
                    </div>

                    <div className={styles.pillarCard}>
                        <span className={styles.pillarLabel}>The Promise</span>
                        <span className={styles.pillarPrefix}>We promise...</span>
                        <textarea
                            className={styles.pillarInput}
                            value={messaging.promisePillar}
                            onChange={(e) => handleChange('promisePillar', e.target.value)}
                            placeholder="What transformation do you guarantee?"
                            rows={2}
                        />
                    </div>

                    <div className={styles.pillarCard}>
                        <span className={styles.pillarLabel}>The Proof</span>
                        <span className={styles.pillarPrefix}>Here&apos;s evidence...</span>
                        <textarea
                            className={styles.pillarInput}
                            value={messaging.proofPillar}
                            onChange={(e) => handleChange('proofPillar', e.target.value)}
                            placeholder="What proves your belief and promise are true?"
                            rows={2}
                        />
                    </div>
                </div>
            </div>

            <div className={styles.actions}>
                <Button variant="secondary" onClick={onBack}>
                    <BackIcon />
                    Back
                </Button>
                <Button variant="default" onClick={onNext}>
                    Continue
                    <ArrowIcon />
                </Button>
            </div>
        </div>
    );
}

function ArrowIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M3 8H13M13 8L9 4M13 8L9 12" />
        </svg>
    );
}

function BackIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M13 8H3M3 8L7 4M3 8L7 12" />
        </svg>
    );
}
