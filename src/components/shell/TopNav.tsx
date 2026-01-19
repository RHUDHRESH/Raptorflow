"use client";

import { Search, Bell, Settings, ChevronDown, Sparkles, Command, Menu } from "lucide-react";
import * as React from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { CommandPalette } from "./CommandPalette";
import { Breadcrumbs } from "./Breadcrumbs";
import { NotificationBell } from "./NotificationCenter";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Sidebar } from "./Sidebar";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — Top Navigation
   Features:
   - Paper background with subtle texture
   - Blueprint accent line at bottom
   - Technical breadcrumb styling
   - Search styled as technical input
   - Architectural measurements visible
   ══════════════════════════════════════════════════════════════════════════════ */

export function TopNav() {
    const router = useRouter(); // Requires "use client" which is already there
    const [openCmd, setOpenCmd] = React.useState(false);

    React.useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setOpenCmd((open) => !open);
            }
        };
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, []);

    return (
        <>
            <CommandPalette open={openCmd} onOpenChange={setOpenCmd} />
            <header className="relative h-14 bg-[var(--paper)] border-b border-[var(--border)] flex items-center px-4 lg:px-6 gap-4 lg:gap-6 sticky top-0 z-40 ink-bleed-sm">
                {/* Mobile Menu Trigger */}
                <div className="lg:hidden relative z-10">
                    <Sheet>
                        <SheetTrigger asChild>
                            <button className="p-2 -ml-2 rounded-[var(--radius-sm)] hover:bg-[var(--canvas)] transition-colors">
                                <Menu size={20} className="text-[var(--ink-secondary)]" />
                            </button>
                        </SheetTrigger>
                        <SheetContent side="left" className="p-0 w-64 bg-[var(--paper)]">
                            <Sidebar />
                        </SheetContent>
                    </Sheet>
                </div>

                {/* Paper texture overlay */}
                <div
                    className="absolute inset-0 pointer-events-none"
                    style={{
                        backgroundImage: "url('/textures/paper-grain.png')",
                        backgroundRepeat: "repeat",
                        backgroundSize: "256px 256px",
                        opacity: 0.04,
                        mixBlendMode: "multiply",
                    }}
                />

                {/* Blueprint accent line at bottom */}
                <div className="absolute bottom-0 left-0 right-0 h-px bg-[var(--blueprint-line)]" />

                {/* Measurement tick at edge */}
                <div className="absolute top-0 left-0 h-full w-px bg-[var(--blueprint-line)]" />
                <div className="absolute top-0 left-6 h-2 w-px bg-[var(--blueprint)] hidden lg:block" />

                {/* ═══════════════════════════════════════════════════════════════════
              BREADCRUMB — Clean path
              ═══════════════════════════════════════════════════════════════════ */}
                <div className="flex-1 flex items-center gap-4 relative z-10 overflow-hidden">
                    <Breadcrumbs />
                </div>

                {/* ═══════════════════════════════════════════════════════════════════
              SEARCH — Blueprint input style (Hidden on small mobile)
              ═══════════════════════════════════════════════════════════════════ */}
                <div className="flex-1 max-w-md relative z-10 hidden sm:block">
                    <div
                        className="relative group cursor-pointer"
                        onClick={() => setOpenCmd(true)}
                    >
                        {/* Search icon */}
                        <Search
                            size={14}
                            strokeWidth={1.5}
                            className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)] group-hover:text-[var(--secondary)] group-focus-within:text-[var(--blueprint)] transition-colors"
                        />

                        {/* Input (Read only, acts as trigger) */}
                        <div className="w-full h-9 pl-9 pr-16 text-sm bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-[var(--ink-muted)] flex items-center transition-all ink-bleed-xs group-hover:border-[var(--blueprint)] group-hover:bg-[var(--blueprint-light)]/10">
                            Search...
                        </div>

                        {/* Keyboard shortcut */}
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-0.5">
                            <kbd className="font-technical px-1.5 py-0.5 text-[var(--muted)] bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-xs)] flex items-center gap-0.5">
                                <Command size={10} strokeWidth={1.5} />
                                <span>K</span>
                            </kbd>
                        </div>
                    </div>
                </div>

                {/* ═══════════════════════════════════════════════════════════════════
              RIGHT ACTIONS — Technical controls
              ═══════════════════════════════════════════════════════════════════ */}
                <div className="flex-shrink-0 flex items-center justify-end gap-2 lg:gap-4 relative z-10">
                    {/* Muse AI Button - Label hidden on mobile */}
                    <button
                        onClick={() => router.push("/muse")}
                        className="flex items-center gap-2 p-2 lg:px-3 lg:py-1.5 bg-[var(--blueprint-light)] border border-[var(--blueprint)]/30 rounded-[var(--radius-sm)] text-xs font-medium text-[var(--blueprint)] hover:bg-[var(--blueprint)]/10 hover:border-[var(--blueprint)]/50 transition-all group"
                    >
                        <Sparkles size={14} strokeWidth={1.5} className="group-hover:rotate-12 transition-transform" />
                        <span className="font-technical hidden lg:inline">MUSE</span>
                    </button>

                    {/* Divider with tick - Hidden on mobile */}
                    <div className="relative h-6 w-px bg-[var(--border)] hidden lg:block">
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-px bg-[var(--blueprint-line)]" />
                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2 h-px bg-[var(--blueprint-line)]" />
                    </div>

                    {/* Notifications */}
                    <NotificationBell />

                    {/* Settings - Hidden on very small screens (accessible via sidebar) */}
                    <button
                        onClick={() => router.push("/settings")}
                        className="p-2 rounded-[var(--radius-sm)] hover:bg-[var(--canvas)] transition-colors group hidden sm:block"
                    >
                        <Settings
                            size={16}
                            strokeWidth={1.5}
                            className="text-[var(--muted)] group-hover:text-[var(--ink)] group-hover:rotate-45 transition-all"
                        />
                    </button>
                </div>
            </header>
        </>
    );
}
