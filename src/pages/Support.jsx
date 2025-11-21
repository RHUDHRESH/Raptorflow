import { motion } from 'framer-motion'
import { Mail, MessageSquare, Book, FileText, Send, ArrowRight } from 'lucide-react'

export default function Support() {
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
          },
          {
            title: 'Live Chat',
            description: 'Chat with our support team in real-time',
            icon: MessageSquare,
            action: 'Start Chat',
            delay: 0.15,
          },
          {
            title: 'Documentation',
            description: 'Browse guides, tutorials, and best practices',
            icon: Book,
            action: 'View Docs',
            delay: 0.2,
          },
          {
            title: 'Feature Request',
            description: 'Suggest new features or improvements',
            icon: FileText,
            action: 'Submit Request',
            delay: 0.25,
          },
        ].map((option, index) => {
          const Icon = option.icon
          return (
            <motion.div
              key={option.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: option.delay, duration: 0.3 }}
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
              className="group inline-flex items-center gap-2 border-2 border-neutral-900 bg-black text-white px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] hover:bg-neutral-800 transition-all duration-200"
            >
              <span>Send Message</span>
              <Send className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
            </motion.button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
