import * as React from "react";

import { cn } from "@/lib/utils";

type ArtworkPlacement =
  | "masthead-bg"
  | "empty-illustration"
  | "error-illustration"
  | "inline";

type ArtworkFallback = {
  monogram?: string;
  gradientClassName?: string;
  grain?: boolean;
};

export function ArtworkSlot({
  id,
  placement,
  prompt,
  aspectRatio,
  fallback,
  width,
  height,
  alt,
  file,
  className,
}: {
  id?: string;
  placement: ArtworkPlacement;
  prompt?: string;
  aspectRatio?: number;
  fallback?: ArtworkFallback;
  width?: number;
  height?: number;
  alt?: string;
  file?: string;
  className?: string;
}) {
  const resolvedWidth = width ?? 1200;
  const resolvedHeight = height ?? 900;
  const resolvedAlt = alt ?? prompt ?? "Artwork placeholder";
  const resolvedAspectRatio =
    aspectRatio ?? (resolvedWidth && resolvedHeight ? resolvedWidth / resolvedHeight : 4 / 3);

  return (
    <div
      role="img"
      aria-label={resolvedAlt}
      className={cn(
        "relative w-full overflow-hidden rounded-card border border-border bg-card",
        className,
      )}
      style={{ aspectRatio: `${resolvedAspectRatio}` }}
    >
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 p-6 text-center">
        <div className="text-[11px] font-medium tracking-wide text-muted-foreground">ARTWORK SLOT</div>

        {id ? (
          <div className="font-mono text-[11px] text-muted-foreground">id=&quot;{id}&quot;</div>
        ) : null}

        <div className="text-sm text-foreground">
          {placement} / {Math.round(resolvedAspectRatio * 1000) / 1000}
        </div>

        {prompt ? (
          <div className="max-w-[54ch] text-xs text-muted-foreground">{prompt}</div>
        ) : resolvedAlt ? (
          <div className="max-w-[54ch] text-xs text-muted-foreground">{resolvedAlt}</div>
        ) : null}

        {file ? (
          <div className="mt-1 font-mono text-[11px] text-muted-foreground">
            file=&quot;{file}&quot;
          </div>
        ) : null}
      </div>

      {fallback?.monogram ? (
        <div className="absolute left-4 top-4 rounded-card border border-border bg-background/70 px-2 py-1 font-mono text-[11px] text-muted-foreground">
          {fallback.monogram}
        </div>
      ) : null}

      <div
        aria-hidden="true"
        className={cn(
          "absolute inset-0 opacity-[0.08]",
          fallback?.gradientClassName ?? "",
        )}
        style={{
          backgroundImage:
            "radial-gradient(circle at 20% 20%, hsl(var(--foreground) / 0.6) 0, transparent 40%), radial-gradient(circle at 80% 30%, hsl(var(--foreground) / 0.5) 0, transparent 38%), radial-gradient(circle at 40% 80%, hsl(var(--foreground) / 0.45) 0, transparent 42%)",
        }}
      />

      {fallback?.grain ? (
        <div
          aria-hidden="true"
          className="absolute inset-0 opacity-[0.06] mix-blend-multiply"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
          }}
        />
      ) : null}
    </div>
  );
}
