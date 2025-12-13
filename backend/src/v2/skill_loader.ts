import fs from 'fs';
import path from 'path';
import { z } from 'zod';
import { ToolDescriptor } from './types';
import { toolbox, createTool } from './toolbox';

// =====================================================
// SKILL SHEET SCHEMA
// =====================================================

const SkillSheetSchema = z.object({
  skill_name: z.string(),
  description: z.string(),
  category: z.string(),
  parameters: z.record(z.any()),
  output_format: z.record(z.any()).optional(),
  cost_estimate: z.number().optional(),
  timeout_ms: z.number().optional(),
  retry_policy: z.object({
    max_attempts: z.number(),
    backoff_ms: z.number()
  }).optional(),
  implementation: z.string(), // Code or reference
  examples: z.array(z.object({
    input: z.record(z.any()),
    output: z.record(z.any()),
    explanation: z.string().optional()
  })).optional()
});

type SkillSheet = z.infer<typeof SkillSheetSchema>;

// =====================================================
// SKILL SHEET PARSER
// =====================================================

export class SkillSheetLoader {
  private static instance: SkillSheetLoader;
  private skillsDir: string;
  private loadedSkills: Map<string, SkillSheet> = new Map();

  private constructor(skillsDir: string = './skills') {
    this.skillsDir = path.resolve(skillsDir);
  }

  static getInstance(skillsDir?: string): SkillSheetLoader {
    if (!SkillSheetLoader.instance) {
      SkillSheetLoader.instance = new SkillSheetLoader(skillsDir);
    }
    return SkillSheetLoader.instance;
  }

  /**
   * Parse markdown skill sheet
   */
  private parseMarkdownSkill(content: string): SkillSheet {
    const lines = content.split('\n');
    const skill: Partial<SkillSheet> = {};

    let currentSection = '';
    let codeBlock = '';
    let inCodeBlock = false;

    for (const line of lines) {
      if (line.startsWith('```')) {
        if (inCodeBlock) {
          // End of code block
          if (currentSection === 'implementation') {
            skill.implementation = codeBlock.trim();
          }
          inCodeBlock = false;
          codeBlock = '';
        } else {
          // Start of code block
          inCodeBlock = true;
        }
        continue;
      }

      if (inCodeBlock) {
        codeBlock += line + '\n';
        continue;
      }

      // Parse headers
      if (line.startsWith('# ')) {
        skill.skill_name = line.substring(2).trim();
      } else if (line.startsWith('## ')) {
        currentSection = line.substring(3).trim().toLowerCase().replace(/\s+/g, '_');
      } else if (line.includes(':')) {
        const [key, ...valueParts] = line.split(':');
        const value = valueParts.join(':').trim();

        switch (currentSection) {
          case 'metadata':
            this.parseMetadata(skill, key.trim(), value);
            break;
          case 'parameters':
            if (!skill.parameters) skill.parameters = {};
            this.parseParameter(skill.parameters, key.trim(), value);
            break;
          case 'output_format':
            if (!skill.output_format) skill.output_format = {};
            this.parseParameter(skill.output_format, key.trim(), value);
            break;
          case 'examples':
            if (!skill.examples) skill.examples = [];
            this.parseExample(skill.examples, line);
            break;
        }
      }
    }

    return SkillSheetSchema.parse(skill);
  }

  private parseMetadata(skill: Partial<SkillSheet>, key: string, value: string): void {
    switch (key.toLowerCase()) {
      case 'description':
        skill.description = value;
        break;
      case 'category':
        skill.category = value;
        break;
      case 'cost_estimate':
        skill.cost_estimate = parseFloat(value.replace('$', ''));
        break;
      case 'timeout_ms':
        skill.timeout_ms = parseInt(value);
        break;
    }
  }

  private parseParameter(params: Record<string, any>, key: string, value: string): void {
    // Simple type inference from value
    if (value.toLowerCase() === 'string') {
      params[key] = 'string';
    } else if (value.toLowerCase() === 'number') {
      params[key] = 'number';
    } else if (value.toLowerCase() === 'boolean') {
      params[key] = 'boolean';
    } else if (value.includes('array')) {
      params[key] = 'array';
    } else {
      params[key] = value; // Default to string
    }
  }

  private parseExample(examples: any[], line: string): void {
    // Simple example parsing - in practice would be more sophisticated
    if (line.includes('Input:')) {
      examples.push({ input: {}, output: {} });
    }
  }

  /**
   * Load skill from markdown file
   */
  async loadSkillFromFile(filePath: string): Promise<SkillSheet> {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const skill = this.parseMarkdownSkill(content);
      this.loadedSkills.set(skill.skill_name, skill);
      return skill;
    } catch (error) {
      throw new Error(`Failed to load skill from ${filePath}: ${error}`);
    }
  }

  /**
   * Load all skills from directory
   */
  async loadAllSkillsFromDir(): Promise<SkillSheet[]> {
    const skills: SkillSheet[] = [];

    if (!fs.existsSync(this.skillsDir)) {
      console.warn(`Skills directory not found: ${this.skillsDir}`);
      return skills;
    }

    const files = fs.readdirSync(this.skillsDir)
      .filter(file => file.endsWith('.md'))
      .map(file => path.join(this.skillsDir, file));

    for (const file of files) {
      try {
        const skill = await this.loadSkillFromFile(file);
        skills.push(skill);
      } catch (error) {
        console.error(`Failed to load skill from ${file}:`, error);
      }
    }

    return skills;
  }

  /**
   * Convert skill sheet to tool descriptor
   */
  skillToToolDescriptor(skill: SkillSheet): ToolDescriptor {
    // Create Zod schema from parameters
    const paramSchema = this.createZodSchemaFromParams(skill.parameters);

    // Create tool execution function
    const execute = async (params: any): Promise<any> => {
      // This is where we'd execute the skill implementation
      // For now, return a placeholder
      console.log(`Executing skill: ${skill.skill_name}`, params);

      // Mock implementation based on skill category
      switch (skill.category.toLowerCase()) {
        case 'scraping':
          return this.executeScrapingSkill(skill, params);
        case 'enrichment':
          return this.executeEnrichmentSkill(skill, params);
        case 'analysis':
          return this.executeAnalysisSkill(skill, params);
        default:
          return { result: 'Skill executed', params };
      }
    };

    return createTool(
      skill.skill_name.toLowerCase().replace(/\s+/g, '_'),
      skill.description,
      paramSchema,
      execute,
      {
        cost_estimate: skill.cost_estimate,
        timeout: skill.timeout_ms,
        retry_policy: skill.retry_policy
      }
    );
  }

  private createZodSchemaFromParams(params: Record<string, any>): z.ZodSchema {
    const schema: Record<string, z.ZodTypeAny> = {};

    for (const [key, type] of Object.entries(params)) {
      switch (type) {
        case 'string':
          schema[key] = z.string();
          break;
        case 'number':
          schema[key] = z.number();
          break;
        case 'boolean':
          schema[key] = z.boolean();
          break;
        case 'array':
          schema[key] = z.array(z.any());
          break;
        default:
          schema[key] = z.string(); // Default to string
      }
    }

    return z.object(schema);
  }

  // Mock skill implementations (would be replaced with actual integrations)
  private async executeScrapingSkill(skill: SkillSheet, params: any): Promise<any> {
    return {
      skill: skill.skill_name,
      scraped_data: `Mock scraped data for ${params.url || params.query}`,
      timestamp: new Date().toISOString()
    };
  }

  private async executeEnrichmentSkill(skill: SkillSheet, params: any): Promise<any> {
    return {
      skill: skill.skill_name,
      enriched_data: `Mock enriched data for ${params.domain || params.company}`,
      timestamp: new Date().toISOString()
    };
  }

  private async executeAnalysisSkill(skill: SkillSheet, params: any): Promise<any> {
    return {
      skill: skill.skill_name,
      analysis: `Mock analysis result for input data`,
      insights: ['Key insight 1', 'Key insight 2'],
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Register skill as tool
   */
  registerSkillAsTool(skill: SkillSheet): void {
    const toolDescriptor = this.skillToToolDescriptor(skill);
    toolbox.registerTool(toolDescriptor);
    console.log(`✅ Registered skill as tool: ${skill.skill_name}`);
  }

  /**
   * Load and register all skills
   */
  async loadAndRegisterAllSkills(): Promise<number> {
    const skills = await this.loadAllSkillsFromDir();
    let registered = 0;

    for (const skill of skills) {
      try {
        this.registerSkillAsTool(skill);
        registered++;
      } catch (error) {
        console.error(`Failed to register skill ${skill.skill_name}:`, error);
      }
    }

    console.log(`📚 Loaded ${skills.length} skills, registered ${registered} tools`);
    return registered;
  }

  /**
   * Get loaded skill
   */
  getSkill(name: string): SkillSheet | undefined {
    return this.loadedSkills.get(name);
  }

  /**
   * Get all loaded skills
   */
  getAllSkills(): SkillSheet[] {
    return Array.from(this.loadedSkills.values());
  }
}

// =====================================================
// GLOBAL SKILL LOADER INSTANCE
// =====================================================

export const skillLoader = SkillSheetLoader.getInstance('./skills');

// =====================================================
// EXAMPLE SKILL SHEETS
// =====================================================

export const EXAMPLE_SKILL_SHEETS = {
  WEB_SCRAPER: `# Web Scraper
## Metadata
Description: Scrape content from web pages with optional CSS selectors
Category: scraping
Cost Estimate: $0.01
Timeout MS: 30000

## Parameters
url: string
selector: string (optional)
include_text: boolean (default: true)
include_html: boolean (default: false)

## Output Format
content: string
url: string
timestamp: string
status: string

## Implementation
\`\`\`typescript
// Implementation would integrate with Cheerio/Puppeteer
const result = await scrapeWebsite(params);
return result;
\`\`\`

## Examples
### Basic scraping
Input: { "url": "https://example.com", "include_text": true }
Output: { "content": "Page content...", "url": "https://example.com" }
Explanation: Basic content extraction

### Selector-based scraping
Input: { "url": "https://news.com", "selector": ".article-content" }
Output: { "content": "Article text...", "url": "https://news.com" }
Explanation: Extract specific content sections
`,

  COMPANY_ENRICHER: `# Company Enricher
## Metadata
Description: Enrich company data from domain or name
Category: enrichment
Cost Estimate: $0.005
Timeout MS: 10000

## Parameters
domain: string
include_social: boolean (default: false)
include_tech_stack: boolean (default: true)

## Output Format
company_name: string
domain: string
industry: string
description: string
social_links: object (optional)
tech_stack: array (optional)

## Implementation
\`\`\`typescript
// Integration with Clearbit/BuiltWith APIs
const enriched = await enrichCompany(params);
return enriched;
\`\`\`

## Examples
### Basic enrichment
Input: { "domain": "openai.com" }
Output: { "company_name": "OpenAI", "industry": "AI" }
Explanation: Standard company data enrichment
`
};

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

/**
 * Create skills directory and example files
 */
export const initializeSkillsDirectory = (): void => {
  const skillsDir = './skills';

  if (!fs.existsSync(skillsDir)) {
    fs.mkdirSync(skillsDir, { recursive: true });
  }

  // Create example skill sheets
  Object.entries(EXAMPLE_SKILL_SHEETS).forEach(([name, content]) => {
    const filePath = path.join(skillsDir, `${name.toLowerCase()}.md`);
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, content);
      console.log(`📄 Created example skill sheet: ${filePath}`);
    }
  });
};
