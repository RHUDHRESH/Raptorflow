'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import {
    Home,
    Layers,
    Users,
    Zap,
    Megaphone,
    Sparkles,
    LayoutGrid,
    Box,
    Settings,
    Plus,
    FileText,
    Search,
    ArrowRight,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

import {
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
    CommandShortcut,
} from '@/components/ui/command';

// Navigation pages
const pages = [
    { title: 'Home', url: '/dashboard', icon: Home, category: 'Navigation' },
    { title: 'Foundation', url: '/foundation', icon: Layers, category: 'Navigation' },
    { title: 'Cohorts', url: '/cohorts', icon: Users, category: 'Navigation' },
    { title: 'Moves', url: '/moves', icon: Zap, category: 'Navigation' },
    { title: 'Campaigns', url: '/campaigns', icon: Megaphone, category: 'Navigation' },
    { title: 'Radar', url: '/radar', icon: LayoutGrid, category: 'Navigation' },
    { title: 'Muse', url: '/muse', icon: Sparkles, category: 'Navigation' },
    { title: 'Blackbox', url: '/blackbox', icon: Box, category: 'Navigation' },
    { title: 'Settings', url: '/settings', icon: Settings, category: 'Navigation' },
];

// Quick actions
const actions = [
    { title: 'New Move', description: 'Create a new marketing move', icon: Plus, action: '/moves?new=true', shortcut: '⌘M' },
    { title: 'New Campaign', description: 'Start a 90-day campaign', icon: Megaphone, action: '/campaigns?new=true', shortcut: '⌘N' },
    { title: 'Generate Content', description: 'Open Muse for content generation', icon: Sparkles, action: '/muse', shortcut: '⌘G' },
    { title: 'View Insights', description: 'Check competitive analysis', icon: LayoutGrid, action: '/radar', shortcut: '⌘I' },
];

export function CommandPalette() {
    const [open, setOpen] = React.useState(false);
    const router = useRouter();

    React.useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setOpen((open) => !open);
            }
        };

        document.addEventListener('keydown', down);
        return () => document.removeEventListener('keydown', down);
    }, []);

    const runCommand = React.useCallback((command: () => void) => {
        setOpen(false);
        command();
    }, []);

    return (
        <CommandDialog open={open} onOpenChange={setOpen}>
            <div className="relative">
                {/* Premium gradient accent */}
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[#E9ECE6]/20 to-transparent" />

                <CommandInput
                    placeholder="Search pages, actions, or type a command..."
                    className="h-14 text-[15px] border-0 focus:ring-0 placeholder:text-[#5a6268]"
                />
            </div>

            <CommandList className="max-h-[400px] overflow-y-auto">
                <CommandEmpty className="py-12">
                    <div className="flex flex-col items-center gap-3 text-center">
                        <Search className="h-8 w-8 text-[#5a6268]/50" />
                        <div>
                            <p className="text-[14px] font-medium text-[#8a9298]">No results found</p>
                            <p className="text-[12px] text-[#5a6268] mt-1">Try a different search term</p>
                        </div>
                    </div>
                </CommandEmpty>

                {/* Quick Actions */}
                <CommandGroup heading="Quick Actions">
                    {actions.map((action) => (
                        <CommandItem
                            key={action.title}
                            onSelect={() => runCommand(() => router.push(action.action))}
                            className="h-14 px-4 gap-4 cursor-pointer rounded-lg mx-2 my-0.5 data-[selected=true]:bg-[#E9ECE6]/[0.05]"
                        >
                            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#141618] border border-[#1e2326]">
                                <action.icon className="h-4 w-4 text-[#E9ECE6]" />
                            </div>
                            <div className="flex-1">
                                <p className="text-[14px] font-medium text-[#E9ECE6]">{action.title}</p>
                                <p className="text-[12px] text-[#5a6268]">{action.description}</p>
                            </div>
                            <CommandShortcut className="text-[11px] text-[#5a6268]">
                                {action.shortcut}
                            </CommandShortcut>
                        </CommandItem>
                    ))}
                </CommandGroup>

                <CommandSeparator className="my-2 bg-[#1e2326]" />

                {/* Pages */}
                <CommandGroup heading="Pages">
                    {pages.map((page) => (
                        <CommandItem
                            key={page.url}
                            onSelect={() => runCommand(() => router.push(page.url))}
                            className="h-11 px-4 gap-3 cursor-pointer rounded-lg mx-2 my-0.5 data-[selected=true]:bg-[#E9ECE6]/[0.05]"
                        >
                            <page.icon className="h-4 w-4 text-[#8a9298]" />
                            <span className="text-[14px] text-[#E9ECE6]">{page.title}</span>
                            <ArrowRight className="ml-auto h-3 w-3 text-[#5a6268]" />
                        </CommandItem>
                    ))}
                </CommandGroup>
            </CommandList>

            {/* Footer */}
            <div className="flex items-center justify-between border-t border-[#1e2326] p-3 text-[11px] text-[#5a6268]">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5">
                        <kbd className="px-1.5 py-0.5 rounded bg-[#1e2326] border border-[#2b3134] font-mono text-[10px]">↵</kbd>
                        <span>to select</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <kbd className="px-1.5 py-0.5 rounded bg-[#1e2326] border border-[#2b3134] font-mono text-[10px]">↑↓</kbd>
                        <span>to navigate</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <kbd className="px-1.5 py-0.5 rounded bg-[#1e2326] border border-[#2b3134] font-mono text-[10px]">esc</kbd>
                        <span>to close</span>
                    </div>
                </div>
                <span className="text-[#5a6268]/60">RaptorFlow Command</span>
            </div>
        </CommandDialog>
    );
}
