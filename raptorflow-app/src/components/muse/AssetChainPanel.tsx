import React from 'react';
import { cn } from '@/lib/utils';
import { Asset, ASSET_TYPES } from './types';
import { ArrowDown, Link as LinkIcon, ExternalLink } from 'lucide-react';

interface AssetChainPanelProps {
    currentAsset: Asset;
    allAssets: Asset[];
    onSelectAsset?: (asset: Asset) => void;
    className?: string;
}

export function AssetChainPanel({
    currentAsset,
    allAssets,
    onSelectAsset,
    className
}: AssetChainPanelProps) {
    // Find parent
    const parent = currentAsset.parentAssetId
        ? allAssets.find(a => a.id === currentAsset.parentAssetId)
        : null;

    // Find children (assets that have this asset as parent OR are in linkedAssets)
    const children = allAssets.filter(a =>
        a.parentAssetId === currentAsset.id ||
        currentAsset.linkedAssets?.includes(a.id)
    );

    const renderAssetCard = (asset: Asset, relationship: 'parent' | 'current' | 'child') => {
        const config = ASSET_TYPES.find(t => t.type === asset.type);
        const Icon = config ? require('lucide-react')[config.icon] : LinkIcon;

        return (
            <div
                key={asset.id}
                onClick={() => relationship !== 'current' && onSelectAsset?.(asset)}
                className={cn(
                    'p-3 rounded-lg border transition-all',
                    relationship === 'current'
                        ? 'bg-primary/5 border-primary ring-1 ring-primary/20 cursor-default'
                        : 'bg-card border-border hover:border-primary/50 cursor-pointer hover:shadow-sm'
                )}
            >
                <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                        <div className={cn(
                            'h-8 w-8 rounded-full flex items-center justify-center',
                            relationship === 'current' ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
                        )}>
                            {Icon && <Icon className="h-4 w-4" />}
                        </div>
                        <div>
                            <p className={cn(
                                'text-sm font-medium leading-none',
                                relationship === 'current' ? 'text-primary' : 'text-foreground'
                            )}>
                                {config?.label || 'Asset'}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
                                {asset.title}
                            </p>
                        </div>
                    </div>
                </div>
                {relationship !== 'current' && (
                    <div className="mt-2 flex items-center gap-1 text-[10px] text-muted-foreground uppercase tracking-wider font-medium">
                        <ExternalLink className="h-3 w-3" />
                        {relationship === 'parent' ? 'Source' : 'Derived'}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className={cn('space-y-4', className)}>
            <div className="flex items-center gap-2 mb-6">
                <LinkIcon className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-semibold">Asset Chain</h3>
            </div>

            <div className="relative space-y-2">
                {/* Connection Line Layer */}
                <div className="absolute left-[1.65rem] top-4 bottom-4 w-0.5 bg-border/50 -z-10" />

                {/* Parent */}
                {parent ? (
                    <>
                        {renderAssetCard(parent, 'parent')}
                        <div className="flex justify-center py-1">
                            <ArrowDown className="h-4 w-4 text-muted-foreground/50" />
                        </div>
                    </>
                ) : (
                    <div className="p-4 border border-dashed border-border rounded-lg text-center bg-muted/20">
                        <span className="text-xs text-muted-foreground">No source asset</span>
                    </div>
                )}

                {/* Arrow to current */}
                <div className="flex justify-center py-1">
                    <ArrowDown className="h-4 w-4 text-primary/50" />
                </div>

                {/* Current */}
                {renderAssetCard(currentAsset, 'current')}

                {/* Children */}
                {children.length > 0 && (
                    <>
                        <div className="flex justify-center py-1">
                            <ArrowDown className="h-4 w-4 text-muted-foreground/50" />
                        </div>
                        <div className="space-y-2 pl-4 border-l-2 border-border/30 ml-6">
                            {children.map(child => renderAssetCard(child, 'child'))}
                        </div>
                    </>
                )}

                {children.length === 0 && (
                    <div className="mt-4 p-3 text-center">
                        <p className="text-xs text-muted-foreground italic">No derived assets yet</p>
                        <button className="mt-2 text-xs text-primary hover:underline">
                            + Create derived asset
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
