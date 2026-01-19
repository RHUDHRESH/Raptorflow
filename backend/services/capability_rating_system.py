"""
Capability Rating System
Advanced capability assessment and rating for Raptorflow
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import asyncio
from collections import defaultdict

# Import AI services
try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

logger = logging.getLogger(__name__)


class CapabilityCategory(str, Enum):
    """Categories of capabilities"""
    TECHNICAL = "technical"
    MARKETING = "marketing"
    SALES = "sales"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    FINANCIAL = "financial"
    LEADERSHIP = "leadership"
    INNOVATION = "innovation"


class CapabilityLevel(str, Enum):
    """Capability levels"""
    ONLY_YOU = "only_you"  # Unique capability only you have
    UNIQUE = "unique"  # Rare capability few competitors have
    COMPETITIVE = "competitive"  # Common capability but you excel at it
    TABLE_STAKES = "table_stakes"  # Basic capability everyone has


class MaturityLevel(str, Enum):
    """Maturity levels for capabilities"""
    EMERGING = "emerging"  # 0-25% developed
    DEVELOPING = "developing"  # 25-50% developed
    MATURING = "maturing"  # 50-75% developed
    MATURE = "mature"  # 75-100% developed


@dataclass
class Capability:
    """Individual capability"""
    id: str
    name: str
    description: str
    category: CapabilityCategory
    level: CapabilityLevel
    maturity: MaturityLevel
    proficiency_score: float  # 0-1 scale
    importance_score: float  # 0-1 scale
    competitive_advantage: float  # 0-1 scale
    development_priority: float  # 0-1 scale
    evidence: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    development_actions: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "level": self.level.value,
            "maturity": self.maturity.value,
            "proficiency_score": self.proficiency_score,
            "importance_score": self.importance_score,
            "competitive_advantage": self.competitive_advantage,
            "development_priority": self.development_priority,
            "evidence": self.evidence,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "development_actions": self.development_actions,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class CapabilityAssessment:
    """Complete capability assessment"""
    company_info: Dict[str, Any]
    capabilities: List[Capability]
    category_scores: Dict[str, float]
    overall_score: float
    competitive_positioning: Dict[str, Any]
    development_priorities: List[str]
    capability_gaps: List[str]
    strategic_recommendations: List[str]
    implementation_roadmap: Dict[str, List[str]]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class CapabilityRatingSystem:
    """Advanced capability rating system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Capability framework
        self.capability_framework = self._initialize_capability_framework()
        
        # Rating criteria
        self.rating_criteria = self._initialize_rating_criteria()
        
        # Development actions
        self.development_actions = self._initialize_development_actions()
    
    def _initialize_capability_framework(self) -> Dict[CapabilityCategory, List[Dict[str, Any]]]:
        """Initialize capability framework"""
        return {
            CapabilityCategory.TECHNICAL: [
                {
                    "name": "Product Development",
                    "description": "Ability to design, build, and ship quality products",
                    "keywords": ["engineering", "development", "product", "technology", "innovation"]
                },
                {
                    "name": "Data Analytics",
                    "description": "Ability to collect, analyze, and derive insights from data",
                    "keywords": ["data", "analytics", "insights", "metrics", "measurement"]
                },
                {
                    "name": "Infrastructure",
                    "description": "Ability to maintain and scale technical infrastructure",
                    "keywords": ["infrastructure", "scalability", "reliability", "security", "performance"]
                },
                {
                    "name": "Integration",
                    "description": "Ability to integrate with third-party systems",
                    "keywords": ["integration", "api", "connectivity", "ecosystem", "partnerships"]
                }
            ],
            CapabilityCategory.MARKETING: [
                {
                    "name": "Brand Building",
                    "description": "Ability to create and maintain strong brand presence",
                    "keywords": ["brand", "positioning", "awareness", "reputation", "identity"]
                },
                {
                    "name": "Content Marketing",
                    "description": "Ability to create compelling content that attracts and engages",
                    "keywords": ["content", "storytelling", "messaging", "creative", "engagement"]
                },
                {
                    "name": "Digital Marketing",
                    "description": "Ability to execute effective digital marketing campaigns",
                    "keywords": ["digital", "online", "social", "ppc", "seo", "email"]
                },
                {
                    "name": "Marketing Analytics",
                    "description": "Ability to measure and optimize marketing performance",
                    "keywords": ["attribution", "roi", "optimization", "testing", "measurement"]
                }
            ],
            CapabilityCategory.SALES: [
                {
                    "name": "Sales Process",
                    "description": "Ability to execute effective sales processes",
                    "keywords": ["selling", "process", "methodology", "technique", "conversion"]
                },
                {
                    "name": "Customer Relationships",
                    "description": "Ability to build and maintain customer relationships",
                    "keywords": ["relationships", "trust", "partnership", "retention", "loyalty"]
                },
                {
                    "name": "Sales Technology",
                    "description": "Ability to leverage technology for sales effectiveness",
                    "keywords": ["crm", "automation", "tools", "technology", "efficiency"]
                },
                {
                    "name": "Market Expansion",
                    "description": "Ability to expand into new markets and segments",
                    "keywords": ["expansion", "growth", "new markets", "segments", "geography"]
                }
            ],
            CapabilityCategory.OPERATIONAL: [
                {
                    "name": "Process Optimization",
                    "description": "Ability to optimize business processes for efficiency",
                    "keywords": ["process", "efficiency", "optimization", "workflow", "productivity"]
                },
                {
                    "name": "Quality Management",
                    "description": "Ability to maintain high quality standards",
                    "keywords": ["quality", "standards", "excellence", "consistency", "reliability"]
                },
                {
                    "name": "Customer Service",
                    "description": "Ability to provide excellent customer service",
                    "keywords": ["service", "support", "experience", "satisfaction", "success"]
                },
                {
                    "name": "Supply Chain",
                    "description": "Ability to manage supply chain effectively",
                    "keywords": ["supply", "chain", "logistics", "procurement", "operations"]
                }
            ],
            CapabilityCategory.STRATEGIC: [
                {
                    "name": "Strategic Planning",
                    "description": "Ability to develop and execute strategic plans",
                    "keywords": ["strategy", "planning", "vision", "goals", "execution"]
                },
                {
                    "name": "Market Intelligence",
                    "description": "Ability to gather and analyze market intelligence",
                    "keywords": ["intelligence", "research", "analysis", "insights", "trends"]
                },
                {
                    "name": "Competitive Analysis",
                    "description": "Ability to analyze competitive landscape",
                    "keywords": ["competition", "analysis", "positioning", "advantage", "landscape"]
                },
                {
                    "name": "Innovation Strategy",
                    "description": "Ability to develop and execute innovation strategy",
                    "keywords": ["innovation", "strategy", "disruption", "breakthrough", "future"]
                }
            ],
            CapabilityCategory.FINANCIAL: [
                {
                    "name": "Financial Planning",
                    "description": "Ability to plan and manage financial resources",
                    "keywords": ["financial", "planning", "budgeting", "forecasting", "management"]
                },
                {
                    "name": "Fundraising",
                    "description": "Ability to raise capital and manage investor relations",
                    "keywords": ["fundraising", "investment", "capital", "investors", "financing"]
                },
                {
                    "name": "Cost Management",
                    "description": "Ability to manage costs effectively",
                    "keywords": ["costs", "expenses", "efficiency", "optimization", "control"]
                },
                {
                    "name": "Revenue Optimization",
                    "description": "Ability to optimize revenue streams",
                    "keywords": ["revenue", "optimization", "pricing", "monetization", "growth"]
                }
            ],
            CapabilityCategory.LEADERSHIP: [
                {
                    "name": "Team Leadership",
                    "description": "Ability to lead and develop high-performing teams",
                    "keywords": ["leadership", "team", "management", "culture", "motivation"]
                },
                {
                    "name": "Talent Acquisition",
                    "description": "Ability to attract and retain top talent",
                    "keywords": ["talent", "hiring", "recruitment", "retention", "people"]
                },
                {
                    "name": "Decision Making",
                    "description": "Ability to make effective decisions under uncertainty",
                    "keywords": ["decisions", "judgment", "analysis", "risk", "clarity"]
                },
                {
                    "name": "Change Management",
                    "description": "Ability to manage organizational change",
                    "keywords": ["change", "transformation", "adaptation", "flexibility", "resilience"]
                }
            ],
            CapabilityCategory.INNOVATION: [
                {
                    "name": "Product Innovation",
                    "description": "Ability to innovate and improve products",
                    "keywords": ["product", "innovation", "development", "improvement", "evolution"]
                },
                {
                    "name": "Business Model Innovation",
                    "description": "Ability to innovate business models",
                    "keywords": ["business", "model", "innovation", "disruption", "transformation"]
                },
                {
                    "name": "Process Innovation",
                    "description": "Ability to innovate business processes",
                    "keywords": ["process", "innovation", "automation", "efficiency", "breakthrough"]
                },
                {
                    "name": "Market Innovation",
                    "description": "Ability to create new markets or market segments",
                    "keywords": ["market", "creation", "innovation", "disruption", "pioneering"]
                }
            ]
        }
    
    def _initialize_rating_criteria(self) -> Dict[str, float]:
        """Initialize rating criteria weights"""
        return {
            "proficiency": 0.3,  # How well you do it
            "importance": 0.25,  # How important it is to success
            "uniqueness": 0.2,  # How unique it is compared to competitors
            "maturity": 0.15,  # How developed the capability is
            "scalability": 0.1  # How scalable the capability is
        }
    
    def _initialize_development_actions(self) -> Dict[CapabilityLevel, List[str]]:
        """Initialize development actions for each level"""
        return {
            CapabilityLevel.ONLY_YOU: [
                "Protect and enhance unique capability",
                "Build moats around the capability",
                "Leverage for maximum competitive advantage",
                "Document and systematize the capability"
            ],
            CapabilityLevel.UNIQUE: [
                "Invest in capability development",
                "Build differentiation around capability",
                "Scale capability for broader impact",
                "Create barriers to imitation"
            ],
            CapabilityLevel.COMPETITIVE: [
                "Achieve excellence in capability",
                "Optimize for efficiency and quality",
                "Integrate with other capabilities",
                "Measure and improve continuously"
            ],
            CapabilityLevel.TABLE_STAKES: [
                "Ensure basic competency",
                "Maintain industry standards",
                "Optimize for cost efficiency",
                "Consider outsourcing if not core"
            ]
        }
    
    async def assess_capabilities(self, company_info: Dict[str, Any], evidence: List[Dict[str, Any]] = None, competitive_context: Dict[str, Any] = None) -> CapabilityAssessment:
        """Perform comprehensive capability assessment"""
        start_time = datetime.now()
        
        # Generate capabilities for each category
        capabilities = []
        for category, capability_templates in self.capability_framework.items():
            category_capabilities = await self._assess_category_capabilities(category, capability_templates, company_info, evidence)
            capabilities.extend(category_capabilities)
        
        # Calculate category scores
        category_scores = await self._calculate_category_scores(capabilities)
        
        # Calculate overall score
        overall_score = sum(category_scores.values()) / len(category_scores) if category_scores else 0.0
        
        # Analyze competitive positioning
        competitive_positioning = await self._analyze_competitive_positioning(capabilities, competitive_context)
        
        # Identify development priorities
        development_priorities = await self._identify_development_priorities(capabilities, category_scores)
        
        # Identify capability gaps
        capability_gaps = await self._identify_capability_gaps(capabilities, competitive_context)
        
        # Generate strategic recommendations
        strategic_recommendations = await self._generate_strategic_recommendations(capabilities, category_scores, competitive_positioning)
        
        # Create implementation roadmap
        implementation_roadmap = await self._create_implementation_roadmap(capabilities, development_priorities)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return CapabilityAssessment(
            company_info=company_info,
            capabilities=capabilities,
            category_scores=category_scores,
            overall_score=overall_score,
            competitive_positioning=competitive_positioning,
            development_priorities=development_priorities,
            capability_gaps=capability_gaps,
            strategic_recommendations=strategic_recommendations,
            implementation_roadmap=implementation_roadmap,
            processing_time=processing_time,
            metadata={
                "assessment_date": datetime.now().isoformat(),
                "total_capabilities": len(capabilities),
                "categories_assessed": len(category_scores)
            }
        )
    
    async def _assess_category_capabilities(self, category: CapabilityCategory, capability_templates: List[Dict[str, Any]], company_info: Dict[str, Any], evidence: List[Dict[str, Any]]) -> List[Capability]:
        """Assess capabilities for a specific category"""
        capabilities = []
        
        for template in capability_templates:
            capability = await self._assess_individual_capability(template, category, company_info, evidence)
            capabilities.append(capability)
        
        return capabilities
    
    async def _assess_individual_capability(self, template: Dict[str, Any], category: CapabilityCategory, company_info: Dict[str, Any], evidence: List[Dict[str, Any]]) -> Capability:
        """Assess individual capability"""
        # Generate capability ID
        capability_id = f"{category.value}_{template['name'].lower().replace(' ', '_')}"
        
        # Assess proficiency based on company info and evidence
        proficiency_score = await self._assess_proficiency(template, company_info, evidence)
        
        # Determine capability level
        level = await self._determine_capability_level(template, proficiency_score, company_info)
        
        # Assess maturity
        maturity = await self._assess_maturity(proficiency_score, company_info)
        
        # Calculate importance score
        importance_score = await self._calculate_importance(template, category, company_info)
        
        # Calculate competitive advantage
        competitive_advantage = await self._calculate_competitive_advantage(level, proficiency_score, category)
        
        # Calculate development priority
        development_priority = await self._calculate_development_priority(importance_score, competitive_advantage, proficiency_score)
        
        # Generate evidence
        capability_evidence = await self._generate_evidence(template, evidence)
        
        # Generate strengths and weaknesses
        strengths, weaknesses = await self._generate_strengths_weaknesses(template, proficiency_score, maturity)
        
        # Generate development actions
        development_actions = self.development_actions[level]
        
        # Generate metrics
        metrics = await self._generate_metrics(template, category)
        
        return Capability(
            id=capability_id,
            name=template["name"],
            description=template["description"],
            category=category,
            level=level,
            maturity=maturity,
            proficiency_score=proficiency_score,
            importance_score=importance_score,
            competitive_advantage=competitive_advantage,
            development_priority=development_priority,
            evidence=capability_evidence,
            strengths=strengths,
            weaknesses=weaknesses,
            development_actions=development_actions,
            metrics=metrics
        )
    
    async def _assess_proficiency(self, template: Dict[str, Any], company_info: Dict[str, Any], evidence: List[Dict[str, Any]]) -> float:
        """Assess capability proficiency"""
        base_score = 0.5  # Start with neutral score
        
        # Adjust based on company info
        company_size = company_info.get("size", "startup").lower()
        if company_size in ["startup", "small"]:
            base_score -= 0.1  # Smaller companies typically have lower proficiency
        elif company_size in ["large", "enterprise"]:
            base_score += 0.1  # Larger companies typically have higher proficiency
        
        # Adjust based on company age
        founded_year = company_info.get("founded_year")
        if founded_year:
            age = datetime.now().year - founded_year
            if age > 10:
                base_score += 0.1
            elif age < 2:
                base_score -= 0.1
        
        # Adjust based on evidence
        if evidence:
            evidence_keywords = " ".join([e.get("content", "") + " " + e.get("title", "") for e in evidence]).lower()
            template_keywords = template.get("keywords", [])
            
            keyword_matches = sum(1 for keyword in template_keywords if keyword in evidence_keywords)
            if keyword_matches > 0:
                base_score += min(0.2, keyword_matches * 0.05)
        
        # Adjust based on financial resources
        financial_resources = company_info.get("financial_resources", "limited").lower()
        if financial_resources == "strong":
            base_score += 0.1
        elif financial_resources == "limited":
            base_score -= 0.1
        
        return max(0.0, min(1.0, base_score))
    
    async def _determine_capability_level(self, template: Dict[str, Any], proficiency_score: float, company_info: Dict[str, Any]) -> CapabilityLevel:
        """Determine capability level"""
        # Base determination on proficiency
        if proficiency_score > 0.8:
            base_level = CapabilityLevel.ONLY_YOU
        elif proficiency_score > 0.6:
            base_level = CapabilityLevel.UNIQUE
        elif proficiency_score > 0.4:
            base_level = CapabilityLevel.COMPETITIVE
        else:
            base_level = CapabilityLevel.TABLE_STAKES
        
        # Adjust based on company context
        company_size = company_info.get("size", "startup").lower()
        if company_size in ["startup", "small"] and base_level == CapabilityLevel.ONLY_YOU:
            # Small companies rarely have "Only You" capabilities
            base_level = CapabilityLevel.UNIQUE
        
        # Adjust based on innovation capability
        innovation_capability = company_info.get("innovation_capability", "developing").lower()
        if innovation_capability == "mature" and proficiency_score > 0.7:
            base_level = CapabilityLevel.ONLY_YOU
        elif innovation_capability == "limited" and base_level in [CapabilityLevel.ONLY_YOU, CapabilityLevel.UNIQUE]:
            base_level = CapabilityLevel.COMPETITIVE
        
        return base_level
    
    async def _assess_maturity(self, proficiency_score: float, company_info: Dict[str, Any]) -> MaturityLevel:
        """Assess capability maturity"""
        if proficiency_score > 0.75:
            return MaturityLevel.MATURE
        elif proficiency_score > 0.5:
            return MaturityLevel.MATURING
        elif proficiency_score > 0.25:
            return MaturityLevel.DEVELOPING
        else:
            return MaturityLevel.EMERGING
    
    async def _calculate_importance(self, template: Dict[str, Any], category: CapabilityCategory, company_info: Dict[str, Any]) -> float:
        """Calculate capability importance"""
        base_importance = 0.5
        
        # Adjust based on category importance
        category_importance = {
            CapabilityCategory.TECHNICAL: 0.8,
            CapabilityCategory.MARKETING: 0.7,
            CapabilityCategory.SALES: 0.7,
            CapabilityCategory.OPERATIONAL: 0.6,
            CapabilityCategory.STRATEGIC: 0.8,
            CapabilityCategory.FINANCIAL: 0.7,
            CapabilityCategory.LEADERSHIP: 0.7,
            CapabilityCategory.INNOVATION: 0.6
        }
        
        base_importance = category_importance.get(category, 0.5)
        
        # Adjust based on company stage
        growth_stage = company_info.get("growth_stage", "early").lower()
        if growth_stage == "early":
            if category in [CapabilityCategory.TECHNICAL, CapabilityCategory.INNOVATION]:
                base_importance += 0.1
            elif category in [CapabilityCategory.OPERATIONAL, CapabilityCategory.FINANCIAL]:
                base_importance -= 0.1
        elif growth_stage == "mature":
            if category in [CapabilityCategory.OPERATIONAL, CapabilityCategory.FINANCIAL]:
                base_importance += 0.1
            elif category in [CapabilityCategory.INNOVATION]:
                base_importance -= 0.1
        
        return max(0.0, min(1.0, base_importance))
    
    async def _calculate_competitive_advantage(self, level: CapabilityLevel, proficiency_score: float, category: CapabilityCategory) -> float:
        """Calculate competitive advantage score"""
        base_advantage = {
            CapabilityLevel.ONLY_YOU: 0.9,
            CapabilityLevel.UNIQUE: 0.7,
            CapabilityLevel.COMPETITIVE: 0.4,
            CapabilityLevel.TABLE_STAKES: 0.1
        }
        
        advantage = base_advantage[level]
        
        # Adjust based on proficiency
        if proficiency_score > 0.8:
            advantage += 0.1
        elif proficiency_score < 0.4:
            advantage -= 0.1
        
        return max(0.0, min(1.0, advantage))
    
    async def _calculate_development_priority(self, importance_score: float, competitive_advantage: float, proficiency_score: float) -> float:
        """Calculate development priority"""
        # High importance + high competitive advantage + low proficiency = high priority
        priority = (importance_score * 0.4) + (competitive_advantage * 0.4) + ((1 - proficiency_score) * 0.2)
        
        return max(0.0, min(1.0, priority))
    
    async def _generate_evidence(self, template: Dict[str, Any], evidence: List[Dict[str, Any]]) -> List[str]:
        """Generate evidence for capability"""
        if not evidence:
            return ["No specific evidence available"]
        
        evidence_list = []
        template_keywords = template.get("keywords", [])
        
        for item in evidence:
            content = (item.get("content", "") + " " + item.get("title", "")).lower()
            
            # Check if evidence contains relevant keywords
            if any(keyword in content for keyword in template_keywords):
                evidence_list.append(item.get("title", "Evidence item"))
        
        return evidence_list[:3]  # Top 3 evidence items
    
    async def _generate_strengths_weaknesses(self, template: Dict[str, Any], proficiency_score: float, maturity: MaturityLevel) -> Tuple[List[str], List[str]]:
        """Generate strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        if proficiency_score > 0.7:
            strengths.append("High level of proficiency demonstrated")
        elif proficiency_score < 0.3:
            weaknesses.append("Low proficiency requires improvement")
        
        if maturity == MaturityLevel.MATURE:
            strengths.append("Well-established and systematic approach")
        elif maturity == MaturityLevel.EMERGING:
            weaknesses.append("Capability still in early development stage")
        
        # Add category-specific strengths/weaknesses
        category_keywords = template.get("keywords", [])
        if "innovation" in category_keywords:
            if proficiency_score > 0.6:
                strengths.append("Strong innovation capabilities")
            else:
                weaknesses.append("Limited innovation capacity")
        
        return strengths[:3], weaknesses[:3]
    
    async def _generate_metrics(self, template: Dict[str, Any], category: CapabilityCategory) -> List[str]:
        """Generate metrics for capability"""
        metrics = []
        
        # Category-specific metrics
        if category == CapabilityCategory.TECHNICAL:
            metrics = ["Code quality", "System uptime", "Feature delivery speed", "Bug resolution time"]
        elif category == CapabilityCategory.MARKETING:
            metrics = ["Lead generation", "Conversion rates", "Brand awareness", "Marketing ROI"]
        elif category == CapabilityCategory.SALES:
            metrics = ["Sales cycle length", "Win rate", "Customer acquisition cost", "Revenue growth"]
        elif category == CapabilityCategory.OPERATIONAL:
            metrics = ["Process efficiency", "Quality scores", "Customer satisfaction", "Cost per unit"]
        elif category == CapabilityCategory.STRATEGIC:
            metrics = ["Goal achievement", "Market share growth", "Strategic initiative success", "Competitive positioning"]
        elif category == CapabilityCategory.FINANCIAL:
            metrics = ["Revenue growth", "Profit margins", "Cash flow", "Return on investment"]
        elif category == CapabilityCategory.LEADERSHIP:
            metrics = ["Employee engagement", "Team performance", "Retention rates", "Leadership effectiveness"]
        elif category == CapabilityCategory.INNOVATION:
            metrics = ["Innovation pipeline", "Time to market", "Innovation success rate", "Patent filings"]
        
        return metrics
    
    async def _calculate_category_scores(self, capabilities: List[Capability]) -> Dict[str, float]:
        """Calculate scores for each capability category"""
        category_scores = defaultdict(list)
        
        for capability in capabilities:
            category_scores[capability.category.value].append(capability.proficiency_score)
        
        # Calculate average score for each category
        final_scores = {}
        for category, scores in category_scores.items():
            if scores:
                final_scores[category] = sum(scores) / len(scores)
            else:
                final_scores[category] = 0.0
        
        return final_scores
    
    async def _analyze_competitive_positioning(self, capabilities: List[Capability], competitive_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive positioning based on capabilities"""
        # Count capabilities by level
        level_counts = defaultdict(int)
        for capability in capabilities:
            level_counts[capability.level.value] += 1
        
        # Calculate competitive advantage score
        total_advantage = sum(capability.competitive_advantage for capability in capabilities)
        average_advantage = total_advantage / len(capabilities) if capabilities else 0.0
        
        # Identify key differentiators
        key_differentiators = [
            capability.name for capability in capabilities 
            if capability.level in [CapabilityLevel.ONLY_YOU, CapabilityLevel.UNIQUE]
        ]
        
        return {
            "capability_distribution": dict(level_counts),
            "competitive_advantage_score": average_advantage,
            "key_differentiators": key_differentiators,
            "positioning_strength": "Strong" if average_advantage > 0.6 else "Moderate" if average_advantage > 0.3 else "Weak"
        }
    
    async def _identify_development_priorities(self, capabilities: List[Capability], category_scores: Dict[str, float]) -> List[str]:
        """Identify development priorities"""
        # Sort capabilities by development priority
        sorted_capabilities = sorted(capabilities, key=lambda x: x.development_priority, reverse=True)
        
        # Get top priorities
        top_priorities = []
        for capability in sorted_capabilities[:5]:
            priority_desc = f"{capability.name} ({capability.category.value})"
            top_priorities.append(priority_desc)
        
        return top_priorities
    
    async def _identify_capability_gaps(self, capabilities: List[Capability], competitive_context: Dict[str, Any]) -> List[str]:
        """Identify capability gaps"""
        gaps = []
        
        # Low proficiency capabilities
        low_proficiency = [
            capability.name for capability in capabilities 
            if capability.proficiency_score < 0.4
        ]
        
        # Table stakes capabilities
        table_stakes = [
            capability.name for capability in capabilities 
            if capability.level == CapabilityLevel.TABLE_STAKES and capability.proficiency_score < 0.6
        ]
        
        gaps.extend([f"Improve proficiency: {', '.join(low_proficiency[:3])}"])
        gaps.extend([f"Strengthen table stakes: {', '.join(table_stakes[:3])}"])
        
        return gaps[:5]  # Top 5 gaps
    
    async def _generate_strategic_recommendations(self, capabilities: List[Capability], category_scores: Dict[str, float], competitive_positioning: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Based on competitive positioning
        if competitive_positioning["competitive_advantage_score"] < 0.3:
            recommendations.append("Focus on building unique competitive advantages")
        
        # Based on category scores
        weak_categories = [cat for cat, score in category_scores.items() if score < 0.5]
        if weak_categories:
            recommendations.append(f"Strengthen capabilities in: {', '.join(weak_categories[:2])}")
        
        # Based on capability levels
        only_you_capabilities = [cap for cap in capabilities if cap.level == CapabilityLevel.ONLY_YOU]
        if only_you_capabilities:
            recommendations.append("Leverage and protect 'Only You' capabilities")
        
        # General recommendations
        recommendations.extend([
            "Develop systematic capability measurement",
            "Create capability development roadmap",
            "Align capability development with business strategy"
        ])
        
        return recommendations[:8]  # Top 8 recommendations
    
    async def _create_implementation_roadmap(self, capabilities: List[Capability], development_priorities: List[str]) -> Dict[str, List[str]]:
        """Create implementation roadmap"""
        roadmap = {
            "immediate": [],  # 0-3 months
            "short_term": [],  # 3-6 months
            "medium_term": [],  # 6-12 months
            "long_term": []  # 12+ months
        }
        
        # Sort capabilities by development priority
        sorted_capabilities = sorted(capabilities, key=lambda x: x.development_priority, reverse=True)
        
        # Assign to roadmap phases
        for i, capability in enumerate(sorted_capabilities):
            action = f"Develop {capability.name} capability"
            
            if i < 2:
                roadmap["immediate"].append(action)
            elif i < 5:
                roadmap["short_term"].append(action)
            elif i < 10:
                roadmap["medium_term"].append(action)
            else:
                roadmap["long_term"].append(action)
        
        return roadmap


# Export service
__all__ = ["CapabilityRatingSystem", "CapabilityAssessment", "Capability"]
