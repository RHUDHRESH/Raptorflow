'use client';

import React from 'react';
import { FoundationData, CohortData, CustomerType, SCARFDriver, DecisionStyle, RiskTolerance } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import styles from './Steps.module.css';

interface StepProps {
    data: FoundationData;
    updateData: <K extends keyof FoundationData>(section: K, value: FoundationData[K]) => void;
    onNext: () => void;
    onBack: () => void;
}

const CUSTOMER_TYPES: { value: CustomerType; label: string }[] = [
    { value: 'b2b', label: 'B2B (Businesses)' },
    { value: 'b2c', label: 'B2C (Consumers)' },
    { value: 'b2g', label: 'B2G (Government)' },
    { value: 'mixed', label: 'Mixed' },
];

const SCARF_DRIVERS: { value: SCARFDriver; label: string; description: string }[] = [
    { value: 'status', label: 'Status', description: 'They want to look competent or successful' },
    { value: 'certainty', label: 'Certainty', description: 'They want predictability and guarantees' },
    { value: 'autonomy', label: 'Autonomy', description: 'They want control and freedom to decide' },
    { value: 'relatedness', label: 'Relatedness', description: 'They want to belong to a tribe or community' },
    { value: 'fairness', label: 'Fairness', description: 'They care about transparency and justice' },
];

const DECISION_STYLES: { value: DecisionStyle; label: string; description: string }[] = [
    { value: 'satisficer', label: 'Satisficers', description: 'Quick decision, "good enough" works' },
    { value: 'maximizer', label: 'Maximizers', description: 'Research for days, want the best' },
];

const RISK_TOLERANCES: { value: RiskTolerance; label: string; description: string }[] = [
    { value: 'regret-minimizer', label: 'Regret Minimizers', description: "Don't want to get blamed or look stupid" },
    { value: 'opportunity-seeker', label: 'Opportunity Seekers', description: 'Willing to take risks for upside' },
];

export function StepCohorts({ data, updateData, onNext, onBack }: StepProps) {
    const cohorts = data.cohorts;

    const handleChange = <K extends keyof CohortData>(field: K, value: CohortData[K]) => {
        updateData('cohorts', { ...cohorts, [field]: value });
    };

    const toggleDriver = (driver: SCARFDriver) => {
        const current = cohorts.primaryDrivers;
        if (current.includes(driver)) {
            handleChange('primaryDrivers', current.filter((d) => d !== driver));
        } else if (current.length < 3) {
            handleChange('primaryDrivers', [...current, driver]);
        }
    };

    return (
        <div className={styles.step}>
            <div className={styles.stepHeader}>
                <h2 className={styles.stepTitle}>Who You Serve</h2>
                <p className={styles.stepSubtitle}>
                    Psychological segmentation, not demographics.
                </p>
            </div>

            <div className={styles.form}>
                {/* Customer Type */}
                <div className={styles.field}>
                    <label className={styles.label}>Primary Customer Type</label>
                    <div className={styles.radioGroup}>
                        {CUSTOMER_TYPES.map((type) => (
                            <label key={type.value} className={styles.radioLabel}>
                                <input
                                    type="radio"
                                    name="customerType"
                                    value={type.value}
                                    checked={cohorts.customerType === type.value}
                                    onChange={(e) => handleChange('customerType', e.target.value as CustomerType)}
                                    className={styles.radioInput}
                                />
                                <span className={styles.radioText}>{type.label}</span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Buyer Role */}
                <div className={styles.field}>
                    <label className={styles.label} htmlFor="buyerRole">
                        Who is the actual buyer?
                    </label>
                    <input
                        id="buyerRole"
                        type="text"
                        className={styles.input}
                        value={cohorts.buyerRole}
                        onChange={(e) => handleChange('buyerRole', e.target.value)}
                        placeholder="e.g., Marketing Director, Founder, Head of Ops"
                    />
                </div>

                {/* SCARF Drivers */}
                <div className={styles.field}>
                    <label className={styles.label}>
                        Psychological Drivers (select 2-3)
                    </label>
                    <p className={styles.fieldHint}>What motivates your best customers?</p>
                    <div className={styles.cardGrid}>
                        {SCARF_DRIVERS.map((driver) => {
                            const isSelected = cohorts.primaryDrivers.includes(driver.value);
                            return (
                                <button
                                    key={driver.value}
                                    type="button"
                                    className={`${styles.driverCard} ${isSelected ? styles.selected : ''}`}
                                    onClick={() => toggleDriver(driver.value)}
                                >
                                    <span className={styles.driverLabel}>{driver.label}</span>
                                    <span className={styles.driverDesc}>{driver.description}</span>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Decision Style */}
                <div className={styles.field}>
                    <label className={styles.label}>How do they decide?</label>
                    <div className={styles.choiceCards}>
                        {DECISION_STYLES.map((style) => (
                            <button
                                key={style.value}
                                type="button"
                                className={`${styles.choiceCard} ${cohorts.decisionStyle === style.value ? styles.selected : ''}`}
                                onClick={() => handleChange('decisionStyle', style.value)}
                            >
                                <span className={styles.choiceLabel}>{style.label}</span>
                                <span className={styles.choiceDesc}>{style.description}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Risk Tolerance */}
                <div className={styles.field}>
                    <label className={styles.label}>Risk Tolerance</label>
                    <div className={styles.choiceCards}>
                        {RISK_TOLERANCES.map((risk) => (
                            <button
                                key={risk.value}
                                type="button"
                                className={`${styles.choiceCard} ${cohorts.riskTolerance === risk.value ? styles.selected : ''}`}
                                onClick={() => handleChange('riskTolerance', risk.value)}
                            >
                                <span className={styles.choiceLabel}>{risk.label}</span>
                                <span className={styles.choiceDesc}>{risk.description}</span>
                            </button>
                        ))}
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
