'use client';

import React from 'react';
import { AppSidebar } from './AppSidebar';
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

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

    // Generate clean page titles from pathname
    const pathSegments = pathname.split('/').filter(Boolean);
    const pageName = pathSegments[pathSegments.length - 1] || 'Overview';

    const formatPageTitle = (name: string) => {
        const titleMap: Record<string, string> = {
            'dashboard': 'Overview',
            'muse': 'Studio',
            'library': 'Library',
            'campaigns': 'Campaigns',
            'analytics': 'Analytics',
            'settings': 'Settings'
        };
        return titleMap[name] || name.charAt(0).toUpperCase() + name.slice(1);
    };

    const pageTitle = formatPageTitle(pageName);

    return (
        <SidebarProvider defaultOpen={true}>
            <AppSidebar />
            <SidebarInset className={cn("bg-white", fullBleed && "bg-[#F8F9F7]")}>
                {/* Clean Editorial Header */}
                <header className={cn(
                    "sticky top-0 z-50 flex h-16 shrink-0 items-center border-b border-gray-100 bg-white transition-colors duration-300",
                    fullBleed && "bg-[#F8F9F7] border-transparent"
                )}>
                    <div className="flex items-center gap-4 px-6 w-full">
                        <SidebarTrigger className="-ml-1 text-gray-600 hover:text-gray-900" />

                        {/* Clean Title Section */}
                        <div className="flex-1">
                            <div className="flex items-baseline gap-3">
                                <h1 className="text-sm font-medium text-gray-400 tracking-wide uppercase">
                                    RaptorFlow
                                </h1>
                                {pathSegments.length > 0 && (
                                    <>
                                        <span className="text-gray-300">/</span>
                                        <h2 className="text-lg font-light text-gray-900">
                                            {pageTitle}
                                        </h2>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </header>

                {/* Full Rectangle Content Area */}
                <main className={cn(
                    "flex-1 min-h-[calc(100vh-4rem)]",
                    fullBleed ? "w-full bg-[#F8F9F7]" : "mx-auto max-w-none bg-white"
                )}>
                    {children}
                </main>
            </SidebarInset>
        </SidebarProvider>
    );
}
