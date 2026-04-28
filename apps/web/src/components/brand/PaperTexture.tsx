"use client";

import * as React from "react";
import { cn } from "@/lib/cn";

interface PaperTextureProps {
  children: React.ReactNode;
  intensity?: "none" | "soft" | "standard";
  className?: string;
}

export function PaperTexture({ children, intensity = "soft", className }: PaperTextureProps) {
  const textureClass = intensity === "none" ? "" : intensity === "soft" ? "paper-soft" : "paper";

  return <div className={cn(textureClass, className)}>{children}</div>;
}
