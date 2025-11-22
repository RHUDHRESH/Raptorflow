import { motion, AnimatePresence } from 'framer-motion'
import { User, Mail, Building, Calendar, MapPin, Phone, Edit2, Save, X, AlertCircle } from 'lucide-react'
import { useState, useEffect } from 'react'
import { sanitizeInput, setSecureLocalStorage, getSecureLocalStorage } from '../utils/sanitize'
import { validateEmail, validatePhone, validateRequired, validateTextArea } from '../utils/validation'

export default function Account() {
  const [isEditing, setIsEditing] = useState(false)
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const [profile, setProfile] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    company: 'Acme Corp',
    role: 'Strategy Lead',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    joinedDate: 'January 2024',
    bio: 'Strategic thinker with a passion for execution and results.',
  })
  const [originalProfile, setOriginalProfile] = useState(profile)

  // Load profile from secure localStorage on mount
  useEffect(() => {
    const savedProfile = getSecureLocalStorage('userProfile')
    if (savedProfile) {
      setProfile(savedProfile)
      setOriginalProfile(savedProfile)
    }
  }, [])

  const handleChange = (field, value) => {
    // Sanitize input on change
    const sanitizedValue = sanitizeInput(value)
    setProfile(prev => ({ ...prev, [field]: sanitizedValue }))

    // Clear error for this field when user is typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const handleBlur = (field) => {
    // Mark field as touched
    setTouched(prev => ({ ...prev, [field]: true }))
    
    // Validate only this field
    validateField(field)
  }

  const validateField = (field) => {
    let validation = { isValid: true, error: '' }

    switch (field) {
      case 'name':
        validation = validateRequired(profile.name, 'Name', 2, 100)
        break
      case 'email':
        validation = validateEmail(profile.email)
        break
      case 'phone':
        validation = validatePhone(profile.phone)
        break
      case 'bio':
        validation = validateTextArea(profile.bio, 'Bio', 500)
        break
      default:
        break
    }

    if (!validation.isValid) {
      setErrors(prev => ({ ...prev, [field]: validation.error }))
    } else {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const validateProfile = () => {
    const newErrors = {}

    // Validate name
    const nameValidation = validateRequired(profile.name, 'Name', 2, 100)
    if (!nameValidation.isValid) {
      newErrors.name = nameValidation.error
    }

    // Validate email
    const emailValidation = validateEmail(profile.email)
    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.error
    }

    // Validate phone (optional)
    const phoneValidation = validatePhone(profile.phone)
    if (!phoneValidation.isValid) {
      newErrors.phone = phoneValidation.error
    }

    // Validate bio
    const bioValidation = validateTextArea(profile.bio, 'Bio', 500)
    if (!bioValidation.isValid) {
      newErrors.bio = bioValidation.error
    }

    setErrors(newErrors)
    // Mark all fields as touched on submit attempt
    setTouched({ name: true, email: true, phone: true, bio: true })
    return Object.keys(newErrors).length === 0
  }

  const handleSave = () => {
    // Validate before saving
    if (!validateProfile()) {
      return
    }

    // Save to secure localStorage
    setSecureLocalStorage('userProfile', profile)
    setOriginalProfile(profile)
    setIsEditing(false)
    setErrors({})
    setTouched({})
  }

  const handleCancel = () => {
    // Reset to original values
    setProfile(originalProfile)
    setIsEditing(false)
    setErrors({})
    setTouched({})
  }

  return (
    <div className="animate-fade-in h-full flex flex-col">
      {/* Header - Compact */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="pb-4"
      >
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="micro-label tracking-[0.5em]">Portrait</span>
              <span className="h-px w-16 bg-neutral-200" />
            </div>
            <h1 className="font-serif text-3xl md:text-4xl text-black leading-tight tracking-tight antialiased">
              Archive Your Presence
            </h1>
          </div>
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 border-2 border-neutral-900 bg-black text-white px-5 py-2 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-colors flex-shrink-0"
            >
              <Edit2 className="w-4 h-4" />
              Edit
            </button>
          )}
          {isEditing && (
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                className="flex items-center gap-2 border-2 border-neutral-900 bg-black text-white px-5 py-2 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-colors"
              >
                <Save className="w-4 h-4" />
                Save
              </button>
              <button
                onClick={handleCancel}
                className="flex items-center gap-2 border-2 border-neutral-200 px-5 py-2 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-600 hover:bg-neutral-50 transition-colors"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
            </div>
          )}
        </div>
      </motion.div>

      {/* Profile Overview - Compact */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="runway-card p-6 mb-4"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-neutral-900 text-white flex items-center justify-center flex-shrink-0">
            <User className="w-8 h-8" />
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="font-serif text-xl text-neutral-900 mb-1">
              {profile.name}
            </h2>
            <p className="font-sans text-sm text-neutral-600 mb-2">{profile.role}</p>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-neutral-600">
              <div className="flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5" />
                <span>{profile.company}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5" />
                <span>{profile.location}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" />
                <span>Joined {profile.joinedDate}</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Profile Details - Grid Layout */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="runway-card flex-1 overflow-hidden flex flex-col"
      >
        <div className="p-6 border-b border-neutral-200 flex-shrink-0">
          <h2 className="font-serif text-xl text-neutral-900">Studio Details</h2>
        </div>

        <div className="p-6 flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={isEditing ? 'editing' : 'viewing'}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4"
            >
              {/* Full Name */}
              <div className="border-b border-neutral-200 pb-3">
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-1.5">
                  Full Name
                </label>
                {isEditing ? (
                  <>
                    <input
                      type="text"
                      value={profile.name}
                      onChange={(e) => handleChange('name', e.target.value)}
                      onBlur={() => handleBlur('name')}
                      className={`w-full px-0 py-1.5 border-b ${touched.name && errors.name ? 'border-red-500' : 'border-neutral-200'} bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                    />
                    {touched.name && errors.name && (
                      <p className="text-xs text-red-600 mt-1">{errors.name}</p>
                    )}
                  </>
                ) : (
                  <p className="font-serif text-base text-neutral-900">{profile.name}</p>
                )}
              </div>

              {/* Email */}
              <div className="border-b border-neutral-200 pb-3">
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-1.5">
                  Email
                </label>
                {isEditing ? (
                  <>
                    <input
                      type="email"
                      value={profile.email}
                      onChange={(e) => handleChange('email', e.target.value)}
                      onBlur={() => handleBlur('email')}
                      className={`w-full px-0 py-1.5 border-b ${touched.email && errors.email ? 'border-red-500' : 'border-neutral-200'} bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                    />
                    {touched.email && errors.email && (
                      <p className="text-xs text-red-600 mt-1">{errors.email}</p>
                    )}
                  </>
                ) : (
                  <div className="flex items-center gap-2">
                    <Mail className="w-3.5 h-3.5 text-neutral-400" />
                    <p className="font-serif text-base text-neutral-900">{profile.email}</p>
                  </div>
                )}
              </div>

              {/* Company */}
              <div className="border-b border-neutral-200 pb-3">
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-1.5">
                  Company
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={profile.company}
                    onChange={(e) => handleChange('company', e.target.value)}
                    className="w-full px-0 py-1.5 border-b border-neutral-200 bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base"
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    <Building className="w-3.5 h-3.5 text-neutral-400" />
                    <p className="font-serif text-base text-neutral-900">{profile.company}</p>
                  </div>
                )}
              </div>

              {/* Role */}
              <div className="border-b border-neutral-200 pb-3">
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-1.5">
                  Role
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={profile.role}
                    onChange={(e) => handleChange('role', e.target.value)}
                    className="w-full px-0 py-1.5 border-b border-neutral-200 bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base"
                  />
                ) : (
                  <p className="font-serif text-base text-neutral-900">{profile.role}</p>
                )}
              </div>

              {/* Phone */}
              <div className="border-b border-neutral-200 pb-3">
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-1.5">
                  Phone
                </label>
                {isEditing ? (
                  <>
                    <input
                      type="tel"
                      value={profile.phone}
                      onChange={(e) => handleChange('phone', e.target.value)}
                      onBlur={() => handleBlur('phone')}
                      className={`w-full px-0 py-1.5 border-b ${touched.phone && errors.phone ? 'border-red-500' : 'border-neutral-200'} bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                    />
                    {touched.phone && errors.phone && (
                      <p className="text-xs text-red-600 mt-1">{errors.phone}</p>
                    )}
                  </>
                ) : (
                  <div className="flex items-center gap-2">
                    <Phone className="w-3.5 h-3.5 text-neutral-400" />
                    <p className="font-serif text-base text-neutral-900">{profile.phone}</p>
                  </div>
                )}
              </div>

              {/* Location */}
              <div className="border-b border-neutral-200 pb-3">
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-1.5">
                  Location
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={profile.location}
                    onChange={(e) => handleChange('location', e.target.value)}
                    className="w-full px-0 py-1.5 border-b border-neutral-200 bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base"
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-neutral-400" />
                    <p className="font-serif text-base text-neutral-900">{profile.location}</p>
                  </div>
                )}
              </div>

              {/* Bio - Full Width */}
              <div className="md:col-span-2 border-b border-neutral-200 pb-3">
                <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-1.5">
                  Bio
                </label>
                {isEditing ? (
                  <>
                    <textarea
                      rows={2}
                      value={profile.bio}
                      onChange={(e) => handleChange('bio', e.target.value)}
                      onBlur={() => handleBlur('bio')}
                      className={`w-full px-0 py-1.5 border-b ${touched.bio && errors.bio ? 'border-red-500' : 'border-neutral-200'} bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base resize-none`}
                    />
                    {touched.bio && errors.bio && (
                      <p className="text-xs text-red-600 mt-1">{errors.bio}</p>
                    )}
                  </>
                ) : (
                  <p className="font-serif text-base text-neutral-900 leading-relaxed">{profile.bio}</p>
                )}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  )
}

