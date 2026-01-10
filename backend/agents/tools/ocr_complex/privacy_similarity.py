"""
PII REDACTION AND SIMILARITY
PII detection with regex heuristics + optional masking.
Document similarity/dedup using TF-IDF cosine.
"""

import re
from typing import Any, Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .base_processor import BaseProcessor, ProcessingResult, ProcessingStatus


class PIIRedactor(BaseProcessor):
    """PII detection and optional redaction."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mask_char = config.get("pii_mask_char", "█")
        self.enable_mask = config.get("pii_mask", True)

    def redact(self, text: str) -> ProcessingResult:
        if not text or len(text.strip()) < 5:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Text too short for PII detection",
                verified=False,
            )
        try:
            patterns = {
                "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "phone": r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b",
                "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
                "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            }
            matches: List[Dict[str, Any]] = []
            redacted = text
            for label, pat in patterns.items():
                for m in re.finditer(pat, text):
                    span = {
                        "label": label,
                        "value": m.group(0),
                        "start": m.start(),
                        "end": m.end(),
                    }
                    matches.append(span)
            if self.enable_mask and matches:
                redacted = list(text)
                for m in matches:
                    for i in range(m["start"], m["end"]):
                        redacted[i] = self.mask_char
                redacted = "".join(redacted)
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "pii": matches,
                    "pii_count": len(matches),
                    "redacted_text": redacted if self.enable_mask else text,
                    "masked": self.enable_mask,
                },
                confidence=0.75 if matches else 1.0,
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"PII redaction failed: {str(e)}",
                verified=False,
            )


class SimilarityEngine(BaseProcessor):
    """Document similarity and deduplication using TF-IDF cosine."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.threshold = config.get("similarity_threshold", 0.85)
        self.max_features = config.get("similarity_max_features", 5000)

    def compare(self, documents: List[str]) -> ProcessingResult:
        if not documents or len(documents) < 2:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Need at least 2 documents for similarity",
                verified=False,
            )
        try:
            vectorizer = TfidfVectorizer(
                max_features=self.max_features, stop_words="english"
            )
            tfidf = vectorizer.fit_transform(documents)
            sim_matrix = cosine_similarity(tfidf)
            pairs = []
            n = len(documents)
            for i in range(n):
                for j in range(i + 1, n):
                    score = float(sim_matrix[i, j])
                    if score >= self.threshold:
                        pairs.append({"doc_a": i, "doc_b": j, "similarity": score})
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "similar_pairs": pairs,
                    "threshold": self.threshold,
                    "max_similarity": (
                        float(sim_matrix[np.triu_indices(n, k=1)].max())
                        if n > 1
                        else 0.0
                    ),
                },
                confidence=0.9,
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Similarity computation failed: {str(e)}",
                verified=False,
            )
