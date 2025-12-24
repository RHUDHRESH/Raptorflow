import { StateGraph, MessagesAnnotation, MemorySaver } from "@langchain/langgraph";
import { getGemini15Flash } from "../vertexai";
import { loadSystemSkills } from "./skills-manager";
import { convertSkillsToTools } from "./skill-converter";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import { PostgresSaver } from "@langchain/langgraph-checkpoint-postgres";
import { Pool } from 'pg';
import { retrieveContextTool } from "./rag";
import { saveAssetTool } from "./tools";
import { AIMessage } from "@langchain/core/messages";

// Lazy initialization for PostgreSQL pool and checkpointer
let pool: Pool | null = null;
let checkpointer: PostgresSaver | MemorySaver | null = null;

function getPool(): Pool | null {
    if (!process.env.DATABASE_URL) {
        console.warn("DATABASE_URL not set - PostgreSQL pool unavailable");
        return null;
    }
    if (!pool) {
        pool = new Pool({
            connectionString: process.env.DATABASE_URL,
        });
    }
    return pool;
}

function getCheckpointer(): PostgresSaver | MemorySaver {
    if (!checkpointer) {
        const poolInstance = getPool();
        if (poolInstance) {
            checkpointer = new PostgresSaver(poolInstance);
        } else {
            // Fallback to in-memory checkpointer for development
            console.warn("Using in-memory checkpointer - state will not persist across restarts");
            checkpointer = new MemorySaver();
        }
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
    // Use lazy-initialized model for tool selection
    const model = getGemini15Flash();
    if (!model) {
        console.warn("Vertex AI model not available - returning mock response");
        return {
            messages: [
                new AIMessage({
                    content: "I am currently in offline/mock mode because AI credentials (INFERENCE_SIMPLE) are missing. I can still help you navigate the UI, but I won't be able to generate real content until credentials are provided."
                })
            ]
        };
    }
    const boundModel = model.bindTools(tools);
    const response = await boundModel.invoke(state.messages);
    return { messages: [response] };
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
