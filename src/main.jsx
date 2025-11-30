import { Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import 'leaflet/dist/leaflet.css'

// Import pages directly (no lazy loading for now to avoid suspense issues)
import Dashboard from './pages/Dashboard.tsx'
import Campaigns from './pages/Campaigns.jsx'
import Settings from './pages/Settings.jsx'
import Analytics from './pages/Analytics.jsx'
import DailySweep from './pages/DailySweep.jsx'
import Moves from './pages/Moves.jsx'
import Strategy from './pages/Strategy.jsx'

// Simple loading component
const LoadingScreen = () => (
    <div className="flex items-center justify-center min-h-screen bg-neutral-50">
        <div className="text-center">
            <div className="w-16 h-16 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mx-auto mb-4" />
            <p className="text-neutral-600">Loading...</p>
        </div>
    </div>
)

function App() {
    return (
        <BrowserRouter>
            <Suspense fallback={<LoadingScreen />}>
                <div className="min-h-screen bg-neutral-50">
                    <Routes>
                        {/* Show Dashboard by default */}
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/campaigns" element={<Campaigns />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/daily-sweep" element={<DailySweep />} />
                        <Route path="/moves" element={<Moves />} />
                        <Route path="/strategy" element={<Strategy />} />
                        <Route path="/settings" element={<Settings />} />

                        {/* Fallback route */}
                        <Route path="*" element={
                            <div className="flex items-center justify-center min-h-screen">
                                <div className="text-center max-w-2xl p-8">
                                    <h1 className="text-6xl font-display font-bold mb-6">🎨 RaptorFlow</h1>
                                    <h2 className="text-2xl font-medium mb-4">Premium UI Showcase</h2>
                                    <p className="text-neutral-600 mb-8">Navigate to see the beautiful refactored pages:</p>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <a href="/dashboard" className="p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-lg transition-all">
                                            <div className="text-2xl mb-2">📊</div>
                                            <div className="font-medium">Dashboard</div>
                                        </a>
                                        <a href="/campaigns" className="p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-lg transition-all">
                                            <div className="text-2xl mb-2">🎯</div>
                                            <div className="font-medium">Campaigns</div>
                                        </a>
                                        <a href="/analytics" className="p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-lg transition-all">
                                            <div className="text-2xl mb-2">📈</div>
                                            <div className="font-medium">Analytics</div>
                                        </a>
                                        <a href="/moves" className="p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-lg transition-all">
                                            <div className="text-2xl mb-2">⚡</div>
                                            <div className="font-medium">Moves</div>
                                        </a>
                                        <a href="/daily-sweep" className="p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-lg transition-all">
                                            <div className="text-2xl mb-2">✓</div>
                                            <div className="font-medium">Daily Sweep</div>
                                        </a>
                                        <a href="/strategy" className="p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-lg transition-all">
                                            <div className="text-2xl mb-2">🎲</div>
                                            <div className="font-medium">Strategy</div>
                                        </a>
                                        <a href="/settings" className="p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-lg transition-all">
                                            <div className="text-2xl mb-2">⚙️</div>
                                            <div className="font-medium">Settings</div>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        } />
                    </Routes>
                </div>
            </Suspense>
        </BrowserRouter>
    )
}

createRoot(document.getElementById('root')).render(<App />)
