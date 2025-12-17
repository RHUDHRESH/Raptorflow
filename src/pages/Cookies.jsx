import React from 'react'

import { MarketingLayout } from '@/components/MarketingLayout'

const Cookies = () => {
  return (
    <MarketingLayout>
      <div className="container-editorial py-16 md:py-24">
        <header className="mb-12">
          <div className="text-editorial-caption">Legal</div>
          <h1 className="mt-3 font-serif text-headline-lg text-foreground">Cookies Policy</h1>
          <p className="mt-3 max-w-[70ch] text-body-sm text-muted-foreground">
            This page explains what cookies are, how we use them, and your choices.
          </p>
          <p className="mt-2 text-body-xs text-muted-foreground">Last updated: Dec 2025</p>
        </header>

        <div className="space-y-6">
          {[
            {
              title: '1. What cookies are',
              body: 'Cookies are small text files stored on your device. They help websites remember preferences and maintain sessions.',
            },
            {
              title: '2. Cookies we use',
              body: 'We use essential cookies required for authentication and security. We may use analytics cookies to understand usage and improve the product.',
            },
            {
              title: '3. Your choices',
              body: 'You can control cookies through your browser settings. Blocking essential cookies may prevent the app from functioning correctly.',
            },
          ].map((s) => (
            <section key={s.title} className="rounded-card border border-border bg-card p-6">
              <h2 className="font-serif text-headline-sm text-foreground">{s.title}</h2>
              <p className="mt-2 text-body-sm text-muted-foreground leading-relaxed">{s.body}</p>
            </section>
          ))}
        </div>

        <section className="mt-10 rounded-card border border-border bg-card p-6">
          <div className="text-editorial-caption">Questions</div>
          <p className="mt-2 text-body-sm text-muted-foreground">
            Email{' '}
            <a className="underline" href="mailto:hello@raptorflow.com">
              hello@raptorflow.com
            </a>
            .
          </p>
        </section>
      </div>
    </MarketingLayout>
  )
}

export default Cookies
