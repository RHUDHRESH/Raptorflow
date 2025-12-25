import { StateGraph, MessagesAnnotation, MemorySaver } from "@langchain/langgraph";
import { getInferenceConfig, getInferenceStatus } from "../inference-config";
import { invokeWithModelFallback } from "../vertexai";
import { loadSystemSkills } from "./skills-manager";
import { convertSkillsToTools } from "./skill-converter";
import { ToolNode } from "@langchain/langgraph/prebuilt";
// PostgreSQL imports removed to avoid Turbopack symlink issues on Windows
// import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
// import { Pool } from 'pg';
import { retrieveContextTool } from "./rag";
import { saveAssetTool } from "./tools";
import { AIMessage } from "@langchain/core/messages";

// Singleton in-memory checkpointer for development
// In production, this should be replaced with a persistent checkpointer
let checkpointer: MemorySaver | null = null;

function getCheckpointer(): MemorySaver {
    if (!checkpointer) {
        console.info("Using in-memory checkpointer for development");
        checkpointer = new MemorySaver();
    }
    return checkpointer;
}

async function getAllTools() {
    const skills = await loadSystemSkills();
    const skillTools = convertSkillsToTools(skills);
    return [...skillTools, retrieveContextTool, saveAssetTool];
}

async function agentNode(state: typeof MessagesAnnotation.State) {
    const tools = await getAllTools();
    const inferenceStatus = getInferenceStatus();
    if (!inferenceStatus.ready) {
        console.warn("Vertex AI model not available - returning mock response");
        return {
            messages: [
                new AIMessage({
                    content: inferenceStatus.reason ||
                        "AI inference is unavailable. Configure Vertex credentials to enable responses."
                })
            ]
        };
    }

    const config = getInferenceConfig();
    const modelName = config.models.general || "gemini-2.5-flash-lite";

    try {
        const response = await invokeWithModelFallback({
            input: state.messages,
            modelName,
            temperature: 0.3,
            maxTokens: 2048,
            tools,
        });
        return { messages: [response as AIMessage] };
    } catch (error) {
        console.error("Muse model invocation failed:", error);
        return {
            messages: [
                new AIMessage({
                    content: "Model access failed. Please verify your Gemini model name and API key, then try again."
                })
            ]
        };
    }
}

async function executeTools(state: typeof MessagesAnnotation.State) {
    const tools = await getAllTools();
    const toolNode = new ToolNode(tools);
    return toolNode.invoke(state);
}

function shouldContinue(state: typeof MessagesAnnotation.State) {
    const lastMessage = state.messages[state.messages.length - 1] as AIMessage;
    if (lastMessage.tool_calls?.length) {
        return "tools";
    }
    return "__end__";
}

export const createMuseGraph = () => {
    const workflow = new StateGraph(MessagesAnnotation)
        .addNode("agent", agentNode)
        .addNode("tools", executeTools)
        .addEdge("__start__", "agent")
        .addConditionalEdges("agent", shouldContinue)
        .addEdge("tools", "agent");

    return workflow.compile({ checkpointer: getCheckpointer() });
};
