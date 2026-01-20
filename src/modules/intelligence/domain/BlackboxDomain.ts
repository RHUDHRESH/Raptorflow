import { BlackboxStrategyRequest } from '../types';

export class BlackboxDomain {
  /**
   * Generates a prompt for the Volatility Engine based on risk tolerance.
   */
  static generateStrategyPrompt(request: BlackboxStrategyRequest): string {
    const riskLabel = request.risk_tolerance > 0.7 ? 'Aggressive/Bold' : request.risk_tolerance < 0.3 ? 'Conservative/Safe' : 'Balanced';
    
    return `Generate a ${riskLabel} strategic plan for the following objective.
Objective: ${request.objective}
Risk Tolerance: ${request.risk_tolerance}

Structure your response to include:
1. Rationale
2. Risk Assessment
3. Actionable Moves (Title, Description, Impact, Effort)`;
  }

  /**
   * Validates if a strategy is bold enough for high risk tolerance.
   */
  static isStrategyBoldEnough(moves: any[], risk_tolerance: number): boolean {
    if (risk_tolerance > 0.8) {
      const highImpactMoves = moves.filter(m => m.impact === 'high');
      return highImpactMoves.length >= 2;
    }
    return true;
  }
}
