"use client";

import Link from "next/link";
import { useAtom } from "jotai";
import { activeSidebarAtom, sidebarCollapsedAtom } from "@/lib/store/atoms";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import { SidebarNav } from "./SidebarNav";

export function Sidebar() {
  const [active] = useAtom(activeSidebarAtom);
  const [collapsed, setCollapsed] = useAtom(sidebarCollapsedAtom);

  return (
    <>
      <aside
        className={`fixed left-0 top-0 h-screen bg-white border-r border-gray-200 transition-all duration-300 z-40 ${
          collapsed ? "w-20" : "w-64"
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold">
                R
              </div>
              {!collapsed && (
                <span className="font-semibold text-gray-900">Raptorflow</span>
              )}
            </Link>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => setCollapsed(!collapsed)}
            >
              {collapsed ? <Menu size={20} /> : <X size={20} />}
            </Button>
          </div>

          <nav className="flex-1 overflow-y-auto p-4">
            <SidebarNav collapsed={collapsed} />
          </nav>

          <div className="p-4 border-t border-gray-200">
            <Button variant="outline" className="w-full text-xs" size="sm">
              {collapsed ? "..." : "Sign Out"}
            </Button>
          </div>
        </div>
      </aside>

      <div className={collapsed ? "ml-20" : "ml-64"} />
    </>
  );
}
