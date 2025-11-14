'use client';

import React from 'react';
import { Check, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useGroundwork } from './GroundworkProvider';
import { SectionId } from '@/lib/groundwork/types';
import { SECTIONS } from '@/lib/groundwork/config';

export function SectionNav() {
  const { state, setCurrentSection } = useGroundwork();

  const handleSectionClick = (sectionId: SectionId) => {
    setCurrentSection(sectionId);
  };

  return (
    <div className="w-64 border-r border-rf-cloud bg-rf-bg">
      <div className="p-6 border-b border-rf-cloud">
        <h2 className="text-xl font-bold text-rf-ink">Groundwork</h2>
        <p className="text-sm text-rf-subtle mt-1">Strategic onboarding</p>
      </div>

      <nav className="p-4 space-y-1">
        {SECTIONS.map((section, index) => {
          const sectionState = state.sections[section.id];
          const isActive = state.currentSection === section.id;
          const isCompleted = sectionState.completed;

          return (
            <button
              key={section.id}
              onClick={() => handleSectionClick(section.id)}
              className={cn(
                'w-full text-left px-4 py-3 rounded-lg transition-all duration-200',
                'flex items-center justify-between group',
                isActive
                  ? 'bg-rf-cloud border-l-2 border-rf-primary font-semibold text-rf-ink'
                  : 'hover:bg-rf-cloud/50 text-rf-subtle',
                !isActive && !isCompleted && 'opacity-60'
              )}
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                {isCompleted && !isActive ? (
                  <div className="flex-shrink-0 w-5 h-5 rounded-full bg-rf-success/10 flex items-center justify-center">
                    <Check className="w-3 h-3 text-rf-success" />
                  </div>
                ) : (
                  <div className="flex-shrink-0 w-5 h-5 rounded-full border border-rf-cloud flex items-center justify-center">
                    {isActive && (
                      <div className="w-2 h-2 rounded-full bg-rf-primary" />
                    )}
                  </div>
                )}
                <span className={cn('text-sm truncate', isActive && 'font-semibold')}>
                  {section.title}
                </span>
              </div>
              {isActive && (
                <ChevronRight className="w-4 h-4 text-rf-primary flex-shrink-0" />
              )}
            </button>
          );
        })}
      </nav>
    </div>
  );
}

