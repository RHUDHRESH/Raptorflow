'use client';

import React from 'react';
import { FoundationData, PositioningData } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import styles from './Steps.module.css';

interface StepProps {
    data: FoundationData;
    updateData: <K extends keyof FoundationData>(section: K, value: FoundationData[K]) => void;
    onNext: () => void;
    onBack: () => void;
}

const REFRAME_OPTIONS = [
    { value: 'slow-crafted', label: 'Slow → Crafted / Premium', weakness: 'slow', strength: 'crafted' },
    { value: 'expensive-serious', label: 'Expensive → Serious / Committed', weakness: 'expensive', strength: 'serious' },
    { value: 'new-unburdened', label: 'New → Unburdened by legacy', weakness: 'new', strength: 'unburdened' },
    { value: 'complex-powerful', label: 'Complex → Powerful', weakness: 'complex', strength: 'powerful' },
    { value: 'niche-specialized', label: 'Niche → For those who know', weakness: 'niche', strength: 'specialized' },
    { value: 'custom', label: 'Custom reframe...', weakness: '', strength: '' },
];

export function StepPositioning({ data, updateData, onNext, onBack }: StepProps) {
    const positioning = data.positioning;

    const handleChange = (field: keyof PositioningData, value: string) => {
        updateData('positioning', { ...positioning, [field]: value });
    };

    // Pre-fill target audience from cohorts if available
    const suggestedAudience = data.cohorts.buyerRole || '';

    return (
        <div className={styles.step}>
            <div className={styles.stepHeader}>
                <h2 className={styles.stepTitle}>What You Own</h2>
                <p className={styles.stepSubtitle}>
                    Define your Unique Perceived Value—change the frame, change the value.
                </p>
            </div>

            <div className={styles.form}>
                {/* Positioning Statement Builder */}
                <div className={styles.positioningBuilder}>
                    <p className={styles.builderLabel}>Complete this positioning statement:</p>
                    <div className={styles.builderFlow}>
                        <span className={styles.builderText}>We are the</span>
                        <input
                            type="text"
                            className={styles.inlineInput}
                            value={positioning.category}
                            onChange={(e) => handleChange('category', e.target.value)}
                            placeholder="category"
                        />
                        <span className={styles.builderText}>for</span>
                        <input
                            type="text"
                            className={styles.inlineInput}
                            value={positioning.targetAudience || suggestedAudience}
                            onChange={(e) => handleChange('targetAudience', e.target.value)}
                            placeholder="who"
                        />
                        <span className={styles.builderText}>who want</span>
                        <input
                            type="text"
                            className={styles.inlineInput}
                            value={positioning.psychologicalOutcome}
                            onChange={(e) => handleChange('psychologicalOutcome', e.target.value)}
                            placeholder="psychological outcome"
                        />
                    </div>
                </div>

                {/* Owned Position */}
                <div className={styles.field}>
                    <label className={styles.label} htmlFor="ownedPosition">
                        What&apos;s one thing you could own completely that no one else is claiming?
                    </label>
                    <textarea
                        id="ownedPosition"
                        className={styles.textarea}
                        value={positioning.ownedPosition}
                        onChange={(e) => handleChange('ownedPosition', e.target.value)}
                        placeholder="The specific territory, belief, or approach you can exclusively own..."
                        rows={3}
                    />
                </div>

                {/* Reframe Weakness */}
                <div className={styles.field}>
                    <label className={styles.label}>
                        What weakness could you reframe as a strength?
                    </label>
                    <p className={styles.fieldHint}>
                        Guinness reframed &quot;slow pour&quot; as &quot;good things come to those who wait.&quot;
                    </p>
                    <div className={styles.reframeGrid}>
                        {REFRAME_OPTIONS.map((option) => (
                            <button
                                key={option.value}
                                type="button"
                                className={`${styles.reframeCard} ${positioning.reframedWeakness === option.value ? styles.selected : ''}`}
                                onClick={() => handleChange('reframedWeakness', option.value)}
                            >
                                {option.label}
                            </button>
                        ))}
                    </div>
                    {positioning.reframedWeakness === 'custom' && (
                        <input
                            type="text"
                            className={styles.input}
                            placeholder="My weakness → My strength"
                            style={{ marginTop: 'var(--space-md)' }}
                        />
                    )}
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
