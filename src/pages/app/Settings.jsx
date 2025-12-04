import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../../contexts/AuthContext'
import { 
  User, 
  Mail, 
  Calendar,
  CreditCard,
  Save,
  Edit3,
  CheckCircle2,
  AlertCircle,
  Crown,
  Sparkles
} from 'lucide-react'

const Settings = () => {
  const { user, profile, updateProfile, refreshProfile } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    full_name: profile?.full_name || '',
  })
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

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
    none: 'bg-zinc-500',
    ascent: 'bg-amber-500',
    glide: 'bg-amber-600',
    soar: 'bg-amber-700',
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-light text-white">Settings</h1>
        <p className="text-white/40 mt-1">
          Manage your account and preferences
        </p>
      </motion.div>

      {/* Success message */}
      {saveSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-3"
        >
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <p className="text-emerald-400 text-sm">Profile updated successfully</p>
        </motion.div>
      )}

      {/* Account Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-zinc-900/50 border border-white/5 rounded-xl p-6 mb-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/5 rounded-lg">
              <User className="w-5 h-5 text-white/60" />
            </div>
            <h2 className="text-xl font-medium text-white">Account Details</h2>
          </div>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-white/60 hover:text-white transition-colors"
            >
              <Edit3 className="w-4 h-4" />
              Edit
            </button>
          )}
        </div>

        <div className="space-y-4">
          {/* Email (read-only) */}
          <div>
            <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">
              Email
            </label>
            <div className="flex items-center gap-3">
              <Mail className="w-4 h-4 text-white/30" />
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white/60 cursor-not-allowed"
              />
            </div>
            <p className="text-xs text-white/30 mt-1">Email cannot be changed</p>
          </div>

          {/* Full Name */}
          <div>
            <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">
              Full Name
            </label>
            {isEditing ? (
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="Enter your full name"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:border-amber-500/50 focus:outline-none"
              />
            ) : (
              <div className="flex items-center gap-3">
                <User className="w-4 h-4 text-white/30" />
                <p className="text-white/80">
                  {profile?.full_name || user?.user_metadata?.full_name || 'Not set'}
                </p>
              </div>
            )}
          </div>

          {/* User ID */}
          <div>
            <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">
              User ID
            </label>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4" />
              <code className="text-xs text-white/40 font-mono bg-white/5 px-2 py-1 rounded">
                {user?.id || 'N/A'}
              </code>
            </div>
          </div>

          {/* Account Created */}
          {user?.created_at && (
            <div>
              <label className="text-xs text-white/40 uppercase tracking-wider mb-2 block">
                Member Since
              </label>
              <div className="flex items-center gap-3">
                <Calendar className="w-4 h-4 text-white/30" />
                <p className="text-white/60">
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
            </div>
          )}

          {/* Save/Cancel buttons */}
          {isEditing && (
            <div className="flex items-center gap-3 pt-4">
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg transition-colors disabled:opacity-50"
              >
                {saving ? (
                  <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                Save Changes
              </button>
              <button
                onClick={() => {
                  setIsEditing(false)
                  setFormData({ full_name: profile?.full_name || '' })
                }}
                className="px-5 py-2.5 bg-white/5 hover:bg-white/10 text-white/60 hover:text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </motion.div>

      {/* Plan Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-zinc-900/50 border border-white/5 rounded-xl p-6 mb-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-white/5 rounded-lg">
            <Crown className="w-5 h-5 text-white/60" />
          </div>
          <h2 className="text-xl font-medium text-white">Your Plan</h2>
        </div>

        {profile?.plan && profile.plan !== 'none' ? (
          <div className="space-y-4">
            {/* Current Plan */}
            <div className="p-4 bg-gradient-to-br from-amber-500/10 to-amber-600/5 border border-amber-500/20 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`w-2 h-2 rounded-full ${planColors[profile.plan]}`} />
                    <span className="text-white font-medium">{planNames[profile.plan]}</span>
                    {profile.plan_status === 'active' && (
                      <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-xs rounded">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-white/40 text-sm">
                    {profile.plan_status === 'active' 
                      ? 'Your plan is active and ready to use'
                      : `Status: ${profile.plan_status}`
                    }
                  </p>
                </div>
                <Sparkles className="w-8 h-8 text-amber-400/30" />
              </div>
            </div>

            {/* Plan Dates */}
            {profile.plan_started_at && (
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-white/40 mb-1">Started</p>
                  <p className="text-white">
                    {new Date(profile.plan_started_at).toLocaleDateString()}
                  </p>
                </div>
                {profile.plan_expires_at && (
                  <div>
                    <p className="text-white/40 mb-1">Expires</p>
                    <p className="text-white">
                      {new Date(profile.plan_expires_at).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
              <Crown className="w-8 h-8 text-white/20" />
            </div>
            <p className="text-white/60 mb-4">You don't have an active plan</p>
            <a
              href="/#pricing"
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg transition-colors"
            >
              View Plans
            </a>
          </div>
        )}
      </motion.div>

      {/* Payment History */}
      {profile?.plan && profile.plan !== 'none' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-zinc-900/50 border border-white/5 rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-white/5 rounded-lg">
              <CreditCard className="w-5 h-5 text-white/60" />
            </div>
            <h2 className="text-xl font-medium text-white">Payment History</h2>
          </div>

          {profile.last_payment_date ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="text-white font-medium">{planNames[profile.plan]} Plan</p>
                  <p className="text-white/40 text-sm">
                    {new Date(profile.last_payment_date).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-white font-medium">
                    ₹{profile.last_payment_amount ? (profile.last_payment_amount / 100).toLocaleString() : 'N/A'}
                  </p>
                  <p className={`text-xs ${
                    profile.payment_status === 'completed' ? 'text-emerald-400' : 'text-white/40'
                  }`}>
                    {profile.payment_status || 'pending'}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-white/40 text-sm">No payment history yet</p>
          )}
        </motion.div>
      )}
    </div>
  )
}

export default Settings

