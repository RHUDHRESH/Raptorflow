import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SectionProps {
  children: ReactNode;
  className?: string;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "full";
  id?: string;
}

export function Section({
  children,
  className = "",
  maxWidth = "2xl",
  id,
}: SectionProps) {
  const maxWidthClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    full: "max-w-full",
  };

  return (
    <section
      id={id}
      className={cn(
        "mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-24",
        maxWidthClasses[maxWidth],
        className
      )}
    >
      {children}
    </section>
  );
}

