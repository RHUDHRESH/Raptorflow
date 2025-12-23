import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { createClient } from "@supabase/supabase-js";
import { AssetType } from "../../components/muse/types";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
const supabase = (supabaseUrl && supabaseKey) 
    ? createClient(supabaseUrl, supabaseKey)
    : null;

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
        if (!supabase) return "Supabase not configured. Asset not saved.";

        const { data, error } = await supabase
            .from('muse_assets') // We'll store assets here, or a dedicated 'assets' table
            .insert({
                title,
                content,
                type,
                metadata: {
                    ...metadata,
                    is_final_asset: true,
                    created_at: new Date().toISOString()
                }
            })
            .select()
            .single();

        if (error) {
            console.error("Error saving asset:", error);
            return `Failed to save asset: ${error.message}`;
        }

        return `Asset saved successfully with ID: ${data.id}`;
    }
});
