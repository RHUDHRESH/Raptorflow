import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    '';
const internalKey = process.env.RF_INTERNAL_KEY || '';
const tenantId = process.env.DEFAULT_TENANT_ID || '';

const TYPE_MAP: Record<string, string> = {
    email: 'email',
    'sales-email': 'email',
    'nurture-email': 'email',
    tagline: 'text',
    'one-liner': 'text',
    'brand-story': 'text',
    'video-script': 'text',
    'social-post': 'social_post',
    social_post: 'social_post',
    'product-description': 'text',
    'product-name': 'text',
    'lead-gen-pdf': 'document',
    'sales-talking-points': 'text',
    meme: 'meme',
    'social-card': 'image'
};

function normalizeAssetType(input: string) {
    const key = input.trim().toLowerCase();
    return TYPE_MAP[key] || 'text';
}

export const saveAssetTool = new DynamicStructuredTool({
    name: "save_generated_asset",
    description: "Saves a generated marketing asset to the Muse Library. Use this once an asset (email, post, etc.) is finalized.",
    schema: z.object({
        title: z.string().describe("Clear title for the asset"),
        content: z.string().describe("The full text content of the asset"),
        type: z.string().describe("The type of asset (e.g., 'social-post', 'sales-email')"),
        metadata: z.record(z.any()).optional().describe("Additional context like campaign ID or cohort ID")
    }),
    func: async ({ title, content, type, metadata }) => {
        if (!backendUrl || !internalKey || !tenantId) {
            return "Backend is not configured. Asset not saved.";
        }

        const payload = {
            content,
            asset_type: normalizeAssetType(type),
            metadata: {
                ...metadata,
                title,
                asset_subtype: type,
                is_final_asset: true,
                created_at: new Date().toISOString()
            }
        };

        try {
            const response = await fetch(`${backendUrl}/v1/muse/assets`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-RF-Internal-Key": internalKey,
                    "X-Tenant-ID": tenantId
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorText = await response.text();
                return `Failed to save asset: ${errorText}`;
            }

            const data = await response.json();
            return `Asset saved successfully with ID: ${data.id}`;
        } catch (error) {
            console.error("Error saving asset:", error);
            return "Failed to save asset due to a network or backend error.";
        }
    }
});
