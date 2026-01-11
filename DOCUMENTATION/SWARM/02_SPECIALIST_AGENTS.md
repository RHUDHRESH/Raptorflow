# SPECIALIST AGENTS

---

## 1. ONBOARDING SWARM

### Step-to-Agent Mapping

| Step | Name | Agent | Tools |
|------|------|-------|-------|
| 1 | Evidence Vault | `VaultProcessor` | upload, scraper, OCR |
| 2 | Auto Extraction | `TruthExtractor` | NLP parser |
| 3 | Contradictions | `ContradictionDetector` | semantic similarity |
| 4 | Truth Validation | `TruthValidator` | human-in-loop |
| 6 | Pricing | `PricingAnalyzer` | competitor scraper |
| 7 | Market Research | `MarketResearcher` | web search, review scraper |
| 8 | Competitors | `CompetitorAnalyzer` | web scraper |
| 9 | Competitive Ladder | `CompetitorRanker` | ranking algo |
| 10 | Market Category | `CategoryAdvisor` | market analysis |
| 11 | USPs | `DifferentiationAnalyzer` | capability scorer |
| 12 | Capability Matrix | `PositioningMapper` | perceptual map |
| 13 | Positioning | `PositioningWriter` | copy generator |
| 14 | Focus/Sacrifice | `StrategyAdvisor` | priority ranker |
| 15 | ICP Profiles | `ICPArchitect` | persona generator |
| 16 | Buying Process | `BuyingJourneyMapper` | journey mapper |
| 17 | Guardrails | `MessagingGuardian` | constraint extractor |
| 18 | Soundbites | `SoundbiteGenerator` | copy generator |
| 19 | Hierarchy | `MessageHierarchyBuilder` | organizer |
| 21 | Channels | `ChannelAdvisor` | recommender |
| 22 | TAM/SAM | `MarketSizer` | calculator |
| 23-25 | Synthesis | `SynthesisEngine` | compiler |

### ICP Architect Agent

```python
from pydantic import BaseModel, Field
from langchain_google_vertexai import ChatVertexAI

class ICPProfile(BaseModel):
    id: str
    name: str  # "Scaling SaaS Founder at $1M-$5M ARR"
    tagline: str
    code: str
    demographics: dict  # age, income, location, role, stage
    psychographics: dict  # beliefs, identity, becoming, fears, values
    behaviors: dict  # hangouts, consumption, follows, language, triggers
    market_sophistication: dict  # stage 1-5, reasoning
    scores: dict  # painIntensity, willingnessToPay, accessibility, productFit

ICP_PROMPT = """You create SPECIFIC ICPs, not generic personas.

BAD: "SaaS Founder"
GOOD: "Scaling SaaS founder, B2B at $1M-$5M ARR, scaling first marketing team"

For each ICP define:
1. Demographics: Age, income, location, role, stage
2. Psychographics: Beliefs, identity, aspirations, fears, values
3. Behaviors: Hangouts, consumption, follows, language patterns
4. Market Sophistication: Stage 1-5 (Unaware → Most Aware)
5. Fit Scores: Pain intensity, WTP, accessibility, product fit (0-100)

Business Context: {foundation_summary}
Market Research: {market_research}

Generate {num_profiles} specific ICPs."""

async def icp_architect_node(state):
    llm = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.7, max_tokens=4000)
    profiles = await (ICP_PROMPT | llm.with_structured_output(list[ICPProfile])).ainvoke(state)
    state["step_data"]["icp_profiles"] = [p.model_dump() for p in profiles]
    return state
```

### Market Researcher Agent

```python
MARKET_RESEARCHER_PROMPT = """You find REAL customer insights from actual sources.

1. Customer pain points from reviews, forums, social media
2. ACTUAL language customers use (not marketing speak)
3. Desires and objections
4. Competitors: 3 direct, 2 indirect, 1 status-quo

Tools available: web_search, scrape_reviews, scrape_social, scrape_website

Business: {foundation_summary}
Industry: {industry}

Be thorough. Use real evidence. Cite sources."""

def create_market_researcher():
    from langgraph.prebuilt import create_react_agent

    llm = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.3, max_tokens=8000)
    tools = [web_search_tool, scrape_reviews_tool, scrape_social_tool, scrape_website_tool]

    return create_react_agent(llm, tools, state_modifier=MARKET_RESEARCHER_PROMPT)
```

---

## 2. MOVES GENERATOR

```python
class DailyTask(BaseModel):
    id: str
    title: str
    description: str
    type: Literal["pillar", "story", "engagement", "outreach", "admin"]
    platform: str | None
    estimated_minutes: int
    priority: Literal["must-do", "should-do", "nice-to-have"]
    deliverable: str

class ExecutionDay(BaseModel):
    day: int
    date: str
    theme: str
    tasks: list[DailyTask]
    total_minutes: int

class Move(BaseModel):
    id: str
    name: str
    category: Literal["ignite", "capture", "authority", "repair", "rally"]
    goal: str
    duration_days: int
    target_icp: str
    channels: list[str]
    execution: list[ExecutionDay]
    success_metrics: list[str]
    contingencies: dict[str, str]  # What if day missed?

MOVES_PROMPT = """You create DETAILED marketing execution plans.

A Move is NOT:
- "Post on Instagram"
- Generic advice

A Move IS:
- 7-day battle plan with specific daily tasks
- Pillar: "Create high-contrast hero image"
- Story: "Poll audience about X"
- Engagement: "DM 5 warm prospects"
- Clear time estimates

CRITICAL: If Day 7 missed, don't just say "Do Day 8".
1. Acknowledge gap
2. Suggest adaptation
3. Maintain coherence

Foundation: {foundation_summary}
ICPs: {icps}
Brand Voice: {brand_voice}

Request:
- Category: {category}
- Goal: {goal}
- Time: {time_commitment}/day
- Duration: {duration} days"""

async def moves_generator_node(state):
    llm = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.7, max_tokens=8000)
    move = await (MOVES_PROMPT | llm.with_structured_output(Move)).ainvoke(state["request_data"])
    state["final_output"] = move.model_dump()
    return state
```

---

## 3. BLACKBOX STRATEGY ENGINE

```python
BLACKBOX_SKILLS = {
    "acquisition": ["cold_outreach_optimizer", "lead_magnet_designer", "funnel_architect"],
    "retention": ["churn_predictor", "engagement_optimizer", "loyalty_designer"],
    "revenue": ["pricing_optimizer", "upsell_strategist", "ltv_maximizer"],
    "brand_equity": ["positioning_refiner", "thought_leadership_builder", "pr_strategist"],
    "virality": ["viral_loop_designer", "content_amplifier", "trend_surfer"]
}

RISK_LEVELS = {
    1: "Zero downside. Guaranteed small win.",
    5: "Balanced risk/reward. Standard play.",
    8: "Experimental. Unpredictable.",
    10: "Career-defining. Burn the boats."
}

class BlackBoxStrategy(BaseModel):
    id: str
    name: str
    focus_area: Literal["acquisition", "retention", "revenue", "brand_equity", "virality"]
    risk_level: int
    phases: list[dict]  # Hook, Pivot, Close
    execution_steps: list[str]
    expected_upside: str
    potential_downside: str
    time_to_result: str

BLACKBOX_PROMPT = """You generate HIGH-RISK, HIGH-REWARD strategic plays.

BlackBox is for:
- Pattern breaks that catch attention
- Contrarian moves competitors won't expect
- Calculated risks with asymmetric upside

Focus: {focus_area}
Outcome: {outcome}
Risk: {risk_level}/10 - {risk_guidance}

Foundation: {foundation_summary}
Current Trends: {current_trends}
Skills: {available_skills}

Generate strategy with:
1. Compelling name
2. 3 phases (Hook, Pivot, Close)
3. Execution steps
4. Risk/reward analysis"""

async def blackbox_engine_node(state):
    request = state["request_data"]
    focus = request.get("focus_area", "acquisition")

    # Search trends first
    trends = await search_current_trends(focus, state["foundation_summary"])

    llm = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.8, max_tokens=6000)
    strategy = await (BLACKBOX_PROMPT | llm.with_structured_output(BlackBoxStrategy)).ainvoke({
        **request,
        "current_trends": trends,
        "available_skills": BLACKBOX_SKILLS[focus],
        "risk_guidance": RISK_LEVELS.get(request.get("risk_level", 5))
    })

    state["final_output"] = strategy.model_dump()
    return state
```

---

## 4. DAILY WINS ENGINE

```python
class DailyWin(BaseModel):
    id: str
    topic: str
    angle: str
    hook: str
    outline: list[str]
    platform: str
    time_to_post: str
    trend_source: str
    relevance_score: float

DAILY_WINS_PROMPT = """Find QUICK CONTENT WINS that are:
1. Timely - Current events, trends
2. Relevant - Connected to user's business
3. Fast - <10 minutes to post
4. Effective - Predicted to perform

Search for:
- Trending topics in industry
- News affecting customers
- Viral patterns to adapt
- Calendar opportunities

Foundation: {foundation_summary}
ICPs: {icps}
Date: {current_date}
Recent Moves: {recent_moves}

Generate 3 Daily Wins."""

async def daily_wins_engine_node(state):
    # Multi-search for trends
    searches = await multi_search([
        f"{state['foundation_summary'][:200]} news",
        f"{state['icps'][0]['name']} trending",
        "viral marketing today"
    ])

    llm = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.7, max_tokens=3000)
    wins = await (DAILY_WINS_PROMPT | llm.with_structured_output(list[DailyWin])).ainvoke({
        **state,
        "search_results": searches,
        "current_date": datetime.now().strftime("%B %d, %Y")
    })

    state["final_output"] = {"wins": [w.model_dump() for w in wins[:3]]}
    return state
```

---

## 5. MUSE CREATIVE ENGINE

```python
class MuseAsset(BaseModel):
    id: str
    title: str
    type: Literal["email", "social", "script", "blog", "ad", "carousel"]
    content: str
    tone: str
    word_count: int
    suggestions: list[str]

MUSE_PROMPT = """You are Muse, a senior copywriter who generates HIGH-CONVERTING content.

You are NOT generic AI. You:
- Use user's brand voice consistently
- Reference specific ICPs and pain points
- Apply frameworks (PAS, AIDA)
- Write in customer's language

Foundation: {foundation_summary}
ICPs: {icps}
Brand Voice: {brand_voice}
Guardrails: {guardrails}
Soundbites: {soundbites}

Request:
Type: {content_type}
Topic: {topic}
Platform: {platform}"""

async def muse_engine_node(state):
    request = state["request_data"]

    llm = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.7, max_tokens=4000)
    asset = await (MUSE_PROMPT | llm.with_structured_output(MuseAsset)).ainvoke({
        **state,
        **request
    })

    state["final_output"] = asset.model_dump()
    return state
```

---

## 6. CAMPAIGN PLANNER

```python
class CampaignPhase(BaseModel):
    number: int
    name: str
    duration_weeks: int
    moves: list[str]
    success_criteria: list[str]

class Campaign(BaseModel):
    id: str
    name: str
    objective: str  # Market Entry, Revenue Scaling, etc.
    duration_days: int
    intensity: Literal["sprint", "marathon"]
    target_icp: str
    channels: list[str]
    phases: list[CampaignPhase]
    success_metrics: list[str]

CAMPAIGN_PROMPT = """Design STRATEGIC CAMPAIGNS bundling Moves into initiatives.

A Campaign has:
1. Strategic objective
2. 30-90 day span
3. Multiple coordinated Moves
4. Clear phases with milestones
5. Resource planning

Foundation: {foundation_summary}
ICPs: {icps}

Request:
- Objective: {objective}
- Duration: {duration}
- Intensity: {intensity}
- Channels: {channels}"""

async def campaigns_agent_node(state):
    llm = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.6, max_tokens=8000)
    campaign = await (CAMPAIGN_PROMPT | llm.with_structured_output(Campaign)).ainvoke(state["request_data"])
    state["final_output"] = campaign.model_dump()
    return state
```
