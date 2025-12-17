import * as React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Menu } from 'lucide-react'
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
    <header className="sticky top-0 z-40">
      <div
        className={
          "border-b border-border/60 bg-background/85 backdrop-blur-xl transition-shadow " +
          (scrolled ? "shadow-[0_10px_30px_rgba(0,0,0,0.06)]" : "shadow-none")
        }
      >
        <div className="container-editorial">
          <div className="flex h-16 items-center justify-between">
            <motion.div
              initial={false}
              whileHover={
                reduceMotion
                  ? undefined
                  : {
                    y: -1,
                    transition: { duration: 0.25, ease: [0.16, 1, 0.3, 1] },
                  }
              }
            >
              <RaptorFlowLogo size="md" animated={!reduceMotion} />
            </motion.div>

            <nav className="relative hidden items-center gap-1 md:flex">
              {navItems.map((item) => {
                const hash = item.to.includes('#') ? item.to.slice(item.to.indexOf('#')) : ''
                const isActive = hash && activeHash === hash
                return (
                  <div key={item.to} className="relative px-2">
                    <Link
                      to={item.to}
                      className={
                        "group relative block rounded-full px-3 py-2 text-body-sm transition-editorial " +
                        (isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground")
                      }
                    >
                      <span className="relative z-10">{item.label}</span>
                      <span className="pointer-events-none absolute inset-x-3 -bottom-0.5 h-px origin-left scale-x-0 bg-gradient-to-r from-primary/60 via-primary/20 to-transparent transition-transform duration-300 group-hover:scale-x-100" />
                    </Link>
                    {isActive && !reduceMotion ? (
                      <motion.div
                        layoutId="rf-nav-active"
                        className="absolute inset-0 rounded-full border border-border/70 bg-muted/30"
                        transition={{ type: 'spring', stiffness: 500, damping: 36 }}
                      />
                    ) : isActive ? (
                      <div className="absolute inset-0 rounded-full border border-border/70 bg-muted/30" />
                    ) : null}
                  </div>
                )
              })}
            </nav>

            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="hidden items-center justify-center rounded-md border border-border bg-transparent px-4 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted sm:inline-flex"
              >
                Sign in
              </Link>

              <Link
                to="/#pricing"
                className="hidden items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90 sm:inline-flex"
              >
                View plans
              </Link>

              <div className="md:hidden">
                <details className="relative">
                  <summary className="list-none inline-flex h-10 w-10 items-center justify-center rounded-md border border-border bg-transparent text-muted-foreground transition-editorial hover:bg-muted hover:text-foreground">
                    <Menu className="h-5 w-5" />
                    <span className="sr-only">Open menu</span>
                  </summary>

                  <div className="absolute right-0 mt-3 w-[min(360px,92vw)] overflow-hidden rounded-2xl border border-border bg-background shadow-[0_18px_40px_rgba(0,0,0,0.10)]">
                    <div className="border-b border-border px-5 py-4">
                      <div className="flex items-center justify-between">
                        <div className="text-editorial-caption">Menu</div>
                        <Link to="/#pricing" className="pill-editorial pill-neutral">
                          Plans
                        </Link>
                      </div>
                    </div>

                    <div className="px-5 py-4">
                      <div className="space-y-1">
                        {navItems.map((item) => (
                          <Link
                            key={item.to}
                            to={item.to}
                            className="group flex items-center justify-between rounded-md px-3 py-3 text-body-md text-foreground transition-editorial hover:bg-muted/50"
                          >
                            <span>{item.label}</span>
                            <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                          </Link>
                        ))}
                      </div>

                      <div className="mt-6">
                        <div className="text-editorial-caption">Support</div>
                        <div className="mt-2 grid gap-1">
                          {[
                            { to: '/contact', label: 'Contact' },
                            { to: '/privacy', label: 'Privacy' },
                            { to: '/terms', label: 'Terms' },
                            { to: '/refunds', label: 'Refunds' },
                          ].map((item) => (
                            <Link
                              key={item.to}
                              to={item.to}
                              className="block rounded-md px-3 py-2 text-body-sm text-muted-foreground transition-editorial hover:bg-muted/50 hover:text-foreground"
                            >
                              {item.label}
                            </Link>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-border px-5 py-4">
                      <div className="grid gap-2">
                        <Link
                          to="/#pricing"
                          className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
                        >
                          View plans
                        </Link>
                        <Link
                          to="/login"
                          className="inline-flex w-full items-center justify-center rounded-md border border-border bg-transparent px-4 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
                        >
                          Sign in
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
