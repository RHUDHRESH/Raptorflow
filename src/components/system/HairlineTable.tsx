import * as React from "react";

import { cn } from "@/lib/utils";
import { EmptyState } from "@/components/EmptyState";

export type HairlineTableColumn<T> = {
  key: string;
  header: React.ReactNode;
  width?: string;
  align?: "left" | "center" | "right";
  render?: (row: T) => React.ReactNode;
  headerClassName?: string;
  cellClassName?: string;
};

export function HairlineTable<T>({
  columns,
  data,
  loading,
  onRowClick,
  emptyTitle = "No results",
  emptyDescription = "There’s nothing to show here yet.",
  emptyAction,
  onEmptyAction,
  className,
}: {
  columns: HairlineTableColumn<T>[];
  data: T[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: string;
  onEmptyAction?: () => void;
  className?: string;
}) {
  if (loading) {
    return (
      <div className={cn("rounded-card border border-border bg-card p-10 text-center", className)}>
        <div className="mx-auto h-10 w-10 rounded-full border-2 border-primary/40 border-t-primary animate-spin" />
        <p className="mt-4 text-body-sm text-ink-400">Loading…</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className={cn("rounded-card border border-border bg-card p-6", className)}>
        <EmptyState
          title={emptyTitle}
          description={emptyDescription}
          action={emptyAction}
          onAction={onEmptyAction}
        />
      </div>
    );
  }

  return (
    <div className={cn("rounded-card border border-border bg-card overflow-hidden", className)}>
      <div className="overflow-x-auto">
        <table className="table-editorial">
          <thead>
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    col.align === "right" && "text-right",
                    col.align === "center" && "text-center",
                    col.headerClassName,
                  )}
                  style={col.width ? { width: col.width } : undefined}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={cn(onRowClick && "cursor-pointer")}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={cn(
                      col.align === "right" && "text-right",
                      col.align === "center" && "text-center",
                      col.cellClassName,
                    )}
                  >
                    {col.render ? col.render(row) : (row as any)?.[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
