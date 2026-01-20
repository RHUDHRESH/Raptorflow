import { TitanMode } from '../types';

export class TitanDomain {
  /**
   * Determines the depth and parallelization settings based on the research mode.
   */
  static getResearchSettings(mode: TitanMode) {
    switch (mode) {
      case TitanMode.DEEP:
        return { parallel_scrapers: 10, recursion_depth: 3, include_reddit: true };
      case TitanMode.RESEARCH:
        return { parallel_scrapers: 5, recursion_depth: 1, include_reddit: true };
      case TitanMode.LITE:
      default:
        return { parallel_scrapers: 2, recursion_depth: 0, include_reddit: false };
    }
  }

  /**
   * Generates the search multiplexing prompt.
   */
  static generateMultiplexPrompt(topic: string): string {
    return `Generate 5 search query variations for the following topic to maximize information coverage.
Topic: ${topic}
Format: Return as a simple JSON list of strings.`;
  }
}
