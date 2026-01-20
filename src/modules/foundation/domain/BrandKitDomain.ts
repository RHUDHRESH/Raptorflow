export interface BrandVoiceProfile {
  name: string;
  tone: string;
  style_rules: string[];
  vocabulary: string[];
  prohibited_patterns: string[];
  last_updated?: string;
}

export class BrandKitDomain {
  /**
   * Generates the prompt for Gemini to analyze brand voice samples.
   */
  static generateAnalysisPrompt(samples: string[]): string {
    const samplesText = samples.join('\n---\n');
    return `Analyze the following content samples and extract a definitive 'Brand Voice Profile'.

SAMPLES:
${samplesText}

OUTPUT JSON format:
{
  "name": "descriptive name",
  "tone": "primary tone descriptors",
  "style_rules": ["rule 1", "rule 2"],
  "vocabulary": ["word 1", "word 2"],
  "prohibited_patterns": ["don't do X"]
}
`;
  }

  /**
   * Generates the prompt for Gemini to apply brand voice to content.
   */
  static generateApplyPrompt(content: string, profile: BrandVoiceProfile): string {
    return `Rewrite the following content to match this Brand Voice Profile.

PROFILE:
${JSON.stringify(profile, null, 2)}

CONTENT TO REWRITE:
${content}

Ensure the core message and meaning remain unchanged, but the tone and style adhere strictly to the profile.`;
  }
}
