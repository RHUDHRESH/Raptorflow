# Closed Loops Runbook

Closed loops are first-class operational surfaces, not incidental side effects.

## Registered loops

- `foundation-cache-invalidation`: records every Foundation version or section invalidation event and the affected cache scope.
- `content-performance-to-eel`: records performance signals that should update skill utility, specialist routing, or reflection inputs.
- `monthly-cost-thresholds`: converts `org_monthly_costs` deltas into operator-visible `system_alerts`.
- `prediction-resolution`: records prediction outcomes and pushes the result back into PRL confidence and memory hygiene.

## Expectations

- Each loop must be idempotent and org-scoped.
- Each loop must emit tracing, Sentry context, and a durable event row before mutating downstream state.
- Loops that change prompts, cache scope, or EEL state must leave an auditable record in storage.
- Loop surfaces are allowed to be stubbed in this phase, but the storage contract and operator vocabulary must already exist.
