"use client";

import { Sidebar } from "./Sidebar";
import { TopNav } from "./TopNav";

interface ShellProps {
    children: React.ReactNode;
}

export function Shell({ children }: ShellProps) {
    return (
        <div className="shell">
            {/* Sidebar */}
            <Sidebar />

            {/* Main Area */}
            <div className="main">
                {/* Top Navigation */}
                <TopNav />

                {/* Content */}
                <main className="content animate-fade-in">
                    {children}
                </main>
            </div>
        </div>
    );
}
