import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "flex h-12 w-full rounded-[var(--radius)] px-5 py-3 text-[15px] transition-all duration-300",
        "bg-white/70 backdrop-blur-sm",
        "border border-[var(--warm-200)]",
        "placeholder:text-[var(--warm-400)]",
        "focus:outline-none focus:border-[var(--rf-coral)]/40 focus:bg-white focus:shadow-[0_0_0_4px_rgba(249,112,102,0.08)]",
        "hover:border-[var(--warm-300)] hover:bg-white/90",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "file:border-0 file:bg-transparent file:text-sm file:font-medium",
        className
      )}
      {...props}
    />
  )
}

export { Input }
