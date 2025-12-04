import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'

const Footer = () => {
  const navigate = useNavigate()

  return (
    <footer className="relative bg-black">
      
      {/* Large CTA Section */}
      <div className="relative py-32 md:py-40 border-t border-white/5 overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-b from-black via-zinc-950 to-black" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-amber-900/20 via-transparent to-transparent" />
        </div>

        <div className="max-w-4xl mx-auto px-6 relative z-10 text-center">
          <motion.span
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-[10px] uppercase tracking-[0.4em] text-amber-400/60"
          >
            Get Started
          </motion.span>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mt-6 text-4xl md:text-5xl lg:text-6xl font-light text-white leading-tight"
          >
            Stop planning.
            <br />
            <span className="italic font-normal text-amber-200">Start shipping.</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mt-8 text-white/40 font-light text-lg max-w-xl mx-auto"
          >
            Join 500+ founders who transformed chaos into clarity. 
            Your 90-day war map is waiting.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            className="mt-12"
          >
            <button
              onClick={() => navigate('/start')}
              className="group inline-flex items-center gap-3 px-10 py-5 bg-white text-black font-medium tracking-wide hover:bg-amber-100 transition-colors"
            >
              Get Started — ₹5,000
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            className="mt-6 text-white/30 text-sm"
          >
            7-day satisfaction guarantee. No questions asked.
          </motion.p>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            
            {/* Logo */}
            <div className="flex items-center gap-8">
              <span className="text-white text-lg tracking-tight font-light">
                Raptor<span className="italic font-normal text-amber-200">flow</span>
              </span>
              
              <span className="text-white/20 text-xs">
                © 2025 Raptorflow Inc.
              </span>
            </div>

            {/* Links */}
            <div className="flex items-center gap-8">
              {['Privacy', 'Terms', 'Contact'].map((link) => (
                <Link
                  key={link}
                  to="#"
                  className="text-white/30 text-xs hover:text-white/60 transition-colors"
                >
                  {link}
                </Link>
              ))}
            </div>

            {/* Social */}
            <div className="flex items-center gap-6">
              {['Twitter', 'LinkedIn'].map((social) => (
                <a
                  key={social}
                  href="#"
                  className="text-white/30 text-xs hover:text-white/60 transition-colors"
                >
                  {social}
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
