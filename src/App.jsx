import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Start from './pages/Start'

// Onboarding pages
import Intro from './pages/onboarding/Intro'
import Goals from './pages/onboarding/Goals'
import Audience from './pages/onboarding/Audience'
import Positioning from './pages/onboarding/Positioning'
import Execution from './pages/onboarding/Execution'
import Review from './pages/onboarding/Review'
import Generating from './pages/onboarding/Generating'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/start" element={<Start />} />

        {/* Onboarding flow */}
        <Route path="/onboarding/intro" element={<Intro />} />
        <Route path="/onboarding/goals" element={<Goals />} />
        <Route path="/onboarding/audience" element={<Audience />} />
        <Route path="/onboarding/positioning" element={<Positioning />} />
        <Route path="/onboarding/execution" element={<Execution />} />
        <Route path="/onboarding/review" element={<Review />} />
        <Route path="/onboarding/generating" element={<Generating />} />

        <Route path="*" element={<Landing />} />
      </Routes>
    </Router>
  )
}

export default App

