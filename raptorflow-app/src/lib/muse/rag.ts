import { DynamicTool } from "@langchain/core/tools";
import fs from "fs/promises";
import path from "path";

const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "";
const internalKey = process.env.RF_INTERNAL_KEY || "";
const tenantId = process.env.DEFAULT_TENANT_ID || "";

async function loadFoundationFallback(): Promise<string> {
    try {
        const filePath = path.join(process.cwd(), "public", "foundation_text.json");
        const raw = await fs.readFile(filePath, "utf-8");
        return raw.slice(0, 2000);
    } catch (error) {
        console.warn("Failed to load foundation_text.json fallback:", error);
        return "";
    }
}

export async function searchMuseAssets(
    query: string,
    limit = 5,
    filters?: Record<string, unknown>
): Promise<string> {
    if (!backendUrl || !internalKey || !tenantId) {
        console.warn("Muse RAG backend not configured. Falling back to local metadata.");
        return loadFoundationFallback();
    }

    try {
        const response = await fetch(`${backendUrl}/v1/muse/search`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-RF-Internal-Key": internalKey,
                "X-Tenant-ID": tenantId
            },
            body: JSON.stringify({ query, limit, filters })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.warn("Muse RAG search failed:", errorText);
            return loadFoundationFallback();
        }

        const data = await response.json();
        const results = Array.isArray(data?.results) ? data.results : [];

        if (results.length === 0) {
            return loadFoundationFallback();
        }

        return results
            .map((result: any) => result.content)
            .filter(Boolean)
            .join("\n\n");
    } catch (error) {
        console.error("Muse RAG search error:", error);
        return loadFoundationFallback();
    }
}

export const retrieveContextTool = new DynamicTool({
    name: "retrieve_brand_context",
    description:
        "Retrieves relevant context from the Brand Kit and Muse Library. Use this to check brand voice, past examples, or foundational facts.",
    func: async (query: string) => {
        return searchMuseAssets(query, 6, { type: "foundation" });
    }
});
