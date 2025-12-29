'use client';

import React, { useState, useMemo, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import {
  Search,
  Grid,
  List,
  Folder,
  MoreHorizontal,
  ExternalLink,
  Copy,
  Trash2,
  Link as LinkIcon,
} from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import { LucideIcon } from 'lucide-react';
import { Asset, ASSET_TYPES, getAssetConfig, isVisualAsset } from './types';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface AssetLibraryProps {
  assets: Asset[];
  onAssetClick: (asset: Asset) => void;
  onAssetDelete?: (asset: Asset) => void;
  onAssetDuplicate?: (asset: Asset) => void;
  className?: string;
  hasMore?: boolean;
  onLoadMore?: () => void;
  isLoading?: boolean;
  filters?: {
    type?: string;
    setType: (v?: string) => void;
    folder?: string;
    setFolder: (v?: string) => void;
    status?: string;
    setStatus: (v?: string) => void;
    search?: string;
    setSearch: (v?: string) => void;
  };
}

type ViewMode = 'grid' | 'list';

function getIcon(iconName: string): LucideIcon {
  const icons = LucideIcons as unknown as Record<string, LucideIcon>;
  return icons[iconName] || LucideIcons.FileText;
}

export function AssetLibrary({
  assets,
  onAssetClick,
  onAssetDelete,
  onAssetDuplicate,
  className,
  hasMore,
  onLoadMore,
  isLoading,
  filters,
}: AssetLibraryProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  // Use local state if filters not provided (fallback)
  const [localSearch, setLocalSearch] = useState('');
  const [localFolder, setLocalFolder] = useState<string | undefined>(undefined);

  const search = filters?.search ?? localSearch;
  const setSearch = filters?.setSearch ?? setLocalSearch;
  const folder = filters?.folder ?? localFolder;
  const setFolder = filters?.setFolder ?? setLocalFolder;

  // Group assets by folder for chips
  const folders = useMemo(() => {
    return [...new Set(assets.map((a) => a.folder).filter(Boolean))] as string[];
  }, [assets]);

  // Infinite Scroll Observer
  const observerTarget = useRef(null);
  useEffect(() => {
    if (!hasMore || isLoading || !onLoadMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          onLoadMore();
        }
      },
      { threshold: 1.0 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => observer.disconnect();
  }, [hasMore, isLoading, onLoadMore]);

  // Filter assets locally only if no external filter logic provided
  const filteredAssets = !filters ? assets.filter((asset) => {
    const matchesSearch =
      asset.title.toLowerCase().includes(search.toLowerCase()) ||
      asset.prompt?.toLowerCase().includes(search.toLowerCase());
    const matchesFolder =
      folder === null || asset.folder === folder;
    return matchesSearch && matchesFolder;
  }) : assets;

  return (
    <div className={cn('space-y-12', className)}>
      {/* Editorial Header */}
      <div className="flex items-end justify-between gap-4 border-b border-[#E5E6E3] pb-10">
        <div className="flex-1">
          <h2 className="font-serif text-[36px] text-[#2D3538] leading-none tracking-tight">
            Archive Library
          </h2>
          <p className="font-sans text-[15px] text-[#5B5F61] mt-4">
            {assets.length} distilled brand artifacts
          </p>
        </div>

        {/* Search + View toggle */}
        <div className="flex items-center gap-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9D9F9F]" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search archives..."
              className={cn(
                'h-11 w-64 pl-10 pr-4 rounded-xl',
                'border border-[#E5E6E3] bg-white',
                'text-[14px] text-[#2D3538] placeholder:text-[#9D9F9F]',
                'focus:outline-none focus:border-[#2D3538]',
                'transition-all duration-200'
              )}
            />
          </div>

          <div className="flex items-center gap-1 p-1 bg-[#F8F9F7] border border-[#E5E6E3] rounded-xl">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-2 rounded-lg transition-all',
                viewMode === 'grid'
                  ? 'bg-white text-[#2D3538] shadow-sm'
                  : 'text-[#9D9F9F] hover:text-[#5B5F61]'
              )}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2 rounded-lg transition-all',
                viewMode === 'list'
                  ? 'bg-white text-[#2D3538] shadow-sm'
                  : 'text-[#9D9F9F] hover:text-[#5B5F61]'
              )}
            >
              <List className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Folder chips + Status/Type filters */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 overflow-x-auto pb-2 flex-1">
          <button
            onClick={() => setFolder(undefined)}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-full shrink-0',
              'border text-xs font-medium transition-all duration-200',
              !folder
                ? 'border-[#2D3538] bg-[#2D3538] text-white'
                : 'border-[#E5E6E3] text-[#9D9F9F] hover:border-[#5B5F61]'
            )}
          >
            All Folders
          </button>
          {folders.map((f) => (
            <button
              key={f}
              onClick={() => setFolder(f)}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-full shrink-0',
                'border text-xs font-medium transition-all duration-200',
                folder === f
                  ? 'border-[#2D3538] bg-[#2D3538] text-white'
                  : 'border-[#E5E6E3] text-[#9D9F9F] hover:border-[#5B5F61]'
              )}
            >
              <Folder className="h-3 w-3" />
              {f}
            </button>
          ))}
        </div>

        {filters && (
          <div className="flex items-center gap-2">
            <select
              value={filters.status || ''}
              onChange={(e) => filters.setStatus(e.target.value || undefined)}
              className="h-9 px-3 rounded-lg border border-[#E5E6E3] bg-white text-xs text-[#5B5F61] focus:outline-none focus:border-[#2D3538]"
            >
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="complete">Complete</option>
              <option value="generating">Generating</option>
            </select>

            <select
              value={filters.type || ''}
              onChange={(e) => filters.setType(e.target.value || undefined)}
              className="h-9 px-3 rounded-lg border border-[#E5E6E3] bg-white text-xs text-[#5B5F61] focus:outline-none focus:border-[#2D3538]"
            >
              <option value="">All Types</option>
              {ASSET_TYPES.map(t => (
                <option key={t.type} value={t.type}>{t.label}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Asset grid/list */}
      {filteredAssets.length === 0 ? (
        <EmptyLibrary />
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredAssets.map((asset) => (
            <AssetCard
              key={asset.id}
              asset={asset}
              onClick={() => onAssetClick(asset)}
              onDelete={onAssetDelete ? () => onAssetDelete(asset) : undefined}
              onDuplicate={
                onAssetDuplicate ? () => onAssetDuplicate(asset) : undefined
              }
            />
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredAssets.map((asset) => (
            <AssetListItem
              key={asset.id}
              asset={asset}
              onClick={() => onAssetClick(asset)}
              onDelete={onAssetDelete ? () => onAssetDelete(asset) : undefined}
              onDuplicate={
                onAssetDuplicate ? () => onAssetDuplicate(asset) : undefined
              }
            />
          ))}
        </div>
      )}

      {/* Infinite Scroll Trigger */}
      <div
        ref={observerTarget}
        className={cn(
          "w-full h-20 flex items-center justify-center",
          !hasMore && "hidden"
        )}
      >
        {isLoading && (
          <div className="flex items-center gap-2 text-[#9D9F9F]">
            <div className="h-4 w-4 border-2 border-[#E5E6E3] border-t-[#2D3538] rounded-full animate-spin" />
            <span className="text-xs font-medium tracking-tight">Retrieving archives...</span>
          </div>
        )}
      </div>
    </div>
  );
}

function AssetCard({
  asset,
  onClick,
  onDelete,
  onDuplicate,
}: {
  asset: Asset;
  onClick: () => void;
  onDelete?: () => void;
  onDuplicate?: () => void;
}) {
  const config = getAssetConfig(asset.type);
  const Icon = config ? getIcon(config.icon) : LucideIcons.FileText;
  const isVisual = isVisualAsset(asset.type);

  return (
    <div
      className={cn(
        'group relative rounded-2xl border border-[#E5E6E3] bg-white overflow-hidden',
        'transition-all duration-300',
        'hover:border-[#C0C1BE] hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]',
        'cursor-pointer'
      )}
      onClick={onClick}
    >
      {/* Preview area */}
      <div
        className={cn(
          'aspect-[4/3] flex items-center justify-center bg-[#F8F9F7]'
        )}
      >
        {isVisual ? (
          <div className="text-[#9D9F9F]/30">
            <LucideIcons.Image className="h-12 w-12" />
          </div>
        ) : (
          <Icon className="h-8 w-8 text-[#9D9F9F]" />
        )}
      </div>

      {/* Info */}
      <div className="p-4 space-y-2">
        <p className="text-[15px] font-medium text-[#2D3538] tracking-tight truncate">
          {asset.title}
        </p>
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono uppercase tracking-wider text-[#9D9F9F]">
            {config?.label}
          </span>
          <span className="text-[11px] font-mono text-[#C0C1BE]">
            {formatDate(asset.createdAt)}
          </span>
        </div>
      </div>

      {/* Actions dropdown */}
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              onClick={(e) => e.stopPropagation()}
              className="h-7 w-7 rounded-md bg-background/80 backdrop-blur flex items-center justify-center hover:bg-background"
            >
              <MoreHorizontal className="h-4 w-4" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onClick();
              }}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Open
            </DropdownMenuItem>
            {onDuplicate && (
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onDuplicate();
                }}
              >
                <Copy className="h-4 w-4 mr-2" />
                Duplicate
              </DropdownMenuItem>
            )}
            <DropdownMenuItem>
              <LinkIcon className="h-4 w-4 mr-2" />
              Link to Campaign
            </DropdownMenuItem>
            {onDelete && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                  }}
                  className="text-red-500 focus:text-red-500"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}

function AssetListItem({
  asset,
  onClick,
  onDelete,
  onDuplicate,
}: {
  asset: Asset;
  onClick: () => void;
  onDelete?: () => void;
  onDuplicate?: () => void;
}) {
  const config = getAssetConfig(asset.type);
  const Icon = config ? getIcon(config.icon) : LucideIcons.FileText;

  return (
    <div
      className={cn(
        'group flex items-center gap-4 p-4 rounded-xl border border-border/60 bg-card',
        'transition-all duration-200',
        'hover:border-foreground/20 hover:bg-muted/30',
        'cursor-pointer'
      )}
      onClick={onClick}
    >
      <div className="h-10 w-10 rounded-lg bg-[#F8F9F7] border border-[#E5E6E3] flex items-center justify-center shrink-0">
        <Icon className="h-5 w-5 text-[#5B5F61]" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-[#2D3538] truncate">{asset.title}</p>
        <p className="text-sm text-[#9D9F9F] truncate">
          {config?.label} • {formatDate(asset.createdAt)}
        </p>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            onClick={(e) => e.stopPropagation()}
            className="h-8 w-8 rounded-md flex items-center justify-center opacity-0 group-hover:opacity-100 hover:bg-muted transition-all"
          >
            <MoreHorizontal className="h-4 w-4" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation();
              onClick();
            }}
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Open
          </DropdownMenuItem>
          {onDuplicate && (
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onDuplicate();
              }}
            >
              <Copy className="h-4 w-4 mr-2" />
              Duplicate
            </DropdownMenuItem>
          )}
          {onDelete && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete();
                }}
                className="text-red-500 focus:text-red-500"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

function EmptyLibrary() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="h-16 w-16 rounded-2xl bg-[#F8F9F7] border border-[#E5E6E3] flex items-center justify-center mb-6">
        <LucideIcons.Sparkles className="h-8 w-8 text-[#9D9F9F]" />
      </div>
      <h3 className="font-serif text-[24px] text-[#2D3538] mb-2">
        No assets yet
      </h3>
      <p className="text-[14px] text-[#5B5F61] max-w-xs">
        Create your first asset by describing what you need.
      </p>
    </div>
  );
}

function formatDate(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
