---
id: UnitEconomicsSkill
expert: Sera (Performance Analyst)
category: analytics
level: master
tools:
  - financial_calculator
  - market_benchmark_db
  - revenue_modeler
complexity: high-density
logic_type: analytical_engine
---

# EXPERT SKILL: UNIT ECONOMICS AUDIT PROTOCOL

This is the cold, hard logic engine for auditing the financial viability of any marketing strategy. Designed for the Performance Analyst (Sera) to prevent "Vibe-Based" marketing burn.

## 1. DATA INITIALIZATION
Before execution, Sera must ingest `Revenue_Streams`, `Spend_Forecast`, and `Customer_Data`.
- IF `Data_Quality` < 0.7: Trigger `Benchmark_Interpolation` sequence.
- IF `Data_Quality` >= 0.7: Trigger `Surgical_Audit` sequence.

## 2. PROCEDURAL EXECUTION (200-LINE DENSITY)

### PHASE 1: CAC DECONSTRUCTION (Lines 1-50)
1. Categorize all marketing spend into `Fixed`, `Variable`, and `Auxiliary`.
2. Extract `Direct_CAC`: Sum(Variable_Spend) / New_Customers.
3. Extract `Blended_CAC`: Sum(Total_Spend) / New_Customers.
4. Apply the `Sera_Friction_Coefficient` (1.15x) to account for untracked ad-waste and platform fluctuations.
5. Identify `Channel_Leakage`:
   - Scan for channels where `CAC_Delta` > 20% MoM.
   - IF `Leakage` > threshold: Mark channel as "EXPERIMENTAL" and reduce weighting.
6. Calculate `Organic_Lift_Multiplier`: Total_New / Paid_New.
7. Step 1.1: Audit the `Attribution_Logic`. 
   - IF "Last Click": Apply 15% discount to conversion data.
   - IF "Multi-Touch": Verify weightings against industry SaaS standards.
8. Baseline `Payback_Period` target: < 6 months for Seed, < 12 months for Series A+.

### PHASE 2: LTV PROJECTION (Lines 51-100)
9. Define `ARPU` (Average Revenue Per User) by cohort.
10. Calculate `Churn_Decay_Rate`: 1 - (Retained_Users / Total_Users).
11. Execute `LTV_Surgical_Formula`: (ARPU * Gross_Margin) / Churn.
12. Audit `Gross_Margin` accuracy:
    - Must include: Support costs, server costs, transaction fees.
    - IF `Margin` < 70% (SaaS): Flag as "RISK: UNIT_ECONOMICS".
13. Run `Cohort_Survival_Simulation`:
    - Model user retention over 24 months.
    - Identify the "LTV_Plateau"—where incremental revenue drops below CAC.
14. Adjust LTV for `Expansion_Revenue` potential.
15. Verify `Net_Dollar_Retention` (NDR):
    - Target: > 110% for high-performance marketing approval.

### PHASE 3: THE RATIO COMMAND (Lines 101-150)
16. Calculate `LTV_to_CAC_Ratio`.
    - IF Ratio < 3.0: Output `STRATEGIC_NO_GO`.
    - IF Ratio 3.0 - 5.0: Output `GROWTH_ENABLED`.
    - IF Ratio > 5.0: Output `AGGRESSIVE_SCALE_RECOMMENDED`.
17. Identify `Scale_Diminishing_Returns`:
    - Calculate `Marginal_CAC`: Cost of the *next* customer.
    - IF `Marginal_CAC` > 0.5 * `LTV`: Trigger `Scale_Ceiling_Warning`.
18. Execute `Capital_Efficiency_Audit`:
    - Ratio: (New_ARR) / (S&M_Spend).
    - Target: > 0.8 for "Efficient Growth".
19. Map `Payback_Velocity`:
    - Velocity = 1 / Payback_Period.
    - Higher velocity allows for faster compounding of marketing capital.

### PHASE 4: RISK & SENSITIVITY (Lines 151-200)
20. Run `Monte_Carlo_Sensitivity`:
    - Scenario A: Churn increases by 25%.
    - Scenario B: Platform CPMs increase by 40%.
    - Scenario C: Conversion rate drops by 15%.
21. Identify `Critical_Failure_Point`: The exact metric change that makes the unit economics negative.
22. Define `Mitigation_Triggers`:
    - IF `CAC` > X: Pause automated spend.
    - IF `NDR` < Y: Redirect budget to "Retain" moves.
23. Create the `Economic_Feasibility_Report`:
    - Summary of the math.
    - Hard Go/No-Go verdict.
    - List of 3 "Math-Gaps" to close.
24. FINAL VALIDATION:
    - Is the ROI proven or projected?
    - Is the margin safe?
    - IF NO: Block `Council_Consensus`.
    - IF YES: Forward to `Architect_Review`.

## 3. EDGE CASE LOGIC
- **Scenario: Viral Growth Spikes.**
  - [Logic]: Discount viral users by 50% in LTV models to avoid "Vibe-Inflation".
- **Scenario: Enterprise Sales Cycle (> 6 months).**
  - [Logic]: Shift audit focus from "Payback" to "Pipeline_Velocity" and "MQL_Quality".
- **Scenario: Massive Data Gaps.**
  - [Logic]: Use `Raptorflow_Sector_Benchmarks` based on the company's `Industry` and `Stage`.

## 4. ANALYST'S NOTES (Line 200+)
The math does not have an ego. If the LTV/CAC ratio is broken, no amount of "Great Copy" (Mia) or "Clean Funnels" (Jax) will save the business. My job is to ensure we are building a machine, not a fire.
