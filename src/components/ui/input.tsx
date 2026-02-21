import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "flex h-11 w-full rounded-[var(--radius-sm)] px-4 py-3 text-[16px] transition-all duration-200 ease-out",
        "bg-[var(--bg-surface)] text-[var(--ink-1)] font-sans",
        "border border-[var(--border-2)]",
        "placeholder:text-[var(--ink-3)]",
        "focus:outline-none focus:border-[var(--rf-charcoal)] focus:ring-2 focus:ring-[var(--focus-outer)]",
        "hover:border-[var(--border-1)]",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "file:border-0 file:bg-transparent file:text-sm file:font-medium",
        className
      )}
      {...props}
    />
  )
}

export { Input }
