# RaptorFlow Backend Agent System - LangChain Specifications

This document contains detailed specifications for all LangChain agents, tools, and orchestration required to power the RaptorFlow ICP onboarding system.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Agent Specifications](#2-agent-specifications)
3. [Tool Definitions](#3-tool-definitions)
4. [Database Schema](#4-database-schema)
5. [API Endpoints](#5-api-endpoints)
6. [Orchestration Flow](#6-orchestration-flow)
7. [Webhook & Integration Setup](#7-webhook--integration-setup)

---

## 1. Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAPTORFLOW BACKEND                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  Enrichment │    │  Analysis   │    │  Generation │        │
│  │   Agents    │    │   Agents    │    │   Agents    │        │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│         │                  │                  │                │
│         └──────────────────┼──────────────────┘                │
│                            │                                    │
│                   ┌────────▼────────┐                          │
│                   │   ORCHESTRATOR  │                          │
│                   │   (LangGraph)   │                          │
│                   └────────┬────────┘                          │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                │
│         │                  │                  │                │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐        │
│  │   Supabase  │    │    Redis    │    │   Vector    │        │
│  │  (Postgres) │    │   (Queue)   │    │  (Pinecone) │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

- **Framework**: LangChain + LangGraph (Python 3.11+)
- **LLM Provider**: OpenAI GPT-4o / Claude 3.5 Sonnet
- **Vector Store**: Pinecone
- **Database**: Supabase (PostgreSQL)
- **Queue**: Upstash Redis
- **External APIs**: Clearbit, BuiltWith, LinkedIn Data

---

## 2. Agent Specifications

### 2.1 PositioningParseAgent

**Purpose**: Analyze raw Dan Kennedy & April Dunford answers to extract structured positioning data.

**Trigger**: When user completes Step 1 (Positioning)

**System Prompt**:
```
You are a strategic positioning analyst trained in frameworks from Dan Kennedy, 
April Dunford, and positioning experts. Your job is to analyze raw positioning 
statements and extract structured insights.

Given the user's answers to:
1. Dan Kennedy Question: "Why should I choose you over every other option?"
2. April Dunford Question: "Who is your product obviously better for?"

Extract the following:
- primary_target: The specific audience segment (be precise)
- primary_problem: The core pain point they solve
- primary_outcome: The main result/transformation delivered
- main_alternatives: List of 3-5 alternatives (competitors, DIY, status quo)
- positioning_type: One of ["head-to-head", "niche-subcategory", "create-new-category"]
- value_proposition: One-sentence value prop in format: "For [WHO] who [PROBLEM], [PRODUCT] [OUTCOME] unlike [ALTERNATIVES]"
- clarity_score: 0-100 score of how clear/specific the positioning is

Be critical. Vague answers like "we help businesses grow" should score low (20-40).
Specific answers like "we help Series A SaaS CFOs close their books 5x faster" should score high (80-95).
```

**Input Schema**:
```json
{
  "dan_kennedy_answer": "string (min 50 chars)",
  "dunford_answer": "string (min 50 chars)",
  "company_name": "string (optional)",
  "industry": "string (optional)"
}
```

**Output Schema**:
```json
{
  "primary_target": "string",
  "primary_problem": "string",
  "primary_outcome": "string",
  "main_alternatives": ["string"],
  "positioning_type": "head-to-head | niche-subcategory | create-new-category",
  "value_proposition": "string",
  "clarity_score": "number (0-100)",
  "suggestions_to_improve": ["string"],
  "confidence": "number (0-1)"
}
```

**Tools Required**:
- None (pure LLM analysis)

---

### 2.2 CompanyEnrichAgent

**Purpose**: Enrich company data using external APIs (Clearbit, BuiltWith, etc.)

**Trigger**: When user enters a website/domain in Step 2 (Company)

**System Prompt**:
```
You are a company research specialist. Given a company domain, use the available 
tools to gather comprehensive firmographic and technographic data.

Your goal is to:
1. Call the Clearbit API to get company details
2. Call BuiltWith to get technology stack
3. Cross-reference and validate the data
4. Flag any conflicts between user input and enriched data

Always prioritize accuracy. If data is uncertain, mark confidence level.
```

**Input Schema**:
```json
{
  "domain": "string",
  "user_provided": {
    "company_name": "string",
    "employee_count": "string",
    "industry": "string",
    "stage": "string"
  }
}
```

**Output Schema**:
```json
{
  "firmographics": {
    "legal_name": "string",
    "domain": "string",
    "employee_count": "number",
    "employee_range": "string",
    "annual_revenue": "number | null",
    "founded_year": "number | null",
    "industry": "string",
    "industry_group": "string",
    "location": {
      "city": "string",
      "country": "string",
      "country_code": "string"
    },
    "funding": {
      "total_raised": "number | null",
      "last_round": "string | null",
      "last_round_date": "string | null"
    }
  },
  "technographics": {
    "website_technologies": ["string"],
    "crm": "string | null",
    "marketing_automation": "string | null",
    "analytics": ["string"],
    "cloud_provider": "string | null",
    "other_notable": ["string"]
  },
  "social": {
    "linkedin_url": "string | null",
    "twitter_handle": "string | null",
    "linkedin_employees": "number | null"
  },
  "conflicts": [
    {
      "field": "string",
      "user_value": "any",
      "enriched_value": "any",
      "recommendation": "string"
    }
  ],
  "enrichment_confidence": "number (0-1)"
}
```

**Tools Required**:
1. `clearbit_company_lookup` - Fetch company data from Clearbit
2. `builtwith_technology_lookup` - Fetch tech stack from BuiltWith
3. `linkedin_company_scrape` - Get LinkedIn company page data (optional)

---

### 2.3 TechStackSeedAgent

**Purpose**: Analyze technology stack and derive integration requirements

**Trigger**: After CompanyEnrichAgent completes

**System Prompt**:
```
You are a technical integration specialist. Analyze the company's technology 
stack and determine:

1. Which of our integrations would be immediately relevant
2. What data sources they likely have
3. Potential technical requirements for implementation
4. Whether they use any competing products

Map technologies to our integration catalog:
- Salesforce → CRM integration, lead scoring
- HubSpot → Marketing automation sync
- Slack → Notifications, workflows
- AWS/GCP → Cloud data connectors
- Snowflake/BigQuery → Data warehouse sync
```

**Input Schema**:
```json
{
  "technographics": {
    "website_technologies": ["string"],
    "crm": "string | null",
    "marketing_automation": "string | null",
    "analytics": ["string"],
    "cloud_provider": "string | null"
  },
  "our_integrations": ["Salesforce", "HubSpot", "Slack", "Linear", "Notion", "Snowflake"]
}
```

**Output Schema**:
```json
{
  "relevant_integrations": [
    {
      "integration": "string",
      "priority": "high | medium | low",
      "reason": "string"
    }
  ],
  "uses_competitor": "boolean",
  "competitor_products": ["string"],
  "technical_requirements": ["string"],
  "implementation_complexity": "low | medium | high",
  "data_sources_available": ["string"]
}
```

**Tools Required**:
- None (analysis based on CompanyEnrichAgent output)

---

### 2.4 JTBDMapperAgent

**Purpose**: Extract Jobs-to-be-Done from product description and derive outcome types

**Trigger**: When user completes Step 3 (Product)

**System Prompt**:
```
You are a Jobs-to-be-Done (JTBD) analyst following the frameworks of Clayton 
Christensen and Alan Klement. Analyze the product description to extract:

1. Functional jobs (what task gets done)
2. Emotional jobs (how they want to feel)
3. Social jobs (how they want to be perceived)
4. The primary outcome type (Money, Time, Risk, Status)

For each job, identify the "when" (situation trigger) and "so that" (desired outcome).

Format jobs as: "When [SITUATION], I want to [MOTIVATION], so that I can [OUTCOME]"
```

**Input Schema**:
```json
{
  "product_name": "string",
  "product_type": "saas | service | hybrid | marketplace | other",
  "main_job": "string (user's description of what the product does)",
  "used_by": ["founder", "marketer", "sales", "ops", "developer", "finance"],
  "positioning": {
    "primary_target": "string",
    "primary_problem": "string",
    "primary_outcome": "string"
  }
}
```

**Output Schema**:
```json
{
  "jobs": [
    {
      "type": "functional | emotional | social",
      "situation": "string",
      "motivation": "string",
      "outcome": "string",
      "full_statement": "string",
      "priority": "primary | secondary | tertiary"
    }
  ],
  "primary_outcome_type": "money | time | risk | status",
  "outcome_metrics": [
    {
      "metric": "string (e.g., 'hours saved per week')",
      "estimated_value": "string (e.g., '10-20 hours')"
    }
  ],
  "hook_candidates": [
    "string (potential marketing hooks based on JTBD)"
  ]
}
```

**Tools Required**:
- None (pure LLM analysis)

---

### 2.5 MonetizationAgent

**Purpose**: Analyze pricing model and derive ticket size, ACV, and sale type

**Trigger**: When user completes pricing section in Step 3

**System Prompt**:
```
You are a SaaS pricing analyst. Analyze the pricing structure to determine:

1. Likely Annual Contract Value (ACV)
2. Ticket size classification (low: <$1k, mid: $1k-$10k, high: >$10k)
3. Whether this is a self-serve or high-touch sale
4. Unit economics implications

Consider industry benchmarks:
- Low-ticket SaaS: typically self-serve, PLG motion
- Mid-ticket SaaS: sales-assisted, demo-driven
- High-ticket SaaS: enterprise sales, custom pricing
```

**Input Schema**:
```json
{
  "pricing_model": "one-time | monthly | usage-based | hybrid",
  "price_range": "string (e.g., '300-800')",
  "has_tiers": "boolean",
  "tiers": [
    {
      "name": "string",
      "for_who": "string",
      "price": "string"
    }
  ],
  "industry": "string",
  "company_stage": "string"
}
```

**Output Schema**:
```json
{
  "likely_acv": {
    "low": "number",
    "mid": "number",
    "high": "number"
  },
  "ticket_size": "low | mid | high",
  "sale_type": "self-serve | sales-assisted | enterprise",
  "recommended_motion": "PLG | demo-led | outbound | hybrid",
  "unit_economics_notes": ["string"],
  "pricing_recommendations": ["string"]
}
```

**Tools Required**:
- None (pure LLM analysis)

---

### 2.6 CompetitorSurfaceAgent

**Purpose**: Research competitors and build competitive positioning map

**Trigger**: When user names competitors in Step 4 (Market)

**System Prompt**:
```
You are a competitive intelligence analyst. For each competitor:

1. Fetch their website and extract key messaging
2. Identify their positioning, tagline, and value prop
3. Determine their approximate pricing tier
4. Map their feature set
5. Identify positioning gaps and potential differentiation angles

Build a competitive landscape map showing where each player sits on:
- X-axis: Price (Budget to Premium)
- Y-axis: Complexity (Simple to Power-user)
```

**Input Schema**:
```json
{
  "company_name": "string",
  "company_positioning": {
    "value_proposition": "string",
    "primary_target": "string"
  },
  "competitors": ["string"],
  "user_price_position": "number (0-100)",
  "user_complexity_position": "number (0-100)",
  "industry": "string"
}
```

**Output Schema**:
```json
{
  "competitor_profiles": [
    {
      "name": "string",
      "website": "string",
      "tagline": "string",
      "value_prop": "string",
      "target_audience": "string",
      "pricing_tier": "budget | mid-market | premium | enterprise",
      "key_features": ["string"],
      "positioning_angle": "string",
      "weaknesses": ["string"],
      "map_coordinates": {
        "x": "number (0-100, complexity)",
        "y": "number (0-100, price)"
      }
    }
  ],
  "positioning_gaps": [
    {
      "gap": "string (description of underserved area)",
      "opportunity": "string (how to exploit it)"
    }
  ],
  "differentiation_wedges": [
    {
      "wedge": "string",
      "competitors_weak_on": ["string"],
      "your_strength": "string"
    }
  ],
  "category_maturity": "emerging | growing | mature | declining",
  "recommended_positioning_angle": "string"
}
```

**Tools Required**:
1. `web_scraper` - Fetch and parse competitor websites
2. `google_search` - Search for competitor pricing, reviews
3. `g2_scraper` - Get G2 Crowd reviews and comparisons (optional)

---

### 2.7 StrategyProfileAgent

**Purpose**: Build strategy profile from trade-off matrices and derive recommended protocols

**Trigger**: When user completes Step 5 (Strategy)

**System Prompt**:
```
You are a B2B marketing strategist. Based on the user's strategic choices:

Goal (Velocity/Efficiency/Penetration) + 
Demand Source (Capture/Creation/Expansion) + 
Persuasion Axis (Money/Time/Risk)

Derive:
1. Implied trade-offs (what they're accepting)
2. Recommended execution protocols (A-F)
3. Budget allocation recommendations
4. Channel prioritization
5. Campaign type recommendations

Protocol mapping:
- A: Authority Blitz (content, thought leadership)
- B: Trust Anchor (social proof, validation)
- C: Cost of Inaction (urgency, competitive displacement)
- D: Facilitator Nudge (onboarding, activation)
- E: Champions Armory (internal advocacy, expansion)
- F: Churn Intercept (retention, save plays)
```

**Input Schema**:
```json
{
  "goal_primary": "velocity | efficiency | penetration",
  "goal_secondary": "velocity | efficiency | penetration | null",
  "demand_source": "capture | creation | expansion",
  "persuasion_axis": "money | time | risk-image",
  "company_stage": "string",
  "ticket_size": "low | mid | high",
  "sale_type": "self-serve | sales-assisted | enterprise"
}
```

**Output Schema**:
```json
{
  "strategy_profile": {
    "name": "string (e.g., 'Velocity Creator')",
    "description": "string"
  },
  "implied_tradeoffs": ["string"],
  "recommended_protocols": {
    "primary": ["A", "B"],
    "secondary": ["D"],
    "disabled": ["F"]
  },
  "budget_allocation": {
    "content_creation": "percentage",
    "paid_acquisition": "percentage",
    "outbound": "percentage",
    "events_partnerships": "percentage",
    "retention_expansion": "percentage"
  },
  "channel_priority": [
    {
      "channel": "string",
      "priority": "high | medium | low",
      "reason": "string"
    }
  ],
  "campaign_recommendations": [
    {
      "campaign_type": "string",
      "protocol": "A-F",
      "timing": "phase 1 | phase 2 | phase 3",
      "expected_impact": "string"
    }
  ]
}
```

**Tools Required**:
- None (rule-based + LLM analysis)

---

### 2.8 ICPBuildAgent

**Purpose**: Generate 3 ideal customer profiles based on all collected data

**Trigger**: After StrategyProfileAgent completes

**System Prompt**:
```
You are an ICP (Ideal Customer Profile) architect. Using the 6D ICP Framework:

1. Firmographics - Company characteristics
2. Technographics - Technology stack
3. Psychographics - Motivations, pain points, triggers
4. Behavioral Triggers - Signals they're in-market
5. Buying Committee - Key personas and roles
6. Category Context - Market position and competitive landscape

Generate 3 distinct ICPs:
- ICP 1: "Desperate Scaler" - High urgency, immediate need
- ICP 2: "Frustrated Optimizer" - Tried alternatives, ready to switch
- ICP 3: "Risk Mitigator" - Conservative, needs assurance

Each ICP should be specific enough to inform:
- Targeting criteria for ads
- Messaging angles for content
- Qualification questions for sales
- Trigger-based outreach campaigns

Score each ICP on fit (0-100) based on:
- Alignment with positioning
- Alignment with strategy
- Market size potential
- Likelihood to convert
```

**Input Schema**:
```json
{
  "company": { /* Company data */ },
  "product": { /* Product data */ },
  "positioning": { /* Positioning analysis */ },
  "market": { /* Market & competition data */ },
  "strategy": { /* Strategy profile */ },
  "jtbd": { /* Jobs-to-be-done */ }
}
```

**Output Schema**:
```json
{
  "icps": [
    {
      "id": "string",
      "label": "string (e.g., 'Desperate Scaler')",
      "summary": "string (2-3 sentence description)",
      "firmographics": {
        "employee_range": "string",
        "revenue_range": "string | null",
        "industries": ["string"],
        "stages": ["string"],
        "regions": ["string"],
        "exclude": ["string (anti-patterns)"]
      },
      "technographics": {
        "must_have": ["string"],
        "nice_to_have": ["string"],
        "red_flags": ["string (competitor usage, etc.)"]
      },
      "psychographics": {
        "pain_points": ["string"],
        "motivations": ["string"],
        "internal_triggers": ["string"],
        "buying_constraints": ["string"]
      },
      "behavioral_triggers": [
        {
          "signal": "string",
          "source": "string (LinkedIn, job boards, news, etc.)",
          "urgency_boost": "number (0-100)"
        }
      ],
      "buying_committee": [
        {
          "role": "Decision Maker | Champion | Economic Buyer | Technical Eval | End User",
          "typical_title": "string",
          "concerns": ["string"],
          "success_criteria": ["string"]
        }
      ],
      "category_context": {
        "market_position": "leader | challenger | newcomer",
        "current_solution": "string",
        "switching_triggers": ["string"]
      },
      "fit_score": "number (0-100)",
      "fit_reasoning": "string",
      "messaging_angle": "string",
      "qualification_questions": ["string"]
    }
  ],
  "icp_comparison": {
    "highest_urgency": "string (ICP id)",
    "largest_market": "string (ICP id)",
    "easiest_to_reach": "string (ICP id)"
  }
}
```

**Tools Required**:
- None (synthesis of all previous agent outputs)

---

### 2.9 MoveAssemblyAgent

**Purpose**: Generate 90-day war plan with phases, campaigns, and tactical moves

**Trigger**: After ICPBuildAgent completes

**System Prompt**:
```
You are a B2B marketing strategist building a 90-day execution plan.

Using the strategy profile and selected ICPs, create a phased war plan:

Phase 1 (Days 1-30): Discovery & Foundation
- Objective: Establish presence, build content foundation
- Protocols: A (Authority Blitz)
- Key activities: Pillar content, positioning validation

Phase 2 (Days 31-60): Launch & Validation
- Objective: Generate demand, validate messaging
- Protocols: B (Trust Anchor), C (Cost of Inaction)
- Key activities: Case studies, demand campaigns, outbound

Phase 3 (Days 61-90): Optimization & Scale
- Objective: Double down on winners, prepare for next quarter
- Protocols: D, E, F (as needed)
- Key activities: Optimization, expansion plays

For each phase, define:
- Specific campaigns (with protocol mapping)
- Tactical moves (content pieces, ad campaigns, etc.)
- KPIs with targets
- RAG thresholds (Red/Amber/Green)
```

**Input Schema**:
```json
{
  "strategy_profile": { /* Strategy data */ },
  "selected_icps": [{ /* ICP data */ }],
  "company": { /* Company data */ },
  "product": { /* Product data */ },
  "budget_range": "string (optional)"
}
```

**Output Schema**:
```json
{
  "war_plan": {
    "summary": "string",
    "phases": [
      {
        "id": "number",
        "name": "string",
        "days": "string (e.g., '1-30')",
        "objective": "string",
        "protocols_active": ["A", "B"],
        "campaigns": [
          {
            "name": "string",
            "protocol": "A-F",
            "description": "string",
            "target_icps": ["string (ICP ids)"],
            "channels": ["string"],
            "estimated_effort": "low | medium | high"
          }
        ],
        "moves": [
          {
            "name": "string",
            "type": "content | ad | email | event | outbound",
            "description": "string",
            "deliverables": ["string"],
            "owner": "string (suggested role)",
            "timeline": "string"
          }
        ],
        "kpis": [
          {
            "name": "string",
            "target": "string",
            "rag_thresholds": {
              "green": "string (>= this)",
              "amber": "string (between)",
              "red": "string (<= this)"
            }
          }
        ]
      }
    ],
    "90_day_north_star": {
      "metric": "string",
      "target": "string"
    },
    "first_week_checklist": ["string"],
    "critical_dependencies": ["string"]
  }
}
```

**Tools Required**:
- None (synthesis based on strategy + ICPs)

---

### 2.10 MetricWireAgent

**Purpose**: Define metrics framework and RAG thresholds for the war plan

**Trigger**: After MoveAssemblyAgent completes

**System Prompt**:
```
You are a marketing analytics specialist. For each phase and campaign in the 
war plan, define:

1. Leading indicators (activities, inputs)
2. Lagging indicators (outcomes, results)
3. RAG thresholds based on industry benchmarks
4. Attribution model recommendations
5. Reporting cadence

Use realistic benchmarks:
- Content: 1-3% engagement rate on LinkedIn
- Paid: 1-2% CTR, 3-5% landing page CVR
- Email: 20-30% open rate, 2-5% click rate
- Outbound: 2-5% reply rate
- Demo: 20-30% show rate, 20-40% demo-to-opp

Adjust based on:
- Industry (B2B SaaS vs other)
- Ticket size (low-ticket = higher volume metrics)
- Stage (early = focus on leading indicators)
```

**Input Schema**:
```json
{
  "war_plan": { /* War plan from MoveAssemblyAgent */ },
  "company_stage": "string",
  "ticket_size": "low | mid | high",
  "industry": "string"
}
```

**Output Schema**:
```json
{
  "metrics_framework": {
    "north_star": {
      "metric": "string",
      "definition": "string",
      "target_90_day": "string"
    },
    "phase_metrics": [
      {
        "phase_id": "number",
        "leading_indicators": [
          {
            "name": "string",
            "definition": "string",
            "target": "string",
            "frequency": "daily | weekly | monthly"
          }
        ],
        "lagging_indicators": [
          {
            "name": "string",
            "definition": "string",
            "target": "string",
            "rag": {
              "green": "string",
              "amber": "string",
              "red": "string"
            }
          }
        ]
      }
    ],
    "attribution_model": "first-touch | last-touch | linear | time-decay",
    "reporting_cadence": {
      "daily_standup": ["string (metrics to review)"],
      "weekly_review": ["string (metrics to review)"],
      "monthly_retro": ["string (metrics to review)"]
    },
    "alert_triggers": [
      {
        "condition": "string",
        "action": "string",
        "urgency": "high | medium | low"
      }
    ]
  }
}
```

**Tools Required**:
- None (rule-based + LLM analysis)

---

## 3. Tool Definitions

### 3.1 clearbit_company_lookup

```python
from langchain.tools import tool
from typing import Optional
import httpx

@tool
def clearbit_company_lookup(domain: str) -> dict:
    """
    Fetch company data from Clearbit Enrichment API.
    
    Args:
        domain: Company domain (e.g., 'acme.com')
    
    Returns:
        Company profile including firmographics, funding, tech stack
    """
    CLEARBIT_API_KEY = os.environ["CLEARBIT_API_KEY"]
    
    response = httpx.get(
        f"https://company.clearbit.com/v2/companies/find",
        params={"domain": domain},
        headers={"Authorization": f"Bearer {CLEARBIT_API_KEY}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        return {
            "name": data.get("name"),
            "legal_name": data.get("legalName"),
            "domain": data.get("domain"),
            "employee_count": data.get("metrics", {}).get("employees"),
            "employee_range": data.get("metrics", {}).get("employeesRange"),
            "annual_revenue": data.get("metrics", {}).get("estimatedAnnualRevenue"),
            "industry": data.get("category", {}).get("industry"),
            "industry_group": data.get("category", {}).get("industryGroup"),
            "location": {
                "city": data.get("geo", {}).get("city"),
                "country": data.get("geo", {}).get("country"),
                "country_code": data.get("geo", {}).get("countryCode")
            },
            "founded_year": data.get("foundedYear"),
            "funding": {
                "total_raised": data.get("metrics", {}).get("raised"),
                "last_round": data.get("crunchbase", {}).get("lastFundingRound"),
            },
            "tech": data.get("tech", []),
            "linkedin_handle": data.get("linkedin", {}).get("handle"),
            "twitter_handle": data.get("twitter", {}).get("handle")
        }
    elif response.status_code == 404:
        return {"error": "Company not found", "domain": domain}
    else:
        return {"error": f"API error: {response.status_code}"}
```

### 3.2 builtwith_technology_lookup

```python
@tool
def builtwith_technology_lookup(domain: str) -> dict:
    """
    Fetch technology stack from BuiltWith API.
    
    Args:
        domain: Company domain (e.g., 'acme.com')
    
    Returns:
        List of technologies detected on the website
    """
    BUILTWITH_API_KEY = os.environ["BUILTWITH_API_KEY"]
    
    response = httpx.get(
        f"https://api.builtwith.com/v20/api.json",
        params={
            "KEY": BUILTWITH_API_KEY,
            "LOOKUP": domain
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        technologies = []
        
        for result in data.get("Results", []):
            for path in result.get("Result", {}).get("Paths", []):
                for tech in path.get("Technologies", []):
                    technologies.append({
                        "name": tech.get("Name"),
                        "category": tech.get("Categories", []),
                        "first_detected": tech.get("FirstDetected"),
                        "last_detected": tech.get("LastDetected")
                    })
        
        return {
            "domain": domain,
            "technologies": technologies,
            "categories": list(set([
                cat for tech in technologies 
                for cat in tech.get("category", [])
            ]))
        }
    else:
        return {"error": f"API error: {response.status_code}"}
```

### 3.3 web_scraper

```python
@tool
def web_scraper(url: str, selectors: dict = None) -> dict:
    """
    Scrape a webpage and extract content.
    
    Args:
        url: URL to scrape
        selectors: Optional dict of CSS selectors to extract specific content
    
    Returns:
        Page content including title, meta, headings, and body text
    """
    from bs4 import BeautifulSoup
    
    response = httpx.get(url, follow_redirects=True, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    result = {
        "url": url,
        "title": soup.title.string if soup.title else None,
        "meta_description": None,
        "h1": [],
        "h2": [],
        "body_text": ""
    }
    
    # Meta description
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        result["meta_description"] = meta.get("content")
    
    # Headings
    result["h1"] = [h.get_text().strip() for h in soup.find_all("h1")]
    result["h2"] = [h.get_text().strip() for h in soup.find_all("h2")]
    
    # Body text (cleaned)
    for script in soup(["script", "style", "nav", "footer"]):
        script.decompose()
    result["body_text"] = soup.get_text(separator=" ", strip=True)[:5000]
    
    # Custom selectors
    if selectors:
        for key, selector in selectors.items():
            elements = soup.select(selector)
            result[key] = [el.get_text().strip() for el in elements]
    
    return result
```

### 3.4 google_search

```python
@tool
def google_search(query: str, num_results: int = 5) -> list:
    """
    Search Google and return top results.
    
    Args:
        query: Search query
        num_results: Number of results to return
    
    Returns:
        List of search results with title, URL, and snippet
    """
    SERP_API_KEY = os.environ["SERP_API_KEY"]
    
    response = httpx.get(
        "https://serpapi.com/search",
        params={
            "q": query,
            "api_key": SERP_API_KEY,
            "num": num_results
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "title": r.get("title"),
                "url": r.get("link"),
                "snippet": r.get("snippet")
            }
            for r in data.get("organic_results", [])
        ]
    else:
        return []
```

---

## 4. Database Schema

### 4.1 Supabase Tables

```sql
-- Onboarding intake (stores all step data)
CREATE TABLE onboarding_intake (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Step 1: Positioning
    positioning JSONB DEFAULT '{}',
    positioning_derived JSONB DEFAULT '{}',
    
    -- Step 2: Company
    company JSONB DEFAULT '{}',
    company_enriched JSONB DEFAULT '{}',
    
    -- Step 3: Product
    product JSONB DEFAULT '{}',
    product_derived JSONB DEFAULT '{}',
    
    -- Step 4: Market
    market JSONB DEFAULT '{}',
    market_system_view JSONB DEFAULT '{}',
    
    -- Step 5: Strategy
    strategy JSONB DEFAULT '{}',
    strategy_derived JSONB DEFAULT '{}',
    
    -- Generated outputs
    icps JSONB DEFAULT '[]',
    war_plan JSONB DEFAULT '{}',
    metrics_framework JSONB DEFAULT '{}',
    
    -- Metadata
    current_step INTEGER DEFAULT 1,
    completed_steps INTEGER[] DEFAULT '{}',
    mode VARCHAR(20) DEFAULT 'self-service', -- 'self-service' or 'sales-assisted'
    sales_rep_id UUID REFERENCES auth.users(id),
    share_token VARCHAR(50) UNIQUE,
    
    -- Payment
    selected_plan VARCHAR(20),
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_completed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent execution logs
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_id UUID REFERENCES onboarding_intake(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shared links for sales-assisted flow
CREATE TABLE shared_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intake_id UUID REFERENCES onboarding_intake(id) ON DELETE CASCADE,
    token VARCHAR(50) UNIQUE NOT NULL,
    sales_rep_id UUID REFERENCES auth.users(id),
    expires_at TIMESTAMPTZ,
    accessed_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    payment_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE onboarding_intake ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_links ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can access own intake" ON onboarding_intake
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Sales reps can access assigned intake" ON onboarding_intake
    FOR ALL USING (auth.uid() = sales_rep_id);

CREATE POLICY "Shared links public read" ON shared_links
    FOR SELECT USING (true);
```

---

## 5. API Endpoints

### 5.1 Onboarding Endpoints

```
POST /api/onboarding/intake
  - Create or update intake data
  - Body: { step: number, data: object }
  - Triggers relevant agents for the step

GET /api/onboarding/intake/:id
  - Get complete intake data
  - Returns all steps + derived data

POST /api/onboarding/generate-icps
  - Trigger ICP generation
  - Requires steps 1-5 completed
  - Returns job_id for polling

POST /api/onboarding/generate-warplan
  - Trigger war plan generation
  - Requires ICPs generated
  - Returns job_id for polling

GET /api/onboarding/job/:job_id
  - Poll job status
  - Returns { status, result }
```

### 5.2 Shared Link Endpoints

```
POST /api/shared/create
  - Create shared link for sales-assisted flow
  - Body: { intake_id: uuid }
  - Returns { token, url, expires_at }

GET /api/shared/:token
  - Get shared intake data (public)
  - Returns intake summary for display

POST /api/shared/:token/payment
  - Initiate payment for shared link
  - Body: { plan: string }
  - Returns PhonePe payment URL
```

### 5.3 Payment Endpoints

```
POST /api/payments/initiate
  - Initiate PhonePe payment
  - Body: { plan: string, intake_id: uuid }
  - Returns { payment_url, txn_id }

POST /api/payments/webhook
  - PhonePe webhook callback
  - Verifies signature, updates payment status
  - Activates user plan

GET /api/payments/status/:txn_id
  - Check payment status
  - Returns { status, plan }
```

---

## 6. Orchestration Flow

### 6.1 LangGraph Workflow

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class OnboardingState(TypedDict):
    intake_id: str
    step: int
    positioning: dict
    positioning_derived: dict
    company: dict
    company_enriched: dict
    product: dict
    product_derived: dict
    market: dict
    market_system_view: dict
    strategy: dict
    strategy_derived: dict
    icps: List[dict]
    war_plan: dict
    metrics: dict
    errors: List[str]

def build_onboarding_graph():
    graph = StateGraph(OnboardingState)
    
    # Add nodes (agents)
    graph.add_node("positioning_parse", positioning_parse_node)
    graph.add_node("company_enrich", company_enrich_node)
    graph.add_node("tech_stack_seed", tech_stack_seed_node)
    graph.add_node("jtbd_mapper", jtbd_mapper_node)
    graph.add_node("monetization", monetization_node)
    graph.add_node("competitor_surface", competitor_surface_node)
    graph.add_node("strategy_profile", strategy_profile_node)
    graph.add_node("icp_build", icp_build_node)
    graph.add_node("move_assembly", move_assembly_node)
    graph.add_node("metric_wire", metric_wire_node)
    
    # Define edges based on step
    def route_by_step(state: OnboardingState):
        step = state["step"]
        if step == 1:
            return "positioning_parse"
        elif step == 2:
            return "company_enrich"
        elif step == 3:
            return "jtbd_mapper"
        elif step == 4:
            return "competitor_surface"
        elif step == 5:
            return "strategy_profile"
        elif step == 6:
            return "icp_build"
        elif step == 7:
            return "move_assembly"
        else:
            return END
    
    graph.add_conditional_edges(
        "__start__",
        route_by_step
    )
    
    # Sequential flows within steps
    graph.add_edge("company_enrich", "tech_stack_seed")
    graph.add_edge("jtbd_mapper", "monetization")
    graph.add_edge("icp_build", END)
    graph.add_edge("move_assembly", "metric_wire")
    graph.add_edge("metric_wire", END)
    
    return graph.compile()
```

### 6.2 Job Queue (Upstash Redis)

```python
from upstash_redis import Redis
import json

redis = Redis.from_env()

def queue_agent_job(agent_name: str, intake_id: str, input_data: dict):
    """Queue an agent job for async processing"""
    job_id = f"job_{intake_id}_{agent_name}_{int(time.time())}"
    
    job = {
        "id": job_id,
        "agent": agent_name,
        "intake_id": intake_id,
        "input": input_data,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Add to queue
    redis.lpush("agent_jobs", json.dumps(job))
    
    # Store job for status lookup
    redis.set(f"job:{job_id}", json.dumps(job), ex=86400)  # 24h expiry
    
    return job_id

def process_agent_jobs():
    """Worker that processes queued jobs"""
    while True:
        job_data = redis.brpop("agent_jobs", timeout=30)
        if not job_data:
            continue
        
        job = json.loads(job_data[1])
        job_id = job["id"]
        
        try:
            # Update status
            job["status"] = "running"
            job["started_at"] = datetime.utcnow().isoformat()
            redis.set(f"job:{job_id}", json.dumps(job))
            
            # Run the agent
            result = run_agent(job["agent"], job["input"])
            
            # Update with result
            job["status"] = "completed"
            job["output"] = result
            job["completed_at"] = datetime.utcnow().isoformat()
            redis.set(f"job:{job_id}", json.dumps(job))
            
        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)
            redis.set(f"job:{job_id}", json.dumps(job))
```

---

## 7. Webhook & Integration Setup

### 7.1 PhonePe Webhook

```python
from fastapi import APIRouter, Request, HTTPException
import hashlib
import hmac

router = APIRouter()

@router.post("/api/payments/webhook")
async def phonepe_webhook(request: Request):
    """Handle PhonePe payment webhook"""
    
    body = await request.body()
    signature = request.headers.get("X-VERIFY")
    
    # Verify signature
    expected = hmac.new(
        PHONEPE_SALT_KEY.encode(),
        body + f"/pg/v1/status/{MERCHANT_ID}".encode(),
        hashlib.sha256
    ).hexdigest() + "###" + PHONEPE_SALT_INDEX
    
    if signature != expected:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse response
    data = await request.json()
    
    if data.get("code") == "PAYMENT_SUCCESS":
        txn_id = data.get("data", {}).get("merchantTransactionId")
        
        # Update payment record
        await supabase.from_("payments").update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "phonepe_response": data
        }).eq("txn_id", txn_id).execute()
        
        # Get payment details
        payment = await supabase.from_("payments").select("*").eq("txn_id", txn_id).single().execute()
        
        # Activate plan
        await supabase.rpc("activate_plan", {
            "p_user_id": payment.data["user_id"],
            "p_plan": payment.data["plan"],
            "p_payment_id": payment.data["id"],
            "p_amount": payment.data["amount"]
        }).execute()
    
    return {"status": "ok"}
```

### 7.2 Clearbit Webhook (Data Refresh)

```python
@router.post("/api/webhooks/clearbit")
async def clearbit_webhook(request: Request):
    """Handle Clearbit data change notifications"""
    
    data = await request.json()
    domain = data.get("domain")
    
    # Find intakes using this domain
    intakes = await supabase.from_("onboarding_intake").select("id").eq(
        "company->website", domain
    ).execute()
    
    for intake in intakes.data:
        # Re-run enrichment
        queue_agent_job("company_enrich", intake["id"], {"domain": domain})
    
    return {"status": "ok", "refreshed": len(intakes.data)}
```

---

## Summary

This backend system uses:

1. **10 LangChain Agents** for different processing tasks
2. **4 Tools** for external data fetching (Clearbit, BuiltWith, Web Scraper, Google Search)
3. **LangGraph** for orchestrating agent workflows
4. **Supabase** for data persistence
5. **Upstash Redis** for job queuing
6. **PhonePe** for payment processing

Each agent is triggered at specific steps of the onboarding flow, with outputs feeding into subsequent agents. The system supports both synchronous (small tasks) and asynchronous (ICP generation, war plan) processing.

For the sales-assisted flow, the system generates shareable links that allow prospects to view a summary and complete payment without authentication.

