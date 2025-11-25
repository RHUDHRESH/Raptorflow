import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { sanitizeInput } from '../utils/sanitize';
import { ArrowRight, Lock, Mail, AlertCircle, CheckCircle2, Loader2, Github, Chrome } from 'lucide-react';
import { cn } from '../utils/cn';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [isSupabaseReady, setIsSupabaseReady] = useState(true);

  const { login, loginWithGoogle, skipLoginDev, loading, error: authError, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  useEffect(() => {
    // Check if Supabase env vars are actually loaded
    const url = import.meta.env.VITE_SUPABASE_URL;
    const key = import.meta.env.VITE_SUPABASE_ANON_KEY;
    if (!url || !key) {
      setIsSupabaseReady(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && !loading) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, loading, navigate, from]);

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
    <div className="flex min-h-screen w-full bg-white">
      {/* Left Panel - Visuals */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-black text-white overflow-hidden flex-col justify-between p-12">
        <div className="relative z-10">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-white/20 backdrop-blur-md border border-white/10" />
            <span className="text-xl font-bold tracking-widest uppercase font-mono">Raptorflow</span>
          </div>
        </div>

        <div className="relative z-10 max-w-lg">
          <h1 className="text-6xl font-bold leading-tight tracking-tight mb-6">
            Orchestrate your <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-neutral-200 to-neutral-500">
              digital empire.
            </span>
          </h1>
          <p className="text-lg text-neutral-400 leading-relaxed">
            The advanced agentic workspace for high-velocity teams.
            Manage campaigns, cohorts, and content pipelines in one unified interface.
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-4 text-sm text-neutral-500 font-mono">
          <span>v2.4.0-beta</span>
          <span className="h-1 w-1 rounded-full bg-neutral-700" />
          <span>System Operational</span>
        </div>

        {/* Abstract Background Elements */}
        <div className="absolute top-0 right-0 -translate-y-1/4 translate-x-1/4 w-[800px] h-[800px] bg-gradient-to-br from-neutral-800/30 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 translate-y-1/4 -translate-x-1/4 w-[600px] h-[600px] bg-neutral-900/50 rounded-full blur-3xl pointer-events-none" />

        {/* Grid Pattern Overlay */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-soft-light pointer-events-none" />
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-12 bg-white relative">
        <div className="w-full max-w-md space-y-8">

          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-bold tracking-tight text-neutral-900">Welcome back</h2>
            <p className="mt-2 text-neutral-500">Enter your credentials to access the workspace.</p>
          </div>

          {!isSupabaseReady && (
            <div className="rounded-lg bg-amber-50 p-4 border border-amber-200">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-amber-600 shrink-0" />
                <div className="text-sm text-amber-800">
                  <p className="font-semibold">Configuration Missing</p>
                  <p className="mt-1">Supabase environment variables are missing. Please check your <code className="bg-amber-100 px-1 py-0.5 rounded">.env</code> file.</p>
                  <p className="mt-2 text-xs font-mono">Required: VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY</p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <button
              onClick={handleGoogleLogin}
              disabled={loading || !isSupabaseReady}
              className="w-full flex items-center justify-center gap-3 h-12 px-4 rounded-xl border border-neutral-200 bg-white text-neutral-900 font-medium transition-all hover:bg-neutral-50 hover:border-neutral-300 focus:ring-2 focus:ring-black/5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Chrome className="h-5 w-5" />
              Continue with Google
            </button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-neutral-200"></div>
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-neutral-400 font-medium">Or continue with email</span>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-neutral-700">Email</label>
                <div className="relative">
                  <input
                    name="email"
                    type="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className={cn(
                      "w-full h-12 px-4 rounded-xl border bg-neutral-50/50 text-neutral-900 placeholder:text-neutral-400 transition-all focus:bg-white focus:ring-2 focus:ring-black/5 outline-none",
                      errors.email ? "border-red-300 focus:border-red-300" : "border-neutral-200 focus:border-neutral-400"
                    )}
                    placeholder="name@company.com"
                  />
                  <Mail className="absolute right-4 top-3.5 h-5 w-5 text-neutral-400 pointer-events-none" />
                </div>
                {errors.email && <p className="text-xs text-red-500 font-medium">{errors.email}</p>}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-neutral-700">Password</label>
                <div className="relative">
                  <input
                    name="password"
                    type={showPassword ? "text" : "password"}
                    required
                    value={formData.password}
                    onChange={handleChange}
                    className={cn(
                      "w-full h-12 px-4 rounded-xl border bg-neutral-50/50 text-neutral-900 placeholder:text-neutral-400 transition-all focus:bg-white focus:ring-2 focus:ring-black/5 outline-none",
                      errors.password ? "border-red-300 focus:border-red-300" : "border-neutral-200 focus:border-neutral-400"
                    )}
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-3.5 text-neutral-400 hover:text-neutral-600 transition-colors"
                  >
                    {showPassword ? <CheckCircle2 className="h-5 w-5" /> : <Lock className="h-5 w-5" />}
                  </button>
                </div>
                {errors.password && <p className="text-xs text-red-500 font-medium">{errors.password}</p>}
              </div>

              {(errors.submit || authError) && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-100 flex items-start gap-2 text-sm text-red-600">
                  <AlertCircle className="h-5 w-5 shrink-0" />
                  <span>{errors.submit || authError}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !isSupabaseReady}
                className="group w-full h-12 flex items-center justify-center gap-2 rounded-xl bg-black text-white font-medium transition-all hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-black/10 hover:shadow-xl hover:shadow-black/20 active:scale-[0.99]"
              >
                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : (
                  <>
                    Sign In <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="pt-6 text-center">
            <p className="text-sm text-neutral-500">
              Don't have an account?{' '}
              <Link to="/register" className="font-semibold text-black hover:underline">
                Create account
              </Link>
            </p>
          </div>

          {import.meta.env.DEV && (
            <div className="pt-8 border-t border-neutral-100">
              <button
                onClick={handleDevLogin}
                className="w-full py-2 px-4 rounded-lg border border-dashed border-neutral-300 text-xs font-mono text-neutral-500 hover:bg-neutral-50 hover:text-neutral-900 transition-colors"
              >
                [DEV] Bypass Authentication
              </button>
            </div>
          )}
        </div>

        {/* Footer Links */}
        <div className="absolute bottom-8 left-0 w-full text-center lg:text-left lg:pl-12">
          <div className="flex gap-6 justify-center lg:justify-start text-xs text-neutral-400">
            <a href="#" className="hover:text-neutral-600">Privacy Policy</a>
            <a href="#" className="hover:text-neutral-600">Terms of Service</a>
            <a href="#" className="hover:text-neutral-600">Help Center</a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
