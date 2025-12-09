# Metrics & Analytics

A lightweight data warehouse implementation within Postgres.

## Schema

### `public.metric_definitions`
Metadata about what can be measured.
-   `code`: Unique identifier (e.g., `page_views`)
-   `aggregation`: Default aggregation method (`sum`, `avg`)

### `public.metrics`
Partitioned time-series table for data points.
-   `recorded_at`: Timestamp (Partition Key)
-   `metric_id`: FK to definition
-   `subject_type`, `subject_id`: Polymorphic link or generic grouping
-   `value`: Numeric value
-   `organization_id`: Owner

## Partitions
-   `metrics_2025_q1`
-   `metrics_2025_q2`
...

## Usage
Data is inserted raw. Materialized Views are used to aggregate this data for dashboards to keep read performance high.
