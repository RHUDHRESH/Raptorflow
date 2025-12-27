"use client"

import * as React from "react"
import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import {
    ChevronRight,
    Search,
    Settings,
    LayoutDashboard,
    Users,
    Map,
    Target,
    Sparkles,
    Box,
    Radar,
    LogOut,
    Plus,
    CreditCard,
    Bell,
    BookOpen,
    Layers,
    Radio,
    BrainCircuit
} from "lucide-react"

import { SearchForm } from "./SearchForm"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarRail,
    SidebarSeparator,
    useSidebar,
} from "@/components/ui/sidebar"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

// RaptorFlow Navigation Data
const items = {
    platform: [
        {
            title: "Overview",
            subtitle: "Command Center",
            url: "/dashboard",
            icon: LayoutDashboard,
        },
        {
            title: "Moves",
            subtitle: "Weekly Execution",
            url: "/moves",
            icon: Target,
        },
        {
            title: "Campaigns",
            subtitle: "Growth Initiatives",
            url: "/campaigns",
            icon: Layers,
        },
    ],
    intelligence: [
        {
            title: "Radar",
            subtitle: "Market Intelligence",
            url: "/radar",
            icon: Radio,
        },
        {
            title: "Muse Studio",
            subtitle: "Creative Engine",
            url: "/muse",
            icon: Sparkles,
        },
        {
            title: "Blackbox",
            subtitle: "Learning & Insights",
            url: "/blackbox",
            icon: BrainCircuit,
        },
    ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
    const pathname = usePathname()
    const { state } = useSidebar()

    return (
        <Sidebar collapsible="icon" className="border-r border-sidebar-border/50 bg-sidebar" {...props}>
            <SidebarHeader className="h-14 flex items-center justify-center px-4 mb-2 pt-4">
                <Link href="/" className="block group-data-[collapsible=icon]:hidden w-full flex justify-center">
                    <Image
                        src="/logo_primary.png"
                        alt="RaptorFlow — Founder OS"
                        width={180}
                        height={52}
                        className="object-contain"
                        priority
                    />
                </Link>
                {/* Collapsed state: show just the icon portion */}
                <Link href="/" className="hidden group-data-[collapsible=icon]:block">
                    <Image
                        src="/logo_primary.png"
                        alt="RaptorFlow"
                        width={28}
                        height={28}
                        className="object-contain"
                        priority
                    />
                </Link>
            </SidebarHeader>
            <SearchForm />
            <SidebarContent className="px-2 py-1">
                {Object.entries(items).map(([groupTitle, groupItems]) => (
                    <SidebarGroup key={groupTitle} className="py-1">
                        <SidebarGroupLabel className="hidden">
                            {groupTitle}
                        </SidebarGroupLabel>
                        <SidebarMenu className="gap-0.5">
                            {groupItems.map((item) => {
                                const isActive = pathname === item.url

                                return (
                                    <SidebarMenuItem key={item.title}>
                                        <SidebarMenuButton
                                            asChild
                                            isActive={isActive}
                                            tooltip={item.title}
                                            className={cn(
                                                "transition-all duration-150 h-10 rounded-md",
                                                isActive
                                                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                                                    : "text-muted-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent/40"
                                            )}
                                        >
                                            <Link href={item.url} className="flex items-center gap-3 w-full px-2">
                                                {item.icon && <item.icon className={cn("size-4 shrink-0", isActive ? "opacity-100" : "opacity-60")} strokeWidth={1.5} />}
                                                <div className="flex flex-col items-start gap-0 overflow-hidden group-data-[collapsible=icon]:hidden">
                                                    <span className="text-sm font-medium leading-tight">{item.title}</span>
                                                    <span className={cn(
                                                        "text-[11px] font-normal text-muted-foreground/50 leading-tight",
                                                        isActive && "text-sidebar-accent-foreground/60"
                                                    )}>
                                                        {item.subtitle}
                                                    </span>
                                                </div>
                                            </Link>
                                        </SidebarMenuButton>
                                    </SidebarMenuItem>
                                )
                            })}
                        </SidebarMenu>
                    </SidebarGroup>
                ))}
            </SidebarContent>

            <SidebarFooter className="p-2">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <SidebarMenuButton
                                    size="default"
                                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground transition-all duration-150 h-10"
                                >
                                    <Avatar className="h-7 w-7 rounded-md border border-sidebar-border/30">
                                        <AvatarImage src="/avatars/user.jpg" alt="Founder" />
                                        <AvatarFallback className="rounded-md bg-sidebar-accent font-medium text-xs">FD</AvatarFallback>
                                    </Avatar>
                                    <div className="grid flex-1 text-left text-sm leading-tight group-data-[collapsible=icon]:hidden">
                                        <span className="truncate font-medium text-sm">Founder</span>
                                        <span className="truncate text-[11px] text-muted-foreground/60">Pro Plan</span>
                                    </div>
                                    <ChevronRight className="ml-auto size-4 transition-transform duration-150 group-data-[state=open]:rotate-90 group-data-[collapsible=icon]:hidden opacity-50" />
                                </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg bg-popover text-popover-foreground border-border shadow-lg"
                                side="bottom"
                                align="end"
                                sideOffset={4}
                            >
                                <DropdownMenuLabel className="p-0 font-normal">
                                    <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                                        <Avatar className="h-8 w-8 rounded-lg">
                                            <AvatarFallback className="rounded-lg bg-primary/10 text-primary">FD</AvatarFallback>
                                        </Avatar>
                                        <div className="grid flex-1 text-left text-sm leading-tight">
                                            <span className="truncate font-semibold">Founder</span>
                                            <span className="truncate text-xs text-muted-foreground">founder@raptorflow.com</span>
                                        </div>
                                    </div>
                                </DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuGroup>
                                    <DropdownMenuItem className="gap-2 cursor-pointer">
                                        <Sparkles className="h-4 w-4 text-amber-500" />
                                        Upgrade to Pro
                                    </DropdownMenuItem>
                                </DropdownMenuGroup>
                                <DropdownMenuSeparator />
                                <DropdownMenuGroup>
                                    <DropdownMenuItem className="gap-2 cursor-pointer">
                                        <CreditCard className="h-4 w-4 text-muted-foreground" />
                                        Billing
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="gap-2 cursor-pointer">
                                        <Settings className="h-4 w-4 text-muted-foreground" />
                                        Settings
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="gap-2 cursor-pointer">
                                        <Bell className="h-4 w-4 text-muted-foreground" />
                                        Notifications
                                    </DropdownMenuItem>
                                </DropdownMenuGroup>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem className="gap-2 text-destructive focus:text-destructive cursor-pointer">
                                    <LogOut className="h-4 w-4" />
                                    Log out
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
            <SidebarRail />
        </Sidebar>
    )
}
