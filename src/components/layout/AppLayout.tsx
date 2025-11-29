import React from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

/**
 * App Layout Props
 */
interface AppLayoutProps {
    children: React.ReactNode;
}

/**
 * AppLayout Component
 * 
 * Core layout for workspace-scoped pages.
 * Provides consistent topbar, sidebar, and main content area.
 * 
 * Usage:
 * ```tsx
 * <AppLayout>
 *   <YourPageContent />
 * </AppLayout>
 * ```
 */
export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
    return (
        <div className="min-h-screen flex flex-col bg-neutral-50">
            {/* Topbar */}
            <Topbar />

            {/* Main Content Area */}
            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <Sidebar />

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto">
                    <div className="max-w-7xl mx-auto p-6">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default AppLayout;
