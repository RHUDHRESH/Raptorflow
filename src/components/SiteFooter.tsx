import * as React from 'react'
import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import { Github, Linkedin, Twitter } from 'lucide-react'

const GITHUB_URL = 'https://github.com/raptorflow'

export function SiteFooter() {
  const reduceMotion = useReducedMotion()

  return (
    <footer className="relative border-t border-border bg-background">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

      <div className="container-editorial">
        {/* CTA band */}
        <div className="py-12">
          <div className="rounded-card border border-border bg-card p-8">
            <div className="grid gap-6 lg:grid-cols-12 lg:items-center">
              <div className="lg:col-span-7">
                <div className="text-editorial-caption">Ready to ship daily?</div>
                <div className="mt-2 font-serif text-headline-sm">Build the 90-day map. Then run it.</div>
                <p className="mt-2 max-w-[70ch] text-body-sm text-muted-foreground">
                  A system for decisions, assets, and one metric that matters—without weekly resets.
                </p>
              </div>
              <div className="lg:col-span-5">
                <div className="flex flex-wrap items-stretch gap-2">
                  <motion.div
                    whileHover={reduceMotion ? undefined : { y: -1 }}
                    whileTap={reduceMotion ? undefined : { scale: 0.99 }}
                    className="flex-1 min-w-[160px]"
                  >
                    <Link
                      to="/signup"
                      className="inline-flex h-full w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                    >
                      Get started
                    </Link>
                  </motion.div>
                  <motion.div
                    whileHover={reduceMotion ? undefined : { y: -1 }}
                    whileTap={reduceMotion ? undefined : { scale: 0.99 }}
                    className="flex-1 min-w-[160px]"
                  >
                    <Link
                      to="/pricing"
                      className="inline-flex h-full w-full items-center justify-center rounded-md border border-border bg-transparent px-4 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-primary/40 focus-visible:ring-offset-background"
                    >
                      View pricing
                    </Link>
                  </motion.div>
                  <motion.a
                    href="mailto:hello@raptorflow.com"
                    className="inline-flex min-w-[160px] flex-1 items-center justify-center rounded-md border border-border bg-transparent px-4 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                    whileHover={reduceMotion ? undefined : { y: -1 }}
                    whileTap={reduceMotion ? undefined : { scale: 0.99 }}
                  >
                    Email us
                  </motion.a>
                </div>
                <div className="mt-3 text-[11px] text-muted-foreground">No spam. Just a reply.</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main footer */}
        <div className="grid gap-10 pb-12 md:grid-cols-12">
          <div className="md:col-span-5">
            <motion.div
              className="inline-flex items-center gap-3"
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
              <Link
                to="/"
                className="inline-flex items-center gap-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              >
                <motion.div
                  className="relative flex h-9 w-9 items-center justify-center rounded-card border border-border bg-card"
                  initial={false}
                  whileHover={
                    reduceMotion
                      ? undefined
                      : {
                        rotate: -3,
                        scale: 1.02,
                        transition: { type: 'spring', stiffness: 420, damping: 26 },
                      }
                  }
                >
                  <img src="/logo.svg" alt="RaptorFlow" className="h-5 w-5" />
                </motion.div>

                <div>
                  <div className="text-sm font-medium tracking-tight">
                    Raptor<span className="text-primary">Flow</span>
                  </div>
                  <div className="text-body-xs text-muted-foreground">Daily decisions that stack.</div>
                </div>
              </Link>
            </motion.div>

            <p className="mt-5 max-w-[52ch] text-body-sm text-muted-foreground">
              Editorial systems for founders who want compounding execution.
            </p>

            <div className="mt-6 flex items-center gap-2">
              <a
                href="https://twitter.com/raptorflow"
                target="_blank"
                className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card text-muted-foreground transition-editorial hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                aria-label="RaptorFlow on Twitter"
                title="Twitter"
                rel="me noopener noreferrer"
              >
                <Twitter className="h-4 w-4" />
              </a>
              <a
                href="https://linkedin.com/company/raptorflow"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card text-muted-foreground transition-editorial hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                aria-label="RaptorFlow on LinkedIn"
                title="LinkedIn"
              >
                <Linkedin className="h-4 w-4" />
              </a>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card text-muted-foreground transition-editorial hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                aria-label="RaptorFlow on GitHub"
                title="GitHub"
              >
                <Github className="h-4 w-4" />
              </a>
            </div>
          </div>

          <div className="md:col-span-7">
            <nav aria-label="Footer" className="grid gap-10 sm:grid-cols-4">
              {(
                [
                  {
                    title: 'Product',
                    links: [
                      { to: '/', label: 'Landing' },
                      { to: '/pricing', label: 'Pricing' },
                      { to: '/login', label: 'Sign in' },
                      { to: '/signup', label: 'Get started' },
                    ],
                  },
                  {
                    title: 'Company',
                    links: [
                      { to: '/about', label: 'About' },
                      { to: '/manifesto', label: 'Manifesto' },
                      { to: '/blog', label: 'Blog' },
                      { to: '/careers', label: 'Careers' },
                    ],
                  },
                  {
                    title: 'Support',
                    links: [
                      { to: '/contact', label: 'Contact' },
                      { to: '/faq', label: 'FAQ' },
                      { to: '/changelog', label: 'Changelog' },
                      { to: '/status', label: 'Status' },
                    ],
                  },
                  {
                    title: 'Legal',
                    links: [
                      { to: '/privacy', label: 'Privacy' },
                      { to: '/terms', label: 'Terms' },
                      { to: '/refunds', label: 'Refunds' },
                      { to: '/cookies', label: 'Cookies' },
                    ],
                  },
                ] as const
              ).map((col) => (
                <div key={col.title} className="space-y-3">
                  <div className="text-editorial-caption">{col.title}</div>
                  <div className="grid gap-2">
                    {col.links.map((item) => (
                      <motion.div
                        key={item.to}
                        className="relative w-fit"
                        initial={false}
                        whileHover={reduceMotion ? undefined : { x: 2 }}
                        transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
                      >
                        <Link
                          to={item.to}
                          className="group text-body-sm text-muted-foreground transition-editorial hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                        >
                          {item.label}
                          <span className="pointer-events-none absolute -bottom-0.5 left-0 h-px w-full origin-left scale-x-0 bg-gradient-to-r from-primary/60 via-primary/20 to-transparent transition-transform duration-300 group-hover:scale-x-100" />
                        </Link>
                      </motion.div>
                    ))}
                  </div>
                </div>
              ))}
            </nav>
          </div>
        </div>

        {/* bottom legal */}
        <div className="flex flex-col gap-3 border-t border-border py-6 text-body-xs text-muted-foreground md:flex-row md:items-center md:justify-between">
          <div className="flex flex-col gap-1">
            <div>© {new Date().getFullYear()} RaptorFlow</div>
            <div className="text-[11px] text-muted-foreground flex items-center gap-2 flex-wrap">
              <span>Powered by caffeine ☕</span>
              <span className="text-muted-foreground/40">•</span>
              <span>Refereed with ❤️ in India</span>
              <span className="text-muted-foreground/40">•</span>
              <span>Built by <a href="https://beats.studio" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Beats</a></span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-6">
            <motion.button
              type="button"
              className="group relative w-fit transition-editorial hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              whileHover={reduceMotion ? undefined : { x: 2 }}
              transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
              onClick={() => {
                const prefersReducedMotion = (() => {
                  try {
                    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
                  } catch {
                    return false
                  }
                })()
                window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' })
              }}
            >
              Back to top
              <span className="pointer-events-none absolute -bottom-0.5 left-0 h-px w-full origin-left scale-x-0 bg-gradient-to-r from-primary/60 via-primary/20 to-transparent transition-transform duration-300 group-hover:scale-x-100" />
            </motion.button>
            <Link
              to="/contact"
              className="group relative w-fit transition-editorial hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              Contact
              <span className="pointer-events-none absolute -bottom-0.5 left-0 h-px w-full origin-left scale-x-0 bg-gradient-to-r from-primary/60 via-primary/20 to-transparent transition-transform duration-300 group-hover:scale-x-100" />
            </Link>
            <Link
              to="/privacy"
              className="group relative w-fit transition-editorial hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              Privacy
              <span className="pointer-events-none absolute -bottom-0.5 left-0 h-px w-full origin-left scale-x-0 bg-gradient-to-r from-primary/60 via-primary/20 to-transparent transition-transform duration-300 group-hover:scale-x-100" />
            </Link>
            <Link
              to="/terms"
              className="group relative w-fit transition-editorial hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
            >
              Terms
              <span className="pointer-events-none absolute -bottom-0.5 left-0 h-px w-full origin-left scale-x-0 bg-gradient-to-r from-primary/60 via-primary/20 to-transparent transition-transform duration-300 group-hover:scale-x-100" />
            </Link>
            <motion.a
              href="mailto:hello@raptorflow.com"
              className="group relative w-fit transition-editorial hover:text-foreground"
              whileHover={reduceMotion ? undefined : { x: 2 }}
              transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
            >
              hello@raptorflow.com
              <span className="pointer-events-none absolute -bottom-0.5 left-0 h-px w-full origin-left scale-x-0 bg-gradient-to-r from-primary/60 via-primary/20 to-transparent transition-transform duration-300 group-hover:scale-x-100" />
            </motion.a>
          </div>
        </div>
      </div>
    </footer>
  )
}
