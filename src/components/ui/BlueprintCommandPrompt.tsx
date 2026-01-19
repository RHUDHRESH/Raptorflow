"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
    Command,
    Search,
    Zap,
    FileText,
    Settings,
    Box,
    Target,
    BarChart3,
    CornerDownLeft
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useSettingsStore } from "@/stores/settingsStore";
import { BlueprintModal } from "@/components/ui/BlueprintModal";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT COMMAND — Global Command Interface
   An omnibar for navigation and quick actions.
   ══════════════════════════════════════════════════════════════════════════════ */

interface CommandItem {
    id: string;
    icon: React.ReactNode;
    label: string;
    description?: string;
    shortcut?: string;
    action: () => void;
    group: string;
}

export function BlueprintCommandPrompt() {
    const router = useRouter();
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState("");
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);
    const { preferences } = useSettingsStore();

    const openPrompt = useCallback(() => {
        setQuery("");
        setSelectedIndex(0);
        setIsOpen(true);
    }, []);

    const closePrompt = useCallback(() => setIsOpen(false), []);

    // Toggle on CMD+K
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setIsOpen((prev) => {
                    if (prev) {
                        return false;
                    }
                    openPrompt();
                    return true;
                });
            }
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [openPrompt]);

    // Focus input on open
    useEffect(() => {
        if (isOpen) {
            const timeout = setTimeout(() => inputRef.current?.focus(), 100);
            return () => clearTimeout(timeout);
        }
    }, [isOpen]);

    const commands: CommandItem[] = [
        // Navigation
        { id: "nav-dashboard", icon: <Box size={14} />, label: "Go to Dashboard", group: "Navigation", action: () => router.push("/dashboard") },
        { id: "nav-foundation", icon: <Target size={14} />, label: "Go to Foundation", group: "Navigation", action: () => router.push("/foundation") },
        { id: "nav-moves", icon: <Zap size={14} />, label: "Go to Moves", group: "Navigation", action: () => router.push("/moves") },
        { id: "nav-campaigns", icon: <Target size={14} />, label: "Go to Campaigns", group: "Navigation", action: () => router.push("/campaigns") },
        { id: "nav-muse", icon: <FileText size={14} />, label: "Go to Muse", group: "Navigation", action: () => router.push("/muse") },
        { id: "nav-daily-wins", icon: <Target size={14} />, label: "Go to Daily Wins", group: "Navigation", action: () => router.push("/daily-wins") },
        { id: "nav-cohorts", icon: <Target size={14} />, label: "Go to Cohorts", group: "Navigation", action: () => router.push("/cohorts") },
        { id: "nav-analytics", icon: <BarChart3 size={14} />, label: "Go to Analytics", group: "Navigation", action: () => router.push("/analytics") },
        { id: "nav-blackbox", icon: <Box size={14} />, label: "Go to Blackbox", group: "Navigation", action: () => router.push("/blackbox") },
        { id: "nav-settings", icon: <Settings size={14} />, label: "Settings", group: "Navigation", action: () => router.push("/settings") },

        // Actions
        { id: "act-create-move", icon: <Zap size={14} />, label: "Create New Move", description: "Start a tactical move", group: "Actions", action: () => router.push("/moves") },
        { id: "act-draft-content", icon: <FileText size={14} />, label: "Draft Content", description: "Open Muse writer", group: "Actions", action: () => router.push("/muse") },
    ];

    const filteredCommands = commands.filter(cmd =>
        cmd.label.toLowerCase().includes(query.toLowerCase()) ||
        cmd.group.toLowerCase().includes(query.toLowerCase())
    );

    // Grouping
    const groups = Array.from(new Set(filteredCommands.map(c => c.group)));

    const handleSelect = (cmd: CommandItem) => {
        cmd.action();
        closePrompt();
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "ArrowDown") {
            e.preventDefault();
            setSelectedIndex(prev => (prev + 1) % filteredCommands.length);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % filteredCommands.length);
        } else if (e.key === "Enter") {
            e.preventDefault();
            if (filteredCommands[selectedIndex]) {
                handleSelect(filteredCommands[selectedIndex]);
            }
        } else if (e.key === "Escape") {
            closePrompt();
        }
    };

    if (!preferences.commandPalette) return null;

    return (
        <BlueprintModal
            isOpen={isOpen}
            onClose={closePrompt}
            size="md"
            showClose={false}
            className="p-0 overflow-hidden bg-[var(--surface)] border-2 border-[var(--ink)]"
        >
            <div className="flex items-center gap-3 p-4 border-b border-[var(--border)] bg-[var(--paper)]">
                <Search size={18} className="text-[var(--ink-muted)]" />
                <input
                    ref={inputRef}
                    value={query}
                    onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0); }}
                    onKeyDown={handleKeyDown}
                    placeholder="Type a command or search..."
                    className="flex-1 bg-transparent text-lg text-[var(--ink)] placeholder:text-[var(--muted)] focus:outline-none font-sans"
                />
                <div className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 rounded-[4px] border border-[var(--border)] bg-[var(--canvas)] text-[10px] font-mono text-[var(--muted)]">ESC</kbd>
                </div>
            </div>

            <div className="max-h-[300px] overflow-y-auto p-2">
                {filteredCommands.length === 0 && (
                    <div className="p-8 text-center text-[var(--muted)] text-sm">
                        No commands found.
                    </div>
                )}

                {groups.map(group => (
                    <div key={group} className="mb-2">
                        <div className="px-3 py-1.5 text-[10px] font-bold text-[var(--muted)] uppercase tracking-wider sticky top-0 bg-[var(--surface)] z-10">
                            {group}
                        </div>
                        {filteredCommands.filter(c => c.group === group).map((cmd) => {
                            const globalIndex = filteredCommands.findIndex(c => c.id === cmd.id);
                            const isSelected = globalIndex === selectedIndex;

                            return (
                                <button
                                    key={cmd.id}
                                    onClick={() => handleSelect(cmd)}
                                    onMouseEnter={() => setSelectedIndex(globalIndex)}
                                    className={cn(
                                        "w-full flex items-center justify-between px-3 py-2.5 rounded-[var(--radius-sm)] text-left transition-all",
                                        isSelected
                                            ? "bg-[var(--blueprint)] text-[var(--paper)]"
                                            : "text-[var(--ink)] hover:bg-[var(--paper)]"
                                    )}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={cn(
                                            "w-6 h-6 rounded-[4px] flex items-center justify-center border",
                                            isSelected
                                                ? "border-transparent bg-[var(--paper)]/20 text-[var(--paper)]"
                                                : "border-[var(--border)] bg-[var(--paper)] text-[var(--ink-secondary)]"
                                        )}>
                                            {cmd.icon}
                                        </div>
                                        <div>
                                            <div className="text-sm font-medium">{cmd.label}</div>
                                            {cmd.description && (
                                                <div className={cn("text-xs opacity-80", isSelected ? "text-[var(--paper)]" : "text-[var(--muted)]")}>
                                                    {cmd.description}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    {isSelected && <CornerDownLeft size={14} className="opacity-50" />}
                                </button>
                            );
                        })}
                    </div>
                ))}
            </div>

            <div className="p-2 border-t border-[var(--border)] bg-[var(--canvas)] flex justify-between items-center text-[10px] text-[var(--muted)] font-mono">
                <div className="flex gap-3">
                    <span>ProTip: Use arrows to navigate</span>
                    <span>Enter to select</span>
                </div>
                <div className="flex items-center gap-1">
                    <Command size={10} />
                    <span>GLOBAL COMMAND</span>
                </div>
            </div>
        </BlueprintModal>
    );
}
