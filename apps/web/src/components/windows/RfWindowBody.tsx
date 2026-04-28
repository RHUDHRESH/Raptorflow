"use client";

import * as React from "react";
import { cn } from "@/lib/cn";
import type { WindowDensity } from "./RfWindow";

interface RfWindowBodyProps {
  children: React.ReactNode;
  className?: string;
  density?: WindowDensity;
}

export function RfWindowBody({ children, className, density = "comfortable" }: RfWindowBodyProps) {
  return <div className={cn(density === "comfortable" ? "p-6" : "p-4", className)}>{children}</div>;
}
