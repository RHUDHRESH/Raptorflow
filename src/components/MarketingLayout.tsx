import * as React from 'react'

import { cn } from '@/lib/utils'

import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'
import { NanobanaBackground } from '@/components/ui/NanobanaBackground'

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
    <div className="relative min-h-screen bg-background text-foreground overflow-x-hidden">
      <NanobanaBackground variant="nebula" intensity="medium" />
      <SiteHeader />
      <main className={cn('relative z-10 flex-1', mainClassName)}>{children}</main>
      {showFooter && <SiteFooter />}
    </div>
  )
}
