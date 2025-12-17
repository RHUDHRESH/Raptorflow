import * as React from 'react'

import { cn } from '@/lib/utils'

import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

export function MarketingLayout({
  children,
  mainClassName,
  showFooter = true,
}: {
  children: React.ReactNode
  mainClassName?: string
  showFooter?: boolean
}) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader />
      <main className={cn('flex-1', mainClassName)}>{children}</main>
      {showFooter && <SiteFooter />}
    </div>
  )
}
