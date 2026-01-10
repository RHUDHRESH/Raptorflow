"use client";

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { BlueprintCard } from '@/components/ui/BlueprintCard';

const BlueprintButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export const runtime = 'edge';

export default function SetupPage() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [sqlCode, setSqlCode] = useState('');

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/verify-setup');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to check status:', error);
    }
    setLoading(false);
  };

  const createTables = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/setup', { method: 'POST' });
      const result = await response.json();
      if (result.success) {
        await checkStatus();
      }
    } catch (error) {
      console.error('Failed to create tables:', error);
    }
    setLoading(false);
  };

  const getStorageSQL = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/create-storage', { method: 'POST' });
      const result = await response.json();
      if (result.success) {
        setSqlCode(result.sql);
      }
    } catch (error) {
      console.error('Failed to get SQL:', error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[var(--canvas)] p-8">
      <div className="max-w-4xl mx-auto">
        <BlueprintCard figure="SETUP" code="SYS-01" showCorners variant="elevated" padding="lg">
          <h1 className="font-serif text-3xl text-[var(--ink)] mb-6">
            RaptorFlow Setup Status
          </h1>

          {status && (
            <div className="space-y-6">
              {/* Status Overview */}
              <div className="grid grid-cols-2 gap-4">
                <div className={`p-4 rounded-[var(--radius)] ${status.supabase.connected ? 'bg-[var(--success-light)]' : 'bg-[var(--error-light)]'}`}>
                  <h3 className="font-semibold mb-2">Supabase Connection</h3>
                  <p className={`text-sm ${status.supabase.connected ? 'text-[var(--success)]' : 'text-[var(--error)]'}`}>
                    {status.supabase.connected ? '✅ Connected' : '❌ Disconnected'}
                  </p>
                  {status.supabase.error && (
                    <p className="text-xs text-[var(--error)] mt-1">{status.supabase.error}</p>
                  )}
                </div>

                <div className={`p-4 rounded-[var(--radius)] ${status.auth.working ? 'bg-[var(--success-light)]' : 'bg-[var(--error-light)]'}`}>
                  <h3 className="font-semibold mb-2">Authentication System</h3>
                  <p className={`text-sm ${status.auth.working ? 'text-[var(--success)]' : 'text-[var(--error)]'}`}>
                    {status.auth.working ? '✅ Working' : '❌ Issues'}
                  </p>
                </div>

                <div className={`p-4 rounded-[var(--radius)] ${status.tables.user_profiles ? 'bg-[var(--success-light)]' : 'bg-[var(--warning-light)]'}`}>
                  <h3 className="font-semibold mb-2">User Profiles Table</h3>
                  <p className={`text-sm ${status.tables.user_profiles ? 'text-[var(--success)]' : 'text-[var(--warning)]'}`}>
                    {status.tables.user_profiles ? '✅ Exists' : '⚠️ Missing'}
                  </p>
                </div>

                <div className={`p-4 rounded-[var(--radius)] ${status.tables.payments ? 'bg-[var(--success-light)]' : 'bg-[var(--warning-light)]'}`}>
                  <h3 className="font-semibold mb-2">Payments Table</h3>
                  <p className={`text-sm ${status.tables.payments ? 'text-[var(--success)]' : 'text-[var(--warning)]'}`}>
                    {status.tables.payments ? '✅ Exists' : '⚠️ Missing'}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-4">
                <h3 className="font-semibold text-[var(--ink)]">Required Actions:</h3>

                {(!status.tables.user_profiles || !status.tables.payments) && (
                  <div>
                    <BlueprintButton onClick={createTables} disabled={loading} className="w-full">
                      {loading ? 'Creating Tables...' : 'Create Database Tables'}
                    </BlueprintButton>
                    <p className="text-xs text-[var(--secondary)] mt-2">
                      Creates user_profiles and payments tables with proper RLS policies
                    </p>
                  </div>
                )}

                <div>
                  <BlueprintButton onClick={getStorageSQL} disabled={loading} variant="secondary" className="w-full">
                    {loading ? 'Generating...' : 'Get Storage Setup SQL'}
                  </BlueprintButton>
                  <p className="text-xs text-[var(--secondary)] mt-2">
                    Generates SQL for creating storage buckets and policies
                  </p>
                </div>

                {sqlCode && (
                  <div className="mt-4">
                    <h4 className="font-semibold mb-2">Storage Setup SQL:</h4>
                    <div className="bg-[var(--canvas)] border border-[var(--structure)] rounded-[var(--radius)] p-4">
                      <pre className="text-xs font-mono text-[var(--ink)] whitespace-pre-wrap">
                        {sqlCode}
                      </pre>
                    </div>
                    <div className="mt-2 p-3 bg-[var(--blueprint)]/10 rounded-[var(--radius)]">
                      <p className="text-sm font-technical text-[var(--blueprint)]">
                        1. Go to <a href="https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/sql" target="_blank" className="underline">Supabase SQL Editor</a><br/>
                        2. Copy and paste the SQL above<br/>
                        3. Click "Run" to execute
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Next Steps */}
              {status.tables.user_profiles && status.tables.payments && (
                <div className="mt-6 p-4 bg-[var(--success-light)] border border-[var(--success)] rounded-[var(--radius)]">
                  <h3 className="font-semibold text-[var(--success)] mb-2">✅ Database Ready!</h3>
                  <p className="text-sm text-[var(--secondary)] mb-4">
                    Your database is set up. Now you need to:
                  </p>
                  <ol className="list-decimal list-inside space-y-1 text-sm text-[var(--secondary)]">
                    <li>Update SUPABASE_SERVICE_ROLE_KEY in .env.local</li>
                    <li>Run the storage setup SQL above</li>
                    <li>Test authentication at <a href="/login" className="text-[var(--blueprint)] underline">/login</a></li>
                  </ol>
                </div>
              )}
            </div>
          )}

          <div className="mt-6 flex gap-4">
            <BlueprintButton onClick={checkStatus} variant="secondary" className="flex-1">
              Refresh Status
            </BlueprintButton>
            <BlueprintButton onClick={() => window.open('/login', '_blank')} className="flex-1">
              Test Login
            </BlueprintButton>
          </div>
        </BlueprintCard>
      </div>
    </div>
  );
}
