"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import type { Route } from "next";
import { useCreateCampaign } from "@/hooks/use-campaigns";
import { RouteShell } from "@/components/layout/route-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const CHANNEL_OPTIONS = [
  "LinkedIn",
  "Twitter",
  "Email",
  "Blog",
  "Webinar",
  "Podcast",
  "YouTube",
  "Instagram",
  "TikTok",
  "Reddit",
  "SEO",
  "PPC",
];

export default function NewCampaignPage(): React.ReactElement {
  const router = useRouter();
  const createCampaign = useCreateCampaign();

  const [name, setName] = React.useState("");
  const [goal, setGoal] = React.useState("");
  const [timeline, setTimeline] = React.useState("");
  const [channels, setChannels] = React.useState<string[]>([]);

  const toggleChannel = (ch: string) => {
    setChannels((prev) => (prev.includes(ch) ? prev.filter((c) => c !== ch) : [...prev, ch]));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    createCampaign.mutate(
      { name, goal: goal || undefined, timeline: timeline || undefined, channels },
      {
        onSuccess: (campaign) => {
          router.push(`/campaigns/${campaign.campaignId}` as Route);
        },
      },
    );
  };

  return (
    <RouteShell
      eyebrow="Campaigns"
      title="New campaign"
      description="Create a new marketing campaign with goal, timeline, and channel setup."
      tags={["campaigns", "create"]}
      backHref="/campaigns"
      backLabel="Back to Campaigns"
    >
      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="text-sm font-medium">Campaign name *</label>
              <input
                type="text"
                className="mt-1 w-full rounded border border-[var(--border)] bg-white px-3 py-2 text-sm"
                placeholder="Q2 LinkedIn awareness push"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">Primary goal</label>
              <input
                type="text"
                className="mt-1 w-full rounded border border-[var(--border)] bg-white px-3 py-2 text-sm"
                placeholder="Drive 500 qualified leads by end of Q2"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Timeline</label>
              <input
                type="text"
                className="mt-1 w-full rounded border border-[var(--border)] bg-white px-3 py-2 text-sm"
                placeholder="Apr 1 – Jun 30, 2025"
                value={timeline}
                onChange={(e) => setTimeline(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Channels</label>
              <div className="mt-2 flex flex-wrap gap-2">
                {CHANNEL_OPTIONS.map((ch) => (
                  <button
                    key={ch}
                    type="button"
                    onClick={() => toggleChannel(ch)}
                    className={[
                      "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                      channels.includes(ch)
                        ? "border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]"
                        : "border-[var(--border)] bg-white text-[var(--foreground)] hover:bg-[var(--muted)]",
                    ].join(" ")}
                  >
                    {ch}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={createCampaign.isPending || !name.trim()}>
                {createCampaign.isPending ? "Creating..." : "Create campaign"}
              </Button>
              <Button type="button" variant="ghost" onClick={() => router.back()}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
