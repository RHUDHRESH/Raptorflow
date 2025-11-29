import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    Target,
    Users,
    Zap,
    FileText,
    Settings
} from 'lucide-react';

/**
 * Navigation Item Type
 */
interface NavItem {
    label: string;
    href: string;
    icon: React.ComponentType<{ className?: string }>;
    disabled?: boolean;
}

/**
 * Sidebar Component
 * 
 * Left-hand navigation for workspace-scoped pages.
 * Shows links to main app sections and highlights the active route.
 */
export const Sidebar: React.FC = () => {
    const location = useLocation();
    const pathname = location.pathname;

    // Navigation items
    const navItems: NavItem[] = [
        {
            label: 'Dashboard',
            href: '/dashboard',
            icon: LayoutDashboard,
        },
        {
            label: 'Positioning',
            href: '/positioning',
            icon: Target,
        },
        {
            label: 'Cohorts',
            href: '/cohorts',
            icon: Users,
        },
        {
            label: 'Campaigns',
            href: '/campaigns',
            icon: Zap,
        },
        {
            label: 'Content',
            href: '/muse',
            icon: FileText,
        },
    ];

    const bottomNavItems: NavItem[] = [
        {
            label: 'Settings',
            href: '/settings',
            icon: Settings,
        },
    ];

    // Check if route is active
    const isActive = (href: string) => {
        if (href === '/dashboard') {
            return pathname === href;
        }
        return pathname.startsWith(href);
    };

    return (
        <aside className="w-64 bg-white border-r border-neutral-200 flex flex-col h-full">
            {/* Main Navigation */}
            <nav className="flex-1 px-3 py-4 space-y-1">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);

                    return (
                        <Link
                            key={item.href}
                            to={item.href}
                            className={`
                flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                ${active
                                    ? 'bg-neutral-900 text-white'
                                    : 'text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900'
                                }
                ${item.disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
                            onClick={(e) => item.disabled && e.preventDefault()}
                        >
                            <Icon className="h-5 w-5" />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            {/* Bottom Navigation */}
            <nav className="px-3 py-4 border-t border-neutral-200 space-y-1">
                {bottomNavItems.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);

                    return (
                        <Link
                            key={item.href}
                            to={item.href}
                            className={`
                flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                ${active
                                    ? 'bg-neutral-900 text-white'
                                    : 'text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900'
                                }
              `}
                        >
                            <Icon className="h-5 w-5" />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>
        </aside>
    );
};

export default Sidebar;
