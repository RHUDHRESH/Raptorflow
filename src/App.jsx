import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Moves from './pages/Moves'
import MoveDetail from './pages/MoveDetail'
import WarRoom from './pages/WarRoom'
import MoveLibrary from './pages/MoveLibrary'
import Quests from './pages/Quests'
import TechTree from './pages/TechTree'
import Today from './pages/Today'
import DailySweep from './pages/DailySweep'
import OnboardingWizard from './pages/OnboardingWizard'
import Strategy from './pages/Strategy'
import StrategyWizard from './pages/StrategyWizard'
import Analytics from './pages/Analytics'
import WeeklyReview from './pages/WeeklyReview'
import CohortsManager from './pages/CohortsManager'
import CohortsMoves from './pages/CohortsMoves'
import Support from './pages/Support'
import History from './pages/History'
import Account from './pages/Account'
import Settings from './pages/Settings'

function App() {
  return (
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
        <Route path="/moves/war-room" element={
          <ProtectedRoute>
            <Layout>
              <WarRoom />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/moves/library" element={
          <ProtectedRoute>
            <Layout>
              <MoveLibrary />
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
        <Route path="/tech-tree" element={
          <ProtectedRoute>
            <Layout>
              <TechTree />
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
        <Route path="/daily-sweep" element={
          <ProtectedRoute>
            <Layout>
              <DailySweep />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/onboarding" element={
          <ProtectedRoute>
            <Layout>
              <OnboardingWizard />
            </Layout>
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
            <Layout>
              <StrategyWizard />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/analytics" element={
          <ProtectedRoute>
            <Layout>
              <Analytics />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/review" element={
          <ProtectedRoute>
            <Layout>
              <WeeklyReview />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/cohorts" element={
          <ProtectedRoute>
            <Layout>
              <CohortsManager />
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
      </Routes>
    </AuthProvider>
  )
}

export default App

