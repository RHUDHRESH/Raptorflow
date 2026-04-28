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
  MixerHorizontalIcon,
} from "@radix-ui/react-icons";
import { cn } from "@/lib/cn";
import { RaptorMark } from "@/components/brand/RaptorMark";
import { BrandWordmark } from "@/components/brand/BrandWordmark";
import { routeGroups } from "@/brand/routes";
import { OfficeMiniStrip } from "@/components/office/office-mini-strip";
import { NotificationPanel } from "@/components/layout/notification-panel";
import { useOfficeStore } from "@/state/office-store";
import { Menu, X } from "lucide-react";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  "/app/dashboard": DashboardIcon,
  "/office": MagicWandIcon,
  "/daily-wins": CalendarIcon,
  "/uploads": UploadIcon,
  "/intel": TargetIcon,
  "/nudges": BellIcon,
  "/ripples": MixerHorizontalIcon,
  "/campaigns": BackpackIcon,
  "/council": AvatarIcon,
  "/muse": ChatBubbleIcon,
  "/content": FileTextIcon,
  "/foundation": HomeIcon,
  "/settings": GearIcon,
};

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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const eventLog = useOfficeStore((s) => s.eventLog);
  const unreadCount = eventLog.filter((e) => !e.processed).length;

  React.useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-[var(--sidebar-background)] border border-[var(--sidebar-border)] text-[var(--ink-400)] hover:text-[var(--ink-900)]"
        aria-label="Open sidebar"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={cn(
          "flex h-screen w-64 flex-col fixed left-0 top-0 bg-[var(--sidebar-background)] border-r border-[var(--sidebar-border)] z-40 overflow-hidden paper-soft",
          "transition-transform duration-200 ease-out",
          "lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="h-16 px-6 flex items-center justify-between border-b border-[var(--sidebar-border)] relative">
          <div className="flex items-center gap-3">
            <RaptorMark size={28} className="text-[var(--ink-900)]" />
            <div className="flex flex-col">
              <BrandWordmark size={90} className="text-[var(--ink-900)]" />
              <span className="text-[9px] font-mono text-[var(--ink-400)] uppercase tracking-widest mt-0.5">
                AI-NATIVE MARKETING OS
              </span>
            </div>
          </div>

          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden absolute -right-2 top-1/2 -translate-y-1/2 p-2 text-[var(--ink-400)] hover:text-[var(--ink-900)]"
            aria-label="Close sidebar"
          >
            <X className="w-4 h-4" />
          </button>
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
          {routeGroups.map((group, groupIndex) => (
            <div key={group.key} className="px-3">
              <h2 className="px-3 mb-3 text-[9px] font-bold text-[var(--ink-400)] uppercase tracking-[0.2em] font-mono">
                {group.label}
              </h2>
              <div className="space-y-1">
                {group.routes.map((route, itemIndex) => {
                  const href = route.href as Route;
                  const isExact = pathname === route.href;
                  const isNested =
                    route.href !== "/office" &&
                    route.href !== "/app/dashboard" &&
                    pathname.startsWith(route.href + "/");
                  const isActive = isExact || isNested;
                  const Icon = iconMap[route.href] ?? DashboardIcon;

                  return (
                    <Link
                      key={route.href}
                      href={href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 text-[13px] transition-all duration-150 group relative rounded-[var(--radius)]",
                        isActive
                          ? "bg-[var(--amber-wash)] text-[var(--ink-900)] shadow-sm border border-[var(--amber-stroke)]/20"
                          : "text-[var(--ink-500)] hover:text-[var(--ink-900)] hover:bg-[var(--paper-150)]",
                      )}
                      style={{
                        animationDelay: `${(groupIndex * 4 + itemIndex) * 50}ms`,
                      }}
                    >
                      {isActive && (
                        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[2px] h-5 bg-[var(--primary)] rounded-r-full" />
                      )}
                      <Icon
                        className={cn(
                          "w-4 h-4 transition-colors duration-200",
                          isActive
                            ? "text-[var(--primary)]"
                            : "text-[var(--ink-400)] group-hover:text-[var(--ink-700)]",
                        )}
                      />
                      <span className="font-medium">{route.label}</span>
                      {isActive && <span className="ml-auto status-dot-live" />}
                      {route.href === "/intel" && (
                        <SidebarBadge queryKey={["intel"]} countPath="signals.length" />
                      )}
                      {route.href === "/nudges" && (
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
