'use client';

import React from 'react';
import { Icp } from '@/types/icp-types';
import { ArrowRight, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';

interface ICPEvolutionProposalProps {
    currentIcp: Icp;
    proposedChanges: Partial<Icp>;
    impact: {
        confidenceDelta: number;
        reason: string;
    };
    onAccept: () => void;
    onReject: () => void;
}

export default function ICPEvolutionProposal({
    currentIcp,
    proposedChanges,
    impact,
    onAccept,
    onReject
}: ICPEvolutionProposalProps) {
    const newConfidence = Math.min(0.99, currentIcp.confidenceScore + impact.confidenceDelta);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden"
            >
                {/* Header */}
                <div className="bg-[#2D3538] text-white p-8">
                    <h2 className="font-serif text-2xl mb-2">Proposed Targeting Refinement</h2>
                    <p className="text-white/70 text-sm">
                        Based on your input: <span className="italic">"{impact.reason}"</span>
                    </p>
                </div>

                {/* Diff Content */}
                <div className="p-8 space-y-8">
                    {/* Impact Stats */}
                    <div className="flex items-center gap-8 p-4 bg-[#F3F4EE] rounded-xl border border-[#C0C1BE]/30">
                        <div>
                            <div className="text-xs uppercase font-bold text-[#9D9F9F]">Confidence Impact</div>
                            <div className="flex items-center gap-2 mt-1">
                                <span className="text-xl font-serif text-[#5B5F61]">{(currentIcp.confidenceScore * 100).toFixed(0)}%</span>
                                <ArrowRight className="w-4 h-4 text-[#9D9F9F]" />
                                <span className="text-xl font-serif text-emerald-600 font-bold">{(newConfidence * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                        <div>
                            <div className="text-xs uppercase font-bold text-[#9D9F9F]">Muse Adaptation</div>
                            <div className="flex items-center gap-2 mt-1">
                                <span className="text-sm font-medium text-[#2D3538]">More Technical</span>
                            </div>
                        </div>
                    </div>

                    {/* The Changes */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-bold uppercase text-[#9D9F9F]">Suggested Changes</h3>

                        {/* Mock Diff - In a real app this would iterate over keys */}
                        {proposedChanges.psycholinguistics?.tonePreference && (
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div className="p-3 rounded-lg border border-red-100 bg-red-50/50 text-red-900 opacity-70 decoration-slice">
                                    <div className="text-xs font-bold mb-1 text-red-700">CURRENT</div>
                                    {currentIcp.psycholinguistics.tonePreference.join(', ')}
                                </div>
                                <div className="p-3 rounded-lg border border-emerald-100 bg-emerald-50 text-emerald-900 font-medium">
                                    <div className="text-xs font-bold mb-1 text-emerald-700">PROPOSED</div>
                                    {proposedChanges.psycholinguistics.tonePreference.join(', ')}
                                </div>
                            </div>
                        )}
                        {proposedChanges.firmographics?.companyType && (
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div className="p-3 rounded-lg border border-red-100 bg-red-50/50 text-red-900 opacity-70">
                                    <div className="text-xs font-bold mb-1 text-red-700">CURRENT</div>
                                    {currentIcp.firmographics.companyType.join(', ')}
                                </div>
                                <div className="p-3 rounded-lg border border-emerald-100 bg-emerald-50 text-emerald-900 font-medium">
                                    <div className="text-xs font-bold mb-1 text-emerald-700">PROPOSED</div>
                                    {proposedChanges.firmographics.companyType.join(', ')}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer Actions */}
                <div className="p-6 bg-[#F3F4EE] border-t border-[#C0C1BE]/30 flex justify-between items-center">
                    <button
                        onClick={onReject}
                        className="text-[#5B5F61] font-medium px-4 py-2 hover:bg-white rounded-lg transition-colors"
                    >
                        Keep current targeting
                    </button>
                    <button
                        onClick={onAccept}
                        className="bg-[#2D3538] text-white px-6 py-3 rounded-xl font-medium shadow-sm hover:bg-black transition-colors flex items-center gap-2"
                    >
                        Apply Update <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
            </motion.div>
        </div>
    );
}
