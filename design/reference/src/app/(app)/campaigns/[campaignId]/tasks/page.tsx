"use client";

import * as React from "react";
import type { Route } from "next";
import { useCallback, useState } from "react";
import Link from "next/link";
import { ArrowLeftIcon, PlusIcon, CheckIcon } from "@radix-ui/react-icons";
import { cn } from "@/lib/cn";
import { AGENTS } from "@/lib/agents";
import { AgentPortrait } from "@/components/ui/agent-portrait";

/* ─── Priority config ───────────────────────────────────────────── */
const PRIORITY_CONFIG = {
  high:   { label: "HIGH",   color: "var(--signal-red)",   bg: "rgba(220,38,38,0.07)"   },
  medium: { label: "MED",    color: "var(--amber-war)",    bg: "rgba(196,128,30,0.07)"  },
  low:    { label: "LOW",    color: "var(--leaf-confirm)", bg: "rgba(34,197,94,0.07)"   },
} as const;

/* ─── Column config ─────────────────────────────────────────────── */
const COLUMNS = [
  { id: "backlog",     label: "BACKLOG",     accentColor: "var(--border)" },
  { id: "in_progress", label: "IN PROGRESS", accentColor: "var(--indigo-muse)" },
  { id: "review",      label: "REVIEW",      accentColor: "var(--amber-war)" },
  { id: "completed",   label: "DONE",        accentColor: "var(--leaf-confirm)" },
] as const;

type TaskStatus = "backlog" | "in_progress" | "review" | "completed";

interface Task {
  id: string;
  title: string;
  priority: "high" | "medium" | "low";
  assignee: string;
  agentKey?: string;
  dueDate: string;
  moveType: string;
  status?: TaskStatus;
}

interface Column {
  id: TaskStatus;
  label: string;
  accentColor: string;
  tasks: Task[];
}

const AGENT_NAME_MAP: Record<string, string> = {
  "Ogilvy": "ogilvy",
  "Patel":  "patel",
  "Sharp":  "sharp",
  "Cialdini": "cialdini",
};

const INITIAL_TASKS: Task[] = [
  { id: "t1", title: "Draft LinkedIn awareness post",       priority: "high",   assignee: "Ogilvy",   agentKey: "ogilvy",   dueDate: "Apr 15", moveType: "awareness" },
  { id: "t2", title: "Set up conversion tracking",          priority: "high",   assignee: "Patel",    agentKey: "patel",    dueDate: "Apr 14", moveType: "conversion", status: "completed" },
  { id: "t3", title: "Write email sequence — awareness",    priority: "medium", assignee: "Ogilvy",   agentKey: "ogilvy",   dueDate: "Apr 18", moveType: "awareness", status: "in_progress" },
  { id: "t4", title: "Design newsletter template",          priority: "low",    assignee: "Sharp",    agentKey: undefined,  dueDate: "Apr 20", moveType: "consideration" },
  { id: "t5", title: "Review competitor ad creatives",      priority: "medium", assignee: "Sharp",    agentKey: undefined,  dueDate: "Apr 13", moveType: "consideration", status: "review" },
  { id: "t6", title: "Publish blog post on strategy",       priority: "high",   assignee: "Ogilvy",   agentKey: "ogilvy",   dueDate: "Apr 16", moveType: "consideration", status: "in_progress" },
  { id: "t7", title: "Finalize webinar topic",              priority: "medium", assignee: "Cialdini", agentKey: "cialdini", dueDate: "Apr 12", moveType: "launch", status: "completed" },
  { id: "t8", title: "QA all copy assets",                  priority: "low",    assignee: "QA",       agentKey: undefined,  dueDate: "Apr 22", moveType: "conversion" },
];

const MOVE_TYPE_TO_STATUS: Record<string, TaskStatus> = {
  awareness:     "backlog",
  consideration: "in_progress",
  conversion:    "review",
  launch:        "completed",
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

/* ─── Task Card ─────────────────────────────────────────────────── */
function TaskCard({
  task,
  isDragging,
  onDragStart,
  onDragEnd,
}: {
  task: Task;
  isDragging: boolean;
  onDragStart: () => void;
  onDragEnd: () => void;
}): React.ReactElement {
  const prio   = PRIORITY_CONFIG[task.priority];
  const agent  = task.agentKey ? AGENTS.find((a) => a.key === task.agentKey) : undefined;
  const isOver = new Date(task.dueDate) < new Date() && taskStatus(task) !== "completed";

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      className={cn(
        "border border-[var(--border)] p-4 cursor-grab select-none transition-all hover:border-[var(--foreground)]",
        isDragging ? "opacity-30" : "opacity-100"
      )}
      style={{ background: "var(--background)" }}
    >
      {/* Priority + move type */}
      <div className="flex items-center gap-2 mb-3">
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 8,
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.12em",
            border: `1px solid ${prio.color}`,
            color: prio.color,
            background: prio.bg,
            padding: "2px 5px",
          }}
        >
          {prio.label}
        </span>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 8,
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            color: "var(--muted-foreground)",
          }}
        >
          {task.moveType}
        </span>
      </div>

      {/* Title */}
      <p
        style={{
          fontFamily: "'Inter', sans-serif",
          fontSize: 12,
          fontWeight: 500,
          lineHeight: 1.5,
          color: "var(--foreground)",
          marginBottom: 12,
        }}
      >
        {task.title}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {agent ? (
            <AgentPortrait agent={agent} size={18} />
          ) : (
            <div
              className="flex h-[18px] w-[18px] items-center justify-center"
              style={{ background: "var(--muted)", fontFamily: "'JetBrains Mono', monospace", fontSize: 7, color: "var(--muted-foreground)" }}
            >
              {task.assignee.slice(0, 2).toUpperCase()}
            </div>
          )}
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, color: "var(--muted-foreground)" }}>
            {task.assignee}
          </span>
        </div>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 8,
            color: isOver ? "var(--signal-red)" : "var(--muted-foreground)",
            textDecoration: isOver ? "underline" : "none",
          }}
        >
          {task.dueDate}
        </span>
      </div>
    </div>
  );
}

/* ─── Kanban Column ─────────────────────────────────────────────── */
function KanbanColumn({
  column,
  draggingId,
  onDragOver,
  onDrop,
  onDragStart,
  onDragEnd,
}: {
  column: Column;
  draggingId: string | null;
  onDragOver: (e: React.DragEvent) => void;
  onDrop: () => void;
  onDragStart: (id: string) => void;
  onDragEnd: () => void;
}): React.ReactElement {
  const [isOver, setIsOver] = useState(false);

  return (
    <div
      className="flex flex-col min-w-[260px] flex-1"
      onDragOver={(e) => { e.preventDefault(); setIsOver(true); onDragOver(e); }}
      onDragLeave={() => setIsOver(false)}
      onDrop={() => { setIsOver(false); onDrop(); }}
    >
      {/* Column Header */}
      <div
        className="flex items-center justify-between px-4 py-3 border-t-2 border-x border-[var(--border)] mb-0"
        style={{ borderTopColor: column.accentColor, background: "var(--card)" }}
      >
        <div className="flex items-center gap-2">
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.18em",
              color: column.accentColor === "var(--border)" ? "var(--muted-foreground)" : column.accentColor,
            }}
          >
            {column.label}
          </span>
        </div>
        <span
          style={{
            fontFamily: "'DM Serif Display', serif",
            fontSize: 20,
            color: "var(--foreground)",
            lineHeight: 1,
          }}
        >
          {column.tasks.length}
        </span>
      </div>

      {/* Task stack */}
      <div
        className={cn(
          "flex flex-col gap-0 border border-t-0 border-[var(--border)] min-h-[320px] transition-all",
          isOver ? "bg-[var(--accent)]" : "bg-[var(--background)]"
        )}
      >
        {column.tasks.map((task) => (
          <div key={task.id} className="border-b border-[var(--border)] last:border-0">
            <TaskCard
              task={task}
              isDragging={draggingId === task.id}
              onDragStart={() => onDragStart(task.id)}
              onDragEnd={onDragEnd}
            />
          </div>
        ))}

        {column.tasks.length === 0 && (
          <div
            className="flex flex-1 items-center justify-center py-12"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              textTransform: "uppercase",
              letterSpacing: "0.16em",
              color: "var(--muted-foreground)",
            }}
          >
            {isOver ? "Drop here" : "Empty"}
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Main Tasks Page ───────────────────────────────────────────── */
export default function CampaignTasksPage({
  params,
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const { campaignId } = React.use(params);
  const [columns, setColumns] = useState<Column[]>(() => buildColumns(INITIAL_TASKS));
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [sourceColId, setSourceColId] = useState<TaskStatus | null>(null);
  const [targetColId, setTargetColId] = useState<TaskStatus | null>(null);

  const totalTasks = columns.reduce((s, c) => s + c.tasks.length, 0);
  const doneCount  = columns.find((c) => c.id === "completed")?.tasks.length ?? 0;
  const pct        = totalTasks > 0 ? Math.round((doneCount / totalTasks) * 100) : 0;

  const handleDragStart = useCallback((taskId: string, colId: TaskStatus) => {
    setDraggingId(taskId);
    setSourceColId(colId);
  }, []);

  const handleDrop = useCallback((colId: TaskStatus) => {
    if (!draggingId || !sourceColId || sourceColId === colId) {
      setDraggingId(null); setSourceColId(null); return;
    }
    setColumns((prev) => {
      const next = prev.map((c) => ({ ...c, tasks: [...c.tasks] }));
      const src  = next.find((c) => c.id === sourceColId)!;
      const tgt  = next.find((c) => c.id === colId)!;
      const idx  = src.tasks.findIndex((t) => t.id === draggingId);
      if (idx === -1) return prev;
      const [task] = src.tasks.splice(idx, 1);
      tgt.tasks.push(task);
      return next;
    });
    setDraggingId(null); setSourceColId(null);
  }, [draggingId, sourceColId]);

  return (
    <div className="flex flex-col gap-8 py-2">

      {/* ── Back ─────────────────────────────────────────── */}
      <Link
        href={`/campaigns/${campaignId}` as Route}
        className="flex w-fit items-center gap-2 hover:underline"
        style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)" }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Campaign Hub
      </Link>

      {/* ── Header ───────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)", marginBottom: 8 }}>
            Campaign Task Board
          </p>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            Tasks
          </h1>
          <p className="mt-2" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.14em", color: "var(--muted-foreground)" }}>
            {doneCount}/{totalTasks} complete
          </p>
        </div>

        <div className="flex items-center gap-6 shrink-0">
          {/* Overall completion */}
          <div className="text-right">
            <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: "var(--foreground)", lineHeight: 1 }}>{pct}%</p>
            <div style={{ height: 2, width: 80, background: "var(--muted)", marginTop: 4 }}>
              <div style={{ height: "100%", width: `${pct}%`, background: "var(--leaf-confirm)", transition: "width 0.6s" }} />
            </div>
          </div>

          <button
            className="flex h-10 items-center gap-2 px-4 hover:opacity-80 transition-opacity"
            style={{ background: "var(--foreground)", color: "var(--background)", fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em" }}
          >
            <PlusIcon className="h-3.5 w-3.5" />
            Add Task
          </button>
        </div>
      </header>

      {/* ── Kanban Board ─────────────────────────────────── */}
      <div className="flex gap-0 overflow-x-auto pb-4">
        {columns.map((col) => (
          <KanbanColumn
            key={col.id}
            column={col}
            draggingId={draggingId}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => handleDrop(col.id)}
            onDragStart={(taskId) => handleDragStart(taskId, col.id)}
            onDragEnd={() => setDraggingId(null)}
          />
        ))}
      </div>

      {/* ── Legend ───────────────────────────────────────── */}
      <div className="flex items-center gap-4 border-t border-[var(--border)] pt-4">
        <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.14em", color: "var(--muted-foreground)" }}>
          Priority:
        </p>
        {Object.entries(PRIORITY_CONFIG).map(([key, conf]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div className="h-2 w-2" style={{ background: conf.color }} />
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--muted-foreground)" }}>
              {conf.label}
            </span>
          </div>
        ))}
        <p className="ml-auto" style={{ fontFamily: "'JetBrains Mono', monospace', fontSize: 8", fontSize: 8, color: "var(--muted-foreground)" }}>
          Drag cards between columns to update status
        </p>
      </div>
    </div>
  );
}
