'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';

export function BillingSuccessClient() {
  const [status, setStatus] = useState('Finalizing your payment...');
  const router = useRouter();
  const searchParams = useSearchParams();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    async function finalizePayment() {
      const orderId = searchParams.get('order_id');
      if (!orderId) {
        setStatus('Missing order reference. Please contact support.');
        return;
      }

      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        router.push('/login');
        return;
      }

      try {
        const response = await fetch(
          `${apiUrl}/v1/payments/confirm/${orderId}`,
          {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${session.access_token}`,
              'Content-Type': 'application/json',
              'X-Tenant-ID': session.user.id,
            },
          }
        );

        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          throw new Error(body?.detail || 'Unable to confirm payment.');
        }

        setStatus('Payment confirmed. Redirecting to your dashboard...');
        setTimeout(() => router.push('/dashboard'), 1500);
      } catch (error: any) {
        setStatus(
          error?.message || 'Payment confirmation failed. Please contact support.'
        );
      }
    }

    finalizePayment();
  }, [apiUrl, router, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-canvas px-6 py-12">
      <div className="max-w-lg text-center space-y-4">
        <h1 className="text-3xl font-display font-semibold text-foreground">
          Payment Processing
        </h1>
        <p className="text-muted-foreground">{status}</p>
      </div>
    </div>
  );
}
