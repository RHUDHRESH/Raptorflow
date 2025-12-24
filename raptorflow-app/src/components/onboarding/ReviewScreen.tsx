import React from 'react';
import { FoundationData } from '@/lib/foundation';
import { SECTIONS } from '@/lib/questionFlowData';
import styles from './QuestionFlow.module.css';
import { ArrowRight, Download, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { generateFoundationPDF } from '@/lib/pdfGenerator';
import { FounderQuote } from './FounderQuote';
import { FirstMoveTeaser } from './FirstMoveTeaser';
import { BrandAura } from './BrandAura';
import { PitchScript } from './PitchScript';
import { ClarityScore } from './ClarityScore';

interface ReviewScreenProps {
    data: FoundationData;
    onBack: () => void;
    onComplete: () => void;
    onEditSection: (id: string) => void;
}

// Helper to format arrays nicely
function formatList(arr?: string[] | string): string {
    if (!arr) return '—';
    if (Array.isArray(arr)) {
        if (arr.length === 0) return '—';
        return arr.map(v => v.charAt(0).toUpperCase() + v.slice(1).replace(/-/g, ' ')).join(', ');
    }
    return arr.charAt(0).toUpperCase() + arr.slice(1).replace(/-/g, ' ');
}

// Helper to format single values
function formatValue(val?: string): string {
    if (!val) return '—';
    return val.charAt(0).toUpperCase() + val.slice(1).replace(/-/g, ' ');
}

export function ReviewScreen({ data, onBack, onComplete, onEditSection }: ReviewScreenProps) {
    const renderSectionSummary = (sectionId: string) => {
        switch (sectionId) {
            case 'know-you':
                return (
                    <div className={styles.reviewStack}>
                        {/* Business Link */}
                        {data.business?.websiteUrl && (
                            <div className={`${styles.reviewItem} ${styles.fullWidth}`}>
                                <span className={styles.reviewLabel}>Website / Link</span>
                                <a
                                    href={data.business.websiteUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-primary hover:underline flex items-center gap-2"
                                >
                                    {data.business.websiteUrl}
                                    <ExternalLink className="h-3 w-3" />
                                </a>
                            </div>
                        )}

                        <div className={styles.reviewGrid}>
                            <ReviewItem label="Business Type" value={formatValue(data.business?.businessType)} />
                            <ReviewItem label="Industry" value={data.business?.industry} />
                            <ReviewItem label="Stage" value={formatValue(data.business?.stage)} />
                            <ReviewItem label="Customer Type" value={formatValue(data.cohorts?.customerType as string)} />
                            <ReviewItem label="Price Band" value={formatValue(data.business?.priceBand)} />
                            <ReviewItem label="Sales Motion" value={formatValue(data.business?.salesMotion)} />
                            <ReviewItem label="Voice" value={formatValue(data.messaging?.voicePreference)} />
                        </div>

                        {/* Offer Statement */}
                        {data.business?.offerStatement && (
                            <div className={`${styles.reviewItem} ${styles.fullWidth} ${styles.highlight}`}>
                                <span className={styles.reviewLabel}>Value Proposition</span>
                                <p className={styles.reviewValue}>{data.business.offerStatement}</p>
                            </div>
                        )}

                        <div className={styles.reviewGrid}>
                            <ReviewItem label="Buyer Roles" value={formatList(data.cohorts?.buyerRoleChips)} />
                            <ReviewItem label="Regions" value={formatList(data.cohorts?.primaryRegions)} />
                            <ReviewItem label="Languages" value={formatList(data.cohorts?.languages)} />
                            <ReviewItem label="90-Day Goal" value={formatValue(data.goals?.primaryGoal)} />
                        </div>

                        <div className={styles.reviewGrid}>
                            <ReviewItem label="Constraints" value={formatList(data.goals?.constraints)} />
                            <ReviewItem label="Current Channels" value={formatList(data.reality?.currentChannels)} />
                            <ReviewItem label="Current Tools" value={formatList(data.reality?.currentTools)} />
                            <ReviewItem label="Proof Available" value={formatList(data.proof?.proofTypes)} />
                        </div>

                        {/* Customer Insights (New) */}
                        <div className={styles.reviewStack} style={{ marginTop: '2rem' }}>
                            <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">Customer Intelligence</h4>
                            <div className={styles.reviewGrid}>
                                <ReviewItem label="Best Customers" value={formatList(data.customerInsights?.bestCustomers)} />
                                <ReviewItem label="Trigger Events" value={formatList(data.customerInsights?.triggerEvents)} />
                                <ReviewItem label="Alternatives" value={formatList(data.customerInsights?.alternatives)} />
                                <ReviewItem label="Pain Ranking" value={formatList(data.customerInsights?.painRanking)} />
                            </div>
                        </div>
                    </div>
                );

            case 'clarifiers':
                // Only show if there's any clarifier data
                const hasClarifierData = data.cohorts?.companySize || data.cohorts?.salesCycle || data.cohorts?.averageOrderValue || data.business?.name;
                if (!hasClarifierData) return <p className="text-muted-foreground text-sm">No additional details captured.</p>;

                return (
                    <div className={styles.reviewGrid}>
                        {data.business?.name && (
                            <ReviewItem label="Business Name" value={data.business.name} />
                        )}
                        {data.cohorts?.companySize && (
                            <ReviewItem label="Target Company Size" value={data.cohorts.companySize} />
                        )}
                        {data.cohorts?.salesCycle && (
                            <ReviewItem label="Sales Cycle" value={formatValue(data.cohorts.salesCycle)} />
                        )}
                        {data.cohorts?.averageOrderValue && (
                            <ReviewItem label="Average Order Value" value={data.cohorts.averageOrderValue} />
                        )}
                    </div>
                );

            case 'deep-dive':
                // Only show if confession data exists
                const hasConfessionData = data.confession?.expensiveProblem || data.confession?.embarrassingTruth || data.confession?.signaling;
                if (!hasConfessionData) return <p className="text-muted-foreground text-sm">Not completed yet. You can add this later from Settings.</p>;

                return (
                    <div className={styles.reviewStack}>
                        <ReviewItem label="Expensive Problem" value={data.confession?.expensiveProblem} fullWidth />
                        <ReviewItem label="Embarrassing Truth" value={data.confession?.embarrassingTruth} fullWidth />
                        <ReviewItem label="Signaling" value={data.confession?.signaling} fullWidth />
                    </div>
                );

            default:
                return null;
        }
    };

    // Filter to only show non-review sections that have questions
    const visibleSections = SECTIONS.filter(s => s.id !== 'review');

    return (
        <div className={styles.reviewContainer}>
            <div className={styles.reviewHeader}>
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className={styles.reviewTitle}>Foundation Review</h1>
                        <p className={styles.reviewSubtitle}>
                            Here's what we know about your business. Review and launch.
                        </p>
                    </div>
                    <ClarityScore data={data} />
                </div>
            </div>

            <div className={styles.reviewSections}>
                {visibleSections.map((section) => (
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

            {/* Premium Components Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
                <FirstMoveTeaser data={data} />
                <BrandAura data={data} />
            </div>

            {/* Founder Quote */}
            <FounderQuote data={data} className="mt-6" />

            {/* Pitch Script */}
            <PitchScript data={data} className="mt-6" />

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
    if (!value || value === '—' || (Array.isArray(value) && value.length === 0)) return null;

    return (
        <div className={`${styles.reviewItem} ${fullWidth ? styles.fullWidth : ''} ${highlight ? styles.highlight : ''}`}>
            <span className={styles.reviewLabel}>{label}</span>
            <p className={styles.reviewValue}>{value}</p>
        </div>
    );
}
