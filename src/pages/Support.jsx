import { motion, AnimatePresence } from 'framer-motion'
import { Mail, MessageSquare, Book, FileText, Send, ArrowRight, X, Check, ExternalLink } from 'lucide-react'
import { useState } from 'react'
import { sanitizeInput } from '../utils/sanitize'
import { validateEmail, validateRequired } from '../utils/validation'

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
      // For now, just show success message
      setSubmitSuccess(true)
      setTimeout(() => {
        closeModal()
      }, 2000)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative"
      >
        <div className="space-y-3 pb-4">
          <div className="flex items-center gap-3">
            <span className="micro-label tracking-[0.5em]">Support</span>
            <span className="h-px w-16 bg-neutral-200" />
          </div>
          <div className="space-y-2">
            <h1 className="font-serif text-4xl md:text-5xl text-black leading-[1.1] tracking-tight antialiased">
              Support & Feedback
            </h1>
            <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
              We're here to help. Get assistance with your account, features, or submit feedback.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Support Channels */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            title: 'Email Support',
            description: 'Send us a message and we will respond within 24 hours',
            icon: Mail,
            action: 'Send Email',
            delay: 0.1,
            modalKey: 'email',
          },
          {
            title: 'Live Chat',
            description: 'Chat with our support team in real-time',
            icon: MessageSquare,
            action: 'Start Chat',
            delay: 0.15,
            modalKey: 'chat',
          },
          {
            title: 'Documentation',
            description: 'Browse guides, tutorials, and best practices',
            icon: Book,
            action: 'View Docs',
            delay: 0.2,
            modalKey: 'docs',
          },
          {
            title: 'Feature Request',
            description: 'Suggest new features or improvements',
            icon: FileText,
            action: 'Submit Request',
            delay: 0.25,
            modalKey: 'feature',
          },
        ].map((option) => {
          const Icon = option.icon
          return (
            <motion.div
              key={option.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: option.delay, duration: 0.3 }}
              onClick={() => openModal(option.modalKey)}
              className="group relative border-2 border-neutral-200 bg-white p-5 hover:border-neutral-900 transition-all duration-300 cursor-pointer"
            >
              <div className="space-y-4">
                <div className="w-12 h-12 rounded-full border-2 border-neutral-200 flex items-center justify-center group-hover:border-neutral-900 group-hover:bg-neutral-900 transition-all duration-300">
                  <Icon className="w-5 h-5 text-neutral-900 group-hover:text-white transition-colors duration-300" />
                </div>
                
                <div className="space-y-2">
                  <h3 className="font-serif text-xl text-neutral-900 leading-tight">
                    {option.title}
                  </h3>
                  <p className="font-sans text-xs text-neutral-600 leading-relaxed">
                    {option.description}
                  </p>
                </div>

                <button className="group/btn inline-flex items-center gap-2 border border-neutral-900 px-4 py-2 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-900 hover:bg-neutral-900 hover:text-white transition-all duration-200">
                  <span>{option.action}</span>
                  <ArrowRight className="w-3 h-3 group-hover/btn:translate-x-1 transition-transform" />
                </button>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Contact Form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.3 }}
        className="border-2 border-neutral-200 bg-white p-6 md:p-8"
      >
        <div className="space-y-8">
          {/* Header */}
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <span className="micro-label tracking-[0.5em]">Contact Us</span>
              <span className="h-px w-16 bg-neutral-200" />
            </div>
            <h2 className="font-serif text-2xl md:text-3xl text-black leading-[1.1] tracking-tight">
              Send us a Message
            </h2>
          </div>

          {/* Form */}
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">
                Subject
              </label>
              <input
                type="text"
                placeholder="What can we help you with?"
                className="w-full px-0 py-3 border-b-2 border-neutral-200 bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-lg placeholder:text-neutral-400 placeholder:font-sans placeholder:text-sm"
              />
            </div>
            
            <div className="space-y-2">
              <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">
                Message
              </label>
              <textarea
                rows={5}
                placeholder="Please provide details about your question or issue..."
                className="w-full px-0 py-3 border-b-2 border-neutral-200 bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-sans text-sm leading-relaxed resize-none placeholder:text-neutral-400"
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-6 border-t border-neutral-200">
            <p className="font-sans text-xs text-neutral-500">
              We typically respond within 24 hours
            </p>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => openModal('contact')}
              className="group inline-flex items-center gap-2 border-2 border-neutral-900 bg-black text-white px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-all duration-200"
            >
              <span>Send Message</span>
              <Send className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Modals */}
      <AnimatePresence>
        {/* Email Support Modal */}
        {activeModal === 'email' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-2 border-black rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5" />
                  <h2 className="font-serif text-2xl text-neutral-900">Email Support</h2>
                </div>
                <button onClick={closeModal} className="text-neutral-400 hover:text-neutral-900 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-6">
                {submitSuccess ? (
                  <div className="flex flex-col items-center justify-center py-12 space-y-4">
                    <div className="w-16 h-16 rounded-full bg-green-50 border-2 border-green-500 flex items-center justify-center">
                      <Check className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="font-serif text-2xl text-neutral-900">Message Sent!</h3>
                    <p className="font-sans text-sm text-neutral-600 text-center max-w-md">
                      We've received your message and will respond within 24 hours.
                    </p>
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Name</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => handleChange('name', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.name ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="Your name"
                      />
                      {errors.name && <p className="text-xs text-red-600 mt-1">{errors.name}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Email</label>
                      <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleChange('email', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.email ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="your@email.com"
                      />
                      {errors.email && <p className="text-xs text-red-600 mt-1">{errors.email}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Subject</label>
                      <input
                        type="text"
                        value={formData.subject}
                        onChange={(e) => handleChange('subject', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.subject ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="What can we help you with?"
                      />
                      {errors.subject && <p className="text-xs text-red-600 mt-1">{errors.subject}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Message</label>
                      <textarea
                        rows={5}
                        value={formData.message}
                        onChange={(e) => handleChange('message', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.message ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-sans text-sm resize-none`}
                        placeholder="Please provide details..."
                      />
                      {errors.message && <p className="text-xs text-red-600 mt-1">{errors.message}</p>}
                    </div>
                    <div className="flex gap-3 pt-4">
                      <button
                        type="button"
                        onClick={closeModal}
                        className="flex-1 border-2 border-neutral-200 text-neutral-600 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="flex-1 bg-black text-white px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-colors"
                      >
                        Send Message
                      </button>
                    </div>
                  </>
                )}
              </form>
            </motion.div>
          </motion.div>
        )}

        {/* Live Chat Modal */}
        {activeModal === 'chat' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-2 border-black rounded-lg shadow-xl max-w-md w-full"
            >
              <div className="border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <MessageSquare className="w-5 h-5" />
                  <h2 className="font-serif text-2xl text-neutral-900">Live Chat</h2>
                </div>
                <button onClick={closeModal} className="text-neutral-400 hover:text-neutral-900 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-8 text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-neutral-100 border-2 border-neutral-200 flex items-center justify-center mx-auto">
                  <MessageSquare className="w-8 h-8 text-neutral-400" />
                </div>
                <h3 className="font-serif text-xl text-neutral-900">Coming Soon</h3>
                <p className="font-sans text-sm text-neutral-600">
                  Live chat support is currently under development. Please use email support for now.
                </p>
                <button
                  onClick={closeModal}
                  className="border-2 border-black text-black px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-black hover:text-white transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Documentation Modal */}
        {activeModal === 'docs' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-2 border-black rounded-lg shadow-xl max-w-md w-full"
            >
              <div className="border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Book className="w-5 h-5" />
                  <h2 className="font-serif text-2xl text-neutral-900">Documentation</h2>
                </div>
                <button onClick={closeModal} className="text-neutral-400 hover:text-neutral-900 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-8 space-y-6">
                  <div className="space-y-3">
                  <h3 className="font-serif text-lg text-neutral-900">Available Resources</h3>
                  <div className="space-y-2">
                    <button onClick={closeModal} className="w-full flex items-center justify-between p-3 border border-neutral-200 rounded-lg hover:border-neutral-900 transition-colors group">
                      <span className="font-sans text-sm text-neutral-900">Getting Started Guide</span>
                      <ExternalLink className="w-4 h-4 text-neutral-400 group-hover:text-neutral-900 transition-colors" />
                    </button>
                    <button onClick={closeModal} className="w-full flex items-center justify-between p-3 border border-neutral-200 rounded-lg hover:border-neutral-900 transition-colors group">
                      <span className="font-sans text-sm text-neutral-900">API Reference</span>
                      <ExternalLink className="w-4 h-4 text-neutral-400 group-hover:text-neutral-900 transition-colors" />
                    </button>
                    <button onClick={closeModal} className="w-full flex items-center justify-between p-3 border border-neutral-200 rounded-lg hover:border-neutral-900 transition-colors group">
                      <span className="font-sans text-sm text-neutral-900">Best Practices</span>
                      <ExternalLink className="w-4 h-4 text-neutral-400 group-hover:text-neutral-900 transition-colors" />
                    </button>
                  </div>
                </div>
                <button
                  onClick={closeModal}
                  className="w-full border-2 border-black text-black px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-black hover:text-white transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}

        {/* Feature Request Modal */}
        {activeModal === 'feature' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-2 border-black rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5" />
                  <h2 className="font-serif text-2xl text-neutral-900">Feature Request</h2>
                </div>
                <button onClick={closeModal} className="text-neutral-400 hover:text-neutral-900 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-6">
                {submitSuccess ? (
                  <div className="flex flex-col items-center justify-center py-12 space-y-4">
                    <div className="w-16 h-16 rounded-full bg-green-50 border-2 border-green-500 flex items-center justify-center">
                      <Check className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="font-serif text-2xl text-neutral-900">Request Submitted!</h3>
                    <p className="font-sans text-sm text-neutral-600 text-center max-w-md">
                      Thank you for your suggestion. We'll review it and consider it for future updates.
                    </p>
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Your Name</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => handleChange('name', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.name ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="Your name"
                      />
                      {errors.name && <p className="text-xs text-red-600 mt-1">{errors.name}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Email</label>
                      <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleChange('email', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.email ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="your@email.com"
                      />
                      {errors.email && <p className="text-xs text-red-600 mt-1">{errors.email}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Feature Title</label>
                      <input
                        type="text"
                        value={formData.subject}
                        onChange={(e) => handleChange('subject', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.subject ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="Brief title for your feature idea"
                      />
                      {errors.subject && <p className="text-xs text-red-600 mt-1">{errors.subject}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Description</label>
                      <textarea
                        rows={6}
                        value={formData.message}
                        onChange={(e) => handleChange('message', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.message ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-sans text-sm resize-none`}
                        placeholder="Describe your feature idea in detail..."
                      />
                      {errors.message && <p className="text-xs text-red-600 mt-1">{errors.message}</p>}
                    </div>
                    <div className="flex gap-3 pt-4">
                      <button
                        type="button"
                        onClick={closeModal}
                        className="flex-1 border-2 border-neutral-200 text-neutral-600 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="flex-1 bg-black text-white px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-colors"
                      >
                        Submit Request
                      </button>
                    </div>
                  </>
                )}
              </form>
            </motion.div>
          </motion.div>
        )}

        {/* Contact Modal (from bottom form) */}
        {activeModal === 'contact' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-2 border-black rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="sticky top-0 bg-white border-b border-neutral-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Send className="w-5 h-5" />
                  <h2 className="font-serif text-2xl text-neutral-900">Contact Us</h2>
                </div>
                <button onClick={closeModal} className="text-neutral-400 hover:text-neutral-900 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-6">
                {submitSuccess ? (
                  <div className="flex flex-col items-center justify-center py-12 space-y-4">
                    <div className="w-16 h-16 rounded-full bg-green-50 border-2 border-green-500 flex items-center justify-center">
                      <Check className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="font-serif text-2xl text-neutral-900">Message Sent!</h3>
                    <p className="font-sans text-sm text-neutral-600 text-center max-w-md">
                      We've received your message and will respond within 24 hours.
                    </p>
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Name</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => handleChange('name', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.name ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="Your name"
                      />
                      {errors.name && <p className="text-xs text-red-600 mt-1">{errors.name}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Email</label>
                      <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleChange('email', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.email ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="your@email.com"
                      />
                      {errors.email && <p className="text-xs text-red-600 mt-1">{errors.email}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Subject</label>
                      <input
                        type="text"
                        value={formData.subject}
                        onChange={(e) => handleChange('subject', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.subject ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-serif text-base`}
                        placeholder="What can we help you with?"
                      />
                      {errors.subject && <p className="text-xs text-red-600 mt-1">{errors.subject}</p>}
                    </div>
                    <div>
                      <label className="block font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400 mb-3">Message</label>
                      <textarea
                        rows={5}
                        value={formData.message}
                        onChange={(e) => handleChange('message', e.target.value)}
                        className={`w-full px-4 py-3 border-2 ${errors.message ? 'border-red-500' : 'border-neutral-200'} rounded-lg bg-transparent focus:outline-none focus:border-neutral-900 transition-all font-sans text-sm resize-none`}
                        placeholder="Please provide details..."
                      />
                      {errors.message && <p className="text-xs text-red-600 mt-1">{errors.message}</p>}
                    </div>
                    <div className="flex gap-3 pt-4">
                      <button
                        type="button"
                        onClick={closeModal}
                        className="flex-1 border-2 border-neutral-200 text-neutral-600 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-50 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="flex-1 bg-black text-white px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-colors"
                      >
                        Send Message
                      </button>
                    </div>
                  </>
                )}
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
