# RaptorFlow Cost Model & Optimization Analysis

## Current Cost Drivers (Estimated per request)

### 1. LLM/Inference Costs (Primary Driver)
**Current Architecture:**
- Centralized LLM adapter with Vertex AI primary + OpenAI fallback
- 4-tier model system: Heavy → Reasoning → General → Simple
- 17+ agents mapped to different models
- Telemetry service tracks usage but no active cost optimization

**Cost Breakdown per request:**
- **Heavy tasks** (ICP Build, Barrier Engine, Strategy Profile): ~$0.15-0.25 (Gemini 2.0 Flash Thinking)
- **Reasoning tasks** (Plan Generator, Muse Agent, etc.): ~$0.08-0.12 (Gemini 2.5 Pro)
- **General tasks** (Company Enrich, Competitor Surface): ~$0.02-0.04 (Gemini 2.5 Flash)
- **Simple tasks** (Data Extract, Input Validate): ~$0.005-0.01 (Gemini 1.5 Flash)

**Average estimated cost per LLM request: $0.06-0.08**

### 2. Infrastructure Costs (Secondary)
**Current Setup:**
- ECS Fargate: 512 CPU / 1024 MB RAM = ~$0.04/hour (~$29/month)
- RDS t3.micro PostgreSQL = ~$0.02/hour (~$15/month)
- ElastiCache t3.micro Redis = ~$0.02/hour (~$15/month)
- SQS queues = negligible
- S3 storage = ~$0.02/month

**Per-request infrastructure cost: ~$0.001-0.002** (assuming 1000 requests/hour)

### 3. External API Costs (Tertiary)
- PhonePe payments: 2% transaction fee (not per-request)
- Supabase: Included in plan limits
- No other significant external APIs identified

## Current Total Cost Estimate

**Per-request cost: $0.06-0.08** (LLM dominated)
**Monthly cost at 10K requests/day: $180-240** (plus infrastructure ~$60)

## Major Cost Optimization Opportunities

### 1. Model Selection Optimization (High Impact)
**Current Issue:** All agents use fixed model mappings regardless of actual complexity
**Opportunity:** Dynamic model selection based on:
- Input size/complexity
- Response requirements
- Cost thresholds

**Potential Savings:** 30-50% on LLM costs

### 2. Response Caching (High Impact)
**Current Issue:** No caching of expensive operations
**Opportunity:** Redis caching for:
- Company enrichment results (6+ hour TTL)
- Similar prompts/responses
- Static agent outputs

**Potential Savings:** 20-40% on repeated requests

### 3. Request Batching (Medium-High Impact)
**Current Issue:** Individual LLM calls for each agent
**Opportunity:** Batch similar requests and process in parallel
**Potential Savings:** 15-25% through efficiency gains

### 4. Infrastructure Rightsizing (Medium Impact)
**Current Issue:** Over-provisioned for current load
**Opportunity:** Right-size containers and enable spot instances
**Potential Savings:** 20-30% on infrastructure costs

### 5. Async Processing (Medium Impact)
**Current Issue:** Synchronous LLM calls block requests
**Opportunity:** Queue heavy work, return immediate responses
**Potential Savings:** 10-20% through better resource utilization

## Implementation Priority

1. **Phase 1: Quick Wins** (1-2 weeks)
   - Implement response caching → 20-40% savings
   - Add dynamic model selection → 30-50% savings
   - Right-size infrastructure → 20-30% savings

2. **Phase 2: Architecture Changes** (2-3 weeks)
   - Centralized LLM client with batching
   - Async worker queues
   - Enhanced telemetry

3. **Phase 3: Advanced Optimizations** (1-2 weeks)
   - Prompt engineering and token trimming
   - Advanced caching strategies
   - Load testing and validation

**Target: Reduce per-request cost to <$0.03 (50% reduction)**

## Success Metrics
- Per-request cost < $0.03
- 50%+ reduction in LLM API costs
- 90%+ cache hit rate for repeated requests
- Sub-2 second average response time maintained


