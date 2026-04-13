"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { use } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const MOCK_TASKS: Record<string, {
  title: string; description: string; status: string; priority: string;
  assignee: string; dueDate: string; moveType: string; campaignId: string;
}> = {
  "t1": { title: "Write 3 ad creatives", description: "Create compelling ad copy for LinkedIn campaign targeting SaaS decision-makers.", status: "done", priority: "high", assignee: "Ogilvy", dueDate: "2025-04-15", moveType: "awareness", campaignId: "campaign-001" },
  "t2": { title: "Set up campaign in LinkedIn Ads", description: "Configure campaign structure, audience targeting, and budget allocation.", status: "done", priority: "high", assignee: "Patel", dueDate: "2025-04-16", moveType: "awareness", campaignId: "campaign-001" },
  "t3": { title: "Define audience segments", description: "Research and define ICP segments for the LinkedIn campaign.", status: "in_progress", priority: "medium", assignee: "Strategist", dueDate: "2025-04-18", moveType: "awareness", campaignId: "campaign-001" },
  "t4": { title: "Launch and monitor CTR", description: "Go live with ads and track click-through rates for first 48 hours.", status: "pending", priority: "high", assignee: "Patel", dueDate: "2025-04-20", moveType: "awareness", campaignId: "campaign-001" },
};

export default async function CampaignTaskDetailPage({
  params
}: {
  params: Promise<{ campaignId: string; taskId: string }>;
}): Promise<React.ReactElement> {
  const { campaignId, taskId } = await params;
  const task = MOCK_TASKS[taskId] ?? Object.values(MOCK_TASKS)[0];

  return (
    <RouteShell
      eyebrow="Task detail"
      title={task.title}
      description={task.description}
      tags={[task.status, task.priority]}
      backHref={`/campaigns/${campaignId}/tasks` as Route}
      backLabel="Back to Tasks"
    >
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Task details</CardTitle>
                <Badge className={
                  task.status === "done" ? "bg-green-100 text-green-700" :
                  task.status === "in_progress" ? "bg-blue-100 text-blue-700" :
                  "bg-[var(--muted)]"
                }>
                  {task.status.replace("_", " ")}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-[var(--muted-foreground)]">{task.description}</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-[var(--muted-foreground)]">Assignee</p>
                  <p className="font-medium">{task.assignee}</p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Due date</p>
                  <p className="font-medium">{task.dueDate}</p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Priority</p>
                  <Badge variant="outline" className={
                    task.priority === "high" ? "text-red-600 border-red-200" :
                    task.priority === "medium" ? "text-amber-600 border-amber-200" : "text-[var(--muted-foreground)]"
                  }>{task.priority}</Badge>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Move type</p>
                  <p className="font-medium capitalize">{task.moveType}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Activity log</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { actor: "Patel", action: "changed status to In Progress", time: "2 hours ago" },
                  { actor: "Strategist", action: "assigned to Patel", time: "1 day ago" },
                  { actor: "Ogilvy", action: "changed status to To Do", time: "2 days ago" },
                ].map((entry, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--muted)] text-xs font-bold">
                      {entry.actor[0]}
                    </span>
                    <div>
                      <p><span className="font-medium">{entry.actor}</span> {entry.action}</p>
                      <p className="text-xs text-[var(--muted-foreground)]">{entry.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" size="sm">Mark complete</Button>
              <Button className="w-full" size="sm" variant="secondary">Edit task</Button>
              <Button className="w-full" size="sm" variant="secondary">Reassign</Button>
              <Button className="w-full" size="sm" variant="destructive">Delete task</Button>
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50/50">
            <CardHeader>
              <CardTitle className="text-base">📝 What to implement next</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-amber-800">
              <p><strong>Backend:</strong> Wire to tasks API — create <code>tasksApi.get(id)</code>, <code>tasksApi.update(id, body)</code> endpoints.</p>
              <p><strong>Status transitions:</strong> Enforce valid status transitions (todo → in_progress → done → verified).</p>
              <p><strong>Comments:</strong> Threaded comment system on tasks for team communication.</p>
              <p><strong>Attachments:</strong> Allow attaching files (briefs, creative assets) to tasks.</p>
              <p><strong>Notifications:</strong> Send nudges when tasks are assigned or reach due date.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </RouteShell>
  );
}
