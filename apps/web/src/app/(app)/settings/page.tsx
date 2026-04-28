"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { useUser, useOrganization } from "@clerk/nextjs";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { GearIcon, AvatarIcon, Link1Icon, TargetIcon } from "@radix-ui/react-icons";
import { AppPageFrame } from "@/components/layout/AppPageFrame";
import { AppPageSection } from "@/components/layout/AppPageSection";
import { AppLoadingState } from "@/components/layout/AppLoadingState";
import { StatusPill } from "@/components/windows/StatusPill";

export default function SettingsPage(): React.ReactElement {
  const { user, isLoaded: userLoaded } = useUser();
  const { organization, isLoaded: orgLoaded } = useOrganization();

  if (!userLoaded || !orgLoaded) {
    return (
      <AppPageFrame eyebrow="System" title="Settings">
        <AppLoadingState label="Loading workspace..." />
      </AppPageFrame>
    );
  }

  return (
    <AppPageFrame
      eyebrow="System"
      title="Settings"
      description="Workspace configuration and account management."
      maxWidth="wide"
    >
      <GsapBridge stagger={true} className="flex flex-col lg:flex-row gap-8">
        {/* Settings nav rail */}
        <aside className="gsap-reveal w-full lg:w-56 shrink-0">
          <nav className="flex flex-col space-y-1 font-mono text-xs uppercase tracking-widest">
            <Link
              href={"/settings" as Route}
              className="flex items-center gap-3 bg-[var(--primary)] text-[var(--primary-foreground)] px-4 py-3 rounded-[var(--radius)]"
            >
              <GearIcon className="h-4 w-4" /> Workspace
            </Link>
            <Link
              href={"/foundation" as Route}
              className="flex items-center gap-3 hover:bg-[var(--paper-150)] text-[var(--foreground)] px-4 py-3 rounded-[var(--radius)] transition-colors"
            >
              <TargetIcon className="h-4 w-4" /> Onboarding
            </Link>
            <button className="flex items-center gap-3 hover:bg-[var(--paper-150)] text-[var(--foreground)] px-4 py-3 rounded-[var(--radius)] transition-colors text-left opacity-50 cursor-not-allowed">
              <AvatarIcon className="h-4 w-4" /> Team Access
            </button>
            <button className="flex items-center gap-3 hover:bg-[var(--paper-150)] text-[var(--foreground)] px-4 py-3 rounded-[var(--radius)] transition-colors text-left opacity-50 cursor-not-allowed">
              <Link1Icon className="h-4 w-4" /> Integrations
            </button>
          </nav>
        </aside>

        <div className="flex-1 space-y-8">
          <AppPageSection title="Organization Profile">
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-3">
                <label className="mono-label">Workspace Name</label>
                <input
                  type="text"
                  defaultValue={organization?.name || "RaptorFlow Workspace"}
                  className="w-full bg-transparent border-b border-[var(--border)] focus:border-[var(--primary)] outline-none py-2 font-display text-2xl transition-colors"
                />
              </div>
              <div className="space-y-3">
                <label className="mono-label">Workspace ID</label>
                <div className="py-2 text-sm font-mono text-[var(--ink-400)]">{organization?.id || "org_pending"}</div>
              </div>
            </div>

            <div className="mt-6 flex items-center gap-4">
              <button
                disabled
                title="Workspace name changes are managed via the Clerk dashboard"
                className="btn-primary opacity-40 cursor-not-allowed"
              >
                Save Changes
              </button>
              <p className="text-xs font-mono text-[var(--ink-400)]">
                Org name is managed via{" "}
                <a href="https://dashboard.clerk.com" target="_blank" rel="noreferrer" className="underline hover:text-[var(--ink-900)] transition-colors">
                  Clerk Dashboard
                </a>
              </p>
            </div>
          </AppPageSection>

          <AppPageSection title="Access Status">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="font-display text-2xl">
                  {organization ? organization.name : "Workspace access"}
                </p>
                <p className="text-sm text-[var(--ink-500)]">
                  {organization
                    ? "Access is granted after Clerk sign-in. No paywall or unlock step is required."
                    : "Loading workspace access status from Clerk."}
                </p>
              </div>
              <StatusPill status="Active" tone="success" />
            </div>
          </AppPageSection>

          <AppPageSection title="Onboarding">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="font-display text-2xl">Foundation flow</p>
                <p className="text-sm text-[var(--ink-500)]">
                  Open the guided onboarding whenever you want. It is no longer forced on login.
                </p>
              </div>
              <Link
                href={"/foundation" as Route}
                className="btn-secondary"
              >
                Start onboarding
              </Link>
            </div>
          </AppPageSection>

          <AppPageSection title="Personal Account">
            <div className="flex flex-col md:flex-row items-center gap-6">
              {user ? (
                <>
                  {user.imageUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={user.imageUrl} alt={user.fullName ?? "User"} className="h-16 w-16 rounded-[var(--radius)] grayscale border border-[var(--border)]" />
                  ) : (
                    <div className="h-16 w-16 rounded-[var(--radius)] bg-[var(--paper-150)] border border-[var(--border)] flex items-center justify-center font-display text-2xl text-[var(--ink-400)]">
                      {user.fullName?.charAt(0) || "U"}
                    </div>
                  )}
                  <div className="flex-1 text-center md:text-left">
                    <h3 className="font-display text-xl mb-0.5">{user.fullName ?? "Unknown"}</h3>
                    <p className="font-mono text-xs text-[var(--ink-400)]">{user.primaryEmailAddress?.emailAddress}</p>
                  </div>
                </>
              ) : (
                <div className="h-16 w-full animate-pulse bg-[var(--paper-200)] rounded-[var(--radius)]" />
              )}

              <button className="btn-secondary">
                Manage Auth
              </button>
            </div>
          </AppPageSection>

          <AppPageSection title="Danger Zone" variant="danger">
            <div className="flex flex-col gap-4">
              <h3 className="font-display text-2xl text-[var(--destructive)]">Erase Workspace</h3>
              <p className="text-[var(--ink-500)] text-sm max-w-xl">
                This will permanently destroy the foundation, council logs, active campaigns, and intelligence streams. This action cannot be undone.
              </p>
              <button className="btn-primary bg-[var(--destructive)] hover:bg-[var(--destructive)]/90 w-fit">
                Acknowledge and Delete
              </button>
            </div>
          </AppPageSection>
        </div>
      </GsapBridge>
    </AppPageFrame>
  );
}
