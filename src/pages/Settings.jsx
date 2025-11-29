import { motion, AnimatePresence } from 'framer-motion'
import { Settings as SettingsIcon, Bell, Shield, Palette, Globe, Database, Download, Upload, Trash2, Sparkles, ArrowRight, Check, X, CreditCard, ChevronDown, AlertTriangle } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Onboarding from '../components/Onboarding'
import { sanitizeInput, setSecureLocalStorage, getSecureLocalStorage } from '../utils/sanitize'
import { backendAPI } from '../lib/services/backend-api'

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
  const navigate = useNavigate()
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [showChangelog, setShowChangelog] = useState(false)
  const [showComingSoon, setShowComingSoon] = useState(false)
  const [comingSoonFeature, setComingSoonFeature] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [dataMessage, setDataMessage] = useState({ type: '', text: '' })
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

  const fileInputRef = useRef(null)

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
    // Update preferences directly - dropdown values are safe as they come from predefined options
    setPreferences(prev => ({ ...prev, [field]: value }))
  }

  const showComingSoonModal = (feature) => {
    setComingSoonFeature(feature)
    setShowComingSoon(true)
  }

  const handleExportData = () => {
    try {
      // Get all localStorage data
      const allData = {}
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key) {
          const value = localStorage.getItem(key)
          try {
            allData[key] = JSON.parse(value)
          } catch {
            allData[key] = value
          }
        }
      }

      // Create blob and download
      const dataStr = JSON.stringify(allData, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `raptorflow-backup-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      setDataMessage({ type: 'success', text: 'Data exported successfully!' })
      setTimeout(() => setDataMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      setDataMessage({ type: 'error', text: 'Failed to export data' })
      setTimeout(() => setDataMessage({ type: '', text: '' }), 3000)
      console.error('Export error:', error)
    }
  }

  const handleImportData = (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const importedData = JSON.parse(e.target.result)

        // Validate it's an object
        if (typeof importedData !== 'object' || importedData === null) {
          throw new Error('Invalid data format')
        }

        // Import the data
        Object.entries(importedData).forEach(([key, value]) => {
          const sanitizedKey = sanitizeInput(key)
          if (sanitizedKey) {
            localStorage.setItem(sanitizedKey, typeof value === 'string' ? value : JSON.stringify(value))
          }
        })

        setDataMessage({ type: 'success', text: 'Data imported successfully! Refresh the page to see changes.' })
        setTimeout(() => setDataMessage({ type: '', text: '' }), 5000)
      } catch (error) {
        setDataMessage({ type: 'error', text: 'Failed to import data. Invalid file format.' })
        setTimeout(() => setDataMessage({ type: '', text: '' }), 3000)
        console.error('Import error:', error)
      }
    }
    reader.readAsText(file)

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDeleteAllData = () => {
    try {
      localStorage.clear()
      setShowDeleteConfirm(false)
      setDataMessage({ type: 'success', text: 'All data deleted successfully! Refresh the page.' })
      setTimeout(() => {
        window.location.reload()
      }, 2000)
    } catch (error) {
      setDataMessage({ type: 'error', text: 'Failed to delete data' })
      setTimeout(() => setDataMessage({ type: '', text: '' }), 3000)
      console.error('Delete error:', error)
    }
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
        {/* Coming Soon Modal */}
        {showComingSoon && (
          <motion.div
            key="coming-soon-modal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowComingSoon(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-2 border-black rounded-lg shadow-xl max-w-md w-full"
            >
              <div className="border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
                <h2 className="font-serif text-2xl text-neutral-900">Coming Soon</h2>
                <button
                  onClick={() => setShowComingSoon(false)}
                  className="text-neutral-400 hover:text-neutral-900 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-8 text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-neutral-100 border-2 border-neutral-200 flex items-center justify-center mx-auto">
                  <Shield className="w-8 h-8 text-neutral-400" />
                </div>
                <h3 className="font-serif text-xl text-neutral-900">{comingSoonFeature}</h3>
                <p className="font-sans text-sm text-neutral-600">
                  This security feature is currently under development and will be available soon.
                </p>
                <button
                  onClick={() => setShowComingSoon(false)}
                  className="border-2 border-black text-black px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-black hover:text-white transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <motion.div
            key="delete-confirm-modal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowDeleteConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-2 border-red-500 rounded-lg shadow-xl max-w-md w-full"
            >
              <div className="border-b border-red-200 px-6 py-4 flex items-center justify-between bg-red-50">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  <h2 className="font-serif text-2xl text-red-900">Delete All Data</h2>
                </div>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="text-red-400 hover:text-red-900 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-8 space-y-6">
                <div className="space-y-3">
                  <p className="font-sans text-base text-neutral-900 font-semibold">
                    Are you absolutely sure?
                  </p>
                  <p className="font-sans text-sm text-neutral-600 leading-relaxed">
                    This action cannot be undone. This will permanently delete all your data including:
                  </p>
                  <ul className="font-sans text-sm text-neutral-600 space-y-1 list-disc list-inside ml-2">
                    <li>User preferences and settings</li>
                    <li>Cohort profiles</li>
                    <li>Moves and strategies</li>
                    <li>All saved progress</li>
                  </ul>
                  <p className="font-sans text-sm text-red-600 font-medium mt-4">
                    Please export your data before proceeding if you want to keep a backup.
                  </p>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1 border-2 border-neutral-200 text-neutral-600 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDeleteAllData}
                    className="flex-1 bg-red-600 text-white px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-red-700 transition-colors"
                  >
                    Delete Everything
                  </button>
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
                  className={`relative flex items-center gap-2 px-6 py-4 font-sans text-sm font-medium transition-all ${isActive
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
              <div className="bg-white border-2 border-black p-12 space-y-8">
                <h2 className="font-serif text-3xl text-black mb-8">Notification Settings</h2>
                {[
                  { key: 'email', label: 'Email Notifications', description: 'Receive email updates about your campaigns and moves' },
                  { key: 'push', label: 'Push Notifications', description: 'Real-time browser notifications for important events' },
                  { key: 'weekly', label: 'Weekly Reminder', description: 'Weekly recap reminder for your strategy review' },
                ].map((item, index) => (
                  <div key={item.key} className={`flex items-center justify-between py-6 ${index < 2 ? 'border-b border-neutral-200' : ''}`}>
                    <div className="flex-1 pr-8">
                      <h3 className="font-sans font-semibold text-black mb-2 text-base">{item.label}</h3>
                      <p className="font-sans text-sm text-neutral-600">{item.description}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notifications[item.key]}
                        onChange={(e) => setNotifications({ ...notifications, [item.key]: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-neutral-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-black rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-black after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
                    </label>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'preferences' && (
              <div className="bg-white border-2 border-black p-12 space-y-8">
                <h2 className="font-serif text-3xl text-black mb-8">Preferences</h2>
                <div className="space-y-8">
                  <div>
                    <label className="block font-sans text-[11px] font-semibold uppercase tracking-[0.2em] text-[#D4AF37] mb-3">
                      Theme
                    </label>
                    <div className="relative">
                      <select
                        value={preferences.theme}
                        onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                        className="w-full bg-white border-2 border-black rounded-lg px-4 py-3 pr-10 font-serif text-lg text-black appearance-none cursor-pointer hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 transition-colors"
                      >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="editorial">Editorial</option>
                        <option value="runway">Runway</option>
                      </select>
                      <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-black pointer-events-none" />
                    </div>
                  </div>
                  <div className="border-t border-neutral-200 pt-8">
                    <label className="block font-sans text-[11px] font-semibold uppercase tracking-[0.2em] text-[#D4AF37] mb-3">
                      Language
                    </label>
                    <div className="relative">
                      <select
                        value={preferences.language}
                        onChange={(e) => handlePreferenceChange('language', e.target.value)}
                        className="w-full bg-white border-2 border-black rounded-lg px-4 py-3 pr-10 font-serif text-lg text-black appearance-none cursor-pointer hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 transition-colors"
                      >
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                      </select>
                      <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-black pointer-events-none" />
                    </div>
                  </div>
                  <div className="border-t border-neutral-200 pt-8">
                    <label className="block font-sans text-[11px] font-semibold uppercase tracking-[0.2em] text-[#D4AF37] mb-3">
                      Timezone
                    </label>
                    <div className="relative">
                      <select
                        value={preferences.timezone}
                        onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
                        className="w-full bg-white border-2 border-black rounded-lg px-4 py-3 pr-10 font-serif text-lg text-black appearance-none cursor-pointer hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 transition-colors"
                      >
                        <option value="UTC">UTC</option>
                        <option value="EST">Eastern Time</option>
                        <option value="PST">Pacific Time</option>
                        <option value="GMT">GMT</option>
                      </select>
                      <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-black pointer-events-none" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'pricing' && (
              <div className="space-y-8">
                {/* Current Plan */}
                <div className="border-2 border-black bg-black text-white p-8 rounded-lg">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <p className="font-sans text-[11px] font-semibold uppercase tracking-[0.2em] text-[#D4AF37] mb-3">Current Plan</p>
                      <h2 className="font-serif text-3xl md:text-4xl text-white mb-2">
                        {currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)}
                      </h2>
                      <p className="font-sans text-base text-neutral-300">
                        {currentPlanData.price}/month
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-white">{currentPlanData.cohorts} cohorts</div>
                      <div className="text-sm text-neutral-300">Limit</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-6 pt-6 border-t border-neutral-700">
                    <div>
                      <p className="text-xs text-neutral-400 uppercase tracking-[0.2em] mb-2">Cohort Profiles</p>
                      <p className="text-xl font-semibold text-white">{currentPlanData.cohorts}</p>
                    </div>
                    <div>
                      <p className="text-xs text-neutral-400 uppercase tracking-[0.2em] mb-2">Moves</p>
                      <p className="text-xl font-semibold text-white">{currentPlanData.moves}</p>
                    </div>
                  </div>
                </div>

                {/* Available Plans */}
                <div>
                  <h3 className="font-serif text-2xl text-neutral-900 mb-6">Available Plans</h3>
                  <div className="flex gap-6 overflow-x-auto pb-4 custom-scrollbar">
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
                          className={`bg-white border-2 rounded-lg p-8 transition-all flex-shrink-0 w-full min-w-[320px] max-w-[380px] ${isCurrent
                            ? 'border-black'
                            : 'border-neutral-200 hover:border-black'
                            }`}
                        >
                          <div className="space-y-6">
                            <div>
                              <div className="flex items-center justify-between mb-3">
                                <h3 className="font-serif text-2xl text-black">{plan.name}</h3>
                                {isCurrent && (
                                  <span className="px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] bg-black text-white rounded">
                                    Current
                                  </span>
                                )}
                              </div>
                              <p className="font-sans text-3xl font-semibold text-black mb-2">
                                {planData.price}
                                <span className="text-sm font-normal text-neutral-500">/mo</span>
                              </p>
                              <p className="font-sans text-xs text-[#D4AF37] uppercase tracking-[0.2em] font-semibold">
                                Tier {planData.tier}
                              </p>
                            </div>
                            <div className="space-y-3 py-6 border-t border-neutral-200">
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-xs uppercase tracking-[0.2em] text-[#D4AF37] font-semibold">Cohort Profiles</span>
                                <span className="font-semibold text-black text-base">{planData.cohorts}</span>
                              </div>
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-xs uppercase tracking-[0.2em] text-[#D4AF37] font-semibold">Moves</span>
                                <span className="font-semibold text-black text-base">{planData.moves}</span>
                              </div>
                            </div>
                            <button
                              disabled={isCurrent}
                              onClick={async () => {
                                if (!isCurrent) {
                                  try {
                                    // Create PhonePe checkout session
                                    const response = await backendAPI.payment.createCheckout({
                                      plan: plan.key,
                                      billing_period: 'monthly',
                                      success_url: window.location.origin + '/settings?tab=pricing&payment=success',
                                      cancel_url: window.location.origin + '/settings?tab=pricing&payment=cancelled'
                                    });

                                    // Redirect to PhonePe payment page
                                    if (response.checkout_url) {
                                      window.location.href = response.checkout_url;
                                    } else {
                                      alert('Unable to initiate payment. Please try again.');
                                    }
                                  } catch (error) {
                                    console.error('Payment error:', error);
                                    alert('Payment failed: ' + error.message);
                                  }
                                }
                              }}
                              className={`w-full border-2 px-6 py-3 text-[11px] font-semibold uppercase tracking-[0.2em] transition-colors ${isCurrent
                                ? 'border-neutral-300 bg-neutral-100 text-neutral-400 cursor-not-allowed'
                                : 'border-black text-black hover:bg-black hover:text-white'
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
              <div className="bg-white border-2 border-black p-12">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-4">
                      <span className="font-sans text-[11px] font-semibold uppercase tracking-[0.2em] text-[#D4AF37]">Onboarding</span>
                      <span className="h-px w-8 bg-neutral-300" />
                      <span className="font-sans text-[11px] font-semibold uppercase tracking-[0.2em] text-[#D4AF37]">Setup</span>
                    </div>
                    <h3 className="font-serif text-2xl md:text-3xl text-black leading-tight mb-3">
                      Get Started
                    </h3>
                    <p className="font-sans text-base text-neutral-600 max-w-xl leading-relaxed">
                      Complete the onboarding process to set up your workspace and configure your preferences.
                    </p>
                  </div>
                  <div className="flex items-center">
                    <button
                      onClick={() => navigate('/onboarding-new')}
                      className="group relative inline-flex items-center gap-3 border-2 border-black bg-black text-white px-8 py-3 text-[11px] font-semibold uppercase tracking-[0.2em] hover:bg-neutral-800 transition-colors"
                    >
                      Start Setup
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'data' && (
              <div className="bg-white border-2 border-black p-12 space-y-0">
                <h2 className="font-serif text-3xl text-black mb-8">Data Management</h2>

                {/* Success/Error Messages */}
                {dataMessage.text && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`mb-6 p-4 rounded-lg border-2 ${dataMessage.type === 'success'
                      ? 'bg-green-50 border-green-500 text-green-900'
                      : 'bg-red-50 border-red-500 text-red-900'
                      }`}
                  >
                    <div className="flex items-center gap-2">
                      {dataMessage.type === 'success' ? (
                        <Check className="w-5 h-5" />
                      ) : (
                        <X className="w-5 h-5" />
                      )}
                      <p className="font-sans text-sm font-medium">{dataMessage.text}</p>
                    </div>
                  </motion.div>
                )}

                <div className="space-y-0">
                  <button
                    onClick={handleExportData}
                    className="w-full flex items-center justify-between py-6 px-0 border-b border-neutral-200 hover:bg-neutral-50 transition-colors group"
                  >
                    <div className="flex items-center gap-4">
                      <Download className="w-5 h-5 text-black group-hover:text-neutral-700 transition-colors" />
                      <div className="text-left">
                        <h3 className="font-sans font-semibold text-black mb-1 text-base">Export Data</h3>
                        <p className="font-sans text-sm text-neutral-600">Download your data as JSON</p>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-black transition-colors" />
                  </button>

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".json"
                    onChange={handleImportData}
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full flex items-center justify-between py-6 px-0 border-b border-neutral-200 hover:bg-neutral-50 transition-colors group"
                  >
                    <div className="flex items-center gap-4">
                      <Upload className="w-5 h-5 text-black group-hover:text-neutral-700 transition-colors" />
                      <div className="text-left">
                        <h3 className="font-sans font-semibold text-black mb-1 text-base">Import Data</h3>
                        <p className="font-sans text-sm text-neutral-600">Restore from a saved backup</p>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-black transition-colors" />
                  </button>

                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="w-full flex items-center justify-between py-6 px-0 border-b-0 hover:bg-red-50 transition-colors group"
                  >
                    <div className="flex items-center gap-4">
                      <Trash2 className="w-5 h-5 text-red-600 group-hover:text-red-700 transition-colors" />
                      <div className="text-left">
                        <h3 className="font-sans font-semibold text-red-600 group-hover:text-red-700 mb-1 text-base transition-colors">Delete All Data</h3>
                        <p className="font-sans text-sm text-red-500 group-hover:text-red-600 transition-colors">Permanently delete all data</p>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-red-400 group-hover:text-red-600 transition-colors" />
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="bg-white border-2 border-black p-12 space-y-0">
                <h2 className="font-serif text-3xl text-black mb-8">Security Settings</h2>
                <div className="space-y-0">
                  <button
                    onClick={() => showComingSoonModal('Change Password')}
                    className="w-full flex items-center justify-between px-0 py-6 text-left border-b border-neutral-200 hover:bg-neutral-50 transition-colors group"
                  >
                    <span className="font-sans text-base font-medium text-black">Change Password</span>
                    <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-black transition-colors" />
                  </button>
                  <button
                    onClick={() => showComingSoonModal('Two-Factor Authentication')}
                    className="w-full flex items-center justify-between px-0 py-6 text-left border-b border-neutral-200 hover:bg-neutral-50 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <span className="font-sans text-base font-medium text-black">Two-Factor Authentication</span>
                      <span className="px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.1em] bg-neutral-200 text-neutral-600 rounded">Not Set</span>
                    </div>
                    <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-black transition-colors" />
                  </button>
                  <button
                    onClick={() => showComingSoonModal('Active Sessions')}
                    className="w-full flex items-center justify-between px-0 py-6 text-left border-b-0 hover:bg-neutral-50 transition-colors group"
                  >
                    <span className="font-sans text-base font-medium text-black">Active Sessions</span>
                    <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-black transition-colors" />
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'about' && (
              <div className="bg-white border-2 border-black p-12">
                <h2 className="font-serif text-3xl text-black mb-8">About</h2>
                <div className="space-y-4">
                  <div>
                    <p className="font-serif text-3xl text-black mb-2">Raptorflow v1.0</p>
                    <p className="font-sans text-base text-neutral-600 mb-6">Strategy Execution Platform</p>
                  </div>
                  <button
                    onClick={() => setShowChangelog(true)}
                    className="inline-flex items-center gap-2 border-2 border-black text-black px-6 py-3 text-[11px] font-semibold uppercase tracking-[0.2em] hover:bg-black hover:text-white transition-colors"
                  >
                    View Changelog
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </>
  )
}
