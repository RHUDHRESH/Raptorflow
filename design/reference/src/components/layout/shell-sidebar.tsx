"use client";

import type * as React from "react";
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
  IdCardIcon,
  UploadIcon,
  ChevronRightIcon,
  LightningBoltIcon,
} from "@radix-ui/react-icons";
import { cn } from "@/lib/cn";
import { OfficeMiniStrip } from "@/components/office/office-mini-strip";

/* ─── Navigation Structure ─────────────────────────────────────── */
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
      { href: "/app" as Route, label: "Dashboard", icon: DashboardIcon },
      { href: "/office" as Route, label: "The Office", icon: MagicWandIcon },
      { href: "/daily-wins" as Route, label: "Daily Wins", icon: CalendarIcon },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { href: "/intel" as Route, label: "Intel", icon: TargetIcon },
      { href: "/nudges" as Route, label: "Nudges", icon: BellIcon },
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

/* ─── Main Sidebar ─────────────────────────────────────────────── */
export function ShellSidebar({
  identity,
}: {
  identity: { userId: string; orgId: string };
}) {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col fixed left-0 top-0 bg-[#0f0f0f] border-r border-zinc-800 z-40 overflow-hidden">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-zinc-800">
        <div className="w-6 h-6 bg-amber-500 flex items-center justify-center rounded-sm">
          <LightningBoltIcon className="w-4 h-4 text-black" />
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-bold text-white tracking-tight leading-none">RaptorFlow</span>
          <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest mt-0.5">EST. 1989</span>
        </div>
      </div>

      {/* Navigation Groups */}
      <nav className="flex-1 overflow-y-auto pt-6 space-y-8 scrollbar-hide">
        {NAV_GROUPS.map((group) => (
          <div key={group.label} className="px-3">
            <h2 className="px-3 mb-3 text-[9px] font-bold text-zinc-600 uppercase tracking-[0.2em] font-mono">
              {group.label}
            </h2>
            <div className="space-y-1">
              {group.items.map((item) => {
                const isActive = pathname === item.href || (item.href !== "/app" && pathname.startsWith(item.href + "/"));
                const Icon = item.icon;
                
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 text-[13px] transition-all duration-150 group",
                      isActive
                        ? "text-white bg-[#1a1a1a] border-l-2 border-amber-500"
                        : "text-zinc-500 hover:text-zinc-300 hover:bg-[#161616]"
                    )}
                  >
                    <Icon className={cn(
                      "w-4 h-4 transition-colors",
                      isActive ? "text-amber-500" : "text-zinc-600 group-hover:text-zinc-400"
                    )} />
                    <span className="font-medium">{item.label}</span>
                    {isActive && (
                      <div className="ml-auto w-1 h-1 rounded-full bg-amber-500 animate-pulse" />
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Org Info */}
      <div className="px-6 py-4 border-t border-zinc-900 bg-black/20">
        <p className="text-[9px] font-mono text-zinc-600 uppercase tracking-widest leading-relaxed">
          UPLINK: ACTIVE<br/>
          ORG: {identity.orgId.slice(0, 12)}
        </p>
      </div>

      {/* Office Mini-Strip (Passive View) */}
      <OfficeMiniStrip />
    </aside>
  );
}
