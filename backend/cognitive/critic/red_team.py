"""
Red Team Agent - Security and vulnerability testing

Performs comprehensive security analysis, vulnerability assessment,
and attack simulation to identify potential risks.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from ..models import Severity, Vulnerability, VulnerabilityType

logger = logging.getLogger(__name__)


class RedTeamAgent:
    """Red team agent for security and vulnerability testing."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.security_patterns = self._load_security_patterns()

    async def attack(self, content: str) -> List[Vulnerability]:
        """
        Perform red team attack on content.

        Args:
            content: Content to attack

        Returns:
            List of identified vulnerabilities
        """
        try:
            vulnerabilities = []

            # Multiple attack vectors
            attack_methods = [
                self._attack_factual_accuracy,
                self._attack_logical_reasoning,
                self._attack_security_privacy,
                self._attack_legal_compliance,
                self._attack_brand_reputation,
                self._attack_accessibility,
                self._attack_technical_accuracy,
            ]

            for attack_method in attack_methods:
                try:
                    method_vulnerabilities = await attack_method(content)
                    vulnerabilities.extend(method_vulnerabilities)
                except Exception as e:
                    logger.warning(
                        f"Attack method {attack_method.__name__} failed: {e}"
                    )

            # Deduplicate and prioritize
            vulnerabilities = self._deduplicate_vulnerabilities(vulnerabilities)
            vulnerabilities = self._prioritize_vulnerabilities(vulnerabilities)

            return vulnerabilities

        except Exception as e:
            logger.error(f"Red team attack failed: {e}")
            return [
                Vulnerability(
                    category=VulnerabilityType.TECHNICAL,
                    severity=Severity.HIGH,
                    description=f"Red team analysis failed: {str(e)}",
                    impact="Unable to assess security",
                    mitigation="Fix red team system error",
                )
            ]

    async def _attack_factual_accuracy(self, content: str) -> List[Vulnerability]:
        """Attack factual accuracy of content."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-pro", temperature=0.3, max_tokens=1500
            )

            prompt = f"""
You are a fact-checker trying to find inaccuracies in this content. Be skeptical and question every claim.

Content to fact-check:
---
{content}
---

Look for:
- Unverifiable claims
- Outdated information
- Questionable statistics
- Missing sources
- Overgeneralizations
- Speculation presented as fact

Respond in JSON:
{{
    "factual_vulnerabilities": [
        {{
            "claim": "<specific_claim>",
            "issue": "<what's_wrong_with_it>",
            "severity": "<low|medium|high|critical>",
            "location": "<where_in_content>",
            "impact": "<potential_consequences>",
            "mitigation": "<how_to_fix>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            vulnerabilities = []
            for vuln in data.get("factual_vulnerabilities", []):
                vulnerabilities.append(
                    Vulnerability(
                        category=VulnerabilityType.FACTUAL,
                        severity=Severity(vuln["severity"]),
                        description=vuln["issue"],
                        location=vuln.get("location"),
                        impact=vuln["impact"],
                        mitigation=vuln["mitigation"],
                    )
                )

            return vulnerabilities

        except Exception as e:
            logger.error(f"Factual accuracy attack failed: {e}")
            return []

    async def _attack_logical_reasoning(self, content: str) -> List[Vulnerability]:
        """Attack logical reasoning in content."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-pro", temperature=0.3, max_tokens=1500
            )

            prompt = f"""
You are a logic expert looking for fallacies and weak reasoning in this content.

Content to analyze:
---
{content}
---

Look for logical fallacies:
- Circular reasoning
- False dichotomies
- Hasty generalizations
- Ad hominem attacks
- Slippery slope arguments
- Appeal to emotion without logic
- Correlation vs causation errors

Respond in JSON:
{{
    "logical_vulnerabilities": [
        {{
            "fallacy": "<type_of_fallacy>",
            "description": "<specific_issue>",
            "severity": "<low|medium|high|critical>",
            "location": "<where_in_content>",
            "impact": "<how_this_weakens_argument>",
            "mitigation": "<how_to_fix_reasoning>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            vulnerabilities = []
            for vuln in data.get("logical_vulnerabilities", []):
                vulnerabilities.append(
                    Vulnerability(
                        category=VulnerabilityType.LOGICAL,
                        severity=Severity(vuln["severity"]),
                        description=vuln["description"],
                        location=vuln.get("location"),
                        impact=vuln["impact"],
                        mitigation=vuln["mitigation"],
                    )
                )

            return vulnerabilities

        except Exception as e:
            logger.error(f"Logical reasoning attack failed: {e}")
            return []

    async def _attack_security_privacy(self, content: str) -> List[Vulnerability]:
        """Attack security and privacy aspects."""
        vulnerabilities = []

        # Pattern-based security checks
        security_patterns = [
            (
                r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                "credit_card",
                "Potential credit card number",
            ),
            (
                r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
                "ssn",
                "Potential Social Security number",
            ),
            (
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "email",
                "Email address exposed",
            ),
            (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "ip_address", "IP address exposed"),
            (r"password\s*[:=]\s*\S+", "password", "Password exposed"),
        ]

        for pattern, vuln_type, description in security_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                vulnerabilities.append(
                    Vulnerability(
                        category=VulnerabilityType.SECURITY,
                        severity=Severity.HIGH,
                        description=f"{description}: {len(matches)} instances found",
                        location=f"Pattern: {pattern}",
                        impact="Security/privacy breach risk",
                        mitigation="Remove or redact sensitive information",
                    )
                )

        # LLM-based security analysis
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.1, max_tokens=1000
            )

            prompt = f"""
Analyze this content for security and privacy vulnerabilities:

Content:
---
{content}
---

Look for:
- Personal information exposure
- Security advice that could be dangerous
- Privacy violations
- Data handling issues
- Authentication weaknesses

Respond in JSON:
{{
    "security_vulnerabilities": [
        {{
            "type": "<vulnerability_type>",
            "description": "<specific_issue>",
            "severity": "<low|medium|high|critical>",
            "impact": "<security_impact>",
            "mitigation": "<how_to_fix>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            for vuln in data.get("security_vulnerabilities", []):
                vulnerabilities.append(
                    Vulnerability(
                        category=VulnerabilityType.SECURITY,
                        severity=Severity(vuln["severity"]),
                        description=vuln["description"],
                        impact=vuln["impact"],
                        mitigation=vuln["mitigation"],
                    )
                )

        except Exception as e:
            logger.warning(f"LLM security analysis failed: {e}")

        return vulnerabilities

    async def _attack_legal_compliance(self, content: str) -> List[Vulnerability]:
        """Attack legal and compliance aspects."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-pro", temperature=0.2, max_tokens=1200
            )

            prompt = f"""
You are a legal expert looking for compliance issues in this content.

Content to analyze:
---
{content}
---

Look for legal issues:
- Copyright violations
- Trademark infringement
- Defamation risks
- Privacy law violations
- Regulatory non-compliance
- Liability risks
- Disclaimers needed

Respond in JSON:
{{
    "legal_vulnerabilities": [
        {{
            "issue": "<specific_legal_issue>",
            "description": "<details_of_issue>",
            "severity": "<low|medium|high|critical>",
            "impact": "<legal_consequences>",
            "mitigation": "<how_to_address_legal_issue>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            vulnerabilities = []
            for vuln in data.get("legal_vulnerabilities", []):
                vulnerabilities.append(
                    Vulnerability(
                        category=VulnerabilityType.LEGAL,
                        severity=Severity(vuln["severity"]),
                        description=vuln["description"],
                        impact=vuln["impact"],
                        mitigation=vuln["mitigation"],
                    )
                )

            return vulnerabilities

        except Exception as e:
            logger.error(f"Legal compliance attack failed: {e}")
            return []

    async def _attack_brand_reputation(self, content: str) -> List[Vulnerability]:
        """Attack brand reputation aspects."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.3, max_tokens=1000
            )

            prompt = f"""
You are a brand reputation expert looking for reputation risks in this content.

Content to analyze:
---
{content}
---

Look for brand risks:
- Inappropriate tone
- Off-brand messaging
- Controversial statements
- Poor quality that reflects on brand
- Customer alienation risks
- PR crisis potential

Respond in JSON:
{{
    "brand_vulnerabilities": [
        {{
            "risk": "<specific_brand_risk>",
            "description": "<details_of_risk>",
            "severity": "<low|medium|high|critical>",
            "impact": "<reputation_damage>",
            "mitigation": "<how_to_protect_brand>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            vulnerabilities = []
            for vuln in data.get("brand_vulnerabilities", []):
                vulnerabilities.append(
                    Vulnerability(
                        category=VulnerabilityType.BRAND,
                        severity=Severity(vuln["severity"]),
                        description=vuln["description"],
                        impact=vuln["impact"],
                        mitigation=vuln["mitigation"],
                    )
                )

            return vulnerabilities

        except Exception as e:
            logger.error(f"Brand reputation attack failed: {e}")
            return []

    async def _attack_accessibility(self, content: str) -> List[Vulnerability]:
        """Attack accessibility aspects."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.2, max_tokens=800
            )

            prompt = f"""
You are an accessibility expert looking for accessibility barriers in this content.

Content to analyze:
---
{content}
---

Look for accessibility issues:
- Exclusionary language
- Complex jargon without explanation
- Instructions that assume certain abilities
- Color-dependent information
- Time-based challenges
- Cognitive overload

Respond in JSON:
{{
    "accessibility_vulnerabilities": [
        {{
            "barrier": "<specific_accessibility_barrier>",
            "description": "<details_of_barrier>",
            "severity": "<low|medium|high|critical>",
            "impact": "<accessibility_impact>",
            "mitigation": "<how_to_improve_accessibility>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            vulnerabilities = []
            for vuln in data.get("accessibility_vulnerabilities", []):
                vulnerabilities.append(
                    Vulnerability(
                        category=VulnerabilityType.ACCESSIBILITY,
                        severity=Severity(vuln["severity"]),
                        description=vuln["description"],
                        impact=vuln["impact"],
                        mitigation=vuln["mitigation"],
                    )
                )

            return vulnerabilities

        except Exception as e:
            logger.error(f"Accessibility attack failed: {e}")
            return []

    async def _attack_technical_accuracy(self, content: str) -> List[Vulnerability]:
        """Attack technical accuracy."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-pro", temperature=0.2, max_tokens=1200
            )

            prompt = f"""
You are a technical expert looking for technical inaccuracies in this content.

Content to analyze:
---
{content}
---

Look for technical issues:
- Incorrect procedures
- Outdated technical information
- Unsafe technical advice
- Missing safety warnings
- Technical oversimplifications
- Wrong technical specifications

Respond in JSON:
{{
    "technical_vulnerabilities": [
        {{
            "issue": "<specific_technical_issue>",
            "description": "<details_of_issue>",
            "severity": "<low|medium|high|critical>",
            "impact": "<technical_consequences>",
            "mitigation": "<how_to_fix_technical_issue>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            vulnerabilities = []
            for vuln in data.get("technical_vulnerabilities", []):
                vulnerabilities.append(
                    Vulnerability(
                        category=VulnerabilityType.TECHNICAL,
                        severity=Severity(vuln["severity"]),
                        description=vuln["description"],
                        impact=vuln["impact"],
                        mitigation=vuln["mitigation"],
                    )
                )

            return vulnerabilities

        except Exception as e:
            logger.error(f"Technical accuracy attack failed: {e}")
            return []

    def _deduplicate_vulnerabilities(
        self, vulnerabilities: List[Vulnerability]
    ) -> List[Vulnerability]:
        """Remove duplicate vulnerabilities."""
        seen = set()
        unique_vulnerabilities = []

        for vuln in vulnerabilities:
            # Create a key based on category and description
            key = (vuln.category, vuln.description[:100])  # First 100 chars

            if key not in seen:
                seen.add(key)
                unique_vulnerabilities.append(vuln)

        return unique_vulnerabilities

    def _prioritize_vulnerabilities(
        self, vulnerabilities: List[Vulnerability]
    ) -> List[Vulnerability]:
        """Prioritize vulnerabilities by severity."""
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
        }

        return sorted(vulnerabilities, key=lambda x: severity_order.get(x.severity, 4))

    def _load_security_patterns(self) -> List[tuple]:
        """Load security pattern matching rules."""
        return [
            (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "credit_card"),
            (r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", "ssn"),
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
            (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "ip_address"),
        ]
