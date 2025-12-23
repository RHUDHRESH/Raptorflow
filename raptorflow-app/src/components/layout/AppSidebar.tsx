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
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Navigation Model as per UI.md (recommended sections)
const navItems = [
    { title: 'Home', url: '/', icon: Home },
    { title: 'Foundation', url: '/foundation', icon: Layers },
    { title: 'Cohorts', url: '/cohorts', icon: Users },
    { title: 'Moves', url: '/moves', icon: Zap },
    { title: 'Campaigns', url: '/campaigns', icon: Megaphone },
    { title: 'Muse', url: '/muse', icon: Sparkles },
    { title: 'Matrix', url: '/matrix', icon: LayoutGrid },
    { title: 'Blackbox', url: '/blackbox', icon: Box },
];

export function AppSidebar() {
    const pathname = usePathname();

    return (
        <Sidebar collapsible="icon" variant="sidebar">
            <SidebarHeader className="p-4 pl-6">
                <Link href="/" className="flex items-center gap-3 font-display text-xl font-semibold tracking-tight text-foreground group-hover:opacity-100 transition-opacity">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground text-background shadow-lg shadow-foreground/20">
                        <span className="text-sm font-bold font-sans">RF</span>
                    </div>
                    <span className="group-data-[collapsible=icon]:hidden opacity-90">RaptorFlow</span>
                </Link>
            </SidebarHeader>

            <SidebarSeparator className="opacity-30 mx-4" />

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
                                            className={`
                                                h-10 px-3 my-0.5 transition-all duration-200 rounded-lg group/item
                                                ${isActive
                                                    ? 'font-medium text-foreground bg-sidebar-accent shadow-sm border-l-[3px] border-foreground rounded-l-none pl-3.5'
                                                    : 'text-muted-foreground/80 hover:text-foreground hover:bg-muted/50 hover:pl-4'
                                                }
                                            `}
                                        >
                                            <Link href={item.url} className="flex items-center gap-3">
                                                <item.icon className={`
                                                    h-[18px] w-[18px] transition-colors
                                                    ${isActive ? 'text-foreground stroke-[2px]' : 'text-muted-foreground stroke-[1.5px] group-hover/item:text-foreground'}
                                                `} />
                                                <span className={`text-[15px] tracking-tight ${isActive ? 'font-semibold' : 'font-medium'}`}>{item.title}</span>
                                            </Link>
                                        </SidebarMenuButton>
                                    </SidebarMenuItem>
                                )
                            })}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>

            <SidebarFooter className="p-4">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <SidebarMenuButton size="lg" className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground rounded-xl hover:bg-muted/50 transition-colors">
                                    <Avatar className="h-9 w-9 rounded-lg border border-border/50">
                                        <AvatarFallback className="rounded-lg bg-muted text-muted-foreground font-medium">FD</AvatarFallback>
                                    </Avatar>
                                    <div className="grid flex-1 text-left text-sm leading-tight ml-1">
                                        <span className="truncate font-semibold tracking-tight">Founder</span>
                                        <span className="truncate text-xs text-muted-foreground">you@startup.com</span>
                                    </div>
                                    <ChevronDown className="ml-auto h-4 w-4 opacity-50" />
                                </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent className="w-[--radix-dropdown-menu-trigger-width] rounded-lg" side="top" align="start" sideOffset={4}>
                                <DropdownMenuItem asChild>
                                    <Link href="/settings" className="cursor-pointer">
                                        <Settings className="mr-2 h-4 w-4" />
                                        Settings
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem>
                                    Log out
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
