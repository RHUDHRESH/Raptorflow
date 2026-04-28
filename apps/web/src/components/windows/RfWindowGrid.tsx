"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface RfWindowGridProps {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4;
  className?: string;
}

const colMap: Record<number, string> = {
  1: "grid-cols-1",
  2: "grid-cols-1 sm:grid-cols-2",
  3: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3",
  4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4",
};

export function RfWindowGrid({ children, columns = 2, className }: RfWindowGridProps) {
  return <div className={cn("grid gap-4", colMap[columns], className)}>{children}</div>;
}
