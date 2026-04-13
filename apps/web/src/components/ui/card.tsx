import type * as React from "react";
import { cn } from "@/lib/cn";

export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>): React.ReactElement {
  return (
    <div
      className={cn("rounded-[24px] border border-[var(--border)] bg-[var(--card)]/90 shadow-sm", className)}
      {...props}
    />
  );
}

export function CardHeader({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>): React.ReactElement {
  return <div className={cn("space-y-1 px-6 pt-6", className)} {...props} />;
}

export function CardTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>): React.ReactElement {
  return <h3 className={cn("text-lg font-semibold", className)} {...props} />;
}

export function CardContent({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>): React.ReactElement {
  return <div className={cn("px-6 pb-6 pt-3", className)} {...props} />;
}
