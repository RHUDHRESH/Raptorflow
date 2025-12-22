/**
 * Black Box Z — Skill Library
 */

import { SkillRole } from './blackbox-types';

export interface Skill {
    id: string;
    name: string;
    role: SkillRole;
    description: string;
    prompt_template: string;
    version: string;
}

export const HOOK_SKILLS: Skill[] = [
    {
        id: 'curiosity_gap',
        name: 'Curiosity Gap',
        role: 'hook',
        version: '1.0',
        description: 'Opens a gap in knowledge that the reader must close.',
        prompt_template: 'Start with a hook that highlights a surprising gap between what the audience knows and the truth of the situation.'
    },
    {
        id: 'contrarian_opener',
        name: 'Contrarian Opener',
        role: 'hook',
        version: '1.0',
        description: 'Challenges a commonly held belief in the industry.',
        prompt_template: 'Challenge a popular but ineffective marketing belief right at the start.'
    },
    {
        id: 'founder_confession',
        name: 'Founder Confession',
        role: 'hook',
        version: '1.0',
        description: 'Uses vulnerability to build instant trust.',
        prompt_template: 'Begin with a raw, honest admission of a past mistake or struggle.'
    }
];

export const STRUCTURE_SKILLS: Skill[] = [
    {
        id: 'problem_agitate_solve',
        name: 'PAS Framework',
        role: 'structure',
        version: '1.0',
        description: 'Problem, Agitate, Solve structure.',
        prompt_template: 'Structure the message by first identifying a core problem, making its consequences felt, and then presenting the solution.'
    },
    {
        id: 'inverted_pyramid',
        name: 'Inverted Pyramid',
        role: 'structure',
        version: '1.0',
        description: 'Lead with the most important info first.',
        prompt_template: 'Put the most critical value proposition in the first sentence, followed by supporting details.'
    }
];

export const TONE_SKILLS: Skill[] = [
    {
        id: 'calm_executive',
        name: 'Calm Executive',
        role: 'tone',
        version: '1.0',
        description: 'Polished, authoritative, yet understated.',
        prompt_template: 'Use a tone that is professional, authoritative, and calm. Avoid hype and excessive punctuation.'
    },
    {
        id: 'direct_surgeon',
        name: 'Direct Surgeon',
        role: 'tone',
        version: '1.0',
        description: 'Surgical precision, zero fluff.',
        prompt_template: 'Write with extreme brevity and precision. Every word must earn its place.'
    },
    {
        id: 'founder_to_founder',
        name: 'Founder to Founder',
        role: 'tone',
        version: '1.0',
        description: 'Peer-to-peer, informal but serious.',
        prompt_template: 'Write as one founder talking to another. Use informal but serious language.'
    }
];

export const CTA_SKILLS: Skill[] = [
    {
        id: 'reply_to_qualify',
        name: 'Reply to Qualify',
        role: 'cta',
        version: '1.0',
        description: 'Asks for a specific reply instead of a link click.',
        prompt_template: 'Instead of a link, ask the reader to reply with a specific keyword if they want the next step.'
    },
    {
        id: 'micro_yes_ladder',
        name: 'Micro-Yes Ladder',
        role: 'cta',
        version: '1.0',
        description: 'Asks a low-friction question to get initial commitment.',
        prompt_template: 'End with a simple "yes/no" question that is easy to answer and starts a conversation.'
    }
];

export const ALL_SKILLS = [
    ...HOOK_SKILLS,
    ...STRUCTURE_SKILLS,
    ...TONE_SKILLS,
    ...CTA_SKILLS
];

export function getSkill(id: string): Skill | undefined {
    return ALL_SKILLS.find(s => s.id === id);
}
