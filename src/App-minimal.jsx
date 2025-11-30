import React, { Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import LoadingScreen from './components/LoadingScreen'

// Lazy load only essential pages for testing
const Dashboard = React.lazy(() => import('./pages/Dashboard.tsx'))
const Campaigns = React.lazy(() => import('./pages/Campaigns.jsx'))
const Settings = React.lazy(() => import('./pages/Settings.jsx'))

function App() {
    return (
        <div className="min-h-screen bg-neutral-50">
            <Suspense fallback={<LoadingScreen />}>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/campaigns" element={<Campaigns />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="*" element={
                        <div className="flex items-center justify-center min-h-screen">
                            <div className="text-center">
                                <h1 className="text-4xl font-bold mb-4">RaptorFlow</h1>
                                <p className="text-neutral-600 mb-4">Premium UI Demo</p>
                                <div className="space-x-4">
                                    <a href="/dashboard" className="text-blue-600 hover:underline">Dashboard</a>
                                    <a href="/campaigns" className="text-blue-600 hover:underline">Campaigns</a>
                                    <a href="/settings" className="text-blue-600 hover:underline">Settings</a>
                                </div>
                            </div>
                        </div>
                    } />
                </Routes>
            </Suspense>
        </div>
    )
}

export default App
