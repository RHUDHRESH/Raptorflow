import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
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
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/moves" element={<Moves />} />
        <Route path="/moves/war-room" element={<WarRoom />} />
        <Route path="/moves/library" element={<MoveLibrary />} />
        <Route path="/moves/:id" element={<MoveDetail />} />
        <Route path="/quests" element={<Quests />} />
        <Route path="/tech-tree" element={<TechTree />} />
        <Route path="/today" element={<Today />} />
        <Route path="/daily-sweep" element={<DailySweep />} />
        <Route path="/onboarding" element={<OnboardingWizard />} />
        <Route path="/strategy" element={<Strategy />} />
        <Route path="/strategy/wizard" element={<StrategyWizard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/review" element={<WeeklyReview />} />
        <Route path="/cohorts" element={<CohortsManager />} />
        <Route path="/cohorts/:id/moves" element={<CohortsMoves />} />
        <Route path="/support" element={<Support />} />
        <Route path="/history" element={<History />} />
        <Route path="/account" element={<Account />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App

