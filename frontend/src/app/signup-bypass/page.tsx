"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { BlueprintCard } from '@/components/ui/BlueprintCard';

const BlueprintButton = dynamic(() => import('@/components/ui/BlueprintButton').then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export const runtime = 'edge';

export default function SignupBypassPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const router = useRouter();

  const handleBypassSignup = async () => {
    setLoading(true);
    setResult(null);

    try {
      // Create mock user session directly
      const mockUserId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      // Store mock user in localStorage
      const mockUser = {
        id: mockUserId,
        email: email,
        fullName: fullName,
        subscriptionPlan: 'soar',
        subscriptionStatus: 'active',
        createdAt: new Date().toISOString()
      };

      localStorage.setItem('raptorflow_user', JSON.stringify(mockUser));
      localStorage.setItem('raptorflow_session', JSON.stringify({
        access_token: 'bypass-access-token',
        user: mockUser,
        expires_at: new Date(Date.now() + 3600000).toISOString()
      }));

      setResult({
        success: true,
        user: mockUser,
        message: 'Bypass signup successful!'
      });

      // Redirect to pricing after 2 seconds
      setTimeout(() => {
        router.push('/pricing');
      }, 2000);

    } catch (error: any) {
      setResult({
        success: false,
        error: error.message
      });
    }

    setLoading(false);
  };

  const handleTestLogin = async () => {
    // Check if user exists in localStorage
    const userStr = localStorage.getItem('raptorflow_user');
    const sessionStr = localStorage.getItem('raptorflow_session');

    if (userStr && sessionStr) {
      const user = JSON.parse(userStr);
      const session = JSON.parse(sessionStr);

      setResult({
        success: true,
        user: user,
        session: session,
        message: 'User logged in via bypass!'
      });
    } else {
      setResult({
        success: false,
        error: 'No user found in bypass storage'
      });
    }
  };

  return (
    <div className="min-h-screen bg-[var(--canvas)] p-8">
      <div className="max-w-4xl mx-auto">
        <BlueprintCard figure="BYPASS" code="AUTH" showCorners variant="elevated" padding="lg">
          <h1 className="font-serif text-3xl text-[var(--ink)] mb-6">
            🔧 Authentication Bypass
          </h1>

          <div className="space-y-6">
            {/* Status */}
            <BlueprintCard padding="md" className="border-[var(--blueprint)] bg-[var(--blueprint-light)]">
              <h3 className="font-semibold text-[var(--blueprint)] mb-3">
                📋 Current Status
              </h3>
              <p className="text-sm text-[var(--secondary)]">
                Database tables are missing, so authentication is failing.
                This bypass creates a mock user session to test the system.
              </p>
            </BlueprintCard>

            {/* Bypass Form */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors blueprint-focus"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
                  className="w-full h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors blueprint-focus"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--ink)] mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter any password"
                  className="w-full h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors blueprint-focus"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <BlueprintButton
                onClick={handleBypassSignup}
                disabled={loading || !email || !fullName || !password}
                className="flex-1"
              >
                {loading ? '🔄 Creating...' : '🚀 Create Bypass Account'}
              </BlueprintButton>

              <BlueprintButton
                onClick={handleTestLogin}
                className="flex-1"
                variant="secondary"
              >
                🔍 Test Login
              </BlueprintButton>
            </div>

            {/* Results */}
            {result && (
              <div
                className={`p-4 rounded-[var(--radius)] ${
                  result.success
                    ? 'bg-[var(--success-light)] border-[var(--success)]'
                    : 'bg-[var(--error-light)] border-[var(--error)]'
                }`}
              >
                <h3
                  className={`font-semibold mb-2 ${
                    result.success
                      ? 'text-[var(--success)]'
                      : 'text-[var(--error)]'
                  }`}
                >
                  {result.success ? '✅ Success' : '❌ Error'}
                </h3>
                <p className="text-sm text-[var(--secondary)]">
                  {result.message}
                </p>
                {result.user && (
                  <div className="mt-3 p-3 bg-[var(--canvas)] rounded-[var(--radius)]">
                    <p className="text-xs text-[var(--ink)]">
                      <strong>User ID:</strong> {result.user.id}
                    </p>
                    <p className="text-xs text-[var(--ink)]">
                      <strong>Email:</strong> {result.user.email}
                    </p>
                    <p className="text-xs text-[var(--ink)]">
                      <strong>Name:</strong> {result.user.fullName}
                    </p>
                    <p className="text-xs text-[var(--ink)]">
                      <strong>Plan:</strong> {result.user.subscriptionPlan}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Instructions */}
            <BlueprintCard padding="md" className="border-[var(--structure)] bg-[var(--paper)]">
              <h3 className="font-semibold text-[var(--ink)] mb-3">
                📋 Instructions
              </h3>
              <ol className="list-decimal list-inside space-y-2 text-sm text-[var(--secondary)]">
                <li>Fill in the form above with any email, name, and password</li>
                <li>Click "Create Bypass Account" to create a mock user</li>
                <li>You'll be automatically redirected to the pricing page</li>
                <li>Use "Test Login" to verify the bypass is working</li>
                <li>The bypass stores user data in localStorage for testing</li>
              </ol>
            </BlueprintCard>

            {/* Benefits */}
            <BlueprintCard padding="md" className="border-[var(--success)] bg-[var(--success-light)]">
              <h3 className="font-semibold text-[var(--success)] mb-3">
                🎯 Bypass Benefits
              </h3>
              <ul className="list-disc list-inside space-y-2 text-sm text-[var(--secondary)]">
                <li>✅ No database tables required</li>
                <li>✅ Instant account creation</li>
                <li>✅ Full system testing capability</li>
                <li>✅ Works without Supabase setup</li>
                <li>✅ Perfect for development and testing</li>
              </ul>
            </BlueprintCard>

            {/* Limitations */}
            <BlueprintCard padding="md" className="border-[var(--warning)] bg-[var(--warning-light)]">
              <h3 className="font-semibold text-[var(--warning)] mb-3">
                ⚠️ Bypass Limitations
              </h3>
              <ul className="list-disc list-inside space-y-2 text-sm text-[var(--secondary)]">
                <li>❌ Data is stored in localStorage only</li>
                <li>❌ Not suitable for production</li>
                <li>❌ No real database persistence</li>
                <li>❌ No real payment processing</li>
                <li>❌ Session expires after 1 hour</li>
              </ul>
            </BlueprintCard>
          </div>
        </BlueprintCard>
      </div>
    </div>
  );
}
