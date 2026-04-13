import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/cn";

export function RouteShell({
  eyebrow,
  title,
  description,
  tags,
  backHref,
  backLabel,
  children,
  rail
}: {
  eyebrow: string;
  title: string;
  description: string;
  tags?: string[];
  backHref?: Route;
  backLabel?: string;
  children: React.ReactNode;
  rail?: React.ReactNode;
}): React.ReactElement {
  return (
    <div className="space-y-6">
      <header className="space-y-3">
        {backHref ? (
          <Link
            href={backHref}
            className="text-sm text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)]"
          >
            {backLabel ?? "Back"}
          </Link>
        ) : null}
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div className="max-w-3xl space-y-2">
            <p className="text-sm uppercase tracking-[0.22em] text-[var(--muted-foreground)]">
              {eyebrow}
            </p>
            <h1 className="font-[family-name:var(--font-display)] text-4xl">{title}</h1>
            <p className="max-w-2xl text-sm text-[var(--muted-foreground)]">{description}</p>
          </div>
          {tags?.length ? (
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <Badge key={tag} className="bg-white/85">
                  {tag}
                </Badge>
              ))}
            </div>
          ) : null}
        </div>
      </header>
      <div className={cn("grid gap-6", rail ? "xl:grid-cols-[minmax(0,1fr)_320px]" : "")}>
        <section className="space-y-4">{children}</section>
        {rail ? <aside className="space-y-4">{rail}</aside> : null}
      </div>
    </div>
  );
}

export function RouteCard({
  title,
  body,
  footer
}: {
  title: string;
  body: string;
  footer?: React.ReactNode;
}): React.ReactElement {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm text-[var(--muted-foreground)]">
        <p>{body}</p>
        {footer}
      </CardContent>
    </Card>
  );
}
