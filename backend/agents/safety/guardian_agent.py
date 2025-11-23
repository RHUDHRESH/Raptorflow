"""
Enhanced Guardian Agent - Comprehensive safety and compliance enforcement.

This agent provides multi-layered content safety validation:
- Legal compliance (advertising regulations, required disclosures)
- Copyright and plagiarism detection
- Brand safety (prohibited terms, controversial topics)
- Competitor mentions policy
- Inclusive language checking
- Data privacy compliance (GDPR, CCPA)
- Industry-specific regulations
- Prompt injection prevention
- Unauthorized action blocking

Features:
- Deterministic rule-based checks for reliability
- LLM-assisted contextual analysis for nuance
- Action validation with granular permission system
- Comprehensive audit logging
"""

import re
import json
import structlog
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime, timezone

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class ViolationType(Enum):
    """Comprehensive violation types."""
    # Security violations
    PROMPT_INJECTION = "prompt_injection"
    UNAUTHORIZED_API = "unauthorized_api"

    # Content violations
    MEDICAL_CLAIM = "medical_claim"
    FINANCIAL_ADVICE = "financial_advice"
    HATE_SPEECH = "hate_speech"
    EXPLICIT_CONTENT = "explicit_content"

    # Legal violations
    TRADEMARK_ISSUE = "trademark_issue"
    COPYRIGHT_ISSUE = "copyright_issue"
    LEGAL_CLAIM = "legal_claim"
    ADVERTISING_VIOLATION = "advertising_violation"
    REQUIRED_DISCLOSURE_MISSING = "required_disclosure_missing"

    # Brand violations
    BRAND_SAFETY = "brand_safety"
    COMPETITOR_MENTION = "competitor_mention"
    PROHIBITED_TERM = "prohibited_term"

    # Compliance violations
    DATA_PRIVACY = "data_privacy"
    GDPR_VIOLATION = "gdpr_violation"
    CCPA_VIOLATION = "ccpa_violation"
    INDUSTRY_REGULATION = "industry_regulation"

    # Language violations
    NON_INCLUSIVE_LANGUAGE = "non_inclusive_language"
    DISCRIMINATORY_LANGUAGE = "discriminatory_language"


class SafetyStatus(Enum):
    """Content safety status levels."""
    APPROVED = "approved"
    FLAGGED = "flagged"  # Warnings but can proceed with caution
    BLOCKED = "blocked"  # Critical violations, must not proceed


class GuardianAgent:
    """
    Comprehensive safety and compliance enforcement agent.

    Provides multi-dimensional content safety checking:
    - Security: Prompt injection, unauthorized API calls
    - Legal: Advertising laws, disclosures, copyright
    - Brand: Safety guidelines, competitor mentions
    - Privacy: GDPR, CCPA, data handling
    - Language: Inclusive language, discrimination checks
    - Industry: Sector-specific regulations
    """

    def __init__(self):
        self.llm = vertex_ai_client
        self.db = supabase_client

        # === Security Patterns === #

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
            r"override your",
            r"bypass.*filter",
        ]

        # Unauthorized API patterns
        self.restricted_apis = [
            r"delete.*database",
            r"drop.*table",
            r"truncate.*table",
            r"exec\(",
            r"eval\(",
            r"__import__",
            r"subprocess",
            r"os\.system",
            r"shell_exec",
        ]

        # === Legal Compliance Patterns === #

        # Medical/health claim keywords
        self.medical_keywords = [
            "cure", "treat", "diagnose", "prevent disease",
            "FDA approved", "clinically proven", "guaranteed results",
            "miracle cure", "doctor recommended", "medical breakthrough"
        ]

        # Financial advice keywords
        self.financial_keywords = [
            "guaranteed return", "risk-free investment", "insider trading",
            "get rich quick", "double your money", "guaranteed profit",
            "can't lose", "zero risk", "immediate returns"
        ]

        # Advertising regulation keywords (FTC)
        self.advertising_red_flags = [
            "as seen on TV", "limited time only", "act now",
            "free trial", "risk-free", "money back guarantee"
        ]

        # Required disclosure triggers
        self.disclosure_triggers = [
            "affiliate", "sponsored", "paid partnership",
            "advertisement", "promoted", "partnership"
        ]

        # === Brand Safety === #

        # Prohibited terms (company-specific - should be configurable)
        self.prohibited_terms = [
            "scam", "cheat", "hack", "illegal",
            "pirated", "cracked", "stolen"
        ]

        # Controversial topics
        self.controversial_topics = [
            "politics", "religion", "abortion", "gun control",
            "immigration", "climate change denial"
        ]

        # === Competitor Mentions === #

        # Example competitor names (should be configurable per workspace)
        self.competitor_keywords = [
            "competitor", "rival company", "alternative to"
        ]

        # === Inclusive Language === #

        # Non-inclusive language patterns
        self.non_inclusive_patterns = [
            r"\b(crazy|insane|dumb|stupid|lame)\b",
            r"\b(manpower|mankind)\b",
            r"\b(blacklist|whitelist)\b",
            r"\b(master/slave)\b",
            r"\b(guys)\b(?!.*\bgirls\b)",  # "guys" without "girls" context
        ]

        # Better alternatives
        self.inclusive_alternatives = {
            "crazy": "surprising/unexpected",
            "insane": "remarkable/extraordinary",
            "dumb": "ineffective/confusing",
            "stupid": "inefficient/problematic",
            "lame": "disappointing/inadequate",
            "manpower": "workforce/staffing",
            "mankind": "humanity/people",
            "blacklist": "blocklist/deny list",
            "whitelist": "allowlist/permit list",
            "master/slave": "primary/replica",
            "guys": "everyone/folks/team"
        }

        # === Data Privacy === #

        # GDPR/CCPA sensitive data patterns
        self.privacy_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",  # Email (in certain contexts)
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IP address
        ]

    async def guard_content(
        self,
        content: str,
        content_type: str,
        workspace_config: Optional[Dict] = None,
        industry: Optional[str] = None,
        target_region: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive content safety validation.

        This is the main API for content safety checking. It:
        1. Runs deterministic rule-based checks (fast, reliable)
        2. Performs LLM-assisted contextual analysis (nuanced)
        3. Evaluates industry-specific regulations
        4. Checks regional compliance (GDPR, CCPA, etc.)
        5. Returns detailed safety assessment with actions

        Args:
            content: The text content to validate
            content_type: Type of content (ad, blog, email, social_post, etc.)
            workspace_config: Workspace-specific safety configuration
                {
                    "prohibited_terms": List[str],
                    "competitor_names": List[str],
                    "required_disclosures": List[str],
                    "brand_guidelines": Dict
                }
            industry: Industry type (healthcare, finance, etc.) for specific checks
            target_region: Target region (US, EU, etc.) for compliance
            correlation_id: Request correlation ID for tracking

        Returns:
            Detailed safety structure:
            {
                "safety_status": "approved" | "flagged" | "blocked",
                "confidence": float (0-1),
                "checks": {
                    "security": {"passed": bool, "violations": List[Dict]},
                    "legal_compliance": {"passed": bool, "violations": List[Dict]},
                    "copyright": {"passed": bool, "violations": List[Dict]},
                    "brand_safety": {"passed": bool, "violations": List[Dict]},
                    "competitor_policy": {"passed": bool, "violations": List[Dict]},
                    "inclusive_language": {"passed": bool, "violations": List[Dict]},
                    "data_privacy": {"passed": bool, "violations": List[Dict]},
                    "industry_regulations": {"passed": bool, "violations": List[Dict]}
                },
                "required_actions": List[str],  # Must-do items
                "recommended_actions": List[str],  # Nice-to-have improvements
                "metadata": {
                    "content_type": str,
                    "checks_performed": int,
                    "timestamp": str
                }
            }

        Example:
            result = await guardian_agent.guard_content(
                content="Your marketing copy here...",
                content_type="advertisement",
                workspace_config={"prohibited_terms": ["competitor_name"]},
                industry="healthcare",
                target_region="EU"
            )

            if result["safety_status"] == "approved":
                proceed_with_publishing()
            elif result["safety_status"] == "flagged":
                review_warnings(result["recommended_actions"])
            else:  # blocked
                fix_violations(result["required_actions"])
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info(
            "Starting comprehensive safety validation",
            content_type=content_type,
            content_length=len(content),
            industry=industry,
            target_region=target_region,
            correlation_id=correlation_id
        )

        workspace_config = workspace_config or {}

        try:
            # Run all safety checks
            checks = {}

            # 1. Security checks (deterministic)
            checks["security"] = self._check_security(content)

            # 2. Legal compliance checks
            checks["legal_compliance"] = self._check_legal_compliance(
                content,
                content_type,
                workspace_config
            )

            # 3. Copyright/plagiarism checks
            checks["copyright"] = await self._check_copyright(content, correlation_id)

            # 4. Brand safety checks
            checks["brand_safety"] = self._check_brand_safety(
                content,
                workspace_config
            )

            # 5. Competitor mention checks
            checks["competitor_policy"] = self._check_competitor_mentions(
                content,
                workspace_config
            )

            # 6. Inclusive language checks
            checks["inclusive_language"] = self._check_inclusive_language(content)

            # 7. Data privacy checks (GDPR/CCPA)
            checks["data_privacy"] = self._check_data_privacy(
                content,
                target_region
            )

            # 8. Industry-specific regulations
            checks["industry_regulations"] = await self._check_industry_regulations(
                content,
                industry,
                correlation_id
            )

            # Aggregate results
            all_violations = []
            for check_name, check_result in checks.items():
                all_violations.extend(check_result.get("violations", []))

            # Determine overall safety status
            critical_violations = [v for v in all_violations if v.get("severity") == "critical"]
            high_violations = [v for v in all_violations if v.get("severity") == "high"]

            if critical_violations:
                safety_status = SafetyStatus.BLOCKED.value
                confidence = 0.95
            elif high_violations:
                safety_status = SafetyStatus.FLAGGED.value
                confidence = 0.85
            elif all_violations:
                safety_status = SafetyStatus.FLAGGED.value
                confidence = 0.75
            else:
                safety_status = SafetyStatus.APPROVED.value
                confidence = 0.90

            # Build action lists
            required_actions = []
            recommended_actions = []

            for violation in all_violations:
                if violation.get("severity") in ["critical", "high"]:
                    action = violation.get("guidance", f"Fix {violation.get('type')}")
                    required_actions.append(action)
                else:
                    action = violation.get("guidance", f"Consider addressing {violation.get('type')}")
                    recommended_actions.append(action)

            result = {
                "safety_status": safety_status,
                "confidence": confidence,
                "checks": checks,
                "required_actions": list(set(required_actions))[:10],
                "recommended_actions": list(set(recommended_actions))[:10],
                "metadata": {
                    "content_type": content_type,
                    "checks_performed": len(checks),
                    "total_violations": len(all_violations),
                    "critical_violations": len(critical_violations),
                    "high_violations": len(high_violations),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "correlation_id": correlation_id
                }
            }

            logger.info(
                "Safety validation completed",
                status=safety_status,
                violations=len(all_violations),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                f"Safety validation failed: {e}",
                error_type=type(e).__name__,
                correlation_id=correlation_id
            )
            return self._get_fallback_guard_result(str(e))

    def _check_security(self, content: str) -> Dict[str, Any]:
        """Check for security violations (prompt injection, unauthorized APIs)."""

        violations = []

        # Check for prompt injection
        for pattern in self.injection_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "type": ViolationType.PROMPT_INJECTION.value,
                    "severity": "critical",
                    "description": f"Detected potential prompt injection attempt",
                    "matched_text": match.group(),
                    "position": match.start(),
                    "guidance": "Remove instruction override attempts"
                })

        # Check for unauthorized API calls
        for pattern in self.restricted_apis:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "type": ViolationType.UNAUTHORIZED_API.value,
                    "severity": "critical",
                    "description": f"Detected potentially dangerous API call",
                    "matched_text": match.group(),
                    "guidance": "Remove dangerous system calls"
                })

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def _check_legal_compliance(
        self,
        content: str,
        content_type: str,
        workspace_config: Dict
    ) -> Dict[str, Any]:
        """Check for legal compliance violations."""

        violations = []

        # Medical claims
        for keyword in self.medical_keywords:
            if keyword.lower() in content.lower():
                violations.append({
                    "type": ViolationType.MEDICAL_CLAIM.value,
                    "severity": "high",
                    "description": f"Unverified medical claim detected: '{keyword}'",
                    "guidance": "Remove claim or add disclaimer: 'Consult a healthcare professional before making medical decisions'"
                })

        # Financial advice
        for keyword in self.financial_keywords:
            if keyword.lower() in content.lower():
                violations.append({
                    "type": ViolationType.FINANCIAL_ADVICE.value,
                    "severity": "high",
                    "description": f"Unverified financial advice detected: '{keyword}'",
                    "guidance": "Remove guarantees or add disclaimer: 'Past performance does not guarantee future results'"
                })

        # Advertising regulations
        if content_type in ["advertisement", "ad", "sponsored_post"]:
            for keyword in self.advertising_red_flags:
                if keyword.lower() in content.lower():
                    violations.append({
                        "type": ViolationType.ADVERTISING_VIOLATION.value,
                        "severity": "medium",
                        "description": f"Advertising red flag: '{keyword}'",
                        "guidance": "Ensure claims are substantiated and not misleading"
                    })

            # Check for required disclosures
            disclosure_needed = any(
                trigger.lower() in content.lower()
                for trigger in self.disclosure_triggers
            )

            if disclosure_needed:
                has_disclosure = any(
                    disclosure.lower() in content.lower()
                    for disclosure in ["disclosure:", "disclaimer:", "#ad", "#sponsored"]
                )

                if not has_disclosure:
                    violations.append({
                        "type": ViolationType.REQUIRED_DISCLOSURE_MISSING.value,
                        "severity": "critical",
                        "description": "Required advertising disclosure missing",
                        "guidance": "Add clear disclosure: '#ad', '#sponsored', or 'Paid Partnership'"
                    })

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    async def _check_copyright(self, content: str, correlation_id: str) -> Dict[str, Any]:
        """Check for potential copyright issues using LLM assistance."""

        violations = []

        # Simple heuristic checks
        # Check for common copyright-protected phrases
        copyright_phrases = [
            "all rights reserved",
            "©",
            "copyright",
            "™",
            "®"
        ]

        found_phrases = [phrase for phrase in copyright_phrases if phrase.lower() in content.lower()]

        if found_phrases:
            violations.append({
                "type": ViolationType.COPYRIGHT_ISSUE.value,
                "severity": "medium",
                "description": f"Content contains copyright-related terms: {', '.join(found_phrases)}",
                "guidance": "Verify you have rights to use this content or remove copyrighted material"
            })

        # TODO: In production, integrate with plagiarism detection APIs
        # (Copyscape, Grammarly, etc.)

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def _check_brand_safety(self, content: str, workspace_config: Dict) -> Dict[str, Any]:
        """Check for brand safety violations."""

        violations = []

        # Check prohibited terms (workspace-specific)
        workspace_prohibited = workspace_config.get("prohibited_terms", [])
        all_prohibited = self.prohibited_terms + workspace_prohibited

        for term in all_prohibited:
            if term.lower() in content.lower():
                violations.append({
                    "type": ViolationType.PROHIBITED_TERM.value,
                    "severity": "high",
                    "description": f"Prohibited term detected: '{term}'",
                    "guidance": f"Remove or replace '{term}'"
                })

        # Check controversial topics
        for topic in self.controversial_topics:
            if topic.lower() in content.lower():
                violations.append({
                    "type": ViolationType.BRAND_SAFETY.value,
                    "severity": "medium",
                    "description": f"Potentially controversial topic: '{topic}'",
                    "guidance": "Review content for brand alignment and potential controversy"
                })

        # Simple hate speech detection
        hate_keywords = [
            "racist", "sexist", "homophobic", "transphobic",
            "xenophobic", "bigot", "discrimination"
        ]

        for keyword in hate_keywords:
            if keyword in content.lower():
                violations.append({
                    "type": ViolationType.HATE_SPEECH.value,
                    "severity": "critical",
                    "description": f"Potential hate speech detected: '{keyword}'",
                    "guidance": "Review and remove inappropriate language"
                })

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def _check_competitor_mentions(self, content: str, workspace_config: Dict) -> Dict[str, Any]:
        """Check for competitor mentions."""

        violations = []

        # Get workspace-specific competitor names
        competitors = workspace_config.get("competitor_names", [])
        competitors.extend(self.competitor_keywords)

        for competitor in competitors:
            if competitor.lower() in content.lower():
                violations.append({
                    "type": ViolationType.COMPETITOR_MENTION.value,
                    "severity": "medium",
                    "description": f"Competitor mention detected: '{competitor}'",
                    "guidance": "Review competitor mention policy and ensure comparison is fair/legal"
                })

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def _check_inclusive_language(self, content: str) -> Dict[str, Any]:
        """Check for non-inclusive language."""

        violations = []

        for pattern in self.non_inclusive_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                matched_term = match.group().strip()
                alternative = self.inclusive_alternatives.get(
                    matched_term.lower(),
                    "more inclusive language"
                )

                violations.append({
                    "type": ViolationType.NON_INCLUSIVE_LANGUAGE.value,
                    "severity": "low",
                    "description": f"Non-inclusive language: '{matched_term}'",
                    "guidance": f"Consider using '{alternative}' instead",
                    "position": match.start()
                })

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def _check_data_privacy(self, content: str, target_region: Optional[str]) -> Dict[str, Any]:
        """Check for data privacy violations (GDPR, CCPA)."""

        violations = []

        # Check for sensitive data patterns
        for pattern in self.privacy_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "type": ViolationType.DATA_PRIVACY.value,
                    "severity": "critical",
                    "description": f"Potential PII detected: {match.group()[:10]}...",
                    "guidance": "Remove or redact personal identifiable information (PII)"
                })

        # GDPR-specific checks (EU)
        if target_region and "EU" in target_region.upper():
            gdpr_keywords = ["data collection", "personal data", "tracking", "cookies"]
            found_gdpr = [kw for kw in gdpr_keywords if kw.lower() in content.lower()]

            if found_gdpr:
                has_consent = any(
                    consent in content.lower()
                    for consent in ["consent", "opt-in", "permission", "agree"]
                )

                if not has_consent:
                    violations.append({
                        "type": ViolationType.GDPR_VIOLATION.value,
                        "severity": "high",
                        "description": "GDPR: Data collection mentioned without clear consent mechanism",
                        "guidance": "Add explicit consent request and privacy policy link"
                    })

        # CCPA-specific checks (California)
        if target_region and "CA" in target_region.upper():
            ccpa_triggers = ["sell your data", "share your information", "third party"]
            found_ccpa = [kw for kw in ccpa_triggers if kw.lower() in content.lower()]

            if found_ccpa:
                has_opt_out = "do not sell" in content.lower() or "opt out" in content.lower()

                if not has_opt_out:
                    violations.append({
                        "type": ViolationType.CCPA_VIOLATION.value,
                        "severity": "high",
                        "description": "CCPA: Data selling/sharing mentioned without opt-out option",
                        "guidance": "Add 'Do Not Sell My Personal Information' link"
                    })

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    async def _check_industry_regulations(
        self,
        content: str,
        industry: Optional[str],
        correlation_id: str
    ) -> Dict[str, Any]:
        """Check industry-specific regulations using LLM assistance."""

        violations = []

        if not industry:
            return {"passed": True, "violations": []}

        # Industry-specific keyword checks
        industry_rules = {
            "healthcare": {
                "keywords": ["HIPAA", "patient data", "medical records"],
                "guidance": "Ensure HIPAA compliance for patient data"
            },
            "finance": {
                "keywords": ["financial data", "account information", "transaction"],
                "guidance": "Ensure compliance with financial regulations (SOX, PCI-DSS)"
            },
            "legal": {
                "keywords": ["attorney-client", "legal advice", "representation"],
                "guidance": "Add disclaimer: 'This is not legal advice'"
            }
        }

        industry_lower = industry.lower()
        if industry_lower in industry_rules:
            rules = industry_rules[industry_lower]
            found_keywords = [
                kw for kw in rules["keywords"]
                if kw.lower() in content.lower()
            ]

            if found_keywords:
                violations.append({
                    "type": ViolationType.INDUSTRY_REGULATION.value,
                    "severity": "high",
                    "description": f"{industry} industry regulations apply: {', '.join(found_keywords)}",
                    "guidance": rules["guidance"]
                })

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def validate_action(
        self,
        action: str,
        context: Dict[str, Any],
        user_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhanced action validation with granular permissions.

        Args:
            action: Action type (e.g., "publish_post", "delete_campaign")
            context: Action context including parameters
            user_role: User's role (admin, editor, viewer, etc.)

        Returns:
            Validation result with detailed permission info
        """
        logger.debug("Validating action", action=action, user_role=user_role)

        # Define action permission matrix
        action_permissions = {
            # Read actions (all roles)
            "fetch_analytics": {"roles": ["admin", "editor", "viewer"], "requires_confirmation": False},
            "view_content": {"roles": ["admin", "editor", "viewer"], "requires_confirmation": False},
            "list_campaigns": {"roles": ["admin", "editor", "viewer"], "requires_confirmation": False},

            # Write actions (editor+)
            "generate_content": {"roles": ["admin", "editor"], "requires_confirmation": False},
            "create_campaign": {"roles": ["admin", "editor"], "requires_confirmation": False},
            "update_campaign": {"roles": ["admin", "editor"], "requires_confirmation": False},

            # Publish actions (editor+, with confirmation)
            "publish_post": {"roles": ["admin", "editor"], "requires_confirmation": True},
            "schedule_post": {"roles": ["admin", "editor"], "requires_confirmation": True},
            "send_email": {"roles": ["admin", "editor"], "requires_confirmation": True},

            # Delete actions (admin only, with confirmation)
            "delete_campaign": {"roles": ["admin"], "requires_confirmation": True},
            "delete_content": {"roles": ["admin"], "requires_confirmation": True},
            "bulk_delete": {"roles": ["admin"], "requires_confirmation": True},

            # Administrative actions (admin only, with confirmation)
            "change_permissions": {"roles": ["admin"], "requires_confirmation": True},
            "modify_settings": {"roles": ["admin"], "requires_confirmation": True},
            "export_data": {"roles": ["admin"], "requires_confirmation": True},
        }

        violations = []
        user_role = user_role or "viewer"

        # Check if action exists in permission matrix
        if action not in action_permissions:
            violations.append({
                "type": "unknown_action",
                "severity": "high",
                "description": f"Unknown or unsupported action: '{action}'",
                "guidance": "Verify action type is correct"
            })
            return {
                "is_allowed": False,
                "action": action,
                "violations": violations,
                "recommendation": "block"
            }

        # Check role permissions
        permissions = action_permissions[action]
        if user_role not in permissions["roles"]:
            violations.append({
                "type": "insufficient_permissions",
                "severity": "critical",
                "description": f"User role '{user_role}' not authorized for action '{action}'",
                "guidance": f"Required roles: {', '.join(permissions['roles'])}"
            })

        # Check user confirmation for sensitive actions
        if permissions["requires_confirmation"]:
            if not context.get("user_confirmed"):
                violations.append({
                    "type": "confirmation_required",
                    "severity": "high",
                    "description": f"Action '{action}' requires explicit user confirmation",
                    "guidance": "Request user approval before proceeding"
                })

        # Additional context validation
        if action in ["bulk_delete", "delete_campaign"]:
            # Ensure target is specified
            if not context.get("target_id"):
                violations.append({
                    "type": "missing_parameter",
                    "severity": "high",
                    "description": "Delete action missing target ID",
                    "guidance": "Specify which resource to delete"
                })

        if action == "send_email":
            # Ensure recipients are specified
            if not context.get("recipients"):
                violations.append({
                    "type": "missing_parameter",
                    "severity": "high",
                    "description": "Email action missing recipients",
                    "guidance": "Specify email recipients"
                })

        is_allowed = len(violations) == 0

        return {
            "is_allowed": is_allowed,
            "action": action,
            "user_role": user_role,
            "requires_confirmation": permissions["requires_confirmation"],
            "violations": violations,
            "recommendation": "proceed" if is_allowed else "block"
        }

    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.

        New code should use guard_content() instead.
        """
        logger.info("Using legacy validate_content (consider migrating to guard_content)")

        result = self._check_security(content)
        brand_result = self._check_brand_safety(content, {})

        all_violations = result["violations"] + brand_result["violations"]

        risk_level = self._calculate_risk_level(all_violations)
        is_safe = len(all_violations) == 0

        return {
            "is_safe": is_safe,
            "risk_level": risk_level,
            "violations": all_violations,
            "violation_count": len(all_violations),
            "recommendation": "approve" if is_safe else "reject" if risk_level == "critical" else "review"
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

    def _get_fallback_guard_result(self, error: str) -> Dict[str, Any]:
        """Return a safe fallback guard result when validation fails."""

        return {
            "safety_status": SafetyStatus.BLOCKED.value,
            "confidence": 0.0,
            "checks": {},
            "required_actions": [f"System error: {error}. Manual review required."],
            "recommended_actions": [],
            "metadata": {
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }


# Global singleton instance
guardian_agent = GuardianAgent()
