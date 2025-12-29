'use client';

import React from 'react';
import { AppSidebar } from './AppSidebar';
import { CommandPalette } from './CommandPalette';
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
  useSidebar,
} from '@/components/ui/sidebar';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, Moon, Sun, Command, Wifi, WifiOff, Plus } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface PublicLayoutProps {
  children: React.ReactNode;
  /** When true, removes max-width constraint for full-bleed layouts */
  fullBleed?: boolean;
}

/**
 * Public layout without AuthGuard for non-sensitive pages
 */
export function PublicLayout({ children, fullBleed = false }: PublicLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [isOnline, setIsOnline] = React.useState(true);
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
    setIsOnline(navigator.onLine);
    
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          {/* Header */}
          <header className="flex h-16 shrink-0 items-center gap-2 border-b border-[#E5E6E3] bg-white px-4">
            <SidebarTrigger className="-ml-1" />
            
            <div className="flex flex-1 items-center justify-between">
              <div className="flex items-center gap-2">
                <CommandPalette />
              </div>
              
              <div className="flex items-center gap-2">
                {/* Online Status */}
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      {isOnline ? (
                        <Wifi className="h-4 w-4 text-green-600" />
                      ) : (
                        <WifiOff className="h-4 w-4 text-red-600" />
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{isOnline ? 'Online' : 'Offline'}</p>
                  </TooltipContent>
                </Tooltip>

                {/* Theme Toggle */}
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                    >
                      {theme === 'dark' ? (
                        <Sun className="h-4 w-4" />
                      ) : (
                        <Moon className="h-4 w-4" />
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Toggle theme</p>
                  </TooltipContent>
                </Tooltip>

                {/* Sign In Button */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push('/login')}
                >
                  Sign In
                </Button>
              </div>
            </div>
          </header>

          {/* Full Rectangle Content Area */}
          <main
            className={cn(
              'flex-1 min-h-[calc(100vh-3.5rem)]',
              fullBleed
                ? 'w-full bg-background'
                : 'mx-auto max-w-none bg-background'
            )}
          >
            {children}
          </main>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  );
}
