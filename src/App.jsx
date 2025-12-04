import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'

// Landing pages
import Landing from './pages/Landing'
import Login from './pages/Login'
import Start from './pages/Start'

// App pages
import AppLayout from './layouts/AppLayout'
import Dashboard from './pages/app/Dashboard'
import Moves from './pages/app/Moves'
import Muse from './pages/app/Muse'
import Campaigns from './pages/app/Campaigns'
import Matrix from './pages/app/Matrix'
import Position from './pages/app/Position'
import Cohorts from './pages/app/Cohorts'
import Settings from './pages/app/Settings'

// Payment pages
import PaymentProcess from './pages/payment/PaymentProcess'
import PaymentCallback from './pages/payment/PaymentCallback'

// OAuth callback
import OAuthCallback from './pages/OAuthCallback'

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, user, profile } = useAuth()
  const [profileLoading, setProfileLoading] = useState(false)

  // Wait for profile to be created (with timeout)
  useEffect(() => {
    if (user && !profile && !loading) {
      setProfileLoading(true)
      // Give profile creation up to 3 seconds
      const timer = setTimeout(() => {
        setProfileLoading(false)
      }, 3000)
      return () => clearTimeout(timer)
    } else {
      setProfileLoading(false)
    }
  }, [user, profile, loading])

  if (loading || profileLoading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-white/40 text-sm">
            {loading ? 'Loading...' : 'Setting up your account...'}
          </p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  // Allow access even if profile is still being created (it will be created in background)
  return children
}

// App routes component (needs to be inside AuthProvider)
const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/start" element={<Start />} />
      
      {/* OAuth callback */}
      <Route path="/auth/callback" element={<OAuthCallback />} />
      
      {/* Payment routes */}
      <Route path="/payment/process" element={<PaymentProcess />} />
      <Route path="/payment/callback" element={<PaymentCallback />} />

      {/* Protected app routes */}
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="moves" element={<Moves />} />
        <Route path="muse" element={<Muse />} />
        <Route path="campaigns" element={<Campaigns />} />
        <Route path="matrix" element={<Matrix />} />
        <Route path="position" element={<Position />} />
        <Route path="cohorts" element={<Cohorts />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Catch all - redirect to landing */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  )
}

export default App
