import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Users, Trash2, Check, Loader2, Edit2 } from 'lucide-react';
import { LuxeHeading, LuxeCard, LuxeButton, LuxeInput, LuxeTextarea, LuxeBadge } from '../ui/PremiumUI';

const Act3Tribes = ({ positioning, strategy, onComplete, onBack }) => {
    const [isLoading, setIsLoading] = useState(true);
    const [icps, setIcps] = useState([]);
    const [selectedIcpId, setSelectedIcpId] = useState(null);

    const selectedIcp = icps.find(icp => icp.id === selectedIcpId);

    // Simulate AI generating ICPs based on positioning context
    useEffect(() => {
        const generateICPs = async () => {
            setIsLoading(true);
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Mock AI-generated ICPs based on context
            const proposedICPs = [
                {
                    id: 'icp-1',
                    name: 'Indie SaaS Founders',
                    label: 'Product-led, bootstrapped',
                    keep: true,
                    firmographics: {
                        companySize: '$500K - $3M ARR',
                        stage: 'Seed to Series A',
                        geography: 'North America, Europe',
                        teamSize: '5-20 employees'
                    },
                    psychographics: {
                        motivations: ['Efficiency', 'Control', 'Speed to market'],
                        fears: ['Vendor lock-in', 'Complexity', 'High CAC'],
                        worldview: 'Believes in lean operations and product-market fit over growth-at-all-costs'
                    },
                    buyingSignals: {
                        channels: ['Product Hunt', 'Twitter', 'Indie Hackers', 'LinkedIn'],
                        triggers: ['Hitting scaling limits', 'Manual process pain', 'Competitor launch'],
                        objections: ['Price vs features', 'Implementation time', 'Integration complexity']
                    }
                },
                {
                    id: 'icp-2',
                    name: 'Enterprise RevOps Leaders',
                    label: 'Process-driven, metrics-focused',
                    keep: true,
                    firmographics: {
                        companySize: '$50M+ ARR',
                        stage: 'Series C+',
                        geography: 'Global',
                        teamSize: '500+ employees'
                    },
                    psychographics: {
                        motivations: ['Predictability', 'Compliance', 'ROI proof'],
                        fears: ['Data silos', 'Audit failures', 'Team resistance'],
                        worldview: 'Needs executive buy-in and proven ROI before any purchase'
                    },
                    buyingSignals: {
                        channels: ['LinkedIn', 'Industry conferences', 'Analyst reports', 'Referrals'],
                        triggers: ['Quarterly planning', 'System migration', 'Compliance deadline'],
                        objections: ['Security review', 'Budget approval', 'Change management']
                    }
                },
                {
                    id: 'icp-3',
                    name: 'Growth-Stage Marketing Teams',
                    label: 'Data-hungry, experimental',
                    keep: true,
                    firmographics: {
                        companySize: '$5M - $20M ARR',
                        stage: 'Series A to B',
                        geography: 'US, UK, Canada',
                        teamSize: '50-200 employees'
                    },
                    psychographics: {
                        motivations: ['Attribution clarity', 'Campaign velocity', 'Competitive edge'],
                        fears: ['Wasted ad spend', 'Missed opportunities', 'Slow execution'],
                        worldview: 'Willing to experiment with new tools if they promise measurable impact'
                    },
                    buyingSignals: {
                        channels: ['Google search', 'Podcasts', 'Slack communities', 'Webinars'],
                        triggers: ['New funding round', 'Hiring spree', 'Product launch'],
                        objections: ['Learning curve', 'Stack bloat', 'Unclear differentiation']
                    }
                }
            ];

            setIcps(proposedICPs);
            setSelectedIcpId(proposedICPs[0].id);
            setIsLoading(false);
        };

        generateICPs();
    }, [positioning, strategy]);

    const toggleKeep = (id) => {
        setIcps(prev => prev.map(icp =>
            icp.id === id ? { ...icp, keep: !icp.keep } : icp
        ));
    };

    const updateIcpName = (id, newName) => {
        setIcps(prev => prev.map(icp =>
            icp.id === id ? { ...icp, name: newName } : icp
        ));
    };

    const handleFinish = () => {
        const keptICPs = icps.filter(icp => icp.keep);
        if (keptICPs.length > 0) {
            onComplete(keptICPs);
        }
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="fixed inset-0 flex items-center justify-center" style={{ backgroundColor: 'var(--bg-app)' }}>
                <div className="text-center space-y-6">
                    <Loader2 className="w-12 h-12 animate-spin mx-auto" style={{ color: 'var(--ink-strong)' }} />
                    <div>
                        <h2 className="font-display text-3xl mb-2" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                            Mapping your tribes…
                        </h2>
                        <p className="text-base" style={{ color: 'var(--ink-soft)' }}>
                            Analyzing your positioning to identify ideal customer profiles.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full py-12"
        >
            <div className="max-w-[1200px] mx-auto">
                {/* Header */}
                <div className="text-center mb-12">
                    <LuxeBadge variant="outline" className="mb-4">Act III</LuxeBadge>
                    <h1 className="font-display text-4xl lg:text-5xl mb-3" style={{ fontFamily: 'var(--font-display)', color: 'var(--ink-strong)' }}>
                        The Tribes
                    </h1>
                    <p className="text-lg" style={{ color: 'var(--ink-soft)' }}>
                        These are the tribes your positioning naturally speaks to. Name them and keep the ones that matter.
                    </p>
                </div>

                {/* Two-column layout */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Left: ICP List */}
                    <div className="lg:col-span-4 space-y-4">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--ink-soft)' }}>
                                Your ICPs
                            </h3>
                            <span className="text-xs" style={{ color: 'var(--ink-soft)' }}>
                                {icps.filter(icp => icp.keep).length} selected
                            </span>
                        </div>

                        <div className="space-y-3 max-h-[600px] overflow-y-auto scrollbar-hide">
                            {icps.map(icp => (
                                <div
                                    key={icp.id}
                                    onClick={() => setSelectedIcpId(icp.id)}
                                    className="p-4 rounded-lg cursor-pointer transition-all group relative"
                                    style={{
                                        border: selectedIcpId === icp.id ? '2px solid var(--ink-strong)' : '1px solid var(--border-subtle)',
                                        backgroundColor: selectedIcpId === icp.id ? '#FAFAFA' : 'white',
                                        opacity: icp.keep ? 1 : 0.5
                                    }}
                                >
                                    <div className="flex items-start gap-3">
                                        <div
                                            className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                                            style={{ backgroundColor: selectedIcpId === icp.id ? 'var(--ink-strong)' : '#F5F5F5' }}
                                        >
                                            <Users
                                                className="w-4 h-4"
                                                style={{ color: selectedIcpId === icp.id ? 'white' : 'var(--ink-soft)' }}
                                            />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <h4 className="font-semibold text-sm truncate" style={{ color: 'var(--ink-strong)' }}>
                                                {icp.name}
                                            </h4>
                                            <p className="text-xs truncate mt-1" style={{ color: 'var(--ink-soft)' }}>
                                                {icp.label}
                                            </p>
                                            <div className="flex flex-wrap gap-1 mt-2">
                                                <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ backgroundColor: '#F5F5F5', color: 'var(--ink-soft)' }}>
                                                    {icp.firmographics.companySize}
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                toggleKeep(icp.id);
                                            }}
                                            className="p-1.5 rounded transition-all"
                                            style={{
                                                backgroundColor: icp.keep ? 'var(--ink-strong)' : '#F5F5F5',
                                                color: icp.keep ? 'white' : 'var(--ink-soft)'
                                            }}
                                        >
                                            <Check className="w-3 h-3" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Right: ICP Detail */}
                    <div className="lg:col-span-8">
                        {selectedIcp ? (
                            <LuxeCard className="p-8 space-y-8">
                                {/* Editable Name */}
                                <div className="space-y-4">
                                    <LuxeInput
                                        label="ICP Name"
                                        value={selectedIcp.name}
                                        onChange={(e) => updateIcpName(selectedIcp.id, e.target.value)}
                                        className="text-xl font-display"
                                    />
                                    <p className="text-sm" style={{ color: 'var(--ink-soft)' }}>
                                        {selectedIcp.label}
                                    </p>
                                </div>

                                {/* Firmographics */}
                                <div className="space-y-4 pt-6" style={{ borderTop: '1px solid var(--border-subtle)' }}>
                                    <h4 className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--ink-soft)' }}>
                                        Who they are
                                    </h4>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-xs font-semibold mb-1" style={{ color: 'var(--ink-soft)' }}>Company Size</p>
                                            <p className="text-sm" style={{ color: 'var(--ink-strong)' }}>{selectedIcp.firmographics.companySize}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs font-semibold mb-1" style={{ color: 'var(--ink-soft)' }}>Stage</p>
                                            <p className="text-sm" style={{ color: 'var(--ink-strong)' }}>{selectedIcp.firmographics.stage}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs font-semibold mb-1" style={{ color: 'var(--ink-soft)' }}>Geography</p>
                                            <p className="text-sm" style={{ color: 'var(--ink-strong)' }}>{selectedIcp.firmographics.geography}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs font-semibold mb-1" style={{ color: 'var(--ink-soft)' }}>Team Size</p>
                                            <p className="text-sm" style={{ color: 'var(--ink-strong)' }}>{selectedIcp.firmographics.teamSize}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Psychographics */}
                                <div className="space-y-4 pt-6" style={{ borderTop: '1px solid var(--border-subtle)' }}>
                                    <h4 className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--ink-soft)' }}>
                                        How they think
                                    </h4>
                                    <div className="space-y-4">
                                        <div>
                                            <p className="text-xs font-semibold mb-2" style={{ color: 'var(--ink-soft)' }}>Motivations</p>
                                            <div className="flex flex-wrap gap-2">
                                                {selectedIcp.psychographics.motivations.map((m, i) => (
                                                    <span key={i} className="text-xs px-3 py-1 rounded-full" style={{ backgroundColor: '#F5F5F5', color: 'var(--ink-strong)' }}>
                                                        {m}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-xs font-semibold mb-2" style={{ color: 'var(--ink-soft)' }}>Fears</p>
                                            <div className="flex flex-wrap gap-2">
                                                {selectedIcp.psychographics.fears.map((f, i) => (
                                                    <span key={i} className="text-xs px-3 py-1 rounded-full" style={{ backgroundColor: '#F5F5F5', color: 'var(--ink-strong)' }}>
                                                        {f}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-xs font-semibold mb-2" style={{ color: 'var(--ink-soft)' }}>Worldview</p>
                                            <p className="text-sm leading-relaxed" style={{ color: 'var(--ink-strong)' }}>
                                                {selectedIcp.psychographics.worldview}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Buying Signals */}
                                <div className="space-y-4 pt-6" style={{ borderTop: '1px solid var(--border-subtle)' }}>
                                    <h4 className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--ink-soft)' }}>
                                        How they buy
                                    </h4>
                                    <div className="space-y-4">
                                        <div>
                                            <p className="text-xs font-semibold mb-2" style={{ color: 'var(--ink-soft)' }}>Primary Channels</p>
                                            <div className="flex flex-wrap gap-2">
                                                {selectedIcp.buyingSignals.channels.map((c, i) => (
                                                    <span key={i} className="text-xs px-3 py-1 rounded-full" style={{ backgroundColor: '#F5F5F5', color: 'var(--ink-strong)' }}>
                                                        {c}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-xs font-semibold mb-2" style={{ color: 'var(--ink-soft)' }}>Buying Triggers</p>
                                            <ul className="space-y-1">
                                                {selectedIcp.buyingSignals.triggers.map((t, i) => (
                                                    <li key={i} className="text-sm flex items-start gap-2" style={{ color: 'var(--ink-strong)' }}>
                                                        <span className="w-1 h-1 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: 'var(--ink-soft)' }}></span>
                                                        {t}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                        <div>
                                            <p className="text-xs font-semibold mb-2" style={{ color: 'var(--ink-soft)' }}>Common Objections</p>
                                            <ul className="space-y-1">
                                                {selectedIcp.buyingSignals.objections.map((o, i) => (
                                                    <li key={i} className="text-sm flex items-start gap-2" style={{ color: 'var(--ink-strong)' }}>
                                                        <span className="w-1 h-1 rounded-full mt-2 flex-shrink-0" style={{ backgroundColor: 'var(--ink-soft)' }}></span>
                                                        {o}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </LuxeCard>
                        ) : (
                            <div className="h-full flex items-center justify-center" style={{ color: 'var(--ink-soft)' }}>
                                Select an ICP to view details
                            </div>
                        )}
                    </div>
                </div>

                {/* Controls */}
                <div className="flex justify-between items-center pt-8 mt-8" style={{ borderTop: '1px solid var(--border-subtle)' }}>
                    <LuxeButton variant="ghost" onClick={onBack}>
                        <ArrowLeft className="mr-2 w-4 h-4" /> Back
                    </LuxeButton>
                    <LuxeButton
                        onClick={handleFinish}
                        disabled={icps.filter(icp => icp.keep).length === 0}
                        size="lg"
                    >
                        Save Tribes & Finish <Check className="ml-2 w-4 h-4" />
                    </LuxeButton>
                </div>
            </div>
        </motion.div>
    );
};

export default Act3Tribes;
