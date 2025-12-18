import React from 'react'
import { Link } from 'react-router-dom'

const MinimalFooter = () => {
  return (
    <footer className="bg-background border-t border-white/5 py-20">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 md:gap-24">
          <div className="md:col-span-2">
            <Link to="/" className="text-2xl font-bold tracking-tighter flex items-center gap-2 mb-6">
              <div className="w-8 h-8 bg-foreground rounded-full flex items-center justify-center">
                <span className="text-background font-serif italic font-bold">R</span>
              </div>
              <span>Raptorflow</span>
            </Link>
            <p className="text-zinc-500 max-w-sm font-light">
              Refining the chaos of growth into the elegance of strategy.
            </p>
          </div>

          <div>
            <h4 className="text-white uppercase tracking-widest text-xs mb-6 font-medium">Platform</h4>
            <ul className="space-y-4 text-zinc-500 font-light">
              <li><Link to="/features" className="hover:text-accent transition-colors">Features</Link></li>
              <li><Link to="/pricing" className="hover:text-accent transition-colors">Pricing</Link></li>
              <li><Link to="/login" className="hover:text-accent transition-colors">Login</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white uppercase tracking-widest text-xs mb-6 font-medium">Company</h4>
            <ul className="space-y-4 text-zinc-500 font-light">
              <li><Link to="/about" className="hover:text-accent transition-colors">About</Link></li>
              <li><Link to="/manifesto" className="hover:text-accent transition-colors">Manifesto</Link></li>
              <li><Link to="/contact" className="hover:text-accent transition-colors">Contact</Link></li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center mt-20 pt-8 border-t border-white/5 text-xs text-zinc-600 uppercase tracking-widest">
          <div>© 2025 Raptorflow Inc.</div>
          <div className="flex gap-8 mt-4 md:mt-0">
            <Link to="/privacy" className="hover:text-zinc-400">Privacy</Link>
            <Link to="/terms" className="hover:text-zinc-400">Terms</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default MinimalFooter

