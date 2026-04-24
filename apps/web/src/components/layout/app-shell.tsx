import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { ShellSidebar } from "@/components/layout/shell-sidebar";

export function AppShell({
  identity,
  children,
}: {
  identity: {
    userId: string;
    orgId: string;
  };
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <div className="flex min-h-screen">
      <ShellSidebar identity={identity} />
      <main className="flex-1 min-w-0 px-6 py-8 md:px-10 ml-64 bg-[var(--background)] paper-soft transition-all duration-500">
        {children}
      </main>
    </div>
  );
}

export function ShellTitle({
  title,
  subtitle,
  href,
}: {
  title: string;
  subtitle: string;
  href?: Route;
}): React.ReactElement {
  const content = (
    <>
      <p className="eyebrow mb-2">{subtitle}</p>
      <h1 className="display-md">{title}</h1>
    </>
  );

  return href ? (
    <Link href={href} className="group">
      {content}
    </Link>
  ) : (
    content
  );
}
