'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    DashboardIcon,
    FoundationIcon,
    CohortsIcon,
    MovesIcon,
    CampaignsIcon,
    MuseIcon,
    MatrixIcon,
    BlackboxIcon,
    AppearanceIcon // Using AppearanceIcon for Settings as a placeholder or reuse
} from '@/components/ui/icons';

/**
 * Sidebar — Following COMPONENTS.md and UI.md spec
 * 
 * Width: 220px/240px (using w-60 aka 240px for comfortable spacing)
 * Background: surface
 * Typography: Inter Medium 13px/14px
 */

const NAV_ITEMS = [
    { name: 'Dashboard', href: '/', icon: DashboardIcon },
    { name: 'Foundation', href: '/foundation', icon: FoundationIcon },
    { name: 'Cohorts', href: '/cohorts', icon: CohortsIcon },
    { name: 'Moves', href: '/moves', icon: MovesIcon },
    { name: 'Campaigns', href: '/campaigns', icon: CampaignsIcon },
    { name: 'Muse', href: '/muse', icon: MuseIcon },
    { name: 'Matrix', href: '/matrix', icon: MatrixIcon },
    { name: 'Blackbox', href: '/blackbox', icon: BlackboxIcon },
];

const BOTTOM_ITEMS = [
    { name: 'Settings', href: '/settings', icon: AppearanceIcon }, // Using AppearanceIcon as generic settings gear-ish
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 h-screen w-60 flex flex-col border-r border-border bg-sidebar px-3 py-5 z-50">
            {/* Logo */}
            <div className="flex items-center gap-3 px-3 mb-8">
                <div className="flex items-center justify-center h-8 w-8 rounded-md bg-foreground text-background font-semibold text-sm">
                    RF
                </div>
                <span className="font-semibold text-lg tracking-tight text-foreground">
                    RaptorFlow
                </span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 flex flex-col space-y-0.5">
                {NAV_ITEMS.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`
                                group flex items-center gap-3 px-3 h-10 rounded-md text-sm font-medium transition-colors
                                ${isActive
                                    ? 'bg-sidebar-accent text-sidebar-primary'
                                    : 'text-muted-foreground hover:bg-sidebar-accent hover:text-foreground'
                                }
                            `}
                        >
                            <item.icon
                                size={18}
                                className={`
                                    transition-opacity
                                    ${isActive ? 'opacity-100' : 'opacity-70 group-hover:opacity-100'}
                                `}
                            />
                            {item.name}
                        </Link>
                    );
                })}

                {/* Bottom Section */}
                <div className="mt-auto pt-4">
                    <div className="h-px bg-border mx-3 mb-4" />
                    {BOTTOM_ITEMS.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`
                                    group flex items-center gap-3 px-3 h-10 rounded-md text-sm font-medium transition-colors
                                    ${isActive
                                        ? 'bg-sidebar-accent text-sidebar-primary'
                                        : 'text-muted-foreground hover:bg-sidebar-accent hover:text-foreground'
                                    }
                                `}
                            >
                                <item.icon
                                    size={18}
                                    className={`
                                        transition-opacity
                                        ${isActive ? 'opacity-100' : 'opacity-70 group-hover:opacity-100'}
                                    `}
                                />
                                {item.name}
                            </Link>
                        );
                    })}
                </div>
            </nav>
        </aside>
    );
}
