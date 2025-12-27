'use client';

import React from 'react';
import { AppSidebar } from './AppSidebar';
import { CommandPalette } from './CommandPalette';
import { SidebarProvider, SidebarInset, SidebarTrigger, useSidebar } from '@/components/ui/sidebar';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Bell,
    Moon,
    Sun,
    Command,
    Wifi,
    WifiOff,
    Plus,
} from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface AppLayoutProps {
    children: React.ReactNode;
    /** When true, removes max-width constraint for full-bleed layouts */
    fullBleed?: boolean;
}

/**
 * Full-rectangle editorial AppLayout that encompasses the entire app.
 * Clean typography, minimal aesthetic, generous whitespace.
 */
export function AppLayout({ children, fullBleed = false }: AppLayoutProps) {
    const pathname = usePathname();
    const { theme, setTheme } = useTheme();
    const [isOnline, setIsOnline] = React.useState(true);
    const [mounted, setMounted] = React.useState(false);

    React.useEffect(() => {
        setMounted(true);
        setIsOnline(navigator.onLine);

        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    // Generate clean page titles from pathname
    const pathSegments = pathname.split('/').filter(Boolean);
    const pageName = pathSegments[pathSegments.length - 1] || 'Overview';

    const formatPageTitle = (name: string) => {
        const titleMap: Record<string, string> = {
            'dashboard': 'Overview',
            'foundation': 'Foundation',
            'cohorts': 'Cohorts',
            'moves': 'Moves',
            'campaigns': 'Campaigns',
            'radar': 'Radar',
            'muse': 'Muse Studio',
            'blackbox': 'Blackbox',
            'settings': 'Settings'
        };
        return titleMap[name] || name.charAt(0).toUpperCase() + name.slice(1);
    };

    const pageTitle = formatPageTitle(pageName);

    return (
        <SidebarProvider defaultOpen={true}>
            <AppSidebar />
            <CommandPalette />
            <SidebarInset className={cn(
                "transition-colors duration-500",
                fullBleed && "bg-transparent"
            )}>
                {/* Enhanced Editorial Header */}
                <header className={cn(
                    "sticky top-0 z-50 flex h-14 shrink-0 items-center transition-all duration-300",
                    "bg-background/80 dark:bg-background/80 backdrop-blur-xl",
                    "border-b border-sidebar-border/50",
                    fullBleed && "bg-background/80 dark:bg-background/80 border-transparent"
                )}>
                    <div className="flex items-center gap-4 px-4 w-full">
                        {/* Sidebar Toggle */}
                        <SidebarTrigger className="-ml-1 h-8 w-8 text-gray-500 hover:text-gray-900 dark:text-[#8a9298] dark:hover:text-[#E9ECE6] hover:bg-gray-100 dark:hover:bg-[#E9ECE6]/[0.05] rounded-lg transition-colors" />

                        {/* Breadcrumb / Title Section */}
                        <div className="flex-1">
                            <div className="flex items-center gap-2">
                                <motion.span
                                    className="text-[11px] font-medium text-gray-400 dark:text-[#5a6268] tracking-widest uppercase"
                                    initial={{ opacity: 0, y: -5 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    key="brand"
                                >
                                    RaptorFlow
                                </motion.span>
                                {pathSegments.length > 0 && (
                                    <>
                                        <span className="text-gray-300 dark:text-[#2b3134]">/</span>
                                        <motion.span
                                            className="text-[14px] font-medium text-gray-800 dark:text-[#E9ECE6]"
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            key={pageTitle}
                                        >
                                            {pageTitle}
                                        </motion.span>
                                    </>
                                )}
                            </div>
                        </div>

                        {/* Action Bar */}
                        <div className="flex items-center gap-1">
                            {/* Command Palette Trigger */}
                            <TooltipProvider delayDuration={0}>
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-8 gap-2 text-gray-500 dark:text-[#8a9298] hover:text-gray-900 dark:hover:text-[#E9ECE6] hover:bg-gray-100 dark:hover:bg-[#E9ECE6]/[0.05] rounded-lg px-2"
                                            onClick={() => {
                                                // Trigger command palette
                                                const event = new KeyboardEvent('keydown', {
                                                    key: 'k',
                                                    ctrlKey: true,
                                                    bubbles: true
                                                });
                                                document.dispatchEvent(event);
                                            }}
                                        >
                                            <Command className="h-3.5 w-3.5" />
                                            <span className="text-[11px] hidden sm:inline">Search</span>
                                            <kbd className="hidden sm:inline px-1.5 py-0.5 rounded bg-gray-100 dark:bg-[#1e2326] border border-gray-200 dark:border-[#2b3134] text-[10px] font-mono text-gray-400 dark:text-[#5a6268]">
                                                ⌘K
                                            </kbd>
                                        </Button>
                                    </TooltipTrigger>
                                    <TooltipContent side="bottom" className="text-xs">
                                        Command Palette
                                    </TooltipContent>
                                </Tooltip>
                            </TooltipProvider>

                            {/* Status Indicator */}
                            <TooltipProvider delayDuration={0}>
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 text-gray-500 dark:text-[#8a9298] hover:bg-gray-100 dark:hover:bg-[#E9ECE6]/[0.05] rounded-lg"
                                        >
                                            {isOnline ? (
                                                <Wifi className="h-3.5 w-3.5 text-emerald-500" />
                                            ) : (
                                                <WifiOff className="h-3.5 w-3.5 text-red-400" />
                                            )}
                                        </Button>
                                    </TooltipTrigger>
                                    <TooltipContent side="bottom" className="text-xs">
                                        {isOnline ? 'Connected' : 'Offline'}
                                    </TooltipContent>
                                </Tooltip>
                            </TooltipProvider>

                            {/* Notifications */}
                            <TooltipProvider delayDuration={0}>
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 text-gray-500 dark:text-[#8a9298] hover:text-gray-900 dark:hover:text-[#E9ECE6] hover:bg-gray-100 dark:hover:bg-[#E9ECE6]/[0.05] rounded-lg relative"
                                        >
                                            <Bell className="h-3.5 w-3.5" />
                                            {/* Notification dot */}
                                            <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.5)]" />
                                        </Button>
                                    </TooltipTrigger>
                                    <TooltipContent side="bottom" className="text-xs">
                                        Notifications
                                    </TooltipContent>
                                </Tooltip>
                            </TooltipProvider>

                            {/* Theme Toggle */}
                            {mounted && (
                                <TooltipProvider delayDuration={0}>
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 text-gray-500 dark:text-[#8a9298] hover:text-gray-900 dark:hover:text-[#E9ECE6] hover:bg-gray-100 dark:hover:bg-[#E9ECE6]/[0.05] rounded-lg"
                                                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                                            >
                                                <AnimatePresence mode="wait" initial={false}>
                                                    {theme === 'dark' ? (
                                                        <motion.div
                                                            key="sun"
                                                            initial={{ rotate: -90, opacity: 0 }}
                                                            animate={{ rotate: 0, opacity: 1 }}
                                                            exit={{ rotate: 90, opacity: 0 }}
                                                            transition={{ duration: 0.15 }}
                                                        >
                                                            <Sun className="h-3.5 w-3.5" />
                                                        </motion.div>
                                                    ) : (
                                                        <motion.div
                                                            key="moon"
                                                            initial={{ rotate: 90, opacity: 0 }}
                                                            animate={{ rotate: 0, opacity: 1 }}
                                                            exit={{ rotate: -90, opacity: 0 }}
                                                            transition={{ duration: 0.15 }}
                                                        >
                                                            <Moon className="h-3.5 w-3.5" />
                                                        </motion.div>
                                                    )}
                                                </AnimatePresence>
                                            </Button>
                                        </TooltipTrigger>
                                        <TooltipContent side="bottom" className="text-xs">
                                            {theme === 'dark' ? 'Light mode' : 'Dark mode'}
                                        </TooltipContent>
                                    </Tooltip>
                                </TooltipProvider>
                            )}

                            {/* Quick Add */}
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button
                                        size="sm"
                                        className="h-8 gap-1.5 ml-2 bg-gray-900 hover:bg-gray-800 dark:bg-[#E9ECE6] dark:hover:bg-[#d4d8ce] text-white dark:text-[#0E1112] rounded-lg text-[12px] font-medium shadow-sm"
                                    >
                                        <Plus className="h-3.5 w-3.5" />
                                        <span className="hidden sm:inline">New</span>
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-48 rounded-xl dark:bg-[#141618] dark:border-[#1e2326]">
                                    <DropdownMenuItem className="cursor-pointer rounded-lg dark:focus:bg-[#E9ECE6]/[0.05]">
                                        <span className="text-[13px]">New Move</span>
                                        <span className="ml-auto text-[10px] text-gray-400 dark:text-[#5a6268]">⌘M</span>
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="cursor-pointer rounded-lg dark:focus:bg-[#E9ECE6]/[0.05]">
                                        <span className="text-[13px]">New Campaign</span>
                                        <span className="ml-auto text-[10px] text-gray-400 dark:text-[#5a6268]">⌘N</span>
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="cursor-pointer rounded-lg dark:focus:bg-[#E9ECE6]/[0.05]">
                                        <span className="text-[13px]">Generate with Muse</span>
                                        <span className="ml-auto text-[10px] text-gray-400 dark:text-[#5a6268]">⌘G</span>
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </div>
                    </div>
                </header>

                {/* Full Rectangle Content Area */}
                <main className={cn(
                    "flex-1 min-h-[calc(100vh-3.5rem)]",
                    fullBleed
                        ? "w-full bg-background"
                        : "mx-auto max-w-none bg-background"
                )}>
                    {children}
                </main>
            </SidebarInset>
        </SidebarProvider>
    );
}
