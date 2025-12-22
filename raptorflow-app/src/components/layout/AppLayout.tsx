'use client';

import React from 'react';
import { AppSidebar } from './AppSidebar';
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { usePathname } from 'next/navigation';

interface AppLayoutProps {
    children: React.ReactNode;
}

/**
 * AppLayout with Shadcn SidebarProvider.
 * Features: Toggleable Sidebar (Cmd+B), Breadcrumbs, Header.
 */
export function AppLayout({ children }: AppLayoutProps) {
    const pathname = usePathname();

    // Generate breadcrumbs from pathname
    const pathSegments = pathname.split('/').filter(Boolean);
    const pageName = pathSegments[pathSegments.length - 1] || 'Dashboard';
    const formattedPageName = pageName.charAt(0).toUpperCase() + pageName.slice(1);

    return (
        <SidebarProvider defaultOpen={true}>
            <AppSidebar />
            <SidebarInset>
                {/* Sticky Header with Sidebar Trigger and Breadcrumbs */}
                <header className="sticky top-0 z-50 flex h-14 shrink-0 items-center gap-2 border-b bg-background/80 backdrop-blur-sm px-4">
                    <SidebarTrigger className="-ml-1" />
                    <Separator orientation="vertical" className="mr-2 h-4" />
                    <Breadcrumb>
                        <BreadcrumbList>
                            <BreadcrumbItem className="hidden md:block">
                                <BreadcrumbLink href="/">
                                    RaptorFlow
                                </BreadcrumbLink>
                            </BreadcrumbItem>
                            {pathSegments.length > 0 && (
                                <>
                                    <BreadcrumbSeparator className="hidden md:block" />
                                    <BreadcrumbItem>
                                        <BreadcrumbPage>{formattedPageName}</BreadcrumbPage>
                                    </BreadcrumbItem>
                                </>
                            )}
                        </BreadcrumbList>
                    </Breadcrumb>
                </header>

                {/* Main Content Area with proper padding */}
                <div className="flex-1 px-8 py-8 md:px-12 md:py-12 max-w-[1200px] mx-auto w-full">
                    {children}
                </div>
            </SidebarInset>
        </SidebarProvider>
    );
}
