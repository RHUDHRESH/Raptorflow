"use client";

import type { ReactElement } from "react";

interface CalendarItem {
  date?: string;
  week?: string;
  channel?: string;
  topic?: string;
  status?: string;
  notes?: string;
}

export interface CalendarPlanBody {
  items?: CalendarItem[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

function isCalendarItem(value: unknown): value is CalendarItem {
  return isRecord(value);
}

function isCalendarItemArray(value: unknown): value is CalendarItem[] {
  return Array.isArray(value) && value.every(isCalendarItem);
}

export function isCalendarPlanBody(body: unknown): body is CalendarPlanBody {
  return isRecord(body);
}

export function CalendarPlanRenderer({ body }: { body: unknown }): ReactElement {
  if (!isRecord(body)) {
    return (
      <pre className="mt-4 overflow-x-auto whitespace-pre-wrap text-xs text-[var(--muted-foreground)]">
        {JSON.stringify(body, null, 2)}
      </pre>
    );
  }

  const b = body as Record<string, unknown>;

  return (
    <div className="mt-4 space-y-4 text-sm">
      {isCalendarItemArray(b.items) && b.items.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr className="border-b border-[var(--border)] font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)]">
                <th className="py-2 pr-4 text-left font-normal">Date</th>
                <th className="py-2 pr-4 text-left font-normal">Week</th>
                <th className="py-2 pr-4 text-left font-normal">Channel</th>
                <th className="py-2 pr-4 text-left font-normal">Topic</th>
                <th className="py-2 pr-4 text-left font-normal">Status</th>
                <th className="py-2 text-left font-normal">Notes</th>
              </tr>
            </thead>
            <tbody>
              {b.items.map((item, i) => (
                <tr key={i} className="border-b border-[var(--border)] last:border-0">
                  <td className="py-2 pr-4 text-[var(--foreground)]">
                    {isString(item.date) ? item.date : "—"}
                  </td>
                  <td className="py-2 pr-4 text-[var(--foreground)]">
                    {isString(item.week) ? item.week : "—"}
                  </td>
                  <td className="py-2 pr-4">
                    {isString(item.channel) && (
                      <span className="inline-block rounded bg-[var(--border)] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-[var(--foreground)]">
                        {item.channel}
                      </span>
                    )}
                  </td>
                  <td className="py-2 pr-4 text-[var(--foreground)]">
                    {isString(item.topic) ? item.topic : "—"}
                  </td>
                  <td className="py-2 pr-4">
                    {isString(item.status) && (
                      <span
                        className={`inline-block rounded px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider ${
                          item.status === "published"
                            ? "bg-green-900/30 text-green-400"
                            : item.status === "draft"
                              ? "bg-yellow-900/30 text-yellow-400"
                              : item.status === "scheduled"
                                ? "bg-blue-900/30 text-blue-400"
                                : "bg-[var(--border)] text-[var(--muted-foreground)]"
                        }`}
                      >
                        {item.status}
                      </span>
                    )}
                  </td>
                  <td className="py-2 text-[var(--muted-foreground)]">
                    {isString(item.notes) ? item.notes : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-[var(--muted-foreground)] italic">No calendar items</p>
      )}
    </div>
  );
}
