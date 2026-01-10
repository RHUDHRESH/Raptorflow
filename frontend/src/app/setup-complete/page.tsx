"use client";

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { BlueprintCard } from '@/components/ui/BlueprintCard';

const BlueprintButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export const runtime = 'edge';

export default function SetupCompletePage() {
  const [sql, setSql] = useState({ profiles: '', payments: '' });
  const [copied, setCopied] = useState({ profiles: false, payments: false });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSQL();
  }, []);

  const fetchSQL = async () => {
    try {
      const response = await fetch('/api/create-tables', { method: 'POST' });
      const data = await response.json();
      setSql({
        profiles: data.profiles_sql || '',
        payments: data.payments_sql || ''
      });
    } catch (error) {
      console.error('Failed to fetch SQL:', error);
    }
  };

  const copyToClipboard = (text: string, type: 'profiles' | 'payments') => {
    navigator.clipboard.writeText(text);
    setCopied(prev => ({ ...prev, [type]: true }));
    setTimeout(() => setCopied(prev => ({ ...prev, [type]: false })), 2000);
  };

  const runTests = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/test-db-direct');
      const data = await response.json();
      console.log('Test results:', data);
      alert('Test results: ' + JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Test failed:', error);
      alert('Test failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[var(--canvas)] p-8">
      <div className="max-w-6xl mx-auto">
        <BlueprintCard figure="SETUP" code="COMPLETE" showCorners variant="elevated" padding="lg">
          <h1 className="font-serif text-3xl text-[var(--ink)] mb-6">
            Complete Database Setup
          </h1>

          <div className="space-y-6">
            {/* Instructions */}
            <div className="p-4 bg-[var(--blueprint)]/10 border border-[var(--blueprint)] rounded-[var(--radius)]">
              <h2 className="font-semibold text-[var(--blueprint)] mb-3">
                📋 Instructions:
              </h2>
              <ol className="list-decimal list-inside space-y-2 text-sm text-[var(--ink)]">
                <li>Go to <a href="https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/sql" target="_blank" className="text-[var(--blueprint)] underline">Supabase SQL Editor</a></li>
                <li>Copy the SQL code from below (user_profiles table)</li>
                <li>Click "Run" to execute</li>
                <li>Copy the SQL code for payments table</li>
                <li>Click "Run" again</li>
                <li>Click "Test Tables" to verify</li>
              </ol>
            </div>

            {/* User Profiles Table SQL */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-[var(--ink)]">User Profiles Table SQL:</h3>
                <BlueprintButton
                  onClick={() => copyToClipboard(sql.profiles, 'profiles')}
                  variant="secondary"
                  size="sm"
                >
                  {copied.profiles ? '✅ Copied!' : '📋 Copy'}
                </BlueprintButton>
              </div>
              <div className="bg-[var(--canvas)] border border-[var(--structure)] rounded-[var(--radius)] p-4">
                <pre className="text-xs font-mono text-[var(--ink)] whitespace-pre-wrap max-h-64 overflow-auto">
                  {sql.profiles || 'Loading...'}
                </pre>
              </div>
            </div>

            {/* Payments Table SQL */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-[var(--ink)]">Payments Table SQL:</h3>
                <BlueprintButton
                  onClick={() => copyToClipboard(sql.payments, 'payments')}
                  variant="secondary"
                  size="sm"
                >
                  {copied.payments ? '✅ Copied!' : '📋 Copy'}
                </BlueprintButton>
              </div>
              <div className="bg-[var(--canvas)] border border-[var(--structure)] rounded-[var(--radius)] p-4">
                <pre className="text-xs font-mono text-[var(--ink)] whitespace-pre-wrap max-h-64 overflow-auto">
                  {sql.payments || 'Loading...'}
                </pre>
              </div>
            </div>

            {/* Test Button */}
            <div className="flex gap-4">
              <BlueprintButton
                onClick={runTests}
                disabled={loading}
                className="flex-1"
              >
                {loading ? 'Testing...' : '🧪 Test Tables'}
              </BlueprintButton>
              <BlueprintButton
                onClick={() => window.open('https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/sql', '_blank')}
                variant="secondary"
                className="flex-1"
              >
                🔗 Open Supabase SQL
              </BlueprintButton>
            </div>

            {/* Status */}
            <div className="p-4 bg-[var(--success-light)] border border-[var(--success)] rounded-[var(--radius)]">
              <h3 className="font-semibold text-[var(--success)] mb-2">
                ✅ Ready to Complete Setup
              </h3>
              <p className="text-sm text-[var(--secondary)]">
                Follow the instructions above to create the database tables, then test the authentication flow.
              </p>
            </div>

            {/* Next Steps */}
            <div className="mt-6 p-4 bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)]">
              <h3 className="font-semibold text-[var(--ink)] mb-3">After Setup:</h3>
              <ul className="space-y-2 text-sm text-[var(--secondary)]">
                <li>✅ Test user registration at <a href="/login" className="text-[var(--blueprint)] underline">/login</a></li>
                <li>✅ Verify email confirmation works</li>
                <li>✅ Check pricing page redirects</li>
                <li>✅ Test payment initiation</li>
                <li>✅ Verify workspace access protection</li>
              </ul>
            </div>
          </div>
        </BlueprintCard>
      </div>
    </div>
  );
}
