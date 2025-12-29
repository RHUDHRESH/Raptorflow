'use client';

import { Search } from 'lucide-react';
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarInput,
} from '@/components/ui/sidebar';

export function SearchForm() {
  return (
    <form onSubmit={(e) => e.preventDefault()}>
      <SidebarGroup className="py-0 group-data-[collapsible=icon]:hidden">
        <SidebarGroupContent className="relative px-2">
          <SidebarInput
            placeholder="Search..."
            className="pl-9 bg-sidebar-accent/30 border-sidebar-border/30 focus:bg-sidebar-accent/50 focus:border-sidebar-ring h-8 text-sm transition-all duration-150 rounded-md"
          />
          <Search className="pointer-events-none absolute left-2 top-1/2 size-3.5 -translate-y-1/2 select-none text-muted-foreground/50" />
        </SidebarGroupContent>
      </SidebarGroup>
    </form>
  );
}
