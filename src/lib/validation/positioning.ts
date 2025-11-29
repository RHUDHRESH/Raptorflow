import { z } from 'zod';

/**
 * Zod Schema for Positioning Form (Wizard 2.0)
 * Defines all fields required for the brand positioning wizard.
 */
export const PositioningFormSchema = z.object({
    // Step 1: Founder & Brand Identity
    founder_name: z.string().min(2, "Founder name is required"),
    founder_background: z.string().optional(), // Optional context
    brand_name: z.string().min(2, "Brand name is required"),
    category: z.string().min(2, "Category is required (e.g., 'SaaS', 'E-commerce')"),

    // Step 2: Audience & Pain
    audience_summary: z.string().min(10, "Describe your target audience (min 10 chars)"),
    core_pain: z.string().min(10, "Describe the core pain point (min 10 chars)"),

    // Step 3: Promise & Differentiator
    core_promise: z.string().min(10, "What is your core promise? (min 10 chars)"),
    differentiator: z.string().min(10, "What makes you different? (min 10 chars)"),

    // Step 4: Strategic Narrative
    positioning_statement: z.string().optional(), // Can be auto-generated, so optional initially
    mission_statement: z.string().optional(),
    origin_story: z.string().optional(),
});

export type PositioningFormValues = z.infer<typeof PositioningFormSchema>;

/**
 * Database Record Type
 * Represents the structure stored in Supabase 'positioning' table
 */
export interface PositioningRecord extends PositioningFormValues {
    id: string;
    workspace_id: string;
    created_at: string;
    updated_at: string;
    status: 'draft' | 'published';
}

/**
 * Helper to validate positioning form data
 */
export function validatePositioningForm(data: unknown) {
    return PositioningFormSchema.safeParse(data);
}
