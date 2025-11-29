import * as React from "react"
import { NavLink, useLocation } from "react-router-dom"
import { Tooltip, TooltipProvider } from "./ui/tooltip"
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
import { cn } from "../utils/cn"
import { WorkspaceSelector } from "./WorkspaceSelector.tsx"
import { sidebarSections } from "../config/sidebar"

/**
 * Sidebar Content Component
 * 
 * Renders the sidebar navigation using the centralized config.
 * Applies high-fashion SaaS styling with monochrome palette.
 */
const SidebarContentInner = () => {
  const location = useLocation()
  const { open } = useSidebar()

  const renderNavItem = (item) => {
    const Icon = item.icon
    const isActive =
      location.pathname === item.to ||
      (item.to !== "/" && location.pathname.startsWith(item.to))

    const itemContent = (
      <NavLink
        to={item.to}
        className={({ isActive: linkActive }) =>
          cn(
            // Base styles
            "flex items-center h-10 w-full relative transition-all duration-200 ease-out",
            "rounded-lg",
            // Spacing
            !open && "justify-center px-0",
            open && "px-3",
            // Active state - solid dark pill + white text
            linkActive || isActive
              ? "bg-neutral-900 text-white"
              : "text-neutral-400 hover:text-white hover:bg-neutral-900/60"
          )
        }
      >
        {Icon && (
          <Icon
            className={cn(
              "flex-shrink-0 transition-colors",
              isActive ? "text-white opacity-100" : "text-neutral-400 opacity-80"
            )}
            size={18}
            strokeWidth={1.5}
            style={{
              marginRight: open ? "10px" : "0",
            }}
          />
        )}

        {open && (
          <span className="whitespace-nowrap text-[13px] font-medium tracking-[0.01em]">
            {item.label}
          </span>
        )}
      </NavLink>
    )

    if (!open) {
      return (
        <Tooltip content={item.label}>
          {itemContent}
        </Tooltip>
      )
    }

    return itemContent
  }

  return (
    <TooltipProvider>
      <div className="flex flex-col h-full min-h-screen bg-neutral-950">
        {/* Header - Logo/Brand */}
        <SidebarHeader className="px-0 pt-8 pb-0 border-b-0 flex-shrink-0">
          <div
            className={cn(
              "flex items-center w-full h-12 mb-6",
              open ? "px-6 justify-start" : "justify-center"
            )}
          >
            <span
              className="font-display font-bold text-white leading-none"
              style={{
                fontSize: open ? "22px" : "18px",
                letterSpacing: "-0.02em",
              }}
            >
              {open ? "RaptorFlow" : "RF"}
            </span>
          </div>
        </SidebarHeader>

        <SidebarContent className="px-0 flex flex-col flex-1 min-h-0">
          {/* Workspace Selector */}
          <div className={cn("mb-6", open ? "px-4" : "px-2")}>
            <WorkspaceSelector open={open} />
          </div>

          {/* Main Navigation Sections */}
          <div className="flex-1 min-h-0 overflow-y-auto">
            {sidebarSections.map((section, sectionIndex) => (
              <SidebarGroup
                key={section.id}
                className={cn(
                  sectionIndex === 0 ? "flex-1" : "flex-shrink-0",
                  sectionIndex > 0 && "mt-6"
                )}
              >
                {/* Section Label */}
                {open && (
                  <div className="mb-3 px-6">
                    <span className="text-[10px] font-mono font-medium uppercase tracking-[0.15em] text-neutral-500">
                      {section.label}
                    </span>
                  </div>
                )}

                {/* Section Items */}
                <SidebarMenu className={cn("space-y-1", open ? "px-3" : "px-2")}>
                  {section.items.map((item) => (
                    <SidebarMenuItem key={item.id}>
                      {renderNavItem(item)}
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroup>
            ))}
          </div>

          {/* Bottom Padding */}
          <div className="flex-shrink-0 h-6" />
        </SidebarContent>
        <SidebarRail />
      </div>
    </TooltipProvider>
  )
}

/**
 * App Sidebar Component
 * 
 * Main sidebar wrapper with desktop and mobile variants.
 * Width: 260-280px on desktop, collapsible.
 */
export function AppSidebar({ ...props }) {
  const { open } = useSidebar()
  const sidebarWidth = open ? 260 : DESKTOP_SIDEBAR_COLLAPSED_WIDTH

  return (
    <>
      <DesktopSidebar
        {...props}
        className="border-r border-neutral-900/50 bg-neutral-950"
        style={{
          width: sidebarWidth,
          transition: "width 240ms cubic-bezier(0.4, 0, 0.2, 1)",
        }}
      >
        <SidebarContentInner />
      </DesktopSidebar>
      <MobileSidebar {...props} className="bg-neutral-950 border-r border-neutral-900/50">
        <SidebarContentInner />
      </MobileSidebar>
    </>
  )
}
