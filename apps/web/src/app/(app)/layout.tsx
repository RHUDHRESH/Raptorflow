import type * as React from "react";
import { auth } from "@clerk/nextjs/server";
import type { Route } from "next";
import { redirect } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";

export default async function ProtectedLayout({
  children
}: {
  children: React.ReactNode;
}): Promise<React.ReactElement> {
  const { userId, orgId } = await auth();

  if (!userId) {
    redirect("/sign-in" as Route);
  }

  return (
    <AppShell
      identity={{
        userId,
        orgId: orgId ?? "org_unselected"
      }}
    >
      {children}
    </AppShell>
  );
}
