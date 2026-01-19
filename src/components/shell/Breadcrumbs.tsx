"use client";

import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

const routeMap: Record<string, string> = {
  dashboard: "DASHBOARD",
  foundation: "FOUNDATION",
  moves: "MOVES",
  campaigns: "CAMPAIGNS",
  muse: "MUSE",
  "daily-wins": "DAILY WINS",
  analytics: "ANALYTICS",
  blackbox: "BLACKBOX",
  settings: "SETTINGS",
  help: "HELP",
  cohorts: "COHORTS",
};

export function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname?.split("/").filter(Boolean) || [];

  return (
    <nav className="flex items-center gap-2 relative z-10 font-technical text-[10px] tracking-widest text-[var(--ink-muted)]">
      <Link 
        href="/dashboard" 
        className="hover:text-[var(--blueprint)] transition-colors uppercase"
      >
        WORKSPACE
      </Link>
      
      {segments.map((segment, index) => {
        const href = `/${segments.slice(0, index + 1).join("/")}`;
        const isLast = index === segments.length - 1;
        const label = routeMap[segment] || segment.toUpperCase();

        return (
          <React.Fragment key={href}>
            <div className="w-4 h-px bg-[var(--border)] mx-1" />
            <Link
              href={href}
              className={cn(
                "transition-colors",
                isLast 
                  ? "text-[var(--blueprint)] font-bold" 
                  : "hover:text-[var(--blueprint)]"
              )}
            >
              {label}
            </Link>
          </React.Fragment>
        );
      })}
    </nav>
  );
}
