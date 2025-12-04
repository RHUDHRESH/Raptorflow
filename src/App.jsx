import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'

// Landing pages
import Landing from './pages/Landing'
import Login from './pages/Login'

// App pages
import AppLayout from './layouts/AppLayout'
import Dashboard from './pages/app/Dashboard'
import Moves from './pages/app/Moves'
import Muse from './pages/app/Muse'
import Campaigns from './pages/app/Campaigns'
import Matrix from './pages/app/Matrix'
import Position from './pages/app/Position'
import Cohorts from './pages/app/Cohorts'

// Payment pages
import PaymentProcess from './pages/payment/PaymentProcess'
import PaymentCallback from './pages/payment/PaymentCallback'

// OAuth callback
import OAuthCallback from './pages/OAuthCallback'

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, user, profile } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-white/40 text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  // If user exists but profile doesn't, wait a bit for it to be created
  if (user && !profile && !loading) {
    // Give it a moment - profile creation might be in progress
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-white/40 text-sm">Setting up your account...</p>
        </div>
      </div>
    )
  }

  return children
}

// App routes component (needs to be inside AuthProvider)
const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      
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
