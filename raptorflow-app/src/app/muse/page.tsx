'use client';

import React, { useState, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { MuseChat } from '@/components/muse/MuseChat';
import { GenerationCard } from '@/components/muse/GenerationCard';
import { MuseTextEditor } from '@/components/muse/editors/MuseTextEditor';
import { MuseCanvas } from '@/components/muse/editors/MuseCanvas';
import { MuseNameEditor } from '@/components/muse/editors/MuseNameEditor';
import {
    Asset,
    AssetType,
    GenerationJob,
    isVisualAsset,
    getAssetConfig
} from '@/components/muse/types';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { FolderOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';

// Mock data for demo
const MOCK_ASSETS: Asset[] = [
    {
        id: '1',
        type: 'email',
        title: 'Welcome Email Sequence',
        content: 'Subject: Welcome to RaptorFlow!\n\nHi {{name}},\n\nWelcome to RaptorFlow! We\'re thrilled to have you on board.\n\nYour journey to marketing clarity starts now...',
        prompt: 'Make me a welcome email for new users',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2),
        updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2),
        folder: 'Onboarding',
        status: 'complete',
    },
    {
        id: '2',
        type: 'tagline',
        title: 'Brand Taglines',
        content: 'Marketing. Finally under control.\n\nFrom chaos to clarity.\n\nYour marketing war room.',
        prompt: 'Generate tagline options for RaptorFlow',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
        updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
        status: 'complete',
    },
    {
        id: '3',
        type: 'social-post',
        title: 'LinkedIn Launch Post',
        content: '🚀 Excited to announce RaptorFlow — the marketing operating system for founders.\n\nNo more tool sprawl. No more random posting. No more "marketing by vibes."\n\nOne system. Clear decisions. Weekly execution.\n\n#MarketingOS #FounderLife #SaaS',
        prompt: 'Write a LinkedIn post announcing RaptorFlow',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5),
        updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 5),
        folder: 'Social',
        status: 'complete',
    },
];

// Mock cohorts
const MOCK_COHORTS = [
    { id: 'cohort-1', name: 'Early-stage founders' },
    { id: 'cohort-2', name: 'Marketing managers' },
    { id: 'cohort-3', name: 'Agency owners' },
];

// Mock competitors
const MOCK_COMPETITORS = [
    { name: 'Jasper AI' },
    { name: 'Copy.ai' },
    { name: 'HubSpot' },
];

// Mock campaigns
const MOCK_CAMPAIGNS = [
    { id: 'camp-1', name: 'Product Launch Q1' },
    { id: 'camp-2', name: 'Founder Story Series' },
];


// Simulate generation with realistic timing
function simulateGeneration(
    prompt: string,
    assetType: AssetType,
    context: Record<string, string> | undefined,
    onProgress: (progress: number) => void,
    onComplete: (content: string) => void
) {
    const duration = 5000 + Math.random() * 10000; // 5-15 seconds
    const steps = 20;
    const stepDuration = duration / steps;
    let currentStep = 0;

    const interval = setInterval(() => {
        currentStep++;
        const progress = Math.min(95, (currentStep / steps) * 100);
        onProgress(progress);

        if (currentStep >= steps) {
            clearInterval(interval);

            // Generate mock content based on type
            const config = getAssetConfig(assetType);
            const cohortInfo = context?.cohort ? `\n\n**Target Audience:** ${context.cohort}` : '';
            const mockContent = `# ${config?.label || 'Asset'}\n\nGenerated based on: "${prompt}"${cohortInfo}\n\n[This is simulated content. Backend AI integration coming soon.]`;

            setTimeout(() => {
                onComplete(mockContent);
            }, 500);
        }
    }, stepDuration);

    return () => clearInterval(interval);
}

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function MusePageContent() {
    const searchParams = useSearchParams();
    const initialPrompt = searchParams.get('prompt') || undefined;

    const [assets, setAssets] = useState<Asset[]>(MOCK_ASSETS);
    const [jobs, setJobs] = useState<GenerationJob[]>([]);
    const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
    const [editorOpen, setEditorOpen] = useState(false);

    // Handle new asset creation from chat
    const handleCreate = useCallback((prompt: string, assetType: AssetType, context?: Record<string, string>) => {
        const jobId = `job-${Date.now()}`;

        const newJob: GenerationJob = {
            id: jobId,
            prompt,
            assetType,
            status: 'generating',
            progress: 0,
            startedAt: new Date(),
        };

        setJobs(prev => [...prev, newJob]);

        // Start simulation
        simulateGeneration(
            prompt,
            assetType,
            context,
            (progress) => {
                setJobs(prev => prev.map(j =>
                    j.id === jobId ? { ...j, progress } : j
                ));
            },
            (content) => {
                const newAsset: Asset = {
                    id: `asset-${Date.now()}`,
                    type: assetType,
                    title: prompt.slice(0, 50) + (prompt.length > 50 ? '...' : ''),
                    content,
                    prompt,
                    createdAt: new Date(),
                    updatedAt: new Date(),
                    status: 'complete',
                    linkedCohort: context?.cohort,
                };

                setAssets(prev => [newAsset, ...prev]);
                setJobs(prev => prev.map(j =>
                    j.id === jobId ? { ...j, status: 'complete', asset: newAsset } : j
                ));
            }
        );
    }, []);

    // Handle opening an asset
    const handleOpenAsset = useCallback((asset: Asset) => {
        setSelectedAsset(asset);
        setEditorOpen(true);
    }, []);

    // Handle job card click (open completed asset)
    const handleJobClick = useCallback((job: GenerationJob) => {
        if (job.status === 'complete' && job.asset) {
            handleOpenAsset(job.asset);
        }
    }, [handleOpenAsset]);

    // Handle save from editor
    const handleSave = useCallback((content: string) => {
        if (!selectedAsset) return;

        setAssets(prev => prev.map(a =>
            a.id === selectedAsset.id
                ? { ...a, content, updatedAt: new Date() }
                : a
        ));
        setEditorOpen(false);
    }, [selectedAsset]);

    // Active jobs (not complete)
    const activeJobs = jobs.filter(j => j.status !== 'complete');

    return (
        <AppLayout>
            <div className="relative h-[calc(100vh-80px)] flex flex-col">

                {/* Active generation cards - floating at top */}
                {activeJobs.length > 0 && (
                    <div className="absolute top-4 right-4 z-20 w-80 space-y-3">
                        {activeJobs.map(job => (
                            <GenerationCard
                                key={job.id}
                                job={job}
                                onClick={() => handleJobClick(job)}
                                className="shadow-xl"
                            />
                        ))}
                    </div>
                )}

                {/* Library button - links to library page */}
                <Link
                    href="/muse/library"
                    className={cn(
                        'fixed bottom-6 left-[calc(var(--sidebar-width)+24px)] z-20',
                        'flex items-center gap-2 h-11 px-5 rounded-full',
                        'bg-foreground text-background',
                        'text-sm font-medium',
                        'shadow-lg shadow-foreground/10',
                        'hover:scale-105 active:scale-95',
                        'transition-all duration-200'
                    )}
                >
                    <FolderOpen className="h-4 w-4" />
                    Library
                    {assets.length > 0 && (
                        <span className="ml-1 h-5 px-1.5 rounded-full bg-background/20 text-xs flex items-center justify-center">
                            {assets.length}
                        </span>
                    )}
                </Link>

                {/* Main chat interface */}
                <MuseChat
                    initialPrompt={initialPrompt}
                    onAssetCreate={handleCreate}
                    cohorts={MOCK_COHORTS}
                    competitors={MOCK_COMPETITORS}
                    campaigns={MOCK_CAMPAIGNS}
                    className="flex-1"
                />

            </div>

            {/* Editor Dialog */}
            <Dialog open={editorOpen} onOpenChange={setEditorOpen}>
                <DialogContent className="max-w-5xl h-[85vh] p-0 overflow-hidden">
                    {selectedAsset && (
                        // Route to appropriate editor based on asset type
                        selectedAsset.type === 'product-name' || selectedAsset.type === 'domain-name' ? (
                            <MuseNameEditor
                                title={selectedAsset.title}
                                onSave={(name) => {
                                    setAssets(prev => prev.map(a =>
                                        a.id === selectedAsset.id
                                            ? { ...a, content: name, updatedAt: new Date() }
                                            : a
                                    ));
                                    setEditorOpen(false);
                                }}
                                onClose={() => setEditorOpen(false)}
                            />
                        ) : isVisualAsset(selectedAsset.type) ? (
                            <MuseCanvas
                                initialData={typeof selectedAsset.content === 'object' ? selectedAsset.content : undefined}
                                onSave={(data) => {
                                    if (selectedAsset) {
                                        setAssets(prev => prev.map(a =>
                                            a.id === selectedAsset.id
                                                ? { ...a, content: data, updatedAt: new Date() }
                                                : a
                                        ));
                                        setEditorOpen(false);
                                    }
                                }}
                                onClose={() => setEditorOpen(false)}
                            />
                        ) : (
                            <MuseTextEditor
                                title={selectedAsset.title}
                                initialContent={typeof selectedAsset.content === 'string' ? selectedAsset.content : ''}
                                currentAsset={selectedAsset}
                                allAssets={assets}
                                onSave={handleSave}
                                onClose={() => setEditorOpen(false)}
                            />
                        )
                    )}
                </DialogContent>
            </Dialog>
        </AppLayout>
    );
}

export default function MusePage() {
    return (
        <Suspense fallback={
            <AppLayout>
                <div className="flex items-center justify-center h-[calc(100vh-80px)]">
                    <div className="text-muted-foreground">Loading Muse...</div>
                </div>
            </AppLayout>
        }>
            <MusePageContent />
        </Suspense>
    );
}
