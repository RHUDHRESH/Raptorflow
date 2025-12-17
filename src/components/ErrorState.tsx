import * as React from "react";

import { cn } from "@/lib/utils";
import { ArtworkSlot } from "@/components/ArtworkSlot";

type ErrorAction = {
  label: string;
  onClick?: () => void;
};

export function ErrorState({
  title,
  description,
  action,
  secondaryAction,
  className,
  illustrationAlt = "Ink illustration: raptor silhouette over paper",
  illustrationFile = "error_state_ink.svg",
}: {
  title: string;
  description?: string;
  action?: ErrorAction;
  secondaryAction?: ErrorAction;
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
          placement="error-illustration"
          width={800}
          height={600}
          alt={illustrationAlt}
          file={illustrationFile}
          className="bg-muted"
        />

        <div>
          <h3 className="font-serif text-headline-sm text-foreground">{title}</h3>
          {description ? (
            <p className="mt-2 text-body-sm text-muted-foreground">{description}</p>
          ) : null}

          {action ? (
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
              <button
                type="button"
                onClick={action.onClick}
                className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-editorial hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                {action.label}
              </button>

              {secondaryAction ? (
                <button
                  type="button"
                  onClick={secondaryAction.onClick}
                  className="inline-flex items-center justify-center rounded-md border border-border bg-transparent px-4 py-2 text-sm font-medium text-foreground transition-editorial hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {secondaryAction.label}
                </button>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
