import type * as React from "react";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";

export default async function ProtectedLayout({
  children
}: {
  children: React.ReactNode;
}): Promise<React.ReactElement> {
  const { userId, orgId } = await auth();

  if (!userId) {
    redirect("/sign-in" as never);
  }

  if (!orgId) {
    redirect("/create-workspace" as never);
  }

  return (
    <AppShell
      identity={{
        userId,
        orgId
      }}
    >
      {children}
    </AppShell>
  );
}