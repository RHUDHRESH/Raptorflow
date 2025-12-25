'use client';

import { useEffect, useState } from 'react';
import { Asset, ASSET_TYPES } from '@/components/muse/types';

const STORAGE_KEY = 'rf_muse_assets_v1';

type StoredAsset = Omit<Asset, 'createdAt' | 'updatedAt'> & {
    createdAt: string;
    updatedAt: string;
};

function serializeAssets(assets: Asset[]): StoredAsset[] {
    return assets.map((asset) => ({
        ...asset,
        createdAt: asset.createdAt.toISOString(),
        updatedAt: asset.updatedAt.toISOString(),
    }));
}

function deserializeAssets(raw: StoredAsset[]): Asset[] {
    const allowedTypes = new Set(ASSET_TYPES.map((type) => type.type));
    return raw
        .filter((asset) => allowedTypes.has(asset.type))
        .map((asset) => ({
            ...asset,
            createdAt: new Date(asset.createdAt),
            updatedAt: new Date(asset.updatedAt),
        }));
}

function readStoredAssets(fallback: Asset[]): Asset[] {
    if (typeof window === 'undefined') return fallback;

    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return fallback;
        const parsed = JSON.parse(raw) as StoredAsset[];
        if (!Array.isArray(parsed)) return fallback;
        return deserializeAssets(parsed);
    } catch (error) {
        console.warn('Failed to load Muse assets from storage', error);
        return fallback;
    }
}

function persistAssets(assets: Asset[]) {
    if (typeof window === 'undefined') return;

    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(serializeAssets(assets)));
    } catch (error) {
        console.warn('Failed to save Muse assets to storage', error);
    }
}

export function useMuseAssets(fallbackAssets: Asset[]) {
    const [assets, setAssets] = useState<Asset[]>(fallbackAssets);
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
        setAssets(readStoredAssets(fallbackAssets));
        setIsLoaded(true);
    }, [fallbackAssets]);

    useEffect(() => {
        if (!isLoaded) return;
        persistAssets(assets);
    }, [assets, isLoaded]);

    return { assets, setAssets, isLoaded };
}
