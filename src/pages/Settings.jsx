import { motion, AnimatePresence } from 'framer-motion'
import { Settings as SettingsIcon, Bell, Shield, Palette, Globe, Database, Download, Upload, Trash2, Sparkles, ArrowRight, Check, X, CreditCard, ChevronDown, AlertTriangle, User, Lock, LogOut } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Onboarding from '../components/Onboarding'
import { sanitizeInput, setSecureLocalStorage, getSecureLocalStorage } from '../utils/sanitize'
import { backendAPI } from '../lib/services/backend-api'
import {
  HeroSection,
  LuxeCard,
  LuxeButton,
  LuxeBadge,
  LuxeModal,
  LuxeInput,
  FilterPills,
  staggerContainer,
  fadeInUp
} from '../components/ui/PremiumUI'
import { cn } from '../utils/cn'

const settingsTabs = [
  { value: 'notifications', label: 'Notifications', icon: Bell },
  { value: 'preferences', label: 'Preferences', icon: Palette },
  { value: 'pricing', label: 'Pricing', icon: CreditCard },
  { value: 'onboarding', label: 'Onboarding', icon: Sparkles },
  { value: 'data', label: 'Data', icon: Database },
  { value: 'security', label: 'Security', icon: Shield },
  { value: 'about', label: 'About', icon: Globe },
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
    setPreferences(prev => ({ ...prev, [field]: value }))
  }

  const showComingSoonModal = (feature) => {
    setComingSoonFeature(feature)
    setShowComingSoon(true)
  }

  const handleExportData = () => {
    try {
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

        if (typeof importedData !== 'object' || importedData === null) {
          throw new Error('Invalid data format')
        }

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
    <motion.div
      className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={staggerContainer}
    >
      {showOnboarding && <Onboarding onClose={() => setShowOnboarding(false)} />}

      {/* Modals */}
      <LuxeModal
        isOpen={showChangelog}
        onClose={() => setShowChangelog(false)}
        title="Changelog"
      >
        <div className="space-y-6">
          <div>
            <h3 className="font-display text-xl font-medium text-neutral-900 mb-2">Version 1.0</h3>
            <p className="text-sm text-neutral-500 mb-4">Strategy Execution Platform</p>
            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-sm text-neutral-900 mb-2">Initial Release</h4>
                <ul className="text-sm text-neutral-600 space-y-1 list-disc list-inside">
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
          <LuxeButton onClick={() => setShowChangelog(false)} className="w-full">Close</LuxeButton>
        </div>
      </LuxeModal>

      <LuxeModal
        isOpen={showComingSoon}
        onClose={() => setShowComingSoon(false)}
        title="Coming Soon"
      >
        <div className="text-center space-y-6 py-4">
          <div className="w-16 h-16 rounded-full bg-neutral-50 flex items-center justify-center mx-auto">
            <Shield className="w-8 h-8 text-neutral-400" />
          </div>
          <div>
            <h3 className="font-display text-xl font-medium text-neutral-900 mb-2">{comingSoonFeature}</h3>
            <p className="text-sm text-neutral-600">
              This security feature is currently under development and will be available soon.
            </p>
          </div>
          <LuxeButton onClick={() => setShowComingSoon(false)} className="w-full">Close</LuxeButton>
        </div>
      </LuxeModal>

      <LuxeModal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        title="Delete All Data"
      >
        <div className="space-y-6">
          <div className="p-4 bg-red-50 rounded-xl border border-red-100 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-medium text-red-900">Are you absolutely sure?</p>
              <p className="text-sm text-red-700">This action cannot be undone. This will permanently delete all your data.</p>
            </div>
          </div>

          <ul className="text-sm text-neutral-600 space-y-2 list-disc list-inside pl-2">
            <li>User preferences and settings</li>
            <li>Cohort profiles</li>
            <li>Moves and strategies</li>
            <li>All saved progress</li>
          </ul>

          <div className="flex gap-3 pt-4">
            <LuxeButton variant="outline" onClick={() => setShowDeleteConfirm(false)} className="flex-1">Cancel</LuxeButton>
            <LuxeButton onClick={handleDeleteAllData} className="flex-1 bg-red-600 text-white hover:bg-red-700 border-red-600">Delete Everything</LuxeButton>
          </div>
        </div>
      </LuxeModal>

      {/* Header */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="Settings"
          subtitle="Configure your workspace preferences, notifications, and subscription."
          metrics={[
            { label: 'Current Plan', value: currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1) },
            { label: 'Theme', value: preferences.theme.charAt(0).toUpperCase() + preferences.theme.slice(1) },
            { label: 'Language', value: preferences.language.toUpperCase() }
          ]}
        />
      </motion.div>

      {/* Tabs */}
      <motion.div variants={fadeInUp}>
        <FilterPills
          filters={settingsTabs}
          activeFilter={activeTab}
          onFilterChange={setActiveTab}
          className="mb-8"
        />
      </motion.div>

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
            <LuxeCard className="max-w-2xl">
              <div className="p-6 border-b border-neutral-100">
                <h2 className="font-display text-xl font-medium text-neutral-900">Notification Settings</h2>
                <p className="text-sm text-neutral-500 mt-1">Manage how you receive updates.</p>
              </div>
              <div className="p-6 space-y-6">
                {[
                  { key: 'email', label: 'Email Notifications', description: 'Receive email updates about your campaigns and moves' },
                  { key: 'push', label: 'Push Notifications', description: 'Real-time browser notifications for important events' },
                  { key: 'weekly', label: 'Weekly Reminder', description: 'Weekly recap reminder for your strategy review' },
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-neutral-900">{item.label}</h3>
                      <p className="text-sm text-neutral-500">{item.description}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notifications[item.key]}
                        onChange={(e) => setNotifications({ ...notifications, [item.key]: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-neutral-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-neutral-900"></div>
                    </label>
                  </div>
                ))}
              </div>
            </LuxeCard>
          )}

          {activeTab === 'preferences' && (
            <LuxeCard className="max-w-2xl">
              <div className="p-6 border-b border-neutral-100">
                <h2 className="font-display text-xl font-medium text-neutral-900">Preferences</h2>
                <p className="text-sm text-neutral-500 mt-1">Customize your workspace experience.</p>
              </div>
              <div className="p-6 space-y-8">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-3">Theme</label>
                  <div className="relative">
                    <select
                      value={preferences.theme}
                      onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                      className="w-full bg-white border border-neutral-200 rounded-xl px-4 py-3 pr-10 text-neutral-900 appearance-none cursor-pointer hover:border-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-colors"
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="editorial">Editorial</option>
                      <option value="runway">Runway</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-3">Language</label>
                  <div className="relative">
                    <select
                      value={preferences.language}
                      onChange={(e) => handlePreferenceChange('language', e.target.value)}
                      className="w-full bg-white border border-neutral-200 rounded-xl px-4 py-3 pr-10 text-neutral-900 appearance-none cursor-pointer hover:border-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-colors"
                    >
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                      <option value="de">German</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-3">Timezone</label>
                  <div className="relative">
                    <select
                      value={preferences.timezone}
                      onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
                      className="w-full bg-white border border-neutral-200 rounded-xl px-4 py-3 pr-10 text-neutral-900 appearance-none cursor-pointer hover:border-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-colors"
                    >
                      <option value="UTC">UTC</option>
                      <option value="EST">Eastern Time</option>
                      <option value="PST">Pacific Time</option>
                      <option value="GMT">GMT</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-500 pointer-events-none" />
                  </div>
                </div>
              </div>
            </LuxeCard>
          )}

          {activeTab === 'pricing' && (
            <div className="space-y-8">
              {/* Current Plan */}
              <LuxeCard className="bg-neutral-900 text-white border-none p-8">
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-white/60 mb-2">Current Plan</p>
                    <h2 className="font-display text-4xl font-medium text-white mb-2">
                      {currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)}
                    </h2>
                    <p className="text-neutral-400">
                      {currentPlanData.price}/month
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-display font-medium text-white">{currentPlanData.cohorts}</div>
                    <div className="text-sm text-neutral-400">Cohorts Limit</div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-8 pt-8 border-t border-white/10">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-white/60 mb-2">Cohort Profiles</p>
                    <p className="text-xl font-medium text-white">{currentPlanData.cohorts}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-white/60 mb-2">Moves</p>
                    <p className="text-xl font-medium text-white">{currentPlanData.moves}</p>
                  </div>
                </div>
              </LuxeCard>

              {/* Available Plans */}
              <div>
                <h3 className="font-display text-2xl font-medium text-neutral-900 mb-6">Available Plans</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
                      <LuxeCard
                        key={plan.name}
                        className={cn(
                          "p-8 flex flex-col h-full",
                          isCurrent ? "border-neutral-900 ring-1 ring-neutral-900" : ""
                        )}
                      >
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="font-display text-2xl font-medium text-neutral-900">{plan.name}</h3>
                          {isCurrent && (
                            <LuxeBadge variant="dark">Current</LuxeBadge>
                          )}
                        </div>
                        <p className="text-3xl font-medium text-neutral-900 mb-2">
                          {planData.price}
                          <span className="text-sm font-normal text-neutral-500 ml-1">/mo</span>
                        </p>
                        <p className="text-xs font-bold uppercase tracking-wider text-neutral-400 mb-8">
                          Tier {planData.tier}
                        </p>

                        <div className="space-y-4 mb-8 flex-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-neutral-500">Cohort Profiles</span>
                            <span className="font-medium text-neutral-900">{planData.cohorts}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-neutral-500">Moves</span>
                            <span className="font-medium text-neutral-900">{planData.moves}</span>
                          </div>
                        </div>

                        <LuxeButton
                          variant={isCurrent ? "secondary" : "primary"}
                          disabled={isCurrent}
                          className="w-full justify-center"
                          onClick={async () => {
                            if (!isCurrent) {
                              try {
                                const response = await backendAPI.payment.createCheckout({
                                  plan: plan.key,
                                  billing_period: 'monthly',
                                  success_url: window.location.origin + '/settings?tab=pricing&payment=success',
                                  cancel_url: window.location.origin + '/settings?tab=pricing&payment=cancelled'
                                });
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
                        >
                          {buttonText}
                        </LuxeButton>
                      </LuxeCard>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'onboarding' && (
            <LuxeCard className="p-8">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">Onboarding</span>
                    <span className="h-px w-8 bg-neutral-200" />
                    <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">Setup</span>
                  </div>
                  <h3 className="font-display text-3xl font-medium text-neutral-900 mb-3">
                    Get Started
                  </h3>
                  <p className="text-neutral-600 max-w-xl leading-relaxed">
                    Complete the onboarding process to set up your workspace and configure your preferences.
                  </p>
                </div>
                <div className="flex items-center">
                  <LuxeButton
                    onClick={() => navigate('/onboarding-new')}
                    className="bg-neutral-900 text-white hover:bg-neutral-800"
                  >
                    Start Setup
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </LuxeButton>
                </div>
              </div>
            </LuxeCard>
          )}

          {activeTab === 'data' && (
            <LuxeCard className="max-w-2xl">
              <div className="p-6 border-b border-neutral-100">
                <h2 className="font-display text-xl font-medium text-neutral-900">Data Management</h2>
                <p className="text-sm text-neutral-500 mt-1">Export, import, or delete your data.</p>
              </div>

              {dataMessage.text && (
                <div className={`mx-6 mt-6 p-4 rounded-xl border ${dataMessage.type === 'success'
                  ? 'bg-emerald-50 border-emerald-100 text-emerald-900'
                  : 'bg-red-50 border-red-100 text-red-900'
                  }`}>
                  <div className="flex items-center gap-2">
                    {dataMessage.type === 'success' ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
                    <p className="text-sm font-medium">{dataMessage.text}</p>
                  </div>
                </div>
              )}

              <div className="divide-y divide-neutral-100">
                <button
                  onClick={handleExportData}
                  className="w-full flex items-center justify-between p-6 hover:bg-neutral-50 transition-colors group text-left"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-neutral-50 flex items-center justify-center text-neutral-500 group-hover:bg-neutral-900 group-hover:text-white transition-all">
                      <Download className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-medium text-neutral-900 mb-1">Export Data</h3>
                      <p className="text-sm text-neutral-500">Download your data as JSON</p>
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-neutral-300 group-hover:text-neutral-900 transition-colors" />
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
                  className="w-full flex items-center justify-between p-6 hover:bg-neutral-50 transition-colors group text-left"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-neutral-50 flex items-center justify-center text-neutral-500 group-hover:bg-neutral-900 group-hover:text-white transition-all">
                      <Upload className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-medium text-neutral-900 mb-1">Import Data</h3>
                      <p className="text-sm text-neutral-500">Restore from a saved backup</p>
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-neutral-300 group-hover:text-neutral-900 transition-colors" />
                </button>

                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="w-full flex items-center justify-between p-6 hover:bg-red-50 transition-colors group text-left"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center text-red-500 group-hover:bg-red-600 group-hover:text-white transition-all">
                      <Trash2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-medium text-red-600 mb-1">Delete All Data</h3>
                      <p className="text-sm text-red-400">Permanently delete all data</p>
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-red-200 group-hover:text-red-600 transition-colors" />
                </button>
              </div>
            </LuxeCard>
          )}

          {activeTab === 'security' && (
            <LuxeCard className="max-w-2xl">
              <div className="p-6 border-b border-neutral-100">
                <h2 className="font-display text-xl font-medium text-neutral-900">Security Settings</h2>
                <p className="text-sm text-neutral-500 mt-1">Manage your account security.</p>
              </div>
              <div className="divide-y divide-neutral-100">
                <button
                  onClick={() => showComingSoonModal('Change Password')}
                  className="w-full flex items-center justify-between p-6 hover:bg-neutral-50 transition-colors group text-left"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-neutral-50 flex items-center justify-center text-neutral-500 group-hover:bg-neutral-900 group-hover:text-white transition-all">
                      <Lock className="w-5 h-5" />
                    </div>
                    <span className="font-medium text-neutral-900">Change Password</span>
                  </div>
                  <ArrowRight className="w-5 h-5 text-neutral-300 group-hover:text-neutral-900 transition-colors" />
                </button>
                <button
                  onClick={() => showComingSoonModal('Two-Factor Authentication')}
                  className="w-full flex items-center justify-between p-6 hover:bg-neutral-50 transition-colors group text-left"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-neutral-50 flex items-center justify-center text-neutral-500 group-hover:bg-neutral-900 group-hover:text-white transition-all">
                      <Shield className="w-5 h-5" />
                    </div>
                    <div>
                      <span className="font-medium text-neutral-900 block">Two-Factor Authentication</span>
                      <span className="text-xs text-neutral-500">Not Set</span>
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-neutral-300 group-hover:text-neutral-900 transition-colors" />
                </button>
                <button
                  onClick={() => showComingSoonModal('Active Sessions')}
                  className="w-full flex items-center justify-between p-6 hover:bg-neutral-50 transition-colors group text-left"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-neutral-50 flex items-center justify-center text-neutral-500 group-hover:bg-neutral-900 group-hover:text-white transition-all">
                      <LogOut className="w-5 h-5" />
                    </div>
                    <span className="font-medium text-neutral-900">Active Sessions</span>
                  </div>
                  <ArrowRight className="w-5 h-5 text-neutral-300 group-hover:text-neutral-900 transition-colors" />
                </button>
              </div>
            </LuxeCard>
          )}

          {activeTab === 'about' && (
            <LuxeCard className="max-w-2xl p-8">
              <div className="flex items-start gap-6">
                <div className="w-16 h-16 rounded-2xl bg-neutral-900 flex items-center justify-center text-white">
                  <Globe className="w-8 h-8" />
                </div>
                <div>
                  <h2 className="font-display text-2xl font-medium text-neutral-900 mb-2">Raptorflow v1.0</h2>
                  <p className="text-neutral-600 mb-6">Strategy Execution Platform</p>
                  <LuxeButton
                    onClick={() => setShowChangelog(true)}
                    variant="outline"
                  >
                    View Changelog
                  </LuxeButton>
                </div>
              </div>
            </LuxeCard>
          )}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  )
}
