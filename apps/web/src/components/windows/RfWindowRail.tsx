"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface RfWindowRailProps {
  children: React.ReactNode;
  className?: string;
}

export function RfWindowRail({ children, className }: RfWindowRailProps) {
  return (
    <aside className={cn("w-full lg:w-80 xl:w-96 shrink-0 paper-card p-5 h-fit", className)}>
      {children}
    </aside>
  );
}
