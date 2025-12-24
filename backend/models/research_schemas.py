import operator
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ResearchHypothesis(BaseModel):
    statement: str
    confirmed: bool = False
    evidence_ids: List[str] = []
    contradiction_ids: List[str] = []


class WebDocument(BaseModel):
    url: HttpUrl
    title: str
    raw_content: str
    summary: str
    relevance_score: float
    published_date: Optional[str] = None
    author: Optional[str] = None


class FactClaim(BaseModel):
    id: str
    claim: str
    source_url: HttpUrl
    context_snippet: str
    confidence: float
    verification_status: str = "unverified"  # verified | debunked | conflicting


class ResearchDeepState(BaseModel):
    # Context
    workspace_id: str
    task_id: str
    objective: str

    # Brain State
    queries: List[str] = []
    hypotheses: List[ResearchHypothesis] = []
    documents: List[WebDocument] = []
    claims: List[FactClaim] = []

    # Progress
    depth: int = 0
    max_depth: int = 3
    research_logs: List[str] = []

    # Output
    final_report_md: str = ""
    citations: List[Dict[str, Any]] = []
    status: str = "initializing"


class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str
    source: str
