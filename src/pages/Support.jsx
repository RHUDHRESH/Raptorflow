import { motion, AnimatePresence } from 'framer-motion'
import { Mail, MessageSquare, Book, FileText, Send, ArrowRight, X, Check, ExternalLink, HelpCircle } from 'lucide-react'
import { useState } from 'react'
import { sanitizeInput } from '../utils/sanitize'
import { validateEmail, validateRequired } from '../utils/validation'
import {
  HeroSection,
  LuxeCard,
  LuxeButton,
  LuxeInput,
  LuxeModal,
  fadeInUp,
  staggerContainer
} from '../components/ui/PremiumUI'

export default function Support() {
  const [activeModal, setActiveModal] = useState(null)
  const [formData, setFormData] = useState({ subject: '', message: '', email: '', name: '' })
  const [errors, setErrors] = useState({})
  const [submitSuccess, setSubmitSuccess] = useState(false)

  const openModal = (modalName) => {
    setActiveModal(modalName)
    setFormData({ subject: '', message: '', email: '', name: '' })
    setErrors({})
    setSubmitSuccess(false)
  }

  const closeModal = () => {
    setActiveModal(null)
    setFormData({ subject: '', message: '', email: '', name: '' })
    setErrors({})
    setSubmitSuccess(false)
  }

  const handleChange = (field, value) => {
    const sanitizedValue = sanitizeInput(value)
    setFormData(prev => ({ ...prev, [field]: sanitizedValue }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const validateForm = () => {
    const newErrors = {}

    const emailValidation = validateEmail(formData.email)
    if (!emailValidation.isValid) {
      newErrors.email = emailValidation.error
    }

    const nameValidation = validateRequired(formData.name, 'Name', 2, 100)
    if (!nameValidation.isValid) {
      newErrors.name = nameValidation.error
    }

    const subjectValidation = validateRequired(formData.subject, 'Subject', 3, 200)
    if (!subjectValidation.isValid) {
      newErrors.subject = subjectValidation.error
    }

    const messageValidation = validateRequired(formData.message, 'Message', 10, 2000)
    if (!messageValidation.isValid) {
      newErrors.message = messageValidation.error
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validateForm()) {
      // In production, send to backend
      setSubmitSuccess(true)
      setTimeout(() => {
        closeModal()
      }, 2000)
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
      {/* Hero Section */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="Support & Feedback"
          subtitle="We're here to help. Get assistance with your account, features, or submit feedback."
          metrics={[
            { label: 'Avg Response', value: '< 24h' },
            { label: 'Satisfaction', value: '98%' },
            { label: 'Status', value: 'Online' }
          ]}
        />
      </motion.div>

      {/* Support Channels */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        variants={staggerContainer}
      >
        {[
          {
            title: 'Email Support',
            description: 'Send us a message and we will respond within 24 hours',
            icon: Mail,
            action: 'Send Email',
            modalKey: 'email',
          },
          {
            title: 'Live Chat',
            description: 'Chat with our support team in real-time',
            icon: MessageSquare,
            action: 'Start Chat',
            modalKey: 'chat',
          },
          {
            title: 'Documentation',
            description: 'Browse guides, tutorials, and best practices',
            icon: Book,
            action: 'View Docs',
            modalKey: 'docs',
          },
          {
            title: 'Feature Request',
            description: 'Suggest new features or improvements',
            icon: FileText,
            action: 'Submit Request',
            modalKey: 'feature',
          },
        ].map((option, index) => {
          const Icon = option.icon
          return (
            <motion.div key={option.title} variants={fadeInUp}>
              <LuxeCard
                className="h-full flex flex-col hover:shadow-lg transition-all cursor-pointer group p-6"
                onClick={() => openModal(option.modalKey)}
              >
                <div className="w-12 h-12 rounded-xl bg-neutral-50 flex items-center justify-center mb-6 group-hover:bg-neutral-900 group-hover:text-white transition-all">
                  <Icon className="w-6 h-6" />
                </div>

                <h3 className="font-display text-xl font-medium text-neutral-900 mb-2">
                  {option.title}
                </h3>
                <p className="text-sm text-neutral-600 mb-6 flex-1">
                  {option.description}
                </p>

                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-neutral-900 group-hover:translate-x-1 transition-transform">
                  {option.action}
                  <ArrowRight className="w-3 h-3" />
                </div>
              </LuxeCard>
            </motion.div>
          )
        })}
      </motion.div>

      {/* Contact Form */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8 md:p-12">
          <div className="flex flex-col md:flex-row gap-12">
            <div className="md:w-1/3 space-y-6">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Contact Us</p>
                <h2 className="font-display text-3xl font-medium text-neutral-900">Send us a Message</h2>
              </div>
              <p className="text-neutral-600 leading-relaxed">
                Have a specific question or need detailed assistance? Fill out the form and our team will get back to you as soon as possible.
              </p>
              <div className="flex items-center gap-3 text-sm text-neutral-500">
                <HelpCircle className="w-4 h-4" />
                <span>We typically respond within 24 hours</span>
              </div>
            </div>

            <div className="md:w-2/3 space-y-6">
              <LuxeInput
                label="Subject"
                placeholder="What can we help you with?"
                value={formData.subject} // Although not controlled here, just for visual layout
                onChange={() => { }} // Placeholder
                readOnly
                onClick={() => openModal('contact')}
                className="cursor-pointer"
              />
              <div className="relative">
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Message</label>
                <div
                  className="w-full p-4 border border-neutral-200 rounded-xl bg-neutral-50 text-neutral-400 h-32 cursor-pointer hover:border-neutral-400 transition-colors"
                  onClick={() => openModal('contact')}
                >
                  Please provide details about your question or issue...
                </div>
              </div>
              <div className="flex justify-end">
                <LuxeButton onClick={() => openModal('contact')}>
                  Send Message
                  <Send className="w-4 h-4 ml-2" />
                </LuxeButton>
              </div>
            </div>
          </div>
        </LuxeCard>
      </motion.div>

      {/* Modals */}
      <LuxeModal
        isOpen={activeModal === 'email' || activeModal === 'contact'}
        onClose={closeModal}
        title={activeModal === 'email' ? 'Email Support' : 'Contact Us'}
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          {submitSuccess ? (
            <div className="text-center py-8 space-y-4">
              <div className="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto">
                <Check className="w-8 h-8 text-emerald-600" />
              </div>
              <h3 className="font-display text-2xl font-medium text-neutral-900">Message Sent!</h3>
              <p className="text-neutral-600">
                We've received your message and will respond within 24 hours.
              </p>
            </div>
          ) : (
            <>
              <LuxeInput
                label="Name"
                placeholder="Your name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                error={errors.name}
              />
              <LuxeInput
                label="Email"
                placeholder="your@email.com"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                error={errors.email}
              />
              <LuxeInput
                label="Subject"
                placeholder="What can we help you with?"
                value={formData.subject}
                onChange={(e) => handleChange('subject', e.target.value)}
                error={errors.subject}
              />
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Message</label>
                <textarea
                  rows={5}
                  value={formData.message}
                  onChange={(e) => handleChange('message', e.target.value)}
                  className={`w-full px-4 py-3 border rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm resize-none ${errors.message ? 'border-red-500' : 'border-neutral-200'}`}
                  placeholder="Please provide details..."
                />
                {errors.message && <p className="text-xs text-red-600 mt-1">{errors.message}</p>}
              </div>
              <div className="flex gap-3 pt-2">
                <LuxeButton variant="outline" onClick={closeModal} className="flex-1" type="button">Cancel</LuxeButton>
                <LuxeButton className="flex-1" type="submit">Send Message</LuxeButton>
              </div>
            </>
          )}
        </form>
      </LuxeModal>

      <LuxeModal
        isOpen={activeModal === 'chat'}
        onClose={closeModal}
        title="Live Chat"
      >
        <div className="text-center py-8 space-y-4">
          <div className="w-16 h-16 rounded-full bg-neutral-50 flex items-center justify-center mx-auto">
            <MessageSquare className="w-8 h-8 text-neutral-400" />
          </div>
          <h3 className="font-display text-xl font-medium text-neutral-900">Coming Soon</h3>
          <p className="text-neutral-600">
            Live chat support is currently under development. Please use email support for now.
          </p>
          <LuxeButton onClick={closeModal} className="w-full">Close</LuxeButton>
        </div>
      </LuxeModal>

      <LuxeModal
        isOpen={activeModal === 'docs'}
        onClose={closeModal}
        title="Documentation"
      >
        <div className="space-y-6">
          <div className="space-y-3">
            <h3 className="font-medium text-neutral-900">Available Resources</h3>
            <div className="space-y-2">
              {['Getting Started Guide', 'API Reference', 'Best Practices'].map((item) => (
                <button key={item} onClick={closeModal} className="w-full flex items-center justify-between p-4 border border-neutral-200 rounded-xl hover:border-neutral-900 transition-colors group bg-white">
                  <span className="text-sm font-medium text-neutral-900">{item}</span>
                  <ExternalLink className="w-4 h-4 text-neutral-400 group-hover:text-neutral-900 transition-colors" />
                </button>
              ))}
            </div>
          </div>
          <LuxeButton onClick={closeModal} className="w-full">Close</LuxeButton>
        </div>
      </LuxeModal>

      <LuxeModal
        isOpen={activeModal === 'feature'}
        onClose={closeModal}
        title="Feature Request"
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          {submitSuccess ? (
            <div className="text-center py-8 space-y-4">
              <div className="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto">
                <Check className="w-8 h-8 text-emerald-600" />
              </div>
              <h3 className="font-display text-2xl font-medium text-neutral-900">Request Submitted!</h3>
              <p className="text-neutral-600">
                Thank you for your suggestion. We'll review it and consider it for future updates.
              </p>
            </div>
          ) : (
            <>
              <LuxeInput
                label="Your Name"
                placeholder="Your name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                error={errors.name}
              />
              <LuxeInput
                label="Email"
                placeholder="your@email.com"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                error={errors.email}
              />
              <LuxeInput
                label="Feature Title"
                placeholder="Brief title for your feature idea"
                value={formData.subject}
                onChange={(e) => handleChange('subject', e.target.value)}
                error={errors.subject}
              />
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-neutral-500 mb-2">Description</label>
                <textarea
                  rows={6}
                  value={formData.message}
                  onChange={(e) => handleChange('message', e.target.value)}
                  className={`w-full px-4 py-3 border rounded-xl bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all text-sm resize-none ${errors.message ? 'border-red-500' : 'border-neutral-200'}`}
                  placeholder="Describe your feature idea in detail..."
                />
                {errors.message && <p className="text-xs text-red-600 mt-1">{errors.message}</p>}
              </div>
              <div className="flex gap-3 pt-2">
                <LuxeButton variant="outline" onClick={closeModal} className="flex-1" type="button">Cancel</LuxeButton>
                <LuxeButton className="flex-1" type="submit">Submit Request</LuxeButton>
              </div>
            </>
          )}
        </form>
      </LuxeModal>
    </motion.div>
  )
}
