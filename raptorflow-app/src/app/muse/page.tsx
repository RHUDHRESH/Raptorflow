'use client';

import React, { useState, useCallback, useRef, useEffect, lazy, Suspense } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { LazyLoad } from '@/components/ui/LazyLoad';
import {
  Dialog,
  DialogContent,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

// Lazy load heavy components
const MuseChat = lazy(() => import('@/components/muse/MuseChat'));
const GenerationCard = lazy(() => import('@/components/muse/GenerationCard'));
const MuseTextEditor = lazy(() => import('@/components/muse/editors/MuseTextEditor'));
const MuseCanvas = lazy(() => import('@/components/muse/editors/MuseCanvas'));
const MuseNameEditor = lazy(() => import('@/components/muse/editors/MuseNameEditor'));
import {
  Asset,
  AssetType,
  GenerationJob,
  isVisualAsset,
} from '@/components/muse/types';
import { X } from 'lucide-react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'motion/react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useFoundationMentions } from '@/context/FoundationProvider';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import { createMuseAsset, getMuseAsset, listMuseAssets } from '@/lib/muse/api';

// Register GSAP plugins
// eslint-disable-next-line @typescript-eslint/no-unused-vars
gsap.registerPlugin(ScrollTrigger);

function mapMuseAssetToUi(asset: any): Asset {
  const rawType = (asset.asset_type || 'text').toLowerCase();
  const normalizedType = (rawType === 'social_post' ? 'social-post' : rawType) as AssetType;
  const safeType = (['email', 'social-post', 'meme', 'social-card', 'product-name'] as AssetType[]).includes(
    normalizedType
  )
    ? normalizedType
    : 'email';

  return {
    id: asset.id,
    type: safeType,
    title: asset.generation_prompt || asset.metadata?.title || 'Muse Asset',
    content: asset.content || '',
    prompt: asset.generation_prompt || asset.metadata?.prompt,
    createdAt: new Date(asset.created_at || Date.now()),
    updatedAt: new Date(asset.updated_at || Date.now()),
    status: asset.status === 'ready' ? 'complete' : 'queued',
    linkedCohort: asset.metadata?.cohort,
  } as Asset;
}

async function hydrateAssets(): Promise<Asset[]> {
  const rawAssets = await listMuseAssets();
  return rawAssets.map(mapMuseAssetToUi);
}

function MusePageContent() {
  const searchParams = useSearchParams();
  const initialPrompt = searchParams.get('prompt') || undefined;
  const initialAssetId = searchParams.get('asset_id');
  const autoCreate = searchParams.get('auto') === '1';
  const pageRef = useRef<HTMLDivElement>(null);
  const libraryButtonRef = useRef<HTMLAnchorElement>(null);

  // Get cohorts, competitors, campaigns from Foundation
  const {
    cohorts,
    competitors,
    campaigns,
  } = useFoundationMentions();

  const [assets, setAssets] = useState<Asset[]>([]);
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const fetched = await hydrateAssets();
        setAssets(fetched);
      } catch (error) {
        console.error('Failed to load Muse assets', error);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (!initialAssetId) return;
    const loadAsset = async () => {
      try {
        const asset = await getMuseAsset(initialAssetId);
        const mapped = mapMuseAssetToUi(asset);
        setAssets((prev) => {
          const exists = prev.find((item) => item.id === mapped.id);
          return exists ? prev : [mapped, ...prev];
        });
        setSelectedAsset(mapped);
        setEditorOpen(true);
      } catch (error) {
        console.error('Failed to open asset', error);
      }
    };
    loadAsset();
  }, [initialAssetId]);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.muse-page-entrance', {
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power3.out',
      });

      gsap.from(libraryButtonRef.current, {
        opacity: 0,
        scale: 0.8,
        duration: 0.6,
        delay: 0.3,
        ease: 'back.out(1.7)',
      });
    }, pageRef);

    return () => ctx.revert();
  }, []);

  const activeJobs = jobs.filter((j) => j.status !== 'complete');

  const handleCreate = useCallback(
    async (
      prompt: string,
      assetType: AssetType,
      context?: Record<string, string>
    ) => {
      const jobId = `job-${Date.now()}`;

      const newJob: GenerationJob = {
        id: jobId,
        prompt,
        assetType,
        status: 'generating',
        progress: 10,
        startedAt: new Date(),
      };

      setJobs((prev) => [...prev, newJob]);

      try {
        setJobs((prev) =>
          prev.map((job) => (job.id === jobId ? { ...job, progress: 45 } : job))
        );
        const asset = await createMuseAsset(prompt, assetType, {
          cohort: context?.cohort,
          campaign: context?.campaign,
        });
        const mapped = mapMuseAssetToUi(asset);

        setJobs((prev) =>
          prev.map((job) =>
            job.id === jobId ? { ...job, status: 'complete', progress: 100, asset: mapped } : job
          )
        );
        setAssets((prev) => [mapped, ...prev]);
        setSelectedAsset(mapped);
        setEditorOpen(true);
      } catch (error) {
        console.error('Asset generation failed:', error);
        setJobs((prev) =>
          prev.map((job) =>
            job.id === jobId ? { ...job, status: 'failed', progress: 100 } : job
          )
        );
      }
    },
    []
  );

  useEffect(() => {
    if (!autoCreate || !initialPrompt) return;
    handleCreate(initialPrompt, 'email');
  }, [autoCreate, initialPrompt, handleCreate]);

  const handleOpenAsset = useCallback((asset: Asset) => {
    setSelectedAsset(asset);
    setEditorOpen(true);
  }, []);

  const handleJobClick = useCallback(
    (job: GenerationJob) => {
      if (job.status === 'complete' && job.asset) {
        handleOpenAsset(job.asset);
      }
    },
    [handleOpenAsset]
  );

  const handleSave = useCallback(
    (content: string) => {
      if (!selectedAsset) return;

      setAssets((prev) =>
        prev.map((asset) =>
          asset.id === selectedAsset.id
            ? { ...asset, content, updatedAt: new Date() }
            : asset
        )
      );
      setEditorOpen(false);
    },
    [selectedAsset]
  );

  return (
    <AppLayout fullBleed>
      <div
        ref={pageRef}
        className="min-h-screen bg-[#F8F9F7] muse-page-entrance"
      >
        <div className="w-full h-full px-8 lg:px-16 pt-6">
          <div className="flex justify-end mb-6">
            <Link
              href="/muse/library"
              className="flex items-center gap-2 h-11 px-5 rounded-xl bg-[#1a1d1e] text-white text-[13px] font-medium tracking-tight shadow-md hover:shadow-lg hover:scale-[1.02] transition-all"
              ref={libraryButtonRef}
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
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
                    <LazyLoad>
                      <GenerationCard
                        job={job}
                        onClick={() => handleJobClick(job)}
                        className="shadow-xl bg-white border-[#E5E6E3]"
                      />
                    </LazyLoad>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          <LazyLoad>
            <MuseChat
              initialPrompt={initialPrompt}
              onAssetCreate={handleCreate}
              cohorts={cohorts}
              competitors={competitors}
              campaigns={campaigns}
              className="flex-1 min-h-[600px]"
            />
          </LazyLoad>
        </div>
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
                    ease: [0.175, 0.885, 0.32, 1.275],
                  }}
                  className="h-full"
                >
                  {selectedAsset &&
                    (selectedAsset.type === 'product-name' ? (
                      <MuseNameEditor
                        title={selectedAsset.title}
                        onSave={(name) => {
                          setAssets((prev) =>
                            prev.map((asset) =>
                              asset.id === selectedAsset.id
                                ? { ...asset, content: name, updatedAt: new Date() }
                                : asset
                            )
                          );
                          setEditorOpen(false);
                        }}
                        onClose={() => setEditorOpen(false)}
                      />
                    ) : isVisualAsset(selectedAsset.type) ? (
                      <MuseCanvas
                        initialData={
                          typeof selectedAsset.content === 'object'
                            ? selectedAsset.content
                            : undefined
                        }
                        onSave={(data) => {
                          if (selectedAsset) {
                            setAssets((prev) =>
                              prev.map((asset) =>
                                asset.id === selectedAsset.id
                                  ? { ...asset, content: data, updatedAt: new Date() }
                                  : asset
                              )
                            );
                            setEditorOpen(false);
                          }
                        }}
                        onClose={() => setEditorOpen(false)}
                      />
                    ) : (
                      <MuseTextEditor
                        title={selectedAsset.title}
                        initialContent={
                          typeof selectedAsset.content === 'string'
                            ? selectedAsset.content
                            : ''
                        }
                        currentAsset={selectedAsset}
                        allAssets={assets}
                        onSave={handleSave}
                        onClose={() => setEditorOpen(false)}
                      />
                    ))}
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
    <Suspense
      fallback={
        <AppLayout>
          <div className="flex items-center justify-center h-full">
            <div className="text-muted-foreground">Loading Muse...</div>
          </div>
        </AppLayout>
      }
    >
      <MusePageContent />
    </Suspense>
  );
}
