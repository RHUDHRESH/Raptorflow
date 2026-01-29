"""
DOCUMENT Q&A MODULE
Lightweight extractive QA using embedding similarity over sentences.
Explicit success/failure only.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ...base_processor import BaseProcessor, ProcessingResult, ProcessingStatus


@dataclass
class QAContext:
    sentence: str
    score: float


class QAModule(BaseProcessor):
    """
    Simple extractive QA:
    - Split document into sentences
    - TF-IDF encode question + sentences
    - Return top-K relevant sentences as answer
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.top_k = config.get("qa_top_k", 3)
        self.min_sentence_len = config.get("qa_min_sentence_len", 10)

    def answer(self, question: str, document: str) -> ProcessingResult:
        if not question or len(question.strip()) < 3:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Question too short",
                verified=False,
            )
        if not document or len(document.strip()) < 20:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Document too short for QA",
                verified=False,
            )
        try:
            sentences = self._split_sentences(document)
            sentences = [s for s in sentences if len(s) >= self.min_sentence_len]
            if not sentences:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No usable sentences for QA",
                    verified=False,
                )

            corpus = sentences + [question]
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf = vectorizer.fit_transform(corpus)

            doc_vecs = tfidf[:-1]
            q_vec = tfidf[-1]
            sims = cosine_similarity(doc_vecs, q_vec).flatten()

            top_idx = sims.argsort()[::-1][: self.top_k]
            answers = [
                {"sentence": sentences[i], "score": float(sims[i])}
                for i in top_idx
                if sims[i] > 0
            ]
            if not answers:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No relevant answer found",
                    verified=False,
                )
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={"answers": answers, "question": question},
                confidence=float(sims[top_idx[0]]),
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"QA failed: {str(e)}",
                verified=False,
            )

    def _split_sentences(self, text: str) -> List[str]:
        # Simple sentence split
        raw = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in raw if s.strip()]
