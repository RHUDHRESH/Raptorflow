import React from 'react'

import { MarketingLayout } from '@/components/MarketingLayout'

const Changelog = () => {
  return (
    <MarketingLayout>
      <div className="container-editorial py-16 md:py-24">
        <header className="mb-12">
          <div className="text-editorial-caption">Product</div>
          <h1 className="mt-3 font-serif text-headline-lg text-foreground">Changelog</h1>
          <p className="mt-3 max-w-[70ch] text-body-sm text-muted-foreground">
            A running log of improvements, fixes, and new capabilities.
          </p>
        </header>

        <div className="space-y-6">
          {[
            {
              version: 'v0.1',
              date: 'Dec 2025',
              items: ['Improved marketing footer IA and navigation', 'Added support/legal pages', 'Polished CTA and focus states'],
            },
          ].map((entry) => (
            <section key={entry.version} className="rounded-card border border-border bg-card p-6">
              <div className="flex flex-col gap-1 md:flex-row md:items-baseline md:justify-between">
                <h2 className="font-serif text-headline-sm text-foreground">{entry.version}</h2>
                <div className="text-body-xs text-muted-foreground">{entry.date}</div>
              </div>
              <ul className="mt-4 space-y-2">
                {entry.items.map((it) => (
                  <li key={it} className="text-body-sm text-muted-foreground leading-relaxed flex items-start gap-3">
                    <span className="mt-2 h-1.5 w-1.5 rounded-full bg-primary/60 flex-shrink-0" />
                    {it}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>

        <div className="mt-12 rounded-card border border-border bg-card p-6">
          <div className="text-editorial-caption">Want updates?</div>
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

export default Changelog
