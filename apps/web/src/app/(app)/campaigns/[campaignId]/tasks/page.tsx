"use client";

import * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { ArrowLeftIcon } from "@radix-ui/react-icons";
import { useCampaignTasks } from "@/features/campaigns";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusPill } from "@/components/windows";

const STATUS_ORDER: Record<string, number> = {
  pending: 0,
  in_progress: 1,
  completed: 2,
  cancelled: 3,
};

export default function CampaignTasksPage({
  params,
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const { campaignId } = React.use(params);
  const { data: tasks, isLoading, error } = useCampaignTasks(campaignId);

  const taskList = tasks ?? [];
  const pendingCount = taskList.filter((t) => t.status === "pending").length;
  const inProgressCount = taskList.filter((t) => t.status === "in_progress").length;
  const completedCount = taskList.filter((t) => t.status === "completed").length;

  const grouped = React.useMemo(() => {
    const groups: Record<string, typeof taskList> = {
      pending: [],
      in_progress: [],
      completed: [],
      cancelled: [],
    };
    for (const task of taskList) {
      const key = task.status in groups ? task.status : "pending";
      groups[key].push(task);
    }
    return groups;
  }, [taskList]);

  return (
    <div className="flex flex-col gap-8 py-2">
      <Link
        href={`/campaigns/${campaignId}` as Route}
        className="flex w-fit items-center gap-2 hover:underline"
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          textTransform: "uppercase",
          letterSpacing: "0.16em",
          color: "var(--muted-foreground)",
        }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Campaign Hub
      </Link>

      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <p
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.2em",
              color: "var(--muted-foreground)",
              marginBottom: 8,
            }}
          >
            Campaign Task Board
          </p>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            Tasks
          </h1>
          <p
            className="mt-2"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "var(--muted-foreground)",
            }}
          >
            {completedCount}/{taskList.length} complete · {inProgressCount} in progress · {pendingCount} pending
          </p>
        </div>
      </header>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      ) : error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-800">
          Failed to load campaign tasks from the backend.
        </div>
      ) : taskList.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--border)] p-10 text-center">
          <p className="font-semibold">No tasks exist yet for this campaign.</p>
          <p className="mt-2 text-sm text-[var(--muted-foreground)]">
            Tasks will appear after moves are generated.
          </p>
          <div className="mt-4">
            <Button asChild variant="secondary">
              <Link href={`/campaigns/${campaignId}` as Route}>Open campaign</Link>
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {Object.entries(grouped).map(([status, statusTasks]) =>
            statusTasks.length === 0 ? null : (
              <div key={status}>
                <div className="flex items-center gap-3 mb-4">
                  <StatusPill
                    status={status.replace("_", " ")}
                    tone={
                      status === "completed"
                        ? "success"
                        : status === "in_progress"
                          ? "amber"
                          : status === "cancelled"
                            ? "danger"
                            : "neutral"
                    }
                  />
                  <span className="mono-label text-[var(--ink-500)]">
                    {statusTasks.length}
                  </span>
                </div>
                <div className="space-y-2">
                  {statusTasks.map((task) => (
                    <div
                      key={task.taskId}
                      className="flex items-center justify-between p-4 border border-[var(--border)] bg-[var(--paper-100)] hover:bg-[var(--paper-150)] transition-colors"
                    >
                      <div className="min-w-0">
                        <p className="font-medium text-[var(--ink-900)]">
                          {task.title}
                        </p>
                        {task.description && (
                          <p className="text-sm text-[var(--ink-500)]">
                            {task.description}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center gap-3 shrink-0 ml-4">
                        {task.dueAt && (
                          <span className="mono-label text-[var(--ink-500)]">
                            {new Date(task.dueAt).toLocaleDateString()}
                          </span>
                        )}
                        {task.owner && (
                          <span className="text-xs text-[var(--ink-500)]">
                            {task.owner}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}
