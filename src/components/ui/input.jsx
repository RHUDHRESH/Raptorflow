import * as React from "react"

import { cn } from "@/lib/utils"

/**
 * Input Component — RaptorFlow Design System
 * Governed by: Dieter Rams' 10 Rules
 * 
 * TACTILE STATES:
 * - Default: calm border --border-1
 * - Focus: stronger border --border-2 + 2px ring
 * - Error: rust border + helper text (via className)
 * - Disabled: lower contrast + cursor-not-allowed
 * 
 * Transitions: 160ms standard easing
 */
const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        // Base
        "flex h-10 w-full rounded-md px-3 py-2",
        "text-sm",
        "bg-[var(--surface-3)] text-[var(--text-1)]",
        "border border-[var(--border-1)]",
        // Placeholder
        "placeholder:text-[var(--text-3)]",
        // File input
        "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-[var(--text-1)]",
        // Focus — stronger border + ring
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "focus-visible:border-[var(--border-2)]",
        // Hover — subtle
        "hover:border-[var(--border-2)]",
        // Disabled
        "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-[var(--muted)]",
        // Transition
        "transition-all duration-[160ms] ease-[cubic-bezier(0.4,0,0.2,1)]",
        className
      )}
      ref={ref}
      {...props}
    />
  );
})
Input.displayName = "Input"

export { Input }


