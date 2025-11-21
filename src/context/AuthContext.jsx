import React, { createContext, useContext, useState, useEffect } from 'react';
import { sanitizeInput, sanitizeEmail, getSecureLocalStorage, setSecureLocalStorage } from '../utils/sanitize';
import { validateEmail, validatePassword } from '../utils/validation';

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

  // Check for existing session on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    try {
      const storedUser = getSecureLocalStorage('auth_user');
      const storedToken = getSecureLocalStorage('auth_token');
      const sessionExpiry = getSecureLocalStorage('auth_expiry');

      if (storedUser && storedToken && sessionExpiry) {
        const now = new Date().getTime();
        if (now < sessionExpiry) {
          setUser(storedUser);
        } else {
          // Session expired
          clearAuth();
        }
      }
    } catch (err) {
      console.error('Error checking auth:', err);
      clearAuth();
    } finally {
      setLoading(false);
    }
  };

  const clearAuth = () => {
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_expiry');
    setUser(null);
  };

  const login = async (email, password) => {
    try {
      setError(null);
      setLoading(true);

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

      // In a real application, this would make an API call
      // For now, we'll implement a simple localStorage-based auth
      const storedUsers = getSecureLocalStorage('users') || [];
      const userAccount = storedUsers.find(u => u.email === sanitizedEmail);

      if (!userAccount) {
        throw new Error('Invalid email or password');
      }

      // In production, you would verify the hashed password
      // This is a simplified version for demonstration
      if (userAccount.password !== password) {
        throw new Error('Invalid email or password');
      }

      // Create session
      const userData = {
        id: userAccount.id,
        email: sanitizedEmail,
        name: sanitizeInput(userAccount.name),
      };

      // Generate a simple token (in production, use JWT from backend)
      const token = btoa(JSON.stringify({ userId: userData.id, timestamp: Date.now() }));

      // Set session expiry (24 hours)
      const expiryTime = new Date().getTime() + (24 * 60 * 60 * 1000);

      // Store auth data
      setSecureLocalStorage('auth_user', userData);
      setSecureLocalStorage('auth_token', token);
      setSecureLocalStorage('auth_expiry', expiryTime);

      setUser(userData);
      setLoading(false);

      return { success: true, user: userData };
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

      // Check if user already exists
      const storedUsers = getSecureLocalStorage('users') || [];
      const existingUser = storedUsers.find(u => u.email === sanitizedEmail);

      if (existingUser) {
        throw new Error('An account with this email already exists');
      }

      // Create new user
      const newUser = {
        id: Date.now().toString(),
        name: sanitizedName,
        email: sanitizedEmail,
        password: password, // In production, hash the password before storing
        createdAt: new Date().toISOString(),
      };

      // Store user
      storedUsers.push(newUser);
      setSecureLocalStorage('users', storedUsers);

      // Auto-login after registration
      const loginResult = await login(sanitizedEmail, password);

      setLoading(false);
      return loginResult;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return { success: false, error: err.message };
    }
  };

  const logout = () => {
    clearAuth();
    setError(null);
  };

  const updateProfile = (updates) => {
    try {
      const sanitizedUpdates = {};

      if (updates.name) {
        sanitizedUpdates.name = sanitizeInput(updates.name.trim());
      }

      if (updates.email) {
        const emailValidation = validateEmail(updates.email);
        if (!emailValidation.isValid) {
          throw new Error(emailValidation.error);
        }
        sanitizedUpdates.email = sanitizeEmail(updates.email);
      }

      const updatedUser = { ...user, ...sanitizedUpdates };
      setUser(updatedUser);
      setSecureLocalStorage('auth_user', updatedUser);

      return { success: true, user: updatedUser };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
