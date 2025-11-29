import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { sanitizeInput } from '../utils/sanitize';
import { ArrowRight, Lock, Mail, AlertCircle, CheckCircle2, Chrome, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { LuxeInput, LuxeButton, LuxeHeading } from '../components/ui/PremiumUI';
import { pageTransition, fadeInUp, shimmer } from '../utils/animations';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [isSupabaseReady, setIsSupabaseReady] = useState(true);

  const { login, loginWithGoogle, skipLoginDev, loading, error: authError, isAuthenticated, onboardingCompleted, subscription } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  useEffect(() => {
    const url = import.meta.env.VITE_SUPABASE_URL;
    const key = import.meta.env.VITE_SUPABASE_ANON_KEY;
    if (!url || !key) {
      setIsSupabaseReady(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && !loading) {
      if (!onboardingCompleted) {
        navigate('/onboarding', { replace: true });
      } else if (!subscription || subscription.plan === 'free' || (subscription.status !== 'active' && subscription.status !== 'trialing')) {
        // Redirect to payment/billing if no active paid subscription
        navigate('/billing', { replace: true });
      } else {
        navigate(from, { replace: true });
      }
    }
  }, [isAuthenticated, loading, navigate, from, onboardingCompleted, subscription]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const sanitizedValue = sanitizeInput(value);
    setFormData(prev => ({ ...prev, [name]: sanitizedValue }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    // Bypass auth if Supabase is not ready (Demo Mode) OR specific dev credentials
    if (!isSupabaseReady || (import.meta.env.DEV && formData.email === 'user' && formData.password === 'pass')) {
      const result = await skipLoginDev();
      if (result.success) {
        navigate(from, { replace: true });
      } else {
        setErrors({ submit: result.error });
      }
      return;
    }

    const result = await login(formData.email, formData.password);

    if (result.success) {
      navigate(from, { replace: true });
    } else {
      setErrors({ submit: result.error });
    }
  };

  const handleGoogleLogin = async () => {
    setErrors({});
    const result = await loginWithGoogle();
    if (!result.success) {
      setErrors({ submit: result.error });
    }
  };

  const handleDevLogin = async () => {
    setErrors({});
    const result = await skipLoginDev();
    if (!result.success) {
      setErrors({ submit: result.error });
    }
  };

  return (
    <motion.div
      className="flex min-h-screen w-full bg-white"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageTransition}
    >
      {/* Left Panel - Visuals */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-neutral-900 text-white overflow-hidden flex-col justify-between p-12">
        <div className="relative z-10">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-white/20 backdrop-blur-md border border-white/10 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="text-xl font-bold tracking-widest uppercase font-sans">Raptorflow</span>
          </div>
        </div>

        <motion.div
          className="relative z-10 max-w-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h1 className="text-6xl font-serif font-bold leading-tight tracking-tight mb-6 text-white">
            Orchestrate your <br />
            <span className="text-neutral-400">
              digital empire.
            </span>
          </h1>
          <p className="text-lg text-neutral-400 leading-relaxed font-sans">
            The advanced agentic workspace for high-velocity teams.
            Manage campaigns, cohorts, and content pipelines in one unified interface.
          </p>
        </motion.div>

        <div className="relative z-10 flex items-center gap-4 text-sm text-neutral-500 font-mono">
          <span>v2.4.0-beta</span>
          <span className="h-1 w-1 rounded-full bg-neutral-700" />
          <span>System Operational</span>
        </div>

        {/* Abstract Background Elements */}
        <motion.div
          className="absolute top-0 right-0 -translate-y-1/4 translate-x-1/4 w-[800px] h-[800px] bg-gradient-to-br from-neutral-800/30 to-transparent rounded-full blur-3xl pointer-events-none"
          animate={{ scale: [1, 1.1, 1], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <div className="absolute bottom-0 left-0 translate-y-1/4 -translate-x-1/4 w-[600px] h-[600px] bg-neutral-900/50 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-soft-light pointer-events-none" />
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-12 bg-white relative">
        <motion.div
          className="w-full max-w-md space-y-8"
          variants={fadeInUp}
        >
          <div className="text-center lg:text-left">
            <LuxeHeading level={2} className="mb-2">Welcome back</LuxeHeading>
            <p className="text-neutral-500">Enter your credentials to access the workspace.</p>
          </div>

          {/* Dev/Demo Mode implicitly handled via Sign In if config missing */}
          {!isSupabaseReady && (
             <div className="mb-4 p-3 bg-blue-50 text-blue-700 text-sm rounded-lg border border-blue-100">
                <strong>Demo Mode Available:</strong> Sign in with any credentials to access the dashboard.
             </div>
          )}

          <div className="space-y-4">
            <LuxeButton
              variant="secondary"
              className="w-full"
              onClick={handleGoogleLogin}
              disabled={loading || !isSupabaseReady}
              icon={Chrome}
            >
              Continue with Google
            </LuxeButton>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-neutral-200"></div>
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-neutral-400 font-medium tracking-wider">Or continue with email</span>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <LuxeInput
                label="Email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder="name@company.com"
                error={errors.email}
              />

              <div className="relative">
                <LuxeInput
                  label="Password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  error={errors.password}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-[34px] text-neutral-400 hover:text-neutral-600 transition-colors"
                >
                  {showPassword ? <CheckCircle2 className="h-5 w-5" /> : <Lock className="h-5 w-5" />}
                </button>
              </div>

              {(errors.submit || authError) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="p-3 rounded-lg bg-red-50 border border-red-100 flex items-start gap-2 text-sm text-red-600"
                >
                  <AlertCircle className="h-5 w-5 shrink-0" />
                  <span>{errors.submit || authError}</span>
                </motion.div>
              )}

              <LuxeButton
                type="submit"
                className="w-full"
                disabled={loading}
                isLoading={loading}
                icon={ArrowRight}
              >
                Sign In
              </LuxeButton>
            </form>
          </div>

          <div className="pt-6 text-center">
            <p className="text-sm text-neutral-500">
              Don't have an account?{' '}
              <Link to="/register" className="font-semibold text-neutral-900 hover:underline">
                Create account
              </Link>
            </p>
          </div>

          {import.meta.env.DEV && (
            <div className="pt-8 border-t border-neutral-100 space-y-2">
              <button
                onClick={handleDevLogin}
                className="w-full py-2 px-4 rounded-lg border border-dashed border-neutral-300 text-xs font-mono text-neutral-500 hover:bg-neutral-50 hover:text-neutral-900 transition-colors"
              >
                [DEV] Bypass Authentication
              </button>
            </div>
          )}
        </motion.div>

        {/* Footer Links */}
        <div className="absolute bottom-8 left-0 w-full text-center lg:text-left lg:pl-12">
          <div className="flex gap-6 justify-center lg:justify-start text-xs text-neutral-400 uppercase tracking-wider">
            <Link to="/privacy" className="hover:text-neutral-600">Privacy</Link>
            <Link to="/terms" className="hover:text-neutral-600">Terms</Link>
            <a href="mailto:support@raptorflow.in" className="hover:text-neutral-600">Help</a>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Login;
