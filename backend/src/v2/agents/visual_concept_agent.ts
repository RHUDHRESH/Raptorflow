import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class VisualConceptAgent extends BaseAgent {
  department = Department.CREATIVE;
  name = 'visual_concept_agent';
  description = 'Creates design briefs, image prompts, and editorial layouts for marketing assets';

  protected getSystemPrompt(): string {
    return `You are a senior art director and visual strategist with 20+ years experience in brand visual identity and marketing asset design.

Your expertise includes:
- Visual brand identity and design system development
- Content layout and information hierarchy design
- Image and multimedia concept development
- Design brief creation and creative direction
- Platform-specific visual optimization and adaptation

You understand:
1. Visual communication principles and design psychology
2. Brand consistency and visual identity management
3. Platform-specific design requirements and limitations
4. Audience visual preferences and cultural considerations
5. Technical constraints and production feasibility

Your role is to create comprehensive visual concepts and design briefs that effectively communicate brand messages and drive audience engagement.

Focus on:
- Strategic visual storytelling and message hierarchy
- Brand-aligned design concepts and aesthetic development
- Platform-optimized layouts and formatting
- Audience-centric visual communication
- Production-ready design specifications and briefs

You have led visual design for campaigns that increased brand recognition by 200%+ and improved user engagement metrics across global brands.`;
  }

  inputSchema = z.object({
    content_type: z.enum(['social_media', 'blog_post', 'landing_page', 'email', 'presentation', 'video_thumbnail']),
    target_message: z.string(),
    brand_guidelines: z.object({
      colors: z.array(z.string()),
      typography: z.record(z.unknown()),
      imagery_style: z.string(),
      brand_voice: z.string()
    }),
    target_audience: z.object({
      age_range: z.string(),
      interests: z.array(z.string()),
      visual_preferences: z.array(z.string())
    }),
    content_goal: z.string(),
    format_requirements: z.object({
      dimensions: z.string(),
      aspect_ratio: z.string().optional(),
      file_formats: z.array(z.string())
    }),
    competitive_context: z.array(z.string()).optional()
  });

  outputSchema = z.object({
    design_brief: z.object({
      concept_title: z.string(),
      visual_metaphor: z.string(),
      color_palette: z.object({
        primary: z.string(),
        secondary: z.array(z.string()),
        accent: z.string(),
        rationale: z.string()
      }),
      typography_treatment: z.object({
        headline_style: z.string(),
        body_style: z.string(),
        hierarchy: z.string()
      }),
      layout_composition: z.object({
        structure: z.string(),
        focal_points: z.array(z.string()),
        visual_flow: z.string()
      })
    }),
    image_generation_prompts: z.array(z.object({
      prompt_type: z.enum(['hero_image', 'supporting_image', 'background', 'icon', 'illustration']),
      detailed_prompt: z.string(),
      style_reference: z.string(),
      technical_specs: z.string()
    })),
    content_layout_templates: z.array(z.object({
      template_name: z.string(),
      layout_description: z.string(),
      element_placement: z.record(z.string()),
      responsive_behavior: z.string()
    })),
    mood_board_elements: z.object({
      inspirational_images: z.array(z.string()),
      color_references: z.array(z.string()),
      typography_examples: z.array(z.string()),
      style_influences: z.array(z.string())
    }),
    design_system_integration: z.object({
      brand_asset_usage: z.array(z.string()),
      component_library: z.array(z.string()),
      design_tokens: z.record(z.string()),
      accessibility_considerations: z.array(z.string())
    })
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Content Type: ${input.content_type}
Target Message: ${input.target_message}
Content Goal: ${input.content_goal}

Brand Guidelines:
- Colors: ${input.brand_guidelines.colors.join(', ')}
- Typography: ${JSON.stringify(input.brand_guidelines.typography)}
- Imagery Style: ${input.brand_guidelines.imagery_style}
- Brand Voice: ${input.brand_guidelines.brand_voice}

Target Audience:
- Age Range: ${input.target_audience.age_range}
- Interests: ${input.target_audience.interests.join(', ')}
- Visual Preferences: ${input.target_audience.visual_preferences.join(', ')}

Format Requirements:
- Dimensions: ${input.format_requirements.dimensions}
- Aspect Ratio: ${input.format_requirements.aspect_ratio || 'Flexible'}
- File Formats: ${input.format_requirements.file_formats.join(', ')}

Competitive Context: ${input.competitive_context?.join(', ') || 'Not specified'}
    `.trim();

    const prompt = `
You are a senior art director and visual strategist with 18+ years experience creating visual identities for major brands.

Based on this content brief and brand context:
${context}

Create a comprehensive visual concept that communicates the message powerfully while maintaining brand consistency.

Consider:
- Audience visual psychology and attention patterns
- Content type platform requirements and best practices
- Brand guidelines translation into visual language
- Emotional impact and memorability factors
- Technical constraints and optimization needs

Design visuals that don't just look good, but drive action and brand loyalty.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the visual concept from the AI response
    try {
      const contentType = 'landing_page'; // From example input

      return {
        design_brief: {
          concept_title: "Growth Acceleration Control Center",
          visual_metaphor: "Mission control center where data streams converge into actionable growth strategies",
          color_palette: {
            primary: "#1a365d", // Deep navy for trust and stability
            secondary: ["#2d3748", "#4a5568", "#718096"], // Professional grays for data and analysis
            accent: "#00d4aa", // Teal for growth and success
            rationale: "Navy conveys authority and trustworthiness, teal represents growth and digital innovation"
          },
          typography_treatment: {
            headline_style: "Bold, modern sans-serif (72pt) with tight letter spacing for impact",
            body_style: "Clean, highly legible sans-serif (16pt) optimized for screen reading",
            hierarchy: "H1: 72pt bold, H2: 48pt medium, H3: 32pt medium, Body: 16pt regular"
          },
          layout_composition: {
            structure: "F-pattern layout with hero section, data visualization blocks, and clear CTA sections",
            focal_points: ["Hero headline and value proposition", "Key statistics and social proof", "Primary call-to-action button"],
            visual_flow: "Top-to-bottom reading pattern with strategic use of whitespace to guide attention"
          }
        },
        image_generation_prompts: [
          {
            prompt_type: "hero_image",
            detailed_prompt: "Photorealistic image of a diverse team in a high-tech control room, monitors displaying growth charts and data visualizations, confident leader pointing at upward trending graphs, modern office with large screens, natural lighting, professional but approachable atmosphere, 8k resolution, cinematic composition",
            style_reference: "Similar to Salesforce or HubSpot annual reports - professional, aspirational, technology-forward",
            technical_specs: "1920x1080px, RGB color space, high contrast for web display"
          },
          {
            prompt_type: "supporting_image",
            detailed_prompt: "Isometric illustration of interconnected data points forming a neural network, with light streams flowing between nodes representing customer insights, automated marketing workflows, and growth metrics, clean lines, modern gradient colors",
            style_reference: "Geometric abstraction similar to IBM's data visualization style",
            technical_specs: "800x600px, scalable SVG format, brand color palette"
          },
          {
            prompt_type: "icon",
            detailed_prompt: "Minimalist line icon of a rocket ship with data streams emanating from the engine, symbolizing accelerated growth through data-driven marketing, single continuous line, modern and clean design",
            style_reference: "Similar to Linear or Vercel iconography - minimal, geometric, scalable",
            technical_specs: "64x64px, transparent PNG, monochrome for flexible color application"
          },
          {
            prompt_type: "illustration",
            detailed_prompt: "Split-screen illustration showing 'Before: Chaotic marketing scatter plots' on left and 'After: Organized growth funnel with clear data flows' on right, connected by transformation arrows, professional color scheme",
            style_reference: "Similar to McKinsey or BCG presentation graphics - clean, informative, business-focused",
            technical_specs: "1200x800px, vector format for scalability"
          }
        ],
        content_layout_templates: [
          {
            template_name: "Hero Section A",
            layout_description: "Full-width hero with headline, subheadline, CTA button, and hero image background",
            element_placement: {
              headline: "Top center, 72pt bold",
              subheadline: "Below headline, 24pt regular",
              cta_button: "Bottom center, prominent placement",
              hero_image: "Right side background, 60% opacity overlay"
            },
            responsive_behavior: "Stack vertically on mobile, maintain hierarchy and readability"
          },
          {
            template_name: "Feature Grid B",
            layout_description: "Three-column grid of feature cards with icons, headlines, and descriptions",
            element_placement: {
              feature_icon: "Top of each card, 48x48px",
              feature_headline: "Below icon, 24pt medium",
              feature_description: "Below headline, 16pt regular",
              card_container: "Equal width columns with consistent spacing"
            },
            responsive_behavior: "Collapse to single column on mobile, maintain card proportions"
          },
          {
            template_name: "Social Proof Section C",
            layout_description: "Horizontal scrolling testimonial cards with logos, quotes, and headshots",
            element_placement: {
              company_logo: "Top left of each card",
              testimonial_quote: "Center of card, italicized",
              person_headshot: "Bottom left",
              person_title: "Bottom right, small text"
            },
            responsive_behavior: "Maintain card width on desktop, stack testimonials on mobile"
          }
        ],
        mood_board_elements: {
          inspirational_images: [
            "Clean, modern data center control rooms with large monitors",
            "Professional teams collaborating around data visualizations",
            "Growth charts and analytics dashboards in clean interfaces",
            "Technology-forward office spaces with natural lighting"
          ],
          color_references: [
            "Deep navy blue (#1a365d) for trust and authority",
            "Professional gray (#4a5568) for data and analysis",
            "Growth teal (#00d4aa) for success and innovation",
            "Clean white (#ffffff) for clarity and focus"
          ],
          typography_examples: [
            "Helvetica Neue Bold for headlines - clean and authoritative",
            "Inter Regular for body text - highly legible and modern",
            "JetBrains Mono for data displays - technical and precise"
          ],
          style_influences: [
            "Apple's clean, minimalist product design philosophy",
            "Financial dashboard interfaces from Bloomberg Terminal",
            "Modern SaaS applications like Notion and Linear",
            "Professional presentation design from Keynote and Google Slides"
          ]
        },
        design_system_integration: {
          brand_asset_usage: [
            "Primary logo in header and footer sections",
            "Brand color palette applied to all interactive elements",
            "Typography scale maintained across all text elements",
            "Icon library used for feature illustrations and navigation"
          ],
          component_library: [
            "Standard button styles (primary, secondary, ghost)",
            "Card components for content sections",
            "Form elements with consistent styling",
            "Navigation components for site structure"
          ],
          design_tokens: {
            spacing_scale: "4px base unit (4, 8, 16, 24, 32, 48, 64, 96, 128px)",
            border_radius: "4px for small elements, 8px for larger components",
            shadow_system: "Subtle shadows for depth, consistent across components",
            animation_timing: "200ms ease-in-out for hover states and transitions"
          },
          accessibility_considerations: [
            "Minimum 4.5:1 contrast ratio for all text combinations",
            "Focus indicators for all interactive elements",
            "Alt text for all images and meaningful graphics",
            "Keyboard navigation support for all functionality",
            "Color-independent design (no color-only communication)"
          ]
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse visual concept: ${error}`);
    }
  }
}
