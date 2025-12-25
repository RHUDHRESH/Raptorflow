'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { AppIcon, Icons } from '@/components/ui/Icons';

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
    { title: 'Home', url: '/', icon: Icons.Home },
    { title: 'Foundation', url: '/foundation', icon: Icons.Nature },
    { title: 'Cohorts', url: '/cohorts', icon: Icons.Team },
    { title: 'Moves', url: '/moves', icon: Icons.Moves },
    { title: 'Campaigns', url: '/campaigns', icon: Icons.Campaigns },
    { title: 'Muse', url: '/muse', icon: Icons.Edit },
    { title: 'Matrix', url: '/matrix', icon: Icons.Brain },
    { title: 'Blackbox', url: '/blackbox', icon: Icons.Security },
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
                            <AppIcon icon={item.icon} size={16} className="mr-2" />
                            <span>{item.title}</span>
                        </CommandItem>
                    ))}
                </CommandGroup>
                <CommandSeparator />
                <CommandGroup heading="Actions">
                    <CommandItem onSelect={() => runCommand(() => console.log('Creating new campaign...'))}>
                        <AppIcon icon={Icons.Target} size={16} className="mr-2" />
                        <span>Create New Campaign</span>
                    </CommandItem>
                    <CommandItem onSelect={() => runCommand(() => console.log('Opening settings...'))}>
                        <AppIcon icon={Icons.Settings} size={16} className="mr-2" />
                        <span>Open Settings</span>
                    </CommandItem>
                </CommandGroup>
            </CommandList>
        </CommandDialog>
    );
}
