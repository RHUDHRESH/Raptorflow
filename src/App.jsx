import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'

import { Toaster } from '@/components/ui/sonner'

// Landing pages
import LandingPage from './pages/LandingPage'
import PremiumLanding from './pages/PremiumLanding.tsx'
import Login from './pages/Login'
import Start from './pages/Start'

// Public pages (footer links)
import About from './pages/About'
import Blog from './pages/Blog'
import Careers from './pages/Careers'
import Contact from './pages/Contact'
import Privacy from './pages/Privacy'
import Terms from './pages/Terms'
import Refunds from './pages/Refunds'
import Manifesto from './pages/Manifesto'

import FAQ from './pages/FAQ'
import Changelog from './pages/Changelog'
import Status from './pages/Status'
import Cookies from './pages/Cookies'
import Pricing from './pages/Pricing'

// Product feature pages
import ProductMoves from './pages/product/Moves'
import ProductBlackBox from './pages/product/BlackBox'

// Onboarding pages
import {
  OnboardingLayout,
  StepPositioning,
  StepCompany,
  StepProduct,
  StepMarket,
  StepStrategy,
  StepICPs,
  StepWarPlan,
  StepPlan,
  SharedView
} from './pages/onboarding'

// App pages
import AppLayout from './layouts/AppLayout'
import MovesPage from './pages/app/MovesPage'
import MoveBuilder from './pages/app/moves/MoveBuilder.jsx'
import CampaignsPage from './pages/app/CampaignsPage'
import RadarPage from './pages/app/RadarPage'
import BlackBoxPage from './pages/app/BlackBoxPage'
import TrailPage from './pages/app/TrailPage'
import SettingsPage from './pages/app/SettingsPage'
import SignalsPage from './pages/app/SignalsPage'

// Legacy pages (keeping for backwards compatibility)
import Dashboard from './pages/app/Dashboard'
import Moves from './pages/app/Moves'
import Campaigns from './pages/app/Campaigns'
import Matrix from './pages/app/Matrix'
import Position from './pages/app/Position'
import Cohorts from './pages/app/Cohorts'
import Settings from './pages/app/Settings'
import WarRoom from './pages/app/WarRoom'
import Spikes from './pages/app/Spikes'
import SpikeSetup from './pages/app/SpikeSetup'
import Radar from './pages/app/Radar'
import MuseChatPage from './pages/app/MuseChatPage'

// Payment pages
import PaymentProcess from './pages/payment/PaymentProcess'
import PaymentCallback from './pages/payment/PaymentCallback'

// OAuth callback
import OAuthCallback from './pages/OAuthCallback'

import { AUTH_DISABLED } from './config/auth'

// Protected route wrapper - requires authentication
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, user, profile } = useAuth()
  const [profileLoading, setProfileLoading] = useState(false)

  // Wait for profile to be created (with timeout)
  useEffect(() => {
    if (AUTH_DISABLED) return
    if (user && !profile && !loading) {
      setProfileLoading(true)
      // Give profile creation up to 3 seconds
      const timer = setTimeout(() => {
        setProfileLoading(false)
      }, 3000)
      return () => clearTimeout(timer)
    }
    setProfileLoading(false)
  }, [user, profile, loading])

  if (AUTH_DISABLED) {
    return children
  }

  if (loading || profileLoading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin" />
          <p className="text-ink-400 text-sm">
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

// Onboarding route wrapper - requires authentication but no paid plan
const OnboardingRoute = ({ children }) => {
  const { isAuthenticated, loading, user, isPaid } = useAuth()

  if (AUTH_DISABLED) {
    return children
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin" />
          <p className="text-ink-400 text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/start" replace />
  }

  // If user already has a paid plan, redirect to app
  if (isPaid) {
    return <Navigate to="/app" replace />
  }

  return children
}

// Paid route wrapper - requires paid plan
const PaidRoute = ({ children }) => {
  const { isAuthenticated, loading, user, isPaid } = useAuth()

  if (AUTH_DISABLED) {
    return children
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin" />
          <p className="text-ink-400 text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  // If user hasn't paid, redirect to onboarding
  if (!isPaid) {
    return <Navigate to="/onboarding/positioning" replace />
  }

  return children
}

const ScrollManager = () => {
  const location = useLocation()

  useEffect(() => {
    const isMarketingRoute =
      !location.pathname.startsWith('/app') && !location.pathname.startsWith('/onboarding')

    if (!isMarketingRoute) return

    const prefersReducedMotion = (() => {
      try {
        return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
      } catch {
        return false
      }
    })()

    const behavior = prefersReducedMotion ? 'auto' : 'smooth'
    const headerOffset = 88

    const tryScrollToHash = () => {
      if (!location.hash) return false

      const id = decodeURIComponent(location.hash.slice(1))
      if (!id) return false

      const element = document.getElementById(id)
      if (!element) return false

      const y = element.getBoundingClientRect().top + window.scrollY - headerOffset
      window.scrollTo({ top: y, behavior })
      return true
    }

    if (location.hash) {
      if (tryScrollToHash()) return

      let attempts = 0
      const timer = window.setInterval(() => {
        attempts += 1
        if (tryScrollToHash() || attempts > 20) {
          window.clearInterval(timer)
        }
      }, 50)

      return () => window.clearInterval(timer)
    }

    window.scrollTo({ top: 0, behavior })
  }, [location.pathname, location.hash])

  return null
}

// App routes component (needs to be inside AuthProvider)
const AppRoutes = () => {
  return (
    <>
      <ScrollManager />
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/premium" element={<PremiumLanding />} />
        <Route path="/login" element={<Navigate to="/app" replace />} />
        <Route path="/start" element={<Navigate to="/app" replace />} />
        <Route path="/signup" element={<Navigate to="/app" replace />} />

        {/* Footer link pages */}
        <Route path="/about" element={<About />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/careers" element={<Careers />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/refunds" element={<Refunds />} />
        <Route path="/manifesto" element={<Manifesto />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/changelog" element={<Changelog />} />
        <Route path="/status" element={<Status />} />
        <Route path="/cookies" element={<Cookies />} />

        {/* Product feature pages */}
        <Route path="/product/moves" element={<ProductMoves />} />
        <Route path="/product/blackbox" element={<ProductBlackBox />} />

        {/* OAuth callback */}
        <Route path="/auth/callback" element={<OAuthCallback />} />

        {/* Payment routes */}
        <Route path="/payment/process" element={<PaymentProcess />} />
        <Route path="/payment/callback" element={<PaymentCallback />} />

        {/* Shared view (public - for sales-assisted flow) */}
        <Route path="/shared/:token" element={<SharedView />} />

        {/* Onboarding routes - requires auth but not paid */}
        <Route
          path="/onboarding"
          element={
            <OnboardingRoute>
              <OnboardingLayout />
            </OnboardingRoute>
          }
        >
          <Route index element={<Navigate to="positioning" replace />} />
          <Route path="positioning" element={<StepPositioning />} />
          <Route path="company" element={<StepCompany />} />
          <Route path="product" element={<StepProduct />} />
          <Route path="market" element={<StepMarket />} />
          <Route path="strategy" element={<StepStrategy />} />
          <Route path="icps" element={<StepICPs />} />
          <Route path="warplan" element={<StepWarPlan />} />
          <Route path="plan" element={<StepPlan />} />
        </Route>

        {/* Protected app routes - requires paid plan */}
        <Route
          path="/app"
          element={
            <PaidRoute>
              <AppLayout />
            </PaidRoute>
          }
        >
          {/* New routes - Matrix as home, full RaptorFlow OS */}
          <Route index element={<Navigate to="/app/matrix" replace />} />
          <Route path="matrix" element={<Matrix />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="campaigns/new" element={<CampaignsPage />} />
          <Route path="campaigns/:id" element={<CampaignsPage />} />

          {/* Moves System */}
          <Route path="moves" element={<MovesPage />} />
          <Route path="moves/new/:step" element={<MoveBuilder />} />
          <Route path="moves/library" element={<MovesPage />} />
          <Route path="moves/:id" element={<MovesPage />} />
          <Route path="moves/:id/:tab" element={<MovesPage />} />

          <Route path="radar" element={<RadarPage />} />
          <Route path="muse" element={<MuseChatPage />} />
          <Route path="signals" element={<SignalsPage />} />
          <Route path="signals/:id" element={<SignalsPage />} />
          <Route path="black-box" element={<BlackBoxPage />} />
          <Route path="black-box/new" element={<BlackBoxPage />} />
          <Route path="black-box/:id" element={<BlackBoxPage />} />
          <Route path="trail" element={<TrailPage />} />
          <Route path="settings" element={<SettingsPage />} />

          {/* Legacy routes - kept for backwards compatibility */}
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="warroom" element={<WarRoom />} />
          <Route path="matrix-old" element={<Matrix />} />
          <Route path="spikes" element={<Spikes />} />
          <Route path="spikes/new" element={<SpikeSetup />} />
          <Route path="spikes/:id" element={<Spikes />} />
          <Route path="position" element={<Position />} />
          <Route path="cohorts" element={<Cohorts />} />
          <Route path="cohorts/:id" element={<Cohorts />} />
        </Route>

        {/* Catch all - redirect to landing */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <AppRoutes />
          <Toaster />
        </AuthProvider>
      </ThemeProvider>
    </Router>
  )
}

export default App
