/**
 * Muse — Asset Creator Type Definitions
 */

export type AssetType =
    // Text-based
    | 'email'
    | 'sales-email'
    | 'nurture-email'
    | 'tagline'
    | 'one-liner'
    | 'brand-story'
    | 'video-script'
    | 'social-post'
    | 'product-description'
    | 'product-name'
    | 'lead-gen-pdf'
    | 'sales-talking-points'
    // Visual
    | 'meme'
    | 'social-card';

export type AssetCategory = 'text' | 'visual' | 'strategy';

export interface AssetTypeConfig {
    type: AssetType;
    label: string;
    category: AssetCategory;
    description: string;
    icon: string; // Lucide icon name
}

export const ASSET_TYPES: AssetTypeConfig[] = [
    // Text-based assets
    { type: 'email', label: 'Email', category: 'text', description: 'General email copy', icon: 'Mail' },
    { type: 'sales-email', label: 'Sales Email', category: 'text', description: 'Cold outreach or follow-up', icon: 'Send' },
    { type: 'nurture-email', label: 'Nurture Email', category: 'text', description: 'Relationship building sequence', icon: 'Heart' },
    { type: 'tagline', label: 'Tagline', category: 'text', description: 'Short memorable phrase', icon: 'Quote' },
    { type: 'one-liner', label: 'One-Liner', category: 'text', description: 'Elevator pitch', icon: 'MessageCircle' },
    { type: 'brand-story', label: 'Brand Story', category: 'text', description: 'Company narrative', icon: 'BookOpen' },
    { type: 'video-script', label: 'Video Script', category: 'text', description: 'Script for video content', icon: 'Video' },
    { type: 'social-post', label: 'Social Post', category: 'text', description: 'LinkedIn, Twitter, etc.', icon: 'Share2' },
    { type: 'product-description', label: 'Product Description', category: 'text', description: 'Feature and benefit copy', icon: 'Package' },
    { type: 'product-name', label: 'Product Name', category: 'strategy', description: 'Name ideas for products', icon: 'Lightbulb' },
    { type: 'lead-gen-pdf', label: 'Lead Gen PDF', category: 'text', description: 'PDF content outline', icon: 'FileText' },
    { type: 'sales-talking-points', label: 'Sales Talking Points', category: 'text', description: 'Key points for sales calls', icon: 'Mic' },
    // Visual assets
    { type: 'meme', label: 'Meme', category: 'visual', description: 'Image with text overlay', icon: 'Image' },
    { type: 'social-card', label: 'Social Card', category: 'visual', description: 'Visual post for feeds', icon: 'Layout' },
];

export type GenerationStatus = 'queued' | 'generating' | 'complete' | 'failed';

export interface CanvasElement {
    id: string;
    type: 'text' | 'image' | 'shape';
    x: number;
    y: number;
    width: number;
    height: number;
    rotation: number;
    content: string;
    style: Record<string, string | number>;
    locked: boolean;
    visible: boolean;
    animation?: 'none' | 'fade' | 'slide-up' | 'scale' | 'breathe';
}

export interface CanvasData {
    width: number;
    height: number;
    background: string;
    elements: CanvasElement[];
}

export interface Asset {
    id: string;
    type: AssetType;
    title: string;
    content: string | CanvasData;
    prompt?: string;
    createdAt: Date;
    updatedAt: Date;
    folder?: string;
    linkedCampaign?: string;
    linkedCohort?: string;
    parentAssetId?: string; // Parent asset ID for chain
    linkedAssets?: string[]; // Child/Related asset IDs
    tone?: string; // Tone setting (Casual, Professional, etc.)
    variants?: string[]; // Multi-variant IDs
    status: GenerationStatus;
}

export interface GenerationJob {
    id: string;
    prompt: string;
    assetType: AssetType;
    status: GenerationStatus;
    progress: number; // 0-100 (abstract, not real)
    startedAt: Date;
    asset?: Asset;
}

export function getAssetConfig(type: AssetType): AssetTypeConfig | undefined {
    return ASSET_TYPES.find(a => a.type === type);
}

export function isVisualAsset(type: AssetType): boolean {
    const config = getAssetConfig(type);
    return config?.category === 'visual';
}
