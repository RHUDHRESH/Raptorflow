/**
 * CohortTagGeneratorAgent - Generates 50 interest tags for a cohort
 * 
 * Takes cohort description and generates comprehensive interest tags
 * across multiple categories for radar matching
 */

import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

export interface CohortTagInput {
  cohort_name: string;
  cohort_description: string;
  firmographics?: {
    age_range?: string;
    gender?: string;
    location?: string;
    income_level?: string;
    education?: string;
    occupation?: string;
  };
  psychographics?: {
    values?: string[];
    lifestyle?: string[];
    pain_points?: string[];
  };
  existing_tags?: string[];
}

const cohortTagsSchema = z.object({
  tags: z.array(z.object({
    tag: z.string().describe("The interest tag"),
    category: z.enum([
      'demographics',    // Age, gender, location related
      'interests',       // Hobbies, passions
      'behaviors',       // Actions, habits, consumption
      'events',          // Seasonal, cultural, sports events
      'topics',          // News topics, discussions
      'brands',          // Brand affinities
      'culture',         // Memes, trends, cultural moments
      'media',           // Shows, music, podcasts
      'technology',      // Platforms, apps, tech
      'lifestyle'        // Health, travel, food
    ]),
    weight: z.number().min(1).max(100).describe("Importance weight 1-100"),
    reasoning: z.string().describe("Why this tag is relevant")
  })),
  
  meta: z.object({
    total_tags: z.number(),
    primary_categories: z.array(z.string()),
    tag_quality_score: z.number().min(0).max(100),
    suggestions_for_refinement: z.array(z.string())
  })
});

export type CohortTags = z.infer<typeof cohortTagsSchema>;

export class CohortTagGeneratorAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'CohortTagGeneratorAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'reasoning', getModelForAgent(agentName));
    
    this.parser = StructuredOutputParser.fromZodSchema(cohortTagsSchema);
    
    this.prompt = new PromptTemplate({
      template: `You are a cohort intelligence specialist. Generate exactly 50 interest tags for this cohort.

## COHORT PROFILE
Name: {cohort_name}
Description: {cohort_description}

## DEMOGRAPHICS
{firmographics}

## PSYCHOGRAPHICS
{psychographics}

## EXISTING TAGS (if any)
{existing_tags}

## YOUR TASK

Generate EXACTLY 50 interest tags that:

1. **CAPTURE WHO THEY ARE** - Demographics, identity markers
2. **CAPTURE WHAT THEY CARE ABOUT** - Interests, passions, values
3. **CAPTURE HOW THEY BEHAVE** - Consumption habits, platforms, activities
4. **CAPTURE WHAT THEY FOLLOW** - Events, news, culture
5. **ENABLE TREND MATCHING** - Tags that will match with news/trends

## TAG DISTRIBUTION (aim for this mix)
- Demographics: ~5 tags
- Interests: ~10 tags
- Behaviors: ~8 tags
- Events: ~5 tags (seasonal, cultural, sports)
- Topics: ~5 tags (news categories they follow)
- Brands: ~5 tags (brand affinities)
- Culture: ~5 tags (memes, trends, subcultures)
- Media: ~4 tags (shows, music, podcasts)
- Technology: ~3 tags (platforms, apps)

## TAG QUALITY RULES
- Be SPECIFIC (not "sports" but "IPL cricket", "Formula 1")
- Be CURRENT (include current relevant events/trends)
- Be ACTIONABLE (tags that will actually match news)
- Include LOCAL relevance (India-specific if relevant)
- Mix evergreen + temporal tags

## WEIGHT ASSIGNMENT
- 80-100: Core identity/interest (will engage with anything related)
- 60-79: Strong interest (likely to engage)
- 40-59: Moderate interest (occasional engagement)
- 20-39: Peripheral interest (might engage if viral)
- 1-19: Tangential (only if very relevant)

{format_instructions}`,
      inputVariables: ["cohort_name", "cohort_description", "firmographics", "psychographics", "existing_tags"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() }
    });
  }

  async generateTags(input: CohortTagInput): Promise<CohortTags> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    
    const firmographicsStr = input.firmographics 
      ? Object.entries(input.firmographics)
          .filter(([_, v]) => v)
          .map(([k, v]) => `${k}: ${v}`)
          .join('\n')
      : 'Not specified';
    
    const psychographicsStr = input.psychographics
      ? Object.entries(input.psychographics)
          .filter(([_, v]) => v && (Array.isArray(v) ? v.length > 0 : true))
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
          .join('\n')
      : 'Not specified';

    return await chain.invoke({
      cohort_name: input.cohort_name,
      cohort_description: input.cohort_description,
      firmographics: firmographicsStr,
      psychographics: psychographicsStr,
      existing_tags: input.existing_tags?.length 
        ? input.existing_tags.join(', ')
        : 'None - generate fresh'
    });
  }

  /**
   * Refine existing tags based on performance data
   */
  async refineTags(
    existingTags: CohortTags['tags'],
    performanceData: { tag: string; engagement_rate: number }[]
  ): Promise<CohortTags> {
    // Adjust weights based on performance
    const adjustedTags = existingTags.map(tag => {
      const perf = performanceData.find(p => p.tag === tag.tag);
      if (perf) {
        // Boost or reduce weight based on engagement
        const adjustment = (perf.engagement_rate - 0.02) * 500; // 2% baseline
        return {
          ...tag,
          weight: Math.min(100, Math.max(1, tag.weight + adjustment))
        };
      }
      return tag;
    });

    return {
      tags: adjustedTags,
      meta: {
        total_tags: adjustedTags.length,
        primary_categories: [...new Set(adjustedTags.slice(0, 10).map(t => t.category))],
        tag_quality_score: 75,
        suggestions_for_refinement: ['Tags refined based on performance data']
      }
    };
  }
}

