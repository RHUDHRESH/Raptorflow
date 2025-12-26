'use client';

import React, { useState } from 'react';
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
    Link as LinkIcon
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
    className
}: AssetLibraryProps) {
    const [searchQuery, setSearchQuery] = useState('');
    const [viewMode, setViewMode] = useState<ViewMode>('grid');
    const [selectedFolder, setSelectedFolder] = useState<string | null>(null);

    // Group assets by folder
    const folders = [...new Set(assets.map(a => a.folder).filter(Boolean))] as string[];

    // Filter assets
    const filteredAssets = assets.filter(asset => {
        const matchesSearch = asset.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            asset.prompt?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesFolder = selectedFolder === null || asset.folder === selectedFolder;
        return matchesSearch && matchesFolder;
    });

    return (
        <div className={cn('space-y-12', className)}>
            {/* Editorial Header */}
            <div className="flex items-end justify-between gap-4 border-b border-[#E5E6E3] pb-10">
                <div className="flex-1">
                    <h2 className="font-serif text-[36px] text-[#2D3538] leading-none tracking-tight">Archive Library</h2>
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
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
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
                                viewMode === 'grid' ? 'bg-white text-[#2D3538] shadow-sm' : 'text-[#9D9F9F] hover:text-[#5B5F61]'
                            )}
                        >
                            <Grid className="h-4 w-4" />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className={cn(
                                'p-2 rounded-lg transition-all',
                                viewMode === 'list' ? 'bg-white text-[#2D3538] shadow-sm' : 'text-[#9D9F9F] hover:text-[#5B5F61]'
                            )}
                        >
                            <List className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Folder chips */}
            {folders.length > 0 && (
                <div className="flex items-center gap-2 overflow-x-auto pb-2">
                    <button
                        onClick={() => setSelectedFolder(null)}
                        className={cn(
                            'flex items-center gap-1.5 px-3 py-1.5 rounded-full shrink-0',
                            'border text-xs font-medium transition-all duration-200',
                            selectedFolder === null
                                ? 'border-[#2D3538] bg-[#2D3538] text-white'
                                : 'border-[#E5E6E3] text-[#9D9F9F] hover:border-[#5B5F61]'
                        )}
                    >
                        All
                    </button>
                    {folders.map(folder => (
                        <button
                            key={folder}
                            onClick={() => setSelectedFolder(folder)}
                            className={cn(
                                'flex items-center gap-1.5 px-3 py-1.5 rounded-full shrink-0',
                                'border text-xs font-medium transition-all duration-200',
                                selectedFolder === folder
                                    ? 'border-[#2D3538] bg-[#2D3538] text-white'
                                    : 'border-[#E5E6E3] text-[#9D9F9F] hover:border-[#5B5F61]'
                            )}
                        >
                            <Folder className="h-3 w-3" />
                            {folder}
                        </button>
                    ))}
                </div>
            )}

            {/* Asset grid/list */}
            {filteredAssets.length === 0 ? (
                <EmptyLibrary />
            ) : viewMode === 'grid' ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {filteredAssets.map(asset => (
                        <AssetCard
                            key={asset.id}
                            asset={asset}
                            onClick={() => onAssetClick(asset)}
                            onDelete={onAssetDelete ? () => onAssetDelete(asset) : undefined}
                            onDuplicate={onAssetDuplicate ? () => onAssetDuplicate(asset) : undefined}
                        />
                    ))}
                </div>
            ) : (
                <div className="space-y-2">
                    {filteredAssets.map(asset => (
                        <AssetListItem
                            key={asset.id}
                            asset={asset}
                            onClick={() => onAssetClick(asset)}
                            onDelete={onAssetDelete ? () => onAssetDelete(asset) : undefined}
                            onDuplicate={onAssetDuplicate ? () => onAssetDuplicate(asset) : undefined}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

function AssetCard({
    asset,
    onClick,
    onDelete,
    onDuplicate
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
            <div className={cn(
                'aspect-[4/3] flex items-center justify-center bg-[#F8F9F7]',
            )}>
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
                <p className="text-[15px] font-medium text-[#2D3538] tracking-tight truncate">{asset.title}</p>
                <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-[#9D9F9F]">{config?.label}</span>
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
                        <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onClick(); }}>
                            <ExternalLink className="h-4 w-4 mr-2" />
                            Open
                        </DropdownMenuItem>
                        {onDuplicate && (
                            <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onDuplicate(); }}>
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
                                    onClick={(e) => { e.stopPropagation(); onDelete(); }}
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
    onDuplicate
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
                    <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onClick(); }}>
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Open
                    </DropdownMenuItem>
                    {onDuplicate && (
                        <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onDuplicate(); }}>
                            <Copy className="h-4 w-4 mr-2" />
                            Duplicate
                        </DropdownMenuItem>
                    )}
                    {onDelete && (
                        <>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                                onClick={(e) => { e.stopPropagation(); onDelete(); }}
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
            <h3 className="font-serif text-[24px] text-[#2D3538] mb-2">No assets yet</h3>
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
