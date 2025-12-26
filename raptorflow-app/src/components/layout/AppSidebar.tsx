'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    Home01Icon,
    Layers01Icon,
    UserGroupIcon,
    FlashIcon,
    Megaphone01Icon,
    DashboardSquare01Icon,
    SparklesIcon,
    PackageIcon,
    Settings01Icon,
    ArrowDown01Icon,
    PlusSignIcon
} from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarRail,
} from '@/components/ui/sidebar';
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Navigation as per UI.md + Foundation Vibe
const navItems = [
    { title: 'Home', url: '/dashboard', icon: Home01Icon },
    { title: 'Foundation', url: '/foundation', icon: Layers01Icon },
    { title: 'Cohorts', url: '/cohorts', icon: UserGroupIcon },
    { title: 'Moves', url: '/moves', icon: FlashIcon },
    { title: 'Campaigns', url: '/campaigns', icon: Megaphone01Icon },
    { title: 'Radar', url: '/radar', icon: DashboardSquare01Icon },
    { title: 'Muse', url: '/muse', icon: SparklesIcon },
    { title: 'Blackbox', url: '/blackbox', icon: PackageIcon },
];

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
    const pathname = usePathname();

    return (
        <Sidebar
            collapsible="icon"
            variant="sidebar"
            className="border-r border-sidebar-border bg-sidebar"
            {...props}
        >
            <SidebarHeader className="p-6 pb-2">
                <Link href="/" className="flex items-center gap-3 group transition-all">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground shadow-sm transition-transform group-hover:scale-105">
                        <span className="text-sm font-bold font-sans tracking-tight">RF</span>
                    </div>
                    <div className="flex flex-col group-data-[collapsible=icon]:hidden overflow-hidden transition-all duration-300">
                        <span className="font-serif text-lg font-medium text-sidebar-foreground tracking-tight leading-none">RaptorFlow</span>
                        <span className="text-[10px] font-mono uppercase tracking-[0.25em] text-muted-foreground/60 mt-1">Founder OS</span>
                    </div>
                </Link>
            </SidebarHeader>

            <SidebarContent className="px-3 py-6">
                <SidebarGroup>
                    <SidebarGroupContent>
                        <SidebarMenu className="gap-2">
                            {navItems.map((item) => {
                                const isActive = pathname === item.url;
                                return (
                                    <SidebarMenuItem key={item.title}>
                                        <SidebarMenuButton
                                            asChild
                                            isActive={isActive}
                                            tooltip={item.title}
                                            className={cn(
                                                "h-10 px-3 rounded-lg group/item relative overflow-hidden transition-all duration-200",
                                                isActive
                                                    ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                                                    : 'text-muted-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent/50'
                                            )}
                                        >
                                            <Link href={item.url} className="flex items-center gap-3 w-full">
                                                <HugeiconsIcon icon={item.icon}
                                                    className={cn(
                                                        "h-[18px] w-[18px] transition-all duration-200",
                                                        isActive ? 'opacity-100' : 'opacity-70 group-hover/item:opacity-100'
                                                    )}
                                                />
                                                <span className="text-sm tracking-tight truncate">
                                                    {item.title}
                                                </span>
                                                {isActive && (
                                                    <motion.div
                                                        layoutId="sidebar-active-indicator"
                                                        className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-sidebar-primary rounded-r-full"
                                                        initial={{ opacity: 0 }}
                                                        animate={{ opacity: 1 }}
                                                        exit={{ opacity: 0 }}
                                                    />
                                                )}
                                            </Link>
                                        </SidebarMenuButton>
                                    </SidebarMenuItem>
                                )
                            })}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>

            <SidebarFooter className="p-4 border-t border-sidebar-border/50">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <SidebarMenuButton
                                    size="lg"
                                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground rounded-lg hover:bg-sidebar-accent/50 transition-all duration-200 px-3 group/user"
                                >
                                    <Avatar className="h-8 w-8 rounded-lg border border-sidebar-border/50">
                                        <AvatarFallback className="rounded-lg bg-sidebar-accent text-sidebar-foreground text-xs font-medium">FD</AvatarFallback>
                                    </Avatar>
                                    <div className="grid flex-1 text-left text-sm leading-tight ml-3 group-data-[collapsible=icon]:hidden">
                                        <span className="truncate font-medium text-sidebar-foreground">Founder</span>
                                        <span className="truncate text-xs text-muted-foreground">you@startup.com</span>
                                    </div>
                                    <HugeiconsIcon icon={ArrowDown01Icon} className="ml-auto h-4 w-4 text-muted-foreground/50 transition-transform group-data-[state=open]/user:rotate-180 group-data-[collapsible=icon]:hidden" />
                                </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg bg-sidebar border-sidebar-border text-sidebar-foreground"
                                side="top"
                                align="start"
                                sideOffset={8}
                            >
                                <DropdownMenuItem className="cursor-pointer rounded-md focus:bg-sidebar-accent focus:text-sidebar-accent-foreground">
                                    <HugeiconsIcon icon={PlusSignIcon} className="mr-2 h-4 w-4 opacity-70" />
                                    <span>New Workspace</span>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator className="bg-sidebar-border/50" />
                                <DropdownMenuItem asChild className="cursor-pointer rounded-md focus:bg-sidebar-accent focus:text-sidebar-accent-foreground">
                                    <Link href="/settings">
                                        <HugeiconsIcon icon={Settings01Icon} className="mr-2 h-4 w-4 opacity-70" />
                                        <span>Settings</span>
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator className="bg-sidebar-border/50" />
                                <DropdownMenuItem className="focus:bg-destructive/10 focus:text-destructive cursor-pointer rounded-md text-red-500/80 focus:text-red-500">
                                    <span>Log out</span>
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>

            <SidebarRail />
        </Sidebar>
    );
}
