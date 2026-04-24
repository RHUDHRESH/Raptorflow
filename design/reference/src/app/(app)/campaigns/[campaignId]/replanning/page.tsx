"use client";

import * as React from "react";
import type { Route } from "next";
import { useState } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/cn";

interface MoveChange {
  id: string;
  type: "added" | "removed" | "modified";
  label: string;
  original: string;
  proposed: string;
}

const MOCK_ORIGINAL_PLAN = [
  { id: "m1", moveType: "awareness", title: "Launch LinkedIn campaign", timeline: "Week 1-2", budget: 4000 },
  { id: "m2", moveType: "consideration", title: "Publish 3 blog posts on industry trends", timeline: "Week 2-4", budget: 1500 },
  { id: "m3", moveType: "conversion", title: "Run webinar with target ICP", timeline: "Week 4", budget: 2500 },
  { id: "m4", moveType: "retention", title: "Launch email nurture sequence", timeline: "Week 5-8", budget: 1000 },
];

const MOCK_PROPOSED_PLAN = [
  { id: "m1", moveType: "awareness", title: "Launch LinkedIn campaign", timeline: "Week 1-2", budget: 5000 },
  { id: "m2", moveType: "consideration", title: "Publish 5 blog posts on industry trends", timeline: "Week 2-5", budget: 2000 },
  { id: "m3", moveType: "conversion", title: "Run webinar with target ICP", timeline: "Week 5", budget: 2000 },
  { id: "m5", moveType: "awareness", title: "Competitor campaign response on Twitter/X", timeline: "Week 3", budget: 1500 },
  { id: "m4", moveType: "retention", title: "Launch email nurture sequence", timeline: "Week 6-10", budget: 800 },
];

const MOCK_CHANGES: MoveChange[] = [
  { id: "m1", type: "modified", label: "LinkedIn awareness", original: "$4,000", proposed: "$5,000 (+25%)" },
  { id: "m2", type: "modified", label: "Blog content push", original: "3 posts / Wk 2-4", proposed: "5 posts / Wk 2-5" },
  { id: "m3", type: "modified", label: "Webinar", original: "Week 4", proposed: "Week 5" },
  { id: "m5", type: "added", label: "Competitor response campaign", original: "—", proposed: "New: $1,500 / Wk 3" },
  { id: "m4", type: "modified", label: "Email nurture", original: "$1,000 / Wk 5-8", proposed: "$800 / Wk 6-10" },
];

type AcceptState = "pending" | "accepted" | "rejected";

function DiffBadge({ type }: { type: MoveChange["type"] }) {
  if (type === "added") return <Badge className="bg-green-100 text-green-700 border-green-200">Added</Badge>;
  if (type === "removed") return <Badge className="bg-red-100 text-red-700 border-red-200">Removed</Badge>;
  return <Badge className="bg-amber-100 text-amber-700 border-amber-200">Modified</Badge>;
}

export default function CampaignReplanningPage({
  params
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const resolvedParams = React.use(params);
  const { campaignId } = resolvedParams;

  const [decisions, setDecisions] = useState<Record<string, AcceptState>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [summary, setSummary] = useState("");

  const campaignRoute = `/campaigns/${campaignId}` as Route;

  const acceptDecision = (id: string) => {
    setDecisions((prev) => ({ ...prev, [id]: "accepted" }));
  };

  const rejectDecision = (id: string) => {
    setDecisions((prev) => ({ ...prev, [id]: "rejected" }));
  };

  const acceptedCount = Object.values(decisions).filter((d) => d === "accepted").length;
  const rejectedCount = Object.values(decisions).filter((d) => d === "rejected").length;
  const pendingCount = MOCK_CHANGES.length - acceptedCount - rejectedCount;

  const originalTotal = MOCK_ORIGINAL_PLAN.reduce((s, m) => s + m.budget, 0);
  const proposedTotal = MOCK_PROPOSED_PLAN.reduce((acc, m) => acc + m.budget, 0);

  return (
    <RouteShell
      eyebrow="Replanning"
      title="Campaign Replan"
      description={`Review proposed changes to campaign ${campaignId} and accept or reject each adjustment.`}
      tags={["replan", "strategy", "diff"]}
      backHref={campaignRoute}
      backLabel="Back to Campaign"
    >
      <div className="grid gap-4 xl:grid-cols-2">
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Original Plan</h2>
          <div className="space-y-3">
            {MOCK_ORIGINAL_PLAN.map((move) => (
              <Card key={move.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{move.moveType}</Badge>
                        <span className="font-medium">{move.title}</span>
                      </div>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        {move.timeline} · <span className="font-medium">${move.budget.toLocaleString()}</span>
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="flex justify-between rounded-xl border border-[var(--border)] bg-white/70 p-4 text-sm font-semibold">
            <span>Total budget</span>
            <span>${originalTotal.toLocaleString()}</span>
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Proposed Plan</h2>
          <div className="space-y-3">
            {MOCK_PROPOSED_PLAN.map((move) => {
              const change = MOCK_CHANGES.find((c) => c.id === move.id);
              return (
                <Card key={move.id} className={cn(change?.type === "added" && "border-green-300 bg-green-50/50")}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{move.moveType}</Badge>
                          <span className="font-medium">{move.title}</span>
                          {change && <DiffBadge type={change.type} />}
                        </div>
                        <p className="text-sm text-[var(--muted-foreground)]">
                          {move.timeline} · <span className="font-medium">${move.budget.toLocaleString()}</span>
                        </p>
                        {change && change.type === "modified" && (
                          <p className="mt-2 rounded-lg border border-amber-200 bg-amber-50 p-2 text-xs">
                            <span className="text-amber-700">Change: </span>
                            {change.original} → {change.proposed}
                          </p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
          <div className="flex justify-between rounded-xl border border-[var(--border)] bg-white/70 p-4 text-sm font-semibold">
            <span>Total proposed budget</span>
            <span className="text-[var(--accent)]">${proposedTotal.toLocaleString()}</span>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Decision Log</CardTitle>
            <div className="flex gap-3 text-xs">
              <span className="text-green-600">{acceptedCount} accepted</span>
              <span className="text-red-600">{rejectedCount} rejected</span>
              <span className="text-[var(--muted-foreground)]">{pendingCount} pending</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {MOCK_CHANGES.map((change) => {
            const decision = decisions[change.id] ?? "pending";
            return (
              <div key={change.id} className="space-y-3 rounded-xl border border-[var(--border)] p-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <DiffBadge type={change.type} />
                    <span className="font-medium">{change.label}</span>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant={decision === "accepted" ? "default" : "outline"}
                      onClick={() => acceptDecision(change.id)}
                      disabled={decision !== "pending"}
                    >
                      Accept
                    </Button>
                    <Button
                      size="sm"
                      variant={decision === "rejected" ? "destructive" : "outline"}
                      onClick={() => rejectDecision(change.id)}
                      disabled={decision !== "pending"}
                    >
                      Reject
                    </Button>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-1">
                    <p className="text-xs uppercase tracking-[0.16em] text-[var(--muted-foreground)]">Original</p>
                    <p className="rounded-lg bg-red-50 p-2 text-red-700">{change.original}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs uppercase tracking-[0.16em] text-[var(--muted-foreground)]">Proposed</p>
                    <p className="rounded-lg bg-green-50 p-2 text-green-700">{change.proposed}</p>
                  </div>
                </div>
                {decision !== "pending" && (
                  <div className={cn(
                    "rounded-lg p-3 text-sm font-medium",
                    decision === "accepted" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                  )}>
                    {decision === "accepted" ? "Accepted — change will be applied" : "Rejected — original plan retained"}
                  </div>
                )}
                <textarea
                  placeholder="Add a note for this decision..."
                  value={notes[change.id] ?? ""}
                  onChange={(e) => setNotes((prev) => ({ ...prev, [change.id]: e.target.value }))}
                  className="w-full rounded-lg border border-[var(--border)] bg-white p-3 text-sm placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
                  rows={2}
                />
              </div>
            );
          })}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Replan Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            placeholder="Describe the rationale for this replan. This will be logged with the campaign audit trail."
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            className="w-full rounded-lg border border-[var(--border)] bg-white p-4 text-sm placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
            rows={4}
          />
          <div className="flex items-center justify-between">
            <p className="text-sm text-[var(--muted-foreground)]">
              {acceptedCount} changes accepted, {rejectedCount} changes rejected, {pendingCount} pending
            </p>
            <div className="flex gap-3">
              <Button variant="secondary">Save draft</Button>
              <Button>Apply accepted changes</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
