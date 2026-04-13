# Threat Model Overview

## Core threats

- Cross-tenant data leakage through SQL, cache keys, WebSocket sessions, or vector filters
- Prompt injection via scraped content, uploaded assets, or tool results
- Webhook replay or forgery for Clerk and Razorpay
- Secret sprawl from local `.env` files or CI misconfiguration
- Queue poisoning or duplicate job execution
- Long-lived websocket session hijacking or stale auth context

## Required controls

- `org_id` enforced in schemas, query surfaces, and RLS
- signed webhook verification with idempotency storage
- per-org Dragonfly key namespaces and lock namespaces
- structured allowlists for tool results entering prompts
- CloudWatch and Sentry correlation IDs on all async workflows
- bounded retry semantics for jobs and webhooks
