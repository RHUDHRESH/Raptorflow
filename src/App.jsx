import { Routes, Route, useNavigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import { ToastProvider } from './components/Toast'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Moves from './pages/Moves'
import MoveDetail from './pages/MoveDetail'
import Quests from './pages/Quests'
import Today from './pages/Today'
import Onboarding from './components/Onboarding'
import Strategy from './pages/Strategy'
import StrategyWizard from './pages/StrategyWizard'
import StrategyWizardEnhanced from './pages/StrategyWizardEnhanced'
import CohortsManager from './pages/CohortsManager'
import CohortsMoves from './pages/CohortsMoves'
import Cohorts from './pages/Cohorts'
import Support from './pages/Support'
import History from './pages/History'
import Account from './pages/Account'
import Settings from './pages/Settings'
import Muse from './pages/Muse'
import Matrix from './pages/Matrix'

function App() {
  const navigate = useNavigate();
  return (
    <ErrorBoundary name="AppRoot">
      <ToastProvider>
        <AuthProvider>
          <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route path="/" element={
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
              <Cohorts />
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
        <Route path="/muse" element={
          <ProtectedRoute>
            <Layout>
              <Muse />
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
