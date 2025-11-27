"""
Safety Models

Pydantic models for security, privacy, and compliance-related data analysis.
Includes PII detection findings and analysis reports for privacy protection.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class PIIFinding(BaseModel):
    """
    Represents a detected piece of personally identifiable information.

    Contains the type of PII, redacted/masked version of the found text,
    and positional information for tracking.
    """

    pii_type: str = Field(
        ...,
        description="Type of personally identifiable information detected",
        examples=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "IP_ADDRESS"]
    )
    redacted_text: str = Field(
        ...,
        description="Partially masked version of the found PII for safe display/logging",
        examples=["user****@****.com", "(555) 123-****"]
    )
    index: int = Field(
        ...,
        description="Starting character position of the PII in the original text",
        ge=0
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
        }


class PIIAnalysisReport(BaseModel):
    """
    Complete report from a PII scanning operation.

    Summarizes the results of privacy scanning on a text sample,
    indicating whether the text is safe to process or contains violations.
    """

    status: str = Field(
        ...,
        description="Scan result status",
        examples=["PASS", "FAIL"]
    )
    findings_count: int = Field(
        ...,
        description="Total number of PII findings detected",
        ge=0
    )
    findings: List[PIIFinding] = Field(
        default_factory=list,
        description="List of individual PII findings"
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
        }

    def add_finding(self, pii_type: str, found_text: str, start_index: int) -> None:
        """
        Add a PII finding to the report.

        Args:
            pii_type: Type of PII detected
            found_text: The actual PII text found
            start_index: Starting position in the original text
        """
        # Create redacted version for safe display
        redacted_text = self._redact_pii(pii_type, found_text)

        finding = PIIFinding(
            pii_type=pii_type,
            redacted_text=redacted_text,
            index=start_index
        )

        self.findings.append(finding)
        self.findings_count = len(self.findings)

        # Update status to FAIL if PII is found
        if self.findings_count > 0:
            self.status = "FAIL"

    def _redact_pii(self, pii_type: str, text: str) -> str:
        """
        Create a partially redacted version of the PII for safer display/logging.

        Args:
            pii_type: Type of PII
            text: Original PII text

        Returns:
            Partially masked version safe for logging
        """
        if pii_type == "EMAIL_ADDRESS" and "@" in text:
            # Mask part of username and domain: user****@****.com
            local, domain = text.split("@", 1)
            masked_local = local[:2] + "****" if len(local) > 2 else local + "****"
            masked_domain = "****." + domain.split(".", 1)[-1] if "." in domain else "****"
            return f"{masked_local}@{masked_domain}"

        elif pii_type == "PHONE_NUMBER":
            # Keep area code, mask rest: (555) 123-****
            digits_only = ''.join(c for c in text if c.isdigit())
            if len(digits_only) >= 10:
                return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:8]}****"
            else:
                return f"****{text[-4:]}" if len(text) > 4 else "****"

        elif pii_type == "CREDIT_CARD":
            # Show only last 4 digits: **** **** **** 1234
            digits_only = ''.join(c for c in text if c.isdigit())
            if len(digits_only) >= 4:
                return f"**** **** **** {digits_only[-4:]}"
            else:
                return "**** **** **** ****"

        elif pii_type == "IP_ADDRESS":
            # Mask IP address: 192.***.***
            if "." in text and text.count(".") == 3:
                parts = text.split(".")
                if len(parts) == 4:
                    return f"{parts[0]}.***.***"
            elif ":" in text:
                # IPv6 - just mask completely for safety
                return "****:****:****:****:****:****:****:****"
            return "****"

        else:
            # Generic masking for unknown types
            return f"****{text[-4:]}" if len(text) > 4 else "****"


class BrandAnalysisReport(BaseModel):
    """
    Report from brand compliance analysis using LLM evaluation.

    Contains the result of sophisticated brand alignment checking,
    including whether content passes brand guidelines and specific
    reasons for any violations.
    """

    status: str = Field(
        ...,
        description="Analysis result status",
        examples=["PASS", "FAIL"]
    )
    reason: str = Field(
        ...,
        description="Explanation for the analysis result",
        examples=[
            "Content uses professional, confident tone aligned with brand guidelines",
            "The text contains casual language and emojis, violating the professional tone requirement"
        ]
    )
    category: Optional[str] = Field(
        None,
        description="Specific category of brand violation (when status is FAIL)",
        examples=["TONE_VIOLATION", "FORBIDDEN_TOPIC", "COMPETITOR_MENTION", "INAPPROPRIATE_LANGUAGE"]
    )
    confidence: Optional[float] = Field(
        None,
        description="LLM confidence score in the analysis (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            str: lambda v: v,
        }
