"use client";

import * as React from "react";
import { cn } from "@/lib/cn";
import { RfWindow } from "@/components/windows/RfWindow";

interface AppPageSectionProps {
  title?: string;
  eyebrow?: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "quiet" | "highlight" | "danger";
}

export function AppPageSection({
  title,
  eyebrow,
  description,
  actions,
  children,
  className,
  variant = "default",
}: AppPageSectionProps) {
  return (
    <RfWindow
      title={title}
      eyebrow={eyebrow}
      description={description}
      actions={actions}
      variant={variant}
      className={cn("mb-6", className)}
    >
      {children}
    </RfWindow>
  );
}
