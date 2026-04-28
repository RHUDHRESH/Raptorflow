"use client";

import * as React from "react";
import { cn } from "@/lib/cn";
import { RfWindow } from "@/components/windows/RfWindow";

interface AppEmptyStateProps {
  title: string;
  description: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export function AppEmptyState({ title, description, action, icon, className }: AppEmptyStateProps) {
  return (
    <RfWindow variant="quiet" className={cn("py-12", className)}>
      <div className="flex flex-col items-center text-center">
        {icon && (
          <div className="w-12 h-12 rounded-[var(--radius-lg)] bg-[var(--paper-150)] flex items-center justify-center mb-4">
            {icon}
          </div>
        )}
        <h3 className="h3 mb-2">{title}</h3>
        <p className="body-muted max-w-sm mb-6">{description}</p>
        {action && <div>{action}</div>}
      </div>
    </RfWindow>
  );
}
