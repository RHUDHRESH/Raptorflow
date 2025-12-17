import React from 'react'

import { MarketingLayout } from '@/components/MarketingLayout'

const Status = () => {
  return (
    <MarketingLayout>
      <div className="container-editorial py-16 md:py-24">
        <header className="mb-12">
          <div className="text-editorial-caption">Support</div>
          <h1 className="mt-3 font-serif text-headline-lg text-foreground">Status</h1>
          <p className="mt-3 max-w-[70ch] text-body-sm text-muted-foreground">
            Current system status and recent incidents.
          </p>
        </header>

        <section className="rounded-card border border-border bg-card p-6">
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-editorial-caption">Overall</div>
              <div className="mt-1 font-serif text-headline-sm text-foreground">All systems operational</div>
            </div>
            <div className="text-body-xs text-muted-foreground">Last updated: just now</div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {[
              { name: 'API', status: 'Operational' },
              { name: 'App', status: 'Operational' },
              { name: 'Billing', status: 'Operational' },
            ].map((svc) => (
              <div key={svc.name} className="rounded-card border border-border bg-background p-4">
                <div className="text-body-sm text-foreground">{svc.name}</div>
                <div className="mt-1 text-body-xs text-muted-foreground">{svc.status}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-8 rounded-card border border-border bg-card p-6">
          <div className="text-editorial-caption">Need help?</div>
          <p className="mt-2 text-body-sm text-muted-foreground">
            If you’re seeing issues, email{' '}
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

export default Status
