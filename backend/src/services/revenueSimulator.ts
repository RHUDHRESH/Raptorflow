/**
 * Revenue Simulator Service
 * Models pipeline uplift, ARR projections, and scenario planning
 */

import type { ICP, Campaign, Spike, GoalType } from '../types';

// =====================================================
// TYPES
// =====================================================

export interface FunnelMetrics {
  monthly_traffic: number;
  traffic_to_lead_rate: number;  // percentage
  lead_to_opp_rate: number;      // percentage
  opp_to_close_rate: number;     // percentage
  avg_deal_value: number;        // currency
  sales_cycle_days: number;
}

export interface SimulationInput {
  current_metrics: FunnelMetrics;
  campaign_budget?: number;
  time_horizon_months?: number;
  goal?: GoalType;
  improvements?: {
    traffic_lift?: number;       // percentage
    conversion_lift?: number;    // percentage
    deal_value_lift?: number;    // percentage
    cycle_reduction?: number;    // percentage
  };
}

export interface SimulationOutput {
  current_state: {
    monthly_leads: number;
    monthly_opps: number;
    monthly_deals: number;
    monthly_arr: number;
    quarterly_pipeline: number;
  };
  projected_state: {
    monthly_leads: number;
    monthly_opps: number;
    monthly_deals: number;
    monthly_arr: number;
    quarterly_pipeline: number;
  };
  improvement: {
    additional_leads: number;
    additional_opps: number;
    additional_deals: number;
    additional_arr: number;
    additional_pipeline: number;
    percentage_lift: number;
  };
  unit_economics: {
    current_cac: number;
    projected_cac: number;
    current_payback_months: number;
    projected_payback_months: number;
    roi_percentage: number;
  };
  confidence_bands: {
    conservative: SimulationOutput['projected_state'];
    moderate: SimulationOutput['projected_state'];
    aggressive: SimulationOutput['projected_state'];
  };
  timeline: Array<{
    month: number;
    pipeline: number;
    arr: number;
    cumulative_arr: number;
  }>;
}

// =====================================================
// BENCHMARK DATA
// =====================================================

const INDUSTRY_BENCHMARKS: Record<string, Partial<FunnelMetrics>> = {
  'saas_b2b': {
    traffic_to_lead_rate: 3,
    lead_to_opp_rate: 15,
    opp_to_close_rate: 25,
    sales_cycle_days: 45
  },
  'saas_smb': {
    traffic_to_lead_rate: 5,
    lead_to_opp_rate: 20,
    opp_to_close_rate: 30,
    sales_cycle_days: 21
  },
  'enterprise': {
    traffic_to_lead_rate: 2,
    lead_to_opp_rate: 10,
    opp_to_close_rate: 20,
    sales_cycle_days: 90
  }
};

const PROTOCOL_LIFT_ESTIMATES: Record<string, {
  traffic_lift: number;
  conversion_lift: number;
  deal_value_lift: number;
  cycle_reduction: number;
}> = {
  'A_AUTHORITY_BLITZ': { traffic_lift: 30, conversion_lift: 5, deal_value_lift: 0, cycle_reduction: 0 },
  'B_TRUST_ANCHOR': { traffic_lift: 0, conversion_lift: 25, deal_value_lift: 10, cycle_reduction: 10 },
  'C_COST_OF_INACTION': { traffic_lift: 0, conversion_lift: 15, deal_value_lift: 5, cycle_reduction: 20 },
  'D_HABIT_HARDCODE': { traffic_lift: 0, conversion_lift: 30, deal_value_lift: 0, cycle_reduction: 0 },
  'E_ENTERPRISE_WEDGE': { traffic_lift: 0, conversion_lift: 10, deal_value_lift: 40, cycle_reduction: 0 },
  'F_CHURN_INTERCEPT': { traffic_lift: 0, conversion_lift: 0, deal_value_lift: 15, cycle_reduction: 0 }
};

// =====================================================
// REVENUE SIMULATOR CLASS
// =====================================================

export class RevenueSimulator {
  /**
   * Run a full simulation
   */
  simulate(input: SimulationInput): SimulationOutput {
    const {
      current_metrics,
      campaign_budget = 0,
      time_horizon_months = 3,
      improvements = {}
    } = input;
    
    // Calculate current state
    const current = this.calculateFunnelOutput(current_metrics);
    
    // Apply improvements
    const improvedMetrics = this.applyImprovements(current_metrics, improvements);
    const projected = this.calculateFunnelOutput(improvedMetrics);
    
    // Calculate improvement delta
    const improvement = {
      additional_leads: projected.monthly_leads - current.monthly_leads,
      additional_opps: projected.monthly_opps - current.monthly_opps,
      additional_deals: projected.monthly_deals - current.monthly_deals,
      additional_arr: projected.monthly_arr - current.monthly_arr,
      additional_pipeline: projected.quarterly_pipeline - current.quarterly_pipeline,
      percentage_lift: current.monthly_arr > 0 
        ? ((projected.monthly_arr - current.monthly_arr) / current.monthly_arr) * 100 
        : 0
    };
    
    // Calculate unit economics
    const unitEconomics = this.calculateUnitEconomics(
      current,
      projected,
      campaign_budget,
      time_horizon_months
    );
    
    // Generate confidence bands
    const confidenceBands = this.generateConfidenceBands(projected, improvements);
    
    // Generate timeline
    const timeline = this.generateTimeline(
      current,
      projected,
      time_horizon_months
    );
    
    return {
      current_state: current,
      projected_state: projected,
      improvement,
      unit_economics: unitEconomics,
      confidence_bands: confidenceBands,
      timeline
    };
  }

  /**
   * Calculate funnel output from metrics
   */
  private calculateFunnelOutput(metrics: FunnelMetrics): SimulationOutput['current_state'] {
    const monthly_leads = metrics.monthly_traffic * (metrics.traffic_to_lead_rate / 100);
    const monthly_opps = monthly_leads * (metrics.lead_to_opp_rate / 100);
    const monthly_deals = monthly_opps * (metrics.opp_to_close_rate / 100);
    const monthly_arr = monthly_deals * metrics.avg_deal_value * 12; // Annualized
    const quarterly_pipeline = monthly_opps * 3 * metrics.avg_deal_value;
    
    return {
      monthly_leads: Math.round(monthly_leads),
      monthly_opps: Math.round(monthly_opps),
      monthly_deals: Math.round(monthly_deals * 10) / 10,
      monthly_arr: Math.round(monthly_arr),
      quarterly_pipeline: Math.round(quarterly_pipeline)
    };
  }

  /**
   * Apply improvements to metrics
   */
  private applyImprovements(
    metrics: FunnelMetrics,
    improvements: SimulationInput['improvements']
  ): FunnelMetrics {
    return {
      ...metrics,
      monthly_traffic: metrics.monthly_traffic * (1 + (improvements?.traffic_lift || 0) / 100),
      traffic_to_lead_rate: Math.min(
        metrics.traffic_to_lead_rate * (1 + (improvements?.conversion_lift || 0) / 100),
        15 // Cap at 15% traffic to lead
      ),
      lead_to_opp_rate: Math.min(
        metrics.lead_to_opp_rate * (1 + (improvements?.conversion_lift || 0) / 100),
        40 // Cap at 40% lead to opp
      ),
      opp_to_close_rate: Math.min(
        metrics.opp_to_close_rate * (1 + (improvements?.conversion_lift || 0) / 100),
        50 // Cap at 50% close rate
      ),
      avg_deal_value: metrics.avg_deal_value * (1 + (improvements?.deal_value_lift || 0) / 100),
      sales_cycle_days: Math.max(
        metrics.sales_cycle_days * (1 - (improvements?.cycle_reduction || 0) / 100),
        14 // Minimum 2 weeks
      )
    };
  }

  /**
   * Calculate unit economics
   */
  private calculateUnitEconomics(
    current: SimulationOutput['current_state'],
    projected: SimulationOutput['projected_state'],
    budget: number,
    months: number
  ): SimulationOutput['unit_economics'] {
    const totalBudget = budget * months;
    const additionalDeals = (projected.monthly_deals - current.monthly_deals) * months;
    const additionalArr = (projected.monthly_arr - current.monthly_arr) * months;
    
    const currentCac = current.monthly_deals > 0 
      ? budget / current.monthly_deals 
      : 0;
    
    const projectedCac = projected.monthly_deals > 0 
      ? budget / projected.monthly_deals 
      : 0;
    
    const mrr = projected.monthly_arr / 12;
    const currentPayback = currentCac > 0 && current.monthly_arr > 0
      ? currentCac / (current.monthly_arr / 12)
      : 0;
    
    const projectedPayback = projectedCac > 0 && mrr > 0
      ? projectedCac / mrr
      : 0;
    
    const roi = totalBudget > 0 
      ? ((additionalArr - totalBudget) / totalBudget) * 100 
      : 0;
    
    return {
      current_cac: Math.round(currentCac),
      projected_cac: Math.round(projectedCac),
      current_payback_months: Math.round(currentPayback * 10) / 10,
      projected_payback_months: Math.round(projectedPayback * 10) / 10,
      roi_percentage: Math.round(roi)
    };
  }

  /**
   * Generate confidence bands
   */
  private generateConfidenceBands(
    projected: SimulationOutput['projected_state'],
    improvements: SimulationInput['improvements']
  ): SimulationOutput['confidence_bands'] {
    // Conservative: 60% of projected improvement
    const conservative = {
      monthly_leads: Math.round(projected.monthly_leads * 0.6),
      monthly_opps: Math.round(projected.monthly_opps * 0.6),
      monthly_deals: Math.round(projected.monthly_deals * 0.6 * 10) / 10,
      monthly_arr: Math.round(projected.monthly_arr * 0.6),
      quarterly_pipeline: Math.round(projected.quarterly_pipeline * 0.6)
    };
    
    // Moderate: 85% of projected (baseline)
    const moderate = {
      monthly_leads: Math.round(projected.monthly_leads * 0.85),
      monthly_opps: Math.round(projected.monthly_opps * 0.85),
      monthly_deals: Math.round(projected.monthly_deals * 0.85 * 10) / 10,
      monthly_arr: Math.round(projected.monthly_arr * 0.85),
      quarterly_pipeline: Math.round(projected.quarterly_pipeline * 0.85)
    };
    
    // Aggressive: 120% of projected (if everything works)
    const aggressive = {
      monthly_leads: Math.round(projected.monthly_leads * 1.2),
      monthly_opps: Math.round(projected.monthly_opps * 1.2),
      monthly_deals: Math.round(projected.monthly_deals * 1.2 * 10) / 10,
      monthly_arr: Math.round(projected.monthly_arr * 1.2),
      quarterly_pipeline: Math.round(projected.quarterly_pipeline * 1.2)
    };
    
    return { conservative, moderate, aggressive };
  }

  /**
   * Generate monthly timeline
   */
  private generateTimeline(
    current: SimulationOutput['current_state'],
    projected: SimulationOutput['projected_state'],
    months: number
  ): SimulationOutput['timeline'] {
    const timeline = [];
    let cumulativeArr = 0;
    
    // Ramp up improvement over time (not immediate)
    for (let month = 1; month <= months; month++) {
      const rampFactor = Math.min(month / 2, 1); // Full effect by month 2
      
      const monthlyImprovement = (projected.monthly_arr - current.monthly_arr) * rampFactor;
      const arr = current.monthly_arr + monthlyImprovement;
      cumulativeArr += arr;
      
      const pipeline = current.quarterly_pipeline + 
        (projected.quarterly_pipeline - current.quarterly_pipeline) * rampFactor;
      
      timeline.push({
        month,
        pipeline: Math.round(pipeline / 3), // Monthly slice of quarterly pipeline
        arr: Math.round(arr),
        cumulative_arr: Math.round(cumulativeArr)
      });
    }
    
    return timeline;
  }

  /**
   * Get improvement estimates for protocols
   */
  getProtocolImprovementEstimates(protocols: string[]): SimulationInput['improvements'] {
    let totalImprovements = {
      traffic_lift: 0,
      conversion_lift: 0,
      deal_value_lift: 0,
      cycle_reduction: 0
    };
    
    for (const protocol of protocols) {
      const estimates = PROTOCOL_LIFT_ESTIMATES[protocol];
      if (estimates) {
        // Diminishing returns - don't just add up
        totalImprovements.traffic_lift = Math.min(
          totalImprovements.traffic_lift + estimates.traffic_lift * 0.7,
          50
        );
        totalImprovements.conversion_lift = Math.min(
          totalImprovements.conversion_lift + estimates.conversion_lift * 0.7,
          40
        );
        totalImprovements.deal_value_lift = Math.min(
          totalImprovements.deal_value_lift + estimates.deal_value_lift * 0.7,
          50
        );
        totalImprovements.cycle_reduction = Math.min(
          totalImprovements.cycle_reduction + estimates.cycle_reduction * 0.7,
          30
        );
      }
    }
    
    return totalImprovements;
  }

  /**
   * Run simulation for a spike
   */
  simulateSpike(
    currentMetrics: FunnelMetrics,
    spike: { protocols: string[]; targets: any; budget?: number },
    months: number = 3
  ): SimulationOutput {
    const improvements = this.getProtocolImprovementEstimates(spike.protocols);
    
    return this.simulate({
      current_metrics: currentMetrics,
      campaign_budget: spike.budget || 0,
      time_horizon_months: months,
      improvements
    });
  }

  /**
   * Compare multiple scenarios
   */
  compareScenarios(
    currentMetrics: FunnelMetrics,
    scenarios: Array<{
      name: string;
      improvements: SimulationInput['improvements'];
      budget: number;
    }>
  ): Array<{
    name: string;
    simulation: SimulationOutput;
    rank: number;
  }> {
    const results = scenarios.map(scenario => ({
      name: scenario.name,
      simulation: this.simulate({
        current_metrics: currentMetrics,
        campaign_budget: scenario.budget,
        improvements: scenario.improvements
      })
    }));
    
    // Rank by ROI
    results.sort((a, b) => 
      b.simulation.unit_economics.roi_percentage - 
      a.simulation.unit_economics.roi_percentage
    );
    
    return results.map((r, i) => ({ ...r, rank: i + 1 }));
  }

  /**
   * Get industry benchmark metrics
   */
  getIndustryBenchmarks(industry: string = 'saas_b2b'): Partial<FunnelMetrics> {
    return INDUSTRY_BENCHMARKS[industry] || INDUSTRY_BENCHMARKS['saas_b2b'];
  }
}

export const revenueSimulator = new RevenueSimulator();

