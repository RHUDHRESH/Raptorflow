'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { FadeIn, Stagger } from '@/components/ui/motion';
import { useIcpStore } from '@/lib/icp-store';
import { loadFoundation, DerivedICP } from '@/lib/foundation';
import { useState, useEffect } from 'react';
import { ArrowRight, Users, Target, Brain, TrendingUp, Shield } from 'lucide-react';
import Link from 'next/link';

export default function CohortsPage() {
    const icps = useIcpStore((state) => state.icps);
    const activeIcpId = useIcpStore((state) => state.activeIcpId);
    const setActiveIcp = useIcpStore((state) => state.setActiveIcp);
    const [selectedIcp, setSelectedIcp] = useState<DerivedICP | null>(null);

    useEffect(() => {
        // Select the first ICP if none selected
        if (icps.length > 0 && !selectedIcp) {
            const active = icps.find(i => i.id === activeIcpId) || icps[0];
            setSelectedIcp(active);
        }
    }, [icps, activeIcpId, selectedIcp]);

    const handleSelectIcp = (icp: DerivedICP) => {
        setSelectedIcp(icp);
        setActiveIcp(icp.id);
    };

    if (icps.length === 0) {
        return (
            <AppLayout>
                <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-8">
                    <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center mb-6">
                        <Users className="w-10 h-10 text-muted-foreground" />
                    </div>
                    <h1 className="font-serif text-4xl mb-4">No ICPs Generated Yet</h1>
                    <p className="text-muted-foreground max-w-md mb-8">
                        Complete your Foundation to generate AI-derived Ideal Customer Profiles.
                    </p>
                    <Link
                        href="/foundation"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors"
                    >
                        Complete Foundation <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
            </AppLayout>
        );
    }

    return (
        <AppLayout>
            <Stagger className="flex flex-col gap-12 pb-24">
                {/* Header */}
                <FadeIn>
                    <section className="pt-8">
                        <span className="text-xs font-semibold tracking-widest uppercase text-muted-foreground mb-3 block">
                            Cohorts
                        </span>
                        <h1 className="font-serif text-5xl tracking-tight text-foreground mb-4">
                            Your Ideal Customers
                        </h1>
                        <p className="text-lg text-muted-foreground max-w-2xl">
                            AI-derived customer profiles based on your Foundation data. Each ICP includes
                            behavioral depth, buying patterns, and engagement strategies.
                        </p>
                    </section>
                </FadeIn>

                {/* ICP Cards Grid */}
                <FadeIn delay={1}>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {icps.map((icp) => (
                            <button
                                key={icp.id}
                                onClick={() => handleSelectIcp(icp)}
                                className={`text-left p-6 rounded-2xl border transition-all duration-300 hover:-translate-y-1 hover:shadow-lg ${selectedIcp?.id === icp.id
                                        ? 'border-primary bg-primary/5 shadow-md'
                                        : 'border-border bg-card hover:border-border/80'
                                    }`}
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <span className={`text-xs font-mono px-2.5 py-1 rounded-full ${icp.priority === 'primary'
                                            ? 'bg-emerald-100 text-emerald-700'
                                            : icp.priority === 'secondary'
                                                ? 'bg-blue-100 text-blue-700'
                                                : 'bg-muted text-muted-foreground'
                                        }`}>
                                        {icp.priority}
                                    </span>
                                    <span className="text-xs font-mono text-muted-foreground">
                                        {Math.round(icp.confidence * 100)}% confidence
                                    </span>
                                </div>
                                <h3 className="font-display text-xl font-medium mb-2">{icp.name}</h3>
                                <p className="text-sm text-muted-foreground line-clamp-2">{icp.description}</p>
                            </button>
                        ))}
                    </div>
                </FadeIn>

                {/* Selected ICP Detail */}
                {selectedIcp && (
                    <FadeIn delay={2}>
                        <div className="border border-border rounded-2xl bg-card overflow-hidden">
                            {/* ICP Header */}
                            <div className="p-8 border-b border-border bg-muted/30">
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                                        <Target className="w-6 h-6 text-primary" />
                                    </div>
                                    <div>
                                        <h2 className="font-display text-2xl font-medium">{selectedIcp.name}</h2>
                                        <p className="text-sm text-muted-foreground">{selectedIcp.description}</p>
                                    </div>
                                </div>
                            </div>

                            {/* ICP Details Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-border">
                                {/* Firmographics */}
                                <div className="p-6 bg-card">
                                    <div className="flex items-center gap-2 mb-4">
                                        <Users className="w-4 h-4 text-muted-foreground" />
                                        <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">Firmographics</h3>
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <span className="text-xs text-muted-foreground">Company Size</span>
                                            <p className="font-medium">{selectedIcp.firmographics.companySize}</p>
                                        </div>
                                        <div>
                                            <span className="text-xs text-muted-foreground">Industry</span>
                                            <p className="font-medium">{selectedIcp.firmographics.industry.join(', ')}</p>
                                        </div>
                                        <div>
                                            <span className="text-xs text-muted-foreground">Geography</span>
                                            <p className="font-medium">{selectedIcp.firmographics.geography.join(', ')}</p>
                                        </div>
                                        <div>
                                            <span className="text-xs text-muted-foreground">Budget</span>
                                            <p className="font-medium">{selectedIcp.firmographics.budget}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Pain Map */}
                                <div className="p-6 bg-card">
                                    <div className="flex items-center gap-2 mb-4">
                                        <TrendingUp className="w-4 h-4 text-muted-foreground" />
                                        <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">Pain Map</h3>
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <span className="text-xs text-muted-foreground">Primary Pain</span>
                                            <p className="font-medium text-red-600">{selectedIcp.painMap.primary}</p>
                                        </div>
                                        <div>
                                            <span className="text-xs text-muted-foreground">Secondary Pains</span>
                                            <div className="flex flex-wrap gap-2 mt-1">
                                                {selectedIcp.painMap.secondary.map((pain, i) => (
                                                    <span key={i} className="text-xs bg-muted px-2 py-1 rounded">{pain}</span>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <span className="text-xs text-muted-foreground">Urgency</span>
                                            <span className={`ml-2 text-xs font-mono px-2 py-0.5 rounded ${selectedIcp.painMap.urgency === 'now' ? 'bg-red-100 text-red-700' :
                                                    selectedIcp.painMap.urgency === 'soon' ? 'bg-amber-100 text-amber-700' :
                                                        'bg-muted text-muted-foreground'
                                                }`}>
                                                {selectedIcp.painMap.urgency}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Social Presence */}
                                <div className="p-6 bg-card">
                                    <div className="flex items-center gap-2 mb-4">
                                        <Brain className="w-4 h-4 text-muted-foreground" />
                                        <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">Social Presence</h3>
                                    </div>
                                    <div className="space-y-3">
                                        {selectedIcp.social.platforms.map((platform, i) => (
                                            <div key={i}>
                                                <span className="text-xs text-muted-foreground">{platform.name}</span>
                                                <p className="text-sm">{platform.timing} — {platform.vibe}</p>
                                            </div>
                                        ))}
                                        <div>
                                            <span className="text-xs text-muted-foreground">Authorities They Trust</span>
                                            <p className="font-medium">{selectedIcp.social.authorities.join(', ')}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Buying Behavior */}
                                <div className="p-6 bg-card">
                                    <div className="flex items-center gap-2 mb-4">
                                        <Shield className="w-4 h-4 text-muted-foreground" />
                                        <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">Buying Behavior</h3>
                                    </div>
                                    <div className="space-y-3">
                                        <div>
                                            <span className="text-xs text-muted-foreground">Timeline</span>
                                            <p className="font-medium">{selectedIcp.buying.timeline}</p>
                                        </div>
                                        <div>
                                            <span className="text-xs text-muted-foreground">Buying Committee</span>
                                            <div className="space-y-1 mt-1">
                                                {selectedIcp.buying.committee.map((member, i) => (
                                                    <p key={i} className="text-sm"><strong>{member.role}:</strong> {member.focus}</p>
                                                ))}
                                            </div>
                                        </div>
                                        <div>
                                            <span className="text-xs text-muted-foreground">Proof Needed</span>
                                            <div className="flex flex-wrap gap-2 mt-1">
                                                {selectedIcp.buying.proofNeeded.map((proof, i) => (
                                                    <span key={i} className="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded">{proof}</span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Behavioral Economics */}
                            <div className="p-6 border-t border-border">
                                <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground mb-4">Behavioral De-Risking</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <span className="text-xs text-muted-foreground">Key Biases</span>
                                        <div className="space-y-2 mt-2">
                                            {selectedIcp.behavioral.biases.map((bias, i) => (
                                                <div key={i} className="p-3 bg-muted rounded-lg">
                                                    <p className="font-medium text-sm">{bias.name}</p>
                                                    <p className="text-xs text-muted-foreground">{bias.implication}</p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <div>
                                        <span className="text-xs text-muted-foreground">De-Risking Tactics</span>
                                        <div className="flex flex-wrap gap-2 mt-2">
                                            {selectedIcp.behavioral.deRisking.map((tactic, i) => (
                                                <span key={i} className="text-sm bg-blue-100 text-blue-700 px-3 py-1.5 rounded-lg">{tactic}</span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </FadeIn>
                )}

                {/* Next Steps */}
                <FadeIn delay={3}>
                    <div className="flex items-center gap-4 p-6 rounded-2xl border border-border bg-card">
                        <div className="flex-1">
                            <h3 className="font-display text-lg font-medium mb-1">Next: Positioning Engine</h3>
                            <p className="text-sm text-muted-foreground">Define your competitive positioning and messaging framework.</p>
                        </div>
                        <Link
                            href="/positioning"
                            className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors"
                        >
                            Continue <ArrowRight className="w-4 h-4" />
                        </Link>
                    </div>
                </FadeIn>
            </Stagger>
        </AppLayout>
    );
}
