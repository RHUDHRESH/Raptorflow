import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { onboardingAPI } from '../../lib/api'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../../components/ui/accordion'
import { 
  User, 
  Mail, 
  Calendar,
  CreditCard,
  Save,
  Edit3,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Rocket,
  RefreshCw,
  ChevronRight,
  Shield,
  LogOut
} from 'lucide-react'

const Settings = () => {
  const navigate = useNavigate()
  const { user, profile, updateProfile, refreshProfile, isOnboardingCompleted, signOut } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    full_name: profile?.full_name || '',
  })
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [resettingOnboarding, setResettingOnboarding] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    setSaveSuccess(false)
    
    const { error } = await updateProfile(formData)
    
    if (error) {
      console.error('Error updating profile:', error)
    } else {
      setSaveSuccess(true)
      setIsEditing(false)
      await refreshProfile()
      setTimeout(() => setSaveSuccess(false), 3000)
    }
    
    setSaving(false)
  }

  const planNames = {
    none: 'No Plan',
    ascent: 'Ascent',
    glide: 'Glide',
    soar: 'Soar',
  }

  const planColors = {
    none: 'bg-border',
    ascent: 'bg-accent',
    glide: 'bg-accent-dark',
    soar: 'bg-ink',
  }

  const displayName = profile?.full_name || user?.user_metadata?.full_name || user?.email || 'Account'
  const displayInitial = (displayName || 'U').trim()[0]?.toUpperCase() || 'U'
  const memberSinceLabel = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
    : null

  const autopayLabel = profile?.mandate_status
    ? String(profile.mandate_status).replace(/_/g, ' ')
    : profile?.subscription_id
      ? 'not set'
      : '—'

  const handleSignOut = async () => {
    await signOut()
    navigate('/')
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
        className="masthead mb-10"
      >
        <div className="flex flex-col gap-6">
          <div>
            <h1 className="font-serif text-headline-lg text-ink">Settings</h1>
            <p className="text-body-md text-ink-400 mt-2">Manage your account and preferences</p>
          </div>

          <div className="card-editorial p-5">
            <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-paper-200 border border-border flex items-center justify-center">
                  <span className="font-serif text-xl text-ink">{displayInitial}</span>
                </div>
                <div>
                  <div className="font-serif text-headline-sm text-ink">{displayName}</div>
                  <div className="text-body-sm text-ink-400">
                    {profile?.plan && profile.plan !== 'none' ? (
                      <span className="inline-flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${planColors[profile.plan]}`} />
                        <span className="capitalize">{planNames[profile.plan] || profile.plan}</span>
                      </span>
                    ) : (
                      <span>No active plan</span>
                    )}
                    {memberSinceLabel ? <span> · Member since {memberSinceLabel}</span> : null}
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => navigate('/onboarding/plan')}
                  className="btn-editorial btn-primary"
                  type="button"
                >
                  Manage plan
                </button>
                <button
                  onClick={() => setIsEditing(true)}
                  className="btn-editorial btn-secondary"
                  type="button"
                >
                  <Edit3 className="w-4 h-4" strokeWidth={1.5} />
                  Edit profile
                </button>
                <button
                  onClick={() => navigate('/onboarding')}
                  className="btn-editorial btn-ghost"
                  type="button"
                >
                  <Rocket className="w-4 h-4" strokeWidth={1.5} />
                  Onboarding
                </button>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 bg-paper-200 rounded-card border border-border-light">
                <div className="text-editorial-caption">Email</div>
                <div className="text-body-sm text-ink mt-1 truncate">{user?.email || '—'}</div>
              </div>
              <div className="p-3 bg-paper-200 rounded-card border border-border-light">
                <div className="text-editorial-caption">User ID</div>
                <div className="text-body-sm text-ink mt-1 font-mono truncate">{user?.id || '—'}</div>
              </div>
              <div className="p-3 bg-paper-200 rounded-card border border-border-light">
                <div className="text-editorial-caption">Status</div>
                <div className="text-body-sm text-ink mt-1">
                  {profile?.plan_status ? String(profile.plan_status).replace('_', ' ') : '—'}
                </div>
              </div>
            </div>

            {profile?.subscription_id ? (
              <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 bg-paper-200 rounded-card border border-border-light">
                  <div className="text-editorial-caption">Autopay</div>
                  <div className="text-body-sm text-ink mt-1 capitalize">{autopayLabel}</div>
                  {profile?.mandate_type ? (
                    <div className="text-body-xs text-ink-400 mt-1">
                      {String(profile.mandate_type).replace(/_/g, ' ')} · {profile?.mandate_provider || '—'}
                    </div>
                  ) : null}
                </div>
                <div className="p-3 bg-paper-200 rounded-card border border-border-light">
                  <div className="text-editorial-caption">Autopay enabled</div>
                  <div className="text-body-sm text-ink mt-1">
                    {profile?.autopay_enabled === true ? 'Yes' : 'No'}
                  </div>
                </div>
                <div className="p-3 bg-paper-200 rounded-card border border-border-light">
                  <div className="text-editorial-caption">Mandate ID</div>
                  <div className="text-body-sm text-ink mt-1 font-mono truncate">{profile?.mandate_id || '—'}</div>
                </div>
              </div>
            ) : null}

            <div className="mt-4 pt-4 border-t border-border-light">
              <div className="text-editorial-caption">Profile notes</div>
              <div className="mt-2 max-w-3xl font-serif italic text-body-sm text-ink-400">
                This dossier summarizes your account posture: identity, subscription state, onboarding completion, and billing record.
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Success message */}
      {saveSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-5 bg-success-muted border border-success/20 rounded-card flex items-center gap-3"
        >
          <CheckCircle2 className="w-5 h-5 text-success" strokeWidth={1.5} />
          <p className="text-success text-body-sm">Profile updated successfully</p>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">

      {/* Account Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card-editorial p-8"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-paper-200 rounded-editorial flex items-center justify-center">
              <User className="w-5 h-5 text-ink-400" strokeWidth={1.5} />
            </div>
            <h2 className="font-serif text-headline-sm text-ink">Account Details</h2>
          </div>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="btn-editorial btn-secondary"
            >
              <Edit3 className="w-4 h-4" strokeWidth={1.5} />
              Edit
            </button>
          )}
        </div>

        <div className="rounded-card border border-border-light overflow-hidden">
          <div className="p-5 bg-paper-200">
            <div className="text-editorial-caption">Identity</div>
            <div className="font-serif text-headline-xs text-ink mt-1">
              {profile?.full_name || user?.user_metadata?.full_name || 'Not set'}
            </div>
            <div className="text-body-sm text-ink-400 mt-1">{user?.email || '—'}</div>
          </div>

          <hr className="divider-hairline" />

          <div className="p-5 bg-paper-50">
            <dl className="grid grid-cols-1">
              <div className="grid grid-cols-1 md:grid-cols-12 md:items-center gap-2 py-4">
                <dt className="md:col-span-4 text-editorial-caption">Full name</dt>
                <dd className="md:col-span-8">
                  {isEditing ? (
                    <input
                      type="text"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      placeholder="Enter your full name"
                      className="input-editorial"
                    />
                  ) : (
                    <div className="text-body-sm text-ink">{profile?.full_name || user?.user_metadata?.full_name || 'Not set'}</div>
                  )}
                </dd>
              </div>

              <hr className="divider-hairline" />

              <div className="grid grid-cols-1 md:grid-cols-12 md:items-center gap-2 py-4">
                <dt className="md:col-span-4 text-editorial-caption">Email</dt>
                <dd className="md:col-span-8">
                  <div className="inline-flex items-center gap-2 text-body-sm text-ink-400">
                    <Mail className="w-4 h-4 text-ink-300" strokeWidth={1.5} />
                    <span className="truncate">{user?.email || '—'}</span>
                  </div>
                  <div className="text-body-xs text-ink-400 mt-1">Email cannot be changed.</div>
                </dd>
              </div>

              <hr className="divider-hairline" />

              <div className="grid grid-cols-1 md:grid-cols-12 md:items-center gap-2 py-4">
                <dt className="md:col-span-4 text-editorial-caption">User ID</dt>
                <dd className="md:col-span-8">
                  <code className="text-xs text-ink-400 font-mono bg-paper-200 px-2 py-1 rounded">
                    {user?.id || '—'}
                  </code>
                </dd>
              </div>

              {user?.created_at && (
                <>
                  <hr className="divider-hairline" />
                  <div className="grid grid-cols-1 md:grid-cols-12 md:items-center gap-2 py-4">
                  <dt className="md:col-span-4 text-editorial-caption">Member since</dt>
                  <dd className="md:col-span-8">
                    <div className="inline-flex items-center gap-2 text-body-sm text-ink-400">
                      <Calendar className="w-4 h-4 text-ink-300" strokeWidth={1.5} />
                      <span>
                        {new Date(user.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </span>
                    </div>
                  </dd>
                  </div>
                </>
              )}
            </dl>
          </div>
        </div>

          {/* Save/Cancel buttons */}
          {isEditing && (
            <div className="flex items-center gap-3 pt-4">
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn-editorial btn-primary"
              >
                {saving ? (
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                ) : (
                  <Save className="w-4 h-4" strokeWidth={1.5} />
                )}
                Save Changes
              </button>
              <button
                onClick={() => {
                  setIsEditing(false)
                  setFormData({ full_name: profile?.full_name || '' })
                }}
                className="btn-editorial btn-secondary"
              >
                Cancel
              </button>
            </div>
          )}
      </motion.div>

        </div>

        <div className="card-editorial p-0 overflow-hidden">
          <Accordion type="single" collapsible defaultValue="plan" className="divide-y divide-border-light">
            <AccordionItem value="plan" className="border-b-0">
              <AccordionTrigger className="px-6 py-5 hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-paper-200 rounded-editorial flex items-center justify-center">
                    <CreditCard className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                  </div>
                  <span className="font-serif text-ink">Your Plan</span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="px-6 pb-6">
                {profile?.plan && profile.plan !== 'none' ? (
                  <div className="space-y-4">
                    <div className="p-5 bg-paper-200 border border-border-light rounded-card">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`w-2 h-2 rounded-full ${planColors[profile.plan]}`} />
                            <span className="text-ink font-medium">{planNames[profile.plan]}</span>
                            {profile.plan_status === 'active' && (
                              <span className="pill-editorial pill-success">Active</span>
                            )}
                          </div>
                          <p className="text-body-sm text-ink-400">
                            {profile.plan_status === 'active'
                              ? 'Your plan is active and ready to use'
                              : `Status: ${profile.plan_status}`}
                          </p>
                        </div>
                        <Sparkles className="w-8 h-8 text-accent/30" strokeWidth={1.5} />
                      </div>
                    </div>

                    {profile.plan_started_at && (
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-body-xs text-ink-400 mb-1">Started</p>
                          <p className="text-ink">{new Date(profile.plan_started_at).toLocaleDateString()}</p>
                        </div>
                        {profile.plan_expires_at && (
                          <div>
                            <p className="text-body-xs text-ink-400 mb-1">Expires</p>
                            <p className="text-ink">{new Date(profile.plan_expires_at).toLocaleDateString()}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <div className="w-14 h-14 bg-paper-200 rounded-full flex items-center justify-center mx-auto mb-4">
                      <CreditCard className="w-7 h-7 text-ink-300" strokeWidth={1.5} />
                    </div>
                    <p className="text-ink-400 mb-5">You do not have an active plan</p>
                    <a href="/#pricing" className="btn-editorial btn-primary">View Plans</a>
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="onboarding" className="border-b-0">
              <AccordionTrigger className="px-6 py-5 hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-paper-200 rounded-editorial flex items-center justify-center">
                    <Rocket className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                  </div>
                  <span className="font-serif text-ink">Onboarding & Setup</span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="px-6 pb-6">
                {isOnboardingCompleted ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-5 bg-success-muted border border-success/20 rounded-card">
                      <CheckCircle2 className="w-5 h-5 text-success" strokeWidth={1.5} />
                      <div>
                        <p className="text-success font-medium">Onboarding completed</p>
                        <p className="text-ink-400 text-body-sm">
                          {profile?.onboarding_completed_at
                            ? `Completed on ${new Date(profile.onboarding_completed_at).toLocaleDateString()}`
                            : 'Your setup is complete'}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-3">
                      <button onClick={() => navigate('/onboarding/icps')} className="btn-editorial btn-secondary">
                        View ICPs
                        <ChevronRight className="w-4 h-4" strokeWidth={1.5} />
                      </button>
                      <button onClick={() => navigate('/onboarding/war-plan')} className="btn-editorial btn-secondary">
                        View War Plan
                        <ChevronRight className="w-4 h-4" strokeWidth={1.5} />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-5 bg-warning-muted border border-warning/20 rounded-card">
                      <AlertCircle className="w-5 h-5 text-warning" strokeWidth={1.5} />
                      <div>
                        <p className="text-ink font-medium">Onboarding required</p>
                        <p className="text-ink-400 text-body-sm">Complete your onboarding to unlock all features</p>
                      </div>
                    </div>
                    <button onClick={() => navigate('/onboarding')} className="btn-editorial btn-primary">
                      <Rocket className="w-4 h-4" strokeWidth={1.5} />
                      Start Onboarding
                    </button>
                  </div>
                )}

                {isOnboardingCompleted && (
                  <div className="mt-6 pt-6 border-t border-border-light">
                    <p className="text-ink-400 text-body-sm mb-4">
                      Want to start fresh? This will reset all your onboarding data.
                    </p>
                    <button
                      onClick={async () => {
                        if (window.confirm('Are you sure you want to reset your onboarding? This will clear all your ICP and positioning data.')) {
                          setResettingOnboarding(true)
                          try {
                            await onboardingAPI.reset()
                            await refreshProfile()
                            navigate('/onboarding')
                          } catch (err) {
                            console.error('Failed to reset onboarding:', err)
                            alert('Failed to reset onboarding. Please try again.')
                          } finally {
                            setResettingOnboarding(false)
                          }
                        }
                      }}
                      disabled={resettingOnboarding}
                      className="btn-editorial btn-secondary text-error border-error/20 hover:bg-error-muted"
                    >
                      {resettingOnboarding ? (
                        <div className="w-4 h-4 border-2 border-error/30 border-t-error rounded-full animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4" strokeWidth={1.5} />
                      )}
                      Reset Onboarding
                    </button>
                  </div>
                )}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="security" className="border-b-0">
              <AccordionTrigger className="px-6 py-5 hover:no-underline">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-paper-200 rounded-editorial flex items-center justify-center">
                    <Shield className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                  </div>
                  <span className="font-serif text-ink">Security & Sessions</span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="px-6 pb-6">
                <div className="space-y-4">
                  <div className="p-5 bg-paper-200 rounded-card border border-border-light">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-editorial-caption">Session</div>
                        <div className="text-body-sm text-ink mt-1">Signed in</div>
                        <div className="text-body-xs text-ink-400 mt-1">For your security, sign out on shared devices.</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button onClick={handleSignOut} className="btn-editorial btn-primary" type="button">
                          <LogOut className="w-4 h-4" strokeWidth={1.5} />
                          Sign out
                        </button>
                        <button onClick={() => navigate('/')} className="btn-editorial btn-secondary" type="button">
                          Exit
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="p-5 bg-paper-200 rounded-card border border-border-light">
                    <div className="text-editorial-caption">Account email</div>
                    <div className="text-body-sm text-ink mt-1">{user?.email || '—'}</div>
                    <div className="text-body-xs text-ink-400 mt-2">Email changes are not supported in this build.</div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>

      </div>

      {/* Payment History */}
      {profile?.plan && profile.plan !== 'none' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card-editorial p-8 mt-10"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-paper-200 rounded-editorial flex items-center justify-center">
              <CreditCard className="w-5 h-5 text-ink-400" strokeWidth={1.5} />
            </div>
            <h2 className="font-serif text-headline-sm text-ink">Payment History</h2>
          </div>

          {profile.last_payment_date ? (
            <div className="bg-paper-200 rounded-card border border-border-light overflow-hidden">
              <div className="p-5">
                <div className="text-editorial-caption">Receipt</div>
                <div className="font-serif text-headline-xs text-ink mt-1">{planNames[profile.plan]} Plan</div>
                <div className="text-body-sm text-ink-400 mt-1">{new Date(profile.last_payment_date).toLocaleDateString()}</div>
              </div>
              <hr className="divider-hairline" />
              <div className="p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-body-sm text-ink-400">Reference</span>
                  <span className="text-body-sm text-ink font-mono">
                    {user?.id ? `RF-${user.id.slice(0, 8).toUpperCase()}` : '—'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-body-sm text-ink-400">Amount</span>
                  <span className="text-body-sm text-ink font-medium">
                    ₹{profile.last_payment_amount ? (profile.last_payment_amount / 100).toLocaleString() : 'N/A'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-body-sm text-ink-400">Status</span>
                  <span className={`pill-editorial ${profile.payment_status === 'completed' ? 'pill-success' : 'pill-neutral'}`}>
                    {profile.payment_status || 'pending'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-body-sm text-ink-400">Account</span>
                  <span className="text-body-sm text-ink">{user?.email || '—'}</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-ink-400 text-body-sm">No payment history yet</p>
          )}
        </motion.div>
      )}
    </div>
  )
}

export default Settings

