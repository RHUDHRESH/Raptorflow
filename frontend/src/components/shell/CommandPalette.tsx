"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Search, LayoutGrid, Zap, Flag, Target, BarChart3, Settings, HelpCircle, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   COMMAND PALETTE ΓÇö Global Navigation & Search
   Accessible via Cmd+K or search bar click.
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface CommandPaletteProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
    const router = useRouter();
    const [query, setQuery] = React.useState("");
    const [selectedIndex, setSelectedIndex] = React.useState(0);

    const COMMANDS = [
        {
            section: "Modules", items: [
                { icon: LayoutGrid, label: "Dashboard", href: "/dashboard", desc: "Overview" },
                { icon: Zap, label: "Moves", href: "/moves", desc: "Tactical execution" },
                { icon: Flag, label: "Campaigns", href: "/campaigns", desc: "Strategic command" },
                { icon: Flag, label: "Daily Wins", href: "/daily-wins", desc: "Quick content" },
                { icon: Target, label: "Foundation", href: "/foundation", desc: "Brand positioning" },
                { icon: BarChart3, label: "Analytics", href: "/analytics", desc: "Performance tracking" },
            ]
        },
        {
            section: "System", items: [
                { icon: Settings, label: "Settings", href: "/settings", desc: "Preferences & Account" },
                { icon: HelpCircle, label: "Help Center", href: "/help", desc: "Documentation" },
            ]
        },
    ];

    // Flatten for keyboard nav
    const allItems = COMMANDS.flatMap(group => group.items);

    const filteredCommands = query
        ? COMMANDS.map(group => ({
            ...group,
            items: group.items.filter(item =>
                item.label.toLowerCase().includes(query.toLowerCase()) ||
                item.desc.toLowerCase().includes(query.toLowerCase())
            )
        })).filter(group => group.items.length > 0)
        : COMMANDS;

    const flatFiltered = filteredCommands.flatMap(g => g.items);

    React.useEffect(() => {
        setSelectedIndex(0);
    }, [query]);

    React.useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (!open) return;

            if (e.key === "ArrowDown") {
                e.preventDefault();
                setSelectedIndex(i => Math.min(i + 1, flatFiltered.length - 1));
            }
            if (e.key === "ArrowUp") {
                e.preventDefault();
                setSelectedIndex(i => Math.max(i - 1, 0));
            }
            if (e.key === "Enter") {
                e.preventDefault();
                if (flatFiltered[selectedIndex]) {
                    router.push(flatFiltered[selectedIndex].href);
                    onOpenChange(false);
                }
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [open, flatFiltered, selectedIndex, router, onOpenChange]);

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] sm:pt-[15vh]">
                <div
                    className="fixed inset-0 bg-black/20 backdrop-blur-sm animate-in fade-in duration-200"
                    onClick={() => onOpenChange(false)}
                />

                <div className="relative w-full max-w-2xl bg-[var(--paper)] border border-[var(--blueprint)] rounded-[var(--radius)] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
                    {/* Technical Border Ticks */}
                    <div className="absolute top-0 left-0 w-2 h-2 border-l border-t border-[var(--blueprint)]" />
                    <div className="absolute top-0 right-0 w-2 h-2 border-r border-t border-[var(--blueprint)]" />
                    <div className="absolute bottom-0 left-0 w-2 h-2 border-l border-b border-[var(--blueprint)]" />
                    <div className="absolute bottom-0 right-0 w-2 h-2 border-r border-b border-[var(--blueprint)]" />

                    <div className="flex items-center px-4 py-3 border-b border-[var(--structure)]">
                        <Search size={18} className="text-[var(--blueprint)] mr-3" />
                        <input
                            autoFocus
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Type a command or search..."
                            className="flex-1 bg-transparent border-none text-[var(--ink)] placeholder:text-[var(--ink-muted)] focus:outline-none text-lg font-medium"
                        />
                        <div className="flex items-center gap-1.5">
                            <span className="text-[10px] font-mono text-[var(--ink-muted)] bg-[var(--surface)] px-1.5 py-0.5 rounded border border-[var(--structure-subtle)]">ESC</span>
                        </div>
                    </div>

                    <div className="max-h-[60vh] overflow-y-auto p-2">
                        {filteredCommands.length === 0 ? (
                            <div className="py-12 text-center text-[var(--ink-muted)]">
                                <p>No results found.</p>
                            </div>
                        ) : (
                            filteredCommands.map((group, gIdx) => (
                                <div key={group.section} className="mb-2 last:mb-0">
                                    <div className="px-2 py-1.5 text-[10px] font-bold text-[var(--ink-muted)] uppercase tracking-wider sticky top-0 bg-[var(--paper)] z-10">
                                        {group.section}
                                    </div>
                                    <div className="space-y-1">
                                        {group.items.map((item, i) => {
                                            const isSelected = item === flatFiltered[selectedIndex];
                                            return (
                                                <button
                                                    key={item.href}
                                                    onClick={() => {
                                                        router.push(item.href);
                                                        onOpenChange(false);
                                                    }}
                                                    onMouseEnter={() => setSelectedIndex(flatFiltered.indexOf(item))}
                                                    className={cn(
                                                        "w-full flex items-center gap-3 px-3 py-2.5 rounded-[var(--radius-sm)] text-left transition-colors",
                                                        isSelected
                                                            ? "bg-[var(--blueprint)] text-[var(--paper)]"
                                                            : "text-[var(--ink)] hover:bg-[var(--surface)]"
                                                    )}
                                                >
                                                    <item.icon size={18} className={cn("opacity-70", isSelected ? "text-[var(--paper)]" : "text-[var(--ink-muted)]")} />
                                                    <div className="flex-1">
                                                        <div className="font-medium text-sm">{item.label}</div>
                                                        <div className={cn("text-xs opacity-70", isSelected ? "text-[var(--paper)]" : "text-[var(--ink-secondary)]")}>
                                                            {item.desc}
                                                        </div>
                                                    </div>
                                                    {isSelected && <span className="text-[10px] opacity-70">Γå╡</span>}
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    <DialogTitle className="sr-only">Command Palette</DialogTitle>
                    <DialogDescription className="sr-only">Search modules and commands</DialogDescription>
                </div>
            </DialogContent>
        </Dialog>
    );
}
