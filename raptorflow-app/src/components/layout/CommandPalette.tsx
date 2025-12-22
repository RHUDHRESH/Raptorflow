'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import {
    Home,
    Layers,
    Users,
    Zap,
    Target,
    Sparkles,
    LayoutGrid,
    Box,
    Settings,
    Search
} from 'lucide-react';

import {
    CommandDialog,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
    CommandSeparator,
} from '@/components/ui/command';

const navItems = [
    { title: 'Home', url: '/', icon: Home },
    { title: 'Foundation', url: '/foundation', icon: Layers },
    { title: 'Cohorts', url: '/cohorts', icon: Users },
    { title: 'Moves', url: '/moves', icon: Zap },
    { title: 'Campaigns', url: '/campaigns', icon: Target },
    { title: 'Muse', url: '/muse', icon: Sparkles },
    { title: 'Matrix', url: '/matrix', icon: LayoutGrid },
    { title: 'Blackbox', url: '/blackbox', icon: Box },
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

    const runCommand = React.useCallback((command: () => unknown) => {
        setOpen(false);
        command();
    }, []);

    return (
        <CommandDialog open={open} onOpenChange={setOpen}>
            <CommandInput placeholder="Type a command or search..." />
            <CommandList>
                <CommandEmpty>No results found.</CommandEmpty>
                <CommandGroup heading="Navigation">
                    {navItems.map((item) => (
                        <CommandItem
                            key={item.url}
                            value={item.title}
                            onSelect={() => runCommand(() => router.push(item.url))}
                        >
                            <item.icon className="mr-2 h-4 w-4" />
                            <span>{item.title}</span>
                        </CommandItem>
                    ))}
                </CommandGroup>
                <CommandSeparator />
                <CommandGroup heading="Actions">
                    <CommandItem onSelect={() => runCommand(() => console.log('Creating new campaign...'))}>
                        <Target className="mr-2 h-4 w-4" />
                        <span>Create New Campaign</span>
                    </CommandItem>
                    <CommandItem onSelect={() => runCommand(() => console.log('Opening settings...'))}>
                        <Settings className="mr-2 h-4 w-4" />
                        <span>Open Settings</span>
                    </CommandItem>
                </CommandGroup>
            </CommandList>
        </CommandDialog>
    );
}
