import { DynamicTool } from "@langchain/core/tools";

// RAG functionality is disabled in development mode to avoid credential issues
// In production, this should use proper VertexAI embeddings and Supabase

export async function searchMuseAssets(_query: string, _limit = 5): Promise<string> {
    // Mock implementation - returns empty in dev mode
    console.info("RAG search disabled - returning mock empty result");
    return "";
}

export const retrieveContextTool = new DynamicTool({
    name: "retrieve_brand_context",
    description: "Retrieves relevant context from the Brand Kit and Muse Library. Use this to check brand voice, past examples, or foundational facts.",
    func: async (_query: string) => {
        // In development, return a helpful placeholder
        return "No relevant context found. (RAG disabled in development mode)";
    }
});
