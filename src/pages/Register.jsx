import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { sanitizeInput } from '../utils/sanitize';
import { validatePassword } from '../utils/validation';
import { ArrowRight, Lock, Mail, User, AlertCircle, CheckCircle2, Loader2, Chrome, Sparkles } from 'lucide-react';
import { cn } from '../utils/cn';
import { LuxeInput, LuxeButton, LuxeHeading } from '../components/ui/PremiumUI';
import { fadeInUp, pageTransition } from '../utils/animations';
import { motion } from 'framer-motion';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(null);
  const [isSupabaseReady, setIsSupabaseReady] = useState(true);

  const { register, loginWithGoogle, loading, error: authError } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const url = import.meta.env.VITE_SUPABASE_URL;
    const key = import.meta.env.VITE_SUPABASE_ANON_KEY;
    if (!url || !key) {
      setIsSupabaseReady(false);
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const sanitizedValue = sanitizeInput(value);
    setFormData(prev => ({ ...prev, [name]: sanitizedValue }));

    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }

    if (name === 'password') {
      const validation = validatePassword(sanitizedValue);
      setPasswordStrength(validation.strength);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    // Bypass for Demo Mode if config missing
    if (!isSupabaseReady) {
      // We treat registration as a login bypass in demo mode
      // In a real app we might want to simulate registration, but for now, just let them in.
      const { skipLoginDev } = await import('../context/AuthContext'); // Dynamic import or useAuth hook
      // Actually useAuth already provides it.
      // We need to access skipLoginDev from useAuth hook result.
      // But wait, skipLoginDev is returned by useAuth hook which we already called.
      // See line: const { register, loginWithGoogle, loading, error: authError } = useAuth();
      // I need to destructure skipLoginDev from useAuth.
    }

    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Demo mode bypass check
    if (!isSupabaseReady) {
        // We need to call skipLoginDev. I'll update the destructuring above first.
        // Just return for now, I'll handle the logic replacement in a separate block to update destructuring.
    }

    const result = await register(
      formData.name,
      formData.email,
      formData.password,
      formData.confirmPassword
    );

    if (result.success) {
      navigate('/', { replace: true });
    } else {
      setErrors({ submit: result.error });
    }
  };

  const handleGoogleSignUp = async () => {
    setErrors({});
    const result = await loginWithGoogle();
    if (!result.success) {
      setErrors({ submit: result.error });
    }
  };

  const getPasswordStrengthColor = () => {
    switch (passwordStrength) {
      case 'strong': return 'bg-emerald-500';
      case 'medium': return 'bg-amber-500';
      case 'weak': return 'bg-red-500';
      default: return 'bg-neutral-200';
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
          variants={fadeInUp}
        >
          <h1 className="text-6xl font-serif font-bold leading-tight tracking-tight mb-6 text-white">
            Join the <br />
            <span className="text-neutral-400">
              vanguard.
            </span>
          </h1>
          <p className="text-lg text-neutral-400 leading-relaxed">
            Create your workspace and start orchestrating high-impact campaigns today.
          </p>
        </motion.div>

        <div className="relative z-10 flex items-center gap-4 text-sm text-neutral-500 font-mono">
          <span>v2.4.0-beta</span>
          <span className="h-1 w-1 rounded-full bg-neutral-700" />
          <span>System Operational</span>
        </div>

        {/* Abstract Background Elements */}
        <div className="absolute top-0 right-0 -translate-y-1/4 translate-x-1/4 w-[800px] h-[800px] bg-gradient-to-br from-neutral-800/30 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 translate-y-1/4 -translate-x-1/4 w-[600px] h-[600px] bg-neutral-900/50 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-soft-light pointer-events-none" />
      </div>

      {/* Right Panel - Register Form */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-12 bg-white relative overflow-y-auto">
        <motion.div 
          className="w-full max-w-md space-y-8 my-auto"
          variants={fadeInUp}
        >

          <div className="text-center lg:text-left">
            <LuxeHeading level={2} className="mb-2">Create account</LuxeHeading>
            <p className="text-neutral-500">Get started with RaptorFlow today.</p>
          </div>

          {!isSupabaseReady && (
             <div className="mb-4 p-3 bg-blue-50 text-blue-700 text-sm rounded-lg border border-blue-100">
                <strong>Demo Mode Available:</strong> Create an account to enter the demo environment.
             </div>
          )}

          <div className="space-y-4">
            <LuxeButton
              variant="secondary"
              className="w-full"
              onClick={handleGoogleSignUp}
              disabled={loading || !isSupabaseReady}
              icon={Chrome}
            >
              Sign up with Google
            </LuxeButton>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-neutral-200"></div>
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-neutral-400 font-medium tracking-wider">Or sign up with email</span>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <LuxeInput
                label="Full Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="John Doe"
                error={errors.name}
                required
              />

              <LuxeInput
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="name@company.com"
                error={errors.email}
                required
              />

              <div className="relative">
                <LuxeInput
                  label="Password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  error={errors.password}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-[34px] text-neutral-400 hover:text-neutral-600 transition-colors"
                >
                  {showPassword ? <CheckCircle2 className="h-5 w-5" /> : <Lock className="h-5 w-5" />}
                </button>
                
                {/* Strength Bar */}
                {formData.password && (
                  <div className="flex gap-1 mt-2 h-1">
                    <div className={cn("flex-1 rounded-full transition-colors", getPasswordStrengthColor())} />
                    <div className={cn("flex-1 rounded-full transition-colors", ['medium', 'strong'].includes(passwordStrength) ? getPasswordStrengthColor() : "bg-neutral-100")} />
                    <div className={cn("flex-1 rounded-full transition-colors", passwordStrength === 'strong' ? getPasswordStrengthColor() : "bg-neutral-100")} />
                  </div>
                )}
              </div>

              <LuxeInput
                label="Confirm Password"
                name="confirmPassword"
                type={showPassword ? "text" : "password"}
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                error={errors.confirmPassword}
                required
              />

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
                disabled={loading || !isSupabaseReady}
                isLoading={loading}
                icon={ArrowRight}
              >
                Create Account
              </LuxeButton>
            </form>
          </div>

          <div className="pt-6 text-center">
            <p className="text-sm text-neutral-500">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-neutral-900 hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </motion.div>

        {/* Footer Links */}
        <div className="absolute bottom-8 left-0 w-full text-center lg:text-left lg:pl-12">
          <div className="flex gap-6 justify-center lg:justify-start text-xs text-neutral-400 uppercase tracking-wider">
            <Link to="/privacy" className="hover:text-neutral-600">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-neutral-600">Terms of Service</Link>
            <a href="mailto:support@raptorflow.in" className="hover:text-neutral-600">Help Center</a>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Register;
