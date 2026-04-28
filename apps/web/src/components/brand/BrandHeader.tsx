"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface BrandHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  status?: React.ReactNode;
  actions?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function BrandHeader({
  eyebrow,
  title,
  description,
  status,
  actions,
  children,
  className,
}: BrandHeaderProps) {
  return (
    <div className={cn("mb-8", className)}>
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex-1 min-w-0">
          {eyebrow && (
            <div className="flex items-center gap-3 mb-3">
              <span className="eyebrow">{eyebrow}</span>
              <span className="h-px flex-1 bg-[var(--border)]" />
            </div>
          )}
          <h1 className="h1">{title}</h1>
          {description && <p className="body-muted mt-2 max-w-xl">{description}</p>}
        </div>
        <div className="flex items-center gap-3 shrink-0">
          {status && <div>{status}</div>}
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      </div>
      {children && <div className="mt-6">{children}</div>}
    </div>
  );
}
