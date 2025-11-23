"""
Grammar Orchestrator - Multi-engine grammar checking with parallel execution.
Integrates multiple grammar engines and aggregates results.
"""

import asyncio
import re
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from enum import Enum

logger = structlog.get_logger(__name__)


class GrammarSeverity(str, Enum):
    """Grammar issue severity levels."""
    CRITICAL = "critical"      # Must fix (spelling, major grammar)
    IMPORTANT = "important"    # Should fix (style, clarity)
    SUGGESTION = "suggestion"  # Nice to have (enhancement)


class GrammarIssue:
    """Represents a single grammar/style issue."""

    def __init__(
        self,
        message: str,
        context: str,
        offset: int,
        length: int,
        severity: GrammarSeverity,
        suggestions: List[str],
        rule_id: str,
        engine: str
    ):
        self.message = message
        self.context = context
        self.offset = offset
        self.length = length
        self.severity = severity
        self.suggestions = suggestions
        self.rule_id = rule_id
        self.engine = engine

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message": self.message,
            "context": self.context,
            "offset": self.offset,
            "length": self.length,
            "severity": self.severity.value,
            "suggestions": self.suggestions,
            "rule_id": self.rule_id,
            "engine": self.engine
        }


class GrammarOrchestrator:
    """
    Orchestrates multiple grammar checking engines in parallel.
    Aggregates results, deduplicates, and prioritizes issues.
    """

    def __init__(self, enable_llm: bool = True):
        """
        Initialize the grammar orchestrator.

        Args:
            enable_llm: Whether to use LLM-based grammar checking
        """
        self.enable_llm = enable_llm
        self._custom_rules = self._load_custom_rules()

        # Try to import optional dependencies
        self.language_tool_available = self._check_language_tool()

        logger.info(
            "Grammar orchestrator initialized",
            llm_enabled=enable_llm,
            language_tool=self.language_tool_available
        )

    def _check_language_tool(self) -> bool:
        """Check if language_tool_python is available."""
        try:
            import language_tool_python
            return True
        except ImportError:
            logger.warning("language_tool_python not available, skipping that engine")
            return False

    def _load_custom_rules(self) -> List[Dict[str, Any]]:
        """Load custom grammar and style rules."""
        return [
            {
                "name": "passive_voice",
                "pattern": r"\b(was|were|been|being|is|are|am)\s+\w+ed\b",
                "message": "Consider using active voice for stronger writing",
                "severity": GrammarSeverity.SUGGESTION
            },
            {
                "name": "weak_verbs",
                "pattern": r"\b(very|really|just|quite|rather)\s+",
                "message": "Consider removing weak intensifiers",
                "severity": GrammarSeverity.SUGGESTION
            },
            {
                "name": "wordiness",
                "pattern": r"\b(in order to|due to the fact that|at this point in time|for the purpose of)\b",
                "message": "Consider more concise phrasing",
                "severity": GrammarSeverity.SUGGESTION
            },
            {
                "name": "double_space",
                "pattern": r"  +",
                "message": "Multiple spaces detected",
                "severity": GrammarSeverity.IMPORTANT
            },
            {
                "name": "contractions_consistency",
                "pattern": r"\b(don't|won't|can't|shouldn't|wouldn't|couldn't|isn't|aren't)\b",
                "message": "Check contraction consistency with style guide",
                "severity": GrammarSeverity.SUGGESTION
            }
        ]

    async def check_grammar(
        self,
        content: str,
        language: str = "en-US",
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run content through multiple grammar engines in parallel.

        Args:
            content: Text to check
            language: Language code (default: en-US)
            correlation_id: Request correlation ID

        Returns:
            Aggregated grammar analysis with issues and suggestions
        """
        logger.info(
            "Starting grammar check",
            content_length=len(content),
            language=language,
            correlation_id=correlation_id
        )

        start_time = datetime.now(timezone.utc)

        # Run all engines in parallel
        tasks = [
            self._check_custom_rules(content),
            self._check_language_tool(content, language) if self.language_tool_available else self._empty_result("language_tool"),
            self._check_basic_patterns(content),
        ]

        if self.enable_llm:
            tasks.append(self._check_with_llm(content))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate all issues
        all_issues = []
        engine_stats = {}

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Grammar engine failed: {result}", correlation_id=correlation_id)
                continue

            if isinstance(result, dict):
                engine = result.get("engine", "unknown")
                issues = result.get("issues", [])
                all_issues.extend(issues)
                engine_stats[engine] = {
                    "issues_found": len(issues),
                    "success": True
                }

        # Deduplicate and prioritize
        deduplicated_issues = self._deduplicate_issues(all_issues)
        prioritized_issues = self._prioritize_issues(deduplicated_issues)

        # Generate auto-fixes for top issues
        auto_fixes = self._generate_auto_fixes(content, prioritized_issues[:10])

        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        result = {
            "total_issues": len(prioritized_issues),
            "critical_count": sum(1 for i in prioritized_issues if i.severity == GrammarSeverity.CRITICAL),
            "important_count": sum(1 for i in prioritized_issues if i.severity == GrammarSeverity.IMPORTANT),
            "suggestion_count": sum(1 for i in prioritized_issues if i.severity == GrammarSeverity.SUGGESTION),
            "issues": [issue.to_dict() for issue in prioritized_issues],
            "auto_fixes": auto_fixes,
            "engine_stats": engine_stats,
            "duration_ms": duration_ms,
            "checked_at": start_time.isoformat()
        }

        logger.info(
            "Grammar check completed",
            total_issues=result["total_issues"],
            duration_ms=duration_ms,
            correlation_id=correlation_id
        )

        return result

    async def _check_custom_rules(self, content: str) -> Dict[str, Any]:
        """Check content against custom rules."""
        issues = []

        for rule in self._custom_rules:
            pattern = rule["pattern"]
            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:
                context_start = max(0, match.start() - 30)
                context_end = min(len(content), match.end() + 30)
                context = content[context_start:context_end]

                issues.append(
                    GrammarIssue(
                        message=rule["message"],
                        context=context,
                        offset=match.start(),
                        length=match.end() - match.start(),
                        severity=rule["severity"],
                        suggestions=[],
                        rule_id=rule["name"],
                        engine="custom_rules"
                    )
                )

        return {
            "engine": "custom_rules",
            "issues": issues
        }

    async def _check_language_tool(self, content: str, language: str) -> Dict[str, Any]:
        """Check content using LanguageTool."""
        if not self.language_tool_available:
            return self._empty_result("language_tool")

        try:
            import language_tool_python

            # Run in executor to avoid blocking
            loop = asyncio.get_running_loop()
            tool = await loop.run_in_executor(
                None,
                lambda: language_tool_python.LanguageTool(language)
            )

            matches = await loop.run_in_executor(
                None,
                lambda: tool.check(content)
            )

            issues = []
            for match in matches:
                # Map LanguageTool categories to our severity levels
                severity = self._map_language_tool_severity(match.category)

                issues.append(
                    GrammarIssue(
                        message=match.message,
                        context=match.context,
                        offset=match.offset,
                        length=match.errorLength,
                        severity=severity,
                        suggestions=match.replacements[:3],  # Top 3 suggestions
                        rule_id=match.ruleId,
                        engine="language_tool"
                    )
                )

            await loop.run_in_executor(None, tool.close)

            return {
                "engine": "language_tool",
                "issues": issues
            }

        except Exception as e:
            logger.error(f"LanguageTool check failed: {e}")
            return self._empty_result("language_tool")

    async def _check_basic_patterns(self, content: str) -> Dict[str, Any]:
        """Check for basic patterns (spelling-like issues)."""
        issues = []

        # Check for repeated words
        repeated_pattern = r'\b(\w+)\s+\1\b'
        for match in re.finditer(repeated_pattern, content, re.IGNORECASE):
            context_start = max(0, match.start() - 30)
            context_end = min(len(content), match.end() + 30)

            issues.append(
                GrammarIssue(
                    message=f"Repeated word: '{match.group(1)}'",
                    context=content[context_start:context_end],
                    offset=match.start(),
                    length=match.end() - match.start(),
                    severity=GrammarSeverity.IMPORTANT,
                    suggestions=[match.group(1)],
                    rule_id="repeated_word",
                    engine="basic_patterns"
                )
            )

        # Check for excessive punctuation
        excessive_punct = r'[!?]{2,}'
        for match in re.finditer(excessive_punct, content):
            context_start = max(0, match.start() - 30)
            context_end = min(len(content), match.end() + 30)

            issues.append(
                GrammarIssue(
                    message="Excessive punctuation",
                    context=content[context_start:context_end],
                    offset=match.start(),
                    length=match.end() - match.start(),
                    severity=GrammarSeverity.SUGGESTION,
                    suggestions=["!", "?"],
                    rule_id="excessive_punctuation",
                    engine="basic_patterns"
                )
            )

        return {
            "engine": "basic_patterns",
            "issues": issues
        }

    async def _check_with_llm(self, content: str) -> Dict[str, Any]:
        """Use LLM for advanced grammar and style checking."""
        try:
            from backend.services.vertex_ai_client import vertex_ai_client

            prompt = f"""Analyze this text for grammar, spelling, and style issues.
Focus on:
- Grammatical errors
- Spelling mistakes
- Awkward phrasing
- Clarity issues

Text:
{content}

Return a JSON array of issues with this format:
[
  {{
    "message": "Brief description of the issue",
    "offset": character_position,
    "length": length_of_issue,
    "severity": "critical|important|suggestion",
    "suggestions": ["fix1", "fix2"]
  }}
]

Only return the JSON array, nothing else."""

            messages = [
                {"role": "system", "content": "You are an expert grammar and style editor."},
                {"role": "user", "content": prompt}
            ]

            response = await vertex_ai_client.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            import json
            llm_issues_data = json.loads(response)

            # Handle both array and object with issues key
            if isinstance(llm_issues_data, dict):
                llm_issues_data = llm_issues_data.get("issues", [])

            issues = []
            for issue_data in llm_issues_data[:20]:  # Limit to top 20
                offset = issue_data.get("offset", 0)
                length = issue_data.get("length", 1)
                context_start = max(0, offset - 30)
                context_end = min(len(content), offset + length + 30)

                # Map severity string to enum
                severity_str = issue_data.get("severity", "suggestion")
                severity = GrammarSeverity.CRITICAL if severity_str == "critical" else \
                          GrammarSeverity.IMPORTANT if severity_str == "important" else \
                          GrammarSeverity.SUGGESTION

                issues.append(
                    GrammarIssue(
                        message=issue_data.get("message", ""),
                        context=content[context_start:context_end],
                        offset=offset,
                        length=length,
                        severity=severity,
                        suggestions=issue_data.get("suggestions", []),
                        rule_id="llm_check",
                        engine="llm"
                    )
                )

            return {
                "engine": "llm",
                "issues": issues
            }

        except Exception as e:
            logger.error(f"LLM grammar check failed: {e}")
            return self._empty_result("llm")

    def _map_language_tool_severity(self, category: str) -> GrammarSeverity:
        """Map LanguageTool categories to severity levels."""
        category_lower = category.lower()

        if any(term in category_lower for term in ["typo", "grammar", "misspelling"]):
            return GrammarSeverity.CRITICAL
        elif any(term in category_lower for term in ["style", "clarity", "redundancy"]):
            return GrammarSeverity.IMPORTANT
        else:
            return GrammarSeverity.SUGGESTION

    def _deduplicate_issues(self, issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """Remove duplicate issues from multiple engines."""
        seen = {}
        unique_issues = []

        for issue in issues:
            # Create a key based on position and message
            key = (issue.offset, issue.length, issue.message.lower()[:50])

            if key not in seen:
                seen[key] = issue
                unique_issues.append(issue)
            else:
                # If duplicate, keep the one with more suggestions
                existing = seen[key]
                if len(issue.suggestions) > len(existing.suggestions):
                    seen[key] = issue
                    unique_issues.remove(existing)
                    unique_issues.append(issue)

        return unique_issues

    def _prioritize_issues(self, issues: List[GrammarIssue]) -> List[GrammarIssue]:
        """Sort issues by severity and position."""
        severity_order = {
            GrammarSeverity.CRITICAL: 0,
            GrammarSeverity.IMPORTANT: 1,
            GrammarSeverity.SUGGESTION: 2
        }

        return sorted(
            issues,
            key=lambda x: (severity_order[x.severity], x.offset)
        )

    def _generate_auto_fixes(
        self,
        content: str,
        top_issues: List[GrammarIssue]
    ) -> List[Dict[str, Any]]:
        """Generate automatic fixes for top issues."""
        auto_fixes = []

        for issue in top_issues:
            if issue.suggestions and len(issue.suggestions) > 0:
                # Create a fix by replacing the issue with the top suggestion
                fix = {
                    "issue": issue.message,
                    "original": content[issue.offset:issue.offset + issue.length],
                    "suggestion": issue.suggestions[0],
                    "offset": issue.offset,
                    "length": issue.length,
                    "confidence": "high" if issue.severity == GrammarSeverity.CRITICAL else "medium"
                }
                auto_fixes.append(fix)

        return auto_fixes

    def _empty_result(self, engine: str) -> Dict[str, Any]:
        """Return empty result for an engine."""
        return {
            "engine": engine,
            "issues": []
        }


# Singleton instance
grammar_orchestrator = GrammarOrchestrator()
