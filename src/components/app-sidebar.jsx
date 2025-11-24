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
  Activity,
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
  DESKTOP_SIDEBAR_WIDTH,
  DESKTOP_SIDEBAR_COLLAPSED_WIDTH,
} from "./ui/sidebar"
import { Tooltip, TooltipProvider } from "./ui/tooltip"
import { cn } from "../utils/cn"

const navigationItems = [
  { title: "Command Center", icon: LayoutDashboard, url: "/" },
  { title: "War Room", icon: Target, url: "/moves/war-room" },
  { title: "Move Library", icon: Library, url: "/moves/library" },
  { title: "Muse", icon: Sparkles, url: "/muse" },
  { title: "Matrix", icon: Activity, url: "/matrix" },
  { title: "Tech Tree", icon: Network, url: "/quests" },
  { title: "Daily Ops", icon: Calendar, url: "/today" },
  { title: "Daily Sweep", icon: Zap, url: "/daily-sweep" },
  { title: "Strategy Atelier", icon: Sparkles, url: "/strategy" },
  { title: "Performance", icon: TrendingUp, url: "/analytics" },
  { title: "Cohorts", icon: Users, url: "/cohorts" },
  { title: "Archive", icon: FileText, url: "/history" },
]

const settingsItems = [
  { title: "Settings", icon: Settings, url: "/settings" },
  { title: "Account", icon: User, url: "/account" },
  { title: "Support", icon: HelpCircle, url: "/support" },
]

const SidebarContentInner = () => {
  const location = useLocation()
  const { open } = useSidebar()

  const renderNavItem = (item, isSystem = false) => {
    const Icon = item.icon
    const isActive =
      location.pathname === item.url ||
      (item.url !== "/" && location.pathname.startsWith(item.url))

    const itemContent = (
      <div className="relative w-full">
        {/* Active left border */}
        {isActive && open && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: 2 }}
            transition={{ duration: 0.18 }}
            className="absolute left-0 top-0 bottom-0 z-10 bg-white rounded-r-sm"
          />
        )}
        
        <Link
          to={item.url}
          className={cn(
            "flex items-center h-10 w-full relative transition-all duration-180 ease-out cursor-pointer",
            "hover:bg-white/10",
            isActive && "bg-white/[0.15]",
            !open && "justify-center px-0",
            open && "px-6"
          )}
        >
          {Icon && (
            <Icon 
              className="flex-shrink-0"
              size={open ? 18 : 20}
              strokeWidth={1.5}
              style={{
                color: isActive ? "#FFFFFF" : "rgba(255, 255, 255, 0.7)",
                marginRight: open ? "12px" : "0",
              }}
            />
          )}
          
          {open && (
            <span
              className="whitespace-nowrap flex-shrink-0 text-sm font-medium"
              style={{
                letterSpacing: "0.02em",
                color: isActive ? "#FFFFFF" : "rgba(255, 255, 255, 0.7)",
              }}
            >
              {item.title}
            </span>
          )}
        </Link>
      </div>
    )

    if (!open) {
      return (
        <Tooltip content={item.title}>
          {itemContent}
        </Tooltip>
      )
    }

    return itemContent
  }

  return (
    <TooltipProvider>
      <div className="flex flex-col h-full">
        <SidebarHeader className="px-0 pt-8 pb-0 border-b-0 flex-shrink-0">
          <div 
            className={cn(
              "flex items-center w-full h-12",
              open ? "px-6 justify-start" : "justify-center"
            )}
          >
            <span 
              className="font-serif font-bold text-white leading-none"
              style={{
                fontSize: open ? "28px" : "24px",
                letterSpacing: "-0.02em",
              }}
            >
              {open ? "RaptorFlow" : "RF"}
            </span>
          </div>
        </SidebarHeader>
        
        <SidebarContent className="px-0 flex flex-col flex-1 min-h-0 pt-8">
          {/* Primary Navigation Section */}
          <SidebarGroup className="flex-1 min-h-0 overflow-y-auto">
            {open && (
              <div className="mb-4 px-6">
                <span className="text-xs font-mono font-medium uppercase tracking-widest text-white/30">
                  Workspace
                </span>
              </div>
            )}
            
            <SidebarMenu className="space-y-1">
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  {renderNavItem(item, false)}
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>

          {/* Divider */}
          <div 
            className={cn(
              "flex-shrink-0 h-px bg-white/10 my-4",
              open ? "mx-6" : "mx-3"
            )}
          />

          {/* System Controls Section */}
          <SidebarGroup className="flex-shrink-0 pb-6">
            {open && (
              <div className="mb-4 px-6">
                <span className="text-xs font-mono font-medium uppercase tracking-widest text-white/30">
                  System
                </span>
              </div>
            )}
            
            <SidebarMenu className="space-y-1">
              {settingsItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  {renderNavItem(item, true)}
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>
        </SidebarContent>
        <SidebarRail />
      </div>
    </TooltipProvider>
  )
}

export function AppSidebar({ ...props }) {
  const { open } = useSidebar()
  const sidebarWidth = open ? DESKTOP_SIDEBAR_WIDTH : DESKTOP_SIDEBAR_COLLAPSED_WIDTH

  return (
    <>
      <DesktopSidebar
        {...props}
        className="border-r border-white/10 bg-black"
        style={{
          width: sidebarWidth,
          transition: "width 240ms ease-out",
        }}
      >
        <SidebarContentInner />
      </DesktopSidebar>
      <MobileSidebar {...props} className="bg-white">
        <div className="text-black">
          <SidebarContentInner />
        </div>
      </MobileSidebar>
    </>
  )
}
