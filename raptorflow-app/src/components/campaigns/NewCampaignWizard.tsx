'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import {
    Campaign,
    CampaignObjective,
    CampaignStatus,
    ChannelType,
    CHANNEL_LABELS
} from '@/lib/campaigns-types';
import { createCampaign, getCampaigns } from '@/lib/campaigns';
import { loadFoundationDB } from '@/lib/foundation';
import { Check, ArrowRight, ArrowLeft, X, Target, Users, Zap, DollarSign, RefreshCw, Rocket } from 'lucide-react';
import { toast } from 'sonner';
import styles from '@/components/moves/MoveWizard.module.css';

interface NewCampaignWizardProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onComplete: () => void;
}

type WizardStep = 'objective' | 'audience' | 'constraints' | 'measurement' | 'plan' | 'review';

const STEPS: WizardStep[] = ['objective', 'audience', 'constraints', 'measurement', 'plan', 'review'];

interface PendingMove {
    name: string;
    template: string;
    duration: number;
    effort: string;
    channels: ChannelType[];
    phase: 'foundation' | 'distribution' | 'scale';
    enabled: boolean;
}

const STEP_INFO: Record<WizardStep, { label: string; title: string; description: string; contextTitle: string; contextDesc: string }> = {
    objective: {
        label: 'Step 1',
        title: 'What are you trying to achieve?',
        description: 'Choose your primary objective for this 90-day campaign.',
        contextTitle: 'Setting Your North Star',
        contextDesc: 'Every campaign needs a clear goal. This determines which Moves we recommend.'
    },
    audience: {
        label: 'Step 2',
        title: 'Who are you targeting?',
        description: 'Select an ICP or describe your target audience.',
        contextTitle: 'Know Your Audience',
        contextDesc: 'The right audience makes all the difference. Be specific.'
    },
    constraints: {
        label: 'Step 3',
        title: 'What are your constraints?',
        description: 'Set your daily time budget and preferred channels.',
        contextTitle: 'Set the Boundaries',
        contextDesc: 'Be realistic. Consistency beats intensity every time.'
    },
    measurement: {
        label: 'Step 4',
        title: 'How will you measure success?',
        description: 'Define your target outcome for the 90 days.',
        contextTitle: 'Define Victory',
        contextDesc: 'A clear target makes execution easier and results measurable.'
    },
    plan: {
        label: 'Step 5',
        title: 'Your Campaign Plan',
        description: 'We\'ve generated a phased Move sequence. Customize as needed.',
        contextTitle: 'The Blueprint',
        contextDesc: 'Proven templates built from thousands of successful campaigns.'
    },
    review: {
        label: 'Step 6',
        title: 'Review & Launch',
        description: 'Confirm everything before you commit.',
        contextTitle: 'Final Check',
        contextDesc: 'Once you launch, it\'s time to execute. No more planning.'
    }
};

const OBJECTIVE_OPTIONS: { id: CampaignObjective; label: string; icon: any; desc: string }[] = [
    { id: 'acquire', label: 'Acquire', icon: Rocket, desc: 'Generate leads, book calls, grow pipeline' },
    { id: 'activate', label: 'Activate', icon: Zap, desc: 'Convert leads to paying customers' },
    { id: 'retain', label: 'Retain', icon: RefreshCw, desc: 'Keep customers engaged and reduce churn' },
    { id: 'monetize', label: 'Monetize', icon: DollarSign, desc: 'Increase revenue from existing customers' },
];

const METRIC_OPTIONS: Record<CampaignObjective, { label: string; unit: string }[]> = {
    acquire: [
        { label: 'Discovery calls booked', unit: 'calls' },
        { label: 'Leads generated', unit: 'leads' },
        { label: 'Demo requests', unit: 'demos' },
    ],
    activate: [
        { label: 'Conversions', unit: 'conversions' },
        { label: 'Trial-to-Paid', unit: 'conversions' },
        { label: 'First purchases', unit: 'purchases' },
    ],
    convert: [
        { label: 'Conversions', unit: 'conversions' },
        { label: 'Close rate', unit: '%' },
        { label: 'Revenue closed', unit: '₹' },
    ],
    launch: [
        { label: 'Signups', unit: 'signups' },
        { label: 'Waitlist entries', unit: 'entries' },
        { label: 'Launch day traffic', unit: 'visits' },
    ],
    proof: [
        { label: 'Testimonials collected', unit: 'testimonials' },
        { label: 'Case studies published', unit: 'case studies' },
        { label: 'Reviews generated', unit: 'reviews' },
    ],
    retain: [
        { label: 'Churn reduction', unit: '%' },
        { label: 'NPS improvement', unit: 'points' },
        { label: 'Engagement rate', unit: '%' },
    ],
    monetize: [
        { label: 'Revenue', unit: '₹' },
        { label: 'Upsells', unit: 'upsells' },
        { label: 'Cross-sells', unit: 'sales' },
    ],
    expand: [
        { label: 'New markets', unit: 'markets' },
        { label: 'Referrals', unit: 'referrals' },
    ],
    reposition: [
        { label: 'Perception shift', unit: '%' },
        { label: 'New segment awareness', unit: '%' },
        { label: 'Brand mentions', unit: 'mentions' },
    ],
};

const PHASE_MOVES: Record<CampaignObjective, PendingMove[]> = {
    acquire: [
        { name: 'Offer Proof Sprint', template: 'offer_proof', duration: 7, effort: '30m/day', channels: ['linkedin', 'email'], phase: 'foundation', enabled: true },
        { name: 'Profile Tune-Up Sprint', template: 'profile_tuneup', duration: 7, effort: '20m/day', channels: ['linkedin'], phase: 'foundation', enabled: true },
        { name: 'Problem Post Sprint', template: 'problem_post', duration: 7, effort: '30m/day', channels: ['linkedin', 'twitter'], phase: 'distribution', enabled: true },
        { name: 'Outbound DM Sprint', template: 'outbound_dm', duration: 7, effort: '45m/day', channels: ['linkedin', 'instagram'], phase: 'distribution', enabled: true },
        { name: 'Case Study Sprint', template: 'case_study', duration: 14, effort: '45m/day', channels: ['linkedin', 'email'], phase: 'scale', enabled: true },
        { name: 'Referral Nudge Sprint', template: 'referral', duration: 7, effort: '20m/day', channels: ['whatsapp', 'email'], phase: 'scale', enabled: true },
    ],
    activate: [
        { name: 'Onboarding Email Sprint', template: 'onboarding_email', duration: 14, effort: '30m/day', channels: ['email'], phase: 'foundation', enabled: true },
        { name: 'Warm DM Campaign', template: 'warm_dm', duration: 7, effort: '30m/day', channels: ['linkedin', 'whatsapp'], phase: 'distribution', enabled: true },
        { name: 'Demo Follow-Up Sprint', template: 'demo_followup', duration: 7, effort: '25m/day', channels: ['email'], phase: 'scale', enabled: true },
    ],
    convert: [
        { name: 'Sales Sequence Sprint', template: 'sales_sequence', duration: 7, effort: '30m/day', channels: ['email'], phase: 'foundation', enabled: true },
        { name: 'Objection Handler Sprint', template: 'objection_handler', duration: 7, effort: '25m/day', channels: ['email', 'linkedin'], phase: 'distribution', enabled: true },
        { name: 'Close Push Sprint', template: 'close_push', duration: 7, effort: '30m/day', channels: ['email'], phase: 'scale', enabled: true },
    ],
    launch: [
        { name: 'Pre-Launch Buzz Sprint', template: 'prelaunch', duration: 14, effort: '30m/day', channels: ['linkedin', 'twitter'], phase: 'foundation', enabled: true },
        { name: 'Launch Day Sprint', template: 'launch_day', duration: 7, effort: '60m/day', channels: ['linkedin', 'twitter', 'email'], phase: 'distribution', enabled: true },
        { name: 'Post-Launch Follow-Up', template: 'post_launch', duration: 7, effort: '30m/day', channels: ['email'], phase: 'scale', enabled: true },
    ],
    proof: [
        { name: 'Testimonial Request Sprint', template: 'testimonial_request', duration: 7, effort: '20m/day', channels: ['email', 'whatsapp'], phase: 'foundation', enabled: true },
        { name: 'Case Study Creation Sprint', template: 'case_study_create', duration: 14, effort: '45m/day', channels: ['linkedin'], phase: 'distribution', enabled: true },
        { name: 'Social Proof Sprint', template: 'social_proof', duration: 7, effort: '25m/day', channels: ['linkedin', 'twitter'], phase: 'scale', enabled: true },
    ],
    retain: [
        { name: 'Check-In Sprint', template: 'checkin', duration: 7, effort: '20m/day', channels: ['email', 'whatsapp'], phase: 'foundation', enabled: true },
        { name: 'Value Reminder Sprint', template: 'value_reminder', duration: 14, effort: '30m/day', channels: ['email'], phase: 'distribution', enabled: true },
        { name: 'Winback Sprint', template: 'winback', duration: 7, effort: '30m/day', channels: ['email'], phase: 'scale', enabled: true },
    ],
    monetize: [
        { name: 'Upsell Sprint', template: 'upsell', duration: 7, effort: '30m/day', channels: ['email'], phase: 'foundation', enabled: true },
        { name: 'Cross-Sell Sprint', template: 'cross_sell', duration: 14, effort: '30m/day', channels: ['email', 'linkedin'], phase: 'distribution', enabled: true },
        { name: 'Referral Incentive Sprint', template: 'referral_incentive', duration: 7, effort: '25m/day', channels: ['email', 'whatsapp'], phase: 'scale', enabled: true },
    ],
    expand: [
        { name: 'Partner Outreach Sprint', template: 'partner_outreach', duration: 14, effort: '45m/day', channels: ['linkedin', 'email'], phase: 'foundation', enabled: true },
        { name: 'Community Build Sprint', template: 'community', duration: 14, effort: '30m/day', channels: ['twitter', 'linkedin'], phase: 'distribution', enabled: true },
    ],
    reposition: [
        { name: 'Messaging Refresh Sprint', template: 'messaging_refresh', duration: 7, effort: '30m/day', channels: ['linkedin'], phase: 'foundation', enabled: true },
        { name: 'New Narrative Sprint', template: 'new_narrative', duration: 14, effort: '45m/day', channels: ['linkedin', 'twitter'], phase: 'distribution', enabled: true },
        { name: 'Authority Build Sprint', template: 'authority', duration: 7, effort: '30m/day', channels: ['linkedin'], phase: 'scale', enabled: true },
    ],
};

export function NewCampaignWizard({ open, onOpenChange, onComplete }: NewCampaignWizardProps) {
    const [step, setStep] = useState<WizardStep>('objective');
    const [icps, setICPs] = useState<any[]>([]);

    // Form state
    const [campaignName, setCampaignName] = useState('');
    const [objective, setObjective] = useState<CampaignObjective | null>(null);
    const [selectedICP, setSelectedICP] = useState<string>('');
    const [audienceDesc, setAudienceDesc] = useState('');
    const [dailyTime, setDailyTime] = useState<number>(30);
    const [selectedChannels, setSelectedChannels] = useState<ChannelType[]>(['linkedin']);
    const [metric, setMetric] = useState<string>('');
    const [targetNumber, setTargetNumber] = useState<number>(0);
    const [pendingMoves, setPendingMoves] = useState<PendingMove[]>([]);

    useEffect(() => {
        if (open) {
            // Reset form
            setStep('objective');
            setCampaignName('');
            setObjective(null);
            setSelectedICP('');
            setAudienceDesc('');
            setDailyTime(30);
            setSelectedChannels(['linkedin']);
            setMetric('');
            setTargetNumber(0);
            setPendingMoves([]);

            // Load ICPs
            loadFoundationDB().then(data => {
                if ((data as any).icps) {
                    setICPs(Object.values((data as any).icps));
                }
            });
        }
    }, [open]);

    // Generate plan when reaching plan step
    useEffect(() => {
        if (step === 'plan' && objective) {
            const moves = PHASE_MOVES[objective] || [];
            setPendingMoves(moves.map(m => ({ ...m })));
        }
    }, [step, objective]);

    const goNext = () => {
        const idx = STEPS.indexOf(step);
        if (idx < STEPS.length - 1) {
            setStep(STEPS[idx + 1]);
        }
    };

    const goBack = () => {
        const idx = STEPS.indexOf(step);
        if (idx > 0) {
            setStep(STEPS[idx - 1]);
        }
    };

    const canProceed = () => {
        switch (step) {
            case 'objective': return !!objective && !!campaignName;
            case 'audience': return !!selectedICP || !!audienceDesc;
            case 'constraints': return dailyTime > 0 && selectedChannels.length > 0;
            case 'measurement': return !!metric && targetNumber > 0;
            case 'plan': return pendingMoves.some(m => m.enabled);
            case 'review': return true;
            default: return false;
        }
    };

    const toggleChannel = (channel: ChannelType) => {
        if (selectedChannels.includes(channel)) {
            if (selectedChannels.length > 1) {
                setSelectedChannels(selectedChannels.filter(c => c !== channel));
            }
        } else {
            setSelectedChannels([...selectedChannels, channel]);
        }
    };

    const toggleMove = (index: number) => {
        setPendingMoves(pendingMoves.map((m, i) =>
            i === index ? { ...m, enabled: !m.enabled } : m
        ));
    };

    const handleCreate = async () => {
        if (!objective) return;

        try {
            const now = new Date();
            const endDate = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000);

            const newCampaign: Omit<Campaign, 'id' | 'createdAt' | 'updatedAt'> = {
                name: campaignName,
                objective,
                status: 'planned',
                ragStatus: 'green',
                targetAudience: selectedICP || audienceDesc,
                channels: selectedChannels,
                duration: 90,
                offer: 'book_call',
                moveLength: 7,
                dailyEffort: dailyTime as 15 | 30 | 60,
                timeline: {
                    startDate: now.toISOString(),
                    endDate: endDate.toISOString(),
                    duration: 90
                },
                metrics: {
                    primary: metric,
                    target: targetNumber,
                    current: 0
                },
                stages: [], // Moves will be created separately
            };

            await createCampaign(newCampaign as any);
            toast.success('Campaign created!');
            onComplete();
        } catch (error) {
            console.error('Failed to create campaign:', error);
            toast.error('Failed to create campaign');
        }
    };

    const getNextLabel = () => {
        switch (step) {
            case 'objective': return 'Set Audience';
            case 'audience': return 'Set Constraints';
            case 'constraints': return 'Set Target';
            case 'measurement': return 'Generate Plan';
            case 'plan': return 'Review';
            case 'review': return 'Launch Campaign';
            default: return 'Continue';
        }
    };

    const renderContent = () => {
        switch (step) {
            case 'objective':
                return (
                    <div className={styles.questionWrapper}>
                        <div className={styles.questionHeader}>
                            <span className={styles.qNumber}>{STEP_INFO[step].label}</span>
                            <h2 className={styles.qText}>{STEP_INFO[step].title}</h2>
                            <p className={styles.qHint}>{STEP_INFO[step].description}</p>
                        </div>

                        <div className={styles.inputArea}>
                            <div className={styles.optionsGrid}>
                                {OBJECTIVE_OPTIONS.map(opt => {
                                    const Icon = opt.icon;
                                    return (
                                        <button
                                            key={opt.id}
                                            className={`${styles.optionCard} ${objective === opt.id ? styles.selected : ''}`}
                                            onClick={() => setObjective(opt.id)}
                                        >
                                            <div className={styles.optionIcon}>
                                                <Icon style={{ width: 24, height: 24 }} />
                                            </div>
                                            <div className={styles.optionTitle}>{opt.label}</div>
                                            <div className={styles.optionDesc}>{opt.desc}</div>
                                            {objective === opt.id && (
                                                <div className={styles.checkmark}>
                                                    <Check style={{ width: 14, height: 14, color: '#1A1D1E' }} />
                                                </div>
                                            )}
                                        </button>
                                    );
                                })}
                            </div>

                            <div style={{ marginTop: 32 }}>
                                <label style={{
                                    display: 'block',
                                    fontFamily: 'Inter, sans-serif',
                                    fontSize: 12,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.1em',
                                    color: '#9D9F9F',
                                    marginBottom: 12
                                }}>
                                    Campaign Name
                                </label>
                                <input
                                    type="text"
                                    value={campaignName}
                                    onChange={e => setCampaignName(e.target.value)}
                                    className={styles.textInput}
                                    placeholder="e.g., Chennai Founders Acquisition"
                                />
                            </div>
                        </div>

                        <div className={styles.actionArea}>
                            <div />
                            <button
                                className={styles.continueBtn}
                                onClick={goNext}
                                disabled={!canProceed()}
                            >
                                {getNextLabel()}
                                <ArrowRight style={{ width: 16, height: 16 }} />
                            </button>
                        </div>
                    </div>
                );

            case 'audience':
                return (
                    <div className={styles.questionWrapper}>
                        <div className={styles.questionHeader}>
                            <span className={styles.qNumber}>{STEP_INFO[step].label}</span>
                            <h2 className={styles.qText}>{STEP_INFO[step].title}</h2>
                            <p className={styles.qHint}>{STEP_INFO[step].description}</p>
                        </div>

                        <div className={styles.inputArea}>
                            {icps.length > 0 && (
                                <>
                                    <label style={{
                                        display: 'block',
                                        fontFamily: 'Inter, sans-serif',
                                        fontSize: 12,
                                        fontWeight: 600,
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.1em',
                                        color: '#9D9F9F',
                                        marginBottom: 12
                                    }}>
                                        Select an ICP
                                    </label>
                                    <div className={styles.optionsGrid}>
                                        {icps.slice(0, 4).map(icp => (
                                            <button
                                                key={icp.id}
                                                className={`${styles.optionCard} ${selectedICP === icp.id ? styles.selected : ''}`}
                                                onClick={() => {
                                                    setSelectedICP(icp.id);
                                                    setAudienceDesc('');
                                                }}
                                                style={{ padding: 20 }}
                                            >
                                                <div className={styles.optionTitle}>{icp.name || 'ICP'}</div>
                                                <div className={styles.optionDesc}>{icp.role || icp.description || 'Target segment'}</div>
                                                {selectedICP === icp.id && (
                                                    <div className={styles.checkmark}>
                                                        <Check style={{ width: 14, height: 14, color: '#1A1D1E' }} />
                                                    </div>
                                                )}
                                            </button>
                                        ))}
                                    </div>
                                </>
                            )}

                            <div style={{ marginTop: 32 }}>
                                <label style={{
                                    display: 'block',
                                    fontFamily: 'Inter, sans-serif',
                                    fontSize: 12,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.1em',
                                    color: '#9D9F9F',
                                    marginBottom: 12
                                }}>
                                    Or describe your audience
                                </label>
                                <input
                                    type="text"
                                    value={audienceDesc}
                                    onChange={e => {
                                        setAudienceDesc(e.target.value);
                                        if (e.target.value) setSelectedICP('');
                                    }}
                                    className={styles.textInput}
                                    placeholder="e.g., B2B SaaS founders in Chennai"
                                />
                            </div>
                        </div>

                        <div className={styles.actionArea}>
                            <button className={styles.backButton} onClick={goBack}>
                                Back
                            </button>
                            <button
                                className={styles.continueBtn}
                                onClick={goNext}
                                disabled={!canProceed()}
                            >
                                {getNextLabel()}
                                <ArrowRight style={{ width: 16, height: 16 }} />
                            </button>
                        </div>
                    </div>
                );

            case 'constraints':
                return (
                    <div className={styles.questionWrapper}>
                        <div className={styles.questionHeader}>
                            <span className={styles.qNumber}>{STEP_INFO[step].label}</span>
                            <h2 className={styles.qText}>{STEP_INFO[step].title}</h2>
                            <p className={styles.qHint}>{STEP_INFO[step].description}</p>
                        </div>

                        <div className={styles.inputArea}>
                            <label style={{
                                display: 'block',
                                fontFamily: 'Inter, sans-serif',
                                fontSize: 12,
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                letterSpacing: '0.1em',
                                color: '#9D9F9F',
                                marginBottom: 12
                            }}>
                                Daily time budget
                            </label>
                            <div className={styles.segmentedControl}>
                                {[15, 30, 45, 60].map(mins => (
                                    <button
                                        key={mins}
                                        className={`${styles.segment} ${dailyTime === mins ? styles.active : ''}`}
                                        onClick={() => setDailyTime(mins)}
                                    >
                                        {mins}m
                                    </button>
                                ))}
                            </div>

                            <div style={{ marginTop: 32 }}>
                                <label style={{
                                    display: 'block',
                                    fontFamily: 'Inter, sans-serif',
                                    fontSize: 12,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.1em',
                                    color: '#9D9F9F',
                                    marginBottom: 12
                                }}>
                                    Channels
                                </label>
                                <div className={styles.optionsGrid} style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
                                    {(Object.entries(CHANNEL_LABELS) as [ChannelType, string][]).slice(0, 6).map(([key, label]) => (
                                        <button
                                            key={key}
                                            className={`${styles.optionCard} ${selectedChannels.includes(key) ? styles.selected : ''}`}
                                            onClick={() => toggleChannel(key)}
                                            style={{ padding: 16 }}
                                        >
                                            <div className={styles.optionTitle}>{label}</div>
                                            {selectedChannels.includes(key) && (
                                                <div className={styles.checkmark}>
                                                    <Check style={{ width: 14, height: 14, color: '#1A1D1E' }} />
                                                </div>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className={styles.actionArea}>
                            <button className={styles.backButton} onClick={goBack}>
                                Back
                            </button>
                            <button
                                className={styles.continueBtn}
                                onClick={goNext}
                                disabled={!canProceed()}
                            >
                                {getNextLabel()}
                                <ArrowRight style={{ width: 16, height: 16 }} />
                            </button>
                        </div>
                    </div>
                );

            case 'measurement':
                return (
                    <div className={styles.questionWrapper}>
                        <div className={styles.questionHeader}>
                            <span className={styles.qNumber}>{STEP_INFO[step].label}</span>
                            <h2 className={styles.qText}>{STEP_INFO[step].title}</h2>
                            <p className={styles.qHint}>{STEP_INFO[step].description}</p>
                        </div>

                        <div className={styles.inputArea}>
                            <label style={{
                                display: 'block',
                                fontFamily: 'Inter, sans-serif',
                                fontSize: 12,
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                letterSpacing: '0.1em',
                                color: '#9D9F9F',
                                marginBottom: 12
                            }}>
                                Primary metric
                            </label>
                            <div className={styles.optionsGrid} style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
                                {objective && METRIC_OPTIONS[objective]?.map(opt => (
                                    <button
                                        key={opt.label}
                                        className={`${styles.optionCard} ${metric === opt.label ? styles.selected : ''}`}
                                        onClick={() => setMetric(opt.label)}
                                        style={{ padding: 16 }}
                                    >
                                        <div className={styles.optionTitle}>{opt.label}</div>
                                        {metric === opt.label && (
                                            <div className={styles.checkmark}>
                                                <Check style={{ width: 14, height: 14, color: '#1A1D1E' }} />
                                            </div>
                                        )}
                                    </button>
                                ))}
                            </div>

                            <div style={{ marginTop: 32 }}>
                                <label style={{
                                    display: 'block',
                                    fontFamily: 'Inter, sans-serif',
                                    fontSize: 12,
                                    fontWeight: 600,
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.1em',
                                    color: '#9D9F9F',
                                    marginBottom: 12
                                }}>
                                    Target in 90 days
                                </label>
                                <input
                                    type="number"
                                    value={targetNumber || ''}
                                    onChange={e => setTargetNumber(parseInt(e.target.value) || 0)}
                                    className={styles.textInput}
                                    placeholder="e.g., 120"
                                />
                            </div>
                        </div>

                        <div className={styles.actionArea}>
                            <button className={styles.backButton} onClick={goBack}>
                                Back
                            </button>
                            <button
                                className={styles.continueBtn}
                                onClick={goNext}
                                disabled={!canProceed()}
                            >
                                {getNextLabel()}
                                <ArrowRight style={{ width: 16, height: 16 }} />
                            </button>
                        </div>
                    </div>
                );

            case 'plan':
                const foundationMoves = pendingMoves.filter(m => m.phase === 'foundation');
                const distributionMoves = pendingMoves.filter(m => m.phase === 'distribution');
                const scaleMoves = pendingMoves.filter(m => m.phase === 'scale');

                return (
                    <div className={styles.questionWrapper}>
                        <div className={styles.questionHeader}>
                            <span className={styles.qNumber}>{STEP_INFO[step].label}</span>
                            <h2 className={styles.qText}>{STEP_INFO[step].title}</h2>
                            <p className={styles.qHint}>{STEP_INFO[step].description}</p>
                        </div>

                        <div className={styles.inputArea} style={{ maxHeight: '50vh', overflowY: 'auto' }}>
                            {/* Foundation Phase */}
                            {foundationMoves.length > 0 && (
                                <div style={{ marginBottom: 24 }}>
                                    <div style={{
                                        fontFamily: 'Inter, sans-serif',
                                        fontSize: 12,
                                        fontWeight: 600,
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.1em',
                                        color: '#D97706',
                                        marginBottom: 12
                                    }}>
                                        Weeks 1-2 — Foundation
                                    </div>
                                    {foundationMoves.map((move, i) => {
                                        const globalIndex = pendingMoves.indexOf(move);
                                        return (
                                            <div
                                                key={i}
                                                style={{
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'space-between',
                                                    padding: 16,
                                                    background: move.enabled ? '#FFFFFF' : '#F8F9F7',
                                                    border: '1px solid #E5E6E3',
                                                    borderRadius: 12,
                                                    marginBottom: 8,
                                                    opacity: move.enabled ? 1 : 0.5
                                                }}
                                            >
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                                    <button
                                                        onClick={() => toggleMove(globalIndex)}
                                                        style={{
                                                            width: 20,
                                                            height: 20,
                                                            borderRadius: 4,
                                                            border: move.enabled ? 'none' : '2px solid #E5E6E3',
                                                            background: move.enabled ? '#1A1D1E' : 'transparent',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center',
                                                            cursor: 'pointer'
                                                        }}
                                                    >
                                                        {move.enabled && <Check style={{ width: 12, height: 12, color: '#FFFFFF' }} />}
                                                    </button>
                                                    <div>
                                                        <div style={{ fontWeight: 600, color: '#2D3538' }}>{move.name}</div>
                                                        <div style={{ fontSize: 12, color: '#5B5F61' }}>
                                                            {move.effort} • {move.duration}D
                                                        </div>
                                                    </div>
                                                </div>
                                                <div style={{ display: 'flex', gap: 6 }}>
                                                    {move.channels.slice(0, 2).map(ch => (
                                                        <span key={ch} style={{
                                                            padding: '4px 8px',
                                                            background: '#F8F9F7',
                                                            borderRadius: 6,
                                                            fontSize: 11,
                                                            color: '#5B5F61'
                                                        }}>
                                                            {CHANNEL_LABELS[ch]}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}

                            {/* Distribution Phase */}
                            {distributionMoves.length > 0 && (
                                <div style={{ marginBottom: 24 }}>
                                    <div style={{
                                        fontFamily: 'Inter, sans-serif',
                                        fontSize: 12,
                                        fontWeight: 600,
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.1em',
                                        color: '#2563EB',
                                        marginBottom: 12
                                    }}>
                                        Weeks 3-6 — Distribution
                                    </div>
                                    {distributionMoves.map((move, i) => {
                                        const globalIndex = pendingMoves.indexOf(move);
                                        return (
                                            <div
                                                key={i}
                                                style={{
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'space-between',
                                                    padding: 16,
                                                    background: move.enabled ? '#FFFFFF' : '#F8F9F7',
                                                    border: '1px solid #E5E6E3',
                                                    borderRadius: 12,
                                                    marginBottom: 8,
                                                    opacity: move.enabled ? 1 : 0.5
                                                }}
                                            >
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                                    <button
                                                        onClick={() => toggleMove(globalIndex)}
                                                        style={{
                                                            width: 20,
                                                            height: 20,
                                                            borderRadius: 4,
                                                            border: move.enabled ? 'none' : '2px solid #E5E6E3',
                                                            background: move.enabled ? '#1A1D1E' : 'transparent',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center',
                                                            cursor: 'pointer'
                                                        }}
                                                    >
                                                        {move.enabled && <Check style={{ width: 12, height: 12, color: '#FFFFFF' }} />}
                                                    </button>
                                                    <div>
                                                        <div style={{ fontWeight: 600, color: '#2D3538' }}>{move.name}</div>
                                                        <div style={{ fontSize: 12, color: '#5B5F61' }}>
                                                            {move.effort} • {move.duration}D
                                                        </div>
                                                    </div>
                                                </div>
                                                <div style={{ display: 'flex', gap: 6 }}>
                                                    {move.channels.slice(0, 2).map(ch => (
                                                        <span key={ch} style={{
                                                            padding: '4px 8px',
                                                            background: '#F8F9F7',
                                                            borderRadius: 6,
                                                            fontSize: 11,
                                                            color: '#5B5F61'
                                                        }}>
                                                            {CHANNEL_LABELS[ch]}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}

                            {/* Scale Phase */}
                            {scaleMoves.length > 0 && (
                                <div>
                                    <div style={{
                                        fontFamily: 'Inter, sans-serif',
                                        fontSize: 12,
                                        fontWeight: 600,
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.1em',
                                        color: '#16A34A',
                                        marginBottom: 12
                                    }}>
                                        Weeks 7-12 — Scale
                                    </div>
                                    {scaleMoves.map((move, i) => {
                                        const globalIndex = pendingMoves.indexOf(move);
                                        return (
                                            <div
                                                key={i}
                                                style={{
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'space-between',
                                                    padding: 16,
                                                    background: move.enabled ? '#FFFFFF' : '#F8F9F7',
                                                    border: '1px solid #E5E6E3',
                                                    borderRadius: 12,
                                                    marginBottom: 8,
                                                    opacity: move.enabled ? 1 : 0.5
                                                }}
                                            >
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                                    <button
                                                        onClick={() => toggleMove(globalIndex)}
                                                        style={{
                                                            width: 20,
                                                            height: 20,
                                                            borderRadius: 4,
                                                            border: move.enabled ? 'none' : '2px solid #E5E6E3',
                                                            background: move.enabled ? '#1A1D1E' : 'transparent',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center',
                                                            cursor: 'pointer'
                                                        }}
                                                    >
                                                        {move.enabled && <Check style={{ width: 12, height: 12, color: '#FFFFFF' }} />}
                                                    </button>
                                                    <div>
                                                        <div style={{ fontWeight: 600, color: '#2D3538' }}>{move.name}</div>
                                                        <div style={{ fontSize: 12, color: '#5B5F61' }}>
                                                            {move.effort} • {move.duration}D
                                                        </div>
                                                    </div>
                                                </div>
                                                <div style={{ display: 'flex', gap: 6 }}>
                                                    {move.channels.slice(0, 2).map(ch => (
                                                        <span key={ch} style={{
                                                            padding: '4px 8px',
                                                            background: '#F8F9F7',
                                                            borderRadius: 6,
                                                            fontSize: 11,
                                                            color: '#5B5F61'
                                                        }}>
                                                            {CHANNEL_LABELS[ch]}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>

                        <div className={styles.actionArea}>
                            <button className={styles.backButton} onClick={goBack}>
                                Back
                            </button>
                            <button
                                className={styles.continueBtn}
                                onClick={goNext}
                                disabled={!canProceed()}
                            >
                                {getNextLabel()}
                                <ArrowRight style={{ width: 16, height: 16 }} />
                            </button>
                        </div>
                    </div>
                );

            case 'review':
                const enabledMoves = pendingMoves.filter(m => m.enabled);
                return (
                    <div className={styles.questionWrapper}>
                        <div className={styles.questionHeader}>
                            <span className={styles.qNumber}>{STEP_INFO[step].label}</span>
                            <h2 className={styles.qText}>{STEP_INFO[step].title}</h2>
                            <p className={styles.qHint}>{STEP_INFO[step].description}</p>
                        </div>

                        <div className={styles.inputArea}>
                            <div className={styles.moveBrief}>
                                <h3 className={styles.briefTitle}>{campaignName}</h3>

                                <div className={styles.briefSection}>
                                    <div className={styles.briefLabel}>Objective</div>
                                    <div className={styles.briefValue}>{objective}</div>
                                </div>

                                <div className={styles.briefSection}>
                                    <div className={styles.briefLabel}>Target</div>
                                    <div className={styles.briefValue}>{targetNumber} {metric} in 90 days</div>
                                </div>

                                <div className={styles.briefSection}>
                                    <div className={styles.briefLabel}>Audience</div>
                                    <div className={styles.briefValue}>{selectedICP || audienceDesc}</div>
                                </div>

                                <div className={styles.briefSection}>
                                    <div className={styles.briefLabel}>Daily Commitment</div>
                                    <div className={styles.briefValue}>{dailyTime} minutes</div>
                                </div>

                                <div className={styles.briefSection}>
                                    <div className={styles.briefLabel}>Moves Planned</div>
                                    <div className={styles.briefValue}>{enabledMoves.length} Moves across 3 phases</div>
                                </div>
                            </div>
                        </div>

                        <div className={styles.actionArea}>
                            <button className={styles.backButton} onClick={goBack}>
                                Back
                            </button>
                            <button
                                className={styles.continueBtn}
                                onClick={handleCreate}
                            >
                                Launch Campaign
                                <Rocket style={{ width: 16, height: 16 }} />
                            </button>
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className={styles.wizardDialog}>
                <div className={styles.wizardContainer}>
                    {/* Left Panel */}
                    <div className={styles.leftPanel}>
                        <div className={styles.logoArea}>
                            <div className={styles.logoBox} />
                            <span className={styles.logoText}>RAPTORFLOW</span>
                        </div>

                        <div className={styles.stepInfo}>
                            <span className={styles.stepLabel}>Create Campaign</span>
                            <h2 className={styles.stepTitle}>{STEP_INFO[step].contextTitle}</h2>
                            <p className={styles.stepDescription}>{STEP_INFO[step].contextDesc}</p>
                        </div>

                        <div className={styles.progressSteps}>
                            {STEPS.map((s, idx) => {
                                const currentIdx = STEPS.indexOf(step);
                                const isActive = s === step;
                                const isCompleted = idx < currentIdx;

                                return (
                                    <div
                                        key={s}
                                        className={`${styles.progressStep} ${isActive ? styles.active : ''} ${isCompleted ? styles.completed : ''}`}
                                    >
                                        <div className={styles.stepDot} />
                                        <span className={styles.stepName}>{STEP_INFO[s].label}</span>
                                    </div>
                                );
                            })}
                        </div>

                        <div className={styles.footerMeta}>
                            <button className={styles.exitButton} onClick={() => onOpenChange(false)}>
                                <X style={{ width: 16, height: 16 }} />
                                Exit
                            </button>
                        </div>
                    </div>

                    {/* Right Panel */}
                    <div className={styles.rightPanel}>
                        <div className={styles.panelContent}>
                            {renderContent()}
                        </div>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
