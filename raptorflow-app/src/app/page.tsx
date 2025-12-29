import { Suspense } from 'react';
import { PublicLayout } from '@/components/layout/PublicLayout';
import { FoundationStudioHero } from '@/components/marketing/FoundationStudioHero';
import { LandingPageClient } from './LandingPageClient';

export default function LandingPage() {
  return (
    <PublicLayout>
      <FoundationStudioHero />
      <Suspense fallback={null}>
        <LandingPageClient />
      </Suspense>
    </PublicLayout>
  );
}
