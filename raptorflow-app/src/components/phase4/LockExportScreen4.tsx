'use client';

import React, { useState } from 'react';
import {
    Lock,
    Download,
    ArrowRight,
    Check,
    AlertCircle,
    FileText,
    Code,
    Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Phase4Data } from '@/lib/foundation';

interface LockExportScreenProps {
    phase4: Phase4Data;
    onLock: () => void;
    onBack: () => void;
}

export function LockExportScreen({
    phase4,
    onLock,
    onBack
}: LockExportScreenProps) {
    const [isExporting, setIsExporting] = useState<'pdf' | 'json' | null>(null);

    // Calculate what's complete vs uncertain
    const getCompletionStatus = () => {
        const completed: string[] = [];
        const uncertain: string[] = [];

        if (phase4.marketCategory?.primary) {
            completed.push(`Category: ${phase4.marketCategory.primary}`);
        } else {
            uncertain.push('No market category selected');
        }

        if ((phase4.competitiveAlternatives?.direct?.length || 0) > 0) {
            completed.push(`${phase4.competitiveAlternatives?.direct?.length} direct competitors mapped`);
        }

        if ((phase4.uniqueAttributes?.length || 0) > 0) {
            completed.push(`${phase4.uniqueAttributes?.length} unique attributes defined`);
        } else {
            uncertain.push('No unique attributes defined');
        }

        if ((phase4.valueClaims?.filter(c => c.isSelected)?.length || 0) > 0) {
            completed.push(`${phase4.valueClaims?.filter(c => c.isSelected)?.length} value claims selected`);
        }

        if (phase4.whoCareSegments?.find(s => s.rank === 'primary')) {
            completed.push(`Primary segment: ${phase4.whoCareSegments.find(s => s.rank === 'primary')?.name}`);
        } else {
            uncertain.push('No primary segment selected');
        }

        if (phase4.positioningStatement) {
            completed.push('Positioning statement locked');
        } else {
            uncertain.push('No positioning statement defined');
        }

        if ((phase4.visuals?.perceptualMap?.points?.length || 0) > 2) {
            completed.push('Perceptual map created');
        }

        const proofItems = phase4.proofIntegrity || [];
        const unprovenClaims = proofItems.filter(p => p.needsFix);
        if (unprovenClaims.length > 0) {
            uncertain.push(`${unprovenClaims.length} claims without proof`);
        }

        return { completed, uncertain };
    };

    const { completed, uncertain } = getCompletionStatus();
    const confidenceScore = phase4.confidenceScore || Math.round((completed.length / (completed.length + uncertain.length)) * 100);

    const handleExport = async (type: 'pdf' | 'json') => {
        setIsExporting(type);
        // Simulate export
        await new Promise(resolve => setTimeout(resolve, 1500));

        if (type === 'json') {
            const blob = new Blob([JSON.stringify(phase4, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'positioning-pack.json';
            a.click();
            URL.revokeObjectURL(url);
        }

        setIsExporting(null);
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center max-w-xl mx-auto">
                <div className="w-16 h-16 bg-[#2D3538] rounded-full flex items-center justify-center mx-auto mb-6">
                    <Lock className="w-8 h-8 text-white" />
                </div>
                <h2 className="font-serif text-3xl text-[#2D3538] mb-3">
                    Lock Your Positioning
                </h2>
                <p className="text-[#5B5F61]">
                    This will become your marketing OS source of truth.
                    All agents will use this positioning pack for content and campaigns.
                </p>
            </div>

            {/* Confidence Score */}
            <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6 max-w-xl mx-auto">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-[#5B5F61]">Positioning Confidence</span>
                    <span className={`text-2xl font-serif ${confidenceScore > 70 ? 'text-green-600' :
                            confidenceScore > 50 ? 'text-amber-600' :
                                'text-red-600'
                        }`}>
                        {confidenceScore}%
                    </span>
                </div>
                <div className="h-2 bg-[#E5E6E3] rounded-full overflow-hidden">
                    <div
                        className={`h-full rounded-full transition-all ${confidenceScore > 70 ? 'bg-green-500' :
                                confidenceScore > 50 ? 'bg-amber-500' :
                                    'bg-red-500'
                            }`}
                        style={{ width: `${confidenceScore}%` }}
                    />
                </div>
            </div>

            {/* What's Complete */}
            <div className="grid grid-cols-2 gap-6 max-w-3xl mx-auto">
                <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Check className="w-5 h-5 text-green-500" />
                        <h3 className="font-medium text-[#2D3538]">Complete</h3>
                    </div>
                    <ul className="space-y-2">
                        {completed.map((item, i) => (
                            <li key={i} className="text-sm text-[#5B5F61] flex items-start gap-2">
                                <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <AlertCircle className="w-5 h-5 text-amber-500" />
                        <h3 className="font-medium text-[#2D3538]">Uncertain</h3>
                    </div>
                    {uncertain.length > 0 ? (
                        <ul className="space-y-2">
                            {uncertain.map((item, i) => (
                                <li key={i} className="text-sm text-amber-700 flex items-start gap-2">
                                    <AlertCircle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-sm text-[#5B5F61]">Everything looks good!</p>
                    )}
                </div>
            </div>

            {/* Export Options */}
            <div className="max-w-xl mx-auto">
                <h3 className="font-serif text-lg text-[#2D3538] mb-4 text-center">Export Options</h3>
                <div className="grid grid-cols-3 gap-4">
                    <button
                        onClick={() => handleExport('pdf')}
                        disabled={isExporting !== null}
                        className="bg-white border border-[#E5E6E3] rounded-xl p-4 hover:border-[#2D3538] transition-colors text-center"
                    >
                        <FileText className="w-6 h-6 text-[#5B5F61] mx-auto mb-2" />
                        <span className="text-sm text-[#2D3538] block">
                            {isExporting === 'pdf' ? 'Generating...' : 'Positioning Pack PDF'}
                        </span>
                    </button>
                    <button
                        onClick={() => handleExport('json')}
                        disabled={isExporting !== null}
                        className="bg-white border border-[#E5E6E3] rounded-xl p-4 hover:border-[#2D3538] transition-colors text-center"
                    >
                        <Code className="w-6 h-6 text-[#5B5F61] mx-auto mb-2" />
                        <span className="text-sm text-[#2D3538] block">
                            {isExporting === 'json' ? 'Exporting...' : 'Agent JSON'}
                        </span>
                    </button>
                    <button
                        disabled
                        className="bg-[#F3F4EE] border border-dashed border-[#C0C1BE] rounded-xl p-4 opacity-50 text-center"
                    >
                        <Sparkles className="w-6 h-6 text-[#9D9F9F] mx-auto mb-2" />
                        <span className="text-sm text-[#9D9F9F] block">Embeddings (auto)</span>
                    </button>
                </div>
            </div>

            {/* Lock Button */}
            <div className="flex flex-col items-center gap-4 pt-6 border-t border-[#E5E6E3] max-w-xl mx-auto">
                <Button
                    onClick={onLock}
                    size="lg"
                    className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-12 py-6 rounded-2xl text-lg font-medium transition-all hover:scale-[1.02]"
                >
                    <Lock className="w-5 h-5 mr-2" />
                    Lock & Continue to Phase 5
                    <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <p className="text-xs text-[#9D9F9F]">
                    You can always unlock and edit later from the Foundation dashboard.
                </p>
            </div>

            {/* Back Button */}
            <div className="text-center">
                <Button
                    variant="ghost"
                    onClick={onBack}
                    className="text-[#5B5F61]"
                >
                    Back to make changes
                </Button>
            </div>
        </div>
    );
}
