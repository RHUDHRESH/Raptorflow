"""
Launch Readiness Checker Agent
Validates go-to-market readiness across all dimensions
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ReadinessCategory(Enum):
    """Categories for launch readiness"""
    POSITIONING = "positioning"
    MESSAGING = "messaging"
    ICP = "icp"
    CONTENT = "content"
    CHANNELS = "channels"
    SALES = "sales"
    PRODUCT = "product"
    ANALYTICS = "analytics"


class ReadinessStatus(Enum):
    """Status of readiness check"""
    READY = "ready"
    ALMOST_READY = "almost_ready"
    NEEDS_WORK = "needs_work"
    NOT_STARTED = "not_started"


class Priority(Enum):
    """Priority level"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ReadinessCheckItem:
    """A single readiness check item"""
    id: str
    category: ReadinessCategory
    name: str
    description: str
    status: ReadinessStatus
    score: float  # 0-100
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM


@dataclass
class LaunchChecklist:
    """Complete launch checklist"""
    items: List[ReadinessCheckItem]
    overall_score: float
    ready_count: int
    blockers_count: int
    launch_ready: bool
    launch_date_recommendation: str
    next_steps: List[str]
    summary: str


class LaunchReadinessChecker:
    """AI-powered launch readiness validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.item_counter = 0
        self.checklist_items = self._load_checklist_items()
    
    def _generate_item_id(self) -> str:
        self.item_counter += 1
        return f"LCH-{self.item_counter:03d}"
    
    def _load_checklist_items(self) -> List[Dict[str, Any]]:
        """Load default checklist items"""
        return [
            {"category": ReadinessCategory.POSITIONING, "name": "Primary positioning statement", "description": "Clear, differentiated positioning statement approved", "priority": Priority.CRITICAL},
            {"category": ReadinessCategory.POSITIONING, "name": "Category definition", "description": "Category strategy defined (create, enter, or reframe)", "priority": Priority.HIGH},
            {"category": ReadinessCategory.POSITIONING, "name": "Competitive differentiation", "description": "'Only we' claims validated and documented", "priority": Priority.HIGH},
            
            {"category": ReadinessCategory.MESSAGING, "name": "Messaging framework", "description": "Complete messaging hierarchy documented", "priority": Priority.CRITICAL},
            {"category": ReadinessCategory.MESSAGING, "name": "Tagline finalized", "description": "Brand tagline tested and approved", "priority": Priority.HIGH},
            {"category": ReadinessCategory.MESSAGING, "name": "Messaging rules", "description": "Brand guardrails and do/don't documented", "priority": Priority.MEDIUM},
            
            {"category": ReadinessCategory.ICP, "name": "Primary ICP defined", "description": "Primary ICP with firmographics and psychographics", "priority": Priority.CRITICAL},
            {"category": ReadinessCategory.ICP, "name": "Buyer personas", "description": "Key buyer personas documented with pain points", "priority": Priority.HIGH},
            {"category": ReadinessCategory.ICP, "name": "Disqualification criteria", "description": "Clear criteria for who NOT to sell to", "priority": Priority.MEDIUM},
            
            {"category": ReadinessCategory.CONTENT, "name": "Website copy", "description": "Homepage and key landing pages written", "priority": Priority.CRITICAL},
            {"category": ReadinessCategory.CONTENT, "name": "Sales deck", "description": "Sales presentation deck completed", "priority": Priority.HIGH},
            {"category": ReadinessCategory.CONTENT, "name": "Case studies", "description": "At least 1 customer success story", "priority": Priority.MEDIUM},
            
            {"category": ReadinessCategory.CHANNELS, "name": "Channel strategy", "description": "Primary GTM channels identified and prioritized", "priority": Priority.HIGH},
            {"category": ReadinessCategory.CHANNELS, "name": "Channel setup", "description": "Top 2 channels configured and ready", "priority": Priority.HIGH},
            
            {"category": ReadinessCategory.SALES, "name": "Sales process", "description": "Sales stages and handoffs defined", "priority": Priority.HIGH},
            {"category": ReadinessCategory.SALES, "name": "Objection handling", "description": "Top objections with responses documented", "priority": Priority.MEDIUM},
            
            {"category": ReadinessCategory.ANALYTICS, "name": "Tracking setup", "description": "Analytics and conversion tracking configured", "priority": Priority.HIGH},
            {"category": ReadinessCategory.ANALYTICS, "name": "Success metrics", "description": "KPIs and targets defined for launch", "priority": Priority.MEDIUM},
        ]
    
    def _evaluate_item(self, item_config: Dict, onboarding_data: Dict[str, Any]) -> ReadinessCheckItem:
        """Evaluate a single checklist item against onboarding data"""
        category = item_config["category"]
        score = 0
        status = ReadinessStatus.NOT_STARTED
        blockers = []
        recommendations = []
        
        # Check based on category
        if category == ReadinessCategory.POSITIONING:
            if onboarding_data.get("positioning"):
                positioning = onboarding_data["positioning"]
                if positioning.get("primary_statement"):
                    score = 80
                    status = ReadinessStatus.ALMOST_READY
                    if positioning.get("only_we_claims"):
                        score = 100
                        status = ReadinessStatus.READY
                else:
                    score = 30
                    status = ReadinessStatus.NEEDS_WORK
                    blockers.append("Primary positioning statement not finalized")
            else:
                blockers.append("Positioning not started")
                recommendations.append("Complete positioning step in onboarding")
        
        elif category == ReadinessCategory.MESSAGING:
            if onboarding_data.get("soundbites"):
                soundbites = onboarding_data["soundbites"]
                count = soundbites.get("count", 0)
                if count >= 5:
                    score = 100
                    status = ReadinessStatus.READY
                elif count >= 3:
                    score = 70
                    status = ReadinessStatus.ALMOST_READY
                else:
                    score = 40
                    status = ReadinessStatus.NEEDS_WORK
                    recommendations.append("Generate more soundbites for messaging coverage")
            else:
                blockers.append("Messaging library not created")
                recommendations.append("Complete soundbites generation")
        
        elif category == ReadinessCategory.ICP:
            if onboarding_data.get("icp_deep"):
                icp = onboarding_data["icp_deep"]
                if icp.get("primary_icp"):
                    score = 90
                    status = ReadinessStatus.READY
                else:
                    score = 50
                    status = ReadinessStatus.NEEDS_WORK
            else:
                blockers.append("ICP profiles not generated")
                recommendations.append("Complete ICP deep generation")
        
        elif category == ReadinessCategory.CONTENT:
            # Check for content readiness
            if onboarding_data.get("soundbites") and onboarding_data.get("positioning"):
                score = 60
                status = ReadinessStatus.ALMOST_READY
                recommendations.append("Create website copy using generated messaging")
            else:
                score = 20
                status = ReadinessStatus.NEEDS_WORK
                blockers.append("Messaging foundation not ready for content")
        
        elif category == ReadinessCategory.CHANNELS:
            if onboarding_data.get("channel_strategy"):
                score = 80
                status = ReadinessStatus.ALMOST_READY
            else:
                score = 0
                status = ReadinessStatus.NOT_STARTED
                blockers.append("Channel strategy not defined")
        
        elif category == ReadinessCategory.SALES:
            if onboarding_data.get("icp_deep") and onboarding_data.get("positioning"):
                score = 50
                status = ReadinessStatus.NEEDS_WORK
                recommendations.append("Create sales deck from positioning")
            else:
                score = 10
                status = ReadinessStatus.NOT_STARTED
        
        elif category == ReadinessCategory.ANALYTICS:
            score = 30
            status = ReadinessStatus.NEEDS_WORK
            recommendations.append("Configure analytics tracking before launch")
        
        return ReadinessCheckItem(
            id=self._generate_item_id(),
            category=category,
            name=item_config["name"],
            description=item_config["description"],
            status=status,
            score=score,
            blockers=blockers,
            recommendations=recommendations,
            priority=item_config["priority"]
        )
    
    async def check_launch_readiness(self, onboarding_data: Dict[str, Any]) -> LaunchChecklist:
        """
        Check launch readiness across all dimensions
        
        Args:
            onboarding_data: All collected onboarding data
        
        Returns:
            LaunchChecklist with detailed assessment
        """
        items = []
        
        for item_config in self.checklist_items:
            evaluated = self._evaluate_item(item_config, onboarding_data)
            items.append(evaluated)
        
        # Calculate metrics
        total_score = sum(item.score for item in items) / len(items) if items else 0
        ready_count = sum(1 for item in items if item.status == ReadinessStatus.READY)
        blockers_count = sum(len(item.blockers) for item in items)
        
        # Determine launch readiness
        critical_items = [i for i in items if i.priority == Priority.CRITICAL]
        critical_ready = all(i.status in [ReadinessStatus.READY, ReadinessStatus.ALMOST_READY] for i in critical_items)
        
        launch_ready = total_score >= 70 and critical_ready
        
        # Determine launch date
        if launch_ready:
            launch_date = "Ready to launch now"
        elif total_score >= 50:
            launch_date = "1-2 weeks with focused effort"
        elif total_score >= 30:
            launch_date = "3-4 weeks with dedicated work"
        else:
            launch_date = "4+ weeks - significant gaps remain"
        
        # Generate next steps
        next_steps = []
        blocker_items = [i for i in items if i.blockers]
        for item in sorted(blocker_items, key=lambda x: x.priority.value)[:5]:
            next_steps.append(f"[{item.priority.value.upper()}] {item.name}: {item.blockers[0]}")
        
        summary = f"Launch readiness: {total_score:.0f}%. "
        summary += f"{ready_count}/{len(items)} items ready. "
        summary += f"{blockers_count} blockers. "
        summary += f"{'READY TO LAUNCH' if launch_ready else 'NOT YET READY'}."
        
        return LaunchChecklist(
            items=items,
            overall_score=total_score,
            ready_count=ready_count,
            blockers_count=blockers_count,
            launch_ready=launch_ready,
            launch_date_recommendation=launch_date,
            next_steps=next_steps,
            summary=summary
        )
    
    def get_checklist_summary(self, checklist: LaunchChecklist) -> Dict[str, Any]:
        """Get summary for display"""
        by_category = {}
        for item in checklist.items:
            cat = item.category.value
            if cat not in by_category:
                by_category[cat] = {"ready": 0, "total": 0, "score": 0}
            by_category[cat]["total"] += 1
            by_category[cat]["score"] += item.score
            if item.status == ReadinessStatus.READY:
                by_category[cat]["ready"] += 1
        
        for cat in by_category:
            by_category[cat]["score"] = by_category[cat]["score"] / by_category[cat]["total"]
        
        return {
            "overall_score": checklist.overall_score,
            "ready_count": checklist.ready_count,
            "total_items": len(checklist.items),
            "launch_ready": checklist.launch_ready,
            "launch_date": checklist.launch_date_recommendation,
            "by_category": by_category,
            "next_steps": checklist.next_steps[:5],
            "summary": checklist.summary
        }
