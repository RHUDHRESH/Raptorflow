"use client";

import * as React from "react";
import { cn } from "@/lib/cn";
import { SectionLabel } from "./landing-ui-primitives";

type LandingSectionProps = {
  id?: string;
  eyebrow?: string;
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  centered?: boolean;
  innerClassName?: string;
};

export function LandingSection({
  id,
  eyebrow,
  title,
  description,
  children,
  className,
  centered,
  innerClassName,
}: LandingSectionProps) {
  return (
    <section
      id={id}
      className={cn("relative px-6 py-24 lg:px-8 lg:py-32 overflow-hidden", className)}
    >
      <div
        className={cn(
          "relative mx-auto max-w-7xl",
          centered && "text-center",
          innerClassName
        )}
      >
        {(eyebrow || title || description) && (
          <div className={cn("mb-16 max-w-3xl", centered && "mx-auto")}>
            {eyebrow && <SectionLabel className="mb-4">{eyebrow}</SectionLabel>}
            {title && (
              <h2 className="text-4xl md:text-5xl lg:text-6xl tracking-tight font-semibold text-white leading-[1.05] mt-3">
                {title}
              </h2>
            )}
            {description && (
              <p className="mt-5 text-base md:text-lg text-zinc-400 leading-7">
                {description}
              </p>
            )}
          </div>
        )}
        {children}
      </div>
    </section>
  );
}
