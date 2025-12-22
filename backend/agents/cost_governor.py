from pydantic import BaseModel, Field

class BudgetCheck(BaseModel):
    allowed: bool
    reason: str = ""
    suggested_tier: str = "fast"

class CostGovernorAgent:
    """
    Enforces per-workspace token and cost limits.
    Prevents runaway agent loops.
    """
    
    async def check_budget(self, workspace_id: str, estimated_tokens: int) -> BudgetCheck:
        # In production, query Redis or DB for current usage
        # For now, we simulate a simple pass/fail
        usage = 500000 # dummy usage
        limit = 1000000 # 1M tokens limit
        
        if usage + estimated_tokens > limit:
            return BudgetCheck(allowed=False, reason="Monthly token limit reached.", suggested_tier="fast")
            
        return BudgetCheck(allowed=True)
