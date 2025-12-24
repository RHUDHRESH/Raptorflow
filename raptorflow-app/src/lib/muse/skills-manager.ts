import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase Client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://dummy.supabase.co';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'dummy-key'; // Service role for backend access

// Prevent crash if envs are missing during build/test, but warn
const supabase = createClient(supabaseUrl, supabaseKey);

export interface SkillManifest {
    id: string;
    name: string;
    description: string;
    version: string;
    inputs: Record<string, unknown>;
    output: string;
    tools?: string[]; // List of tool names this skill uses
}

export interface Skill extends SkillManifest {
    instructions: string;
    type: 'system' | 'custom';
}

const SYSTEM_SKILLS_DIR = path.join(process.cwd(), 'src/skills/system');

export async function loadSystemSkills(): Promise<Skill[]> {
    // Ensure directory exists
    if (!fs.existsSync(SYSTEM_SKILLS_DIR)) {
        // In some environments (like Vercel serverless), we might need to be careful about paths.
        // For now, assuming local/container fs.
        console.warn(`System skills directory not found: ${SYSTEM_SKILLS_DIR}`);
        return [];
    }

    const files = fs.readdirSync(SYSTEM_SKILLS_DIR).filter(f => f.endsWith('.md'));
    const skills: Skill[] = [];

    for (const file of files) {
        const filePath = path.join(SYSTEM_SKILLS_DIR, file);
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        const { data, content } = matter(fileContent);

        // Validate Frontmatter
        if (!data.id || !data.name) {
            console.warn(`Skipping invalid skill file: ${file}`);
            continue;
        }

        skills.push({
            id: data.id,
            name: data.name,
            description: data.description || '',
            version: data.version || '1.0.0',
            inputs: data.inputs || {},
            output: data.output || 'string',
            tools: data.tools || [],
            instructions: content.trim(),
            type: 'system'
        });
    }

    return skills;
}

export async function loadCustomSkills(_userId?: string): Promise<Skill[]> {
    if (!supabaseUrl || !supabaseKey) return [];

    const { data, error } = await supabase
        .from('skills')
        .select('*')
        .eq('type', 'custom');

    if (error) {
        console.error('Error fetching custom skills:', error);
        return [];
    }

    return data.map((row: Record<string, unknown>) => ({
        id: row.id as string,
        name: row.name as string,
        description: row.description as string,
        version: '1.0.0',
        inputs: {}, // Default empty inputs for now
        output: 'string',
        tools: [],
        instructions: row.instructions as string,
        type: 'custom'
    }));
}

export async function getAllSkills(): Promise<Skill[]> {
    const system = await loadSystemSkills();
    const custom = await loadCustomSkills();
    return [...system, ...custom];
}

export function getSkillById(skills: Skill[], id: string): Skill | undefined {
    return skills.find(s => s.id === id);
}
