"use client";

import * as React from "react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  DashboardIcon,
  HomeIcon,
  BackpackIcon,
  TargetIcon,
  BellIcon,
  MagicWandIcon,
  ChatBubbleIcon,
  AvatarIcon,
  CalendarIcon,
  FileTextIcon,
  GearIcon,
  UploadIcon,
  LightningBoltIcon,
  MixerHorizontalIcon,
} from "@radix-ui/react-icons";
import { cn } from "@/lib/cn";
import { OfficeMiniStrip } from "@/components/office/office-mini-strip";
import { NotificationPanel } from "@/components/layout/notification-panel";
import { useOfficeStore } from "@/state/office-store";

type NavItem = {
  href: Route;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  accent?: string;
};

type NavGroup = {
  label: string;
  items: NavItem[];
};

const NAV_GROUPS: NavGroup[] = [
  {
    label: "Workspace",
    items: [
      { href: "/app/dashboard" as Route, label: "Dashboard", icon: DashboardIcon },
      { href: "/office" as Route, label: "The Office", icon: MagicWandIcon },
      { href: "/daily-wins" as Route, label: "Daily Wins", icon: CalendarIcon },
      { href: "/uploads" as Route, label: "Uploads", icon: UploadIcon },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { href: "/intel" as Route, label: "Intel", icon: TargetIcon },
      { href: "/nudges" as Route, label: "Nudges", icon: BellIcon },
      { href: "/ripples" as Route, label: "Ripples", icon: MixerHorizontalIcon },
    ],
  },
  {
    label: "Strategy",
    items: [
      { href: "/campaigns" as Route, label: "Campaigns", icon: BackpackIcon },
      { href: "/council" as Route, label: "Council", icon: AvatarIcon },
      { href: "/muse" as Route, label: "Muse", icon: ChatBubbleIcon, accent: "#4f46e5" },
      { href: "/content" as Route, label: "Content", icon: FileTextIcon },
    ],
  },
  {
    label: "System",
    items: [
      { href: "/foundation" as Route, label: "Foundation", icon: HomeIcon },
      { href: "/settings" as Route, label: "Settings", icon: GearIcon },
    ],
  },
];

function SidebarBadge({ queryKey, countPath }: { queryKey: unknown[]; countPath: string }) {
  const { data } = useQuery({
    queryKey,
    staleTime: 30_000,
  });
  const count = countPath.split(".").reduce((acc: unknown, key: string) => {
    if (acc && typeof acc === "object") return (acc as Record<string, unknown>)[key];
    return 0;
  }, data as unknown) as number;
  if (!count) return null;
  return (
    <span className="ml-auto text-[10px] bg-[var(--primary)] text-white rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1 font-mono font-bold">
      {count > 9 ? "9+" : count}
    </span>
  );
}

export function ShellSidebar({ identity }: { identity: { userId: string; orgId: string } }) {
  const pathname = usePathname();
  const [notifOpen, setNotifOpen] = useState(false);
  const eventLog = useOfficeStore((s) => s.eventLog);
  const unreadCount = eventLog.filter((e) => !e.processed).length;

  return (
    <>
      <aside className="flex h-screen w-64 flex-col fixed left-0 top-0 bg-[var(--sidebar-background)] border-r border-[var(--sidebar-border)] z-40 overflow-hidden paper-soft">
        <div className="h-16 px-6 flex items-center justify-between border-b border-[var(--sidebar-border)]">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 bg-[var(--primary)] flex items-center justify-center rounded-[var(--radius)] transition-transform duration-300 hover:scale-105">
              <LightningBoltIcon className="w-4 h-4 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-[var(--ink-900)] tracking-tight leading-none">
                RaptorFlow
              </span>
              <span className="text-[9px] font-mono text-[var(--ink-400)] uppercase tracking-widest mt-0.5">
                EST. 1989
              </span>
            </div>
          </div>

          <button
            onClick={() => setNotifOpen(true)}
            className="p-2 rounded-[var(--radius)] hover:bg-[var(--paper-150)] transition-all duration-200 relative group"
          >
            <BellIcon
              className={cn(
                "w-4 h-4 transition-colors duration-200",
                unreadCount > 0 ? "text-[var(--primary)]" : "text-[var(--ink-400)]",
              )}
            />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-[var(--primary)] rounded-full animate-pulse shadow-[0_0_8px_rgba(217,119,87,0.5)]" />
            )}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto pt-6 space-y-8 scrollbar-thin">
          {NAV_GROUPS.map((group, groupIndex) => (
            <div key={group.label} className="px-3">
              <h2 className="px-3 mb-3 text-[9px] font-bold text-[var(--ink-400)] uppercase tracking-[0.2em] font-mono">
                {group.label}
              </h2>
              <div className="space-y-1">
                {group.items.map((item, itemIndex) => {
                  const isActive =
                    pathname === item.href ||
                    (item.href !== "/app" && pathname.startsWith(item.href + "/"));
                  const Icon = item.icon;

                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 text-[13px] transition-all duration-200 group relative rounded-[var(--radius)]",
                        isActive
                          ? "text-[var(--ink-900)] bg-white shadow-sm"
                          : "text-[var(--ink-500)] hover:text-[var(--ink-900)] hover:bg-[var(--paper-150)]",
                      )}
                      style={{
                        animationDelay: `${(groupIndex * 4 + itemIndex) * 50}ms`,
                      }}
                    >
                      {isActive && (
                        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-[var(--primary)] rounded-r-full" />
                      )}
                      <Icon
                        className={cn(
                          "w-4 h-4 transition-colors duration-200",
                          isActive
                            ? "text-[var(--primary)]"
                            : "text-[var(--ink-400)] group-hover:text-[var(--ink-500)]",
                        )}
                      />
                      <span className="font-medium">{item.label}</span>
                      {isActive && <span className="ml-auto status-dot-live" />}
                      {item.href === "/intel" && (
                        <SidebarBadge queryKey={["intel"]} countPath="signals.length" />
                      )}
                      {item.href === "/nudges" && (
                        <SidebarBadge queryKey={["nudges"]} countPath="totalCount" />
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="px-6 py-4 border-t border-[var(--sidebar-border)] bg-[var(--paper-150)]/50">
          <div className="flex items-center gap-2 mb-2">
            <span className="status-dot-live" />
            <p className="text-[9px] font-mono text-[var(--ink-500)] uppercase tracking-widest">
              UPLINK: ACTIVE
            </p>
          </div>
          <p className="text-[9px] font-mono text-[var(--ink-400)] uppercase tracking-widest leading-relaxed">
            ORG: {identity.orgId.slice(0, 12)}
          </p>
        </div>

        <OfficeMiniStrip />
      </aside>

      <NotificationPanel isOpen={notifOpen} onClose={() => setNotifOpen(false)} />
    </>
  );
}
