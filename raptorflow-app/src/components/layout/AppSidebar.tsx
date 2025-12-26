'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    Home,
    Layers,
    Users,
    Zap,
    Megaphone,
    Sparkles,
    LayoutGrid,
    Box,
    Settings,
    ChevronDown
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarRail,
    SidebarSeparator,
    SidebarHeader,
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
    { title: 'Home', url: '/dashboard', icon: Home },
    { title: 'Foundation', url: '/foundation', icon: Layers },
    { title: 'Cohorts', url: '/cohorts', icon: Users },
    { title: 'Moves', url: '/moves', icon: Zap },
    { title: 'Campaigns', url: '/campaigns', icon: Megaphone },
    { title: 'Radar', url: '/radar', icon: LayoutGrid },
    { title: 'Muse', url: '/muse', icon: Sparkles },
    { title: 'Blackbox', url: '/blackbox', icon: Box },
];

export function AppSidebar() {
    const pathname = usePathname();

    return (
        <Sidebar
            collapsible="icon"
            variant="sidebar"
            className="border-r border-[#2B3437] bg-[#0E1112]"
        >
            <SidebarHeader className="p-8 pb-4">
                <Link href="/" className="flex items-center gap-4 group transition-all">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#E9ECE6] text-[#0E1112] shadow-[0_0_30px_rgba(255,255,255,0.1)] transition-transform group-hover:scale-105">
                        <span className="text-[14px] font-bold font-sans">RF</span>
                    </div>
                    <div className="flex flex-col group-data-[collapsible=icon]:hidden">
                        <span className="font-serif text-[18px] font-medium text-[#E9ECE6] tracking-tight leading-tight">RaptorFlow</span>
                        <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-[#B8BDB7] opacity-40">Founder OS</span>
                    </div>
                </Link>
            </SidebarHeader>

            <SidebarContent className="px-5 py-8">
                <SidebarGroup>
                    <SidebarGroupContent>
                        <SidebarMenu className="gap-3">
                            {navItems.map((item) => {
                                const isActive = pathname === item.url;
                                return (
                                    <SidebarMenuItem key={item.title}>
                                        <SidebarMenuButton
                                            asChild
                                            isActive={isActive}
                                            tooltip={item.title}
                                            className={cn(
                                                "h-12 px-3 transition-all duration-300 rounded-xl group/item relative overflow-hidden",
                                                isActive
                                                    ? 'bg-[#E9ECE6]/[0.05] text-[#E9ECE6]'
                                                    : 'text-[#B8BDB7] hover:text-[#E9ECE6] hover:bg-[#E9ECE6]/[0.02]'
                                            )}
                                        >
                                            <Link href={item.url} className="flex items-center gap-4 w-full">
                                                <div className="relative z-10">
                                                    <item.icon className={cn(
                                                        "h-[20px] w-[20px] transition-all duration-300",
                                                        isActive ? 'stroke-[2px] opacity-100' : 'stroke-[1.5px] opacity-50 group-hover/item:opacity-100'
                                                    )} />
                                                    {isActive && (
                                                        <motion.div
                                                            layoutId="sidebar-active-dot"
                                                            className="absolute -right-2 -top-1 w-1.5 h-1.5 bg-[#E9ECE6] rounded-full shadow-[0_0_10px_rgba(255,255,255,0.5)]"
                                                        />
                                                    )}
                                                </div>
                                                <span className={cn(
                                                    "text-[15px] tracking-tight transition-all duration-300",
                                                    isActive ? 'font-medium' : 'font-normal opacity-60 group-hover/item:opacity-100'
                                                )}>
                                                    {item.title}
                                                </span>
                                            </Link>
                                        </SidebarMenuButton>
                                    </SidebarMenuItem>
                                )
                            })}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>

            <SidebarFooter className="p-6 border-t border-[#2B3437]">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <SidebarMenuButton
                                    size="lg"
                                    className="data-[state=open]:bg-[#E9ECE6]/[0.05] data-[state=open]:text-[#E9ECE6] rounded-xl hover:bg-[#E9ECE6]/[0.03] transition-all duration-300 px-3"
                                >
                                    <Avatar className="h-9 w-9 rounded-xl border border-[#2B3437]">
                                        <AvatarFallback className="rounded-xl bg-[#141A1C] text-[#E9ECE6] font-medium text-xs">FD</AvatarFallback>
                                    </Avatar>
                                    <div className="grid flex-1 text-left text-sm leading-tight ml-3 group-data-[collapsible=icon]:hidden">
                                        <span className="truncate font-medium text-[#E9ECE6] tracking-tight">Founder</span>
                                        <span className="truncate text-xs text-[#B8BDB7] opacity-40">you@startup.com</span>
                                    </div>
                                    <ChevronDown className="ml-auto h-4 w-4 text-[#B8BDB7] opacity-30 group-data-[collapsible=icon]:hidden" />
                                </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                className="w-[--radix-dropdown-menu-trigger-width] rounded-xl bg-[#141A1C] border-[#2B3437] text-[#E9ECE6]"
                                side="top"
                                align="start"
                                sideOffset={8}
                            >
                                <DropdownMenuItem asChild className="focus:bg-[#E9ECE6]/[0.05] focus:text-[#E9ECE6] cursor-pointer rounded-lg mx-1 my-1">
                                    <Link href="/settings">
                                        <Settings className="mr-3 h-4 w-4 opacity-60" />
                                        <span className="text-[14px]">Settings</span>
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator className="bg-[#2B3437]" />
                                <DropdownMenuItem className="focus:bg-red-500/10 focus:text-red-400 cursor-pointer rounded-lg mx-1 my-1">
                                    <span className="text-[14px]">Log out</span>
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>

            <SidebarRail className="hover:after:bg-[#2B3437]" />
        </Sidebar>
    );
}
