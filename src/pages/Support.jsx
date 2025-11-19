import { motion } from 'framer-motion'
import { HelpCircle, Mail, MessageSquare, FileText, Book, Send } from 'lucide-react'

export default function Support() {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 p-12 text-white"
      >
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-xl flex items-center justify-center">
              <HelpCircle className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-4xl font-display font-bold mb-2">Support & Feedback</h1>
              <p className="text-primary-100 text-lg">
                We're here to help. Share your feedback and get support.
              </p>
            </div>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-accent-500/20 rounded-full blur-3xl" />
      </motion.div>

      {/* Support Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          {
            title: 'Contact Support',
            description: 'Get help from our support team',
            icon: Mail,
            action: 'Send Email',
          },
          {
            title: 'Live Chat',
            description: 'Chat with us in real-time',
            icon: MessageSquare,
            action: 'Start Chat',
          },
          {
            title: 'Documentation',
            description: 'Browse our help articles',
            icon: Book,
            action: 'View Docs',
          },
          {
            title: 'Feature Request',
            description: 'Suggest new features',
            icon: FileText,
            action: 'Submit Request',
          },
        ].map((option, index) => {
          const Icon = option.icon
          return (
            <motion.div
              key={option.title}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-6 hover:shadow-xl transition-all cursor-pointer group"
            >
              <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary-600 flex items-center justify-center mb-4 group-hover:bg-primary-600 group-hover:text-white transition-colors">
                <Icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-neutral-900 mb-2">{option.title}</h3>
              <p className="text-neutral-600 mb-4">{option.description}</p>
              <button className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium">
                {option.action}
                <Send className="w-4 h-4" />
              </button>
            </motion.div>
          )
        })}
      </div>

      {/* Feedback Form */}
      <div className="glass rounded-2xl p-8">
        <h2 className="text-2xl font-display font-bold mb-6">Send Feedback</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Subject
            </label>
            <input
              type="text"
              placeholder="What's this about?"
              className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Message
            </label>
            <textarea
              rows={6}
              placeholder="Tell us what you think..."
              className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
            />
          </div>
          <div className="flex justify-end">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors"
            >
              <Send className="w-5 h-5" />
              Send Feedback
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  )
}

