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
  const isDevBypass = process.env.NODE_ENV !== "production";
  const identity = isDevBypass
    ? {
        userId: "dev-user",
        orgId: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      }
    : await auth();

  if (!identity.userId) {
    redirect("/sign-in" as Route);
  }

  return (
    <AppShell
      identity={{
        userId: identity.userId,
        orgId: identity.orgId ?? "org_unselected"
      }}
    >
      {children}
    </AppShell>
  );
}
