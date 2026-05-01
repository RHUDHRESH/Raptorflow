"use client";

import { useState, useEffect } from "react";
import type * as React from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { CreateOrganization } from "@clerk/nextjs";

export default function CreateWorkspacePage(): React.ReactElement {
  const { isLoaded, isSignedIn, orgId } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && isSignedIn && orgId) {
      router.push("/app");
    }
  }, [isLoaded, isSignedIn, orgId, router]);

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
          Loading...
        </div>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="space-y-4 text-center">
        <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
          You need to be signed in to create a workspace.
        </p>
      </div>
    );
  }

  if (orgId) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
          Redirecting to your workspace...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-none border border-[var(--border)] bg-[var(--card)] p-5 shadow-none">
        <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-[var(--muted-foreground)]">
          Workspace
        </p>
        <h2 className="mt-2 font-[family-name:var(--font-display)] text-2xl text-[var(--foreground)]">
          Create your workspace
        </h2>
        <p className="mt-2 text-sm text-[var(--muted-foreground)] leading-6">
          A workspace is where your team, campaigns, and agents live. Pick a name for your
          organization to get started.
        </p>
      </div>

      <CreateOrganization
        afterCreateOrganizationUrl="/app"
        appearance={{
          elements: {
            rootBox: "w-full",
            card: "bg-[var(--card)] shadow-none border border-[var(--border)] rounded-none p-4",
            headerTitle: "font-[family-name:var(--font-display)] text-2xl text-[var(--foreground)]",
            headerSubtitle: "font-body text-[var(--muted-foreground)]",
            formButtonPrimary:
              "bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 rounded-none h-12 uppercase tracking-wider text-xs font-mono border border-[var(--primary)]",
            formFieldInput:
              "bg-[var(--background)] border border-[var(--border)] rounded-none h-12 px-4 focus:ring-1 focus:ring-[var(--primary)]",
            formFieldLabel:
              "font-mono uppercase tracking-widest text-[10px] text-[var(--muted-foreground)] mb-1",
            socialButtonsBlockButton:
              "border border-[var(--border)] rounded-none h-12 hover:bg-[var(--accent)]",
            organizationSwitcherPopoverActionButton:
              "bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 rounded-none",
          },
        }}
      />
    </div>
  );
}
