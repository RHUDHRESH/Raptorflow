"use client";

import type * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useFoundation } from "@/hooks/use-foundation";
import { useCampaigns } from "@/hooks/use-campaigns";
import { useCouncilSessions } from "@/hooks/use-council";
import { useMuseConversations } from "@/hooks/use-muse";
import { useBillingStatus } from "@/hooks/use-billing";

function DashboardTile({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-[var(--muted-foreground)]">{title}</CardTitle>
        {action}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function LoadingTile({ rows = 3 }: { rows?: number }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="h-4 w-24 animate-pulse rounded bg-[var(--muted)]" />
      </CardHeader>
      <CardContent className="space-y-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-3 w-full animate-pulse rounded bg-[var(--muted)]" />
        ))}
      </CardContent>
    </Card>
  );
}

export default function AppHomePage(): React.ReactElement {
  const { data: foundation, isLoading: foundationLoading } = useFoundation();
  const { data: campaigns, isLoading: campaignsLoading } = useCampaigns();
  const { data: councilSessions, isLoading: councilLoading } = useCouncilSessions();
  const { data: museConversations, isLoading: museLoading } = useMuseConversations();
  const { data: billing, isLoading: billingLoading } = useBillingStatus();

  const foundationComplete = foundation ? Object.keys(foundation.sections).length : 0;
  const activeCampaigns = campaigns?.filter((c) => c.status === "active").length ?? 0;
  const runningSessions = councilSessions?.filter((s) => s.status === "running" || s.status === "streaming").length ?? 0;
  const recentMuse = museConversations?.slice(0, 3) ?? [];

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-[0.22em] text-[var(--muted-foreground)]">
          App shell
        </p>
        <h1 className="font-[family-name:var(--font-display)] text-4xl">
          RaptorFlow control surface
        </h1>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {foundationLoading ? (
          <LoadingTile />
        ) : (
          <DashboardTile title="Foundation completeness" action={<Badge variant="outline">{foundationComplete}/21</Badge>}>
            <div className="space-y-3">
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-[var(--muted)]">
                <div
                  className="h-full rounded-full bg-[var(--primary)] transition-all"
                  style={{ width: `${(foundationComplete / 21) * 100}%` }}
                />
              </div>
              <div className="space-y-1 text-xs text-[var(--muted-foreground)]">
                {foundation?.sections && Object.entries(foundation.sections).slice(0, 5).map(([key, val]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="capitalize">{key.replace(/([A-Z])/g, " $1").toLowerCase().trim()}</span>
                    <span className={val ? "text-green-600" : "text-amber-500"}>{val ? "✓" : "—"}</span>
                  </div>
                ))}
                {foundationComplete < 21 && (
                  <p className="pt-1 text-[var(--muted-foreground)]">
                    {21 - foundationComplete} sections remaining
                  </p>
                )}
              </div>
            </div>
          </DashboardTile>
        )}

        {campaignsLoading ? (
          <LoadingTile />
        ) : (
          <DashboardTile
            title="Campaign execution state"
            action={<Badge className="bg-green-100 text-green-700 border-green-200">{activeCampaigns} active</Badge>}
          >
            <div className="space-y-2">
              {campaigns?.slice(0, 4).map((campaign) => (
                <div key={campaign.campaignId} className="flex items-center justify-between text-sm">
                  <span className="truncate font-medium">{campaign.name}</span>
                  <Badge
                    variant="outline"
                    className={
                      campaign.status === "active" ? "bg-green-50 text-green-700 border-green-200" :
                      campaign.status === "paused" ? "bg-amber-50 text-amber-700 border-amber-200" :
                      "bg-[var(--muted)]"
                    }
                  >
                    {campaign.status}
                  </Badge>
                </div>
              ))}
              {!campaigns?.length && (
                <p className="text-sm text-[var(--muted-foreground)]">No campaigns yet</p>
              )}
            </div>
          </DashboardTile>
        )}

        {councilLoading ? (
          <LoadingTile />
        ) : (
          <DashboardTile
            title="Council session queue"
            action={<Badge variant="outline">{runningSessions} running</Badge>}
          >
            <div className="space-y-2">
              {councilSessions?.slice(0, 4).map((session) => (
                <div key={session.sessionId} className="flex items-center justify-between text-sm">
                  <span className="truncate">
                    <span className="font-medium capitalize">{session.sessionType.replace("_", " ")}</span>
                    {" · "}
                    <span className="text-[var(--muted-foreground)]">
                      {new Date(session.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                    </span>
                  </span>
                  <Badge
                    variant="outline"
                    className={
                      session.status === "running" || session.status === "streaming" ? "bg-blue-50 text-blue-700 border-blue-200" :
                      session.status === "completed" ? "bg-green-50 text-green-700 border-green-200" :
                      "bg-[var(--muted)]"
                    }
                  >
                    {session.status}
                  </Badge>
                </div>
              ))}
              {!councilSessions?.length && (
                <p className="text-sm text-[var(--muted-foreground)]">No sessions yet</p>
              )}
            </div>
          </DashboardTile>
        )}

        {museLoading ? (
          <LoadingTile rows={2} />
        ) : (
          <DashboardTile title="Muse activity" action={<Badge variant="outline">{museConversations?.length ?? 0} conversations</Badge>}>
            <div className="space-y-2">
              {recentMuse.map((conv) => (
                <div key={conv.conversationId} className="flex items-center justify-between text-sm">
                  <span className="truncate font-medium capitalize">{conv.route.replace("_", " ")}</span>
                  <span className="text-xs text-[var(--muted-foreground)]">
                    {conv.messageCount} messages
                  </span>
                </div>
              ))}
              {!recentMuse.length && (
                <p className="text-sm text-[var(--muted-foreground)]">No conversations yet</p>
              )}
            </div>
          </DashboardTile>
        )}

        {billingLoading ? (
          <LoadingTile />
        ) : (
          <DashboardTile
            title="Billing status"
            action={
              <Badge
                className={
                  billing?.status === "active" ? "bg-green-100 text-green-700 border-green-200" :
                  billing?.status === "past_due" ? "bg-red-100 text-red-700 border-red-200" :
                  "bg-[var(--muted)]"
                }
              >
                {billing?.status ?? "—"}
              </Badge>
            }
          >
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted-foreground)]">Plan</span>
                <span className="font-medium capitalize">{billing?.plan ?? "—"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted-foreground)]">Renewal</span>
                <span>
                  {billing?.currentPeriodEnd
                    ? new Date(billing.currentPeriodEnd).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
                    : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted-foreground)]">Invoices</span>
                <span>{billing?.invoiceCount ?? 0}</span>
              </div>
            </div>
          </DashboardTile>
        )}

        <DashboardTile title="Infrastructure health">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span>API</span>
              <span className="ml-auto text-[var(--muted-foreground)]">Operational</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span>Database</span>
              <span className="ml-auto text-[var(--muted-foreground)]">Operational</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span>Queue</span>
              <span className="ml-auto text-[var(--muted-foreground)]">Operational</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span>Cache</span>
              <span className="ml-auto text-[var(--muted-foreground)]">Operational</span>
            </div>
          </div>
        </DashboardTile>
      </div>

      <div className="flex justify-end">
        <Button variant="secondary" size="sm">
          View all campaigns →
        </Button>
      </div>
    </div>
  );
}
