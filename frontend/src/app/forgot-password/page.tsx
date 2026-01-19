"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, ArrowLeft, Check } from "lucide-react";
import dynamic from 'next/dynamic';
import AuthLayout from "@/components/auth/AuthLayout";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsSuccess(true);
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
    <AuthLayout
      title={
        <>
          Password <br />
          <span className="text-[var(--structure)] opacity-80">Recovery</span>
        </>
      }
      subtitle="We'll send you a secure link to reset your password. Check your email for the reset instructions."
      icon={<Mail size={28} strokeWidth={1.5} />}
      sysCode="SYS.V.2.0.4 // SECURE_EMAIL"
    >
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
              Forgot Password?
            </h2>
            <p className="text-[var(--secondary)]">
              Enter your email address and we'll send you a link to reset your password.
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
                  <span>Sending...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <Mail size={18} />
                  <span>Send Reset Link</span>
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
            Reset Link Sent!
          </h2>

          <p className="text-[var(--secondary)] mb-8">
            We've sent a password reset link to <br />
            <span className="font-semibold text-[var(--ink)]">{email}</span>
          </p>

          <div className="bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius-sm)] p-4 mb-8">
            <p className="text-sm text-[var(--ink)]">
              <strong>Next steps:</strong><br />
              1. Check your email inbox<br />
              2. Click the reset link in the email<br />
              3. Create your new password
            </p>
          </div>

          <BlueprintButton
            onClick={() => router.push('/login')}
            className="w-full"
            size="lg"
          >
            Back to Sign In
          </BlueprintButton>
        </div>
      )}
    </AuthLayout>
  );
}
