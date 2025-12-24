import { NextRequest, NextResponse } from "next/server";
import { createMuseGraph } from "@/lib/muse/agent";
import { HumanMessage } from "@langchain/core/messages";

export async function POST(req: NextRequest) {
    try {
        const { message, threadId } = await req.json();

        if (!message) {
            return NextResponse.json({ error: "Message is required" }, { status: 400 });
        }

        const graph = createMuseGraph();

        // Configuration for the run (threadId for persistence)
        const config = {
            configurable: {
                thread_id: threadId || "default-thread",
            },
        };

        // Stream the responses
        // Note: For a simple implementation, we invoke and return the result.
        // For production, use LangChain's streaming capabilities.
        const result = await graph.invoke(
            {
                messages: [new HumanMessage(message)],
            },
            config
        );

        const lastMessage = result.messages[result.messages.length - 1];

        return NextResponse.json({
            response: lastMessage.content,
            threadId: config.configurable.thread_id
        });

    } catch (error: any) {
        console.error("Muse API Error:", error);
        // Return a graceful fallback response instead of crashing
        return NextResponse.json({
            response: "I'm currently experiencing technical difficulties. Please try again in a moment, or check if your API credentials are configured correctly.",
            threadId: "error-thread",
            error: error.message
        });
    }
}
