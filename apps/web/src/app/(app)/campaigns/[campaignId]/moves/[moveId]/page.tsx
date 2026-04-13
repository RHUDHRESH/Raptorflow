"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { use } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const MOVE_DATA: Record<string, {
  title: string; description: string; status: string; budget: number;
  timeline: string; channels: string[]; tasks: { id: string; title: string; status: string; assignee: string }[]
}> = {
  awareness: {
    title: "Launch LinkedIn campaign",
    description: "Initial brand awareness push targeting decision-makers at SaaS companies with 50-500 employees.",
    status: "active",
    budget: 4000,
    timeline: "Week 1-2",
    channels: ["LinkedIn", "Google Ads"],
    tasks: [
      { id: "t1", title: "Write 3 ad creatives", status: "done", assignee: "Ogilvy" },
      { id: "t2", title: "Set up campaign in LinkedIn Ads", status: "done", assignee: "Patel" },
      { id: "t3", title: "Define audience segments", status: "in_progress", assignee: "Strategist" },
      { id: "t4", title: "Launch and monitor CTR", status: "pending", assignee: "Patel" },
    ],
  },
  consideration: {
    title: "Publish 3 blog posts on industry trends",
    description: "Content-led nurture targeting mid-funnel prospects with thought leadership content.",
    status: "planned",
    budget: 1500,
    timeline: "Week 2-4",
    channels: ["Blog", "LinkedIn", "Newsletter"],
    tasks: [
      { id: "t1", title: "Research top 5 industry trends", status: "pending", assignee: "Sharp" },
      { id: "t2", title: "Write post 1: AI in marketing ops", status: "pending", assignee: "Ogilvy" },
    ],
  },
  conversion: {
    title: "Run webinar with target ICP",
    description: "High-intent live event for bottom-of-funnel prospects with demo and Q&A.",
    status: "planned",
    budget: 2500,
    timeline: "Week 4",
    channels: ["Webinar", "Email", "LinkedIn"],
    tasks: [],
  },
  retention: {
    title: "Launch email nurture sequence",
    description: "Onboarding and retention email flow for existing customers and warm leads.",
    status: "planned",
    budget: 1000,
    timeline: "Week 5-8",
    channels: ["Email"],
    tasks: [],
  },
  launch: {
    title: "Product launch announcement",
    description: "Multi-channel launch blast for the new feature announcement.",
    status: "planned",
    budget: 3000,
    timeline: "TBD",
    channels: ["Email", "LinkedIn", "Twitter", "Blog"],
    tasks: [],
  },
};

export default async function CampaignMoveDetailPage({
  params
}: {
  params: Promise<{ campaignId: string; moveId: string }>;
}): Promise<React.ReactElement> {
  const { campaignId, moveId } = await params;
  const move = MOVE_DATA[moveId] ?? MOVE_DATA.consideration;

  return (
    <RouteShell
      eyebrow="Move detail"
      title={move.title}
      description={move.description}
      tags={[moveId, "move"]}
      backHref={`/campaigns/${campaignId}/moves` as Route}
      backLabel="Back to Moves"
    >
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Move overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Badge className={move.status === "active" ? "bg-green-100 text-green-700" : "bg-[var(--muted)]"}>
                  {move.status}
                </Badge>
                <span className="text-lg font-bold">${move.budget.toLocaleString()}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-[var(--muted-foreground)]">Timeline</p>
                  <p className="font-medium">{move.timeline}</p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Channels</p>
                  <div className="flex flex-wrap gap-1">
                    {move.channels.map((ch) => (
                      <Badge key={ch} variant="outline" className="text-xs">{ch}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tasks ({move.tasks.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {move.tasks.length === 0 ? (
                <p className="py-4 text-center text-sm text-[var(--muted-foreground)]">No tasks yet</p>
              ) : (
                <div className="space-y-2">
                  {move.tasks.map((task) => (
                    <div key={task.id} className="flex items-center justify-between rounded-lg border border-[var(--border)] px-3 py-2">
                      <div className="flex items-center gap-3">
                        <span className={`h-2 w-2 rounded-full ${
                          task.status === "done" ? "bg-green-500" :
                          task.status === "in_progress" ? "bg-blue-500" : "bg-[var(--muted)]"
                        }`} />
                        <span className="text-sm">{task.title}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-[var(--muted-foreground)]">{task.assignee}</span>
                        <Link
                          href={`/campaigns/${campaignId}/tasks/${task.id}` as Route}
                          className="text-xs text-[var(--accent)] hover:underline"
                        >
                          View →
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Move actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" size="sm" variant="secondary">Add task</Button>
              <Button className="w-full" size="sm" variant="secondary">Edit move</Button>
              <Button className="w-full" size="sm" variant="destructive">Remove move</Button>
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50/50">
            <CardHeader>
              <CardTitle className="text-base">📝 What to implement next</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-amber-800">
              <p><strong>Task drill-down:</strong> Each task should link to <code>/campaigns/[id]/tasks/[taskId]</code> with full task detail.</p>
              <p><strong>Move editor:</strong> Full CRUD for moves — edit title, description, budget, timeline, channels.</p>
              <p><strong>Task creation:</strong> Create tasks within a move and assign to council agents (Ogilvy, Patel, Sharp, etc.).</p>
              <p><strong>Progress tracking:</strong> Visual progress bar showing tasks done vs total within this move.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </RouteShell>
  );
}
