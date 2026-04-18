import type * as React from "react";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";

interface UnimplementedFeatureProps {
  featureName: string;
  description?: string;
  className?: string;
}

export function UnimplementedFeature({ featureName, description, className = "" }: UnimplementedFeatureProps) {
  return (
    <div className={`p-12 border-2 border-dashed border-zinc-800 bg-zinc-900/10 flex flex-col items-center text-center gap-4 ${className}`}>
      <div className="h-12 w-12 rounded-full bg-zinc-900 flex items-center justify-center border border-zinc-800">
        <ExclamationTriangleIcon className="h-6 w-6 text-zinc-600" />
      </div>
      <div className="space-y-2 max-w-sm">
        <h3 className="font-[family-name:var(--font-display)] text-2xl text-zinc-400">
          {featureName} is in Standby
        </h3>
        <p className="font-mono text-[9px] text-zinc-600 uppercase tracking-widest">
          {description || "The backend engine for this capability is currently under development. Intelligence signals are disconnected from this surface."}
        </p>
      </div>
    </div>
  );
}
