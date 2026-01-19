---
id: CACProjectionSkill
expert: Sera (Performance Analyst)
category: analytics
level: master
tools:
  - cac_forecaster
  - channel_mapper
  - platform_api_scanner
complexity: high-density
logic_type: predictive_modeling
---

# EXPERT SKILL: CAC PROJECTION & CHANNEL FORECASTING

This is the predictive logic engine for forecasting Customer Acquisition Costs (CAC) across multiple digital and offline channels. Designed for the Performance Analyst (Sera) to ensure that scaling doesn't lead to financial bankruptcy.

## 1. PREDICTIVE INITIALIZATION
Before execution, Sera must ingest `Historical_Ad_Data`, `Platform_CPMs`, and `Conversion_Rates`.
- IF `History` < 30 days: Trigger `Benchmark_Bootstrap` protocol.
- IF `History` >= 30 days: Trigger `Time-Series_Extrapolation` protocol.

## 2. PROCEDURAL EXECUTION (200-LINE DENSITY)

### PHASE 1: PLATFORM DYNAMICS AUDIT (Lines 1-50)
1. Execute `CPM_Volatility_Scan` for the top 4 channels:
   - Channel 1: LinkedIn (B2B Authority)
   - Channel 2: Meta (Scale & Retargeting)
   - Channel 3: Google Search (High Intent)
   - Channel 4: X (Real-time Viral)
2. Extract current `Cost_per_Mille` (CPM) trends for the `Industry` segment.
3. Apply the `Market_Saturation_Coefficient`:
   - IF `Market_Cap` is high: Increase CPM forecast by 12% annually.
   - IF `Market_Cap` is low: Project stability.
4. Calculate `CTR_Decay_Forecasting`:
   - Logic: As frequency increases, Click-Through Rate (CTR) typically drops.
   - Formula: CTR_Target * (1 - (Frequency / Max_Frequency_Threshold)).
5. Identify `Ad_Auction_Pressure`:
   - Scan for seasonality spikes (Q4 Black Friday, B2B Fiscal Year End).
   - [Logic]: Inject +25% CAC padding for known high-pressure windows.

### PHASE 2: CONVERSION PIPELINE MODELING (Lines 51-100)
6. Define the `Funnel_Efficiency_Ratio`:
   - Step 1: Click-to-Lead (CTL) %.
   - Step 2: Lead-to-MQL (LTM) %.
   - Step 3: MQL-to-SQL (MTS) %.
   - Step 4: SQL-to-Closed (STC) %.
7. Run `Dynamic_CAC_Chain_Calculation`:
   - Formula: (CPM / 1000) / (CTR * CTL * LTM * MTS * STC).
8. Audit `Creative_Fatigue_Rate`:
   - How long until the `Cost_per_Conversion` doubles?
   - [Logic]: Force a 20% "Creative Refresment" budget into the forecast.
9. Execute `Lead_Quality_Filtering`:
   - IF `MTS_Ratio` < 30%: MARK channel as "LOW_QUALITY_VOLUME".
   - Logic: A low lead-cost is a trap if they don't convert to SQLs.
10. Map `Channel_Interdependency`:
    - Calculate the `Assisted_Conversion_Multiplier`. 
    - (How much does LinkedIn awareness lower the search-CAC?)

### PHASE 3: SCALING SCENARIO SIMULATIONS (Lines 101-150)
11. Execute `Linear_vs_Logarithmic_Scaling_Models`:
    - Scenario A: **The Efficient Path** (Spend $5k/mo).
    - Scenario B: **The Growth Path** (Spend $25k/mo).
    - Scenario C: **The Blitz Path** (Spend $100k/mo).
12. Identify the `CAC_Ceiling`:
    - The point where spend increases but SQL volume plateaus.
    - [Algorithm]: Search for the inflection point where marginal CAC > LTV / 2.
13. Model `Unit_Economic_Breakeven`:
    - At each spend level, how many months until CAC is repaid?
    - Cross-reference with `UnitEconomicsSkill` from the `Analyst` registry.
14. Run `Platform_Risk_Analysis`:
    - What happens if a platform bans the account or changes its algorithm?
    - [Logic]: Mandate a "Channel Diversification Score" > 0.6.

### PHASE 4: THE SURGICAL BUDGET ALLOCATION (Lines 151-200)
15. Execute `Portfolio_Optimization_Logic`:
    - Use "Modern Portfolio Theory" applied to marketing spend.
    - Maximize Expected Return for a given level of "Channel Risk."
16. Create the `CAC_Projection_Master_Table`:
    - Column 1: Channel Name.
    - Column 2: Current CAC.
    - Column 3: Forecasted CAC (+6 months).
    - Column 4: Max Spend Capacity.
    - Column 5: Confidence Interval (0-1).
17. Develop `Mitigation_Tactics` for Rising CAC:
    - Logic: IF CAC > Target: Trigger `Content_Efficiency_Loop` (Mia).
    - Logic: IF CAC > Target: Trigger `Funnel_Optimization_Audit` (Jax).
18. FINAL ANALYTICAL SIGN-OFF:
    - Is the budget allocation optimized for ROI?
    - Is the scale-ceiling identified?
    - IF NO: Re-trigger `Phase 3`.
    - IF YES: Commit to `The Matrix` state.

## 3. EDGE CASE LOGIC
- **Scenario: New Platform (e.g., Threads, TikTok).**
  - [Logic]: Use `Analogous_Platform_Benchmarks` with a 40% "Uncertainty Buffer."
- **Scenario: Dramatic Product Pivot.**
  - [Logic]: Reset all history weightings to 0.2 and rely on `Expert_Intuition` overrides.
- **Scenario: Global Economic Recession.**
  - [Logic]: Increase `Conversion_Friction_Coefficient` by 1.5x for all high-ticket B2B.

## 4. ANALYST'S NOTES (Line 200+)
Scale is not a linear function. Most founders fail because they assume if they spend 10x, they get 10x results. I am here to show them the math of gravity. We scale only when the floor is reinforced.
