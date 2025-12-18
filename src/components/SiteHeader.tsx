import * as React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Menu, Zap } from 'lucide-react'
import { motion, useReducedMotion } from 'framer-motion'
import { RaptorFlowLogo } from '@/components/brand/Logo'

const navItems = [
  { label: '3-Move Stack', to: '/#method' },
  { label: 'Proof', to: '/#proof' },
  { label: 'Plan', to: '/#plan' },
  { label: 'Pricing', to: '/#pricing' },
  { label: 'FAQ', to: '/#faq' },
]

export function SiteHeader() {
  const reduceMotion = useReducedMotion()
  const [scrolled, setScrolled] = React.useState(false)
  const [activeHash, setActiveHash] = React.useState<string>('')

  React.useEffect(() => {
    const update = () => {
      setScrolled(window.scrollY > 8)
      setActiveHash(window.location.hash)
    }
    update()
    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('hashchange', update)
    return () => {
      window.removeEventListener('scroll', update)
      window.removeEventListener('hashchange', update)
    }
  }, [])

  return (
    <header className="sticky top-0 z-50">
      <div
        className={
          "w-full border-b border-transparent transition-all duration-300 " +
          (scrolled ? "bg-black/80 backdrop-blur-xl border-white/5 shadow-[0_4px_30px_rgba(0,0,0,0.5)]" : "bg-transparent")
        }
      >
        <div className="container mx-auto px-6 max-w-7xl">
          <div className="flex h-20 items-center justify-between">
            {/* Logo Area */}
            <motion.div
              initial={false}
              whileHover={{ scale: 1.02 }}
              className="flex items-center gap-2"
            >
              <Link to="/" className="flex items-center gap-2 group">
                <RaptorFlowLogo size="md" animated={true} />
                <span className="text-lg font-bold tracking-widest text-white group-hover:text-primary transition-colors duration-300">
                  RAPTORFLOW
                </span>
              </Link>
            </motion.div>

            {/* Desktop Nav - HUD Style */}
            <nav className="relative hidden items-center gap-1 md:flex p-1 rounded-full border border-white/5 bg-white/5 backdrop-blur-md">
              {navItems.map((item) => {
                const hash = item.to.includes('#') ? item.to.slice(item.to.indexOf('#')) : ''
                const isActive = hash && activeHash === hash
                return (
                  <div key={item.to} className="relative">
                    <Link
                      to={item.to}
                      className={
                        "relative z-10 block px-5 py-2 text-sm font-medium transition-all duration-300 " +
                        (isActive
                          ? "text-black"
                          : "text-muted-foreground hover:text-white")
                      }
                    >
                      {item.label}
                    </Link>
                    {isActive ? (
                      <motion.div
                        layoutId="rf-nav-active"
                        className="absolute inset-0 rounded-full bg-primary shadow-[0_0_20px_rgba(0,240,255,0.4)]"
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                      />
                    ) : null}
                  </div>
                )
              })}
            </nav>

            {/* Actions */}
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="hidden items-center justify-center text-sm font-bold text-muted-foreground hover:text-white transition-colors tracking-wide sm:inline-flex"
              >
                LOGIN
              </Link>

              <Link
                to="/#pricing"
                className="hidden group relative items-center justify-center overflow-hidden rounded-full bg-white text-black px-6 py-2.5 text-sm font-bold transition-transform hover:scale-105 sm:inline-flex"
              >
                <span className="relative z-10 flex items-center gap-2">
                  START NOW <Zap className="w-4 h-4 fill-black" />
                </span>
                <div className="absolute inset-0 z-0 bg-primary opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </Link>

              {/* Mobile Menu Toggle */}
              <div className="md:hidden">
                <details className="relative group/mobile">
                  <summary className="list-none inline-flex h-10 w-10 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-white transition-colors hover:bg-white/10">
                    <Menu className="h-5 w-5" />
                    <span className="sr-only">Open menu</span>
                  </summary>

                  <div className="absolute right-0 mt-4 w-[min(360px,92vw)] overflow-hidden rounded-2xl border border-white/10 bg-[#0A0A0F]/95 backdrop-blur-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] ring-1 ring-white/5 z-50">
                    <div className="px-6 py-6 space-y-6">
                      <div className="space-y-1">
                        {navItems.map((item) => (
                          <Link
                            key={item.to}
                            to={item.to}
                            className="flex items-center justify-between rounded-lg px-4 py-3 text-base font-medium text-white/80 transition-colors hover:bg-white/5 hover:text-primary hover:shadow-glow-sm"
                          >
                            <span>{item.label}</span>
                            <ArrowRight className="h-4 w-4 opacity-50" />
                          </Link>
                        ))}
                      </div>

                      <div className="h-px bg-white/10" />

                      <div className="grid gap-3">
                        <Link
                          to="/#pricing"
                          className="flex items-center justify-center gap-2 w-full rounded-lg bg-primary py-3 text-sm font-bold text-black hover:bg-primary/90 transition-colors"
                        >
                          <Zap className="w-4 h-4 fill-black" /> VIEW PLANS
                        </Link>
                        <Link
                          to="/login"
                          className="flex items-center justify-center w-full rounded-lg border border-white/10 bg-transparent py-3 text-sm font-bold text-white hover:bg-white/5 transition-colors"
                        >
                          SIGN IN
                        </Link>
                      </div>
                    </div>
                  </div>
                </details>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
