import { supabase } from '../supabase';
import { Asset, AssetType, GenerationStatus, CanvasData } from '@/components/muse/types';

/**
 * DB Mapping for Muse Assets
 */
export interface DBAsset {
    id: string;
    workspace_id: string;
    content: string;
    asset_type: string;
    title?: string;
    generation_prompt?: string;
    metadata: {
        title?: string;
        folder?: string;
        linkedCampaign?: string;
        linkedCohort?: string;
        granular_type?: AssetType;
        status?: GenerationStatus;
        [key: string]: any;
    };
    status: string;
    created_at: string;
    updated_at: string;
}

const DEFAULT_WORKSPACE_ID = '00000000-0000-0000-0000-000000000000';

function mapDBAssetToFrontend(db: DBAsset): Asset {
    let content: string | CanvasData = db.content;
    try {
        if (content.startsWith('{')) {
            content = JSON.parse(content);
        }
    } catch (e) {
        // Keep as string
    }

    return {
        id: db.id,
        type: db.metadata.granular_type || (db.asset_type as AssetType),
        title: db.title || db.metadata.title || 'Untitled Asset',
        content,
        prompt: db.generation_prompt,
        createdAt: new Date(db.created_at),
        updatedAt: new Date(db.updated_at),
        folder: db.metadata.folder,
        linkedCampaign: db.metadata.linkedCampaign,
        linkedCohort: db.metadata.linkedCohort,
        status: (db.status === 'ready' ? 'complete' : db.status) as GenerationStatus,
    };
}

function mapFrontendAssetToDB(asset: Asset): Partial<DBAsset> {
    // Map to the broad categories required by DB constraint if possible
    let dbType = 'text';
    if (asset.type.includes('email')) dbType = 'email';
    else if (asset.type.includes('social_post') || asset.type.includes('social-post')) dbType = 'social_post';
    else if (asset.type === 'meme') dbType = 'meme';

    return {
        id: asset.id,
        workspace_id: DEFAULT_WORKSPACE_ID,
        title: asset.title,
        content: typeof asset.content === 'object' ? JSON.stringify(asset.content) : asset.content,
        asset_type: dbType,
        generation_prompt: asset.prompt,
        status: asset.status === 'complete' ? 'ready' : asset.status,
        updated_at: new Date().toISOString(),
        metadata: {
            title: asset.title,
            folder: asset.folder,
            linkedCampaign: asset.linkedCampaign,
            linkedCohort: asset.linkedCohort,
            granular_type: asset.type,
            status: asset.status,
        },
    };
}

export async function getAssets(options: {
    limit?: number;
    offset?: number;
    type?: string;
    folder?: string;
    status?: string;
    search?: string;
} = {}): Promise<Asset[]> {
    let query = supabase
        .from('muse_assets')
        .select('*')
        .order('created_at', { ascending: false });

    if (options.limit) query = query.range(options.offset || 0, (options.offset || 0) + options.limit - 1);
    if (options.type) query = query.eq('metadata->>granular_type', options.type);
    if (options.folder) query = query.eq('metadata->>folder', options.folder);
    if (options.status) query = query.eq('status', options.status === 'complete' ? 'ready' : options.status);

    if (options.search) {
        query = query.or(`title.ilike.%${options.search}%,generation_prompt.ilike.%${options.search}%`);
    }

    const { data, error } = await query;

    if (error) {
        console.error('Error fetching assets:', error);
        return [];
    }

    return (data || []).map(mapDBAssetToFrontend);
}

export async function getAsset(id: string): Promise<Asset | undefined> {
    const { data, error } = await supabase
        .from('muse_assets')
        .select('*')
        .eq('id', id)
        .single();

    if (error) {
        console.error('Error fetching asset:', error);
        return undefined;
    }

    return mapDBAssetToFrontend(data);
}

export async function createAsset(asset: Asset): Promise<Asset | null> {
    const dbAsset = mapFrontendAssetToDB(asset);
    const { data, error } = await supabase
        .from('muse_assets')
        .insert(dbAsset)
        .select()
        .single();

    if (error) {
        console.error('Error creating asset:', error);
        return null;
    }

    return mapDBAssetToFrontend(data);
}

export async function updateAsset(asset: Asset): Promise<Asset | null> {
    const dbAsset = mapFrontendAssetToDB(asset);
    // Remove id from update payload
    delete dbAsset.id;

    const { data, error } = await supabase
        .from('muse_assets')
        .update(dbAsset)
        .eq('id', asset.id)
        .select()
        .single();

    if (error) {
        console.error('Error updating asset:', error);
        return null;
    }

    return mapDBAssetToFrontend(data);
}

export async function deleteAsset(id: string): Promise<boolean> {
    const { error } = await supabase
        .from('muse_assets')
        .delete()
        .eq('id', id);

    if (error) {
        console.error('Error deleting asset:', error);
        return false;
    }

    return true;
}

export async function duplicateAsset(id: string): Promise<Asset | null> {
    const asset = await getAsset(id);
    if (!asset) return null;

    const newAsset: Asset = {
        ...asset,
        id: crypto.randomUUID(),
        title: `${asset.title} (Copy)`,
        createdAt: new Date(),
        updatedAt: new Date(),
    };

    return createAsset(newAsset);
}
