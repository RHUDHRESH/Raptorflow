"use client";

import * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { useRipples, useCreateRipple, useDeleteRipple, useRealizeRipple, useRunDecay } from "@/hooks/use-prl";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/cn";

const PROTECTION_COLORS: Record<string, string> = {
  protected: "text-blue-700 bg-blue-50 border-blue-200",
  important: "text-amber-700 bg-amber-50 border-amber-200",
  normal: "text-[var(--muted-foreground)] bg-[var(--muted)] border-[var(--border)]",
  disposable: "text-red-600 bg-red-50 border-red-200",
};

function ConfidenceBar({ confidence }: { confidence: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-[var(--muted)]">
        <div
          className="h-full rounded-full bg-[var(--primary)]"
          style={{ width: `${confidence * 100}%` }}
        />
      </div>
      <span className="text-xs text-[var(--muted-foreground)]">{Math.round(confidence * 100)}%</span>
    </div>
  );
}

export default function RipplesPage(): React.ReactElement {
  const { data: ripples, isLoading, error } = useRipples();
  const createRipple = useCreateRipple();
  const deleteRipple = useDeleteRipple();
  const realizeRipple = useRealizeRipple();
  const runDecay = useRunDecay();

  const [showCreateForm, setShowCreateForm] = React.useState(false);
  const [newClaim, setNewClaim] = React.useState("");
  const [newReasoning, setNewReasoning] = React.useState("");

  const handleCreate = () => {
    if (!newClaim.trim()) return;
    createRipple.mutate(
      { coreClaim: newClaim, keyReasoning: newReasoning },
      {
        onSuccess: () => {
          setNewClaim("");
          setNewReasoning("");
          setShowCreateForm(false);
        },
      }
    );
  };

  return (
    <RouteShell
      eyebrow="PRL"
      title="Ripples"
      description="Propagated Rationality Log — track claims, reasoning chains, and their confidence over time."
      tags={["prl", "ripples", "reasoning"]}
      rail={
        <Card>
          <CardHeader>
            <CardTitle>About PRL</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-[var(--muted-foreground)]">
            <p>
              Ripples capture strategic claims with confidence scores. Realized ripples propagate through the reasoning graph.
            </p>
            <div className="space-y-1">
              <p className="font-medium text-[var(--foreground)]">Protection bands</p>
              <div className="flex flex-col gap-1">
                {Object.entries(PROTECTION_COLORS).map(([band, cls]) => (
                  <span key={band} className={cn("rounded-full border px-2 py-0.5 text-xs", cls)}>
                    {band}
                  </span>
                ))}
              </div>
            </div>
            <Button size="sm" variant="ghost" className="w-full" onClick={() => runDecay.mutate()}>
              Run decay cycle
            </Button>
          </CardContent>
        </Card>
      }
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">All ripples</h2>
          <p className="text-sm text-[var(--muted-foreground)]">
            {ripples?.length ?? 0} tracked
          </p>
        </div>
        <Button size="sm" onClick={() => setShowCreateForm(true)}>
          + New ripple
        </Button>
      </div>

      {showCreateForm && (
        <Card>
          <CardContent className="space-y-3 p-4">
            <div>
              <label className="text-sm font-medium">Core claim</label>
              <textarea
                className="mt-1 w-full rounded border border-[var(--border)] bg-white p-2 text-sm"
                rows={2}
                placeholder="The claim being tracked..."
                value={newClaim}
                onChange={(e) => setNewClaim(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Key reasoning</label>
              <textarea
                className="mt-1 w-full rounded border border-[var(--border)] bg-white p-2 text-sm"
                rows={3}
                placeholder="Why this claim matters..."
                value={newReasoning}
                onChange={(e) => setNewReasoning(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={handleCreate} disabled={createRipple.isPending}>
                {createRipple.isPending ? "Creating..." : "Create ripple"}
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setShowCreateForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {isLoading && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="h-4 w-3/4 animate-pulse rounded bg-[var(--muted)]" />
                <div className="mt-3 h-3 w-full animate-pulse rounded bg-[var(--muted)]" />
                <div className="mt-2 h-3 w-2/3 animate-pulse rounded bg-[var(--muted)]" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4 text-sm text-red-700">
            Failed to load ripples: {error.message}
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && ripples?.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-3xl">🌊</p>
            <p className="mt-4 font-medium">No ripples yet</p>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              Create your first ripple to start tracking claims
            </p>
            <Button className="mt-4" size="sm" onClick={() => setShowCreateForm(true)}>
              + Create ripple
            </Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && ripples && ripples.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {ripples.map((ripple) => (
            <Card key={ripple.rippleId} className="transition-shadow hover:shadow-md">
              <CardContent className="p-6">
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium leading-snug">{ripple.coreClaim}</p>
                    <Badge
                      variant={ripple.protectionBand === "protected" ? "default" : ripple.protectionBand === "important" ? "warning" : "secondary"}
                      className="flex-shrink-0"
                    >
                      {ripple.protectionBand}
                    </Badge>
                  </div>

                  {ripple.keyReasoning && (
                    <p className="text-xs text-[var(--muted-foreground)] line-clamp-2">
                      {ripple.keyReasoning}
                    </p>
                  )}

                  <ConfidenceBar confidence={ripple.confidence} />

                  {ripple.source && (
                    <p className="text-xs text-[var(--muted-foreground)]">
                      Source: {ripple.source}
                    </p>
                  )}

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-xs text-[var(--muted-foreground)]">
                      {new Date(ripple.createdAt).toLocaleDateString()}
                    </span>
                    <div className="flex gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => realizeRipple.mutate(ripple.rippleId)}
                        title="Realize ripple"
                      >
                        ⚡
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          if (confirm("Delete this ripple?")) {
                            deleteRipple.mutate(ripple.rippleId);
                          }
                        }}
                        title="Delete ripple"
                      >
                        🗑
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </RouteShell>
  );
}
