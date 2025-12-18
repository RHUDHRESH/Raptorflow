import * as React from 'react'
import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import { Github, Linkedin, Twitter, Zap } from 'lucide-react'
import { RaptorFlowLogo } from '@/components/brand/Logo'

const GITHUB_URL = 'https://github.com/raptorflow'

export function SiteFooter() {
  const reduceMotion = useReducedMotion()

  return (
    <footer className="relative border-t border-white/5 bg-[#05050A]">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="container mx-auto px-6 max-w-7xl">
        {/* CTA band */}
        <div className="py-20">
          <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-10 md:p-12">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-purple-500/5" />

            <div className="relative z-10 grid gap-8 lg:grid-cols-12 lg:items-center">
              <div className="lg:col-span-7">
                <h3 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
                  Ready to engage?
                </h3>
                <p className="mt-4 max-w-[60ch] text-lg text-muted-foreground">
                  Stop planning. Start executing. Build your war room and dominate the quarter.
                </p>
              </div>
              <div className="lg:col-span-5 flex flex-col sm:flex-row gap-4 lg:justify-end">
                <motion.div
                  whileHover={reduceMotion ? undefined : { scale: 1.02 }}
                  whileTap={reduceMotion ? undefined : { scale: 0.98 }}
                >
                  <Link
                    to="/signup"
                    className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-primary px-8 text-base font-bold text-black transition-transform hover:bg-primary/90 hover:shadow-[0_0_20px_rgba(0,240,255,0.4)]"
                  >
                    INITIALIZE <Zap className="w-4 h-4 fill-black" />
                  </Link>
                </motion.div>
                <motion.div
                  whileHover={reduceMotion ? undefined : { scale: 1.02 }}
                  whileTap={reduceMotion ? undefined : { scale: 0.98 }}
                >
                  <Link
                    to="/pricing"
                    className="inline-flex h-12 items-center justify-center rounded-lg border border-white/10 bg-transparent px-8 text-base font-bold text-white transition-colors hover:bg-white/5 hover:border-white/20"
                  >
                    VIEW INTEL
                  </Link>
                </motion.div>
              </div>
            </div>
          </div>
        </div>

        {/* Main footer */}
        <div className="grid gap-12 pb-16 pt-8 md:grid-cols-12 border-t border-white/5">
          <div className="md:col-span-5 space-y-6">
            <Link to="/" className="inline-flex items-center gap-3 group">
              <RaptorFlowLogo size="md" animated={true} />
              <span className="text-xl font-bold tracking-widest text-white group-hover:text-primary transition-colors">RAPTORFLOW</span>
            </Link>

            <p className="max-w-[40ch] text-base text-muted-foreground/80 leading-relaxed">
              The operating system for high-velocity founders. Decisions, assets, and execution in one glass cockpit.
            </p>

            <div className="flex items-center gap-4">
              <a
                href="https://twitter.com/raptorflow"
                target="_blank"
                rel="me noopener noreferrer"
                className="p-2 rounded-lg bg-white/5 text-muted-foreground hover:text-white hover:bg-white/10 transition-all border border-transparent hover:border-white/10"
                aria-label="Twitter"
              >
                <Twitter className="h-5 w-5" />
              </a>
              <a
                href="https://linkedin.com/company/raptorflow"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg bg-white/5 text-muted-foreground hover:text-white hover:bg-white/10 transition-all border border-transparent hover:border-white/10"
                aria-label="LinkedIn"
              >
                <Linkedin className="h-5 w-5" />
              </a>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg bg-white/5 text-muted-foreground hover:text-white hover:bg-white/10 transition-all border border-transparent hover:border-white/10"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5" />
              </a>
            </div>
          </div>

          <div className="md:col-span-7">
            <nav className="grid grid-cols-2 gap-8 sm:grid-cols-4">
              {[
                {
                  title: 'Product',
                  links: [
                    { to: '/#method', label: 'Method' },
                    { to: '/#proof', label: 'Proof' },
                    { to: '/pricing', label: 'Pricing' },
                    { to: '/changelog', label: 'Changelog' },
                  ],
                },
                {
                  title: 'Company',
                  links: [
                    { to: '/about', label: 'About' },
                    { to: '/manifesto', label: 'Manifesto' },
                    { to: '/blog', label: 'Transmission' },
                    { to: '/careers', label: 'Join' },
                  ],
                },
                {
                  title: 'Support',
                  links: [
                    { to: '/contact', label: 'Contact' },
                    { to: '/faq', label: 'FAQ' },
                    { to: '/status', label: 'System Status' },
                  ],
                },
                {
                  title: 'Legal',
                  links: [
                    { to: '/privacy', label: 'Privacy' },
                    { to: '/terms', label: 'Terms' },
                    { to: '/refunds', label: 'Refunds' },
                  ],
                },
              ].map((col) => (
                <div key={col.title} className="space-y-4">
                  <div className="text-xs font-bold uppercase tracking-widest text-muted-foreground/60">{col.title}</div>
                  <ul className="space-y-3">
                    {col.links.map((item) => (
                      <li key={item.to}>
                        <Link
                          to={item.to}
                          className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-2 group"
                        >
                          <span className="w-0 overflow-hidden group-hover:w-2 transition-all duration-300 opacity-0 group-hover:opacity-100 text-primary">•</span>
                          {item.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </nav>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col gap-6 border-t border-white/5 py-8 md:flex-row md:items-center md:justify-between text-xs text-muted-foreground font-mono">
          <div className="flex flex-col gap-2">
            <div className="uppercase tracking-widest">© {new Date().getFullYear()} RaptorFlow Systems Inc.</div>
            <div className="flex items-center gap-2 opacity-60">
              <span>EST. 2025</span>
              <span>//</span>
              <span>EARTH_SEC_01</span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <Link to="/privacy" className="hover:text-white transition-colors">PRIVACY</Link>
            <Link to="/terms" className="hover:text-white transition-colors">TERMS</Link>
            <Link to="/status" className="flex items-center gap-2 hover:text-white transition-colors group">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              OPERATIONAL
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
