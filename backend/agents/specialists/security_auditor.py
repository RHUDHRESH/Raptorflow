import logging
import re
from typing import Any, Dict

logger = logging.getLogger("raptorflow.specialists.security_auditor")


class SecurityAuditorAgent:
    """
    Industrial specialist for PII detection and security policy enforcement.
    Scans agent outputs and telemetry for sensitive information.
    """

    def __init__(self):
        # Basic regex for PII (in a real build, use Presidio or similar)
        self.email_pattern = re.compile(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        )
        self.phone_pattern = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs security scan based on supervisor instructions.
        """
        content_to_scan = state.get("instructions", "")
        logger.info("SecurityAuditor starting PII scan...")

        pii_detected = False
        redacted_content = content_to_scan

        if self.email_pattern.search(content_to_scan):
            pii_detected = True
            redacted_content = self.email_pattern.sub(
                "[EMAIL_REDACTED]", redacted_content
            )

        if self.phone_pattern.search(content_to_scan):
            pii_detected = True
            redacted_content = self.phone_pattern.sub(
                "[PHONE_REDACTED]", redacted_content
            )

        summary = (
            f"Security scan complete. PII Detected: {pii_detected}. "
            f"Policy compliance: {'FAILED' if pii_detected else 'PASSED'}."
        )

        return {
            "pii_detected": pii_detected,
            "redacted_content": redacted_content,
            "analysis_summary": summary,
            "metadata": {
                "scanned_length": len(content_to_scan),
                "risk_category": "PII_LEAK" if pii_detected else "NONE",
            },
        }
