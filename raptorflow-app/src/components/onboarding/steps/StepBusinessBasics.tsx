'use client';

import React from 'react';
import { FoundationData, BusinessBasics, BusinessStage, RevenueModel, TeamSize } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import styles from './Steps.module.css';

interface StepProps {
    data: FoundationData;
    updateData: <K extends keyof FoundationData>(section: K, value: FoundationData[K]) => void;
    onNext: () => void;
    onBack: () => void;
}

const STAGES: { value: BusinessStage; label: string }[] = [
    { value: 'idea', label: 'Idea Stage' },
    { value: 'early', label: 'Early (Pre-revenue or <$100k ARR)' },
    { value: 'growth', label: 'Growth ($100k - $1M ARR)' },
    { value: 'scaling', label: 'Scaling ($1M+ ARR)' },
];

const REVENUE_MODELS: { value: RevenueModel; label: string }[] = [
    { value: 'saas', label: 'SaaS / Subscriptions' },
    { value: 'services', label: 'Services / Consulting' },
    { value: 'product', label: 'Physical Products' },
    { value: 'marketplace', label: 'Marketplace / Platform' },
    { value: 'other', label: 'Other' },
];

const TEAM_SIZES: { value: TeamSize; label: string }[] = [
    { value: 'solo', label: 'Solo Founder' },
    { value: '2-5', label: '2-5 people' },
    { value: '6-20', label: '6-20 people' },
    { value: '20+', label: '20+ people' },
];

export function StepBusinessBasics({ data, updateData, onNext }: StepProps) {
    const business = data.business;

    const handleChange = (field: keyof BusinessBasics, value: string) => {
        updateData('business', { ...business, [field]: value });
    };

    const isValid = business.name.trim().length > 0;

    return (
        <div className={styles.step}>
            <div className={styles.stepHeader}>
                <h2 className={styles.stepTitle}>Tell us about your business</h2>
                <p className={styles.stepSubtitle}>
                    We&apos;ll use this to tailor your marketing foundation.
                </p>
            </div>

            <div className={styles.form}>
                {/* Business Name */}
                <div className={styles.field}>
                    <label className={styles.label} htmlFor="businessName">
                        Business Name
                    </label>
                    <input
                        id="businessName"
                        type="text"
                        className={styles.input}
                        value={business.name}
                        onChange={(e) => handleChange('name', e.target.value)}
                        placeholder="Acme Corp"
                    />
                </div>

                {/* Industry */}
                <div className={styles.field}>
                    <label className={styles.label} htmlFor="industry">
                        Industry / Category
                    </label>
                    <input
                        id="industry"
                        type="text"
                        className={styles.input}
                        value={business.industry}
                        onChange={(e) => handleChange('industry', e.target.value)}
                        placeholder="e.g., Marketing Tech, Healthcare, Fintech"
                    />
                </div>

                {/* Business Stage */}
                <div className={styles.field}>
                    <label className={styles.label}>Stage</label>
                    <div className={styles.radioGroup}>
                        {STAGES.map((stage) => (
                            <label key={stage.value} className={styles.radioLabel}>
                                <input
                                    type="radio"
                                    name="stage"
                                    value={stage.value}
                                    checked={business.stage === stage.value}
                                    onChange={(e) => handleChange('stage', e.target.value)}
                                    className={styles.radioInput}
                                />
                                <span className={styles.radioText}>{stage.label}</span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Revenue Model */}
                <div className={styles.field}>
                    <label className={styles.label}>Revenue Model</label>
                    <div className={styles.radioGroup}>
                        {REVENUE_MODELS.map((model) => (
                            <label key={model.value} className={styles.radioLabel}>
                                <input
                                    type="radio"
                                    name="revenueModel"
                                    value={model.value}
                                    checked={business.revenueModel === model.value}
                                    onChange={(e) => handleChange('revenueModel', e.target.value)}
                                    className={styles.radioInput}
                                />
                                <span className={styles.radioText}>{model.label}</span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Team Size */}
                <div className={styles.field}>
                    <label className={styles.label}>Team Size</label>
                    <div className={styles.radioGroup}>
                        {TEAM_SIZES.map((size) => (
                            <label key={size.value} className={styles.radioLabel}>
                                <input
                                    type="radio"
                                    name="teamSize"
                                    value={size.value}
                                    checked={business.teamSize === size.value}
                                    onChange={(e) => handleChange('teamSize', e.target.value)}
                                    className={styles.radioInput}
                                />
                                <span className={styles.radioText}>{size.label}</span>
                            </label>
                        ))}
                    </div>
                </div>
            </div>

            <div className={styles.actions}>
                <div /> {/* Spacer */}
                <Button variant="default" onClick={onNext} disabled={!isValid}>
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
