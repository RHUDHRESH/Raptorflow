"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, ArrowLeft, Check } from "lucide-react";
import dynamic from 'next/dynamic';

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export default function ForgotPasswordSimplePage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState("");
  const [resetLink, setResetLink] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch('/api/auth/forgot-password-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsSuccess(true);
        if (data.resetLink) {
          setResetLink(data.resetLink);
        }
      } else {
        setError(data.error || 'Failed to send reset email');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--canvas)] flex relative overflow-hidden">
      {/* Left Panel - Brand / Art (Hidden on Mobile) */}
      <div className="hidden lg:flex w-1/2 bg-[var(--ink)] relative flex-col justify-between p-16 text-[var(--paper)] overflow-hidden">
        {/* Texture */}
        <div className="absolute inset-0 opacity-[0.05]"
          style={{
            backgroundImage: "url('/textures/paper-grain.png')",
            backgroundRepeat: "repeat",
          }}
        />

        {/* Brand Logo Area */}
        <div className="relative z-10 flex items-center gap-4">
          <div className="w-12 h-12 bg-[var(--paper)] rounded-[var(--radius-md)] flex items-center justify-center text-[var(--ink)] shadow-md">
            <Mail size={28} strokeWidth={1.5} />
          </div>
          <span className="font-serif text-2xl tracking-tight font-semibold">RaptorFlow</span>
        </div>

        {/* Message */}
        <div className="relative z-10 max-w-xl">
          <h1 className="font-serif text-6xl leading-[1.1] mb-8 font-medium">
            Password <br />
            <span className="text-[var(--structure)] opacity-80">Recovery (Testing)</span>
          </h1>
          <div className="w-16 h-1 bg-[var(--accent-amber)] mb-8 opacity-80" />
          <p className="text-[var(--structure-subtle)] font-light text-xl leading-relaxed opacity-90">
            Simple version for testing email functionality. Check console for reset link.
          </p>
        </div>

        {/* Footer */}
        <div className="relative z-10 flex items-center gap-8 text-xs text-[var(--structure)] font-technical tracking-widest uppercase opacity-70">
          <span>SYS.V.2.0.4</span>
          <span>//</span>
          <span>TESTING_MODE</span>
        </div>
      </div>

      {/* Right Panel - Forgot Password Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 md:p-12 relative bg-[var(--paper)]">
        <div className="w-full max-w-md">
          {/* Mobile Logo (Visible only on small screens) */}
          <div className="lg:hidden mb-12 flex items-center justify-center gap-3">
            <div className="w-10 h-10 bg-[var(--ink)] rounded-[var(--radius-sm)] flex items-center justify-center text-[var(--paper)]">
              <Mail size={24} strokeWidth={1.5} />
            </div>
            <span className="font-serif text-2xl text-[var(--ink)]">RaptorFlow</span>
          </div>

          {/* Back to Login */}
          <div className="mb-8">
            <Link 
              href="/login" 
              className="inline-flex items-center gap-2 text-sm text-[var(--ink-secondary)] hover:text-[var(--ink)] transition-colors"
            >
              <ArrowLeft size={16} />
              Back to Sign In
            </Link>
          </div>

          {!isSuccess ? (
            <>
              {/* Header */}
              <div className="mb-8">
                <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">
                  Forgot Password? (Testing)
                </h2>
                <p className="text-[var(--secondary)]">
                  Enter your email address to test the password reset functionality.
                </p>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Email Field */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-[var(--ink)] mb-2">
                    Email Address
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email address"
                    className="w-full px-4 py-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder-[var(--ink-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--blueprint)] focus:border-transparent transition-all"
                    required
                  />
                </div>

                {/* Error Message */}
                {error && (
                  <div className="rounded-[var(--radius-sm)] bg-[var(--error-light)] border border-[var(--error)] p-4">
                    <p className="text-sm text-[var(--error)]">{error}</p>
                  </div>
                )}

                {/* Submit Button */}
                <BlueprintButton
                  type="submit"
                  disabled={isLoading || !email}
                  className="w-full h-12"
                  size="lg"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-[var(--paper)] border-t-transparent rounded-full animate-spin" />
                      <span>Processing...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-2">
                      <Mail size={18} />
                      <span>Test Reset Link</span>
                    </div>
                  )}
                </BlueprintButton>
              </form>
            </>
          ) : (
            /* Success State */
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-[var(--success-light)] rounded-full flex items-center justify-center mx-auto mb-6">
                <Check size={32} className="text-[var(--success)]" />
              </div>
              
              <h2 className="font-serif text-2xl text-[var(--ink)] mb-4">
                Reset Link Generated!
              </h2>
              
              <p className="text-[var(--secondary)] mb-8">
                Check the browser console for the reset link, or use the link below:
              </p>
              
              {resetLink && (
                <div className="bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius-sm)] p-4 mb-8">
                  <p className="text-xs text-[var(--ink)] mb-2">Reset Link:</p>
                  <p className="text-[var(--ink)] break-all font-mono text-xs">
                    {resetLink}
                  </p>
                  <button
                    onClick={() => navigator.clipboard.writeText(resetLink)}
                    className="mt-2 text-xs text-[var(--accent)] hover:underline"
                  >
                    Copy Link
                  </button>
                </div>
              )}

              <BlueprintButton
                onClick={() => window.open(resetLink, '_blank')}
                className="w-full mb-4"
                size="lg"
              >
                Test Reset Link
              </BlueprintButton>

              <BlueprintButton
                onClick={() => router.push('/login')}
                className="w-full"
                size="lg"
                variant="outline"
              >
                Back to Sign In
              </BlueprintButton>
            </div>
          )}

          {/* Legal Links Footer */}
          <div className="mt-8 pt-8 border-t border-[var(--border)] flex justify-center gap-6 text-xs text-[var(--ink-muted)]">
            <a href="/legal/terms" className="hover:text-[var(--ink)] transition-colors">Terms</a>
            <a href="/legal/privacy" className="hover:text-[var(--ink)] transition-colors">Privacy</a>
            <a href="/support" className="hover:text-[var(--ink)] transition-colors">Help</a>
          </div>
        </div>
      </div>
    </div>
  );
}
