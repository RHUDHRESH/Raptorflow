import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { ShellSidebar } from "@/components/layout/shell-sidebar";

export function AppShell({
  identity,
  children
}: {
  identity: {
    userId: string;
    orgId: string;
  };
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <div className="app-shell-grid">
      <ShellSidebar identity={identity} />
      <main className="min-w-0 px-6 py-8 md:px-10">{children}</main>
    </div>
  );
}

export function ShellTitle({
  title,
  subtitle,
  href
}: {
  title: string;
  subtitle: string;
  href?: Route;
}): React.ReactElement {
  const content = (
    <>
      <p className="text-sm uppercase tracking-[0.22em] text-[var(--muted-foreground)]">
        {subtitle}
      </p>
      <h1 className="font-[family-name:var(--font-display)] text-4xl">{title}</h1>
    </>
  );

  return href ? <Link href={href}>{content}</Link> : content;
}
