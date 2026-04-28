"use client";

import * as React from "react";
import { cn } from "@/lib/cn";
import { BrandHeader } from "@/components/brand/BrandHeader";
import { PaperTexture } from "@/components/brand/PaperTexture";

export type MaxWidth = "standard" | "wide" | "full";

interface AppPageFrameProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  rail?: React.ReactNode;
  className?: string;
  maxWidth?: MaxWidth;
  status?: React.ReactNode;
}

const maxWidthMap: Record<MaxWidth, string> = {
  standard: "max-w-5xl",
  wide: "max-w-7xl",
  full: "max-w-none",
};

export function AppPageFrame({
  eyebrow,
  title,
  description,
  actions,
  children,
  rail,
  className,
  maxWidth = "wide",
  status,
}: AppPageFrameProps) {
  return (
    <PaperTexture
      intensity="soft"
      className={cn("min-h-[calc(100vh-theme(spacing.16))]", className)}
    >
      <div className={cn("mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8", maxWidthMap[maxWidth])}>
        <BrandHeader
          eyebrow={eyebrow}
          title={title}
          description={description}
          status={status}
          actions={actions}
        />
        <div className={cn("flex gap-6", rail ? "flex-col lg:flex-row" : "flex-col")}>
          <div className="flex-1 min-w-0">{children}</div>
          {rail && <div className="w-full lg:w-80 xl:w-96 shrink-0">{rail}</div>}
        </div>
      </div>
    </PaperTexture>
  );
}
