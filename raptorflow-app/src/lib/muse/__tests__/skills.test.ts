import { describe, it, expect } from 'vitest';
import { loadSystemSkills } from '../skills-manager';
import { convertSkillsToTools } from '../skill-converter';

describe('Skills Manager', () => {
    it('should load system skills from disk', async () => {
        const skills = await loadSystemSkills();
        expect(skills.length).toBeGreaterThan(0);
        
        const linkedinSkill = skills.find(s => s.id === 'linkedin-thought-leader');
        expect(linkedinSkill).toBeDefined();
        expect(linkedinSkill?.type).toBe('system');
        expect(linkedinSkill?.inputs).toHaveProperty('topic');
    });
});

describe('Skill Converter', () => {
    it('should convert skills to LangChain tools', async () => {
        const skills = await loadSystemSkills();
        const tools = convertSkillsToTools(skills);
        
        expect(tools.length).toBe(skills.length);
        expect(tools[0].name).toBeDefined();
        
        const linkedinTool = tools.find(t => t.name === 'linkedin-thought-leader');
        expect(linkedinTool).toBeDefined();
    });
});
