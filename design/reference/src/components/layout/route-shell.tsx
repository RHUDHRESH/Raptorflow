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
 * RouteShell — Upgraded to 100x Obsidian design system.
 * DM Serif Display h1, JetBrains Mono eyebrow/tags, brutalist divider.
 * Replaces old ShadCN card-wrapped version.
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
      <header>
        {/* Back nav */}
        {backHref && (
          <Link
            href={backHref}
            className="mb-6 flex w-fit items-center gap-2 hover:underline"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              textTransform: "uppercase",
              letterSpacing: "0.16em",
              color: "var(--muted-foreground)",
            }}
          >
            <ArrowLeftIcon className="h-3 w-3" />
            {backLabel ?? "Back"}
          </Link>
        )}

        <div className="flex items-end justify-between gap-6 border-b-2 border-[var(--foreground)] pb-6">
          <div>
            {/* Eyebrow */}
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.22em",
                color: "var(--muted-foreground)",
                marginBottom: 8,
              }}
            >
              {eyebrow}
            </p>

            {/* Title */}
            <h1
              style={{
                fontFamily: "'DM Serif Display', serif",
                fontSize: 40,
                lineHeight: 1,
                color: "var(--foreground)",
                margin: 0,
              }}
            >
              {title}
            </h1>

            {/* Description */}
            {description && (
              <p
                className="mt-3 max-w-2xl"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 13,
                  lineHeight: 1.6,
                  color: "var(--muted-foreground)",
                }}
              >
                {description}
              </p>
            )}
          </div>

          {/* Right: tags + actions */}
          <div className="flex flex-col items-end gap-3 shrink-0">
            {actions}
            {tags && tags.length > 0 && (
              <div className="flex flex-wrap gap-1 justify-end">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: 8,
                      fontWeight: 700,
                      textTransform: "uppercase",
                      letterSpacing: "0.12em",
                      border: "1px solid var(--border)",
                      color: "var(--muted-foreground)",
                      padding: "2px 6px",
                      background: "var(--card)",
                    }}
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
 * RouteCard — Brutalist info card for rail/aside content.
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
    <div
      className="border border-[var(--border)] p-5"
      style={{ background: "var(--card)" }}
    >
      <p
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.16em",
          color: "var(--muted-foreground)",
          marginBottom: 10,
        }}
      >
        {title}
      </p>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, lineHeight: 1.6, color: "var(--foreground)" }}>
        {body}
      </p>
      {footer && <div className="mt-4">{footer}</div>}
    </div>
  );
}
