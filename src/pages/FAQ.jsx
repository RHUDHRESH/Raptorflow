import React from 'react'

import { MarketingLayout } from '@/components/MarketingLayout'

const FAQ = () => {
  return (
    <MarketingLayout>
      <div className="container-editorial py-16 md:py-24">
        <header className="mb-12">
          <div className="text-editorial-caption">Support</div>
          <h1 className="mt-3 font-serif text-headline-lg text-foreground">FAQ</h1>
          <p className="mt-3 max-w-[70ch] text-body-sm text-muted-foreground">
            Answers to the most common questions about RaptorFlow.
          </p>
        </header>

        <div className="grid gap-6 md:grid-cols-2">
          {[
            {
              q: 'Do you offer paid plans only?',
              a: 'Yes. RaptorFlow is a paid product. We do offer a 14-day money-back guarantee if it\'s not a fit.',
            },
            {
              q: 'Do you replace my strategy or help me execute it?',
              a: 'We help you turn decisions into assets and execution—so you ship consistently without weekly resets.',
            },
            {
              q: 'How do I get support?',
              a: 'Email hello@raptorflow.com. We usually respond within 24 hours.',
            },
            {
              q: 'Can I cancel anytime?',
              a: 'Yes. You can cancel from your account settings. If you need help, email us.',
            },
          ].map((item) => (
            <section key={item.q} className="rounded-card border border-border bg-card p-6">
              <h2 className="font-serif text-headline-sm text-foreground">{item.q}</h2>
              <p className="mt-2 text-body-sm text-muted-foreground leading-relaxed">{item.a}</p>
            </section>
          ))}
        </div>

        <div className="mt-12 rounded-card border border-border bg-card p-6">
          <div className="text-editorial-caption">Still stuck?</div>
          <p className="mt-2 text-body-sm text-muted-foreground">
            Email{' '}
            <a className="underline" href="mailto:hello@raptorflow.com">
              hello@raptorflow.com
            </a>
            .
          </p>
        </div>
      </div>
    </MarketingLayout>
  )
}

export default FAQ
