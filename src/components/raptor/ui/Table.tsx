"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";

export interface Column<T> {
  key: string;
  header: string;
  width?: string;
  align?: "left" | "right" | "center";
  render?: (row: T) => React.ReactNode;
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  stickyHeader?: boolean;
  zebra?: boolean;
}

export function Table<T extends object>({
  data,
  columns,
  stickyHeader = false,
  zebra = false,
}: TableProps<T>) {
  const rowRefs = useRef<(HTMLTableRowElement | null)[]>([]);

  const handleMouseEnter = (index: number) => {
    const row = rowRefs.current[index];
    if (row) {
      gsap.to(row, {
        backgroundColor: "var(--state-hover)",
        duration: 0.15,
        ease: "power2.out",
      });
    }
  };

  const handleMouseLeave = (index: number, isZebra: boolean, rowIndex: number) => {
    const row = rowRefs.current[index];
    if (row) {
      const bgColor = isZebra && rowIndex % 2 === 1 ? "var(--bg-surface)" : "transparent";
      gsap.to(row, {
        backgroundColor: bgColor,
        duration: 0.15,
        ease: "power2.out",
      });
    }
  };

  const getAlignClass = (align?: string) => {
    switch (align) {
      case "right":
        return "text-right";
      case "center":
        return "text-center";
      default:
        return "text-left";
    }
  };

  const isIdColumn = (key: string) => {
    return key.toLowerCase().includes("id") || key === "id";
  };

  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr
            className={`
              border-b border-[var(--border-1)]
              ${stickyHeader ? "sticky top-0 bg-[var(--bg-surface)] z-10" : ""}
            `}
          >
            {columns.map((column) => (
              <th
                key={column.key}
                style={{ width: column.width }}
                className={`
                  py-3 px-4 text-[12px] font-semibold uppercase tracking-wide
                  text-[var(--ink-3)] font-['DM_Sans',system-ui,sans-serif]
                  ${getAlignClass(column.align)}
                `}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => {
            const isZebraRow = zebra && rowIndex % 2 === 1;
            const refIndex = rowIndex;

            return (
              <tr
                key={rowIndex}
                ref={(el) => {
                  rowRefs.current[refIndex] = el;
                }}
                className={`
                  border-b border-[var(--border-1)] transition-colors
                  ${isZebraRow ? "bg-[var(--bg-surface)]" : "bg-transparent"}
                `}
                onMouseEnter={() => handleMouseEnter(refIndex)}
                onMouseLeave={() => handleMouseLeave(refIndex, zebra || false, rowIndex)}
              >
                {columns.map((column) => {
                  const cellValue = row[column.key as keyof T] as unknown;
                  const isMono = isIdColumn(column.key) || column.align === "right";

                  return (
                    <td
                      key={column.key}
                      className={`
                        py-3 px-4 text-[14px]
                        ${getAlignClass(column.align)}
                        ${isMono ? "font-['JetBrains_Mono',monospace]" : "font-['DM_Sans',system-ui,sans-serif]"}
                        ${isIdColumn(column.key) ? "text-[var(--ink-2)]" : "text-[var(--ink-1)]"}
                      `}
                    >
                      {column.render
                        ? column.render(row)
                        : (cellValue as React.ReactNode)}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
