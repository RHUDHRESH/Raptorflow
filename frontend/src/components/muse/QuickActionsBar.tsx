"use client";

import { useEffect } from 'react';
import { Plus, Layout, Download, RefreshCw, Command, Zap } from 'lucide-react';
import { BlueprintTooltip } from '@/components/ui/BlueprintTooltip';
import { cn } from '@/lib/utils';

interface QuickAction {
  id: string;
  label: string;
  icon: any;
  shortcut: string;
  code: string;
  action: () => void;
}

interface QuickActionsBarProps {
  onNewChat: () => void;
  onUseTemplate: () => void;
  onExport: () => void;
  onSync: () => void;
  className?: string;
}

export function QuickActionsBar({ onNewChat, onUseTemplate, onExport, onSync, className }: QuickActionsBarProps) {
  const actions: QuickAction[] = [
    { id: 'new', label: 'New Chat', icon: Plus, shortcut: 'N', code: 'ACT-01', action: onNewChat },
    { id: 'template', label: 'Use Template', icon: Layout, shortcut: 'T', code: 'ACT-02', action: onUseTemplate },
    { id: 'export', label: 'Export Data', icon: Download, shortcut: 'E', code: 'ACT-03', action: onExport },
    { id: 'sync', label: 'Refresh Sync', icon: RefreshCw, shortcut: 'S', code: 'ACT-04', action: onSync },
  ];

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) return; // Ignore if modifier key is pressed (for standard shortcuts)
      
      // Don't trigger if user is typing in an input
      if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA') return;

      const key = e.key.toUpperCase();
      const action = actions.find(a => a.shortcut === key);
      if (action) {
        e.preventDefault();
        action.action();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [actions]);

  return (
    <div className={cn(
      "flex items-center gap-1 bg-[var(--ink)] text-[var(--paper)] p-1.5 rounded-full shadow-2xl z-50 border border-[var(--blueprint)]/20",
      className
    )}>
      {/* Indicator */}
      <div className="px-3 py-1 flex items-center gap-2 border-r border-[var(--paper)]/10 mr-1">
        <Zap size={14} className="text-[var(--blueprint)]" />
        <span className="text-[10px] font-technical uppercase tracking-widest opacity-60">Quick</span>
      </div>

      {actions.map((action) => (
        <BlueprintTooltip
          key={action.id}
          content={
            <div className="flex items-center gap-2">
              <span>{action.label}</span>
              <span className="opacity-50 text-[10px] px-1 bg-[var(--paper)]/10 rounded font-mono">{action.shortcut}</span>
            </div>
          }
          code={action.code}
          position="top"
        >
          <button
            onClick={action.action}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-[var(--paper)]/10 transition-all active:scale-95 group relative"
          >
            <action.icon size={18} strokeWidth={2} />
            
            {/* Ink bleed effect on hover */}
            <div className="absolute inset-0 rounded-full bg-[var(--blueprint)] opacity-0 group-hover:opacity-10 blur-md transition-opacity" />
          </button>
        </BlueprintTooltip>
      ))}

      {/* Command Indicator */}
      <div className="pl-2 pr-4 flex items-center gap-2 border-l border-[var(--paper)]/10 ml-1">
        <Command size={12} className="opacity-40" />
        <span className="text-[9px] font-technical opacity-40 uppercase tracking-tighter">Shortcuts Active</span>
      </div>
    </div>
  );
}
