import { motion, AnimatePresence } from 'framer-motion'
import { User, Mail, Building, Calendar, MapPin, Phone, Edit2, Save, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import { sanitizeInput, setSecureLocalStorage, getSecureLocalStorage } from '../utils/sanitize'
import { validateEmail, validatePhone, validateRequired, validateTextArea } from '../utils/validation'
import {
  HeroSection,
  LuxeCard,
  LuxeButton,
  LuxeInput,
  staggerContainer,
  fadeInUp
} from '../components/ui/PremiumUI'

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
    const sanitizedValue = sanitizeInput(value)
    setProfile(prev => ({ ...prev, [field]: sanitizedValue }))

    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const handleBlur = (field) => {
    setTouched(prev => ({ ...prev, [field]: true }))
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

    const nameValidation = validateRequired(profile.name, 'Name', 2, 100)
    if (!nameValidation.isValid) {
      newErrors.name = nameValidation.error
    }

    const emailValidation = validateEmail(profile.email)
    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.error
    }

    const phoneValidation = validatePhone(profile.phone)
    if (!phoneValidation.isValid) {
      newErrors.phone = phoneValidation.error
    }

    const bioValidation = validateTextArea(profile.bio, 'Bio', 500)
    if (!bioValidation.isValid) {
      newErrors.bio = bioValidation.error
    }

    setErrors(newErrors)
    setTouched({ name: true, email: true, phone: true, bio: true })
    return Object.keys(newErrors).length === 0
  }

  const handleSave = () => {
    if (!validateProfile()) {
      return
    }

    setSecureLocalStorage('userProfile', profile)
    setOriginalProfile(profile)
    setIsEditing(false)
    setErrors({})
    setTouched({})
  }

  const handleCancel = () => {
    setProfile(originalProfile)
    setIsEditing(false)
    setErrors({})
    setTouched({})
  }

  return (
    <motion.div
      className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={staggerContainer}
    >
      {/* Header */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="Account Profile"
          subtitle="Manage your personal information and preferences."
          metrics={[
            { label: 'Member Since', value: profile.joinedDate },
            { label: 'Company', value: profile.company },
            { label: 'Role', value: profile.role }
          ]}
          actions={
            !isEditing ? (
              <LuxeButton onClick={() => setIsEditing(true)} className="bg-white text-neutral-900 hover:bg-neutral-100 border-none">
                <Edit2 className="w-4 h-4 mr-2" />
                Edit Profile
              </LuxeButton>
            ) : (
              <div className="flex gap-2">
                <LuxeButton onClick={handleSave} className="bg-white text-neutral-900 hover:bg-neutral-100 border-none">
                  <Save className="w-4 h-4 mr-2" />
                  Save
                </LuxeButton>
                <LuxeButton onClick={handleCancel} variant="ghost" className="text-white hover:bg-white/10">
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </LuxeButton>
              </div>
            )
          }
        />
      </motion.div>

      {/* Profile Overview */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8">
          <div className="flex items-center gap-6 mb-8">
            <div className="w-20 h-20 rounded-full bg-neutral-900 text-white flex items-center justify-center shrink-0">
              <User className="w-10 h-10" />
            </div>
            <div>
              <h2 className="font-display text-2xl font-medium text-neutral-900 mb-1">
                {profile.name}
              </h2>
              <p className="text-neutral-600 mb-2">{profile.role}</p>
              <div className="flex flex-wrap gap-4 text-sm text-neutral-500">
                <div className="flex items-center gap-1.5">
                  <Building className="w-4 h-4" />
                  <span>{profile.company}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4" />
                  <span>{profile.location}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  <span>Joined {profile.joinedDate}</span>
                </div>
              </div>
            </div>
          </div>
        </LuxeCard>
      </motion.div>

      {/* Profile Details */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8">
          <h2 className="font-display text-xl font-medium text-neutral-900 mb-6">Profile Details</h2>

          <AnimatePresence mode="wait">
            <motion.div
              key={isEditing ? 'editing' : 'viewing'}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              {/* Full Name */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                  Full Name
                </label>
                {isEditing ? (
                  <LuxeInput
                    value={profile.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    onBlur={() => handleBlur('name')}
                    error={touched.name && errors.name}
                  />
                ) : (
                  <p className="text-neutral-900 font-medium">{profile.name}</p>
                )}
              </div>

              {/* Email */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                  Email
                </label>
                {isEditing ? (
                  <LuxeInput
                    type="email"
                    value={profile.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    onBlur={() => handleBlur('email')}
                    error={touched.email && errors.email}
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-neutral-400" />
                    <p className="text-neutral-900 font-medium">{profile.email}</p>
                  </div>
                )}
              </div>

              {/* Company */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                  Company
                </label>
                {isEditing ? (
                  <LuxeInput
                    value={profile.company}
                    onChange={(e) => handleChange('company', e.target.value)}
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    <Building className="w-4 h-4 text-neutral-400" />
                    <p className="text-neutral-900 font-medium">{profile.company}</p>
                  </div>
                )}
              </div>

              {/* Role */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                  Role
                </label>
                {isEditing ? (
                  <LuxeInput
                    value={profile.role}
                    onChange={(e) => handleChange('role', e.target.value)}
                  />
                ) : (
                  <p className="text-neutral-900 font-medium">{profile.role}</p>
                )}
              </div>

              {/* Phone */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                  Phone
                </label>
                {isEditing ? (
                  <LuxeInput
                    type="tel"
                    value={profile.phone}
                    onChange={(e) => handleChange('phone', e.target.value)}
                    onBlur={() => handleBlur('phone')}
                    error={touched.phone && errors.phone}
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-neutral-400" />
                    <p className="text-neutral-900 font-medium">{profile.phone}</p>
                  </div>
                )}
              </div>

              {/* Location */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                  Location
                </label>
                {isEditing ? (
                  <LuxeInput
                    value={profile.location}
                    onChange={(e) => handleChange('location', e.target.value)}
                  />
                ) : (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-neutral-400" />
                    <p className="text-neutral-900 font-medium">{profile.location}</p>
                  </div>
                )}
              </div>

              {/* Bio - Full Width */}
              <div className="md:col-span-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">
                  Bio
                </label>
                {isEditing ? (
                  <div>
                    <textarea
                      rows={3}
                      value={profile.bio}
                      onChange={(e) => handleChange('bio', e.target.value)}
                      onBlur={() => handleBlur('bio')}
                      className={`w-full px-4 py-3 border rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm resize-none ${touched.bio && errors.bio ? 'border-red-500' : 'border-neutral-200'}`}
                    />
                    {touched.bio && errors.bio && (
                      <p className="text-xs text-red-600 mt-1">{errors.bio}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-neutral-900 leading-relaxed">{profile.bio}</p>
                )}
              </div>
            </motion.div>
          </AnimatePresence>
        </LuxeCard>
      </motion.div>
    </motion.div>
  )
}
