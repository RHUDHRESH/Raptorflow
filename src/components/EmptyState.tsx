import * as React from "react";

import { cn } from "@/lib/utils";
import { ArtworkSlot } from "@/components/ArtworkSlot";

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  onAction,
  className,
  illustrationAlt = "Ink illustration: raptor silhouette over paper",
  illustrationFile = "empty_state_ink.svg",
}: {
  icon?: React.ComponentType<any>;
  title: string;
  description?: string;
  action?: string;
  onAction?: () => void;
  className?: string;
  illustrationAlt?: string;
  illustrationFile?: string;
}) {
  return (
    <section
      className={cn(
        "rounded-card border border-border bg-card p-8 md:p-10",
        className,
      )}
    >
      <div className="grid gap-8 md:grid-cols-[320px_1fr] md:items-center">
        <ArtworkSlot
          placement="empty-illustration"
          width={800}
          height={600}
          alt={illustrationAlt}
          file={illustrationFile}
          className="bg-muted"
        />

        <div>
          {Icon ? (
            <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground">
              <Icon className="h-5 w-5" strokeWidth={1.5} />
            </div>
          ) : null}

          <h3 className="font-serif text-headline-sm text-foreground">{title}</h3>
          {description ? (
            <p className="mt-2 text-body-sm text-muted-foreground">{description}</p>
          ) : null}

          {action ? (
            <button
              type="button"
              onClick={onAction}
              className="mt-6 inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {action}
            </button>
          ) : null}
        </div>
      </div>
    </section>
  );
}
