import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

/**
 * Button Component — RaptorFlow Design System
 * Governed by: Dieter Rams' 10 Rules of Good Design
 * 
 * TACTILE STATES:
 * - Hover: brightness shift + subtle shadow lift (no glow)
 * - Pressed: translateY(1px) + reduced shadow + darker fill
 * - Focus-visible: clear ring using --focus-ring (not browser blue)
 * - Disabled: lower contrast + remove shadow + cursor-not-allowed
 * 
 * Transitions: 160–200ms, standard easing
 */
const buttonVariants = cva(
  // Base styles
  [
    "inline-flex items-center justify-center gap-2 whitespace-nowrap",
    "rounded-md text-sm font-medium",
    "transition-all duration-150 ease-out",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
    "disabled:pointer-events-none disabled:opacity-50",
    "[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  ].join(" "),
  {
    variants: {
      variant: {
        // Primary CTA — Amber with ink foreground
        default: [
          "bg-primary text-primary-foreground font-semibold",
          "shadow-sm",
          "hover:brightness-110 hover:-translate-y-0.5 hover:shadow-md",
          "active:translate-y-0 active:brightness-95 active:shadow-sm",
        ].join(" "),

        primary: [
          "bg-primary text-primary-foreground font-semibold",
          "shadow-sm",
          "hover:brightness-110 hover:-translate-y-0.5 hover:shadow-md",
          "active:translate-y-0 active:brightness-95 active:shadow-sm",
        ].join(" "),

        // Secondary — Muted surface
        secondary: [
          "bg-secondary text-secondary-foreground",
          "shadow-sm",
          "hover:bg-accent hover:text-accent-foreground",
          "active:bg-muted",
        ].join(" "),

        // Outline — Bordered, transparent
        outline: [
          "border border-border bg-transparent text-foreground",
          "shadow-sm",
          "hover:bg-accent hover:text-accent-foreground hover:border-border/80",
          "active:bg-muted",
        ].join(" "),

        // Ghost — Minimal, no background
        ghost: [
          "text-muted-foreground",
          "hover:bg-accent hover:text-foreground",
          "active:bg-muted",
        ].join(" "),

        // Destructive — Error/danger
        destructive: [
          "bg-destructive text-destructive-foreground font-semibold",
          "shadow-sm",
          "hover:bg-destructive/90 hover:-translate-y-0.5",
          "active:translate-y-0 active:bg-destructive/80",
        ].join(" "),

        // Link — Text only
        link: [
          "text-primary underline-offset-4",
          "hover:underline",
        ].join(" "),
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-11 rounded-md px-6 text-base",
        xl: "h-12 rounded-lg px-8 text-base font-semibold",
        icon: "h-9 w-9",
        "icon-sm": "h-8 w-8",
        "icon-lg": "h-11 w-11",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading = false, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <Loader2 className="animate-spin" />}
        {children}
      </Comp>
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
