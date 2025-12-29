'use client';

import React, { useState, useCallback } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { AssetLibrary } from '@/components/muse/AssetLibrary';
import { MuseTextEditor } from '@/components/muse/editors/MuseTextEditor';
import { MuseCanvas } from '@/components/muse/editors/MuseCanvas';
import { MuseNameEditor } from '@/components/muse/editors/MuseNameEditor';
import { Asset, AssetType, isVisualAsset } from '@/components/muse/types';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { FadeIn, Stagger } from '@/components/ui/motion';
import { ArrowLeft, Plus } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { useAssets } from '@/hooks/useAssets';
import { CreateAssetModal } from '@/components/muse/CreateAssetModal';
import { spine } from '@/lib/muse/spine-client';
import { useToast } from '@/hooks/use-toast';

// Mock data for demo - in real app this would come from context/store
const MOCK_ASSETS: Asset[] = [
  {
    id: '1',
    type: 'email',
    title: 'Welcome Email Sequence',
    content:
      "Subject: Welcome to RaptorFlow!\n\nHi {{name}},\n\nWelcome to RaptorFlow! We're thrilled to have you on board.\n\nYour journey to marketing clarity starts now...",
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
    content:
      'Marketing. Finally under control.\n\nFrom chaos to clarity.\n\nYour marketing war room.',
    prompt: 'Generate tagline options for RaptorFlow',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
    status: 'complete',
  },
  {
    id: '3',
    type: 'social-post',
    title: 'LinkedIn Launch Post',
    content:
      '🚀 Excited to announce RaptorFlow — the marketing operating system for founders.\n\nNo more tool sprawl. No more random posting. No more "marketing by vibes."\n\nOne system. Clear decisions. Weekly execution.\n\n#MarketingOS #FounderLife #SaaS',
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
    content:
      "Subject: Quick question about {{company_name}}'s marketing\n\nHi {{name}},\n\nI noticed {{company_name}} is growing fast. Curious — how are you handling marketing planning right now?\n\nMost founders I talk to spend 10+ hours a week on marketing decisions that should take minutes...",
    prompt: 'Write a cold email for B2B SaaS founders',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 48),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 48),
    folder: 'Sales',
    status: 'complete',
  },
];

export default function MuseLibraryPage() {
  const {
    assets,
    isLoading,
    hasMore,
    loadMore,
    filters,
    createAsset,
    updateAsset,
    deleteAsset,
    duplicateAsset
  } = useAssets({ pageSize: 12 });

  const { toast } = useToast();
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleOpenAsset = useCallback((asset: Asset) => {
    setSelectedAsset(asset);
    setEditorOpen(true);
    setIsDirty(false);
  }, []);

  const handleCloseEditor = useCallback(() => {
    if (isDirty) {
      if (confirm('You have unsaved changes. Are you sure you want to close?')) {
        setEditorOpen(false);
        setIsDirty(false);
      }
    } else {
      setEditorOpen(false);
    }
  }, [isDirty]);

  const handleCreateNew = useCallback(async (type: AssetType, prompt?: string) => {
    const newAsset: Asset = {
      id: crypto.randomUUID(),
      type,
      title: 'New Artifact',
      content: type === 'meme' || type === 'social-card'
        ? { width: 1080, height: 1080, background: '#ffffff', elements: [] }
        : '',
      createdAt: new Date(),
      updatedAt: new Date(),
      status: prompt ? 'generating' : 'complete',
    };

    if (prompt) {
      setIsGenerating(true);
      setCreateModalOpen(false);

      try {
        const response = await spine.chat(prompt);
        newAsset.content = response.asset_content;
        newAsset.status = 'complete';
        newAsset.prompt = prompt;
        newAsset.title = prompt.slice(0, 30) + '...';

        await createAsset(newAsset);
        toast({ title: 'Artifact Generated', description: 'Your new asset is ready.' });
      } catch (err) {
        console.error('Generation failed:', err);
        newAsset.status = 'failed';
        await createAsset(newAsset);
        toast({ variant: 'destructive', title: 'Generation Failed', description: 'Starting with a blank version.' });
      } finally {
        setIsGenerating(false);
      }
    } else {
      await createAsset(newAsset);
      setCreateModalOpen(false);
      setSelectedAsset(newAsset);
      setEditorOpen(true);
    }
  }, [createAsset, toast]);

  const handleSave = useCallback(
    async (content: string | any) => {
      if (!selectedAsset) return;

      const updated = { ...selectedAsset, content, updatedAt: new Date() };
      await updateAsset(updated);
      setEditorOpen(false);
      setIsDirty(false);
      toast({ title: 'Saved', description: 'Artifact safely archived.' });
    },
    [selectedAsset, updateAsset, toast]
  );

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

          <button
            onClick={() => setCreateModalOpen(true)}
            className="flex items-center gap-2 h-11 px-5 rounded-xl bg-[#1a1d1e] text-white text-[13px] font-medium tracking-tight shadow-md hover:shadow-lg transition-all"
          >
            <Plus className="h-4 w-4" />
            Create New
          </button>
        </header>

        {/* Asset Library */}
        <AssetLibrary
          assets={assets}
          onAssetClick={handleOpenAsset}
          onAssetDelete={(a) => deleteAsset(a.id)}
          onAssetDuplicate={(a) => duplicateAsset(a.id)}
          hasMore={hasMore}
          onLoadMore={loadMore}
          isLoading={isLoading}
          filters={filters}
        />

        <CreateAssetModal
          open={createModalOpen}
          onOpenChange={setCreateModalOpen}
          onCreate={handleCreateNew}
        />
      </div>

      {/* Editor Dialog */}
      <Dialog open={editorOpen} onOpenChange={(open) => !open && handleCloseEditor()}>
        <DialogContent className="max-w-5xl h-[85vh] p-0 overflow-hidden">
          {selectedAsset &&
            (selectedAsset.type === 'product-name' ? (
              <MuseNameEditor
                title={selectedAsset.title}
                onSave={handleSave}
                onChange={() => setIsDirty(true)}
                onClose={handleCloseEditor}
              />
            ) : isVisualAsset(selectedAsset.type) ? (
              <MuseCanvas
                initialData={
                  typeof selectedAsset.content === 'object'
                    ? selectedAsset.content
                    : undefined
                }
                onSave={handleSave}
                onChange={() => setIsDirty(true)}
                onClose={handleCloseEditor}
              />
            ) : (
              <MuseTextEditor
                title={selectedAsset.title}
                initialContent={
                  typeof selectedAsset.content === 'string'
                    ? selectedAsset.content
                    : ''
                }
                onSave={handleSave}
                onChange={() => setIsDirty(true)}
                onClose={handleCloseEditor}
              />
            ))}
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}
