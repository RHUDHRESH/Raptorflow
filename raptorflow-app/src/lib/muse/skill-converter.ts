import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { Skill } from "./skills-manager";
import { getInferenceConfig, isInferenceReady } from "../inference-config";
import { invokeWithModelFallback } from "../vertexai";
import { SystemMessage, HumanMessage } from "@langchain/core/messages";

export function convertSkillToTool(skill: Skill): DynamicStructuredTool {
    // Dynamically build Zod schema from skill.inputs
    const schemaShape: Record<string, z.ZodTypeAny> = {};

    for (const [key, _type] of Object.entries(skill.inputs)) {
        schemaShape[key] = z.string().describe(`Input for ${key}`);
    }

    if (Object.keys(schemaShape).length === 0) {
        schemaShape['query'] = z.string().describe("The primary input or topic for this skill");
    }

    return new DynamicStructuredTool({
        name: skill.id,
        description: `${skill.name}: ${skill.description}`,
        schema: z.object(schemaShape),
        func: async (args) => {
            if (!isInferenceReady()) {
                return "AI model not available. Please configure INFERENCE_SIMPLE credentials.";
            }

            // Execute the Skill using the LLM
            const systemMsg = new SystemMessage(
                `${skill.instructions}\n\nCRITICAL: Be surgical. Cut the fluff. Every word must earn its place. Do not include introductory or concluding conversational filler.`
            );

            // Create a clear input for the model
            const inputStr = Object.entries(args)
                .map(([k, v]) => `${k}: ${v}`)
                .join('\n');

            const userMsg = new HumanMessage(inputStr);

            const config = getInferenceConfig();
            const modelName = config.models.general || "gemini-2.5-flash-lite";

            try {
                const response = await invokeWithModelFallback({
                    input: [systemMsg, userMsg],
                    modelName,
                    temperature: 0.7,
                    maxTokens: 8192,
                });
                // Return the content as the tool output
                return typeof response.content === 'string' ? response.content : JSON.stringify(response.content);
            } catch (error) {
                console.error(`Error executing skill ${skill.id}:`, error);
                return `Error executing skill: ${error}`;
            }
        }
    });
}

export function convertSkillsToTools(skills: Skill[]) {
    return skills.map(convertSkillToTool);
}
