import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { ArrowRight, Building2, Compass, Radar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const pillars = [
  {
    title: "Foundation-first onboarding",
    body: "Twenty-one screens, dual scans, and versioned business context before any strategic output."
  },
  {
    title: "Council-driven planning",
    body: "Named avatar deliberation, structured synthesis, and campaign scaffolds with memory hooks."
  },
  {
    title: "The Office as evidence",
    body: "A PixiJS canvas shell tied to websocket events so product state can become visual state."
  }
];

export default function MarketingHome(): React.ReactElement {
  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col gap-12 px-6 py-10 md:px-10">
      <header className="flex items-center justify-between rounded-full border border-[var(--border)] bg-white/70 px-5 py-3 backdrop-blur">
        <div className="flex items-center gap-3 text-sm font-medium">
          <Building2 className="h-4 w-4 text-[var(--primary)]" />
          RaptorFlow
        </div>
        <div className="flex items-center gap-3">
          <Link href={"/sign-in" as Route} className="text-sm text-[var(--muted-foreground)]">
            Sign in
          </Link>
          <Button asChild>
            <Link href={"/sign-up" as Route}>Get access</Link>
          </Button>
        </div>
      </header>

      <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <p className="text-sm uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
            Living marketing office
          </p>
          <h1 className="max-w-4xl font-[family-name:var(--font-display)] text-5xl leading-tight md:text-7xl">
            Production scaffold for a memory-native marketing operating system.
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-[var(--muted-foreground)]">
            This repository is structured for a Next.js 15 frontend, a single-binary Axum backend,
            tenant-safe data planes, and an event-driven Office shell without prematurely filling in
            product logic.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button asChild size="lg">
              <Link href="/app">
                Open app shell
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="secondary">
              <Link href="/office">View Office shell</Link>
            </Button>
          </div>
        </div>

        <div className="grid gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Compass className="h-4 w-4 text-[var(--primary)]" />
                Canonical decisions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-[var(--muted-foreground)]">
              <p>Frontend on Vercel, backend on ECS Fargate, data plane in Mumbai.</p>
              <p>Shared contracts, migrations, and infra modules are scaffolded before runtime logic.</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Radar className="h-4 w-4 text-[var(--accent)]" />
                Product lanes
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-[var(--muted-foreground)]">
              <p>Foundation, Campaigns, Council, Muse, Daily Wins, Billing, and Office all have reserved route and contract surfaces.</p>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {pillars.map((pillar) => (
          <Card key={pillar.title}>
            <CardHeader>
              <CardTitle>{pillar.title}</CardTitle>
            </CardHeader>
            <CardContent className="text-sm leading-7 text-[var(--muted-foreground)]">
              {pillar.body}
            </CardContent>
          </Card>
        ))}
      </section>
    </main>
  );
}
