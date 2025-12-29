'use client';

import React, { use } from 'react';
import { useRouter } from 'next/navigation';
import { AppLayout } from '@/components/layout/AppLayout';
import { useMove } from '@/hooks/useMove';
import { MoveDetail } from '@/components/moves/MoveDetail';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react';
import { FadeIn } from '@/components/ui/motion';

export default function MovePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();

  const {
    move,
    rationale,
    isLoading,
    error,
    updateFields,
    toggleTask,
    refresh
  } = useMove(id);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
          <Loader2 className="w-10 h-10 text-accent animate-spin" />
          <p className="text-secondary-text animate-pulse font-medium tracking-tight">
            Retrieving tactical data...
          </p>
        </div>
      </AppLayout>
    );
  }

  if (error || !move) {
    return (
      <AppLayout>
        <div className="max-w-2xl mx-auto py-20 px-6">
          <div className="p-10 rounded-3xl border border-borders bg-surface flex flex-col items-center text-center space-y-6">
            <div className="p-4 bg-red-100/10 rounded-full">
              <AlertCircle className="w-8 h-8 text-red-500" />
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-display font-medium text-ink">
                Move Not Found
              </h2>
              <p className="text-secondary-text">
                The objective you're looking for might have been archived or deleted.
              </p>
            </div>
            <Button
              variant="outline"
              onClick={() => router.push('/dashboard')}
              className="border-borders hover:bg-muted/10 font-bold"
            >
              Return to Mission Control
            </Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-[1400px] mx-auto px-6 py-8 pb-32">
        <FadeIn>
          <div className="mb-6 flex justify-between items-center">
            <Button
              variant="ghost"
              onClick={() => router.push('/dashboard')}
              className="group -ml-2 text-secondary-text hover:text-ink pl-2 h-9"
            >
              <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
              Mission Control
            </Button>

            {move.campaignId && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/campaigns/${move.campaignId}`)}
                className="text-[10px] uppercase font-bold tracking-widest border-borders"
              >
                View Campaign Arc
              </Button>
            )}
          </div>
        </FadeIn>

        <MoveDetail
          move={move}
          rationale={rationale}
          onUpdate={updateFields}
          onToggleTask={toggleTask}
          onRefresh={refresh}
          standalone={true}
        />
      </div>
    </AppLayout>
  );
}
