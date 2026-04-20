"use client";

import * as React from "react";
import { useState } from "react";
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
  MixerHorizontalIcon,
} from "@radix-ui/react-icons";
import { cn } from "@/lib/cn";
import { OfficeMiniStrip } from "@/components/office/office-mini-strip";
import { NotificationPanel } from "@/components/layout/notification-panel";
import { useOfficeStore } from "@/state/office-store";

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
      { href: "/billing" as Route, label: "Billing", icon: IdCardIcon },
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
  const [notifOpen, setNotifOpen] = useState(false);
  const eventLog = useOfficeStore((s) => s.eventLog);
  const unreadCount = eventLog.filter(e => !e.processed).length;

  return (
    <>
      <aside className="flex h-screen w-64 flex-col fixed left-0 top-0 bg-[#FBF8F2] border-r border-[#E5DED4] z-40 overflow-hidden paper-soft">
        {/* Brand Header */}
        <div className="h-16 px-6 flex items-center justify-between border-b border-[#E5DED4]">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 bg-[#D97757] flex items-center justify-center rounded-sm">
              <LightningBoltIcon className="w-4 h-4 text-[#2A2622]" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-[#2A2622] tracking-tight leading-none">RaptorFlow</span>
              <span className="text-[9px] font-mono text-[#9A948C] uppercase tracking-widest mt-0.5">EST. 1989</span>
            </div>
          </div>

          <button 
            onClick={() => setNotifOpen(true)}
            className="p-2 hover:bg-[#F5F0E8] transition-colors relative"
          >
            <BellIcon className={cn("w-4 h-4 transition-colors", unreadCount > 0 ? "text-[#D97757]" : "text-[#9A948C]")} />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-[#D97757] rounded-full animate-pulse shadow-[0_0_8px_rgba(217,119,87,0.5)]" />
            )}
          </button>
        </div>

        {/* Navigation Groups */}
        <nav className="flex-1 overflow-y-auto pt-6 space-y-8 scrollbar-hide">
          {NAV_GROUPS.map((group) => (
            <div key={group.label} className="px-3">
              <h2 className="px-3 mb-3 text-[9px] font-bold text-[#9A948C] uppercase tracking-[0.2em] font-mono">
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
                          ? "text-[#2A2622] bg-white border-l-2 border-[#D97757]"
                          : "text-[#6B655E] hover:text-[#2A2622] hover:bg-[#F5F0E8]"
                      )}
                    >
                      <Icon className={cn(
                        "w-4 h-4 transition-colors",
                        isActive ? "text-[#D97757]" : "text-[#9A948C] group-hover:text-[#6B655E]"
                      )} />
                      <span className="font-medium">{item.label}</span>
                      {isActive && (
                        <div className="ml-auto w-1 h-1 rounded-full bg-[#D97757] animate-pulse" />
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Org Info */}
        <div className="px-6 py-4 border-t border-[#E5DED4] bg-[#F5F0E8]/50">
          <p className="text-[9px] font-mono text-[#9A948C] uppercase tracking-widest leading-relaxed">
            UPLINK: ACTIVE<br/>
            ORG: {identity.orgId.slice(0, 12)}
          </p>
        </div>

        {/* Office Mini-Strip (Passive View) */}
        <OfficeMiniStrip />
      </aside>

      <NotificationPanel 
        isOpen={notifOpen} 
        onClose={() => setNotifOpen(false)} 
      />
    </>
  );
}
