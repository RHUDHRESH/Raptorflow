"use client";

import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/cn";
import { RaptorMark } from "./RaptorMark";
import { BrandWordmark } from "./BrandWordmark";

export type LogoSize = "sm" | "md" | "lg";
export type LogoVariant = "full" | "mark" | "wordmark";

interface RaptorFlowLogoProps {
  size?: LogoSize;
  variant?: LogoVariant;
  className?: string;
}

const sizeMap: Record<LogoSize, { mark: number; wordmark: number }> = {
  sm: { mark: 24, wordmark: 80 },
  md: { mark: 32, wordmark: 120 },
  lg: { mark: 40, wordmark: 160 },
};

function FullRaptorFlowLogo({
  markSize,
  wordmarkSize,
  className,
}: {
  markSize: number;
  wordmarkSize: number;
  className?: string;
}) {
  const [assetError, setAssetError] = React.useState(false);

  if (!assetError) {
    return (
      <Image
        src="/brand/logo-full.svg"
        alt="RaptorFlow"
        width={wordmarkSize + markSize + 8}
        height={markSize}
        className={cn("h-auto", className)}
        onError={() => setAssetError(true)}
        priority
      />
    );
  }

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <RaptorMark size={markSize} />
      <BrandWordmark size={wordmarkSize} />
    </div>
  );
}

export function RaptorFlowLogo({ size = "md", variant = "full", className }: RaptorFlowLogoProps) {
  const { mark: markSize, wordmark: wordmarkSize } = sizeMap[size];

  if (variant === "mark") {
    return <RaptorMark size={markSize} className={className} aria-label="RaptorFlow" />;
  }

  if (variant === "wordmark") {
    return <BrandWordmark size={wordmarkSize} className={className} aria-label="RaptorFlow" />;
  }

  return (
    <FullRaptorFlowLogo markSize={markSize} wordmarkSize={wordmarkSize} className={className} />
  );
}
