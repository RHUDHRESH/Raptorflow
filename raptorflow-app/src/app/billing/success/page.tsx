import { Suspense } from 'react';
import { BillingSuccessClient } from './BillingSuccessClient';

export default function BillingSuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-canvas px-6 py-12">
          <div className="max-w-lg text-center space-y-4">
            <h1 className="text-3xl font-display font-semibold text-foreground">
              Payment Processing
            </h1>
            <p className="text-muted-foreground">Preparing confirmation...</p>
          </div>
        </div>
      }
    >
      <BillingSuccessClient />
    </Suspense>
  );
}
