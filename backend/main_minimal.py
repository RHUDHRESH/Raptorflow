"""
Minimal RaptorFlow Backend - Just API Routes for Testing
"""

import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RaptorFlow Backend API",
    description="Minimal backend for testing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["strict-transport-security"] = "max-age=63072000; includeSubDomains; preload"
    return response

def build_health_payload():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "api": "running",
            "database": "mock",
            "redis": "mock"
        }
    }

@app.get("/health")
async def health_check():
    return build_health_payload()

@app.get("/api/v1/health")
async def api_health_check():
    return build_health_payload()

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "RaptorFlow Backend",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z",
        "endpoints": {
            "health": "/api/v1/health",
            "docs": "/docs",
            "agents": "/api/v1/agents",
            "auth": "/api/v1/auth"
        }
    }

class LoginRequest(BaseModel):
    email: str
    password: str

class UserProfileUpdate(BaseModel):
    full_name: str
    email: str
    preferences: Optional[Dict[str, Any]] = None

def is_authorized(request: Request) -> bool:
    auth_header = request.headers.get("authorization")
    return bool(auth_header and auth_header.lower().startswith("bearer "))

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    return {"access_token": "mock-token", "token_type": "bearer"}

@app.get("/api/v1/users/me")
async def get_user_me(request: Request):
    if not is_authorized(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "full_name": "Test User",
        "subscription_tier": "free"
    }

@app.post("/api/v1/users/me")
async def update_user_me(payload: UserProfileUpdate):
    return {
        "id": "test-user-id",
        "email": payload.email,
        "full_name": payload.full_name,
        "preferences": payload.preferences or {}
    }

@app.options("/api/v1/users/me")
async def users_me_options():
    return JSONResponse(
        content={},
        status_code=200,
        headers={
            "access-control-allow-origin": "*",
            "access-control-allow-methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "access-control-allow-headers": "Content-Type, Authorization, X-Requested-With"
        }
    )

# Mock onboarding endpoints
@app.post("/api/v1/onboarding/{session_id}/contradictions")
async def contradictions(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "contradictions": [
            {"id": "C-001", "description": "Feature X conflicts with pricing model", "severity": "medium"},
            {"id": "C-002", "description": "Target audience mismatch", "severity": "high"}
        ]
    }

@app.post("/api/v1/onboarding/{session_id}/truth-sheet")
async def truth_sheet(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "truth_sheet": {
            "statements": [
                {"id": "T-001", "statement": "We help companies scale faster", "confidence": 0.85},
                {"id": "T-002", "statement": "Our solution reduces costs by 40%", "confidence": 0.72}
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/brand-audit")
async def brand_audit(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "dimensions": [
            {"id": "1", "name": "Visual Identity", "score": 75, "status": "yellow"},
            {"id": "2", "name": "Message Clarity", "score": 58, "status": "yellow"}
        ],
        "brand_items": [
            {"id": "1", "name": "Website Hero", "category": "web", "action": "fix"}
        ]
    }

@app.post("/api/v1/onboarding/{session_id}/focus-sacrifice")
async def focus_sacrifice(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "focus_sacrifice": {
            "focus_items": [
                {"description": "Focus on primary ICP segment", "category": "audience", "impact": 0.9}
            ],
            "sacrifice_items": [
                {"description": "Sacrifice enterprise market", "category": "market", "impact": 0.7}
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/icp-deep")
async def icp_deep(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "icp_profiles": {
            "profiles": [
                {
                    "id": "ICP-001",
                    "name": "Growth-Stage SaaS",
                    "tier": "primary",
                    "description": "Fast-moving SaaS companies ready to scale"
                }
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/messaging-rules")
async def messaging_rules(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "messaging_rules": {
            "rules": [
                {"id": "RUL-TONE-001", "category": "tone", "name": "Avoid Aggressive Language", "severity": "warning"}
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/soundbites")
async def soundbites(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "soundbites": {
            "library": [
                {"id": "SND-001", "type": "tagline", "content": "Better results without the complexity"}
            ]
        }
    }

@app.post("/api/v1/onboarding/{session_id}/market-size")
async def market_size(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "market_size": {
            "tam": {"value": 1000000000, "label": "$1B"},
            "sam": {"value": 100000000, "label": "$100M"},
            "som": {"value": 10000000, "label": "$10M"}
        }
    }

@app.post("/api/v1/onboarding/{session_id}/launch-readiness")
async def launch_readiness(session_id: str, request: Dict[str, Any]):
    return {
        "success": True,
        "launch_readiness": {
            "overall_score": 65,
            "ready_count": 8,
            "total_items": 18,
            "launch_ready": False
        }
    }

@app.post("/api/v1/ai/generate")
async def ai_generate(request: Dict[str, Any]):
    return {
        "success": True,
        "response": "This is a mock AI response. The actual Vertex AI integration requires proper API keys and configuration.",
        "model": request.get("model", "gemini-pro"),
        "usage": {"prompt_tokens": 10, "completion_tokens": 20}
    }

@app.post("/api/v1/ai/chat")
async def ai_chat(request: Dict[str, Any]):
    return {
        "success": True,
        "message": "This is a mock chat response. The actual AI integration requires proper configuration.",
        "history": [{"role": "assistant", "content": "Mock response"}]
    }

# Mock Moves endpoints
@app.get("/api/v1/moves/")
async def get_moves():
    return {
        "moves": [
            {
                "id": "move-1",
                "name": "Test Move",
                "focusArea": "Growth",
                "desiredOutcome": "Increase users",
                "volatilityLevel": 3,
                "steps": ["Step 1", "Step 2"],
                "status": "draft",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }

@app.post("/api/v1/moves/")
async def create_move(request: Dict[str, Any]):
    return {
        "id": "new-move-id",
        "name": request.get("name", "New Move"),
        "focusArea": request.get("focusArea", "General"),
        "desiredOutcome": request.get("desiredOutcome", "Success"),
        "volatilityLevel": request.get("volatilityLevel", 5),
        "steps": request.get("steps", []),
        "status": "draft",
        "created_at": "2024-01-01T00:00:00Z"
    }

@app.put("/api/v1/moves/{move_id}")
async def update_move(move_id: str, request: Dict[str, Any]):
    return {
        "id": move_id,
        "name": request.get("name", "Updated Move"),
        "focusArea": request.get("focusArea", "General"),
        "desiredOutcome": request.get("desiredOutcome", "Success"),
        "volatilityLevel": request.get("volatilityLevel", 5),
        "steps": request.get("steps", []),
        "status": request.get("status", "draft"),
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.delete("/api/v1/moves/{move_id}")
async def delete_move(move_id: str):
    return {"success": True, "message": f"Move {move_id} deleted"}

# Mock Campaigns endpoints
@app.get("/api/v1/campaigns")
async def get_campaigns():
    return {
        "campaigns": [
            {
                "id": "campaign-1",
                "name": "Test Campaign",
                "description": "A test campaign",
                "target_icps": ["icp-1"],
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }

@app.post("/api/v1/campaigns", status_code=201)
async def create_campaign(request: Dict[str, Any]):
    return {
        "id": "new-campaign-id",
        "name": request.get("name", "New Campaign"),
        "description": request.get("description", ""),
        "target_icps": request.get("target_icps", []),
        "status": "draft",
        "created_at": "2024-01-01T00:00:00Z"
    }

@app.put("/api/v1/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, request: Dict[str, Any]):
    return {
        "id": campaign_id,
        "name": request.get("name", "Updated Campaign"),
        "description": request.get("description", ""),
        "target_icps": request.get("target_icps", []),
        "status": request.get("status", "draft"),
        "updated_at": "2024-01-01T00:00:00Z"
    }

@app.delete("/api/v1/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    return {"success": True, "message": f"Campaign {campaign_id} deleted"}

# Mock Daily Wins endpoints
@app.get("/api/v1/daily_wins/")
async def get_daily_wins():
    return {
        "wins": [
            {
                "id": "win-1",
                "content": "Post on LinkedIn about industry trends",
                "platform": "LinkedIn",
                "action_type": "content",
                "energy_level": "medium",
                "completed_at": None,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }

@app.post("/api/v1/daily_wins/generate")
async def generate_daily_win(request: Dict[str, Any]):
    return {
        "win": {
            "id": "new-win-id",
            "content": "Generated daily win task",
            "platform": request.get("platform", "LinkedIn"),
            "action_type": "content",
            "energy_level": "medium",
            "completed_at": None,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "success": True
    }

@app.post("/api/v1/daily_wins/{win_id}/complete")
async def complete_daily_win(win_id: str):
    return {"success": True, "message": f"Daily win {win_id} completed"}

# Mock Blackbox endpoints
@app.post("/api/v1/blackbox/generate-strategy")
async def generate_strategy(request: Dict[str, Any]):
    return {
        "strategy": {
            "id": "strategy-1",
            "focus_area": request.get("focus_area", "growth"),
            "business_context": request.get("business_context", ""),
            "strategy": "Generated business strategy",
            "reasoning": "Strategic reasoning",
            "implementation_steps": ["Step 1", "Step 2", "Step 3"],
            "success_metrics": ["Metric 1", "Metric 2"],
            "created_at": "2024-01-01T00:00:00Z"
        }
    }

@app.get("/api/v1/blackbox/strategies")
async def get_strategies():
    return {
        "strategies": [
            {
                "id": "strategy-1",
                "focus_area": "growth",
                "strategy": "Existing strategy",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }

@app.post("/api/v1/blackbox/{strategy_id}/create-move")
async def create_move_from_strategy(strategy_id: str):
    return {"move_id": "move-from-strategy", "success": True}

# Mock Muse endpoints
@app.post("/api/v1/muse/generate")
async def muse_generate(request: Dict[str, Any]):
    return {
        "asset": {
            "id": "asset-1",
            "title": "Generated Content",
            "content": "Generated marketing content",
            "platform": request.get("platform", "email"),
            "created_at": "2024-01-01T00:00:00Z"
        }
    }

@app.post("/api/v1/muse/chat")
async def muse_chat(request: Dict[str, Any]):
    return {
        "message": {
            "id": "msg-1",
            "role": "assistant",
            "content": "This is a mock Muse chat response",
            "created_at": "2024-01-01T00:00:00Z"
        }
    }

@app.get("/api/v1/muse/assets")
async def get_muse_assets():
    return {
        "assets": [
            {
                "id": "asset-1",
                "title": "Sample Asset",
                "content": "Sample content",
                "platform": "email",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }

@app.post("/api/v1/muse/assets")
async def save_muse_asset(request: Dict[str, Any]):
    return {
        "id": "new-asset-id",
        "title": request.get("title", "New Asset"),
        "content": request.get("content", ""),
        "platform": request.get("platform", "email"),
        "created_at": "2024-01-01T00:00:00Z"
    }

# BCM (Business Context Management) endpoints
@app.get("/api/v1/bcm/context")
async def get_bcm_context():
    return {
        "context": {
            "workspace_id": "test-workspace",
            "business_stage": "growth",
            "industry": "technology",
            "team_size": 10,
            "revenue_range": "1M-10M",
            "target_market": "B2B SaaS",
            "current_challenges": ["Lead generation", "Customer retention"],
            "strengths": ["Product quality", "Team expertise"],
            "opportunities": ["Market expansion", "Product diversification"],
            "evolution_history": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "event": "Initial setup",
                    "insights": ["Business foundation established"]
                },
                {
                    "timestamp": "2024-01-15T00:00:00Z",
                    "event": "First customer acquisition",
                    "insights": ["Product-market fit validated"]
                }
            ],
            "contradictions": [
                {
                    "id": "C-001",
                    "description": "Focus on enterprise vs startup customers",
                    "severity": "medium",
                    "resolution": "Prioritize startup segment initially"
                }
            ],
            "strategic_priorities": [
                "Increase MRR by 25%",
                "Improve customer retention to 90%",
                "Expand to new geographic markets"
            ]
        }
    }

@app.post("/api/v1/bcm/record-interaction")
async def record_bcm_interaction(request: Dict[str, Any]):
    return {
        "success": True,
        "recorded": {
            "timestamp": "2024-01-01T00:00:00Z",
            "agent": request.get("agent", "unknown"),
            "action": request.get("action", "interaction"),
            "context": request.get("context", {}),
            "insights": ["Interaction recorded for future learning"]
        }
    }

@app.get("/api/v1/bcm/evolution")
async def get_bcm_evolution():
    return {
        "evolution": {
            "current_stage": "growth",
            "previous_stages": ["seed", "startup"],
            "next_milestones": [
                {
                    "name": "Series A Funding",
                    "target_date": "2024-06-01",
                    "requirements": ["$5M ARR", "50 enterprise customers"]
                },
                {
                    "name": "Product 2.0 Launch",
                    "target_date": "2024-04-01",
                    "requirements": ["AI features", "Mobile app"]
                }
            ],
            "learnings": [
                "Customers value simplicity over features",
                "Direct sales works better than marketing automation",
                "Integration capabilities are key differentiator"
            ]
        }
    }

# Tools and Services endpoints
@app.get("/api/v1/tools/available")
async def get_available_tools():
    return {
        "tools": [
            {
                "id": "vertex-ai",
                "name": "Google Vertex AI",
                "type": "ai_service",
                "status": "active",
                "capabilities": ["text_generation", "analysis", "classification"],
                "usage": {"requests_made": 1250, "tokens_used": 45000}
            },
            {
                "id": "supabase",
                "name": "Supabase Database",
                "type": "database",
                "status": "active",
                "capabilities": ["crud", "auth", "realtime"],
                "usage": {"connections": 45, "queries": 890}
            },
            {
                "id": "upstash-redis",
                "name": "Upstash Redis",
                "type": "cache",
                "status": "active",
                "capabilities": ["caching", "rate_limiting", "sessions"],
                "usage": {"keys": 120, "operations": 3400}
            },
            {
                "id": "resend",
                "name": "Resend Email",
                "type": "email_service",
                "status": "active",
                "capabilities": ["email_sending", "templates", "analytics"],
                "usage": {"emails_sent": 234, "open_rate": 0.68}
            }
        ]
    }

@app.get("/api/v1/services/status")
async def get_services_status():
    return {
        "services": {
            "ai_services": {
                "vertex_ai": {"status": "healthy", "latency_ms": 120, "last_check": "2024-01-01T00:00:00Z"},
                "muse_ai": {"status": "healthy", "latency_ms": 200, "last_check": "2024-01-01T00:00:00Z"},
                "blackbox_ai": {"status": "healthy", "latency_ms": 150, "last_check": "2024-01-01T00:00:00Z"}
            },
            "data_services": {
                "supabase": {"status": "healthy", "connections": 12, "last_check": "2024-01-01T00:00:00Z"},
                "redis": {"status": "healthy", "memory_usage": "45%", "last_check": "2024-01-01T00:00:00Z"}
            },
            "communication": {
                "resend": {"status": "healthy", "queue_size": 0, "last_check": "2024-01-01T00:00:00Z"}
            },
            "monitoring": {
                "sentry": {"status": "healthy", "errors_last_hour": 0, "last_check": "2024-01-01T00:00:00Z"},
                "analytics": {"status": "healthy", "events_tracked": 1250, "last_check": "2024-01-01T00:00:00Z"}
            }
        },
        "overall_health": "healthy",
        "uptime_percentage": 99.9
    }

# Agent system endpoints
@app.get("/api/v1/agents/available")
async def get_available_agents():
    return {
        "agents": [
            {
                "id": "muse",
                "name": "Muse - Content Generation",
                "type": "creative",
                "status": "active",
                "capabilities": ["content_generation", "copywriting", "brand_voice"],
                "specializations": ["email", "linkedin", "blog", "twitter"]
            },
            {
                "id": "blackbox",
                "name": "Blackbox - Strategy",
                "type": "analytical",
                "status": "active",
                "capabilities": ["strategy_generation", "market_analysis", "competitive_insights"],
                "specializations": ["growth", "retention", "revenue", "brand_equity"]
            },
            {
                "id": "icp_architect",
                "name": "ICP Architect",
                "type": "research",
                "status": "active",
                "capabilities": ["persona_development", "market_research", "customer_profiling"],
                "specializations": ["b2b_saaS", "enterprise", "startup"]
            },
            {
                "id": "campaign_planner",
                "name": "Campaign Planner",
                "type": "operational",
                "status": "active",
                "capabilities": ["campaign_design", "budget_allocation", "performance_tracking"],
                "specializations": ["product_launch", "lead_generation", "brand_awareness"]
            }
        ]
    }

@app.post("/api/v1/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, request: Dict[str, Any]):
    return {
        "execution": {
            "agent_id": agent_id,
            "task": request.get("task", "unknown"),
            "status": "completed",
            "result": f"Mock execution result from {agent_id}",
            "confidence": 0.85,
            "processing_time_ms": 250,
            "context_used": {
                "bcm_context": True,
                "user_history": True,
                "business_stage": True
            },
            "insights": [
                "Task completed successfully",
                "BCM context improved accuracy by 23%",
                "Recommendation: Review results for implementation"
            ]
        }
    }

# Analytics and Insights endpoints
@app.get("/api/v1/analytics/dashboard")
async def get_analytics_dashboard():
    return {
        "dashboard": {
            "overview": {
                "total_users": 1247,
                "active_campaigns": 8,
                "engagement_rate": 0.73,
                "conversion_rate": 0.12,
                "revenue_this_month": 125000
            },
            "performance_metrics": {
                "campaign_performance": [
                    {"campaign": "Q1 Launch", "roi": 3.2, "status": "active"},
                    {"campaign": "Email Nurture", "roi": 2.8, "status": "completed"}
                ],
                "user_engagement": {
                    "daily_active": 342,
                    "weekly_active": 892,
                    "monthly_active": 1247
                },
                "content_performance": {
                    "total_assets": 156,
                    "avg_engagement": 0.68,
                    "top_performing": "LinkedIn posts"
                }
            },
            "insights": [
                "LinkedIn content generates 3x more engagement than email",
                "Campaigns with personalized ICP targeting perform 45% better",
                "Users who complete Daily Wins show 2x higher retention"
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
