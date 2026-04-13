"use client";

import type * as React from "react";
import { useUser, useOrganization } from "@clerk/nextjs";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function SettingsPage(): React.ReactElement {
  const { user, isLoaded: userLoaded } = useUser();
  const { organization, isLoaded: orgLoaded } = useOrganization();

  return (
    <RouteShell
      eyebrow="Account"
      title="Settings"
      description="Organization settings, auth preferences, upload policy, and operational toggles."
      tags={["settings", "org", "user"]}
    >
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {userLoaded && user ? (
                <div className="flex items-center gap-4">
                  {user.imageUrl && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={user.imageUrl}
                      alt={user.fullName ?? "User"}
                      className="h-12 w-12 rounded-full"
                    />
                  )}
                  <div>
                    <p className="font-semibold">{user.fullName ?? "Unknown"}</p>
                    <p className="text-sm text-[var(--muted-foreground)]">{user.primaryEmailAddress?.emailAddress}</p>
                  </div>
                </div>
              ) : (
                <div className="h-12 w-full animate-pulse rounded bg-[var(--muted)]" />
              )}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-[var(--muted-foreground)]">User ID</p>
                  <p className="font-mono text-xs">{user?.id ?? "—"}</p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Role</p>
                  <p className="font-medium">{user?.publicMetadata?.role as string ?? "member"}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Organization</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {orgLoaded && organization ? (
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--muted)] text-lg font-bold">
                    {organization.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold">{organization.name}</p>
                    <p className="text-sm text-[var(--muted-foreground)]">Org ID: {organization.id}</p>
                  </div>
                </div>
              ) : (
                <div className="h-12 w-full animate-pulse rounded bg-[var(--muted)]" />
              )}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-[var(--muted-foreground)]">Plan</span>
                  <Badge variant="outline">Starter</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-[var(--muted-foreground)]">Members</span>
                  <span className="font-medium">{organization?.membersCount ?? "—"}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span>Email notifications</span>
                <Button size="sm" variant="ghost">Manage →</Button>
              </div>
              <div className="flex items-center justify-between">
                <span>2FA / MFA</span>
                <Button size="sm" variant="ghost">Enable →</Button>
              </div>
              <div className="flex items-center justify-between">
                <span>API keys</span>
                <Button size="sm" variant="ghost">Manage →</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Danger zone</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" size="sm" variant="destructive">Leave organization</Button>
              <Button className="w-full" size="sm" variant="destructive">Delete account</Button>
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50/50">
            <CardHeader>
              <CardTitle className="text-base">📝 What to implement next</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-amber-800">
              <p><strong>Role management:</strong> Admins can change member roles (admin, member, viewer) via Clerk's org membership API.</p>
              <p><strong>Org settings:</strong> Allow org name/logo updates, custom slug, billing email.</p>
              <p><strong>Upload policy:</strong> Max file size, allowed content types, retention period — configurable per org.</p>
              <p><strong>API keys page:</strong> Generate and revoke API keys for programmatic access.</p>
              <p><strong>Audit log:</strong> Log of membership changes, role updates, and org settings modifications.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </RouteShell>
  );
}
