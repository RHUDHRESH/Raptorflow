import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { ArrowLeftIcon } from "@radix-ui/react-icons";
import { cn } from "@/lib/cn";

interface RouteShellProps {
  eyebrow: string;
  title: string;
  description?: string;
  tags?: string[];
  backHref?: Route;
  backLabel?: string;
  children: React.ReactNode;
  rail?: React.ReactNode;
  /** Pass actions (buttons/CTAs) to show in the header right slot */
  actions?: React.ReactNode;
}

/**
 * RouteShell — "Claude meets Notion" design system.
 * Instrument Serif h1, JetBrains Mono eyebrow/tags, soft paper styling.
 */
export function RouteShell({
  eyebrow,
  title,
  description,
  tags,
  backHref,
  backLabel,
  children,
  rail,
  actions,
}: RouteShellProps): React.ReactElement {
  return (
    <div className="flex flex-col gap-8 py-2">
      {/* ── Header ─────────────────────────────────────────── */}
      <header className="gsap-reveal">
        {/* Back nav */}
        {backHref && (
          <Link
            href={backHref}
            className="mb-6 flex w-fit items-center gap-2 link-underline mono-label hover:text-[var(--ink-900)] transition-colors"
          >
            <ArrowLeftIcon className="h-3 w-3" />
            {backLabel ?? "Back"}
          </Link>
        )}

        <div className="flex items-end justify-between gap-6 border-b border-[var(--border)] pb-6">
          <div>
            {/* Eyebrow */}
            <p className="eyebrow mb-2">{eyebrow}</p>

            {/* Title */}
            <h1 className="display-md">{title}</h1>

            {/* Description */}
            {description && <p className="mt-3 max-w-2xl body-muted">{description}</p>}
          </div>

          {/* Right: tags + actions */}
          <div className="flex flex-col items-end gap-3 shrink-0">
            {actions}
            {tags && tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 justify-end">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="mono-label px-2 py-1 border border-[var(--border)] bg-[var(--card)] rounded-[var(--radius-xs)]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ── Body ───────────────────────────────────────────── */}
      <div className={cn("grid gap-8", rail ? "xl:grid-cols-[minmax(0,1fr)_300px]" : "")}>
        <section className="flex flex-col gap-6">{children}</section>
        {rail && <aside className="flex flex-col gap-4">{rail}</aside>}
      </div>
    </div>
  );
}

/**
 * RouteCard — Soft paper card for rail/aside content.
 */
export function RouteCard({
  title,
  body,
  footer,
}: {
  title: string;
  body: string;
  footer?: React.ReactNode;
}): React.ReactElement {
  return (
    <div className="card-elevated p-5">
      <p className="eyebrow mb-3">{title}</p>
      <p className="body-muted">{body}</p>
      {footer && <div className="mt-4">{footer}</div>}
    </div>
  );
}
