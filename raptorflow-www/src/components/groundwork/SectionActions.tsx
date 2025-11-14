'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { useGroundwork } from './GroundworkProvider';
import { SECTIONS } from '@/lib/groundwork/config';
import { SectionId } from '@/lib/groundwork/types';
import { cn } from '@/lib/utils';
import Link from 'next/link';

export function SectionActions() {
  const { state, setCurrentSection, markSectionComplete } = useGroundwork();

  const currentIndex = SECTIONS.findIndex((s) => s.id === state.currentSection);
  const currentSection = SECTIONS[currentIndex];
  const sectionState = state.sections[state.currentSection];

  const hasNext = currentIndex < SECTIONS.length - 1;
  const hasPrevious = currentIndex > 0;
  const isLastSection = currentIndex === SECTIONS.length - 1;

  const handleNext = () => {
    if (hasNext) {
      setCurrentSection(SECTIONS[currentIndex + 1].id);
    }
  };

  const handlePrevious = () => {
    if (hasPrevious) {
      setCurrentSection(SECTIONS[currentIndex - 1].id);
    }
  };

  const handleComplete = () => {
    markSectionComplete(state.currentSection);
    if (hasNext) {
      handleNext();
    } else {
      // Navigate to completion page
      window.location.href = '/groundwork/complete';
    }
  };

  const canComplete = sectionState.data !== null;

  return (
    <div className="sticky bottom-0 border-t border-rf-cloud bg-rf-bg p-6 mt-8">
      <div className="max-w-3xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          {hasPrevious && (
            <Button
              variant="outline"
              onClick={handlePrevious}
              className="border-rf-cloud"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous
            </Button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {!isLastSection ? (
            <Button
              onClick={handleNext}
              disabled={!canComplete}
              className={cn(
                'bg-rf-primary text-white hover:bg-rf-primary/90',
                !canComplete && 'opacity-50 cursor-not-allowed'
              )}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          ) : (
            canComplete ? (
              <Button
                asChild
                className="bg-rf-success text-white hover:bg-rf-success/90"
              >
                <Link href="/groundwork/complete">
                  <Check className="w-4 h-4 mr-1" />
                  Complete Groundwork
                </Link>
              </Button>
            ) : (
              <Button
                disabled
                className="opacity-50 cursor-not-allowed bg-rf-success text-white"
              >
                <Check className="w-4 h-4 mr-1" />
                Complete Groundwork
              </Button>
            )
          )}
        </div>
      </div>
    </div>
  );
}

