import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "flex h-11 w-full rounded-md px-4 py-2 text-sm transition-all duration-200",
        "bg-[var(--paper)] text-[var(--ink)]",
        "border border-[var(--border)]",
        "placeholder:text-[var(--ink-muted)]",
        "focus:outline-none focus:border-[var(--ink)] focus:ring-1 focus:ring-[var(--ink)]",
        "hover:border-[var(--ink-secondary)]",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "file:border-0 file:bg-transparent file:text-sm file:font-medium",
        className
      )}
      {...props}
    />
  )
}

export { Input }
