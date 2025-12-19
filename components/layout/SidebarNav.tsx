"use client";

import Link from "next/link";
import { useAtom } from "jotai";
import { activeSidebarAtom } from "@/lib/store/atoms";
import { cn } from "@/lib/utils/cn";
import {
  Home,
  Zap,
  Rocket,
  Settings,
} from "lucide-react";

interface SidebarNavProps {
  collapsed?: boolean;
}

const navItems = [
  {
    id: "home" as const,
    label: "Home",
    href: "/app/dashboard",
    icon: Home,
  },
  {
    id: "campaigns" as const,
    label: "Campaigns",
    href: "/app/campaigns",
    icon: Zap,
  },
  {
    id: "moves" as const,
    label: "Moves",
    href: "/app/moves",
    icon: Rocket,
  },
  {
    id: "settings" as const,
    label: "Settings",
    href: "/app/settings",
    icon: Settings,
  },
];

export function SidebarNav({ collapsed }: SidebarNavProps) {
  const [active, setActive] = useAtom(activeSidebarAtom);

  return (
    <div className="space-y-2">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = active === item.id;

        return (
          <Link
            key={item.id}
            href={item.href}
            onClick={() => setActive(item.id)}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md transition text-sm",
              isActive
                ? "bg-primary text-primary-foreground"
                : "text-gray-700 hover:bg-gray-100"
            )}
          >
            <Icon size={20} className="flex-shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </Link>
        );
      })}
    </div>
  );
}
