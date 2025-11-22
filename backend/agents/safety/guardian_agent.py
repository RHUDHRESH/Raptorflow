"""
Guardian Agent - Deterministic rule engine for safety and compliance.
Prevents unauthorized actions, prompt injection, and policy violations.
"""

import re
import structlog
from typing import Dict, Any, List, Optional
from enum import Enum

logger = structlog.get_logger(__name__)


class ViolationType(Enum):
    """Types of policy violations."""
    PROMPT_INJECTION = "prompt_injection"
    UNAUTHORIZED_API = "unauthorized_api"
    MEDICAL_CLAIM = "medical_claim"
    FINANCIAL_ADVICE = "financial_advice"
    HATE_SPEECH = "hate_speech"
    EXPLICIT_CONTENT = "explicit_content"
    TRADEMARK_ISSUE = "trademark_issue"
    LEGAL_CLAIM = "legal_claim"


class GuardianAgent:
    """
    Deterministic safety layer enforcing rules and compliance.
    Acts as a gatekeeper before content is generated or actions are executed.
    """
    
    def __init__(self):
        # Prompt injection patterns
        self.injection_patterns = [
            r"ignore previous instructions",
            r"disregard.{0,20}instructions",
            r"forget.{0,20}system prompt",
            r"you are now",
            r"new role:",
            r"act as",
            r"pretend you are",
            r"</system>",
            r"<\|im_start\|>",
            r"jailbreak",
        ]
        
        # Unauthorized API patterns
        self.restricted_apis = [
            r"delete.*database",
            r"drop.*table",
            r"exec\(",
            r"eval\(",
            r"__import__",
            r"subprocess",
            r"os\.system",
        ]
        
        # Medical/health claim keywords
        self.medical_keywords = [
            "cure", "treat", "diagnose", "prevent disease",
            "FDA approved", "clinically proven", "guaranteed results"
        ]
        
        # Financial advice keywords
        self.financial_keywords = [
            "guaranteed return", "risk-free investment", "insider trading",
            "get rich quick", "double your money"
        ]
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        Validates content against safety rules.
        
        Args:
            content: Text to validate
            
        Returns:
            Validation result with violations if any
        """
        logger.debug("Validating content", content_length=len(content))
        
        violations = []
        
        # Check for prompt injection
        for pattern in self.injection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append({
                    "type": ViolationType.PROMPT_INJECTION.value,
                    "severity": "critical",
                    "description": f"Detected prompt injection attempt: {pattern}",
                    "matched_text": re.search(pattern, content, re.IGNORECASE).group()
                })
        
        # Check for unauthorized API calls (in code context)
        for pattern in self.restricted_apis:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append({
                    "type": ViolationType.UNAUTHORIZED_API.value,
                    "severity": "critical",
                    "description": f"Detected potentially dangerous API call: {pattern}"
                })
        
        # Check for medical claims
        for keyword in self.medical_keywords:
            if keyword.lower() in content.lower():
                violations.append({
                    "type": ViolationType.MEDICAL_CLAIM.value,
                    "severity": "high",
                    "description": f"Detected unverified medical claim: '{keyword}'",
                    "guidance": "Remove or add disclaimer: 'Consult a healthcare professional'"
                })
        
        # Check for financial advice
        for keyword in self.financial_keywords:
            if keyword.lower() in content.lower():
                violations.append({
                    "type": ViolationType.FINANCIAL_ADVICE.value,
                    "severity": "high",
                    "description": f"Detected unverified financial advice: '{keyword}'",
                    "guidance": "Add disclaimer or remove guarantees"
                })
        
        # Simple hate speech detection (basic keywords - would use ML in production)
        hate_keywords = ["racist", "sexist", "homophobic", "hate"]
        if any(keyword in content.lower() for keyword in hate_keywords):
            violations.append({
                "type": ViolationType.HATE_SPEECH.value,
                "severity": "critical",
                "description": "Content may contain inappropriate language",
                "guidance": "Review and revise language"
            })
        
        is_safe = len(violations) == 0
        risk_level = self._calculate_risk_level(violations)
        
        return {
            "is_safe": is_safe,
            "risk_level": risk_level,
            "violations": violations,
            "violation_count": len(violations),
            "recommendation": "approve" if is_safe else "reject" if risk_level == "critical" else "review"
        }
    
    def validate_action(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates an agent action before execution.
        
        Args:
            action: Action type (e.g., "publish_post", "delete_campaign")
            context: Action context
            
        Returns:
            Validation result
        """
        logger.debug("Validating action", action=action)
        
        # Define allowed actions
        allowed_actions = {
            "generate_content",
            "publish_post",
            "schedule_post",
            "create_campaign",
            "update_campaign",
            "fetch_analytics",
            "send_email"
        }
        
        # Define restricted actions (require explicit user confirmation)
        restricted_actions = {
            "delete_campaign",
            "delete_content",
            "bulk_delete",
            "change_permissions"
        }
        
        violations = []
        
        if action in restricted_actions:
            if not context.get("user_confirmed"):
                violations.append({
                    "type": "unauthorized_action",
                    "severity": "high",
                    "description": f"Action '{action}' requires explicit user confirmation",
                    "guidance": "Request user approval before proceeding"
                })
        
        if action not in allowed_actions and action not in restricted_actions:
            violations.append({
                "type": "unknown_action",
                "severity": "medium",
                "description": f"Unknown or unsupported action: '{action}'",
                "guidance": "Verify action type is correct"
            })
        
        is_allowed = len(violations) == 0
        
        return {
            "is_allowed": is_allowed,
            "action": action,
            "violations": violations,
            "recommendation": "proceed" if is_allowed else "block"
        }
    
    def _calculate_risk_level(self, violations: List[Dict]) -> str:
        """Calculates overall risk level from violations."""
        if not violations:
            return "none"
        
        severities = [v.get("severity") for v in violations]
        
        if "critical" in severities:
            return "critical"
        elif "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        else:
            return "low"
    
    def sanitize_user_input(self, user_input: str) -> str:
        """
        Sanitizes user input to prevent injection attacks.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Sanitized input
        """
        # Remove potential injection attempts
        sanitized = user_input
        
        for pattern in self.injection_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        
        # Limit length
        max_length = 10000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... [truncated]"
        
        return sanitized


guardian_agent = GuardianAgent()


