'use client';

import React from 'react';
import { FoundationData } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import styles from './Steps.module.css';

interface StepReviewProps {
    data: FoundationData;
    updateData: <K extends keyof FoundationData>(section: K, value: FoundationData[K]) => void;
    onBack: () => void;
    onComplete: () => void;
    goToStep: (step: number) => void;
}

export function StepReview({ data, onBack, onComplete, goToStep }: StepReviewProps) {
    const { business, confession, cohorts, positioning, messaging } = data;

    const positioningStatement = positioning.category && positioning.targetAudience && positioning.psychologicalOutcome
        ? `We are the ${positioning.category} for ${positioning.targetAudience} who want ${positioning.psychologicalOutcome}.`
        : 'Not yet defined';

    const driverLabels: Record<string, string> = {
        status: 'Status',
        certainty: 'Certainty',
        autonomy: 'Autonomy',
        relatedness: 'Relatedness',
        fairness: 'Fairness',
    };

    return (
        <div className={styles.step}>
            <div className={styles.stepHeader}>
                <h2 className={styles.stepTitle}>Your Foundation</h2>
                <p className={styles.stepSubtitle}>
                    Review and launch your marketing foundation.
                </p>
            </div>

            <div className={styles.reviewSections}>
                {/* Business */}
                <div className={styles.reviewSection}>
                    <div className={styles.reviewHeader}>
                        <h3 className={styles.reviewTitle}>Business</h3>
                        <button
                            type="button"
                            className={styles.editButton}
                            onClick={() => goToStep(0)}
                        >
                            Edit
                        </button>
                    </div>
                    <div className={styles.reviewContent}>
                        <div className={styles.reviewItem}>
                            <span className={styles.reviewLabel}>Name</span>
                            <span className={styles.reviewValue}>{business.name || '—'}</span>
                        </div>
                        <div className={styles.reviewItem}>
                            <span className={styles.reviewLabel}>Industry</span>
                            <span className={styles.reviewValue}>{business.industry || '—'}</span>
                        </div>
                        <div className={styles.reviewItem}>
                            <span className={styles.reviewLabel}>Stage</span>
                            <span className={styles.reviewValue}>{business.stage}</span>
                        </div>
                    </div>
                </div>

                {/* Cohorts */}
                <div className={styles.reviewSection}>
                    <div className={styles.reviewHeader}>
                        <h3 className={styles.reviewTitle}>Cohorts</h3>
                        <button
                            type="button"
                            className={styles.editButton}
                            onClick={() => goToStep(2)}
                        >
                            Edit
                        </button>
                    </div>
                    <div className={styles.reviewContent}>
                        <div className={styles.reviewItem}>
                            <span className={styles.reviewLabel}>Customer Type</span>
                            <span className={styles.reviewValue}>
                                {Array.isArray(cohorts.customerType)
                                    ? cohorts.customerType.map(t => t.toUpperCase()).join(', ')
                                    : (cohorts.customerType ? cohorts.customerType.toUpperCase() : '—')
                                }
                            </span>
                        </div>
                        <div className={styles.reviewItem}>
                            <span className={styles.reviewLabel}>Buyer</span>
                            <span className={styles.reviewValue}>{cohorts.buyerRole || '—'}</span>
                        </div>
                        <div className={styles.reviewItem}>
                            <span className={styles.reviewLabel}>Drivers</span>
                            <span className={styles.reviewValue}>
                                {cohorts.primaryDrivers.map(d => driverLabels[d]).join(', ') || '—'}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Positioning */}
                <div className={styles.reviewSection}>
                    <div className={styles.reviewHeader}>
                        <h3 className={styles.reviewTitle}>Positioning</h3>
                        <button
                            type="button"
                            className={styles.editButton}
                            onClick={() => goToStep(3)}
                        >
                            Edit
                        </button>
                    </div>
                    <div className={styles.reviewContent}>
                        <p className={styles.positioningPreview}>{positioningStatement}</p>
                        {positioning.ownedPosition && (
                            <div className={styles.reviewItem}>
                                <span className={styles.reviewLabel}>Owned Position</span>
                                <span className={styles.reviewValue}>{positioning.ownedPosition}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Messaging */}
                <div className={styles.reviewSection}>
                    <div className={styles.reviewHeader}>
                        <h3 className={styles.reviewTitle}>Messaging</h3>
                        <button
                            type="button"
                            className={styles.editButton}
                            onClick={() => goToStep(4)}
                        >
                            Edit
                        </button>
                    </div>
                    <div className={styles.reviewContent}>
                        {messaging.primaryHeuristic && (
                            <p className={styles.heuristicPreview}>
                                &ldquo;{messaging.primaryHeuristic}&rdquo;
                            </p>
                        )}
                        {messaging.beliefPillar && (
                            <div className={styles.reviewItem}>
                                <span className={styles.reviewLabel}>Belief</span>
                                <span className={styles.reviewValue}>{messaging.beliefPillar}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Confession Highlights */}
                {(confession.expensiveProblem || confession.embarrassingTruth) && (
                    <div className={styles.reviewSection}>
                        <div className={styles.reviewHeader}>
                            <h3 className={styles.reviewTitle}>Confession Highlights</h3>
                            <button
                                type="button"
                                className={styles.editButton}
                                onClick={() => goToStep(1)}
                            >
                                Edit
                            </button>
                        </div>
                        <div className={styles.reviewContent}>
                            {confession.expensiveProblem && (
                                <p className={styles.confessionPreview}>
                                    {confession.expensiveProblem.slice(0, 150)}
                                    {confession.expensiveProblem.length > 150 ? '...' : ''}
                                </p>
                            )}
                        </div>
                    </div>
                )}
            </div>

            <div className={styles.actions}>
                <Button variant="secondary" onClick={onBack}>
                    <BackIcon />
                    Back
                </Button>
                <Button variant="default" onClick={onComplete}>
                    Launch Foundation
                    <RocketIcon />
                </Button>
            </div>
        </div>
    );
}

function BackIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M13 8H3M3 8L7 4M3 8L7 12" />
        </svg>
    );
}

function RocketIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M14 2L7 9M14 2L10 14L7 9M14 2L2 6L7 9" />
        </svg>
    );
}
