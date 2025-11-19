import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Moves from './pages/Moves'
import MoveDetail from './pages/MoveDetail'
import Strategy from './pages/Strategy'
import StrategyWizard from './pages/StrategyWizard'
import Analytics from './pages/Analytics'
import WeeklyReview from './pages/WeeklyReview'
import ICPManager from './pages/ICPManager'
import Support from './pages/Support'
import History from './pages/History'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/moves" element={<Moves />} />
        <Route path="/moves/:id" element={<MoveDetail />} />
        <Route path="/strategy" element={<Strategy />} />
        <Route path="/strategy/wizard" element={<StrategyWizard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/review" element={<WeeklyReview />} />
        <Route path="/icps" element={<ICPManager />} />
        <Route path="/support" element={<Support />} />
        <Route path="/history" element={<History />} />
      </Routes>
    </Layout>
  )
}

export default App

