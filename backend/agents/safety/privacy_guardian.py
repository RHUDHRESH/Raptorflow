"""
Privacy Guardian Agent (GRD-002)

Specialized agent for detecting Personally Identifiable Information (PII)
within text content. Acts as a critical privacy firewall to prevent
data leaks and ensure compliance with GDPR, CCPA, and other privacy regulations.

Features:
- High-speed regex-based PII detection for common patterns
- Comprehensive coverage of emails, phone numbers, credit cards, IPs
- Safe redaction of findings for logging and display
- Integration with safety workflows for automatic blocking
- Detailed reporting of all PII occurrences

PII Types Detected:
- Email addresses
- Phone numbers (various formats)
- Credit card numbers
- IPv4 and IPv6 addresses
- Social Security Numbers (SSN)
"""

import re
from typing import List
from uuid import UUID

from backend.models.safety import PIIFinding, PIIAnalysisReport
from backend.utils.correlation import get_correlation_id

import structlog

logger = structlog.get_logger(__name__)


class PrivacyGuardianAgent:
    """
    GRD-002: Privacy Guardian Agent for PII detection and blocking.

    This specialized agent provides comprehensive PII detection capabilities
    designed to protect user privacy and ensure regulatory compliance.

    The agent uses regex patterns optimized for accuracy and performance,
    focusing on the most common types of personally identifiable information
    that should never be processed or logged in clear text.

    Integration:
        - Called automatically by the main GuardianAgent
        - If PII is detected, the entire content processing workflow is blocked
        - Findings are logged with safe redaction for audit purposes
        - Supports both explicit scanning and automatic workflow integration
    """

    def __init__(self):
        """Initialize the Privacy Guardian Agent with optimized PII patterns."""
        # Compile regex patterns for performance
        self.patterns = {
            "EMAIL_ADDRESS": re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                re.IGNORECASE
            ),
            "PHONE_NUMBER": re.compile(
                r"\b(?:(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\d{10}\b)",
                re.IGNORECASE
            ),
            "CREDIT_CARD": re.compile(
                r"\b(?:\d{4}[- ]?){3}\d{4}\b",  # Most common formats
                re.IGNORECASE
            ),
            "IP_ADDRESS": re.compile(
                r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
                r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|"
                r"\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",  # IPv6
                re.IGNORECASE
            ),
            "SSN": re.compile(
                r"\b\d{3}-\d{2}-\d{4}\b",  # US Social Security Numbers
                re.IGNORECASE
            ),
        }

        # Validation functions for each PII type
        self.validators = {
            "EMAIL_ADDRESS": self._validate_email,
            "PHONE_NUMBER": self._validate_phone,
            "CREDIT_CARD": self._validate_credit_card,
            "IP_ADDRESS": self._validate_ip,
            "SSN": self._validate_ssn,
        }

    async def scan_text_for_pii(self, text: str) -> PIIAnalysisReport:
        """
        Comprehensive PII scan of text content.

        This is the main API method for PII detection. It scans the provided
        text for all configured PII types using optimized regex patterns and
        validation logic.

        Args:
            text: The text content to scan for PII

        Returns:
            PIIAnalysisReport containing scan results and all findings

        Example:
            report = await privacy_guardian.scan_text_for_pii(
                "Contact john@example.com or call 555-123-4567"
            )

            if report.status == "FAIL":
                # Block processing and log findings
                for finding in report.findings:
                    logger.warning(
                        "PII detected",
                        type=finding.pii_type,
                        redacted=finding.redacted_text
                    )
                return  # Stop processing
        """
        correlation_id = get_correlation_id()

        logger.info(
            "Starting PII scan",
            text_length=len(text),
            correlation_id=correlation_id
        )

        # Initialize report with PASS status (will change to FAIL if PII found)
        report = PIIAnalysisReport(status="PASS", findings_count=0, findings=[])

        try:
            # Scan for each PII type
            for pii_type, pattern in self.patterns.items():
                matches = pattern.finditer(text)

                for match in matches:
                    found_text = match.group()
                    start_index = match.start()

                    # Validate the match using type-specific logic
                    is_valid_pii = self.validators.get(pii_type, lambda x: True)(found_text)

                    if is_valid_pii:
                        # Add validated PII finding to report
                        report.add_finding(pii_type, found_text, start_index)

                        logger.warning(
                            "PII detected",
                            pii_type=pii_type,
                            redacted_text=report.findings[-1].redacted_text,
                            position=start_index,
                            correlation_id=correlation_id
                        )

            logger.info(
                "PII scan completed",
                status=report.status,
                findings_count=report.findings_count,
                correlation_id=correlation_id
            )

            return report

        except Exception as e:
            logger.error(
                "PII scan failed with error",
                error=str(e),
                correlation_id=correlation_id
            )
            # Return FAIL status on error to be safe
            return PIIAnalysisReport(
                status="FAIL",
                findings_count=1,
                findings=[]
            )

    def _validate_email(self, text: str) -> bool:
        """
        Validate email format with additional checks.

        Args:
            text: Potential email address

        Returns:
            True if this appears to be a valid email address
        """
        # Basic format check is already done by regex
        # Additional validation can be added here if needed
        return True

    def _validate_phone(self, text: str) -> bool:
        """
        Validate phone number format.

        Args:
            text: Potential phone number

        Returns:
            True if this appears to be a valid phone number
        """
        digits_only = re.sub(r'\D', '', text)

        # Valid lengths for phone numbers
        if len(digits_only) >= 10 and len(digits_only) <= 15:
            return True

        return False

    def _validate_credit_card(self, text: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.

        Args:
            text: Potential credit card number

        Returns:
            True if this passes Luhn validation
        """
        digits_only = re.sub(r'\D', '', text)

        # Check length (most cards are 13-19 digits, but focus on common lengths)
        if len(digits_only) < 13 or len(digits_only) > 19:
            return False

        # Luhn algorithm check
        def luhn_checksum(card_num: str) -> bool:
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))

            return checksum % 10 == 0

        return luhn_checksum(digits_only)

    def _validate_ip(self, text: str) -> bool:
        """
        Validate IP address format.

        Args:
            text: Potential IP address

        Returns:
            True if this appears to be a valid IP address
        """
        # Basic format validation is done by regex
        # Additional checks could be added here
        return True

    def _validate_ssn(self, text: str) -> bool:
        """
        Validate SSN format.

        Args:
            text: Potential Social Security Number

        Returns:
            True if this matches SSN format
        """
        # Basic format check is done by regex (XXX-XX-XXXX)
        # Additional validation could check for invalid SSNs (like all zeros)
        return True

    def get_supported_pii_types(self) -> List[str]:
        """
        Get list of PII types this agent can detect.

        Returns:
            List of supported PII type identifiers
        """
        return list(self.patterns.keys())

    def create_safe_log_message(self, text: str) -> str:
        """
        Create a safe version of text for logging by redacting all PII.

        This method can be used to create audit logs that are safe for storage
        while still maintaining most of the text context.

        Args:
            text: Original text containing potential PII

        Returns:
            Text with all PII redacted safely
        """
        safe_text = text

        # Scan and redact each PII type
        for pii_type, pattern in self.patterns.items():
            safe_text = pattern.sub(
                lambda match: self._redact_quick(match.group(), pii_type),
                safe_text
            )

        return safe_text

    def _redact_quick(self, text: str, pii_type: str) -> str:
        """
        Quick redaction method for safe logging.

        Args:
            text: PII text to redact
            pii_type: Type of PII

        Returns:
            Redacted version safe for logging
        """
        if pii_type == "EMAIL_ADDRESS":
            local, domain = text.split("@", 1)
            return f"{'*' * len(local)}@{domain}"
        elif pii_type == "PHONE_NUMBER":
            return "*" * len(text)
        elif pii_type == "CREDIT_CARD":
            digits_only = re.sub(r'\D', '', text)
            return f"**** **** **** {digits_only[-4:]}" if len(digits_only) >= 4 else "*" * len(text)
        elif pii_type == "IP_ADDRESS":
            return "***.***.***.***"
        else:
            return "*" * len(text)


# Global singleton instance
privacy_guardian = PrivacyGuardianAgent()
