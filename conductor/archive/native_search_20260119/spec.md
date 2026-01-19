# Specification: SOTA Native Search Cluster

## Overview
Implement a robust, scalable, and $0-cost search infrastructure for RaptorFlow. This track replaces paid search APIs with a self-hosted, multi-engine aggregator deployed on Google Cloud Platform (GCP), designed to handle hundreds of concurrent SaaS users.

## Functional Requirements
- **Self-Hosted Aggregator**: Deploy and tune SearXNG on GCP Compute Engine to aggregate results from Google, Bing, and DuckDuckGo.
- **Reddit .json Backdoor**: Implement a native scraper that leverages Reddit's `.json` endpoint for social intelligence without requiring an API key.
- **Hybrid API Architecture**:
    - **Sync Flow**: REST API endpoint for instant search results.
    - **Async Flow**: Pub/Sub worker integration for deep-research tasks that save results to Supabase.
- **Stealth & Resilience**:
    - Pair SearXNG with Gluetun for VPN-based IP rotation.
    - Implement TLS/HTTP2 fingerprinting evasion.
- **Intelligence Layer**:
    - Deduplicate results across multiple engines.
    - Implement a basic result-scoring algorithm to ensure high-quality findings.

## Non-Functional Requirements
- **High Concurrency**: Architecture must support 100+ concurrent users via horizontal scaling and Nginx load balancing.
- **Zero API Cost**: 100% reliance on self-hosted tools and native scrapers ($0 search API spend).
- **Performance**: Edge caching via Upstash Redis to deliver repeat results in <100ms.

## Acceptance Criteria
- [ ] Search query returns a merged list of results from at least 3 engines.
- [ ] Reddit results are successfully extracted using the `.json` method.
- [ ] The system successfully falls back to alternative engines if one is blocked.
- [ ] Redis caching is verified to store and retrieve result clusters.
- [ ] Load test verifies the system handles 10 concurrent requests without failure.

## Out of Scope
- Native scraping for Twitter/X and LinkedIn (deferred to future "Expert Skills" track).
- Advanced multimedia (image/video) specific search filtering.
