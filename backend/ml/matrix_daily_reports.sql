-- RaptorFlow Daily Matrix Analytical Reports
-- These queries are designed to run as BigQuery Scheduled Queries

-- 1. Daily Token Burn and Cost Analysis
-- Destination Table: raptorflow_analytics.daily_cost_report
-- Schedule: Daily at 00:00 UTC
SELECT
  CAST(timestamp AS DATE) AS report_date,
  agent_id,
  SUM(tokens) AS total_tokens,
  -- Assuming $0.015 per 1k tokens as a weighted average for Gemini 1.5 Pro/Flash
  ROUND(SUM(tokens) * 0.000015, 4) AS estimated_cost_usd,
  COUNT(*) AS invocation_count
FROM
  `raptorflow-481505.raptorflow_analytics.telemetry_stream`
WHERE
  timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
GROUP BY
  1, 2
ORDER BY
  estimated_cost_usd DESC;

-- 2. Agent Performance & Latency Matrix
-- Destination Table: raptorflow_analytics.daily_performance_matrix
-- Schedule: Daily at 00:00 UTC
SELECT
  CAST(timestamp AS DATE) AS report_date,
  agent_id,
  ROUND(AVG(latency), 2) AS avg_latency_ms,
  ROUND(APPROX_QUANTILES(latency, 100)[OFFSET(95)], 2) AS p95_latency_ms,
  COUNT(*) AS total_calls
FROM
  `raptorflow-481505.raptorflow_analytics.telemetry_stream`
WHERE
  timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
GROUP BY
  1, 2;

-- 3. Campaign ROI Attribution
-- Destination Table: raptorflow_analytics.daily_campaign_roi
-- Schedule: Daily at 00:00 UTC
SELECT
  CAST(o.timestamp AS DATE) AS report_date,
  o.campaign_id,
  SUM(o.value) AS total_outcome_value,
  -- Join with telemetry to get cost (aggregated by move_id)
  (
    SELECT SUM(tokens) * 0.000015 
    FROM `raptorflow-481505.raptorflow_analytics.telemetry_stream` t 
    WHERE t.move_id IN (SELECT move_id FROM `raptorflow-481505.raptorflow_analytics.outcomes_stream` WHERE campaign_id = o.campaign_id)
  ) AS total_cost_usd
FROM
  `raptorflow-481505.raptorflow_analytics.outcomes_stream` o
WHERE
  o.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
GROUP BY
  1, 2;
