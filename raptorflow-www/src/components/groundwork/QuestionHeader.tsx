'use client';

import React from 'react';
import { TextShimmer } from './TextShimmer';
import { useGroundwork } from './GroundworkProvider';
import { SECTIONS } from '@/lib/groundwork/config';

export function QuestionHeader() {
  const { state } = useGroundwork();
  const currentSection = SECTIONS.find((s) => s.id === state.currentSection);

  if (!currentSection) return null;

  return (
    <div className="mb-8">
      <div className="mb-2">
        <h3 className="text-sm font-medium text-rf-subtle uppercase tracking-wide">
          {currentSection.title}
        </h3>
      </div>
      <div className="mt-4">
        <TextShimmer
          as="h2"
          className="text-2xl font-bold text-rf-ink leading-tight"
          duration={3}
        >
          {currentSection.question}
        </TextShimmer>
      </div>
      {currentSection.description && (
        <p className="mt-3 text-sm text-rf-subtle">{currentSection.description}</p>
      )}
    </div>
  );
}

