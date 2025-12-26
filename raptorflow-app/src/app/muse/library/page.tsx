'use client';

import React, { useState, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { AssetLibrary } from '@/components/muse/AssetLibrary';
import { MuseTextEditor } from '@/components/muse/editors/MuseTextEditor';
import { MuseCanvas } from '@/components/muse/editors/MuseCanvas';
import { Asset, isVisualAsset } from '@/components/muse/types';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { FadeIn, Stagger } from '@/components/ui/motion';
import { ArrowLeft, Plus } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { useMuseAssets } from '@/lib/muse/assets-store';

// Mock data for demo - in real app this would come from context/store
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
    {
        id: '4',
        type: 'sales-email',
        title: 'Cold Outreach Email',
        content: 'Subject: Quick question about {{company_name}}\'s marketing\n\nHi {{name}},\n\nI noticed {{company_name}} is growing fast. Curious — how are you handling marketing planning right now?\n\nMost founders I talk to spend 10+ hours a week on marketing decisions that should take minutes...',
        prompt: 'Write a cold email for B2B SaaS founders',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 48),
        updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 48),
        folder: 'Sales',
        status: 'complete',
    },
];

export default function MuseLibraryPage() {
    const { assets, setAssets } = useMuseAssets(MOCK_ASSETS);
    const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
    const [editorOpen, setEditorOpen] = useState(false);

    const handleOpenAsset = useCallback((asset: Asset) => {
        setSelectedAsset(asset);
        setEditorOpen(true);
    }, []);

    const handleDeleteAsset = useCallback((asset: Asset) => {
        setAssets(prev => prev.filter(a => a.id !== asset.id));
    }, []);

    const handleDuplicateAsset = useCallback((asset: Asset) => {
        const newAsset: Asset = {
            ...asset,
            id: `asset-${Date.now()}`,
            title: `${asset.title} (Copy)`,
            createdAt: new Date(),
            updatedAt: new Date(),
        };
        setAssets(prev => [newAsset, ...prev]);
    }, []);

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
            <div className="min-h-screen bg-[#F8F9F7] px-8 lg:px-16 py-10">
                {/* Editorial Header */}
                <header className="flex items-end justify-between mb-12">
                    <div className="flex items-center gap-5">
                        <Link
                            href="/muse"
                            className="flex items-center justify-center h-11 w-11 rounded-xl border border-[#E5E6E3] bg-white hover:bg-[#F8F9F7] transition-colors"
                        >
                            <ArrowLeft className="h-4 w-4 text-[#5B5F61]" />
                        </Link>
                        <div>
                            <h1 className="font-serif text-[36px] text-[#2D3538] tracking-tight leading-none">
                                Library
                            </h1>
                            <p className="font-sans text-[14px] text-[#5B5F61] mt-2">
                                All your created assets in one place
                            </p>
                        </div>
                    </div>

                    <Link
                        href="/muse"
                        className="flex items-center gap-2 h-11 px-5 rounded-xl bg-[#1a1d1e] text-white text-[13px] font-medium tracking-tight shadow-md hover:shadow-lg transition-all"
                    >
                        <Plus className="h-4 w-4" />
                        Create New
                    </Link>
                </header>

                {/* Asset Library */}
                <AssetLibrary
                    assets={assets}
                    onAssetClick={handleOpenAsset}
                    onAssetDelete={handleDeleteAsset}
                    onAssetDuplicate={handleDuplicateAsset}
                />
            </div>

            {/* Editor Dialog */}
            <Dialog open={editorOpen} onOpenChange={setEditorOpen}>
                <DialogContent className="max-w-5xl h-[85vh] p-0 overflow-hidden">
                    {selectedAsset && (
                        isVisualAsset(selectedAsset.type) ? (
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
