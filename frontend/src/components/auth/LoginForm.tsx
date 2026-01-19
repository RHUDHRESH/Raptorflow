/**
 * 🔐 LOGIN FORM - Quiet Luxury Edition
 */

'use client';

import React, { useState } from 'react';
import { useAuth } from './AuthProvider';
import { Button } from '@/components/ui/button';
import { Loader2, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { GoogleOAuthButton } from './OAuthButton';

interface FormData {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export default function LoginForm() {
  const { login, isLoading } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      await login(formData.email, formData.password);
      // Successful login - redirect to system check
      window.location.href = '/system-check';
    } catch (error) {
      console.error('Login failed:', error);
      setErrors({
        general: error instanceof Error ? error.message : 'Login failed. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-sm mx-auto">
      <div className="mb-8">
        <h2 className="font-serif text-3xl text-[var(--ink)] mb-2">
          Welcome Back
        </h2>
        <p className="text-[var(--ink-secondary)]">
          Enter your credentials to access the system.
        </p>
      </div>

      {/* Google OAuth Button */}
      <div className="mb-6">
        <GoogleOAuthButton redirectTo="/system-check" />
      </div>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[var(--border)]"></div>
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-[var(--paper)] px-3 text-[var(--ink-muted)] font-technical tracking-wider">
            or continue with email
          </span>
        </div>
      </div>

      <form className="space-y-6" onSubmit={handleSubmit}>
        {/* Email Field */}
        <div className="space-y-2">
          <label htmlFor="email" className="block text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wider">
            Email address
          </label>
          <div className="relative">
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
              className={`block w-full rounded-[var(--radius-sm)] border-0 ring-1 ring-inset ${errors.email
                ? 'ring-[var(--error)] focus:ring-[var(--error)]'
                : 'ring-[var(--border)] focus:ring-[var(--ink)]'
                } bg-[var(--paper)] py-3 px-4 text-[var(--ink)] placeholder:text-[var(--ink-muted)] focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6 transition-all shadow-sm`}
              placeholder="name@company.com"
            />
          </div>
          {errors.email && (
            <p className="text-xs text-[var(--error)] mt-1">{errors.email}</p>
          )}
        </div>

        {/* Password Field */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="block text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wider">
              Password
            </label>
          </div>
          <div className="relative">
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={formData.password}
              onChange={handleChange}
              className={`block w-full rounded-[var(--radius-sm)] border-0 ring-1 ring-inset ${errors.password
                ? 'ring-[var(--error)] focus:ring-[var(--error)]'
                : 'ring-[var(--border)] focus:ring-[var(--ink)]'
                } bg-[var(--paper)] py-3 px-4 text-[var(--ink)] placeholder:text-[var(--ink-muted)] focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6 transition-all shadow-sm`}
              placeholder="••••••••"
            />
          </div>
          {errors.password && (
            <p className="text-xs text-[var(--error)] mt-1">{errors.password}</p>
          )}
        </div>

        {/* General Error */}
        {errors.general && (
          <div className="rounded-[var(--radius-sm)] bg-[var(--error-light)] border border-[var(--error)] p-4">
            <p className="text-sm text-[var(--error)] font-medium text-center">{errors.general}</p>
          </div>
        )}

        {/* Submit Button */}
        <div>
          <Button
            type="submit"
            disabled={isSubmitting || isLoading}
            className="w-full h-12 bg-[var(--ink)] hover:bg-[var(--ink)]/90 text-[var(--paper)] text-sm font-medium tracking-wide"
          >
            {(isSubmitting || isLoading) ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                AUTHENTICATING...
              </>
            ) : (
              <>
                Sign In <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>

        <div className="text-center mt-6">
          <p className="text-sm text-[var(--ink-secondary)]">
            No account?{' '}
            <Link href="/signup" className="font-semibold text-[var(--ink)] hover:underline decoration-1 underline-offset-4">
              Create a workspace
            </Link>
          </p>
          <p className="text-sm text-[var(--ink-secondary)]">
            <Link href="/forgot-password" className="font-semibold text-[var(--ink)] hover:underline decoration-1 underline-offset-4">
              Forgot your password?
            </Link>
          </p>
        </div>
      </form>
    </div>
  );
}
