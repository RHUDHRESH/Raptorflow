"use client";

import * as React from "react";
import { cn } from "@/lib/cn";
import { RfWindow } from "@/components/windows/RfWindow";

interface AppErrorStateProps {
  title?: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function AppErrorState({
  title = "Something went wrong",
  description = "We couldn't load this section. Try again or contact support if the problem persists.",
  action,
  className,
}: AppErrorStateProps) {
  return (
    <RfWindow variant="danger" className={cn("py-10", className)}>
      <div className="flex flex-col items-center text-center">
        <div className="w-10 h-10 rounded-full bg-[var(--destructive)]/10 flex items-center justify-center mb-4">
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            className="text-[var(--destructive)]"
          >
            <path
              d="M10 6v5M10 15.5h.01M19 10a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <h3 className="h3 mb-2 text-[var(--destructive)]">{title}</h3>
        <p className="body-muted max-w-sm mb-6">{description}</p>
        {action && <div>{action}</div>}
      </div>
    </RfWindow>
  );
}
