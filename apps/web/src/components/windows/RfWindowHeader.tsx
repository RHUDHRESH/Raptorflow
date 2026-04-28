"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface RfWindowHeaderProps {
  eyebrow?: string;
  title?: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

export function RfWindowHeader({
  eyebrow,
  title,
  description,
  actions,
  className,
}: RfWindowHeaderProps) {
  return (
    <div
      className={cn(
        "px-6 pt-5 pb-0 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3",
        className,
      )}
    >
      <div className="flex-1 min-w-0">
        {eyebrow && <span className="eyebrow block mb-1.5">{eyebrow}</span>}
        {title && <h3 className="h3">{title}</h3>}
        {description && <p className="body-muted mt-1">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </div>
  );
}
