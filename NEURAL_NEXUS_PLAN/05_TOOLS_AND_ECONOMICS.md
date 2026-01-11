# PHASE 5: TOOL REGISTRY & PHASE 7: ECONOMICS ENGINE

---

## 5.1 Tool Registry

```python
# backend/tools/registry.py
from typing import Dict, Any, List, Callable, Optional
from pydantic import BaseModel
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of a tool for LLM consumption."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    required_params: List[str] = []
    cost_per_call: float = 0.0
    requires_approval: bool = False
    rate_limit: Optional[int] = None  # Calls per minute


class ToolResult(BaseModel):
    """Result from tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    cost: float = 0.0
    execution_time_ms: float = 0.0


def tool(
    name: str,
    description: str,
    cost_per_call: float = 0.0,
    requires_approval: bool = False,
    rate_limit: int = None
):
    """
    Decorator to register a function as a tool.

    Usage:
        @tool(name="web_search", description="Search the web", cost_per_call=0.005)
        async def web_search(query: str, num_results: int = 10) -> dict:
            ...
    """
    def decorator(func: Callable):
        # Extract parameter schema from function signature
        import inspect
        sig = inspect.signature(func)

        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"
                elif param.annotation == dict:
                    param_type = "object"

            parameters["properties"][param_name] = {"type": param_type}

            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)

        # Create tool definition
        tool_def = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            required_params=parameters["required"],
            cost_per_call=cost_per_call,
            requires_approval=requires_approval,
            rate_limit=rate_limit
        )

        @wraps(func)
        async def wrapper(*args, **kwargs):
            import time
            start = time.time()

            try:
                result = await func(*args, **kwargs)
                return ToolResult(
                    success=True,
                    data=result,
                    cost=cost_per_call,
                    execution_time_ms=(time.time() - start) * 1000
                )
            except Exception as e:
                logger.error(f"Tool {name} failed: {e}")
                return ToolResult(
                    success=False,
                    error=str(e),
                    cost=cost_per_call * 0.5,  # Partial cost for failed calls
                    execution_time_ms=(time.time() - start) * 1000
                )

        wrapper._tool_definition = tool_def
        return wrapper

    return decorator


class ToolRegistry:
    """
    Central registry for all available tools.
    """

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._definitions: Dict[str, ToolDefinition] = {}

    def register(self, func: Callable):
        """Register a tool function."""
        if not hasattr(func, '_tool_definition'):
            raise ValueError(f"Function {func.__name__} is not decorated with @tool")

        tool_def = func._tool_definition
        self._tools[tool_def.name] = func
        self._definitions[tool_def.name] = tool_def

        logger.info(f"Registered tool: {tool_def.name}")

    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_tools(self, names: List[str]) -> List[Callable]:
        """Get multiple tools by name."""
        return [self._tools[n] for n in names if n in self._tools]

    def get_definition(self, name: str) -> Optional[ToolDefinition]:
        """Get tool definition for LLM."""
        return self._definitions.get(name)

    def get_all_definitions(self) -> List[ToolDefinition]:
        """Get all tool definitions."""
        return list(self._definitions.values())

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())


# Singleton
tool_registry = ToolRegistry()
```

---

## 5.2 Core Tools

```python
# backend/tools/search/web_search.py
from tools.registry import tool, ToolResult
from core.resilience import get_circuit_breaker
import aiohttp
import logging

logger = logging.getLogger(__name__)


@tool(
    name="web_search",
    description="Search the web using Google. Returns titles, snippets, and URLs.",
    cost_per_call=0.005,
    rate_limit=60
)
async def web_search(query: str, num_results: int = 10) -> dict:
    """
    Search the web using Google Custom Search API.
    """
    from core.config import get_settings
    settings = get_settings()

    circuit = get_circuit_breaker("google_search")

    async def _search():
        async with aiohttp.ClientSession() as session:
            params = {
                "key": settings.GOOGLE_SEARCH_API_KEY,
                "cx": settings.GOOGLE_SEARCH_ENGINE_ID,
                "q": query,
                "num": min(num_results, 10)
            }

            async with session.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params
            ) as response:
                data = await response.json()

                results = []
                for item in data.get("items", []):
                    results.append({
                        "title": item.get("title"),
                        "snippet": item.get("snippet"),
                        "url": item.get("link")
                    })

                return {"results": results, "total": len(results)}

    return await circuit.call(_search)


@tool(
    name="news_search",
    description="Search recent news articles on a topic.",
    cost_per_call=0.003,
    rate_limit=30
)
async def news_search(query: str, days: int = 7) -> dict:
    """
    Search recent news using News API or Google News.
    """
    # Implementation
    pass
```

```python
# backend/tools/scrapers/generic_scraper.py
from tools.registry import tool
from core.resilience import get_circuit_breaker
import aiohttp
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


@tool(
    name="scraper",
    description="Scrape content from a URL. Extracts text, links, and structured data.",
    cost_per_call=0.01,
    rate_limit=30
)
async def scrape_url(
    url: str,
    extract: list = None,  # ["pricing", "features", "team"]
    max_length: int = 10000
) -> dict:
    """
    Scrape and extract content from a URL.
    """
    circuit = get_circuit_breaker("scraper")

    async def _scrape():
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RaptorflowBot/1.0)"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=30) as response:
                html = await response.text()

                soup = BeautifulSoup(html, 'html.parser')

                # Remove scripts and styles
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()

                # Extract main content
                main_content = soup.find('main') or soup.find('article') or soup.body

                text = main_content.get_text(separator='\n', strip=True) if main_content else ""
                text = text[:max_length]

                # Extract specific sections if requested
                extracted = {}
                if extract:
                    for section in extract:
                        extracted[section] = _extract_section(soup, section)

                return {
                    "url": url,
                    "title": soup.title.string if soup.title else "",
                    "text": text,
                    "extracted": extracted,
                    "links": [a.get('href') for a in soup.find_all('a', href=True)][:20]
                }

    return await circuit.call(_scrape)


def _extract_section(soup, section_type: str) -> dict:
    """Extract specific section types from HTML."""
    if section_type == "pricing":
        # Look for pricing-related content
        pricing_keywords = ['price', 'pricing', 'plan', 'tier', 'cost']
        for keyword in pricing_keywords:
            elements = soup.find_all(class_=lambda x: x and keyword in x.lower())
            if elements:
                return {"found": True, "content": [e.get_text() for e in elements[:5]]}
        return {"found": False}

    elif section_type == "features":
        features_keywords = ['feature', 'benefit', 'capability']
        for keyword in features_keywords:
            elements = soup.find_all(class_=lambda x: x and keyword in x.lower())
            if elements:
                return {"found": True, "content": [e.get_text() for e in elements[:10]]}
        return {"found": False}

    return {"found": False}
```

```python
# backend/tools/scrapers/vision_scraper.py
from tools.registry import tool
import base64
import aiohttp
import logging

logger = logging.getLogger(__name__)


@tool(
    name="vision_scraper",
    description="Take a screenshot of a URL and analyze it visually using AI. Use when CSS selectors fail.",
    cost_per_call=0.02,
    rate_limit=10
)
async def vision_scrape(url: str, question: str = "Describe this page") -> dict:
    """
    Screenshot a page and analyze it with vision model.
    Fallback for when traditional scraping fails.
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(url, wait_until="networkidle")

        # Take screenshot
        screenshot = await page.screenshot(full_page=False)
        screenshot_b64 = base64.b64encode(screenshot).decode()

        await browser.close()

    # Analyze with vision model
    from agents.model_client import model_client

    response = await model_client.generate_with_vision(
        model="gemini-2.0-flash",
        image_base64=screenshot_b64,
        prompt=question
    )

    return {
        "url": url,
        "analysis": response.get("content", ""),
        "screenshot_available": True
    }
```

---

## 5.3 Indian Market Tools

```python
# backend/tools/indian/justdial_scraper.py
from tools.registry import tool
from core.resilience import get_circuit_breaker
import aiohttp
import logging

logger = logging.getLogger(__name__)


@tool(
    name="justdial_search",
    description="Search JustDial for local Indian businesses. Returns business names, phones, ratings.",
    cost_per_call=0.015,
    rate_limit=10  # JustDial is strict
)
async def justdial_search(
    query: str,
    city: str,
    max_results: int = 20
) -> dict:
    """
    Search JustDial for local businesses.

    Args:
        query: Business type (e.g., "restaurants", "plumbers")
        city: Indian city name
        max_results: Maximum results to return
    """
    circuit = get_circuit_breaker("justdial")

    async def _search():
        # JustDial doesn't have a public API, so we scrape carefully
        # In production, consider official partnerships

        url = f"https://www.justdial.com/{city}/{query.replace(' ', '-')}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                html = await response.text()

                # Parse results (simplified)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')

                results = []
                listings = soup.find_all('li', class_='cntanr')[:max_results]

                for listing in listings:
                    name_elem = listing.find('span', class_='lng_cont_name')
                    rating_elem = listing.find('span', class_='green-box')

                    results.append({
                        "name": name_elem.get_text() if name_elem else "Unknown",
                        "rating": rating_elem.get_text() if rating_elem else "N/A",
                        "city": city
                    })

                return {
                    "query": query,
                    "city": city,
                    "results": results,
                    "total": len(results)
                }

    return await circuit.call(_search)


@tool(
    name="indiamart_search",
    description="Search IndiaMART for B2B suppliers and manufacturers.",
    cost_per_call=0.02,
    rate_limit=10
)
async def indiamart_search(
    product: str,
    location: str = None,
    max_results: int = 20
) -> dict:
    """
    Search IndiaMART for B2B suppliers.
    """
    # Similar implementation to JustDial
    pass


@tool(
    name="gst_calculator",
    description="Calculate GST for Indian transactions. Returns CGST, SGST, or IGST breakdown.",
    cost_per_call=0.0  # Free, local calculation
)
async def calculate_gst(
    amount: float,
    gst_rate: float,  # 5, 12, 18, or 28
    is_interstate: bool = False,
    seller_state: str = None,
    buyer_state: str = None
) -> dict:
    """
    Calculate GST breakdown for Indian transactions.

    Args:
        amount: Base amount in INR (before GST)
        gst_rate: GST rate (5, 12, 18, or 28)
        is_interstate: True for inter-state, False for intra-state
        seller_state: Seller's state (for IGST calculation)
        buyer_state: Buyer's state (for IGST calculation)
    """
    gst_amount = amount * (gst_rate / 100)

    if is_interstate or (seller_state and buyer_state and seller_state != buyer_state):
        # IGST for inter-state
        return {
            "base_amount": amount,
            "gst_rate": gst_rate,
            "igst": round(gst_amount, 2),
            "cgst": 0,
            "sgst": 0,
            "total_gst": round(gst_amount, 2),
            "total_amount": round(amount + gst_amount, 2),
            "type": "IGST"
        }
    else:
        # CGST + SGST for intra-state
        half_gst = gst_amount / 2
        return {
            "base_amount": amount,
            "gst_rate": gst_rate,
            "igst": 0,
            "cgst": round(half_gst, 2),
            "sgst": round(half_gst, 2),
            "total_gst": round(gst_amount, 2),
            "total_amount": round(amount + gst_amount, 2),
            "type": "CGST+SGST"
        }
```

---

## 7.1 Cost Predictor

```python
# backend/economics/cost_predictor.py
from typing import Dict, Any
import logging

from skills.registry import skill_registry

logger = logging.getLogger(__name__)


class CostPredictor:
    """
    Predicts execution cost BEFORE running.
    Accounts for: LLM tokens, tool calls, retries.
    """

    MODEL_COSTS = {
        # Cost per 1K tokens (input + output average)
        "gemini-2.0-flash-lite": 0.000025,
        "gemini-2.0-flash": 0.000075,
        "gemini-2.0-pro": 0.00015,
        "gemini-2.0-ultra": 0.0003,
    }

    TOOL_COSTS = {
        "web_search": 0.005,
        "news_search": 0.003,
        "scraper": 0.01,
        "vision_scraper": 0.02,
        "justdial_search": 0.015,
        "indiamart_search": 0.02,
        "gst_calculator": 0.0,
        "database_writer": 0.001,
    }

    def __init__(self, execution_history=None):
        self.history = execution_history

    async def predict(
        self,
        skill_id: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict cost for a skill execution.

        Returns:
            {
                "estimated_cost": 0.05,
                "breakdown": {...},
                "confidence": "HIGH|MEDIUM|LOW"
            }
        """
        skill = skill_registry.get_skill(skill_id)
        if not skill:
            return {"estimated_cost": 0.10, "confidence": "LOW"}

        # Base LLM cost
        input_tokens = self._estimate_input_tokens(skill, inputs)
        output_tokens = self._estimate_output_tokens(skill)

        model = skill.config.model_primary
        cost_per_1k = self.MODEL_COSTS.get(model, 0.0001)

        llm_cost = ((input_tokens + output_tokens) / 1000) * cost_per_1k

        # Tool costs
        tool_cost = 0.0
        for tool_name in skill.config.required_tools:
            calls = self._estimate_tool_calls(tool_name, skill)
            tool_cost += self.TOOL_COSTS.get(tool_name, 0.01) * calls

        # Retry buffer (based on historical retry rate)
        retry_rate = await self._get_retry_rate(skill_id)
        retry_buffer = (llm_cost + tool_cost) * retry_rate * 0.5

        total = llm_cost + tool_cost + retry_buffer

        return {
            "estimated_cost": round(total, 4),
            "estimated_cost_inr": round(total * 83, 2),  # USD to INR
            "breakdown": {
                "llm_cost": round(llm_cost, 4),
                "tool_cost": round(tool_cost, 4),
                "retry_buffer": round(retry_buffer, 4)
            },
            "estimated_tokens": input_tokens + output_tokens,
            "confidence": self._get_confidence(retry_rate)
        }

    def _estimate_input_tokens(self, skill, inputs: Dict) -> int:
        """Estimate input tokens."""
        # Skill prompt
        prompt_tokens = len(skill.system_prompt.split()) * 1.3

        # Inputs
        input_text = str(inputs)
        input_tokens = len(input_text.split()) * 1.3

        # Foundation context (typical)
        context_tokens = 2000

        return int(prompt_tokens + input_tokens + context_tokens)

    def _estimate_output_tokens(self, skill) -> int:
        """Estimate output tokens based on schema."""
        return skill.config.max_tokens // 2  # Usually use about half

    def _estimate_tool_calls(self, tool_name: str, skill) -> int:
        """Estimate number of tool calls."""
        # Heuristics based on tool type
        estimates = {
            "web_search": 2,
            "scraper": 1,
            "vision_scraper": 1,
            "database_writer": 1,
            "justdial_search": 1,
            "indiamart_search": 1,
            "news_search": 1,
        }
        return estimates.get(tool_name, 1)

    async def _get_retry_rate(self, skill_id: str) -> float:
        """Get historical retry rate for a skill."""
        if self.history:
            return await self.history.get_retry_rate(skill_id)
        return 0.1  # Default 10% retry rate

    def _get_confidence(self, retry_rate: float) -> str:
        """Get confidence level based on retry rate."""
        if retry_rate < 0.1:
            return "HIGH"
        elif retry_rate < 0.3:
            return "MEDIUM"
        return "LOW"


# Singleton
cost_predictor = CostPredictor()
```

---

## 7.2 Budget Enforcer

```python
# backend/economics/budget_enforcer.py
from typing import Dict, Any
from datetime import datetime
import logging

from core.redis_client import redis_client
from core.database import async_session_maker

logger = logging.getLogger(__name__)


class BudgetEnforcer:
    """
    Enforces user budgets and prevents runaway costs.

    Features:
    - Pre-execution budget check
    - Budget reservation (prevents race conditions)
    - Real-time usage tracking
    - Alerts at thresholds
    """

    ALERT_THRESHOLDS = [0.5, 0.75, 0.9, 1.0]  # 50%, 75%, 90%, 100%

    async def check_budget(
        self,
        user_id: str,
        estimated_cost: float
    ) -> Dict[str, Any]:
        """
        Check if user can afford the estimated cost.
        """
        # Get user's subscription tier and budget
        user_budget = await self._get_user_budget(user_id)

        # Get current month's usage
        current_usage = await self._get_monthly_usage(user_id)

        remaining = user_budget - current_usage
        can_afford = remaining >= estimated_cost
        percentage_used = (current_usage / user_budget) * 100 if user_budget > 0 else 0

        # Check if we need to send alerts
        await self._check_alerts(user_id, percentage_used)

        return {
            "can_afford": can_afford,
            "remaining_budget": round(remaining, 4),
            "remaining_budget_inr": round(remaining * 83, 2),
            "current_usage": round(current_usage, 4),
            "monthly_budget": user_budget,
            "percentage_used": round(percentage_used, 1),
            "estimated_cost": estimated_cost
        }

    async def reserve_budget(
        self,
        user_id: str,
        execution_id: str,
        amount: float
    ):
        """
        Reserve budget for an execution (pre-authorization).
        Prevents concurrent executions from exceeding budget.
        """
        reserve_key = f"budget_reserve:{user_id}:{execution_id}"
        await redis_client.set(reserve_key, str(amount), ex=3600)  # 1 hour TTL

        # Add to total reserved
        await redis_client.get_client()
        client = await redis_client.get_client()
        await client.incrbyfloat(f"budget_reserved:{user_id}", amount)

    async def finalize_cost(
        self,
        user_id: str,
        execution_id: str,
        actual_cost: float
    ):
        """
        Finalize cost after execution completes.
        """
        # Get reserved amount
        reserve_key = f"budget_reserve:{user_id}:{execution_id}"
        reserved = await redis_client.get(reserve_key)
        reserved_amount = float(reserved) if reserved else 0

        # Remove reservation
        await redis_client.delete(reserve_key)

        # Decrease total reserved
        client = await redis_client.get_client()
        await client.incrbyfloat(f"budget_reserved:{user_id}", -reserved_amount)

        # Record actual usage
        await self._record_usage(user_id, actual_cost, execution_id)

    async def get_usage_report(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed usage report for a user.
        """
        current_usage = await self._get_monthly_usage(user_id)
        daily_usage = await self._get_daily_usage(user_id)
        user_budget = await self._get_user_budget(user_id)

        return {
            "monthly_usage": round(current_usage, 4),
            "monthly_usage_inr": round(current_usage * 83, 2),
            "monthly_budget": user_budget,
            "monthly_budget_inr": round(user_budget * 83, 2),
            "daily_average": round(current_usage / max(datetime.now().day, 1), 4),
            "daily_breakdown": daily_usage,
            "projected_monthly": round((current_usage / max(datetime.now().day, 1)) * 30, 4)
        }

    async def _get_user_budget(self, user_id: str) -> float:
        """Get user's monthly budget based on subscription tier."""
        # Default budgets per tier (in USD)
        tier_budgets = {
            "free": 1.0,
            "starter": 10.0,
            "growth": 50.0,
            "agency": 200.0,
            "enterprise": float('inf')
        }

        async with async_session_maker() as session:
            result = await session.execute(
                "SELECT subscription_tier FROM users WHERE id = :user_id",
                {"user_id": user_id}
            )
            row = result.fetchone()
            tier = row["subscription_tier"] if row else "free"

        return tier_budgets.get(tier, 1.0)

    async def _get_monthly_usage(self, user_id: str) -> float:
        """Get current month's usage."""
        month_key = datetime.now().strftime("%Y-%m")
        usage_key = f"usage:{user_id}:{month_key}"

        usage = await redis_client.get(usage_key)
        return float(usage) if usage else 0.0

    async def _get_daily_usage(self, user_id: str) -> Dict[str, float]:
        """Get daily usage breakdown for current month."""
        # Implementation
        return {}

    async def _record_usage(
        self,
        user_id: str,
        amount: float,
        execution_id: str
    ):
        """Record usage in Redis and database."""
        month_key = datetime.now().strftime("%Y-%m")
        day_key = datetime.now().strftime("%Y-%m-%d")

        # Increment monthly usage
        client = await redis_client.get_client()
        await client.incrbyfloat(f"usage:{user_id}:{month_key}", amount)

        # Increment daily usage
        await client.incrbyfloat(f"usage:{user_id}:{day_key}", amount)

        # Persist to database
        async with async_session_maker() as session:
            await session.execute(
                """
                INSERT INTO usage_records (user_id, execution_id, amount, recorded_at)
                VALUES (:user_id, :execution_id, :amount, NOW())
                """,
                {"user_id": user_id, "execution_id": execution_id, "amount": amount}
            )
            await session.commit()

    async def _check_alerts(self, user_id: str, percentage_used: float):
        """Send alerts at budget thresholds."""
        for threshold in self.ALERT_THRESHOLDS:
            threshold_pct = threshold * 100
            if percentage_used >= threshold_pct:
                alert_key = f"budget_alert:{user_id}:{threshold}"

                # Check if already alerted
                already_sent = await redis_client.exists(alert_key)
                if not already_sent:
                    # Send alert
                    await self._send_budget_alert(user_id, threshold_pct)

                    # Mark as sent (expires at month end)
                    days_remaining = 30 - datetime.now().day
                    await redis_client.set(alert_key, "1", ex=days_remaining * 86400)


# Singleton
budget_enforcer = BudgetEnforcer()
```

---

## 7.3 Semantic Cache

```python
# backend/economics/semantic_cache.py
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np
import json
import logging

from core.redis_client import redis_client

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Cache query results based on semantic similarity.

    Why?
    - "Competitors of Nike" ≈ "Nike competitors" → Same result
    - Saves 10x cost on similar queries

    How?
    - Embed queries and compare similarity
    - If similarity > threshold, return cached result
    """

    DEFAULT_THRESHOLD = 0.92  # 92% similarity
    DEFAULT_TTL = 3600  # 1 hour
    MAX_CACHE_SIZE = 100  # Per skill

    def __init__(self):
        self.embedder = None

    async def initialize(self, embedder):
        self.embedder = embedder

    async def get(
        self,
        user_id: str,
        skill_id: str,
        query: str,
        threshold: float = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a semantically similar query was already executed.

        Returns:
            Cache hit with result, or None
        """
        threshold = threshold or self.DEFAULT_THRESHOLD

        # Generate query embedding
        query_embedding = await self.embedder.embed(query)

        # Get cached entries for this user+skill
        cache_key = f"semantic_cache:{user_id}:{skill_id}"
        entries_json = await redis_client.get(cache_key)

        if not entries_json:
            return None

        entries = json.loads(entries_json)

        # Find best match
        best_match = None
        best_similarity = 0.0

        for entry in entries:
            cached_embedding = np.array(entry["embedding"])

            similarity = self._cosine_similarity(
                query_embedding,
                cached_embedding
            )

            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = entry

        if best_match:
            logger.info(
                f"Cache HIT: {skill_id} (similarity: {best_similarity:.3f})"
            )
            return {
                "hit": True,
                "similarity": best_similarity,
                "result": best_match["result"],
                "cached_at": best_match["cached_at"],
                "original_query": best_match["query"]
            }

        return None

    async def set(
        self,
        user_id: str,
        skill_id: str,
        query: str,
        result: Dict[str, Any],
        ttl: int = None
    ):
        """
        Cache a result with its embedding.
        """
        ttl = ttl or self.DEFAULT_TTL

        # Generate embedding
        query_embedding = await self.embedder.embed(query)

        # Create entry
        entry = {
            "query": query,
            "embedding": query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding,
            "result": result,
            "cached_at": datetime.utcnow().isoformat()
        }

        # Get existing cache
        cache_key = f"semantic_cache:{user_id}:{skill_id}"
        entries_json = await redis_client.get(cache_key)
        entries = json.loads(entries_json) if entries_json else []

        # Add new entry
        entries.insert(0, entry)

        # Enforce size limit
        entries = entries[:self.MAX_CACHE_SIZE]

        # Save
        await redis_client.set(cache_key, json.dumps(entries), ex=ttl)

        logger.debug(f"Cached result for {skill_id}: {query[:50]}...")

    async def invalidate(self, user_id: str, skill_id: str = None):
        """
        Invalidate cache for a user (or specific skill).
        """
        if skill_id:
            await redis_client.delete(f"semantic_cache:{user_id}:{skill_id}")
        else:
            # Invalidate all skills for user
            client = await redis_client.get_client()
            keys = await client.keys(f"semantic_cache:{user_id}:*")
            if keys:
                await client.delete(*keys)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# Singleton
semantic_cache = SemanticCache()
```
