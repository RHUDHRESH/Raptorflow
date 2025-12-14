import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, ArrowRight } from 'lucide-react'

/* ═══════════════════════════════════════════════════════════════════════════
   HEADER - HIGH FASHION EDITORIAL DESIGN
   Navigation with minimal, sophisticated aesthetic
   ═══════════════════════════════════════════════════════════════════════════ */

const Header = () => {
  const navigate = useNavigate()
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { name: 'Features', path: '/#features' },
    { name: 'How It Works', path: '/#how-it-works' },
    { name: 'Pricing', path: '/#pricing' },
  ]

  return (
    <>
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled
          ? 'bg-background/95 backdrop-blur-xl border-b border-border/30'
          : 'bg-background/80 backdrop-blur-sm'
          }`}
      >
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <nav className="flex items-center justify-between h-20">

            {/* Logo */}
            <div
              onClick={() => navigate('/')}
              className="cursor-pointer group flex items-center gap-3"
            >
              <div className="w-9 h-9 bg-primary flex items-center justify-center group-hover:scale-105 transition-transform">
                <span className="text-background font-bold text-sm">Rf</span>
              </div>
              <span className="text-foreground text-xl tracking-tight font-light">
                Raptor<span className="text-primary font-normal">flow</span>
              </span>
            </div>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-12">
              {navItems.map((item) => (
                <button
                  key={item.name}
                  onClick={() => navigate(item.path)}
                  className="text-caption text-muted-foreground hover:text-foreground transition-colors"
                >
                  {item.name}
                </button>
              ))}
            </div>

            {/* CTA */}
            <div className="flex items-center gap-6">
              <button
                onClick={() => navigate('/login')}
                className="hidden md:block text-caption text-muted-foreground hover:text-foreground transition-colors"
              >
                Sign in
              </button>

              <button
                onClick={() => navigate('/start')}
                className="group hidden md:flex items-center gap-2 px-5 py-2.5 bg-foreground text-background text-caption hover:bg-primary transition-colors"
              >
                Get Started
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </button>

              {/* Mobile menu */}
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="md:hidden text-muted-foreground hover:text-foreground transition-colors"
              >
                {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </nav>
        </div>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-background md:hidden flex flex-col items-center justify-center"
          >
            {navItems.map((item, i) => (
              <motion.button
                key={item.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                onClick={() => {
                  navigate(item.path)
                  setMenuOpen(false)
                }}
                className="text-2xl font-light text-muted-foreground hover:text-foreground py-4 transition-colors"
              >
                {item.name}
              </motion.button>
            ))}

            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              onClick={() => {
                navigate('/start')
                setMenuOpen(false)
              }}
              className="mt-8 px-8 py-4 bg-foreground text-background text-caption"
            >
              Get Started
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

export default Header
