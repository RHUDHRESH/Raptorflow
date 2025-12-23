import { VertexAIEmbeddings } from "@langchain/google-vertexai";
import { createClient } from "@supabase/supabase-js";
import { DynamicTool } from "@langchain/core/tools";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

const supabase = (supabaseUrl && supabaseKey) 
    ? createClient(supabaseUrl, supabaseKey)
    : { rpc: () => Promise.resolve({ data: [], error: null }) } as any;

const embeddings = new VertexAIEmbeddings({
    model: "text-embedding-004"
});

export async function searchMuseAssets(query: string, limit = 5) {
    try {
        const vector = await embeddings.embedQuery(query);
        
        const { data, error } = await supabase.rpc('match_muse_assets', {
            query_embedding: vector,
            match_threshold: 0.7, 
            match_count: limit
        });

        if (error) {
            console.error("RAG Search Error:", error);
            return [];
        }

        return data.map((d: any) => d.content).join("\n\n");
    } catch (e) {
        console.error("Embedding Error:", e);
        return "";
    }
}

export const retrieveContextTool = new DynamicTool({
    name: "retrieve_brand_context",
    description: "Retrieves relevant context from the Brand Kit and Muse Library. Use this to check brand voice, past examples, or foundational facts.",
    func: async (query: string) => {
        const results = await searchMuseAssets(query);
        return results || "No relevant context found.";
    }
});
