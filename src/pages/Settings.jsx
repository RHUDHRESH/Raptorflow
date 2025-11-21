import { motion, AnimatePresence } from 'framer-motion'
import { Settings as SettingsIcon, Bell, Shield, Palette, Globe, Database, Download, Upload, Trash2, Sparkles, ArrowRight, Check, X, CreditCard } from 'lucide-react'
import { useState, useEffect } from 'react'
import Onboarding from '../components/Onboarding'
import { sanitizeInput, setSecureLocalStorage, getSecureLocalStorage } from '../utils/sanitize'

const settingsTabs = [
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'preferences', label: 'Preferences', icon: Palette },
  { id: 'pricing', label: 'Pricing', icon: CreditCard },
  { id: 'onboarding', label: 'Onboarding', icon: Sparkles },
  { id: 'data', label: 'Data', icon: Database },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'about', label: 'About', icon: Globe },
]

const PLAN_LIMITS = {
  ascent: { cohorts: 3, moves: 1, price: '$29', tier: 1 },
  glide: { cohorts: 6, moves: 3, price: '$79', tier: 2 },
  soar: { cohorts: 9, moves: 10, price: '$199', tier: 3 },
}

const getUserPlan = () => {
  const plan = getSecureLocalStorage('userPlan')
  return plan || 'ascent'
}

export default function Settings() {
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [showChangelog, setShowChangelog] = useState(false)
  const [activeTab, setActiveTab] = useState('notifications')
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    weekly: true,
  })

  const [preferences, setPreferences] = useState({
    theme: 'light',
    language: 'en',
    timezone: 'UTC',
  })

  // Load preferences from secure localStorage on mount
  useEffect(() => {
    const savedNotifications = getSecureLocalStorage('userNotifications')
    if (savedNotifications) {
      setNotifications(savedNotifications)
    }

    const savedPreferences = getSecureLocalStorage('userPreferences')
    if (savedPreferences) {
      setPreferences(savedPreferences)
    }
  }, [])

  // Save notifications when they change
  useEffect(() => {
    setSecureLocalStorage('userNotifications', notifications)
  }, [notifications])

  // Save preferences when they change
  useEffect(() => {
    setSecureLocalStorage('userPreferences', preferences)
  }, [preferences])

  const currentPlan = getUserPlan().toLowerCase()
  const currentPlanData = PLAN_LIMITS[currentPlan] || PLAN_LIMITS.ascent

  const handlePreferenceChange = (field, value) => {
    // Sanitize the value before updating state
    const sanitizedValue = sanitizeInput(value)
    setPreferences(prev => ({ ...prev, [field]: sanitizedValue }))
  }

  return (
    <>
      {showOnboarding && <Onboarding onClose={() => setShowOnboarding(false)} />}
      <AnimatePresence>
        {showChangelog && (
          <motion.div
            key="changelog-modal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowChangelog(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
                <h2 className="font-serif text-2xl text-neutral-900">Changelog</h2>
                <button
                  onClick={() => setShowChangelog(false)}
                  className="text-neutral-400 hover:text-neutral-900 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-6 space-y-6">
                <div>
                  <h3 className="font-serif text-xl text-neutral-900 mb-2">Version 1.0</h3>
                  <p className="font-sans text-sm text-neutral-600 mb-4">Strategy Execution Platform</p>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-sans font-semibold text-sm text-neutral-900 mb-1">Initial Release</h4>
                      <ul className="font-sans text-sm text-neutral-600 space-y-1 list-disc list-inside">
                        <li>Move Management system</li>
                        <li>Strategy Wizard onboarding</li>
                        <li>Weekly Review ritual</li>
                        <li>Cohorts Manager with AI recommendations</li>
                        <li>Analytics Dashboard</li>
                        <li>Support & History tracking</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="pb-8"
      >
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="micro-label tracking-[0.5em]">Settings</span>
            <span className="h-px w-16 bg-neutral-200" />
          </div>
          <div className="space-y-2">
            <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased">
              Settings
            </h1>
            <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
              Configure your workspace preferences
            </p>
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="border-b-2 border-neutral-200">
        <div className="flex overflow-x-auto scrollbar-hide">
          {settingsTabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative flex items-center gap-2 px-6 py-4 font-sans text-sm font-medium transition-all ${
                  isActive
                    ? 'text-neutral-900'
                    : 'text-neutral-500 hover:text-neutral-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-neutral-900"
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'notifications' && (
            <div className="space-y-0">
              {[
                { key: 'email', label: 'Email Notifications', description: 'Receive email updates' },
                { key: 'push', label: 'Push Notifications', description: 'Real-time browser notifications' },
                { key: 'weekly', label: 'Weekly Reminder', description: 'Weekly recap reminder' },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between py-5 px-0 border-b border-neutral-200 last:border-b-0">
                  <div className="flex-1 pr-6">
                    <h3 className="font-sans font-semibold text-neutral-900 mb-1 text-base">{item.label}</h3>
                    <p className="font-sans text-xs text-neutral-600">{item.description}</p>
                  </div>
                  <label className="checkBox">
                    <input
                      type="checkbox"
                      checked={notifications[item.key]}
                      onChange={(e) => setNotifications({ ...notifications, [item.key]: e.target.checked })}
                    />
                    <div></div>
                  </label>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'preferences' && (
            <div className="space-y-6">
              <div>
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">
                  Theme
                </label>
                <select
                  value={preferences.theme}
                  onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                  className="w-full px-0 py-3 border-b border-neutral-200 bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-lg appearance-none"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="editorial">Editorial</option>
                  <option value="runway">Runway</option>
                </select>
              </div>
              <div>
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">
                  Language
                </label>
                <select
                  value={preferences.language}
                  onChange={(e) => handlePreferenceChange('language', e.target.value)}
                  className="w-full px-0 py-3 border-b border-neutral-200 bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-lg appearance-none"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
              <div>
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">
                  Timezone
                </label>
                <select
                  value={preferences.timezone}
                  onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
                  className="w-full px-0 py-3 border-b border-neutral-200 bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-lg appearance-none"
                >
                  <option value="UTC">UTC</option>
                  <option value="EST">Eastern Time</option>
                  <option value="PST">Pacific Time</option>
                  <option value="GMT">GMT</option>
                </select>
              </div>
            </div>
          )}

          {activeTab === 'pricing' && (
            <div className="space-y-8">
              {/* Current Plan */}
              <div className="border-2 border-neutral-900 bg-neutral-900 text-white p-6 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="micro-label tracking-[0.5em] text-neutral-300 mb-2">Current Plan</p>
                    <h2 className="font-serif text-3xl md:text-4xl text-white mb-1">
                      {currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)}
                    </h2>
                    <p className="font-sans text-sm text-neutral-300">
                      {currentPlanData.price}/month
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{currentPlanData.cohorts} cohorts</div>
                    <div className="text-sm text-neutral-300">Limit</div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-neutral-700">
                  <div>
                    <p className="text-xs text-neutral-400 uppercase tracking-[0.2em] mb-1">Cohort Profiles</p>
                    <p className="text-lg font-semibold">{currentPlanData.cohorts}</p>
                  </div>
                  <div>
                    <p className="text-xs text-neutral-400 uppercase tracking-[0.2em] mb-1">Moves</p>
                    <p className="text-lg font-semibold">{currentPlanData.moves}</p>
                  </div>
                </div>
              </div>

              {/* Available Plans */}
              <div>
                <h3 className="font-serif text-2xl text-neutral-900 mb-6">Available Plans</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[
                    { name: 'Ascent', key: 'ascent' },
                    { name: 'Glide', key: 'glide' },
                    { name: 'Soar', key: 'soar' },
                  ].map((plan) => {
                    const planData = PLAN_LIMITS[plan.key]
                    const isCurrent = currentPlan === plan.key
                    const currentPlanTier = currentPlanData?.tier || 1
                    const planTier = planData.tier
                    const isUpgrade = planTier > currentPlanTier
                    const isDowngrade = planTier < currentPlanTier
                    
                    let buttonText = 'Select Plan'
                    if (isCurrent) {
                      buttonText = 'Current Plan'
                    } else if (isUpgrade) {
                      buttonText = 'Upgrade'
                    } else if (isDowngrade) {
                      buttonText = 'Downgrade'
                    }
                    
                    return (
                      <div
                        key={plan.name}
                        className={`border-2 rounded-lg p-6 transition-all ${
                          isCurrent
                            ? 'border-neutral-900 bg-neutral-50'
                            : 'border-neutral-200 hover:border-neutral-900'
                        }`}
                      >
                        <div className="space-y-4">
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="font-serif text-2xl text-neutral-900">{plan.name}</h3>
                              {isCurrent && (
                                <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-[0.2em] bg-neutral-900 text-white">
                                  Current
                                </span>
                              )}
                            </div>
                            <p className="font-sans text-2xl font-bold text-neutral-900 mb-1">
                              {planData.price}
                              <span className="text-sm font-normal text-neutral-500">/mo</span>
                            </p>
                            <p className="font-sans text-xs text-neutral-500 uppercase tracking-[0.2em]">
                              Tier {planData.tier}
                            </p>
                          </div>
                          <div className="space-y-2 py-4 border-t border-neutral-200">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-neutral-600">Cohort Profiles</span>
                              <span className="font-semibold text-neutral-900">{planData.cohorts}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-neutral-600">Moves</span>
                              <span className="font-semibold text-neutral-900">{planData.moves}</span>
                            </div>
                          </div>
                          <button
                            disabled={isCurrent}
                            onClick={() => {
                              if (!isCurrent) {
                                setSecureLocalStorage('userPlan', plan.key)
                                alert(`Plan changed to ${plan.name}. Please refresh the page.`)
                              }
                            }}
                            className={`w-full border px-4 py-2 text-[10px] font-mono uppercase tracking-[0.3em] transition-colors ${
                              isCurrent
                                ? 'border-neutral-300 bg-neutral-100 text-neutral-400 cursor-not-allowed'
                                : 'border-neutral-900 text-neutral-900 hover:bg-neutral-900 hover:text-white'
                            }`}
                          >
                            {buttonText}
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'onboarding' && (
            <div className="border-2 border-neutral-200 bg-white px-8 py-8">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
                <div className="flex-1">
                  <div className="flex items-center gap-3 text-[10px] font-mono uppercase tracking-[0.5em] text-neutral-500 mb-3">
                    <span>Onboarding</span>
                    <span className="h-px w-8 bg-neutral-300" />
                    <span>Setup</span>
                  </div>
                  <h3 className="font-serif text-2xl md:text-3xl text-neutral-900 leading-tight mb-2">
                    Get Started
                  </h3>
                  <p className="font-sans text-sm text-neutral-600 max-w-xl leading-relaxed">
                    Complete the onboarding process to set up your workspace and configure your preferences.
                  </p>
                </div>
                <div className="flex items-center">
                  <button
                    onClick={() => setShowOnboarding(true)}
                    className="group relative inline-flex items-center gap-3 border-2 border-neutral-900 bg-black text-white px-8 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-all"
                  >
                    Start Setup
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'data' && (
            <div className="space-y-0">
              <button className="w-full flex items-center justify-between py-5 px-0 border-b border-neutral-200 hover:bg-neutral-50 transition-colors">
                <div className="flex items-center gap-4">
                  <Download className="w-5 h-5 text-neutral-900" />
                  <div className="text-left">
                    <h3 className="font-sans font-semibold text-neutral-900 mb-1 text-base">Export Data</h3>
                    <p className="font-sans text-xs text-neutral-600">Download your data as JSON</p>
                  </div>
                </div>
              </button>
              <button className="w-full flex items-center justify-between py-5 px-0 border-b border-neutral-200 hover:bg-neutral-50 transition-colors">
                <div className="flex items-center gap-4">
                  <Upload className="w-5 h-5 text-neutral-900" />
                  <div className="text-left">
                    <h3 className="font-sans font-semibold text-neutral-900 mb-1 text-base">Import Data</h3>
                    <p className="font-sans text-xs text-neutral-600">Restore from a saved backup</p>
                  </div>
                </div>
              </button>
              <button className="w-full flex items-center justify-between py-5 px-0 border-b border-red-200 hover:border-red-400 transition-colors last:border-b-0 group">
                <div className="flex items-center gap-4">
                  <Trash2 className="w-5 h-5 text-red-900 group-hover:text-red-700 transition-colors" />
                  <div className="text-left">
                    <h3 className="font-sans font-semibold text-red-900 group-hover:text-red-700 mb-1 text-base transition-colors">Delete All Data</h3>
                    <p className="font-sans text-xs text-red-600 group-hover:text-red-500 transition-colors">Permanently delete all data</p>
                  </div>
                </div>
              </button>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-0">
              <button className="w-full px-0 py-4 text-left border-b border-neutral-200 hover:bg-neutral-50 transition-colors font-sans text-base font-medium text-neutral-900">
                Change Password
              </button>
              <button className="w-full px-0 py-4 text-left border-b border-neutral-200 hover:bg-neutral-50 transition-colors font-sans text-base font-medium text-neutral-900">
                Two-Factor Authentication
              </button>
              <button className="w-full px-0 py-4 text-left border-b border-neutral-200 hover:bg-neutral-50 transition-colors font-sans text-base font-medium text-neutral-900 last:border-b-0">
                Active Sessions
              </button>
            </div>
          )}

          {activeTab === 'about' && (
            <div className="space-y-2 font-sans text-sm text-neutral-600">
              <p>Raptorflow v1.0</p>
              <p>Strategy Execution Platform</p>
              <button 
                onClick={() => setShowChangelog(true)}
                className="text-neutral-900 font-medium hover:underline mt-4 block"
              >
                View Changelog
              </button>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
    </>
  )
}
