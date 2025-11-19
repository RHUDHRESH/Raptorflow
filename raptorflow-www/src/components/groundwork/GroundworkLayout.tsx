'use client';

import React from 'react';
import { SectionNav } from './SectionNav';
import { SectionContent } from './SectionContent';
import { GroundworkProvider } from './GroundworkProvider';

export function GroundworkLayout({ children }: { children?: React.ReactNode }) {
  return (
    <GroundworkProvider>
      <div className="flex h-screen bg-rf-bg">
        <SectionNav />
        <SectionContent />
      </div>
    </GroundworkProvider>
  );
}

