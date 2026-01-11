# TOOLS AND INFRASTRUCTURE

---

## 1. TOOL REGISTRY

### Web Search Tools

```python
from langchain_core.tools import tool
from typing import Annotated

@tool
async def web_search(
    query: Annotated[str, "Search query"],
    num_results: Annotated[int, "Number of results"] = 10
) -> list[dict]:
    """Search web using Google Custom Search (free: 100/day)."""
    from googleapiclient.discovery import build

    service = build("customsearch", "v1", developerKey=os.getenv("GOOGLE_API_KEY"))
    result = service.cse().list(q=query, cx=os.getenv("GOOGLE_CSE_ID"), num=num_results).execute()

    return [{"title": i["title"], "link": i["link"], "snippet": i["snippet"]}
            for i in result.get("items", [])]

@tool
async def news_search(
    query: Annotated[str, "News query"],
    days_back: Annotated[int, "Days to search"] = 7
) -> list[dict]:
    """Search recent news articles."""
    # Use NewsAPI or Google News RSS
    pass
```

### Scraping Tools

```python
@tool
async def scrape_website(
    url: Annotated[str, "URL to scrape"],
    extract: Annotated[str, "What: text, links, structured"] = "text"
) -> dict:
    """Scrape website content."""
    import httpx
    from bs4 import BeautifulSoup

    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        return {"url": url, "text": soup.get_text(separator="\n", strip=True)[:10000]}

@tool
async def scrape_reviews(
    product: Annotated[str, "Product name"],
    platforms: Annotated[list[str], "g2, capterra, trustradius"] = ["g2"]
) -> list[dict]:
    """Scrape product reviews."""
    # Implementation for G2, Capterra
    pass

@tool
async def scrape_social(
    query: Annotated[str, "Search query"],
    platform: Annotated[str, "reddit, twitter, linkedin"] = "reddit"
) -> list[dict]:
    """Scrape social discussions."""
    pass
```

### Indian Market Tools

```python
@tool
async def scrape_justdial(
    category: Annotated[str, "Business category"],
    location: Annotated[str, "City"]
) -> list[dict]:
    """Scrape JustDial for Indian business listings."""
    pass

@tool
async def scrape_indiamart(
    product: Annotated[str, "Product/service"]
) -> list[dict]:
    """Scrape IndiaMart for B2B listings."""
    pass

@tool
async def calculate_gst(
    amount: Annotated[float, "Base amount INR"],
    seller_state: Annotated[str, "Seller state"],
    buyer_state: Annotated[str, "Buyer state"]
) -> dict:
    """Calculate GST (CGST, SGST, IGST)."""
    GST_RATE = 0.18

    if seller_state == buyer_state:
        cgst = sgst = amount * (GST_RATE / 2)
        return {"cgst": cgst, "sgst": sgst, "igst": 0, "total": amount + cgst + sgst}
    else:
        igst = amount * GST_RATE
        return {"cgst": 0, "sgst": 0, "igst": igst, "total": amount + igst}
```

### File Processing Tools

```python
@tool
async def process_pdf(file_path: Annotated[str, "PDF path"]) -> dict:
    """Extract text from PDF."""
    import fitz

    doc = fitz.open(file_path)
    text = "".join(page.get_text() for page in doc)
    return {"text": text[:50000], "pages": len(doc)}

@tool
async def process_image_ocr(file_path: Annotated[str, "Image path"]) -> dict:
    """Extract text from image using Vertex AI Vision."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()
    with open(file_path, "rb") as f:
        image = vision.Image(content=f.read())

    response = client.text_detection(image=image)
    return {"text": response.text_annotations[0].description if response.text_annotations else ""}
```

### Database Tools

```python
@tool
async def get_foundation(user_id: Annotated[str, "User ID"]) -> dict:
    """Get user's Foundation data."""
    supabase = get_supabase_client()
    return supabase.table("foundations").select("*").eq("user_id", user_id).single().execute().data or {}

@tool
async def get_icps(user_id: Annotated[str, "User ID"]) -> list[dict]:
    """Get user's ICP profiles."""
    supabase = get_supabase_client()
    return supabase.table("icp_profiles").select("*").eq("user_id", user_id).execute().data or []

@tool
async def save_execution(
    user_id: Annotated[str, "User ID"],
    exec_type: Annotated[str, "move, campaign, muse, blackbox"],
    data: Annotated[dict, "Execution data"]
) -> dict:
    """Save agent execution result."""
    supabase = get_supabase_client()
    result = supabase.table("executions").insert({
        "user_id": user_id, "type": exec_type, "data": data
    }).execute()
    return {"id": result.data[0]["id"]}
```

---

## 2. FASTAPI APPLICATION

```python
# backend/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from agents.graph import create_raptorflow_graph

raptorflow_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global raptorflow_graph
    raptorflow_graph = create_raptorflow_graph()
    yield

app = FastAPI(title="Raptorflow Backend", version="5.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.raptorflow.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from api.v1 import agents, onboarding, moves, campaigns, muse, blackbox
app.include_router(agents.router, prefix="/api/v1/agents")
app.include_router(onboarding.router, prefix="/api/v1/onboarding")
app.include_router(moves.router, prefix="/api/v1/moves")
app.include_router(campaigns.router, prefix="/api/v1/campaigns")
app.include_router(muse.router, prefix="/api/v1/muse")
app.include_router(blackbox.router, prefix="/api/v1/blackbox")

@app.get("/health")
async def health():
    return {"status": "healthy", "graph": raptorflow_graph is not None}
```

---

## 3. API ENDPOINTS

```python
# backend/api/v1/agents.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class AgentRequest(BaseModel):
    request_type: str  # onboarding, moves, campaigns, muse, blackbox, daily_wins
    request_data: dict
    stream: bool = False

class AgentResponse(BaseModel):
    success: bool
    output: dict
    tokens_used: int
    cost: float

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(
    request: AgentRequest,
    user = Depends(get_current_user),
    foundation = Depends(get_foundation_context)
):
    """Execute agent through LangGraph."""

    initial_state = {
        "user_id": user.id,
        "workspace_id": user.workspace_id,
        "request_type": request.request_type,
        "request_data": request.request_data,
        "foundation_summary": foundation.get("summary", ""),
        "icps": foundation.get("icps", []),
        "brand_voice": foundation.get("brand_voice", "professional"),
        "messages": [],
        "current_agent": "",
        "agent_outputs": {},
        "tokens_used": 0,
        "estimated_cost": 0.0,
        "budget_remaining": user.budget_remaining,
        "next_step": "",
        "requires_human_approval": False,
        "final_output": None
    }

    final_state = await raptorflow_graph.ainvoke(initial_state)

    return AgentResponse(
        success=final_state.get("final_output") is not None,
        output=final_state.get("final_output"),
        tokens_used=final_state.get("tokens_used", 0),
        cost=final_state.get("estimated_cost", 0.0)
    )
```

---

## 4. SUPABASE INTEGRATION

```python
# backend/core/database.py
from supabase import create_client, Client

_supabase: Client | None = None

def get_supabase_client() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
    return _supabase
```

---

## 5. UPSTASH REDIS

```python
# backend/core/redis.py
from upstash_redis import Redis

_redis: Redis | None = None

def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis(
            url=os.getenv("UPSTASH_REDIS_URL"),
            token=os.getenv("UPSTASH_REDIS_TOKEN")
        )
    return _redis

def cache(ttl: int = 3600):
    """Cache decorator."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            redis = get_redis()
            key = f"cache:{func.__name__}:{hash(str(args))}"
            cached = redis.get(key)
            if cached:
                return cached
            result = await func(*args, **kwargs)
            redis.setex(key, ttl, result)
            return result
        return wrapper
    return decorator
```

---

## 6. VERTEX AI CONFIG

```python
# backend/core/vertex.py
from langchain_google_vertexai import ChatVertexAI

MODELS = {
    "routing": {"name": "gemini-2.0-flash-lite", "max_tokens": 500, "temp": 0.1},
    "standard": {"name": "gemini-2.0-flash", "max_tokens": 8000, "temp": 0.7},
    "creative": {"name": "gemini-2.0-flash", "max_tokens": 8000, "temp": 0.9},
    "reasoning": {"name": "gemini-2.0-pro", "max_tokens": 16000, "temp": 0.3}
}

def get_llm(model_type: str = "standard") -> ChatVertexAI:
    config = MODELS.get(model_type, MODELS["standard"])
    return ChatVertexAI(
        model_name=config["name"],
        project=os.getenv("GCP_PROJECT_ID"),
        location="us-central1",
        temperature=config["temp"],
        max_tokens=config["max_tokens"]
    )
```

---

## 7. COST OPTIMIZATION

### Budget Enforcer

```python
class BudgetEnforcer:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def check_budget(self, user_id: str, estimated_cost: float) -> dict:
        key = f"usage:{user_id}:{datetime.now().strftime('%Y-%m')}"
        current = float(self.redis.get(key) or 0)
        limit = await self.get_user_budget_limit(user_id)
        remaining = limit - current

        return {
            "can_afford": remaining >= estimated_cost,
            "remaining": remaining,
            "estimated": estimated_cost
        }

    async def record_usage(self, user_id: str, cost: float):
        key = f"usage:{user_id}:{datetime.now().strftime('%Y-%m')}"
        self.redis.incrbyfloat(key, cost)
        self.redis.expire(key, 35 * 24 * 3600)
```

### Semantic Cache

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticCache:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = 0.92

    async def get_cached(self, user_id: str, query: str) -> dict | None:
        embedding = self.encoder.encode(query)
        cached = self.redis.hgetall(f"semantic:{user_id}")

        for key, data in cached.items():
            cached_emb = np.frombuffer(data["embedding"], dtype=np.float32)
            similarity = np.dot(embedding, cached_emb) / (
                np.linalg.norm(embedding) * np.linalg.norm(cached_emb)
            )
            if similarity >= self.threshold:
                return data["result"]
        return None

    async def cache_result(self, user_id: str, query: str, result: dict):
        embedding = self.encoder.encode(query)
        self.redis.hset(f"semantic:{user_id}", query[:100], {
            "embedding": embedding.tobytes(),
            "result": result
        })
```

---

## 8. DEPLOYMENT

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Run Config

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/raptorflow-backend', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/raptorflow-backend']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'raptorflow-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/raptorflow-backend'
      - '--region'
      - 'us-central1'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--min-instances'
      - '1'
      - '--max-instances'
      - '10'
```

### Environment Variables

```env
# GCP
GCP_PROJECT_ID=your-project
GCP_LOCATION=us-central1

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# Upstash Redis
UPSTASH_REDIS_URL=https://xxx.upstash.io
UPSTASH_REDIS_TOKEN=xxx

# Google Search (free tier)
GOOGLE_API_KEY=xxx
GOOGLE_CSE_ID=xxx
```
