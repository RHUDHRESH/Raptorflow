import React, { Suspense } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import { ToastProvider } from './components/Toast'
const Login = React.lazy(() => import('./pages/Login'))
const Register = React.lazy(() => import('./pages/Register'))
const Landing = React.lazy(() => import('./pages/Landing'))
const Privacy = React.lazy(() => import('./pages/Privacy'))
const Terms = React.lazy(() => import('./pages/Terms'))
const Dashboard = React.lazy(() => import('./pages/Dashboard'))
const Moves = React.lazy(() => import('./pages/Moves'))
const MoveDetail = React.lazy(() => import('./pages/MoveDetail'))
const Quests = React.lazy(() => import('./pages/Quests'))
const Today = React.lazy(() => import('./pages/Today'))
const Onboarding = React.lazy(() => import('./components/Onboarding'))
const Strategy = React.lazy(() => import('./pages/Strategy'))
const StrategyWizard = React.lazy(() => import('./pages/StrategyWizard'))
const StrategyWizardEnhanced = React.lazy(() => import('./pages/StrategyWizardEnhanced'))
const CohortsMoves = React.lazy(() => import('./pages/CohortsMoves'))
const Support = React.lazy(() => import('./pages/Support'))
const History = React.lazy(() => import('./pages/History'))
const Account = React.lazy(() => import('./pages/Account'))
const Settings = React.lazy(() => import('./pages/Settings'))
const MuseHome = React.lazy(() => import('./pages/muse/MuseHome'))
const MuseDraftWorkspace = React.lazy(() => import('./pages/muse/MuseDraftWorkspace'))
const MuseRepurpose = React.lazy(() => import('./pages/muse/MuseRepurpose'))
const MuseHooks = React.lazy(() => import('./pages/muse/MuseHooks'))
const Matrix = React.lazy(() => import('./pages/Matrix'))
const Billing = React.lazy(() => import('./pages/Billing'))
const PositioningWorkshop = React.lazy(() => import('./pages/strategy/PositioningWorkshop'))
const CampaignBuilderLuxe = React.lazy(() => import('./pages/strategy/CampaignBuilderLuxe'))
const CohortsEnhancedLuxe = React.lazy(() => import('./pages/strategy/CohortsEnhancedLuxe'))
const CohortDetail = React.lazy(() => import('./pages/strategy/CohortDetail'))
const Campaigns = React.lazy(() => import('./pages/Campaigns'))
// Council of Lords Dashboards - Phase 2A
const ArchitectDashboard = React.lazy(() => import('./pages/strategy/ArchitectDashboard'))
const CognitionDashboard = React.lazy(() => import('./pages/strategy/CognitionDashboard'))
const StrategosDashboard = React.lazy(() => import('./pages/strategy/StrategosDashboard'))
const AestheteDashboard = React.lazy(() => import('./pages/strategy/AestheteDashboard'))
const SeerDashboard = React.lazy(() => import('./pages/strategy/SeerDashboard'))
const ArbiterDashboard = React.lazy(() => import('./pages/strategy/ArbiterDashboard'))
const HeraldDashboard = React.lazy(() => import('./pages/strategy/HeraldDashboard'))


function App() {
  const navigate = useNavigate();
  return (
    <ErrorBoundary name="AppRoot">
      <ToastProvider>
        <AuthProvider>
          <Suspense fallback={<div>Loading...</div>}>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/landing" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/privacy" element={<Privacy />} />
              <Route path="/terms" element={<Terms />} />
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
              {/* Council of Lords Dashboards - Phase 2A */}
              <Route path="/strategy/architect" element={
                <ProtectedRoute>
                  <Layout>
                    <ArchitectDashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/strategy/cognition" element={
                <ProtectedRoute>
                  <Layout>
                    <CognitionDashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/strategy/strategos" element={
                <ProtectedRoute>
                  <Layout>
                    <StrategosDashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/strategy/aesthete" element={
                <ProtectedRoute>
                  <Layout>
                    <AestheteDashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/strategy/seer" element={
                <ProtectedRoute>
                  <Layout>
                    <SeerDashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/strategy/arbiter" element={
                <ProtectedRoute>
                  <Layout>
                    <ArbiterDashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/strategy/herald" element={
                <ProtectedRoute>
                  <Layout>
                    <HeraldDashboard />
                  </Layout>
                </ProtectedRoute>
              } />
            </Routes>
          </Suspense>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App
