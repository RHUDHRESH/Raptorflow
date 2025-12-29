'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Asset, AssetType, GenerationStatus } from '@/components/muse/types';
import * as assetLib from '@/lib/muse/assets';

export function useAssets(options: {
    pageSize?: number;
    initialType?: string;
    initialFolder?: string;
    initialStatus?: string;
    initialSearch?: string;
} = {}) {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefetching, setIsRefetching] = useState(false);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [hasMore, setHasMore] = useState(true);

    // Filters
    const [type, setType] = useState<string | undefined>(options.initialType);
    const [folder, setFolder] = useState<string | undefined>(options.initialFolder);
    const [status, setStatus] = useState<string | undefined>(options.initialStatus);
    const [search, setSearch] = useState<string | undefined>(options.initialSearch);

    const pageSize = options.pageSize || 20;

    const fetchAssets = useCallback(async (isLoadMore = false) => {
        if (isLoadMore) setIsLoadingMore(true);
        else setIsRefetching(true);

        try {
            const offset = isLoadMore ? assets.length : 0;
            const data = await assetLib.getAssets({
                limit: pageSize,
                offset,
                type,
                folder,
                status,
                search
            });

            if (isLoadMore) {
                setAssets(prev => [...prev, ...data]);
            } else {
                setAssets(data);
            }

            setHasMore(data.length === pageSize);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to fetch assets'));
        } finally {
            setIsLoading(false);
            setIsRefetching(false);
            setIsLoadingMore(false);
        }
    }, [assets.length, pageSize, type, folder, status, search]);

    // Initial load and filter changes
    useEffect(() => {
        fetchAssets();
    }, [type, folder, status, search]);

    const refresh = useCallback(() => fetchAssets(), [fetchAssets]);

    const loadMore = useCallback(() => {
        if (hasMore && !isLoadingMore && !isRefetching) {
            fetchAssets(true);
        }
    }, [hasMore, isLoadingMore, isRefetching, fetchAssets]);

    const createAsset = async (asset: Asset) => {
        const created = await assetLib.createAsset(asset);
        if (created) {
            setAssets(prev => [created, ...prev]);
        }
        return created;
    };

    const updateAsset = async (asset: Asset) => {
        const updated = await assetLib.updateAsset(asset);
        if (updated) {
            setAssets(prev => prev.map(a => a.id === updated.id ? updated : a));
        }
        return updated;
    };

    const deleteAsset = async (id: string) => {
        const success = await assetLib.deleteAsset(id);
        if (success) {
            setAssets(prev => prev.filter(a => a.id !== id));
        }
        return success;
    };

    const duplicateAsset = async (id: string) => {
        const duplicated = await assetLib.duplicateAsset(id);
        if (duplicated) {
            setAssets(prev => [duplicated, ...prev]);
        }
        return duplicated;
    };

    return {
        assets,
        isLoading,
        isRefetching,
        isLoadingMore,
        error,
        hasMore,
        filters: {
            type,
            folder,
            status,
            search,
            setType,
            setFolder,
            setStatus,
            setSearch
        },
        refresh,
        loadMore,
        createAsset,
        updateAsset,
        deleteAsset,
        duplicateAsset
    };
}
