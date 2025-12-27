'use client';

import React, { useState } from 'react';
import {
    Target,
    Eye,
    ChevronRight,
    Check,
    AlertCircle,
    FileText,
    BarChart3,
    Layers,
    GitCompare
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Phase4Data } from '@/lib/foundation';

interface PositioningStudioHomeProps {
    phase4: Phase4Data;
    onNavigate: (screen: string) => void;
    onShowEvidence: (claimId: string) => void;
}

interface SectionStatus {
    id: string;
    label: string;
    status: 'complete' | 'needs-review' | 'missing';
}

export function PositioningStudioHome({
    phase4,
    onNavigate,
    onShowEvidence
}: PositioningStudioHomeProps) {
    const [activeEvidencePanel, setActiveEvidencePanel] = useState<string | null>(null);

    // Calculate section statuses
    const getSectionStatuses = (): SectionStatus[] => {
        const statuses: SectionStatus[] = [
            {
                id: 'market-frame',
                label: 'Market Frame',
                status: phase4.marketCategory?.primary ? 'complete' : 'missing'
            },
            {
                id: 'alternatives',
                label: 'Alternatives',
                status: (phase4.competitiveAlternatives?.statusQuo?.length || 0) > 0 ? 'complete' : 'missing'
            },
            {
                id: 'attributes',
                label: 'Differentiation',
                status: (phase4.uniqueAttributes?.length || 0) > 0 ? 'complete' : 'missing'
            },
            {
                id: 'value',
                label: 'Value Translation',
                status: (phase4.valueClaims?.length || 0) > 0 ? 'complete' : 'missing'
            },
            {
                id: 'who-cares',
                label: 'Who Cares',
                status: (phase4.whoCareSegments?.filter(s => s.rank !== 'unranked')?.length || 0) > 0 ? 'complete' : 'missing'
            },
            {
                id: 'statement',
                label: 'Statement',
                status: phase4.positioningStatement ? 'complete' : 'missing'
            },
            {
                id: 'maps',
                label: 'Visual Maps',
                status: (phase4.visuals?.perceptualMap?.points?.length || 0) > 0 ? 'complete' : 'missing'
            },
            {
                id: 'proof',
                label: 'Proof Stack',
                status: (phase4.proofIntegrity?.filter(p => !p.needsFix)?.length || 0) > 0 ? 'complete' :
                    (phase4.proofIntegrity?.some(p => p.needsFix) ? 'needs-review' : 'missing')
            }
        ];
        return statuses;
    };

    const sectionStatuses = getSectionStatuses();
    const completedCount = sectionStatuses.filter(s => s.status === 'complete').length;
    const confidenceScore = phase4.confidenceScore || Math.round((completedCount / sectionStatuses.length) * 100);

    // Build positioning statement preview
    const positioningPreview = phase4.positioningStatement ||
        `For [${phase4.whoCareSegments?.[0]?.name || 'target segment'}], ${phase4.marketCategory?.primary || '[product]'} is a [category] that delivers [value], unlike [alternative], because [mechanism].`;

    // Get weak claims that need fixing
    const weakClaims = phase4.proofIntegrity?.filter(p => p.needsFix) || [];

    return (
        <div className="min-h-screen bg-[#F3F4EE]">
            <div className="flex">
                {/* Left Rail - Section Navigation */}
                <div className="w-64 border-r border-[#C0C1BE] bg-white p-6 min-h-screen">
                    <div className="mb-8">
                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                            Positioning Pack
                        </span>
                        <h2 className="font-serif text-xl text-[#2D3538] mt-1">Draft v1</h2>
                    </div>

                    <div className="space-y-2">
                        {sectionStatuses.map((section) => (
                            <button
                                key={section.id}
                                onClick={() => onNavigate(section.id)}
                                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#F3F4EE] transition-colors text-left group"
                            >
                                <div className={`w-2.5 h-2.5 rounded-full ${section.status === 'complete' ? 'bg-[#2D3538]' :
                                        section.status === 'needs-review' ? 'bg-amber-500' :
                                            'bg-[#C0C1BE]'
                                    }`} />
                                <span className="text-sm text-[#2D3538] flex-1">{section.label}</span>
                                <ChevronRight className="w-4 h-4 text-[#9D9F9F] opacity-0 group-hover:opacity-100 transition-opacity" />
                            </button>
                        ))}
                    </div>

                    {/* Confidence Meter */}
                    <div className="mt-10 pt-6 border-t border-[#E5E6E3]">
                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                            Confidence
                        </span>
                        <div className="mt-3 flex items-center gap-3">
                            <div className="flex-1 h-2 bg-[#E5E6E3] rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-[#2D3538] rounded-full transition-all duration-500"
                                    style={{ width: `${confidenceScore}%` }}
                                />
                            </div>
                            <span className="text-sm font-medium text-[#2D3538]">{confidenceScore}%</span>
                        </div>
                    </div>
                </div>

                {/* Main Panel */}
                <div className="flex-1 p-10 max-w-4xl">
                    {/* Your Current Position */}
                    <section className="mb-10">
                        <h1 className="font-serif text-4xl text-[#2D3538] mb-2">
                            Your Current Position
                        </h1>
                        <p className="text-[#5B5F61] mb-6">Draft positioning derived from your inputs</p>

                        <div className="bg-[#2D3538] rounded-3xl p-10">
                            <div className="flex items-center gap-2 mb-4">
                                <Target className="w-5 h-5 text-white/60" />
                                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/60">
                                    Positioning Statement
                                </span>
                            </div>
                            <p className="font-serif text-[26px] text-white leading-[1.4]">
                                "{positioningPreview}"
                            </p>
                            <div className="mt-6 flex items-center gap-4">
                                <Button
                                    variant="ghost"
                                    onClick={() => onNavigate('statement')}
                                    className="text-white/80 hover:text-white hover:bg-white/10"
                                >
                                    Edit Statement
                                </Button>
                                <button
                                    onClick={() => setActiveEvidencePanel('statement')}
                                    className="text-xs text-white/60 hover:text-white/80 transition-colors"
                                >
                                    Show Evidence →
                                </button>
                            </div>
                        </div>
                    </section>

                    {/* Competitive Reality Snapshot */}
                    <section className="mb-10">
                        <div className="flex items-center gap-2 mb-4">
                            <GitCompare className="w-5 h-5 text-[#5B5F61]" />
                            <h2 className="font-serif text-2xl text-[#2D3538]">Competitive Reality</h2>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            {/* Status Quo */}
                            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-5">
                                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                    Status Quo
                                </span>
                                <p className="mt-2 text-sm text-[#2D3538]">
                                    {phase4.competitiveAlternatives?.statusQuo?.[0]?.name || 'Manual processes & spreadsheets'}
                                </p>
                                <p className="mt-1 text-xs text-[#5B5F61]">
                                    {phase4.competitiveAlternatives?.statusQuo?.length || 0} alternatives
                                </p>
                            </div>

                            {/* Indirect */}
                            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-5">
                                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                    Indirect
                                </span>
                                <p className="mt-2 text-sm text-[#2D3538]">
                                    {phase4.competitiveAlternatives?.indirect?.[0]?.name || 'Agencies & freelancers'}
                                </p>
                                <p className="mt-1 text-xs text-[#5B5F61]">
                                    {phase4.competitiveAlternatives?.indirect?.length || 0} alternatives
                                </p>
                            </div>

                            {/* Direct */}
                            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-5">
                                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                                    Direct
                                </span>
                                <p className="mt-2 text-sm text-[#2D3538]">
                                    {phase4.competitiveAlternatives?.direct?.[0]?.name || 'Competing tools'}
                                </p>
                                <p className="mt-1 text-xs text-[#5B5F61]">
                                    {phase4.competitiveAlternatives?.direct?.length || 0} competitors
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* Top Differentiators */}
                    <section className="mb-10">
                        <div className="flex items-center gap-2 mb-4">
                            <Layers className="w-5 h-5 text-[#5B5F61]" />
                            <h2 className="font-serif text-2xl text-[#2D3538]">Top Differentiators</h2>
                        </div>

                        <div className="space-y-3">
                            {(phase4.uniqueAttributes?.slice(0, 5) || []).map((attr, i) => (
                                <div
                                    key={attr.id}
                                    className="bg-white border border-[#E5E6E3] rounded-xl p-4 flex items-center gap-4"
                                >
                                    <div className="w-8 h-8 bg-[#F3F4EE] rounded-full flex items-center justify-center">
                                        <span className="font-serif text-sm text-[#2D3538]">{i + 1}</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm text-[#2D3538] font-medium">{attr.attribute}</p>
                                        <p className="text-xs text-[#5B5F61]">{attr.type} • {attr.copyability} to copy</p>
                                    </div>
                                    {attr.evidenceIds.length > 0 ? (
                                        <Check className="w-4 h-4 text-[#2D3538]" />
                                    ) : (
                                        <AlertCircle className="w-4 h-4 text-amber-500" />
                                    )}
                                </div>
                            ))}

                            {(phase4.uniqueAttributes?.length || 0) === 0 && (
                                <div className="bg-white/50 border border-dashed border-[#C0C1BE] rounded-xl p-6 text-center">
                                    <p className="text-sm text-[#5B5F61]">No differentiators defined yet</p>
                                    <Button
                                        variant="ghost"
                                        onClick={() => onNavigate('attributes')}
                                        className="mt-2 text-[#2D3538]"
                                    >
                                        Add Differentiators
                                    </Button>
                                </div>
                            )}
                        </div>
                    </section>

                    {/* Visuals Ready */}
                    <section className="mb-10">
                        <div className="flex items-center gap-2 mb-4">
                            <BarChart3 className="w-5 h-5 text-[#5B5F61]" />
                            <h2 className="font-serif text-2xl text-[#2D3538]">Visuals Ready</h2>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            {/* Perceptual Map Preview */}
                            <button
                                onClick={() => onNavigate('perceptual-map')}
                                className="bg-white border border-[#E5E6E3] rounded-2xl p-5 text-left hover:border-[#2D3538] transition-colors group"
                            >
                                <div className="w-full aspect-square bg-[#F3F4EE] rounded-xl mb-3 flex items-center justify-center">
                                    <div className="w-12 h-12 relative">
                                        <div className="absolute inset-0 border border-[#C0C1BE]" />
                                        <div className="absolute left-1/3 top-1/4 w-2 h-2 bg-[#2D3538] rounded-full" />
                                        <div className="absolute right-1/4 bottom-1/3 w-2 h-2 bg-[#C0C1BE] rounded-full" />
                                    </div>
                                </div>
                                <span className="text-sm text-[#2D3538] font-medium group-hover:underline">
                                    Perceptual Map
                                </span>
                                <p className="text-xs text-[#5B5F61] mt-1">
                                    {phase4.visuals?.perceptualMap?.points?.length || 0} plotted
                                </p>
                            </button>

                            {/* Attribute Ladder Preview */}
                            <button
                                onClick={() => onNavigate('attribute-ladder')}
                                className="bg-white border border-[#E5E6E3] rounded-2xl p-5 text-left hover:border-[#2D3538] transition-colors group"
                            >
                                <div className="w-full aspect-square bg-[#F3F4EE] rounded-xl mb-3 flex items-center justify-center">
                                    <div className="space-y-1">
                                        {[1, 2, 3].map((i) => (
                                            <div key={i} className={`h-2 rounded bg-[#C0C1BE] ${i === 1 ? 'w-8' : i === 2 ? 'w-6' : 'w-4'}`} />
                                        ))}
                                    </div>
                                </div>
                                <span className="text-sm text-[#2D3538] font-medium group-hover:underline">
                                    Attribute Ladder
                                </span>
                                <p className="text-xs text-[#5B5F61] mt-1">
                                    {phase4.attributeLadder?.rungs?.length || 0} rungs
                                </p>
                            </button>

                            {/* Strategy Canvas Preview */}
                            <button
                                onClick={() => onNavigate('strategy-canvas')}
                                className="bg-white border border-[#E5E6E3] rounded-2xl p-5 text-left hover:border-[#2D3538] transition-colors group"
                            >
                                <div className="w-full aspect-square bg-[#F3F4EE] rounded-xl mb-3 flex items-center justify-center">
                                    <div className="flex items-end gap-1 h-10">
                                        {[3, 5, 2, 4, 3].map((h, i) => (
                                            <div key={i} className="w-2 bg-[#C0C1BE] rounded-t" style={{ height: `${h * 6}px` }} />
                                        ))}
                                    </div>
                                </div>
                                <span className="text-sm text-[#2D3538] font-medium group-hover:underline">
                                    Strategy Canvas
                                </span>
                                <p className="text-xs text-[#5B5F61] mt-1">
                                    {phase4.visuals?.strategyCanvas?.factors?.length || 0} factors
                                </p>
                            </button>
                        </div>
                    </section>

                    {/* Fix What's Weak */}
                    {weakClaims.length > 0 && (
                        <section className="mb-10">
                            <div className="flex items-center gap-2 mb-4">
                                <AlertCircle className="w-5 h-5 text-amber-500" />
                                <h2 className="font-serif text-2xl text-[#2D3538]">Fix What's Weak</h2>
                            </div>

                            <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6">
                                <div className="space-y-4">
                                    {weakClaims.slice(0, 3).map((claim) => (
                                        <div key={claim.id} className="flex items-start gap-3">
                                            <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                                            <div className="flex-1">
                                                <p className="text-sm text-[#2D3538]">{claim.claimText}</p>
                                                <p className="text-xs text-amber-700 mt-1">
                                                    {claim.isHypothesis ? 'Marked as hypothesis' : 'No proof attached'}
                                                </p>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => onNavigate('proof')}
                                                className="text-amber-700 hover:text-amber-900"
                                            >
                                                Fix
                                            </Button>
                                        </div>
                                    ))}
                                </div>

                                {weakClaims.length > 3 && (
                                    <button
                                        onClick={() => onNavigate('proof')}
                                        className="mt-4 text-sm text-amber-700 hover:text-amber-900"
                                    >
                                        +{weakClaims.length - 3} more issues →
                                    </button>
                                )}
                            </div>
                        </section>
                    )}
                </div>

                {/* Right Panel - Evidence Drawer */}
                <div className="w-80 border-l border-[#C0C1BE] bg-white p-6 min-h-screen">
                    <div className="flex items-center gap-2 mb-6">
                        <Eye className="w-4 h-4 text-[#5B5F61]" />
                        <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                            Evidence Drawer
                        </span>
                    </div>

                    {activeEvidencePanel ? (
                        <div className="space-y-4">
                            <p className="text-xs text-[#5B5F61]">
                                Showing sources for: <strong>{activeEvidencePanel}</strong>
                            </p>

                            {phase4.evidenceGraph?.filter(e => e.claimId === activeEvidencePanel).map((evidence) => (
                                <div
                                    key={evidence.id}
                                    className="bg-[#F3F4EE] rounded-xl p-4"
                                >
                                    <div className="flex items-center gap-2 mb-2">
                                        <FileText className="w-3 h-3 text-[#5B5F61]" />
                                        <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                                            {evidence.sourceType}
                                        </span>
                                    </div>
                                    <p className="text-sm text-[#2D3538] italic">
                                        "{evidence.snippet}"
                                    </p>
                                    <p className="text-xs text-[#5B5F61] mt-2">
                                        From Phase {evidence.phaseOrigin}
                                    </p>
                                </div>
                            ))}

                            {(!phase4.evidenceGraph || phase4.evidenceGraph.filter(e => e.claimId === activeEvidencePanel).length === 0) && (
                                <p className="text-sm text-[#5B5F61]">No evidence found for this claim.</p>
                            )}

                            <button
                                onClick={() => setActiveEvidencePanel(null)}
                                className="text-xs text-[#5B5F61] hover:text-[#2D3538]"
                            >
                                Clear selection
                            </button>
                        </div>
                    ) : (
                        <div className="text-center py-10">
                            <Eye className="w-8 h-8 text-[#C0C1BE] mx-auto mb-3" />
                            <p className="text-sm text-[#5B5F61]">
                                Click "Show Evidence" on any card to see supporting sources.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
