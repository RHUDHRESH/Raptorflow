import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowRight, Lock, Mail, AlertCircle, Eye, EyeOff, Sparkles, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Auth Page
 * 
 * Main authentication page for RaptorFlow.
 * Handles email/password login with proper validation and redirects.
 * 
 * Features:
 * - Email/password authentication
 * - Form validation
 * - Loading states
 * - Error handling
 * - Auto-redirect for authenticated users
 * - Redirect to /workspace on success
 */
export default function AuthPage() {
    // Form state
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [formError, setFormError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Auth context
    const { status, user, login } = useAuth();
    const navigate = useNavigate();

    // Redirect authenticated users to workspace
    useEffect(() => {
        if (status === 'authenticated' && user) {
            navigate('/workspace', { replace: true });
        }
    }, [status, user, navigate]);

    // Handle form submission
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError(null);

        // Basic validation
        if (!email || !password) {
            setFormError('Email and password are required');
            return;
        }

        // Simple email format check
        if (!email.includes('@') || email.length < 3) {
            setFormError('Please enter a valid email address');
            return;
        }

        // Submit login
        setIsSubmitting(true);

        try {
            const result = await login(email, password);

            if (result.success) {
                // Success - redirect will happen via useEffect
                navigate('/workspace', { replace: true });
            } else {
                // Show error from auth service
                setFormError(result.error || 'Failed to sign in. Please try again.');
            }
        } catch (error) {
            setFormError('An unexpected error occurred. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Show loading state while checking session
    if (status === 'loading') {
        return (
            <div className="flex min-h-screen items-center justify-center bg-white">
                <div className="text-center">
                    <Loader2 className="h-8 w-8 animate-spin text-neutral-900 mx-auto mb-4" />
                    <p className="text-sm text-neutral-500">Checking your session...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen w-full bg-white">
            {/* Left Panel - Brand & Visuals */}
            <div className="hidden lg:flex lg:w-1/2 relative bg-neutral-900 text-white overflow-hidden flex-col justify-between p-12">
                {/* Logo */}
                <div className="relative z-10">
                    <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-full bg-white/20 backdrop-blur-md border border-white/10 flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <span className="text-xl font-bold tracking-widest uppercase font-serif">
                            RaptorFlow
                        </span>
                    </div>
                </div>

                {/* Hero Content */}
                <motion.div
                    className="relative z-10 max-w-lg"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h1 className="text-6xl font-serif font-bold leading-tight tracking-tight mb-6">
                        Orchestrate your{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-neutral-200 to-neutral-500">
                            digital empire.
                        </span>
                    </h1>
                    <p className="text-lg text-neutral-400 leading-relaxed font-sans">
                        The advanced agentic workspace for high-velocity teams. Manage campaigns, cohorts, and
                        content pipelines in one unified interface.
                    </p>
                </motion.div>

                {/* Version Info */}
                <div className="relative z-10 flex items-center gap-4 text-sm text-neutral-500 font-mono">
                    <span>v2.4.0-beta</span>
                    <span className="h-1 w-1 rounded-full bg-neutral-700" />
                    <span>System Operational</span>
                </div>

                {/* Background Effects */}
                <motion.div
                    className="absolute top-0 right-0 -translate-y-1/4 translate-x-1/4 w-[800px] h-[800px] bg-gradient-to-br from-neutral-800/30 to-transparent rounded-full blur-3xl pointer-events-none"
                    animate={{ scale: [1, 1.1, 1], opacity: [0.3, 0.5, 0.3] }}
                    transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
                />
                <div className="absolute bottom-0 left-0 translate-y-1/4 -translate-x-1/4 w-[600px] h-[600px] bg-neutral-900/50 rounded-full blur-3xl pointer-events-none" />
            </div>

            {/* Right Panel - Auth Form */}
            <div className="flex-1 flex items-center justify-center p-8 lg:p-12 bg-white relative">
                <motion.div
                    className="w-full max-w-md space-y-8"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    {/* Header */}
                    <div className="text-center lg:text-left">
                        <h2 className="text-3xl font-bold text-neutral-900 mb-2">Welcome back</h2>
                        <p className="text-neutral-500">Enter your credentials to access the workspace.</p>
                    </div>

                    {/* Login Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Email Input */}
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-2">
                                Email
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full pl-12 pr-4 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent transition-all"
                                    placeholder="name@company.com"
                                    disabled={isSubmitting}
                                />
                            </div>
                        </div>

                        {/* Password Input */}
                        <div>
                            <label
                                htmlFor="password"
                                className="block text-sm font-medium text-neutral-700 mb-2"
                            >
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" />
                                <input
                                    id="password"
                                    name="password"
                                    type={showPassword ? 'text' : 'password'}
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-12 pr-12 py-3 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent transition-all"
                                    placeholder="••••••••"
                                    disabled={isSubmitting}
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 transition-colors"
                                    tabIndex={-1}
                                >
                                    {showPassword ? (
                                        <EyeOff className="h-5 w-5" />
                                    ) : (
                                        <Eye className="h-5 w-5" />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Error Message */}
                        <AnimatePresence>
                            {formError && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="p-3 rounded-lg bg-red-50 border border-red-100 flex items-start gap-2 text-sm text-red-600"
                                >
                                    <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                                    <span>{formError}</span>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full bg-neutral-900 text-white py-3 px-4 rounded-lg font-medium hover:bg-neutral-800 focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                    <span>Signing in...</span>
                                </>
                            ) : (
                                <>
                                    <span>Sign In</span>
                                    <ArrowRight className="h-5 w-5" />
                                </>
                            )}
                        </button>
                    </form>

                    {/* Sign Up Link */}
                    <div className="pt-6 text-center">
                        <p className="text-sm text-neutral-500">
                            Don't have an account?{' '}
                            <Link to="/register" className="font-semibold text-neutral-900 hover:underline">
                                Create account
                            </Link>
                        </p>
                    </div>

                    {/* Dev Mode Bypass */}
                    {(import.meta as any).env?.DEV && (
                        <div className="pt-8 border-t border-neutral-100">
                            <p className="text-xs text-neutral-400 text-center mb-2 font-mono">
                                Development Mode
                            </p>
                            <Link
                                to="/debug/auth"
                                className="block w-full py-2 px-4 rounded-lg border border-dashed border-neutral-300 text-xs font-mono text-neutral-500 hover:bg-neutral-50 hover:text-neutral-900 transition-colors text-center"
                            >
                                Open Auth Debug Console
                            </Link>
                        </div>
                    )}
                </motion.div>

                {/* Footer Links */}
                <div className="absolute bottom-8 left-0 w-full text-center lg:text-left lg:pl-12">
                    <div className="flex gap-6 justify-center lg:justify-start text-xs text-neutral-400 uppercase tracking-wider">
                        <Link to="/privacy" className="hover:text-neutral-600 transition-colors">
                            Privacy
                        </Link>
                        <Link to="/terms" className="hover:text-neutral-600 transition-colors">
                            Terms
                        </Link>
                        <a
                            href="mailto:support@raptorflow.in"
                            className="hover:text-neutral-600 transition-colors"
                        >
                            Help
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
}
