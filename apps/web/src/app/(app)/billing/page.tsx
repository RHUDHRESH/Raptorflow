"use client";

import type * as React from "react";
import { useBillingStatus } from "@/hooks/use-billing";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function LoadingCard({ lines = 3 }: { lines?: number }) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-3">
          {Array.from({ length: lines }).map((_, i) => (
            <div key={i} className="h-4 w-full animate-pulse rounded bg-[var(--muted)]" />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function BillingPage(): React.ReactElement {
  const { data: billing, isLoading, error } = useBillingStatus();

  const statusColor =
    billing?.status === "active" ? "bg-green-100 text-green-700 border-green-200" :
    billing?.status === "past_due" ? "bg-red-100 text-red-700 border-red-200" :
    billing?.status === "canceled" ? "bg-[var(--muted)]" : "bg-amber-100 text-amber-700 border-amber-200";

  const planLabel =
    billing?.plan === "free" ? "Free" :
    billing?.plan === "starter" ? "Starter — ₹5,000/mo" :
    billing?.plan === "pro" ? "Pro — ₹15,000/mo" :
    billing?.plan === "enterprise" ? "Enterprise" : "—";

  return (
    <RouteShell
      eyebrow="Account"
      title="Billing"
      description="Subscription management, payment history, and plan details via Razorpay."
      tags={["billing", "razorpay", "subscription"]}
    >
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {isLoading ? (
          <>
            <LoadingCard lines={4} />
            <LoadingCard lines={3} />
            <LoadingCard lines={2} />
          </>
        ) : error ? (
          <Card className="col-span-full border-red-200 bg-red-50">
            <CardContent className="p-6 text-sm text-red-700">
              Failed to load billing status: {error.message}
            </CardContent>
          </Card>
        ) : (
          <>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Current plan</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold">{planLabel}</span>
                  <Badge className={statusColor} variant="outline">
                    {billing?.status?.replace("_", " ") ?? "—"}
                  </Badge>
                </div>
                {billing?.currentPeriodEnd && (
                  <p className="text-sm text-[var(--muted-foreground)]">
                    {billing.status === "active"
                      ? `Renews ${new Date(billing.currentPeriodEnd).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}`
                      : `Expired ${new Date(billing.currentPeriodEnd).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}`}
                  </p>
                )}
                <div className="space-y-2 border-t border-[var(--border)] pt-4 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-[var(--muted-foreground)]">Invoices issued</span>
                    <span className="font-medium">{billing?.invoiceCount ?? 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[var(--muted-foreground)]">Provider</span>
                    <span className="font-medium">Razorpay</span>
                  </div>
                </div>
                <Button className="w-full" variant="secondary" size="sm">
                  Manage subscription
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Plan features</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {billing?.plan === "free" && (
                  <>
                    <p className="text-[var(--muted-foreground)]">1 organization, 3 campaigns, limited AI</p>
                    <Button className="mt-2 w-full" size="sm">Upgrade to Starter</Button>
                  </>
                )}
                {billing?.plan === "starter" && (
                  <>
                    <p className="text-[var(--muted-foreground)]">Unlimited campaigns, full AI, priority support</p>
                    <Button className="mt-2 w-full" variant="secondary" size="sm">Upgrade to Pro</Button>
                  </>
                )}
                {billing?.plan === "pro" && (
                  <>
                    <p className="text-[var(--muted-foreground)]">Custom integrations, dedicated support, SLA guarantee</p>
                    <Button className="mt-2 w-full" variant="secondary" size="sm">Contact sales</Button>
                  </>
                )}
                {billing?.plan === "enterprise" && (
                  <p className="text-[var(--muted-foreground)]">Custom contract — contact your account manager</p>
                )}
                {!billing && <p className="text-[var(--muted-foreground)]">Loading...</p>}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Grace period</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">⏱️</div>
                  <div>
                    <p className="font-semibold">2 days grace</p>
                    <p className="text-sm text-[var(--muted-foreground)]">
                      After payment failure, you have 2 days before services are paused.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </RouteShell>
  );
}
