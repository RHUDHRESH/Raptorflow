"""
NLP EXTRAS
Keyword extraction, language detection, and simple text classification.
Explicit success/failure only.
"""

from typing import Any, Dict, List, Union

from langdetect import LangDetectException, detect, detect_langs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from .base_processor import BaseProcessor, ProcessingResult, ProcessingStatus


class KeywordExtractor(BaseProcessor):
    """TF-IDF top-N keyword extractor."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_features = config.get("keyword_max_features", 500)
        self.top_n = config.get("keyword_top_n", 10)

    def extract(self, documents: List[str]) -> ProcessingResult:
        if not documents or all(not d.strip() for d in documents):
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="No documents provided for keyword extraction",
                verified=False,
            )
        try:
            vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.9,
            )
            tfidf = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf.sum(axis=0).A1
            top_idx = scores.argsort()[::-1][: self.top_n]
            keywords = [
                {"term": feature_names[i], "score": float(scores[i])}
                for i in top_idx
                if scores[i] > 0
            ]
            if not keywords:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No significant keywords found",
                    verified=False,
                )
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={"keywords": keywords},
                confidence=0.8,
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Keyword extraction failed: {str(e)}",
                verified=False,
            )


class LanguageDetector(BaseProcessor):
    """Language detection using langdetect."""

    def detect_language(self, text: str) -> ProcessingResult:
        if not text or len(text.strip()) < 5:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Text too short for language detection",
                verified=False,
            )
        try:
            langs = detect_langs(text)
            if not langs:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No language detected",
                    verified=False,
                )
            best = langs[0]
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "language": best.lang,
                    "probability": best.prob,
                    "candidates": [str(l) for l in langs],
                },
                confidence=best.prob,
                verified=False,
            )
        except LangDetectException as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Language detection failed: {str(e)}",
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Language detection error: {str(e)}",
                verified=False,
            )


class SimpleTextClassifier(BaseProcessor):
    """
    Simple classifier using TF-IDF + MultinomialNB.
    Requires training_data list of {text, label} in config. Fails if not provided.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        training = config.get("training_data")
        if (
            not training
            or not isinstance(training, list)
            or not all("text" in t and "label" in t for t in training)
        ):
            raise ValueError(
                "training_data with 'text' and 'label' required for classification"
            )
        texts = [t["text"] for t in training]
        labels = [t["label"] for t in training]
        self.vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), max_features=2000
        )
        X = self.vectorizer.fit_transform(texts)
        self.model = MultinomialNB()
        self.model.fit(X, labels)

    def classify(self, text: str) -> ProcessingResult:
        if not text or len(text.strip()) < 5:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error="Text too short for classification",
                verified=False,
            )
        try:
            X = self.vectorizer.transform([text])
            probs = self.model.predict_proba(X)[0]
            label = self.model.classes_[probs.argmax()]
            confidence = float(probs.max())
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={"label": label, "confidence": confidence},
                confidence=confidence,
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Classification failed: {str(e)}",
                verified=False,
            )
