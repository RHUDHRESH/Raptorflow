import { VertexAIEmbeddings } from "@langchain/google-vertexai";
import { createClient } from "@supabase/supabase-js";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
const supabase = (supabaseUrl && supabaseKey) 
    ? createClient(supabaseUrl, supabaseKey)
    : null;

const embeddings = new VertexAIEmbeddings({
    model: "text-embedding-004"
});

export async function ingestFileContent(content: string, metadata: any = {}) {
    if (!supabase) throw new Error("Supabase not configured");

    // 1. Split text into chunks
    const splitter = new RecursiveCharacterTextSplitter({
        chunkSize: 1000,
        chunkOverlap: 200,
    });
    
    const docs = await splitter.createDocuments([content]);

    // 2. Embed and Store
    for (const doc of docs) {
        const embedding = await embeddings.embedQuery(doc.pageContent);
        
        const { error } = await supabase
            .from('muse_assets')
            .insert({
                content: doc.pageContent,
                metadata: {
                    ...metadata,
                    source: metadata.filename || 'uploaded-file',
                    ingested_at: new Date().toISOString()
                },
                embedding
            });

        if (error) {
            console.error("Error storing chunk:", error);
        }
    }

    return docs.length;
}
