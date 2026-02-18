"""
Critique and repair signal generator for AI Hub outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from backend.ai.hub.contracts import SafetyDecision, TaskRequestV1


@dataclass
class CritiqueResult:
    passed: bool
    score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    safety_decision: SafetyDecision = SafetyDecision.ALLOW


class Critic:
    def evaluate(
        self, *, request: TaskRequestV1, output: str, evidence_refs: List[str]
    ) -> CritiqueResult:
        issues: List[str] = []
        suggestions: List[str] = []
        score = 100.0

        if not output.strip():
            issues.append("Output is empty")
            suggestions.append("Provide a concrete answer to the intent.")
            score -= 60

        long_words = [w.lower() for w in request.intent.split() if len(w) >= 5][:4]
        if long_words and not any(word in output.lower() for word in long_words):
            issues.append("Output weakly aligned with intent keywords")
            suggestions.append("Align response language with the user intent.")
            score -= 20

        requires_evidence = bool(request.constraints.get("requires_evidence"))
        if requires_evidence and not evidence_refs:
            issues.append("No evidence references available despite evidence requirement")
            suggestions.append("Cite retrieved/tool evidence in the response.")
            score -= 25

        blocked_markers = {"drop table", "api key:", "secret:", "credential dump"}
        if any(marker in output.lower() for marker in blocked_markers):
            issues.append("Potential unsafe or sensitive output pattern detected")
            suggestions.append("Remove sensitive content and regenerate safely.")
            return CritiqueResult(
                passed=False,
                score=max(0.0, score - 50),
                issues=issues,
                suggestions=suggestions,
                safety_decision=SafetyDecision.BLOCK,
            )

        if score < 65:
            safety = SafetyDecision.REVIEW
            passed = False
        else:
            safety = SafetyDecision.ALLOW
            passed = True

        return CritiqueResult(
            passed=passed,
            score=max(0.0, score),
            issues=issues,
            suggestions=suggestions,
            safety_decision=safety,
        )

    def build_repair_prompt(self, *, draft: str, critique: CritiqueResult) -> str:
        issue_text = "; ".join(critique.issues) or "Improve quality and precision."
        suggestion_text = "; ".join(critique.suggestions) or "Tighten reasoning and output structure."
        return (
            "Revise the draft response.\n"
            f"Issues: {issue_text}\n"
            f"Suggestions: {suggestion_text}\n\n"
            f"Draft:\n{draft}"
        )

