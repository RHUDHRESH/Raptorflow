import { Link } from 'react-router-dom'
import { Mail, Github, Twitter, Linkedin, Send } from 'lucide-react'
import { useState } from 'react'
import { sanitizeInput } from '../utils/sanitize'
import { validateEmail } from '../utils/validation'

export default function Footer() {
  const [email, setEmail] = useState('')
  const [subscribed, setSubscribed] = useState(false)
  const [error, setError] = useState('')

  const handleNewsletterSubmit = (e) => {
    e.preventDefault()
    const emailValidation = validateEmail(email)
    
    if (!emailValidation.isValid) {
      setError(emailValidation.error)
      return
    }

    console.log('Newsletter subscription:', sanitizeInput(email))
    setSubscribed(true)
    setEmail('')
    setError('')
    
    setTimeout(() => {
      setSubscribed(false)
    }, 3000)
  }

  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-white border-t border-black/10 mt-auto">
      <div className="max-w-[1440px] mx-auto px-6 md:px-12 py-16">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-12 lg:gap-8 mb-12">
          {/* Brand & Newsletter */}
          <div className="lg:col-span-4 space-y-6">
            <div>
              <h3 className="text-subhead mb-3">Raptorflow</h3>
              <p className="text-caption max-w-sm">
                Strategy Execution Platform. Transform vision into reality with precision and clarity.
              </p>
            </div>
            
            {/* Newsletter */}
            <div>
              <label className="text-micro block mb-3">
                Newsletter
              </label>
              <form onSubmit={handleNewsletterSubmit} className="space-y-3">
                <div className="flex gap-2">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value)
                      setError('')
                    }}
                    placeholder="your@email.com"
                    disabled={subscribed}
                    className={`input flex-1 ${error ? 'input-error' : ''} ${subscribed ? 'bg-gray-50' : ''}`}
                  />
                  <button
                    type="submit"
                    disabled={subscribed}
                    className="btn-primary px-4"
                  >
                    <Send className="w-4 h-4" strokeWidth={1.5} />
                  </button>
                </div>
                {error && <p className="error-text">{error}</p>}
                {subscribed && <p className="text-caption text-black">Subscribed successfully!</p>}
              </form>
            </div>
          </div>

          {/* Products */}
          <div className="lg:col-span-2">
            <h4 className="text-micro mb-4">
              Products
            </h4>
            <ul className="space-y-3">
              <li><Link to="/moves" className="text-caption hover:text-black transition-colors duration-180">Moves</Link></li>
              <li><Link to="/cohorts" className="text-caption hover:text-black transition-colors duration-180">Cohorts</Link></li>
              <li><Link to="/strategy" className="text-caption hover:text-black transition-colors duration-180">Strategy</Link></li>
              <li><Link to="/analytics" className="text-caption hover:text-black transition-colors duration-180">Analytics</Link></li>
              <li><Link to="/tech-tree" className="text-caption hover:text-black transition-colors duration-180">Tech Tree</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div className="lg:col-span-2">
            <h4 className="text-micro mb-4">
              Company
            </h4>
            <ul className="space-y-3">
              <li><Link to="/about" className="text-caption hover:text-black transition-colors duration-180">About Us</Link></li>
              <li><Link to="/support" className="text-caption hover:text-black transition-colors duration-180">Support</Link></li>
              <li><Link to="/history" className="text-caption hover:text-black transition-colors duration-180">History</Link></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Careers</span></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Blog</span></li>
            </ul>
          </div>

          {/* Resources */}
          <div className="lg:col-span-2">
            <h4 className="text-micro mb-4">
              Resources
            </h4>
            <ul className="space-y-3">
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Documentation</span></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">API Reference</span></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Community</span></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Tutorials</span></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">FAQ</span></li>
            </ul>
          </div>

          {/* Legal */}
          <div className="lg:col-span-2">
            <h4 className="text-micro mb-4">
              Legal
            </h4>
            <ul className="space-y-3">
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Privacy Policy</span></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Terms of Service</span></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Cookie Policy</span></li>
              <li><Link to="/settings" className="text-caption hover:text-black transition-colors duration-180">Settings</Link></li>
              <li><span className="text-caption text-gray-400 cursor-not-allowed">Licenses</span></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-black/10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            {/* Copyright & Version */}
            <div className="flex flex-col md:flex-row items-center gap-3 md:gap-6">
              <p className="text-caption">
                © {currentYear} Raptorflow. All rights reserved.
              </p>
              <span className="hidden md:block h-4 w-px bg-black/10" />
              <p className="text-micro text-gray-400">
                v1.0.0
              </p>
            </div>

            {/* Social Links */}
            <div className="flex items-center gap-4">
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-full border border-black/10 flex items-center justify-center text-gray-400 hover:text-black hover:border-black/20 transition-all duration-180"
                aria-label="Twitter"
              >
                <Twitter className="w-4 h-4" strokeWidth={1.5} />
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-full border border-black/10 flex items-center justify-center text-gray-400 hover:text-black hover:border-black/20 transition-all duration-180"
                aria-label="GitHub"
              >
                <Github className="w-4 h-4" strokeWidth={1.5} />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-full border border-black/10 flex items-center justify-center text-gray-400 hover:text-black hover:border-black/20 transition-all duration-180"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-4 h-4" strokeWidth={1.5} />
              </a>
              <a
                href="mailto:support@raptorflow.com"
                className="w-9 h-9 rounded-full border border-black/10 flex items-center justify-center text-gray-400 hover:text-black hover:border-black/20 transition-all duration-180"
                aria-label="Email"
              >
                <Mail className="w-4 h-4" strokeWidth={1.5} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
