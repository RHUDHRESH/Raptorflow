import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { Skill } from "./skills-manager";

export function convertSkillToTool(skill: Skill): DynamicStructuredTool {
    // Dynamically build Zod schema from skill.inputs
    // skill.inputs is Record<string, any> e.g. { "topic": "string", "tone": "string" }
    
    const schemaShape: Record<string, z.ZodTypeAny> = {};
    
    for (const [key, type] of Object.entries(skill.inputs)) {
        // Simple mapping for now
        schemaShape[key] = z.string().describe(`Input for ${key}`);
    }
    
    // Always allow a generic "context" or "query" if inputs are empty
    if (Object.keys(schemaShape).length === 0) {
        schemaShape['query'] = z.string().describe("The primary input or topic for this skill");
    }

    return new DynamicStructuredTool({
        name: skill.id,
        description: `${skill.name}: ${skill.description}`,
        schema: z.object(schemaShape),
        func: async (args) => {
            // The tool execution just returns the structured args and ID.
            // The graph will handle the actual "Prompting" phase using the skill instructions.
            return JSON.stringify({
                _skill_id: skill.id,
                ...args
            });
        }
    });
}

export function convertSkillsToTools(skills: Skill[]) {
    return skills.map(convertSkillToTool);
}
