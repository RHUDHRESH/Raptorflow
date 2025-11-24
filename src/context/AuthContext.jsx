import React, { createContext, useContext, useState, useEffect } from 'react';
import { sanitizeInput, sanitizeEmail } from '../utils/sanitize';
import { validateEmail, validatePassword } from '../utils/validation';
import { supabase, isSupabaseConfigured } from '../lib/supabase';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);

  // Check for existing session on mount
  useEffect(() => {
    if (!isSupabaseConfigured() || !supabase) {
      console.warn('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
      setLoading(false);
      return;
    }

    // Check for OAuth callback in URL hash
    const handleOAuthCallback = async () => {
      if (!supabase) return;
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        if (error) throw error;

        if (session?.user) {
          const userData = {
            id: session.user.id,
            email: session.user.email,
            name: session.user.user_metadata?.full_name || session.user.user_metadata?.name || session.user.email?.split('@')[0] || 'User',
            avatar_url: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture,
          };
          setUser(userData);
          setLoading(false);

          // Clear OAuth callback from URL
          if (window.location.hash) {
            window.history.replaceState(null, '', window.location.pathname);
          }
        }
      } catch (err) {
        console.error('Error handling OAuth callback:', err);
        setLoading(false);
      }
    };

    // Check for OAuth callback first
    if (window.location.hash.includes('access_token') || window.location.hash.includes('error')) {
      handleOAuthCallback();
    } else {
      checkAuth();
    }

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
          if (session?.user) {
            const userData = {
              id: session.user.id,
              email: session.user.email,
              name: session.user.user_metadata?.full_name || session.user.user_metadata?.name || session.user.email?.split('@')[0] || 'User',
              avatar_url: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture,
            };
            setUser(userData);

            // Fetch subscription and onboarding status
            await fetchUserStatus(session.user.id);

            // Clear OAuth callback from URL if present
            if (window.location.hash) {
              window.history.replaceState(null, '', window.location.pathname);
            }
          }
        } else if (event === 'SIGNED_OUT') {
          setUser(null);
          setSubscription(null);
          setOnboardingCompleted(false);
        }
        setLoading(false);
      }
    );

    return () => {
      if (subscription) {
        subscription.unsubscribe();
      }
    };
  }, []);

  const checkAuth = async () => {
    if (!isSupabaseConfigured() || !supabase) {
      setLoading(false);
      return;
    }

    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();

      if (sessionError) {
        console.error('Error checking auth:', sessionError);
        setUser(null);
        return;
      }

      if (session?.user) {
        const userData = {
          id: session.user.id,
          email: session.user.email,
          name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'User',
          avatar_url: session.user.user_metadata?.avatar_url,
        };
        setUser(userData);

        // Fetch subscription and onboarding status
        await fetchUserStatus(session.user.id);
      } else {
        setUser(null);
      }
    } catch (err) {
      console.error('Error checking auth:', err);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserStatus = async (userId) => {
    if (!supabase) return;

    try {
      // Fetch user profile for onboarding status
      const { data: profile, error: profileError } = await supabase
        .from('user_profiles')
        .select('onboarding_completed, onboarding_skipped')
        .eq('id', userId)
        .single();

      if (!profileError && profile) {
        setOnboardingCompleted(profile.onboarding_completed || profile.onboarding_skipped);
      }

      // Fetch subscription
      const { data: subscriptionData, error: subError } = await supabase
        .from('subscriptions')
        .select('*')
        .eq('user_id', userId)
        .in('status', ['active', 'trialing'])
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (!subError && subscriptionData) {
        setSubscription(subscriptionData);
      } else {
        // If no subscription found, user might be on free plan
        setSubscription({ plan: 'free', status: 'active' });
      }
    } catch (err) {
      console.error('Error fetching user status:', err);
    }
  };

  const clearAuth = async () => {
    if (isSupabaseConfigured() && supabase) {
      await supabase.auth.signOut();
    }
    setUser(null);
    setSubscription(null);
    setOnboardingCompleted(false);
  };

  const login = async (email, password) => {
    try {
      setError(null);
      setLoading(true);

      if (!isSupabaseConfigured() || !supabase) {
        throw new Error('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
      }

      // Validate inputs
      const emailValidation = validateEmail(email);
      if (!emailValidation.isValid) {
        throw new Error(emailValidation.error);
      }

      const passwordValidation = validatePassword(password);
      if (!passwordValidation.isValid) {
        throw new Error(passwordValidation.error);
      }

      // Sanitize inputs
      const sanitizedEmail = sanitizeEmail(email);

      // Sign in with Supabase
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email: sanitizedEmail,
        password: password,
      });

      if (signInError) {
        throw new Error(signInError.message || 'Invalid email or password');
      }

      if (data?.user) {
        const userData = {
          id: data.user.id,
          email: data.user.email,
          name: data.user.user_metadata?.full_name || data.user.email?.split('@')[0] || 'User',
          avatar_url: data.user.user_metadata?.avatar_url,
        };
        setUser(userData);

        // Fetch subscription and onboarding status
        await fetchUserStatus(data.user.id);

        setLoading(false);
        return { success: true, user: userData };
      }

      throw new Error('Login failed');
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  };

  const loginWithGoogle = async () => {
    try {
      setError(null);
      setLoading(true);

      if (!isSupabaseConfigured() || !supabase) {
        throw new Error('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
      }

      // Redirect to Google OAuth
      const { error: oauthError } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/`,
        },
      });

      if (oauthError) {
        // Provide more helpful error messages
        if (oauthError.message?.includes('provider is not enabled') || oauthError.message?.includes('Unsupported provider')) {
          throw new Error('Google OAuth is not enabled in your Supabase project. Please enable it in the Supabase Dashboard under Authentication > Providers > Google.');
        }
        throw new Error(oauthError.message || 'Failed to sign in with Google');
      }

      // The redirect will happen automatically
      // The auth state change listener will handle setting the user
      return { success: true };
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  };

  const register = async (name, email, password, confirmPassword) => {
    try {
      setError(null);
      setLoading(true);

      if (!isSupabaseConfigured() || !supabase) {
        throw new Error('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
      }

      // Validate inputs
      const emailValidation = validateEmail(email);
      if (!emailValidation.isValid) {
        throw new Error(emailValidation.error);
      }

      const passwordValidation = validatePassword(password);
      if (!passwordValidation.isValid) {
        throw new Error(passwordValidation.error);
      }

      if (password !== confirmPassword) {
        throw new Error('Passwords do not match');
      }

      // Sanitize inputs
      const sanitizedName = sanitizeInput(name.trim());
      const sanitizedEmail = sanitizeEmail(email);

      if (!sanitizedName || sanitizedName.length < 2) {
        throw new Error('Name must be at least 2 characters');
      }

      // Sign up with Supabase
      const { data, error: signUpError } = await supabase.auth.signUp({
        email: sanitizedEmail,
        password: password,
        options: {
          data: {
            full_name: sanitizedName,
          },
        },
      });

      if (signUpError) {
        throw new Error(signUpError.message || 'Registration failed');
      }

      if (data?.user) {
        // Auto-login after registration if email confirmation is not required
        const userData = {
          id: data.user.id,
          email: data.user.email,
          name: sanitizedName,
        };
        setUser(userData);

        // Fetch subscription and onboarding status
        await fetchUserStatus(data.user.id);

        setLoading(false);
        return { success: true, user: userData };
      }

      throw new Error('Registration failed');
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  };

  const logout = async () => {
    await clearAuth();
    setError(null);
  };

  const updateProfile = async (updates) => {
    try {
      setError(null);

      if (!isSupabaseConfigured() || !supabase) {
        throw new Error('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
      }

      const sanitizedUpdates = {};

      if (updates.name) {
        sanitizedUpdates.full_name = sanitizeInput(updates.name.trim());
      }

      if (updates.email) {
        const emailValidation = validateEmail(updates.email);
        if (!emailValidation.isValid) {
          throw new Error(emailValidation.error);
        }
        sanitizedUpdates.email = sanitizeEmail(updates.email);
      }

      // Update user metadata in Supabase
      const { data, error: updateError } = await supabase.auth.updateUser({
        data: sanitizedUpdates,
      });

      if (updateError) {
        throw new Error(updateError.message || 'Failed to update profile');
      }

      if (data?.user) {
        const updatedUser = {
          id: data.user.id,
          email: data.user.email,
          name: data.user.user_metadata?.full_name || user?.name || 'User',
          avatar_url: data.user.user_metadata?.avatar_url,
        };
        setUser(updatedUser);
        return { success: true, user: updatedUser };
      }

      throw new Error('Profile update failed');
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const markOnboardingComplete = async () => {
    setOnboardingCompleted(true);
    if (!user || !supabase) return { success: false, error: 'No user authenticated' };

    try {
      const { error } = await supabase
        .from('user_profiles')
        .update({ onboarding_completed: true })
        .eq('id', user.id);

      if (error) {
        console.error('Error marking onboarding complete:', error);
        return { success: false, error: error.message };
      }

      setOnboardingCompleted(true);
      return { success: true };
    } catch (err) {
      console.error('Error marking onboarding complete:', err);
      return { success: false, error: err.message };
    }
  };

  // DEV ONLY: Skip login for development
  const skipLoginDev = () => {
    if (import.meta.env.DEV) {
      const devUser = {
        id: 'dev-user-123',
        email: 'dev@raptorflow.local',
        name: 'Dev User',
        avatar_url: null,
      };
      setUser(devUser);
      setLoading(false);
      return { success: true, user: devUser };
    }
    return { success: false, error: 'Skip login is only available in development mode' };
  };

  const value = {
    user,
    loading,
    error,
    subscription,
    onboardingCompleted,
    login,
    loginWithGoogle,
    register,
    logout,
    updateProfile,
    markOnboardingComplete,
    skipLoginDev,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
