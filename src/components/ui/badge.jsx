import * as React from "react"
import { cva } from "class-variance-authority";

import { cn } from "@/lib/utils"

/**
 * Badge Component — RaptorFlow Design System
 * 
 * Variants:
 * - default: Primary amber accent
 * - secondary: Muted/subtle
 * - outline: Bordered, transparent
 * - success/warning/error/info: Status indicators (harmonized, not neon)
 */
const badgeVariants = cva(
  [
    "inline-flex items-center rounded-md border px-2 py-0.5",
    "text-xs font-medium",
    "transition-colors duration-150",
    "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  ].join(" "),
  {
    variants: {
      variant: {
        // Default — Primary amber
        default: [
          "border-transparent bg-primary text-primary-foreground",
          "shadow-sm",
        ].join(" "),

        // Secondary — Muted
        secondary: [
          "border-transparent bg-secondary text-secondary-foreground",
        ].join(" "),

        // Outline — Bordered
        outline: [
          "border-border bg-transparent text-foreground",
        ].join(" "),

        // Status: Success — Harmonized evergreen
        success: [
          "border-transparent",
          "bg-success-100 text-success-700",
          "dark:bg-success-900/30 dark:text-success-400",
        ].join(" "),

        // Status: Warning — Amber/rust
        warning: [
          "border-transparent",
          "bg-amber-100 text-amber-700",
          "dark:bg-amber-900/30 dark:text-amber-400",
        ].join(" "),

        // Status: Error — Restrained crimson
        error: [
          "border-transparent",
          "bg-error-100 text-error-700",
          "dark:bg-error-900/30 dark:text-error-400",
        ].join(" "),

        // Status: Info — Steel blue
        info: [
          "border-transparent",
          "bg-info-100 text-info-700",
          "dark:bg-info-900/30 dark:text-info-400",
        ].join(" "),

        // Destructive — Alias for error
        destructive: [
          "border-transparent bg-destructive text-destructive-foreground",
          "shadow-sm",
        ].join(" "),
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant,
  ...props
}) {
  return (<div className={cn(badgeVariants({ variant }), className)} {...props} />);
}

export { Badge, badgeVariants }

