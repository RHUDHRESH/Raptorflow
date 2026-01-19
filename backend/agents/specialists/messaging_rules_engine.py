"""
Messaging Rules Engine
Generates and enforces brand messaging guardrails
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class RuleCategory(Enum):
    """Categories for messaging rules"""
    TONE = "tone"
    LANGUAGE = "language"
    CLAIMS = "claims"
    COMPETITORS = "competitors"
    PRICING = "pricing"
    LEGAL = "legal"
    BRAND = "brand"


class RuleSeverity(Enum):
    """Severity level of rule violations"""
    ERROR = "error"  # Must be fixed
    WARNING = "warning"  # Should be fixed
    SUGGESTION = "suggestion"  # Nice to have


class RuleStatus(Enum):
    """Status of a rule"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


@dataclass
class MessagingRule:
    """A single messaging rule/guardrail"""
    id: str
    category: RuleCategory
    name: str
    description: str
    pattern: Optional[str] = None  # Regex pattern to detect
    examples_good: List[str] = field(default_factory=list)
    examples_bad: List[str] = field(default_factory=list)
    severity: RuleSeverity = RuleSeverity.WARNING
    status: RuleStatus = RuleStatus.ACTIVE
    auto_generated: bool = True
    rationale: str = ""


@dataclass
class RuleViolation:
    """A detected rule violation"""
    rule_id: str
    rule_name: str
    category: RuleCategory
    severity: RuleSeverity
    matched_text: str
    suggestion: str
    position: Optional[Tuple[int, int]] = None  # start, end


@dataclass
class ContentCheckResult:
    """Result of checking content against rules"""
    violations: List[RuleViolation]
    passed: bool
    score: float  # 0-100
    summary: str


@dataclass
class MessagingRulesResult:
    """Complete messaging rules result"""
    rules: List[MessagingRule]
    rule_count: int
    categories_covered: List[str]
    recommendations: List[str]
    summary: str


class MessagingRulesEngine:
    """AI-powered messaging rules and guardrails engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rule_counter = 0
        self.default_rules = self._load_default_rules()
    
    def _generate_rule_id(self) -> str:
        """Generate unique rule ID"""
        self.rule_counter += 1
        return f"RUL-{self.rule_counter:03d}"
    
    def _load_default_rules(self) -> List[MessagingRule]:
        """Load default messaging rules"""
        return [
            # Tone rules
            MessagingRule(
                id="RUL-TONE-001",
                category=RuleCategory.TONE,
                name="Avoid Aggressive Language",
                description="Don't use aggressive or combative language toward competitors",
                pattern=r"\b(destroy|kill|crush|annihilate|obliterate)\s+(the\s+)?competition\b",
                examples_good=["We offer a better alternative", "Choose the smarter solution"],
                examples_bad=["We'll destroy the competition", "Kill your old software"],
                severity=RuleSeverity.WARNING,
                rationale="Aggressive language can damage brand perception and alienate potential customers"
            ),
            MessagingRule(
                id="RUL-TONE-002",
                category=RuleCategory.TONE,
                name="Use Confident Not Arrogant Tone",
                description="Be confident but avoid sounding arrogant or dismissive",
                pattern=r"\b(obviously|clearly|anyone can see|only an? (idiot|fool))\b",
                examples_good=["Our approach delivers results", "We've proven this works"],
                examples_bad=["Obviously we're the best", "Anyone can see we're superior"],
                severity=RuleSeverity.SUGGESTION,
                rationale="Arrogance alienates customers who haven't yet made a decision"
            ),
            
            # Claims rules
            MessagingRule(
                id="RUL-CLAIM-001",
                category=RuleCategory.CLAIMS,
                name="Avoid Unverified Superlatives",
                description="Don't use superlatives without proof",
                pattern=r"\b(best|fastest|cheapest|#1|number one|leading|top)\b(?!\s*\d+%)",
                examples_good=["95% of customers rate us highly", "Faster than X by 40%"],
                examples_bad=["The best solution on the market", "The #1 choice"],
                severity=RuleSeverity.WARNING,
                rationale="Unverified superlatives can be legally problematic and reduce trust"
            ),
            MessagingRule(
                id="RUL-CLAIM-002",
                category=RuleCategory.CLAIMS,
                name="Quantify Claims When Possible",
                description="Use specific numbers instead of vague qualifiers",
                pattern=r"\b(significantly|dramatically|massively|hugely|greatly)\s+(improve|increase|reduce|decrease|boost)\b",
                examples_good=["Improve conversion by 35%", "Reduce costs by $10K/month"],
                examples_bad=["Dramatically improve your results", "Significantly boost performance"],
                severity=RuleSeverity.SUGGESTION,
                rationale="Specific numbers are more credible and memorable"
            ),
            
            # Competitor rules
            MessagingRule(
                id="RUL-COMP-001",
                category=RuleCategory.COMPETITORS,
                name="No Direct Competitor Bashing",
                description="Avoid directly criticizing competitors by name",
                pattern=r"\b(unlike|better than|worse than)\s+[A-Z][a-zA-Z]+\b",
                examples_good=["Our unique approach...", "We focus on..."],
                examples_bad=["Unlike Competitor X, we actually work", "Better than HubSpot"],
                severity=RuleSeverity.WARNING,
                rationale="Direct attacks can invite legal issues and make you look petty"
            ),
            
            # Language rules
            MessagingRule(
                id="RUL-LANG-001",
                category=RuleCategory.LANGUAGE,
                name="Avoid Jargon Overload",
                description="Don't use too much industry jargon without explanation",
                pattern=r"\b(synergy|paradigm shift|leverage|holistic|disrupt|pivot|scalable|ecosystem)\b",
                examples_good=["Work together seamlessly", "A new approach to..."],
                examples_bad=["Leverage synergies to disrupt the paradigm"],
                severity=RuleSeverity.SUGGESTION,
                rationale="Jargon can confuse potential customers and reduce clarity"
            ),
            MessagingRule(
                id="RUL-LANG-002",
                category=RuleCategory.LANGUAGE,
                name="Use Active Voice",
                description="Prefer active voice over passive voice",
                pattern=r"\b(is being|was being|has been|have been|will be)\s+\w+ed\b",
                examples_good=["We deliver results", "Our team handles everything"],
                examples_bad=["Results are being delivered", "Everything is handled by our team"],
                severity=RuleSeverity.SUGGESTION,
                rationale="Active voice is clearer and more engaging"
            ),
            
            # Legal/compliance rules
            MessagingRule(
                id="RUL-LEGAL-001",
                category=RuleCategory.LEGAL,
                name="Avoid Guarantee Language",
                description="Be careful with guarantees and promises",
                pattern=r"\b(guarantee|guaranteed|promise|100%|always|never fail)\b",
                examples_good=["We strive for excellence", "Our goal is your success"],
                examples_bad=["Guaranteed results", "We promise 100% satisfaction"],
                severity=RuleSeverity.ERROR,
                rationale="Absolute guarantees can create legal liability"
            ),
            
            # Brand consistency
            MessagingRule(
                id="RUL-BRAND-001",
                category=RuleCategory.BRAND,
                name="Consistent Value Proposition",
                description="Keep value proposition messaging consistent",
                pattern=None,  # Semantic check, no regex
                examples_good=["Focus on your core differentiator"],
                examples_bad=["Contradicting your main message"],
                severity=RuleSeverity.WARNING,
                rationale="Inconsistent messaging confuses customers"
            ),
        ]
    
    def _generate_custom_rules(self, company_info: Dict[str, Any], positioning: Dict[str, Any]) -> List[MessagingRule]:
        """Generate custom rules based on company positioning"""
        custom_rules = []
        
        # Category-specific rules
        category_path = positioning.get("category_path", "safe")
        
        if category_path == "bold":
            custom_rules.append(MessagingRule(
                id=self._generate_rule_id(),
                category=RuleCategory.BRAND,
                name="Emphasize Category Creation",
                description="As a category creator, emphasize the new category, not old comparisons",
                examples_good=["We invented a new way to...", "This is the first..."],
                examples_bad=["Like X but better", "A better version of..."],
                severity=RuleSeverity.WARNING,
                auto_generated=True,
                rationale="Category creators should avoid old category associations"
            ))
        
        # ICP-specific rules
        target_audience = company_info.get("target_audience", "")
        if "enterprise" in target_audience.lower():
            custom_rules.append(MessagingRule(
                id=self._generate_rule_id(),
                category=RuleCategory.TONE,
                name="Professional Enterprise Tone",
                description="Maintain formal, professional tone for enterprise audience",
                pattern=r"\b(awesome|cool|sick|dope|insane|crazy)\b",
                examples_good=["Exceptional performance", "Outstanding results"],
                examples_bad=["This is awesome!", "Crazy good features"],
                severity=RuleSeverity.SUGGESTION,
                auto_generated=True,
                rationale="Enterprise buyers expect professional communication"
            ))
        
        return custom_rules
    
    async def generate_messaging_rules(self, company_info: Dict[str, Any], positioning: Dict[str, Any] = None) -> MessagingRulesResult:
        """
        Generate messaging rules based on company and positioning
        
        Args:
            company_info: Company information
            positioning: Positioning data (category path, ICP, etc.)
        
        Returns:
            MessagingRulesResult with all applicable rules
        """
        positioning = positioning or {}
        
        # Start with default rules
        all_rules = list(self.default_rules)
        
        # Add custom rules based on positioning
        custom_rules = self._generate_custom_rules(company_info, positioning)
        all_rules.extend(custom_rules)
        
        # Get covered categories
        categories = list(set(r.category.value for r in all_rules))
        
        # Generate recommendations
        recommendations = [
            "Review all rules with your marketing team",
            "Customize rules based on your brand voice",
            "Run existing content through the checker to find violations"
        ]
        
        summary = f"Generated {len(all_rules)} messaging rules across {len(categories)} categories. "
        summary += f"Custom rules: {len(custom_rules)}. Default rules: {len(self.default_rules)}."
        
        return MessagingRulesResult(
            rules=all_rules,
            rule_count=len(all_rules),
            categories_covered=categories,
            recommendations=recommendations,
            summary=summary
        )
    
    async def check_content(self, content: str, rules: List[MessagingRule] = None) -> ContentCheckResult:
        """
        Check content against messaging rules
        
        Args:
            content: Content to check
            rules: Rules to check against (uses defaults if not provided)
        
        Returns:
            ContentCheckResult with violations found
        """
        rules = rules or self.default_rules
        violations = []
        
        for rule in rules:
            if rule.status != RuleStatus.ACTIVE:
                continue
            
            if rule.pattern:
                matches = list(re.finditer(rule.pattern, content, re.IGNORECASE))
                for match in matches:
                    violations.append(RuleViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        matched_text=match.group(),
                        suggestion=f"Consider revising: {rule.examples_good[0] if rule.examples_good else 'See rule guidelines'}",
                        position=(match.start(), match.end())
                    ))
        
        # Calculate score
        error_count = sum(1 for v in violations if v.severity == RuleSeverity.ERROR)
        warning_count = sum(1 for v in violations if v.severity == RuleSeverity.WARNING)
        suggestion_count = sum(1 for v in violations if v.severity == RuleSeverity.SUGGESTION)
        
        # Weighted scoring
        score = 100 - (error_count * 20) - (warning_count * 10) - (suggestion_count * 5)
        score = max(0, min(100, score))
        
        passed = error_count == 0 and warning_count <= 2
        
        summary = f"Found {len(violations)} issues: {error_count} errors, {warning_count} warnings, {suggestion_count} suggestions. "
        summary += f"Score: {score}/100. {'Passed' if passed else 'Needs revision'}."
        
        return ContentCheckResult(
            violations=violations,
            passed=passed,
            score=score,
            summary=summary
        )
    
    def get_rules_summary(self, result: MessagingRulesResult) -> Dict[str, Any]:
        """Get summary for display"""
        return {
            "rule_count": result.rule_count,
            "categories": result.categories_covered,
            "summary": result.summary,
            "recommendations": result.recommendations[:3]
        }
