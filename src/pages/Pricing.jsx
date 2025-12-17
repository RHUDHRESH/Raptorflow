import React from 'react'
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'

import { MarketingLayout } from '@/components/MarketingLayout'

const Pricing = () => {
  const tiers = [
    {
      name: "Founder",
      price: "49",
      description: "For bootstrappers building in public.",
      features: ["Unlimited Strategy Matrices", "3 Active Briefs", "7-Day Analytics History", "Community Support"],
      cta: "Get started",
      popular: false
    },
    {
      name: "Pro",
      price: "49",
      description: "For serious operators scaling to $1M.",
      features: ["Everything in Founder", "Unlimited Briefs", "Full Analytics History", "Priority Support", "Team Collaboration (up to 3)"],
      cta: "Go Pro",
      popular: true
    },
    {
      name: "Agency",
      price: "199",
      description: "For consultants managing multiple portfolios.",
      features: ["Everything in Pro", "Unlimited Clients", "White-label Reports", "Dedicated Account Manager", "API Access"],
      cta: "Contact Sales",
      popular: false
    }
  ]

  return (
    <MarketingLayout>
      <div className="container-editorial py-16 md:py-24">
        <header className="text-center max-w-3xl mx-auto">
          <p className="text-editorial-caption mb-6">Pricing</p>
          <h1 className="font-serif text-headline-xl md:text-[4.25rem] leading-[1.06] text-foreground">
            Simple plans.
            <br />
            <span className="italic text-primary">Compounding execution.</span>
          </h1>
          <p className="mt-6 text-body-lg text-muted-foreground">
            Start with a paid plan. If it’s not a fit, you’re covered by our 14-day money-back guarantee.
          </p>
        </header>

        <section className="mt-14 grid gap-6 md:grid-cols-3 items-start">
          {tiers.map((tier, index) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              className={`rounded-card border ${tier.popular ? 'border-primary/40 bg-card shadow-editorial' : 'border-border bg-card'} p-8`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="font-serif text-headline-sm text-foreground">{tier.name}</h2>
                  <p className="mt-2 text-body-sm text-muted-foreground leading-relaxed">{tier.description}</p>
                </div>
                {tier.popular ? (
                  <div className="pill-editorial pill-neutral">Most popular</div>
                ) : null}
              </div>

              <div className="mt-6 flex items-baseline gap-2">
                <div className="font-serif text-headline-md text-foreground">${tier.price}</div>
                <div className="text-body-sm text-muted-foreground">/mo</div>
              </div>

              <ul className="mt-6 space-y-3">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3 text-body-sm text-muted-foreground">
                    <Check className="mt-0.5 h-4 w-4 text-primary flex-shrink-0" />
                    <span className="leading-relaxed">{feature}</span>
                  </li>
                ))}
              </ul>

              <div className="mt-8">
                <a
                  href="/signup"
                  className={`inline-flex w-full items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-editorial focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-2 focus-visible:ring-offset-background ${
                    tier.popular
                      ? 'bg-primary text-primary-foreground hover:opacity-90'
                      : 'border border-border bg-transparent text-foreground hover:bg-muted'
                  }`}
                >
                  {tier.cta}
                </a>
              </div>
            </motion.div>
          ))}
        </section>

        <section className="mt-14 rounded-card border border-border bg-card p-8">
          <div className="text-center max-w-2xl mx-auto">
            <div className="text-editorial-caption">FAQ</div>
            <h2 className="mt-3 font-serif text-headline-md text-foreground">Common questions</h2>
            <p className="mt-2 text-body-sm text-muted-foreground">
              If you still have questions, email{' '}
              <a className="underline" href="mailto:hello@raptorflow.com">
                hello@raptorflow.com
              </a>
              .
            </p>
          </div>

          <div className="mt-8 grid gap-6 md:grid-cols-2">
            {[
              {
                q: 'Can I cancel anytime?',
                a: 'Yes. Cancel from your account settings. You’ll keep access through the end of your billing period.',
              },
              {
                q: 'Do you offer refunds?',
                a: 'Yes—see our refund policy page for details.',
              },
              {
                q: 'Do you have a team plan?',
                a: 'Team collaboration is available on paid tiers. If you need a larger plan, contact us.',
              },
              {
                q: 'Do you offer paid plans only?',
                a: 'Yes. RaptorFlow is paid. If it’s not a fit, you can request a refund within 14 days.',
              },
            ].map((item) => (
              <div key={item.q} className="rounded-card border border-border bg-background p-6">
                <div className="font-serif text-headline-sm text-foreground">{item.q}</div>
                <div className="mt-2 text-body-sm text-muted-foreground leading-relaxed">{item.a}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-14 text-center border-t border-border pt-12">
          <h2 className="font-serif text-headline-md text-foreground">Ready to ship daily?</h2>
          <p className="mt-3 text-body-sm text-muted-foreground max-w-[70ch] mx-auto">
            Build the 90-day map. Then run it.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            <a
              href="/signup"
              className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-90"
            >
              Get started
            </a>
            <a
              href="/contact"
              className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-5 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted"
            >
              Talk to us
            </a>
          </div>
        </section>
      </div>
    </MarketingLayout>
  )
}

export default Pricing
