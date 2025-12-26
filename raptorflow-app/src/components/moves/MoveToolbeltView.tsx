'use client';

import React from 'react';
import { Search, PenTool, Image, BarChart3, Database, CheckCircle2, AlertCircle, Users, Calendar, Mail, Share2, SearchCode, Download, Bell, Brain, GitBranch } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MoveToolbeltViewProps {
  tools?: string[];
  className?: string;
}

const TOOL_ICONS: Record<string, any> = {
  'Search': Search,
  'Copy': PenTool,
  'ImageGen': Image,
  'Analytics': BarChart3,
  'CRM': Users,
  'Scheduler': Calendar,
  'Email': Mail,
  'Social': Share2,
  'SEO': SearchCode,
  'Export': Download,
  'Notifications': Bell,
  'Perplexity': Brain,
  'Tavily': GitBranch,
  'SocialAPI': Database,
};

/**
 * SOTA Move Toolbelt Component
 * Displays required agentic tools and their verification status.
 */
export function MoveToolbeltView({ tools, className }: MoveToolbeltViewProps) {
  if (!tools || tools.length === 0) return null;

  return (
    <div className={cn("space-y-3", className)}>
      <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400 ml-1">Agentic Toolbelt</h3>

      <div className="flex flex-wrap gap-2">
        {tools.map((tool) => {
          const Icon = TOOL_ICONS[tool] || Database;
          const isVerified = ['Search', 'Copy', 'ImageGen', 'Analytics', 'CRM', 'Scheduler', 'Email', 'Social', 'SEO', 'Export', 'Notifications', 'Perplexity', 'Tavily'].includes(tool); // Mock verification

          return (
            <div
              key={tool}
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-xl border transition-all group",
                isVerified
                  ? "bg-emerald-50/50 border-emerald-100 dark:bg-emerald-900/10 dark:border-emerald-900/30"
                  : "bg-zinc-50 border-zinc-100 dark:bg-zinc-900/50 dark:border-zinc-800"
              )}
            >
              <div className={cn(
                "p-1.5 rounded-lg",
                isVerified ? "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40" : "bg-zinc-100 text-zinc-400 dark:bg-zinc-800"
              )}>
                <Icon size={14} />
              </div>

              <div className="flex flex-col">
                <span className="text-[11px] font-bold text-zinc-900 dark:text-zinc-100 leading-none mb-0.5">{tool}</span>
                <div className="flex items-center gap-1">
                  {isVerified ? (
                    <>
                      <CheckCircle2 size={8} className="text-emerald-500" />
                      <span className="text-[8px] font-bold uppercase text-emerald-600/70">Verified</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle size={8} className="text-zinc-400" />
                      <span className="text-[8px] font-bold uppercase text-zinc-400">Offline</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
