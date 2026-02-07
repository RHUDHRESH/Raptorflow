'use client';

import { AppLayout } from '@/components/layout/AppLayout';
import { useState, useEffect } from 'react';
import { useIcpStore } from '@/lib/icp-store';
import { Icp } from '@/types/icp-types';
import { Users, ArrowRight, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function CohortsPage() {
    const icps = useIcpStore((state) => state.icps);
    const activeIcpId = useIcpStore((state) => state.activeIcpId);
    const setActiveIcp = useIcpStore((state) => state.setActiveIcp);
    const [selectedIcp, setSelectedIcp] = useState<Icp | null>(null);

    useEffect(() => {
        // Select the first ICP if none selected
        if (icps.length > 0 && !selectedIcp) {
            const active = icps.find(i => i.id === activeIcpId) || icps[0];
            setSelectedIcp(active);
        }
    }, [icps, activeIcpId, selectedIcp]);

    const handleSelectIcp = (icp: Icp) => {
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
            <div className="flex flex-col gap-12 pb-24">
                {/* Header */}
                <section className="pt-8">
                    <span className="text-xs font-semibold tracking-widest uppercase text-muted-foreground mb-3 block">
                        Cohorts
                    </span>
                    <h1 className="font-serif text-5xl tracking-tight text-foreground mb-4">
                        Your Ideal Customers
                    </h1>
                    <p className="text-lg text-muted-foreground max-w-2xl">
                        AI-derived customer profiles based on your Foundation data. Each ICP includes
                        firmographics, pain points, and engagement patterns.
                    </p>
                </section>

                {/* ICP Cards Grid */}
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
                                        : 'bg-blue-100 text-blue-700'
                                    }`}>
                                    {icp.priority}
                                </span>
                                <span className="text-xs font-mono text-muted-foreground">
                                    {Math.round(icp.confidenceScore * 100)}% confidence
                                </span>
                            </div>
                            <h3 className="font-display text-xl font-medium mb-2">{icp.name}</h3>
                            <p className="text-sm text-muted-foreground">
                                Status: {icp.status} • Created: {new Date(icp.createdAt).toLocaleDateString()}
                            </p>
                        </button>
                    ))}
                </div>

                {/* Selected ICP Detail */}
                {selectedIcp && (
                    <div className="border border-border rounded-2xl bg-card overflow-hidden">
                        {/* ICP Header */}
                        <div className="p-8 border-b border-border bg-muted/30">
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <Users className="w-6 h-6 text-primary" />
                                </div>
                                <div>
                                    <h2 className="font-display text-2xl font-medium">{selectedIcp.name}</h2>
                                    <p className="text-sm text-muted-foreground">
                                        Priority: {selectedIcp.priority} • Status: {selectedIcp.status}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* ICP Details Grid */}
                        <div className="p-6">
                            <h3 className="font-semibold mb-4">ICP Details</h3>
                            <div className="space-y-4">
                                <div>
                                    <span className="text-xs text-muted-foreground">Confidence Score</span>
                                    <p className="font-medium">{Math.round(selectedIcp.confidenceScore * 100)}%</p>
                                </div>
                                <div>
                                    <span className="text-xs text-muted-foreground">Created</span>
                                    <p className="font-medium">{new Date(selectedIcp.createdAt).toLocaleDateString()}</p>
                                </div>
                                <div>
                                    <span className="text-xs text-muted-foreground">Last Updated</span>
                                    <p className="font-medium">{new Date(selectedIcp.updatedAt).toLocaleDateString()}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
