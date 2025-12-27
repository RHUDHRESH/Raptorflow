'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
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
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { useMuseAssets } from '@/lib/muse/assets-store';
import { motion, AnimatePresence } from 'motion/react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useFoundationMentions } from '@/context/FoundationProvider';

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

// Initial demo assets (will be replaced by user-generated content)
const INITIAL_ASSETS: Asset[] = [
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


import { spine } from '@/lib/muse/spine-client';

// Real generation using the Python Agentic Spine
async function generateAsset(
    prompt: string,
    assetType: AssetType,
    context: Record<string, string> | undefined,
    onProgress: (progress: number) => void,
    onComplete: (content: string) => void
) {
    try {
        onProgress(20);

        // Construct the full prompt including context
        const fullPrompt = context?.cohort
            ? `Create a ${assetType} for the ${context.cohort} cohort. Prompt: ${prompt}`
            : `Create a ${assetType}. Prompt: ${prompt}`;

        const response = await spine.createAsset(
            fullPrompt,
            'default_ws', // Hardcoded for demo
            'default_tenant'
        );

        onProgress(100);
        onComplete(response.asset_content);
    } catch (error) {
        console.error("Asset generation failed:", error);
        onComplete("Failed to generate asset. Ensure backend is running.");
    }
}

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function MusePageContent() {
    const searchParams = useSearchParams();
    const initialPrompt = searchParams.get('prompt') || undefined;
    const pageRef = useRef<HTMLDivElement>(null);
    const libraryButtonRef = useRef<HTMLAnchorElement>(null);

    // Get cohorts, competitors, campaigns from Foundation
    const { cohorts, competitors, campaigns, isLoading: foundationLoading } = useFoundationMentions();

    const { assets, setAssets } = useMuseAssets(INITIAL_ASSETS);
    const [jobs, setJobs] = useState<GenerationJob[]>([]);
    const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
    const [editorOpen, setEditorOpen] = useState(false);
    const [showTips, setShowTips] = useState(true);

    // GSAP entrance animations
    useEffect(() => {
        const ctx = gsap.context(() => {
            // Animate page entrance
            gsap.from('.muse-page-entrance', {
                opacity: 0,
                y: 30,
                duration: 0.8,
                ease: 'power3.out'
            });

            // Animate library button
            gsap.from(libraryButtonRef.current, {
                opacity: 0,
                scale: 0.8,
                duration: 0.6,
                delay: 0.3,
                ease: 'back.out(1.7)'
            });
        }, pageRef);

        return () => ctx.revert();
    }, []);

    // Active jobs (not complete)
    const activeJobs = jobs.filter(j => j.status !== 'complete');

    // Animate new generation cards appearing
    useEffect(() => {
        if (activeJobs.length > 0) {
            gsap.from('.generation-card-new', {
                opacity: 0,
                x: 100,
                duration: 0.5,
                stagger: 0.1,
                ease: 'power2.out'
            });
        }
    }, [activeJobs.length]);

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

        // Start real generation
        generateAsset(
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
                setSelectedAsset(newAsset);
                setEditorOpen(true);
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

    return (
        <AppLayout fullBleed>
            <div ref={pageRef} className="min-h-screen bg-[#F8F9F7] muse-page-entrance">                {/* Main Content - Full height chat */}
                <div className="w-full h-full px-8 lg:px-16 pt-6">
                    {/* Header with Library button */}
                    <div className="flex justify-end mb-6">
                        <Link
                            href="/muse/library"
                            className="flex items-center gap-2 h-11 px-5 rounded-xl bg-[#1a1d1e] text-white text-[13px] font-medium tracking-tight shadow-md hover:shadow-lg hover:scale-[1.02] transition-all"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                            </svg>
                            <span>Library</span>
                            {assets.length > 0 && (
                                <span className="h-5 px-2 rounded-md bg-white/20 text-[11px] font-mono flex items-center justify-center">
                                    {assets.length}
                                </span>
                            )}
                        </Link>
                    </div>

                    {/* Active generation cards - floating */}
                    <AnimatePresence>
                        {activeJobs.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, y: -20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="fixed top-24 right-12 z-50 w-80 space-y-3"
                            >
                                {activeJobs.map((job) => (
                                    <motion.div
                                        key={job.id}
                                        layout
                                        initial={{ opacity: 0, x: 100 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 100 }}
                                    >
                                        <GenerationCard
                                            job={job}
                                            onClick={() => handleJobClick(job)}
                                            className="shadow-xl bg-white border-[#E5E6E3]"
                                        />
                                    </motion.div>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Main Chat - directly on canvas */}
                    <MuseChat
                        initialPrompt={initialPrompt}
                        onAssetCreate={handleCreate}
                        cohorts={cohorts}
                        competitors={competitors}
                        campaigns={campaigns}
                        className="flex-1 min-h-[600px]"
                    />
                </div>

                {/* Enhanced Editor Dialog with animations */}
                <AnimatePresence mode="wait">
                    {editorOpen && (
                        <Dialog open={editorOpen} onOpenChange={setEditorOpen}>
                            <DialogContent className="max-w-5xl h-[85vh] p-0 overflow-hidden">
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                                    animate={{ opacity: 1, scale: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.9, y: 20 }}
                                    transition={{
                                        duration: 0.3,
                                        ease: [0.175, 0.885, 0.32, 1.275]
                                    }}
                                    className="h-full"
                                >
                                    {selectedAsset && (
                                        // Route to appropriate editor based on asset type
                                        selectedAsset.type === 'product-name' ? (
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
                                </motion.div>
                            </DialogContent>
                        </Dialog>
                    )}
                </AnimatePresence>
            </div>
        </AppLayout>
    );
}

export default function MusePage() {
    return (
        <Suspense fallback={
            <AppLayout>
                <div className="flex items-center justify-center h-full">
                    <div className="text-muted-foreground">Loading Muse...</div>
                </div>
            </AppLayout>
        }>
            <MusePageContent />
        </Suspense>
    );
}
