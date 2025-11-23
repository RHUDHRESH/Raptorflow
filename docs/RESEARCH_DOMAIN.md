# Research Domain Implementation

This document describes the research domain implementation for RaptorFlow's customer intelligence system.

## Overview

The research domain creates Ideal Customer Profiles (ICPs) and related persona outputs through a coordinated workflow of specialized agents.

## Architecture

### Components

1. **Customer Intelligence Supervisor** (`backend/agents/research/customer_intelligence_supervisor.py`)
   - Tier 1 supervisor that orchestrates all research sub-agents
   - Implements retry logic with exponential backoff
   - Caches intermediate results in Redis with TTL
   - Logs all steps with correlation IDs

2. **Sub-Agents**

   - **ICP Builder Agent** (`backend/agents/research/icp_builder_agent.py`)
     - Builds structured ICP profiles from company information
     - Uses Vertex AI Gemini (fast model)
     - Validates responses against ICPResponse schema
     - Handles missing data gracefully with fallbacks

   - **Tag Assignment Agent** (`backend/agents/research/tag_assignment_agent.py`)
     - Assigns 5-15 psychographic/demographic tags
     - Uses TAG_OPTIONS catalog from `persona.py`
     - Maps unknown tags to known ones
     - Returns confidence scores for each tag

   - **Persona Narrative Agent** (`backend/agents/research/persona_narrative_agent.py`)
     - Generates human-readable persona narratives
     - Creates memorable alliterative names
     - Produces 2-3 paragraph stories
     - Uses higher temperature for creativity

   - **Pain Point Miner Agent** (`backend/agents/research/pain_point_miner_agent.py`)
     - Extracts and categorizes pain points
     - Categories: operational, financial, strategic
     - Maps pain points to product solutions
     - Rates urgency for each pain point

3. **Research Graph** (`backend/graphs/research_graph.py`)
   - LangGraph StateGraph implementation
   - Defines workflow: build_icp → assign_tags → generate_narrative → mine_pain_points → finalize
   - Uses ResearchState for state management
   - Implements retry logic (3 attempts with exponential backoff)
   - Caches final results with 24-hour TTL

## Workflow

The research workflow follows this sequence:

```
1. Build ICP
   ↓
2. Assign Tags
   ↓
3. Generate Narrative
   ↓
4. Mine Pain Points
   ↓
5. Finalize & Cache
```

Each step:
- Logs execution with correlation ID
- Implements retries on failure
- Caches intermediate results
- Handles errors gracefully (continues on non-critical failures)

## Usage

### Approach 1: Research Graph (Recommended)

```python
from backend.graphs.research_graph import research_graph

# Define ICP request
icp_request = {
    "company_name": "Your Company",
    "industry": "B2B SaaS",
    "product_description": "Your product description",
    "target_market": "Target market segment",
    "target_geo": "Geographic region",
}

# Run the graph
result = await research_graph.run(
    icp_request=icp_request,
    workspace_id="workspace-123",
    goal="Build comprehensive ICP",
)

# Access results
icp = result["icp"]
tags = result["tags"]
narrative = result["persona_narrative"]
pain_points = result["categorized_pain_points"]
```

### Approach 2: Customer Intelligence Supervisor

```python
from backend.agents.research.customer_intelligence_supervisor import (
    customer_intelligence_supervisor
)

# Execute workflow
result = await customer_intelligence_supervisor.execute(
    goal="Build ICP for target customers",
    context={"icp_request": icp_request},
)
```

### Approach 3: Individual Agents

```python
from backend.agents.research.icp_builder_agent import icp_builder_agent

# Use single agent
result = await icp_builder_agent.execute({
    "company_name": "Your Company",
    "industry": "B2B SaaS",
    "product_description": "Your product",
})
```

## Example

Run the example script to see the workflow in action:

```bash
cd /home/user/Raptorflow
python -m backend.examples.research_domain_example
```

## Key Features

### Error Handling
- Retry logic: 3 attempts with exponential backoff (2s, 4s, 8s)
- Graceful degradation: workflow continues even if non-critical steps fail
- Detailed error logging with correlation IDs

### Caching
- Intermediate results: 1-hour TTL
- Final results: 24-hour TTL
- Redis-based with automatic expiration

### Validation
- Pydantic schema validation for all responses
- Fallback data when validation fails
- Tag validation against approved catalog

### Logging
- Structured logging with correlation IDs
- Step-by-step execution tracking
- Performance metrics

### Prompts
- XML-structured prompts for clarity
- System prompts defined in `config/prompts.py`
- Task-specific formatting for each agent

## Models Used

All agents use **Vertex AI Gemini** models:
- ICP Builder: `fast` (Gemini fast model)
- Tag Assignment: `fast` (deterministic tagging)
- Persona Narrative: `creative_fast` (higher temperature for storytelling)
- Pain Point Miner: `fast` (balanced analysis)

## Data Schemas

All responses are validated against Pydantic schemas:
- `ICPResponse` - Complete ICP profile
- `PersonaNarrative` - Persona story
- `Demographics` - Demographic attributes
- `Psychographics` - Psychographic attributes

See `backend/models/persona.py` for schema definitions.

## Redis Caching

Results are cached with these keys:
- `research:{correlation_id}_research` - Intermediate results (1hr)
- `research:{correlation_id}_final` - Final results (24hr)

## Testing

The implementation includes:
- Example script (`backend/examples/research_domain_example.py`)
- Three usage approaches demonstrated
- Sample payloads for different industries

## Dependencies

- Vertex AI Python SDK
- LangGraph for workflow orchestration
- Redis for caching
- Pydantic for validation

## Configuration

Set these environment variables:
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `GOOGLE_CLOUD_LOCATION` - GCP region
- `REDIS_URL` - Redis connection URL

## Future Enhancements

Potential improvements:
- Add real web scraping for pain point mining
- Integrate with external data sources (G2, Reddit, etc.)
- Add A/B testing for prompt variations
- Implement persona scoring and ranking
- Add multi-language support

## Files Created

```
backend/
├── agents/
│   └── research/
│       ├── customer_intelligence_supervisor.py (NEW)
│       ├── icp_builder_agent.py (NEW)
│       ├── tag_assignment_agent.py (NEW)
│       ├── persona_narrative_agent.py (NEW)
│       ├── pain_point_miner_agent.py (NEW)
│       └── __init__.py (UPDATED)
├── graphs/
│   └── research_graph.py (NEW)
├── examples/
│   ├── __init__.py (NEW)
│   └── research_domain_example.py (NEW)
└── config/
    └── prompts.py (UPDATED)
```

## References

- Prompt format: XML-structured with `<context>`, `<task>`, `<output_format>`
- State management: LangGraph `StateGraph` with `ResearchState`
- Base agent: Inherits from `BaseAgent` and `BaseSupervisor`
- Retry pattern: Exponential backoff with configurable max attempts
