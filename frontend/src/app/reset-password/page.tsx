"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Eye, EyeOff, Check } from "lucide-react";
import dynamic from 'next/dynamic';

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState("");
  const [isTokenValid, setIsTokenValid] = useState<boolean | null>(null);

  useEffect(() => {
    if (!token) {
      setError('Invalid reset token');
      return;
    }

    // Validate token
    validateToken();
  }, [token]);

  const validateToken = async () => {
    try {
      const response = await fetch('/api/auth/validate-reset-token-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      const data = await response.json();
      setIsTokenValid(response.ok);
      
      if (!response.ok) {
        setError(data.error || 'Invalid or expired reset token');
      }
    } catch (error) {
      setError('Failed to validate reset token');
      setIsTokenValid(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate passwords
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/auth/reset-password-simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsSuccess(true);
      } else {
        setError(data.error || 'Failed to reset password');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isTokenValid === null) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-[var(--ink)] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[var(--secondary)]">Validating reset token...</p>
        </div>
      </div>
    );
  }

  if (isTokenValid === false) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-[var(--error-light)] border border-[var(--error)] rounded-[var(--radius-sm)] p-6 mb-6">
            <h2 className="text-lg font-semibold text-[var(--error)] mb-2">Invalid Reset Link</h2>
            <p className="text-[var(--error)]">{error}</p>
          </div>
          <Link href="/forgot-password" className="text-[var(--ink)] hover:underline">
            Request a new reset link
          </Link>
        </div>
      </div>
    );
  }

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
            <span className="text-2xl">🔐</span>
          </div>
          <span className="font-serif text-2xl tracking-tight font-semibold">RaptorFlow</span>
        </div>

        {/* Message */}
        <div className="relative z-10 max-w-xl">
          <h1 className="font-serif text-6xl leading-[1.1] mb-8 font-medium">
            Create New <br />
            <span className="text-[var(--structure)] opacity-80">Password</span>
          </h1>
          <div className="w-16 h-1 bg-[var(--accent-amber)] mb-8 opacity-80" />
          <p className="text-[var(--structure-subtle)] font-light text-xl leading-relaxed opacity-90">
            Choose a strong, unique password for your RaptorFlow account. Make it memorable but hard to guess.
          </p>
        </div>

        {/* Footer */}
        <div className="relative z-10 flex items-center gap-8 text-xs text-[var(--structure)] font-technical tracking-widest uppercase opacity-70">
          <span>SYS.V.2.0.4</span>
          <span>//</span>
          <span>SECURE_RESET</span>
        </div>
      </div>

      {/* Right Panel - Reset Password Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 md:p-12 relative bg-[var(--paper)]">
        <div className="w-full max-w-md">
          {/* Mobile Logo (Visible only on small screens) */}
          <div className="lg:hidden mb-12 flex items-center justify-center gap-3">
            <div className="w-10 h-10 bg-[var(--ink)] rounded-[var(--radius-sm)] flex items-center justify-center text-[var(--paper)]">
              <span className="text-xl">🔐</span>
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
                  Reset Password
                </h2>
                <p className="text-[var(--secondary)]">
                  Enter your new password below.
                </p>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Password Field */}
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-[var(--ink)] mb-2">
                    New Password
                  </label>
                  <div className="relative">
                    <input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter new password"
                      className="w-full px-4 py-3 pr-12 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder-[var(--ink-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--blueprint)] focus:border-transparent transition-all"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--ink-muted)] hover:text-[var(--ink)]"
                    >
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                  <p className="text-xs text-[var(--ink-muted)] mt-1">
                    Must be at least 8 characters long
                  </p>
                </div>

                {/* Confirm Password Field */}
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-[var(--ink)] mb-2">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Confirm new password"
                      className="w-full px-4 py-3 pr-12 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink)] placeholder-[var(--ink-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--blueprint)] focus:border-transparent transition-all"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--ink-muted)] hover:text-[var(--ink)]"
                    >
                      {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
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
                  disabled={isLoading || !password || !confirmPassword}
                  className="w-full h-12"
                  size="lg"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-[var(--paper)] border-t-transparent rounded-full animate-spin" />
                      <span>Resetting...</span>
                    </div>
                  ) : (
                    <span>Reset Password</span>
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
                Password Reset Successful!
              </h2>
              
              <p className="text-[var(--secondary)] mb-8">
                Your password has been successfully updated. You can now sign in with your new password.
              </p>

              <BlueprintButton
                onClick={() => router.push('/login')}
                className="w-full"
                size="lg"
              >
                Sign In with New Password
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
