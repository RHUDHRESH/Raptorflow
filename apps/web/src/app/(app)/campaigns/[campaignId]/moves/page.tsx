"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { use } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const MOVE_TYPES = ["awareness", "consideration", "conversion", "retention", "launch"] as const;

const MOCK_MOVES: Record<string, { title: string; description: string; status: string; budget: number }> = {
  awareness: { title: "Launch LinkedIn campaign", description: "Initial brand awareness push on LinkedIn", status: "active", budget: 4000 },
  consideration: { title: "Publish 3 blog posts on industry trends", description: "Content-led nurture for mid-funnel", status: "planned", budget: 1500 },
  conversion: { title: "Run webinar with target ICP", description: "High-intent live event for bottom-of-funnel", status: "planned", budget: 2500 },
  retention: { title: "Launch email nurture sequence", description: "Onboarding and retention email flow", status: "planned", budget: 1000 },
  launch: { title: "Product launch announcement", description: "Multi-channel launch blast", status: "planned", budget: 3000 },
};

export default async function CampaignMovesPage({
  params
}: {
  params: Promise<{ campaignId: string }>;
}): Promise<React.ReactElement> {
  const { campaignId } = await params;
  const campaignRoute = `/campaigns/${campaignId}` as Route;

  return (
    <RouteShell
      eyebrow="Moves"
      title="Move sequence"
      description="Sequenced campaign moves mapped to the customer journey — awareness through retention."
      tags={["moves", "journey", "planning"]}
      backHref={campaignRoute}
      backLabel="Back to Campaign"
    >
      <div className="grid gap-4 xl:grid-cols-2">
        {MOVE_TYPES.map((moveType, index) => {
          const move = MOCK_MOVES[moveType];
          return (
            <Card key={moveType} className="transition-shadow hover:shadow-md">
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--accent)] text-xs font-bold">
                      {index + 1}
                    </span>
                    <div>
                      <p className="font-semibold capitalize">{moveType}</p>
                      <p className="mt-1 text-sm text-[var(--muted-foreground)]">{move.title}</p>
                    </div>
                  </div>
                  <span className={`rounded-full px-2 py-0.5 text-xs ${
                    move.status === "active" ? "bg-green-100 text-green-700" : "bg-[var(--muted)]"
                  }`}>
                    {move.status}
                  </span>
                </div>
                <p className="mt-2 text-sm text-[var(--muted-foreground)]">{move.description}</p>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-sm font-medium">${move.budget.toLocaleString()}</span>
                  <Link
                    href={`/campaigns/${campaignId}/moves/${moveType}` as Route}
                    className="text-xs text-[var(--accent)] hover:underline"
                  >
                    View move →
                  </Link>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="border-amber-200 bg-amber-50/50">
        <CardHeader>
          <CardTitle className="text-base">📝 What to implement next</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-amber-800">
          <p><strong>Backend:</strong> Add moves endpoints to campaignsApi — currently using mock data. Wire to real API endpoints for CRUD operations on moves.</p>
          <p><strong>Move creation:</strong> "Add move" modal that lets users create a new move within a campaign with type, budget, and timeline.</p>
          <p><strong>Reorder:</strong> Drag-and-drop reordering of moves within the sequence — affects the campaign execution order.</p>
          <p><strong>Budget allocation:</strong> Visual budget breakdown showing how the campaign budget is distributed across moves.</p>
          <p><strong>Status propagation:</strong> Move status auto-updates when tasks within it are completed or delayed.</p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
