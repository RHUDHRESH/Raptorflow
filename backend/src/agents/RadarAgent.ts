/**
 * RadarAgent - Trend Detection & Opportunity Matching
 * 
 * Scans news, social media, and web for trending topics
 * that match cohort interest tags, then suggests timely content
 */

import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Interest tag schema
export interface CohortInterestTag {
  tag: string;
  category: 'demographics' | 'interests' | 'behaviors' | 'events' | 'topics' | 'brands' | 'culture';
  weight: number; // 0-100 importance
}

// Radar input
export interface RadarInput {
  cohort_id: string;
  cohort_name: string;
  cohort_description: string;
  interest_tags: CohortInterestTag[];
  recent_news?: string[]; // Optional pre-fetched news
  timeframe?: 'today' | 'this_week' | 'this_month';
}

// Opportunity output schema
const radarOpportunitySchema = z.object({
  opportunities: z.array(z.object({
    id: z.string(),
    title: z.string().describe("Catchy title for the opportunity"),
    trend_type: z.enum(['breaking_news', 'viral_moment', 'cultural_event', 'controversy', 'seasonal', 'meme', 'industry_news']),
    description: z.string().describe("What's happening and why it matters"),
    relevance_score: z.number().min(0).max(100).describe("How relevant to the cohort (0-100)"),
    urgency: z.enum(['post_now', 'within_hours', 'within_day', 'this_week']),
    matching_tags: z.array(z.string()).describe("Which cohort tags this matches"),
    
    // Content suggestions
    content_angles: z.array(z.object({
      angle: z.string(),
      hook: z.string(),
      format: z.enum(['image_post', 'video', 'carousel', 'story', 'reel', 'thread', 'blog', 'email']),
      platforms: z.array(z.string()),
      estimated_engagement: z.enum(['low', 'medium', 'high', 'viral_potential'])
    })),
    
    // Risk assessment
    risk_level: z.enum(['safe', 'moderate', 'sensitive', 'avoid']),
    risk_notes: z.string().nullable(),
    
    // Sources
    sources: z.array(z.object({
      title: z.string(),
      url: z.string(),
      source_type: z.enum(['news', 'social', 'reddit', 'twitter', 'google_trends'])
    })),
    
    // Timing
    peak_window: z.string().describe("Best time window to post"),
    decay_estimate: z.string().describe("How long this trend will stay relevant")
  })),
  
  // Overall radar summary
  radar_summary: z.object({
    total_opportunities: z.number(),
    high_urgency_count: z.number(),
    top_categories: z.array(z.string()),
    recommended_action: z.string()
  })
});

export type RadarOutput = z.infer<typeof radarOpportunitySchema>;

export class RadarAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'RadarAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'reasoning', getModelForAgent(agentName));
    
    this.parser = StructuredOutputParser.fromZodSchema(radarOpportunitySchema);
    
    this.prompt = new PromptTemplate({
      template: `You are a Trend Radar AI - a real-time marketing opportunity detector.

Your job is to analyze current news, trends, and events to find marketing opportunities that perfectly match a specific cohort's interests.

## COHORT PROFILE
Name: {cohort_name}
Description: {cohort_description}

## INTEREST TAGS (50 tags defining this cohort's interests)
{interest_tags}

## RECENT NEWS & TRENDS
{recent_news}

## TIMEFRAME
Looking for opportunities: {timeframe}

## YOUR TASK

1. **SCAN** - Analyze the news/trends for anything relevant to this cohort
2. **MATCH** - Find connections between trending topics and the cohort's interest tags
3. **SCORE** - Rate relevance and urgency (breaking news > cultural moment > seasonal)
4. **SUGGEST** - Create specific content angles with hooks, formats, and platforms
5. **ASSESS RISK** - Flag anything sensitive (controversies, tragedies, polarizing topics)

## MATCHING RULES
- Direct tag match (e.g., "World Cup" news + "sports" tag) = High relevance
- Adjacent match (e.g., "celebrity" news + "entertainment" tag) = Medium relevance  
- Demographic relevance (e.g., "college" news + "19-21 year old students") = High relevance
- Cultural moment (e.g., "meme trending" + "gen-z humor" tag) = High relevance

## CONTENT ANGLE REQUIREMENTS
For each opportunity, provide:
- A specific hook/opening line
- The best format (image, video, carousel, etc.)
- Which platforms work best
- Estimated engagement level

## URGENCY LEVELS
- post_now: Breaking news, viral moments (hours matter)
- within_hours: Trending topics at peak
- within_day: Growing trends
- this_week: Seasonal or ongoing events

Be creative but practical. Suggest content that a marketing team could actually create quickly.

{format_instructions}`,
      inputVariables: ["cohort_name", "cohort_description", "interest_tags", "recent_news", "timeframe"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() }
    });
  }

  async scan(input: RadarInput): Promise<RadarOutput> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    
    // Format interest tags for prompt
    const tagsFormatted = input.interest_tags
      .sort((a, b) => b.weight - a.weight)
      .map(t => `- ${t.tag} (${t.category}, weight: ${t.weight})`)
      .join('\n');
    
    // Format news
    const newsFormatted = input.recent_news?.length 
      ? input.recent_news.join('\n- ')
      : 'No specific news provided - use your knowledge of current events and trends';

    return await chain.invoke({
      cohort_name: input.cohort_name,
      cohort_description: input.cohort_description,
      interest_tags: tagsFormatted,
      recent_news: newsFormatted,
      timeframe: input.timeframe || 'this_week'
    });
  }
}

// Add to agent task types
export const RADAR_AGENT_CONFIG = {
  name: 'RadarAgent',
  taskType: 'reasoning' as const,
  description: 'Scans trends and news to find marketing opportunities for cohorts'
};

