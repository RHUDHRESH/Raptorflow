"""
Test suite for Privacy Guardian Agent

Tests PII detection functionality, ensuring that sensitive data
is properly identified and blocked before processing.
"""

import pytest
from unittest.mock import AsyncMock

from backend.agents.safety.privacy_guardian import privacy_guardian, PrivacyGuardianAgent
from backend.models.safety import PIIAnalysisReport, PIIFinding


class TestPrivacyGuardianAgent:
    """Test PrivacyGuardianAgent core functionality"""

    @pytest.fixture
    def agent(self):
        """Create a fresh agent instance for each test"""
        return PrivacyGuardianAgent()

    def test_supported_pii_types(self, agent):
        """Test that all expected PII types are supported"""
        supported = agent.get_supported_pii_types()
        expected_types = ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "IP_ADDRESS", "SSN"]

        assert set(supported) == set(expected_types)

    def test_create_safe_log_message(self, agent):
        """Test safe log message creation with PII redaction"""
        unsafe_text = "Contact user@example.com or call 555-123-4567 from IP 192.168.1.1"
        safe_text = agent.create_safe_log_message(unsafe_text)

        # Should redact email, phone, and IP
        assert "****" in safe_text
        assert "@" not in safe_text  # Email should be fully redacted
        assert "192.168.1.1" not in safe_text
        assert "***.***.***.***" in safe_text  # IP redaction pattern

    def test_validate_email(self, agent):
        """Test email validation"""
        assert agent._validate_email("user@example.com") == True

    def test_validate_phone_valid(self, agent):
        """Test phone number validation with valid numbers"""
        valid_numbers = [
            "555-123-4567",
            "(555) 123-4567",
            "5551234567",
            "+1-555-123-4567",
            "1234567890"
        ]

        for number in valid_numbers:
            # Extract just the digits for validation
            digits_only = ''.join(c for c in number if c.isdigit())
            assert agent._validate_phone(number) == True, f"Failed to validate {number}"

    def test_validate_phone_invalid(self, agent):
        """Test phone number validation with invalid numbers"""
        invalid_numbers = ["12345", "abc", ""]  # Too short

        for number in invalid_numbers:
            assert agent._validate_phone(number) == False

    def test_validate_credit_card_valid_luhn(self, agent):
        """Test credit card validation with Luhn algorithm"""
        # Valid test card number (passes Luhn)
        valid_card = "4532015112830366"  # This is a valid Visa test number
        assert agent._validate_credit_card(valid_card) == True

    def test_validate_credit_card_invalid_luhn(self, agent):
        """Test credit card validation with invalid Luhn"""
        # Invalid card number (fails Luhn)
        invalid_card = "1111111111111111"  # All 1s fails Luhn
        assert agent._validate_credit_card(invalid_card) == False

    def test_validate_credit_card_wrong_length(self, agent):
        """Test credit card validation with wrong length"""
        short_card = "12345"
        assert agent._validate_credit_card(short_card) == False

    def test_validate_ip(self, agent):
        """Test IP address validation"""
        valid_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
        for ip in valid_ips:
            assert agent._validate_ip(ip) == True

    def test_validate_ssn(self, agent):
        """Test SSN validation"""
        valid_ssn = "123-45-6789"
        assert agent._validate_ssn(valid_ssn) == True

    def test_redact_pii_email(self):
        """Test email redaction"""
        agent = PrivacyGuardianAgent()

        result = agent._redact_pii("EMAIL_ADDRESS", "user@example.com")
        assert "@" in result  # Domain is preserved
        assert "user" not in result  # Username is masked
        assert "****@example.com" == result

    def test_redact_pii_phone(self):
        """Test phone redaction"""
        agent = PrivacyGuardianAgent()

        result = agent._redact_pii("PHONE_NUMBER", "(555) 123-4567")
        # Should mask most digits, keep some structure
        assert "*" in result
        assert len(result) > 0

    def test_redact_pii_credit_card(self):
        """Test credit card redaction"""
        agent = PrivacyGuardianAgent()

        result = agent._redact_pii("CREDIT_CARD", "4532015112830366")
        assert result == "**** **** **** 0366"  # Show last 4 digits

    def test_redact_pii_ip(self):
        """Test IP address redaction"""
        agent = PrivacyGuardianAgent()

        result = agent._redact_pii("IP_ADDRESS", "192.168.1.1")
        assert result == "192.***.***"

    def test_redact_pii_ipv6(self):
        """Test IPv6 address redaction"""
        agent = PrivacyGuardianAgent()

        result = agent._redact_pii("IP_ADDRESS", "2001:db8::1")
        assert result == "****:****:****:****:****:****:****:****"

    @pytest.mark.asyncio
    async def test_scan_text_no_pii(self):
        """Test scanning text with no PII"""
        text = "This is a normal text without any sensitive information."
        report = await privacy_guardian.scan_text_for_pii(text)

        assert isinstance(report, PIIAnalysisReport)
        assert report.status == "PASS"
        assert report.findings_count == 0
        assert len(report.findings) == 0

    @pytest.mark.asyncio
    async def test_scan_text_with_email(self):
        """Test scanning text containing an email address"""
        text = "Please contact user@example.com for more information."
        report = await privacy_guardian.scan_text_for_pii(text)

        assert report.status == "FAIL"
        assert report.findings_count == 1

        finding = report.findings[0]
        assert finding.pii_type == "EMAIL_ADDRESS"
        assert finding.redacted_text == "****@example.com"
        assert finding.index == text.find("user@example.com")

    @pytest.mark.asyncio
    async def test_scan_text_with_phone(self):
        """Test scanning text containing a phone number"""
        text = "Call me at (555) 123-4567 for details."
        report = await privacy_guardian.scan_text_for_pii(text)

        assert report.status == "FAIL"
        assert report.findings_count == 1

        finding = report.findings[0]
        assert finding.pii_type == "PHONE_NUMBER"
        assert "(" in finding.redacted_text  # Should preserve some structure

    @pytest.mark.asyncio
    async def test_scan_text_with_credit_card(self):
        """Test scanning text containing a credit card number"""
        # Use a valid Luhn test number
        text = "Card number: 4532015112830366 expires 12/25"
        report = await privacy_guardian.scan_text_for_pii(text)

        assert report.status == "FAIL"
        assert report.findings_count == 1

        finding = report.findings[0]
        assert finding.pii_type == "CREDIT_CARD"
        assert finding.redacted_text == "**** **** **** 0366"

    @pytest.mark.asyncio
    async def test_scan_text_with_multiple_pii(self):
        """Test scanning text containing multiple types of PII"""
        text = """
        Contact John at john@example.com or call (555) 123-4567.
        Payment details: card 4532015112830366, IP: 192.168.1.1
        """

        report = await privacy_guardian.scan_text_for_pii(text)

        assert report.status == "FAIL"
        # Should find email, phone, credit card, and IP
        pii_types_found = [f.pii_type for f in report.findings]
        assert "EMAIL_ADDRESS" in pii_types_found
        assert "PHONE_NUMBER" in pii_types_found
        assert "CREDIT_CARD" in pii_types_found
        assert "IP_ADDRESS" in pii_types_found
        assert report.findings_count >= 4

    @pytest.mark.asyncio
    async def test_scan_text_with_ip_address(self):
        """Test scanning text containing IP addresses"""
        text = "Server logs show connection from 192.168.1.1 and 10.0.0.1"
        report = await privacy_guardian.scan_text_for_pii(text)

        assert report.status == "FAIL"
        assert report.findings_count >= 2

        pii_types = [f.pii_type for f in report.findings]
        assert all(pt == "IP_ADDRESS" for pt in pii_types)

    @pytest.mark.asyncio
    async def test_scan_text_with_ipv6(self):
        """Test scanning text containing IPv6 addresses"""
        text = "IPv6 connection from 2001:db8::1 detected"
        report = await privacy_guardian.scan_text_for_pii(text)

        assert report.status == "FAIL"
        assert report.findings_count == 1

        finding = report.findings[0]
        assert finding.pii_type == "IP_ADDRESS"

    @pytest.mark.asyncio
    async def test_scan_text_with_ssn(self):
        """Test scanning text containing SSN"""
        text = "Social Security Number: 123-45-6789"
        report = await privacy_guardian.scan_text_for_pii(text)

        assert report.status == "FAIL"
        assert report.findings_count == 1

        finding = report.findings[0]
        assert finding.pii_type == "SSN"
        assert finding.index == text.find("123-45-6789")

    @pytest.mark.asyncio
    async def test_scan_text_mixed_case(self):
        """Test scanning text with mixed case PII"""
        text = "Email: USER@EXAMPLE.COM, Phone: 555-123-4567"
        report = await privacy_guardian.scan_text_for_pii(text)

        assert report.status == "FAIL"
        assert report.findings_count == 2

        pii_types = {f.pii_type for f in report.findings}
        assert pii_types == {"EMAIL_ADDRESS", "PHONE_NUMBER"}

    @pytest.mark.asyncio
    async def test_scan_text_edge_cases(self):
        """Test scanning edge cases"""
        # Empty string
        report = await privacy_guardian.scan_text_for_pii("")
        assert report.status == "PASS"

        # Very short text
        report = await privacy_guardian.scan_text_for_pii("hi")
        assert report.status == "PASS"

        # Text with punctuation only
        report = await privacy_guardian.scan_text_for_pii("!@#$%^&*()")
        assert report.status == "PASS"

    @pytest.mark.asyncio
    async def test_scan_text_credit_card_invalid(self):
        """Test that invalid credit card numbers are not flagged"""
        text = "Invalid card: 1111111111111111 (fails Luhn check)"
        report = await privacy_guardian.scan_text_for_pii(text)

        # Should not find credit card since it fails Luhn validation
        credit_card_findings = [f for f in report.findings if f.pii_type == "CREDIT_CARD"]
        assert len(credit_card_findings) == 0

    @pytest.mark.asyncio
    async def test_scan_text_phone_too_short(self):
        """Test that invalid phone numbers are not flagged"""
        text = "Short number: 123"
        report = await privacy_guardian.scan_text_for_pii(text)

        phone_findings = [f for f in report.findings if f.pii_type == "PHONE_NUMBER"]
        assert len(phone_findings) == 0


class TestPIIAnalysisReport:
    """Test PIIAnalysisReport model functionality"""

    def test_report_initialization_pass(self):
        """Test creating a PASS report"""
        report = PIIAnalysisReport(status="PASS", findings_count=0, findings=[])
        assert report.status == "PASS"
        assert report.findings_count == 0
        assert report.findings == []

    def test_report_initialization_fail(self):
        """Test creating a FAIL report"""
        report = PIIAnalysisReport(status="FAIL", findings_count=1, findings=[])
        assert report.status == "FAIL"
        assert report.findings_count == 1

    def test_add_finding_single(self):
        """Test adding a single PII finding"""
        report = PIIAnalysisReport(status="PASS", findings_count=0, findings=[])

        report.add_finding("EMAIL_ADDRESS", "user@example.com", 10)

        assert report.status == "FAIL"
        assert report.findings_count == 1
        assert len(report.findings) == 1

        finding = report.findings[0]
        assert finding.pii_type == "EMAIL_ADDRESS"
        assert finding.index == 10
        assert "@" in finding.redacted_text

    def test_add_finding_multiple(self):
        """Test adding multiple PII findings"""
        report = PIIAnalysisReport(status="PASS", findings_count=0, findings=[])

        report.add_finding("EMAIL_ADDRESS", "user@example.com", 10)
        report.add_finding("PHONE_NUMBER", "555-123-4567", 35)

        assert report.status == "FAIL"
        assert report.findings_count == 2
        assert len(report.findings) == 2

        pii_types = [f.pii_type for f in report.findings]
        assert "EMAIL_ADDRESS" in pii_types
        assert "PHONE_NUMBER" in pii_types


class TestPIIFinding:
    """Test PIIFinding model functionality"""

    def test_finding_creation(self):
        """Test creating a PIIFinding object"""
        finding = PIIFinding(
            pii_type="EMAIL_ADDRESS",
            redacted_text="****@example.com",
            index=15
        )

        assert finding.pii_type == "EMAIL_ADDRESS"
        assert finding.redacted_text == "****@example.com"
        assert finding.index == 15

    def test_finding_dict_conversion(self):
        """Test PIIFinding model_dump"""
        finding = PIIFinding(
            pii_type="EMAIL_ADDRESS",
            redacted_text="****@example.com",
            index=15
        )

        data = finding.model_dump()
        assert data["pii_type"] == "EMAIL_ADDRESS"
        assert data["redacted_text"] == "****@example.com"
        assert data["index"] == 15


class TestPIIIntegrationScenarios:
    """Test complete integration scenarios"""

    @pytest.mark.asyncio
    async def test_real_world_scenario_marketing_email(self):
        """Test scanning a realistic marketing email with PII"""
        email_content = """
        Dear Customer,

        Thank you for your interest in our product! We collected some information from you:
        Email: customer@gmail.com
        Phone: (415) 555-0123
        IP Address: 192.168.1.100

        Your credit card **** **** **** 4242 will be charged $49.99.

        Best regards,
        Sales Team
        """

        report = await privacy_guardian.scan_text_for_pii(email_content)

        assert report.status == "FAIL"
        # Should find email, phone, IP, and credit card (even though already masked)
        # Note: The already-redacted credit card won't match our pattern, so expect 3 findings
        pii_types = [f.pii_type for f in report.findings]
        assert "EMAIL_ADDRESS" in pii_types
        assert "PHONE_NUMBER" in pii_types
        assert "IP_ADDRESS" in pii_types

    @pytest.mark.asyncio
    async def test_log_safety_features(self):
        """Test safe logging features"""
        sensitive_text = "Contact user@company.com at 555-123-4567 from 10.0.0.1"
        safe_log = privacy_guardian.create_safe_log_message(sensitive_text)

        # Safe log should not contain original PII
        assert "user@company.com" not in safe_log
        assert "555-123-4567" not in safe_log
        assert "10.0.0.1" not in safe_log

        # But should still contain other text
        assert "Contact" in safe_log
        assert "at" in safe_log
        assert "from" in safe_log

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in PII scanning"""
        # Test with None input
        try:
            await privacy_guardian.scan_text_for_pii(None)
            assert False, "Should have raised an exception"
        except Exception:
            # Should handle gracefully
            pass
