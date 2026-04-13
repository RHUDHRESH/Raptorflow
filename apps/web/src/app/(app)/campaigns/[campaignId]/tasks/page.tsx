"use client";

import * as React from "react";
import type { Route } from "next";
import { useCallback, useState } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/cn";

const COLUMNS = [
  { id: "backlog", label: "Backlog", color: "var(--muted-foreground)" },
  { id: "in_progress", label: "In Progress", color: "var(--accent)" },
  { id: "review", label: "Review", color: "var(--primary)" },
  { id: "completed", label: "Done", color: "#22c55e" },
] as const;

type TaskStatus = "backlog" | "in_progress" | "review" | "completed";

interface Task {
  id: string;
  title: string;
  priority: "high" | "medium" | "low";
  assignee: string;
  dueDate: string;
  moveType: string;
  status?: TaskStatus;
}

interface Column {
  id: TaskStatus;
  label: string;
  color: string;
  tasks: Task[];
}

const INITIAL_TASKS: Task[] = [
  { id: "t1", title: "Draft LinkedIn awareness post", priority: "high", assignee: "Ogilvy", dueDate: "2025-04-15", moveType: "awareness" },
  { id: "t2", title: "Set up conversion tracking", priority: "high", assignee: "Patel", dueDate: "2025-04-14", moveType: "conversion" },
  { id: "t3", title: "Write email sequence — awareness", priority: "medium", assignee: "Ogilvy", dueDate: "2025-04-18", moveType: "awareness" },
  { id: "t4", title: "Design newsletter template", priority: "low", assignee: "Sharp", dueDate: "2025-04-20", moveType: "consideration" },
  { id: "t5", title: "Review competitor ad creatives", priority: "medium", assignee: "Sharp", dueDate: "2025-04-13", moveType: "consideration" },
  { id: "t6", title: "Publish blog post on campaign strategy", priority: "high", assignee: "Ogilvy", dueDate: "2025-04-16", moveType: "consideration" },
  { id: "t7", title: "Finalize webinar topic", priority: "medium", assignee: "Cialdini", dueDate: "2025-04-12", moveType: "launch" },
  { id: "t8", title: "QA all copy assets", priority: "low", assignee: "QA Director", dueDate: "2025-04-22", moveType: "conversion" },
];

const MOVE_TYPE_TO_STATUS: Record<string, TaskStatus> = {
  awareness: "backlog",
  consideration: "in_progress",
  conversion: "review",
  launch: "completed",
};

function taskStatus(task: Task): TaskStatus {
  return task.status ?? MOVE_TYPE_TO_STATUS[task.moveType] ?? "backlog";
}

function buildColumns(tasks: Task[]): Column[] {
  return COLUMNS.map((col) => ({
    ...col,
    tasks: tasks.filter((t) => taskStatus(t) === col.id),
  }));
}

function getPriorityColor(priority: Task["priority"]) {
  switch (priority) {
    case "high": return "text-red-600 bg-red-50 border-red-200";
    case "medium": return "text-amber-600 bg-amber-50 border-amber-200";
    case "low": return "text-green-600 bg-green-50 border-green-200";
  }
}

interface DragState {
  taskId: string | null;
  sourceCol: TaskStatus | null;
}

export default function CampaignTasksPage({
  params
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const resolvedParams = React.use(params);
  const { campaignId } = resolvedParams;

  const [columns, setColumns] = useState<Column[]>(() => buildColumns(INITIAL_TASKS));

  const [drag, setDrag] = useState<DragState>({ taskId: null, sourceCol: null });
  const [dragOver, setDragOver] = useState<TaskStatus | null>(null);

  const handleDragStart = useCallback((taskId: string, colId: TaskStatus) => {
    setDrag({ taskId, sourceCol: colId });
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent, colId: TaskStatus) => {
    e.preventDefault();
    setDragOver(colId);
  }, []);

  const handleDrop = useCallback((targetColId: TaskStatus) => {
    if (!drag.taskId || !drag.sourceCol) return;
    if (drag.sourceCol === targetColId) return;

    setColumns((prev) => {
      const next = prev.map((col) => ({ ...col, tasks: [...col.tasks] }));
      const srcCol = next.find((c) => c.id === drag.sourceCol)!;
      const tgtCol = next.find((c) => c.id === targetColId)!;
      const taskIdx = srcCol.tasks.findIndex((t) => t.id === drag.taskId);
      if (taskIdx === -1) return prev;
      const [task] = srcCol.tasks.splice(taskIdx, 1);
      tgtCol.tasks.push(task);
      return next;
    });

    setDrag({ taskId: null, sourceCol: null });
    setDragOver(null);
  }, [drag]);

  const handleDragEnd = useCallback(() => {
    setDrag({ taskId: null, sourceCol: null });
    setDragOver(null);
  }, []);

  const moveTask = useCallback((taskId: string, fromCol: TaskStatus, toCol: TaskStatus) => {
    setColumns((prev) => {
      const next = prev.map((col) => ({ ...col, tasks: [...col.tasks] }));
      const srcCol = next.find((c) => c.id === fromCol)!;
      const tgtCol = next.find((c) => c.id === toCol)!;
      const taskIdx = srcCol.tasks.findIndex((t) => t.id === taskId);
      if (taskIdx === -1) return prev;
      const [task] = srcCol.tasks.splice(taskIdx, 1);
      tgtCol.tasks.push(task);
      return next;
    });
  }, []);

  const campaignRoute = `/campaigns/${campaignId}` as Route;
  const totalTasks = columns.reduce((sum, col) => sum + col.tasks.length, 0);

  return (
    <RouteShell
      eyebrow="Tasks"
      title="Task Board"
      description={`${totalTasks} tasks across ${columns.length} stages for campaign ${campaignId}. Drag tasks between columns to update their status.`}
      tags={["kanban", "drag-drop", "campaign"]}
      backHref={campaignRoute}
      backLabel="Back to Campaign"
    >
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {columns.map((col) => (
            <div key={col.id} className="flex items-center gap-2 text-sm">
              <div className="h-2 w-2 rounded-full" style={{ backgroundColor: col.color }} />
              <span className="text-[var(--muted-foreground)]">
                {col.label}: <strong>{col.tasks.length}</strong>
              </span>
            </div>
          ))}
        </div>
        <Button size="sm" variant="secondary">
          + Add task
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {columns.map((col) => (
          <div
            key={col.id}
            className={cn(
              "flex flex-col gap-3 rounded-2xl border-2 border-dashed p-4 transition-colors",
              dragOver === col.id ? "border-[var(--primary)] bg-[var(--primary)]/5" : "border-[var(--border)] bg-white/40"
            )}
            onDragOver={(e) => handleDragOver(e, col.id)}
            onDragLeave={() => setDragOver(null)}
            onDrop={() => handleDrop(col.id)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full" style={{ backgroundColor: col.color }} />
                <h3 className="font-semibold">{col.label}</h3>
              </div>
              <Badge variant="secondary">{col.tasks.length}</Badge>
            </div>

            <div className="flex flex-col gap-3">
              {col.tasks.map((task) => (
                <Card
                  key={task.id}
                  draggable
                  onDragStart={() => handleDragStart(task.id, col.id)}
                  onDragEnd={handleDragEnd}
                  className={cn(
                    "cursor-grab select-none transition-shadow hover:shadow-md",
                    drag.taskId === task.id ? "opacity-40" : ""
                  )}
                >
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-medium leading-snug">{task.title}</p>
                      </div>
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className={cn("rounded-full border px-2 py-0.5 text-xs font-medium", getPriorityColor(task.priority))}>
                          {task.priority}
                        </span>
                        <Badge variant="outline" className="text-xs">{task.moveType}</Badge>
                      </div>
                      <div className="flex items-center justify-between text-xs text-[var(--muted-foreground)]">
                        <span>{task.assignee}</span>
                        <span>{task.dueDate}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {col.tasks.length === 0 && (
              <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-[var(--border)] py-8 text-sm text-[var(--muted-foreground)]">
                Drop here
              </div>
            )}
          </div>
        ))}
      </div>
    </RouteShell>
  );
}
