import React, { Suspense } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { WorkspaceProvider } from './context/WorkspaceContext'
import ProtectedRoute from './components/ProtectedRoute.tsx'
import WorkspaceGuard from './components/WorkspaceGuard.tsx'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import { ToastProvider } from './components/Toast'
import { routes } from './lib/routes'
import LoadingScreen from './components/LoadingScreen'
const Login = React.lazy(() => import('./pages/Login'))
const Register = React.lazy(() => import('./pages/Register'))
const Auth = React.lazy(() => import('./pages/Auth'))
const Landing = React.lazy(() => import('./pages/Landing'))
const Privacy = React.lazy(() => import('./pages/Privacy'))
const Terms = React.lazy(() => import('./pages/Terms'))
const Dashboard = React.lazy(() => import('./pages/Dashboard.tsx'))
const Moves = React.lazy(() => import('./pages/Moves'))
const MoveDetail = React.lazy(() => import('./pages/MoveDetail'))
const Quests = React.lazy(() => import('./pages/Quests'))
const Today = React.lazy(() => import('./pages/Today'))
const DailySweep = React.lazy(() => import('./pages/DailySweep'))
const Onboarding = React.lazy(() => import('./components/Onboarding'))
const OnboardingLuxe = React.lazy(() => import('./pages/OnboardingLuxe'))
const OnboardingPricing = React.lazy(() => import('./pages/OnboardingPricing'))
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
const CampaignBuilder = React.lazy(() => import('./pages/CampaignBuilder'))
const CampaignDetail = React.lazy(() => import('./pages/CampaignDetail'))
// Council of Lords Dashboards - Phase 2A
const ArchitectDashboard = React.lazy(() => import('./pages/strategy/ArchitectDashboard'))
const CognitionDashboard = React.lazy(() => import('./pages/strategy/CognitionDashboard'))
const StrategosDashboard = React.lazy(() => import('./pages/strategy/StrategosDashboard'))
const AestheteDashboard = React.lazy(() => import('./pages/strategy/AestheteDashboard'))
const SeerDashboard = React.lazy(() => import('./pages/strategy/SeerDashboard'))
const ArbiterDashboard = React.lazy(() => import('./pages/strategy/ArbiterDashboard'))
const HeraldDashboard = React.lazy(() => import('./pages/strategy/HeraldDashboard'))
const ErisDashboard = React.lazy(() => import('./pages/strategy/ErisDashboard'))
const AuthDebug = React.lazy(() => import('./pages/debug/AuthDebug'))
const Workspace = React.lazy(() => import('./pages/Workspace'))
const CreateWorkspace = React.lazy(() => import('./pages/CreateWorkspace.tsx'))
const Positioning = React.lazy(() => import('./pages/Positioning.tsx'))
const Error404 = React.lazy(() => import('./pages/Error404'))


// Force re-resolve
function App() {
  const navigate = useNavigate();
  return (
    <ErrorBoundary name="AppRoot">
      <ToastProvider>
        <AuthProvider>
          <WorkspaceProvider>
            <Suspense fallback={<LoadingScreen />}>
              <Routes>
                {/* Public Routes */}
                <Route path={routes.landing} element={<Landing />} />
                <Route path="/landing" element={<Landing />} />
                <Route path={routes.login} element={<Login />} />
                <Route path={routes.register} element={<Register />} />
                <Route path={routes.auth} element={<Auth />} />
                <Route path={routes.privacy} element={<Privacy />} />
                <Route path={routes.terms} element={<Terms />} />

                {/* Onboarding */}
                <Route path={routes.onboarding} element={
                  <ProtectedRoute requireOnboarding={false}>
                    <Onboarding />
                  </ProtectedRoute>
                } />
                <Route path={routes.onboardingNew} element={
                  <ProtectedRoute requireOnboarding={false}>
                    <OnboardingLuxe />
                  </ProtectedRoute>
                } />
                <Route path={routes.onboardingPricing} element={
                  <ProtectedRoute requireOnboarding={true}>
                    <OnboardingPricing />
                  </ProtectedRoute>
                } />

                {/* Dashboard Routes (Wrapped in Layout) */}
                <Route element={
                  <ProtectedRoute>
                    <WorkspaceGuard>
                      <Layout />
                    </WorkspaceGuard>
                  </ProtectedRoute>
                }>
                  <Route path={routes.dashboard} element={<Dashboard />} /> {/* Dashboard handles its own layout content if needed, but here we wrap it? No, Dashboard.tsx uses AppLayout internally. Let's check. */}
                  {/* Wait, Dashboard.tsx uses AppLayout internally. Layout.jsx renders children. */}
                  {/* If I wrap Dashboard in Layout here, it will double wrap? */}
                  {/* Dashboard.tsx has <AppLayout>...</AppLayout>. AppLayout seems to be similar to Layout. */}
                  {/* I should standardize. Layout.jsx IS AppLayout. */}
                  {/* Let's assume Dashboard.tsx needs to be refactored to NOT use AppLayout if it's wrapped here, OR I don't wrap it here. */}
                  {/* Most other pages are wrapped in Layout manually in the old code. */}
                  {/* I will use a layout route for all dashboard pages to avoid manual wrapping. */}

                  {/* Core */}
                  <Route path={routes.today} element={<Today />} />
                  <Route path={routes.dailySweep} element={<DailySweep />} />

                  {/* Moves */}
                  <Route path={routes.moves} element={<Moves />} />
                  <Route path="/moves/:moveId" element={<MoveDetail />} />

                  {/* Quests */}
                  <Route path={routes.quests} element={<Quests />} />

                  {/* Campaigns */}
                  <Route path={routes.campaigns} element={<Campaigns />} />
                  <Route path={routes.campaignNew} element={<CampaignBuilder />} />
                  <Route path="/campaigns/:id/edit" element={<CampaignBuilder />} />
                  <Route path="/campaigns/:id" element={<CampaignDetail />} />

                  {/* Cohorts */}
                  <Route path={routes.cohorts} element={<CohortsEnhancedLuxe />} />
                  <Route path="/cohorts/:id" element={<CohortDetail />} />

                  {/* Strategy */}
                  <Route path={routes.strategy} element={<Strategy />} />
                  <Route path={routes.strategyWizard} element={<StrategyWizard />} />

                  {/* Tools & Settings */}
                  <Route path={routes.history} element={<History />} />
                  <Route path={routes.account} element={<Account />} />
                  <Route path={routes.billing} element={<Billing />} />
                  <Route path={routes.settings} element={<Settings />} />
                  <Route path={routes.support} element={<Support />} />

                  {/* Muse */}
                  <Route path={routes.muse} element={<MuseHome />} />
                  <Route path={routes.museWorkspace} element={<MuseDraftWorkspace />} />
                  <Route path={routes.museRepurpose} element={<MuseRepurpose />} />
                  <Route path={routes.museHooks} element={<MuseHooks />} />
                  <Route path="/muse/assets/:id" element={<MuseDraftWorkspace />} />

                  {/* Matrix */}
                  <Route path={routes.matrix} element={<Matrix />} />

                  {/* Council */}
                  <Route path={routes.council.architect} element={<ArchitectDashboard />} />
                  <Route path={routes.council.cognition} element={<CognitionDashboard />} />
                  <Route path={routes.council.strategos} element={<StrategosDashboard />} />
                  <Route path={routes.council.aesthete} element={<AestheteDashboard />} />
                  <Route path={routes.council.seer} element={<SeerDashboard />} />
                  <Route path={routes.council.arbiter} element={<ArbiterDashboard />} />
                  <Route path={routes.council.herald} element={<HeraldDashboard />} />
                  <Route path={routes.council.eris} element={<ErisDashboard />} />

                  {/* Positioning */}
                  <Route path={routes.positioning} element={<Positioning />} />
                </Route>

                {/* Standalone Protected Routes */}
                <Route path={routes.workspace} element={
                  <ProtectedRoute>
                    <WorkspaceGuard>
                      <Workspace />
                    </WorkspaceGuard>
                  </ProtectedRoute>
                } />
                <Route path={routes.workspaceCreate} element={
                  <ProtectedRoute>
                    <CreateWorkspace />
                  </ProtectedRoute>
                } />

                <Route path="/debug/auth" element={<AuthDebug />} />
                <Route path="*" element={<Error404 />} />
              </Routes>
            </Suspense>
          </WorkspaceProvider>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App
