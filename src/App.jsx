import { Routes, Route, useNavigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import { ToastProvider } from './components/Toast'
import Login from './pages/Login'
import Register from './pages/Register'
import Landing from './pages/Landing'
import Privacy from './pages/Privacy'
import Terms from './pages/Terms'
import Dashboard from './pages/Dashboard'
import Moves from './pages/Moves'
import MoveDetail from './pages/MoveDetail'
import Quests from './pages/Quests'
import Today from './pages/Today'
import Onboarding from './components/Onboarding'
import Strategy from './pages/Strategy'
import StrategyWizard from './pages/StrategyWizard'
import StrategyWizardEnhanced from './pages/StrategyWizardEnhanced'
import CohortsMoves from './pages/CohortsMoves'

import Support from './pages/Support'
import History from './pages/History'
import Account from './pages/Account'
import Settings from './pages/Settings'
import MuseHome from './pages/muse/MuseHome'
import MuseDraftWorkspace from './pages/muse/MuseDraftWorkspace'
import MuseRepurpose from './pages/muse/MuseRepurpose'
import MuseHooks from './pages/muse/MuseHooks'
import Matrix from './pages/Matrix'
import Billing from './pages/Billing'
import PositioningWorkshop from './pages/strategy/PositioningWorkshop'
import CampaignBuilderLuxe from './pages/strategy/CampaignBuilderLuxe'
import CohortsEnhancedLuxe from './pages/strategy/CohortsEnhancedLuxe'
import CohortDetail from './pages/strategy/CohortDetail'
import Campaigns from './pages/Campaigns'
// Council of Lords Dashboards - Phase 2A
import ArchitectDashboard from './pages/strategy/ArchitectDashboard'
import CognitionDashboard from './pages/strategy/CognitionDashboard'
import StrategosDashboard from './pages/strategy/StrategosDashboard'
import AestheteDashboard from './pages/strategy/AestheteDashboard'
import SeerDashboard from './pages/strategy/SeerDashboard'
import ArbiterDashboard from './pages/strategy/ArbiterDashboard'
import HeraldDashboard from './pages/strategy/HeraldDashboard'


function App() {
  const navigate = useNavigate();
  return (
    <ErrorBoundary name="AppRoot">
      <ToastProvider>
        <AuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/landing" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/terms" element={<Terms />} />

            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/moves" element={
              <ProtectedRoute>
                <Layout>
                  <Moves />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/moves/:id" element={
              <ProtectedRoute>
                <Layout>
                  <MoveDetail />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/quests" element={
              <ProtectedRoute>
                <Layout>
                  <Quests />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/today" element={
              <ProtectedRoute>
                <Layout>
                  <Today />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/onboarding" element={
              <ProtectedRoute requireOnboarding={false}>
                <Onboarding onClose={() => navigate('/')} />
              </ProtectedRoute>
            } />
            <Route path="/strategy" element={
              <ProtectedRoute>
                <Layout>
                  <Strategy />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/strategy/wizard" element={
              <ProtectedRoute>
                <StrategyWizardEnhanced />
              </ProtectedRoute>
            } />
            <Route path="/strategy/wizard-basic" element={
              <ProtectedRoute>
                <Layout>
                  <StrategyWizard />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/cohorts" element={
              <ProtectedRoute>
                <Layout>
                  <CohortsEnhancedLuxe />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/cohorts/:id" element={
              <ProtectedRoute>
                <Layout>
                  <CohortDetail />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/cohorts/:id/moves" element={
              <ProtectedRoute>
                <Layout>
                  <CohortsMoves />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/strategy/positioning" element={
              <ProtectedRoute>
                <PositioningWorkshop />
              </ProtectedRoute>
            } />
            <Route path="/campaigns" element={
              <ProtectedRoute>
                <Layout>
                  <Campaigns />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/campaigns/new" element={
              <ProtectedRoute>
                <CampaignBuilderLuxe />
              </ProtectedRoute>
            } />
            <Route path="/strategy/campaigns/:id" element={
              <ProtectedRoute>
                <CampaignBuilderLuxe />
              </ProtectedRoute>
            } />

            {/* Council of Lords Routes - Phase 2A */}
            <Route path="/strategy/architect" element={
              <ProtectedRoute>
                <ArchitectDashboard />
              </ProtectedRoute>
            } />
            <Route path="/strategy/cognition" element={
              <ProtectedRoute>
                <CognitionDashboard />
              </ProtectedRoute>
            } />
            <Route path="/strategy/strategos" element={
              <ProtectedRoute>
                <StrategosDashboard />
              </ProtectedRoute>
            } />
            <Route path="/strategy/aesthete" element={
              <ProtectedRoute>
                <AestheteDashboard />
              </ProtectedRoute>
            } />
            <Route path="/strategy/seer" element={
              <ProtectedRoute>
                <SeerDashboard />
              </ProtectedRoute>
            } />
            <Route path="/strategy/arbiter" element={
              <ProtectedRoute>
                <ArbiterDashboard />
              </ProtectedRoute>
            } />
            <Route path="/strategy/herald" element={
              <ProtectedRoute>
                <HeraldDashboard />
              </ProtectedRoute>
            } />

            <Route path="/support" element={
              <ProtectedRoute>
                <Layout>
                  <Support />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/history" element={
              <ProtectedRoute>
                <Layout>
                  <History />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/account" element={
              <ProtectedRoute>
                <Layout>
                  <Account />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute>
                <Layout>
                  <Settings />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/billing" element={
              <ProtectedRoute>
                <Layout>
                  <Billing />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/muse" element={
              <ProtectedRoute>
                <Layout>
                  <MuseHome />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/muse/workspace" element={
              <ProtectedRoute>
                <Layout>
                  <MuseDraftWorkspace />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/muse/repurpose" element={
              <ProtectedRoute>
                <Layout>
                  <MuseRepurpose />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/muse/hooks" element={
              <ProtectedRoute>
                <Layout>
                  <MuseHooks />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/muse/assets/:id" element={
              <ProtectedRoute>
                <Layout>
                  <MuseDraftWorkspace />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/matrix" element={
              <ProtectedRoute>
                <Layout>
                  <Matrix />
                </Layout>
              </ProtectedRoute>
            } />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App
