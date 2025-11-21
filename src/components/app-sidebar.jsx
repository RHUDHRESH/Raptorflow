import * as React from "react"
import { Link, useLocation } from "react-router-dom"
import { motion } from "framer-motion"
import {
  LayoutDashboard,
  Target,
  TrendingUp,
  Users,
  FileText,
  Clock,
  HelpCircle,
  Sparkles,
  Settings,
  User,
  BookOpen,
  Network,
  Calendar,
  Library,
  Zap
} from "lucide-react"
import {
  DesktopSidebar,
  MobileSidebar,
  SidebarContent,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from "./ui/sidebar"
import { cn } from "../utils/cn"

const navigationItems = [
  { title: "Runway Dispatch", icon: LayoutDashboard, url: "/" },
  { title: "War Room", icon: Target, url: "/moves/war-room" },
  { title: "Moves & Maneuvers", icon: Library, url: "/moves/library" },
  { title: "Quests & Tech Tree", icon: Network, url: "/quests" },
  { title: "Daily Ops", icon: Calendar, url: "/today" },
  { title: "Daily Sweep", icon: Zap, url: "/daily-sweep" },
  { title: "Strategy Atelier", icon: Sparkles, url: "/strategy" },
  { title: "Insights Studio", icon: TrendingUp, url: "/analytics" },
  { title: "Editorial Recap", icon: Clock, url: "/review" },
  { title: "Audience Archive", icon: Users, url: "/cohorts" },
  { title: "Archive Ledger", icon: FileText, url: "/history" },
]

const settingsItems = [
  { title: "Studio Controls", icon: Settings, url: "/settings" },
  { title: "Portrait", icon: User, url: "/account" },
  { title: "Concierge Desk", icon: HelpCircle, url: "/support" },
]

const SidebarContentInner = () => {
  const location = useLocation()
  const { open, animate } = useSidebar()

  return (
    <>
      <SidebarHeader className="px-4 pt-8 pb-6">
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full border border-neutral-200 bg-white text-neutral-900">
              <LayoutDashboard className="h-4 w-4" />
            </div>
            {open && (
              <div>
                <p className="font-display text-xl text-neutral-900">Raptorflow</p>
              </div>
            )}
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent className="px-3 flex flex-col">
        <SidebarGroup className="space-y-1 flex-1">
          <SidebarMenu className="space-y-1.5">
            {navigationItems.map((item) => {
              const Icon = item.icon
              const isActive =
                location.pathname === item.url ||
                (item.url !== "/" && location.pathname.startsWith(item.url))

              return (
                <SidebarMenuItem key={item.title}>
                  <Link
                    to={item.url}
                    className={cn(
                      "flex items-center rounded-2xl border border-transparent px-3 py-2 text-[13px] font-medium uppercase tracking-[0.2em] transition-all duration-200",
                      isActive
                        ? "border-neutral-900 bg-neutral-900 text-white"
                        : "text-neutral-500 hover:border-neutral-200 hover:bg-white hover:text-neutral-900",
                      !open && "justify-center"
                    )}
                  >
                    {Icon && <Icon className="h-4 w-4 flex-shrink-0" />}
                    <motion.span
                      className="whitespace-nowrap overflow-hidden"
                      animate={{
                        opacity: animate ? (open ? 1 : 0) : 0,
                        width: animate ? (open ? "auto" : "0px") : "0px",
                        marginLeft: animate ? (open ? "12px" : "0px") : "0px",
                      }}
                      transition={{ duration: 0.2 }}
                    >
                      {item.title}
                    </motion.span>
                  </Link>
                </SidebarMenuItem>
              )
            })}
          </SidebarMenu>
        </SidebarGroup>
        <SidebarGroup className="space-y-1 mt-auto pt-4 border-t border-neutral-200">
          <SidebarMenu className="space-y-1.5">
            {settingsItems.map((item) => {
              const Icon = item.icon
              const isActive =
                location.pathname === item.url ||
                (item.url !== "/" && location.pathname.startsWith(item.url))

              return (
                <SidebarMenuItem key={item.title}>
                  <Link
                    to={item.url}
                    className={cn(
                      "flex items-center rounded-2xl border border-transparent px-3 py-2 text-[13px] font-medium uppercase tracking-[0.2em] transition-all duration-200",
                      isActive
                        ? "border-neutral-900 bg-neutral-900 text-white"
                        : "text-neutral-500 hover:border-neutral-200 hover:bg-white hover:text-neutral-900",
                      !open && "justify-center"
                    )}
                  >
                    {Icon && <Icon className="h-4 w-4 flex-shrink-0" />}
                    <motion.span
                      className="whitespace-nowrap overflow-hidden"
                      animate={{
                        opacity: animate ? (open ? 1 : 0) : 0,
                        width: animate ? (open ? "auto" : "0px") : "0px",
                        marginLeft: animate ? (open ? "12px" : "0px") : "0px",
                      }}
                      transition={{ duration: 0.2 }}
                    >
                      {item.title}
                    </motion.span>
                  </Link>
                </SidebarMenuItem>
              )
            })}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarRail />
    </>
  )
}

export function AppSidebar({ ...props }) {
  return (
    <>
      <DesktopSidebar {...props} className="border-r border-neutral-200/70 bg-white/90 backdrop-blur-2xl">
        <SidebarContentInner />
      </DesktopSidebar>
      <MobileSidebar {...props} className="bg-white/95">
        <SidebarContentInner />
      </MobileSidebar>
    </>
  )
}
