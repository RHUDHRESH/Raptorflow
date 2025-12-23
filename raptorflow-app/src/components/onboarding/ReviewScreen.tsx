import React from 'react';
import { FoundationData } from '@/lib/foundation';
import { SECTIONS, QUESTIONS } from '@/lib/questionFlowData';
import styles from './QuestionFlow.module.css';
import { ArrowRight, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { generateFoundationPDF } from '@/lib/pdfGenerator';

interface ReviewScreenProps {
    data: FoundationData;
    onBack: () => void;
    onComplete: () => void;
    onEditSection: (id: string) => void;
}

export function ReviewScreen({ data, onBack, onComplete, onEditSection }: ReviewScreenProps) {
    const renderSectionSummary = (sectionId: string) => {
        switch (sectionId) {
            case 'business':
                return (
                    <div className={styles.reviewGrid}>
                        <ReviewItem label="Business Name" value={data.business.name} />
                        <ReviewItem label="Industry" value={data.business.industry} />
                        <ReviewItem label="Stage" value={data.business.stage} />
                        <ReviewItem label="Revenue Model" value={Array.isArray(data.business.revenueModel) ? data.business.revenueModel.join(', ') : data.business.revenueModel} />
                        <ReviewItem label="Team Size" value={data.business.teamSize} />
                        <ReviewItem label="Context Files" value={data.business.contextFiles ? `${data.business.contextFiles.length} files attached` : 'None'} />
                    </div>
                );
            case 'confession':
                return (
                    <div className={styles.reviewStack}>
                        <ReviewItem label="Expensive Problem" value={data.confession?.expensiveProblem} fullWidth />
                        <ReviewItem label="Embarrassing Truth" value={data.confession?.embarrassingTruth} fullWidth />
                        <ReviewItem label="Stupid Idea" value={data.confession?.stupidIdea} fullWidth />
                        <ReviewItem label="Signaling" value={data.confession?.signaling} fullWidth />
                        <ReviewItem label="Friction" value={data.confession?.friction} fullWidth />
                    </div>
                );
            case 'cohorts':
                return (
                    <div className={styles.reviewGrid}>
                        <ReviewItem label="Customer Type" value={Array.isArray(data.cohorts?.customerType) ? data.cohorts?.customerType.join(', ') : data.cohorts?.customerType} />
                        <ReviewItem label="Buyer Role" value={data.cohorts?.buyerRole} />
                        <ReviewItem label="Primary Drivers" value={data.cohorts?.primaryDrivers?.join(', ')} fullWidth />
                        <ReviewItem label="Decision Style" value={data.cohorts?.decisionStyle} />
                        <ReviewItem label="Risk Tolerance" value={data.cohorts?.riskTolerance} />
                    </div>
                );
            case 'positioning':
                return (
                    <div className={styles.reviewStack}>
                        <div className={styles.positioningStatement}>
                            We are the <strong>{data.positioning?.category || '_____'}</strong> for <strong>{data.positioning?.targetAudience || '_____'}</strong> who want <strong>{data.positioning?.psychologicalOutcome || '_____'}</strong>.
                        </div>
                        <ReviewItem label="Owned Position" value={data.positioning?.ownedPosition} fullWidth />
                        <ReviewItem label="Reframed Weakness" value={data.positioning?.reframedWeakness} fullWidth />
                    </div>
                );
            case 'messaging':
                return (
                    <div className={styles.reviewStack}>
                        <ReviewItem label="Primary Heuristic" value={data.messaging?.primaryHeuristic} highlight />
                        <ReviewItem label="Belief Pillar" value={data.messaging?.beliefPillar} fullWidth />
                        <ReviewItem label="Promise Pillar" value={data.messaging?.promisePillar} fullWidth />
                        <ReviewItem label="Proof Pillar" value={data.messaging?.proofPillar} fullWidth />
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className={styles.reviewContainer}>
            <div className={styles.reviewHeader}>
                <h1 className={styles.reviewTitle}>Foundation Review</h1>
                <p className={styles.reviewSubtitle}>
                    Before we launch, verify the core DNA of your strategy.
                    <br />Construction is easy. Demolition is expensive. Measure twice.
                </p>
            </div>

            <div className={styles.reviewSections}>
                {SECTIONS.filter(s => s.id !== 'review').map((section) => (
                    <div key={section.id} className={styles.reviewSectionCard}>
                        <div className={styles.reviewSectionHeader}>
                            <h3 className={styles.reviewSectionTitle}>{section.name}</h3>
                            <button
                                onClick={() => onEditSection(section.id)}
                                className={styles.editButton}
                            >
                                Edit
                            </button>
                        </div>
                        <div className={styles.reviewSectionContent}>
                            {renderSectionSummary(section.id)}
                        </div>
                    </div>
                ))}
            </div>

            <div className={styles.reviewActions}>
                <Button variant="outline" onClick={onBack} className={styles.backButton}>
                    Back
                </Button>
                <div className="flex gap-3">
                    <Button
                        variant="outline"
                        onClick={() => generateFoundationPDF(data)}
                        className="gap-2"
                    >
                        <Download className="h-4 w-4" /> Download Blueprint
                    </Button>
                    <Button
                        onClick={onComplete}
                        className={`${styles.continueBtn} min-w-[200px]`}
                    >
                        Confirm & Launch <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
}

function ReviewItem({ label, value, fullWidth = false, highlight = false }: { label: string, value?: string | string[], fullWidth?: boolean, highlight?: boolean }) {
    if (!value || (Array.isArray(value) && value.length === 0)) return null;

    return (
        <div className={`${styles.reviewItem} ${fullWidth ? styles.fullWidth : ''} ${highlight ? styles.highlight : ''}`}>
            <span className={styles.reviewLabel}>{label}</span>
            <p className={styles.reviewValue}>{value}</p>
        </div>
    );
}
