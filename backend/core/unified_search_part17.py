"""
Part 17: Machine Learning Integration and AI Models
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module integrates machine learning models for query understanding, result ranking,
and intelligent search optimization.
"""

import asyncio
import json
import logging
import pickle
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from core.unified_search_part1 import ContentType, SearchMode, SearchQuery, SearchResult
from core.unified_search_part16 import QueryAnalysis, SearchPlan

logger = logging.getLogger("raptorflow.unified_search.ml")


class ModelType(Enum):
    """Types of ML models."""

    QUERY_CLASSIFIER = "query_classifier"
    INTENT_DETECTOR = "intent_detector"
    RANKING_MODEL = "ranking_model"
    QUALITY_PREDICTOR = "quality_predictor"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    ANOMALY_DETECTOR = "anomaly_detector"


@dataclass
class ModelPrediction:
    """Model prediction result."""

    model_type: ModelType
    prediction: Any
    confidence: float
    features: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_type": self.model_type.value,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "features": self.features,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class FeatureExtractor:
    """Extracts features for ML models."""

    def __init__(self):
        self.feature_cache = {}

    def extract_query_features(
        self, query: SearchQuery, analysis: Optional[QueryAnalysis] = None
    ) -> Dict[str, float]:
        """Extract features from search query."""
        features = {}

        # Basic text features
        text = query.text.lower()
        features["query_length"] = len(text)
        features["word_count"] = len(text.split())
        features["char_count"] = len(text.replace(" ", ""))
        features["avg_word_length"] = (
            features["char_count"] / features["word_count"]
            if features["word_count"] > 0
            else 0
        )

        # Punctuation features
        features["question_marks"] = text.count("?")
        features["exclamation_marks"] = text.count("!")
        features["periods"] = text.count(".")
        features["commas"] = text.count(",")
        features["quotes"] = text.count('"') + text.count("'")

        # Capitalization features
        features["uppercase_ratio"] = (
            sum(1 for c in text if c.isupper()) / len(text) if text else 0
        )
        features["title_case_words"] = (
            sum(1 for word in text.split() if word.istitle()) / features["word_count"]
            if features["word_count"] > 0
            else 0
        )

        # Numeric features
        features["digit_count"] = sum(c.isdigit() for c in text)
        features["has_numbers"] = 1.0 if features["digit_count"] > 0 else 0.0

        # Search mode features
        mode_features = {
            SearchMode.LIGHTNING: 0.0,
            SearchMode.STANDARD: 0.33,
            SearchMode.DEEP: 0.67,
            SearchMode.EXHAUSTIVE: 1.0,
        }
        features["search_mode_numeric"] = mode_features.get(query.mode, 0.33)

        # Content type features
        content_type_features = {
            ContentType.WEB: 0.0,
            ContentType.ACADEMIC: 0.2,
            ContentType.NEWS: 0.4,
            ContentType.SOCIAL: 0.6,
            ContentType.FORUM: 0.8,
            ContentType.DOCUMENTATION: 1.0,
        }
        if query.content_types:
            features["content_type_avg"] = np.mean(
                [content_type_features.get(ct, 0.0) for ct in query.content_types]
            )
        else:
            features["content_type_avg"] = 0.0

        # Analysis-based features (if available)
        if analysis:
            features["intent_confidence"] = analysis.confidence
            features["complexity"] = analysis.complexity
            features["specificity"] = analysis.specificity
            features["entity_count"] = len(analysis.entities)
            features["keyword_count"] = len(analysis.keywords)
            features["concept_count"] = len(analysis.concepts)

            # Intent features (one-hot encoded)
            intent_mapping = {
                "informational": 0.0,
                "navigational": 0.125,
                "transactional": 0.25,
                "commercial": 0.375,
                "comparison": 0.5,
                "definitional": 0.625,
                "tutorial": 0.75,
                "news": 0.875,
                "research": 1.0,
            }
            features["intent_numeric"] = intent_mapping.get(analysis.intent.value, 0.0)

        return features

    def extract_result_features(
        self, result: SearchResult, query: SearchQuery
    ) -> Dict[str, float]:
        """Extract features from search result."""
        features = {}

        # Basic content features
        title = result.title.lower()
        content = (result.content or "").lower()
        snippet = (result.snippet or "").lower()
        query_text = query.text.lower()

        features["title_length"] = len(title)
        features["content_length"] = len(content)
        features["snippet_length"] = len(snippet)
        features["total_length"] = (
            features["title_length"]
            + features["content_length"]
            + features["snippet_length"]
        )

        # Text overlap features
        query_words = set(query_text.split())
        title_words = set(title.split())
        content_words = set(content.split())
        snippet_words = set(snippet.split())

        features["title_query_overlap"] = (
            len(query_words.intersection(title_words)) / len(query_words)
            if query_words
            else 0
        )
        features["content_query_overlap"] = (
            len(query_words.intersection(content_words)) / len(query_words)
            if query_words
            else 0
        )
        features["snippet_query_overlap"] = (
            len(query_words.intersection(snippet_words)) / len(query_words)
            if query_words
            else 0
        )
        features["total_overlap"] = (
            features["title_query_overlap"]
            + features["content_query_overlap"]
            + features["snippet_query_overlap"]
        ) / 3

        # Domain features
        domain = result.domain.lower()
        features["domain_length"] = len(domain)
        features["domain_dots"] = domain.count(".")
        features["domain_digits"] = sum(c.isdigit() for c in domain)
        features["is_https"] = 1.0 if result.is_https else 0.0

        # Authority and relevance
        features["domain_authority"] = result.domain_authority
        features["relevance_score"] = result.relevance_score
        features["word_count"] = result.word_count
        features["reading_time"] = result.reading_time_minutes

        # Content type features
        content_type_mapping = {
            ContentType.WEB: 0.0,
            ContentType.ACADEMIC: 0.2,
            ContentType.NEWS: 0.4,
            ContentType.SOCIAL: 0.6,
            ContentType.FORUM: 0.8,
            ContentType.DOCUMENTATION: 1.0,
        }
        features["content_type_numeric"] = content_type_mapping.get(
            result.content_type, 0.0
        )

        # Provider features
        provider_mapping = {
            "native": 0.0,
            "serper": 0.25,
            "brave": 0.5,
            "duckduckgo": 0.75,
        }
        features["provider_numeric"] = provider_mapping.get(result.provider.value, 0.0)

        # Temporal features
        if result.publish_date:
            days_old = (datetime.now() - result.publish_date).days
            features["days_since_publish"] = days_old
            features["recency_score"] = 1.0 / (
                1.0 + days_old / 30.0
            )  # Decay over 30 days
        else:
            features["days_since_publish"] = 365.0  # Default to 1 year old
            features["recency_score"] = 0.1

        return features

    def extract_session_features(
        self, queries: List[SearchQuery], results_history: List[List[SearchResult]]
    ) -> Dict[str, float]:
        """Extract features from search session."""
        features = {}

        if not queries:
            return features

        # Session statistics
        features["session_length"] = len(queries)
        features["avg_query_length"] = np.mean([len(q.text) for q in queries])
        features["avg_word_count"] = np.mean([len(q.text.split()) for q in queries])

        # Query diversity
        unique_queries = set(q.text.lower() for q in queries)
        features["query_diversity"] = len(unique_queries) / len(queries)

        # Mode diversity
        modes = [q.mode for q in queries]
        unique_modes = set(modes)
        features["mode_diversity"] = len(unique_modes) / len(modes)

        # Result statistics
        if results_history:
            results_per_query = [len(results) for results in results_history]
            features["avg_results_per_query"] = np.mean(results_per_query)
            features["results_variance"] = np.var(results_per_query)
            features["total_results"] = sum(results_per_query)

        # Time patterns (if timestamps available)
        # This would require timestamp information in queries

        return features


class QueryClassifier:
    """ML-based query classification."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.is_trained = False
        self.class_mapping = {
            "simple": 0,
            "complex": 1,
            "ambiguous": 2,
            "specific": 3,
            "broad": 4,
        }

    async def train(self, training_data: List[Tuple[SearchQuery, str]]):
        """Train the query classifier."""
        logger.info("Training query classifier...")

        # Extract features and labels
        X = []
        y = []

        for query, label in training_data:
            features = self.feature_extractor.extract_query_features(query)
            X.append(list(features.values()))
            y.append(self.class_mapping.get(label, 0))

        if len(X) < 10:
            logger.warning("Insufficient training data for query classifier")
            return

        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)

        # Simple logistic regression model (in production, use proper ML library)
        self.model = self._create_simple_classifier(X, y)
        self.is_trained = True

        logger.info(f"Query classifier trained on {len(X)} samples")

    def _create_simple_classifier(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Create a simple classifier using basic statistics."""
        # This is a placeholder - in production use scikit-learn or similar
        class_means = {}
        class_counts = {}

        for class_label in np.unique(y):
            class_mask = y == class_label
            class_means[class_label] = np.mean(X[class_mask], axis=0)
            class_counts[class_label] = np.sum(class_mask)

        return {
            "class_means": class_means,
            "class_counts": class_counts,
            "total_samples": len(X),
            "feature_names": list(
                self.feature_extractor.extract_query_features(
                    SearchQuery(text="test")
                ).keys()
            ),
        }

    async def predict(self, query: SearchQuery) -> ModelPrediction:
        """Predict query classification."""
        if not self.is_trained:
            return ModelPrediction(
                model_type=ModelType.QUERY_CLASSIFIER,
                prediction="simple",
                confidence=0.5,
                metadata={"reason": "model not trained"},
            )

        features = self.feature_extractor.extract_query_features(query)
        feature_vector = np.array(list(features.values()))

        # Simple distance-based classification
        best_class = None
        best_distance = float("inf")

        for class_label, class_mean in self.model["class_means"].items():
            distance = np.linalg.norm(feature_vector - class_mean)
            if distance < best_distance:
                best_distance = distance
                best_class = class_label

        # Convert class index back to label
        reverse_mapping = {v: k for k, v in self.class_mapping.items()}
        predicted_label = reverse_mapping.get(best_class, "simple")

        # Calculate confidence (inverse of distance)
        confidence = 1.0 / (1.0 + best_distance)

        return ModelPrediction(
            model_type=ModelType.QUERY_CLASSIFIER,
            prediction=predicted_label,
            confidence=confidence,
            features=features,
            metadata={"distance": best_distance},
        )


class RankingModel:
    """ML-based result ranking model."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.is_trained = False
        self.feature_weights = {}

    async def train(self, training_data: List[Tuple[SearchQuery, SearchResult, float]]):
        """Train the ranking model."""
        logger.info("Training ranking model...")

        # Extract features and relevance scores
        X = []
        y = []

        for query, result, relevance_score in training_data:
            features = self.feature_extractor.extract_result_features(result, query)
            X.append(list(features.values()))
            y.append(relevance_score)

        if len(X) < 20:
            logger.warning("Insufficient training data for ranking model")
            return

        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)

        # Simple linear regression model (in production, use proper ML library)
        self.model = self._create_simple_ranker(X, y)
        self.is_trained = True

        logger.info(f"Ranking model trained on {len(X)} samples")

    def _create_simple_ranker(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Create a simple ranking model using feature weights."""
        # Calculate feature importance using correlation with relevance
        feature_correlations = []
        feature_names = list(
            self.feature_extractor.extract_result_features(
                SearchResult(url="test", title="test", content="test"),
                SearchQuery(text="test"),
            ).keys()
        )

        for i in range(X.shape[1]):
            correlation = np.corrcoef(X[:, i], y)[0, 1]
            feature_correlations.append(correlation)

        # Normalize correlations to create weights
        correlations = np.array(feature_correlations)
        correlations = np.nan_to_num(correlations)  # Handle NaN values
        weights = correlations / (np.sum(np.abs(correlations)) + 1e-8)

        feature_weights = dict(zip(feature_names, weights))

        return {
            "feature_weights": feature_weights,
            "feature_correlations": dict(zip(feature_names, correlations)),
            "mean_relevance": np.mean(y),
            "std_relevance": np.std(y),
        }

    async def predict(
        self, query: SearchQuery, results: List[SearchResult]
    ) -> List[ModelPrediction]:
        """Predict relevance scores for results."""
        if not self.is_trained:
            # Return original relevance scores
            return [
                ModelPrediction(
                    model_type=ModelType.RANKING_MODEL,
                    prediction=result.relevance_score,
                    confidence=0.5,
                    features={},
                    metadata={"reason": "model not trained"},
                )
                for result in results
            ]

        predictions = []

        for result in results:
            features = self.feature_extractor.extract_result_features(result, query)

            # Calculate weighted score
            weighted_score = 0.0
            for feature_name, feature_value in features.items():
                weight = self.model["feature_weights"].get(feature_name, 0.0)
                weighted_score += weight * feature_value

            # Normalize score to 0-1 range
            normalized_score = max(0.0, min(1.0, weighted_score))

            prediction = ModelPrediction(
                model_type=ModelType.RANKING_MODEL,
                prediction=normalized_score,
                confidence=0.7,  # Fixed confidence for simple model
                features=features,
                metadata={"weighted_score": weighted_score},
            )

            predictions.append(prediction)

        return predictions

    def rank_results(
        self, query: SearchQuery, results: List[SearchResult]
    ) -> List[SearchResult]:
        """Rank results using the ML model."""
        if not self.is_trained or not results:
            return results

        # Calculate scores for all results
        scored_results = []
        for result in results:
            features = self.feature_extractor.extract_result_features(result, query)

            # Calculate weighted score
            weighted_score = 0.0
            for feature_name, feature_value in features.items():
                weight = self.model["feature_weights"].get(feature_name, 0.0)
                weighted_score += weight * feature_value

            scored_results.append((result, weighted_score))

        # Sort by score (descending)
        scored_results.sort(key=lambda x: x[1], reverse=True)

        # Return sorted results
        return [result for result, score in scored_results]


class QualityPredictor:
    """ML-based result quality prediction."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.is_trained = False

    async def train(self, training_data: List[Tuple[SearchResult, float]]):
        """Train the quality predictor."""
        logger.info("Training quality predictor...")

        # Extract features and quality scores
        X = []
        y = []

        for result, quality_score in training_data:
            features = self.feature_extractor.extract_result_features(
                result, SearchQuery(text="test")
            )
            X.append(list(features.values()))
            y.append(quality_score)

        if len(X) < 20:
            logger.warning("Insufficient training data for quality predictor")
            return

        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)

        # Simple quality model
        self.model = self._create_quality_model(X, y)
        self.is_trained = True

        logger.info(f"Quality predictor trained on {len(X)} samples")

    def _create_quality_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Create a simple quality prediction model."""
        # Calculate feature importance for quality
        feature_importance = {}
        feature_names = list(
            self.feature_extractor.extract_result_features(
                SearchResult(url="test", title="test", content="test"),
                SearchQuery(text="test"),
            ).keys()
        )

        for i in range(X.shape[1]):
            correlation = np.corrcoef(X[:, i], y)[0, 1]
            feature_importance[feature_names[i]] = correlation

        # Quality thresholds
        quality_thresholds = {
            "high": np.percentile(y, 75),
            "medium": np.percentile(y, 50),
            "low": np.percentile(y, 25),
        }

        return {
            "feature_importance": feature_importance,
            "quality_thresholds": quality_thresholds,
            "mean_quality": np.mean(y),
            "std_quality": np.std(y),
        }

    async def predict(self, result: SearchResult) -> ModelPrediction:
        """Predict quality score for a result."""
        if not self.is_trained:
            return ModelPrediction(
                model_type=ModelType.QUALITY_PREDICTOR,
                prediction=0.5,
                confidence=0.3,
                metadata={"reason": "model not trained"},
            )

        features = self.feature_extractor.extract_result_features(
            result, SearchQuery(text="test")
        )

        # Calculate quality score based on important features
        quality_score = self.model["mean_quality"]

        # Adjust based on key quality indicators
        if result.domain_authority > 0.8:
            quality_score += 0.2
        if result.word_count > 500:
            quality_score += 0.1
        if result.snippet and len(result.snippet) > 100:
            quality_score += 0.1

        # Normalize to 0-1 range
        quality_score = max(0.0, min(1.0, quality_score))

        # Determine quality category
        thresholds = self.model["quality_thresholds"]
        if quality_score >= thresholds["high"]:
            category = "high"
        elif quality_score >= thresholds["medium"]:
            category = "medium"
        else:
            category = "low"

        return ModelPrediction(
            model_type=ModelType.QUALITY_PREDICTOR,
            prediction=quality_score,
            confidence=0.6,
            features=features,
            metadata={"category": category, "thresholds": thresholds},
        )


class RecommendationEngine:
    """ML-based recommendation engine."""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.user_profiles = {}
        self.content_profiles = {}
        self.is_initialized = False

    async def initialize(self):
        """Initialize the recommendation engine."""
        # Load user and content profiles
        # This would typically load from a database
        self.is_initialized = True
        logger.info("Recommendation engine initialized")

    async def update_user_profile(
        self,
        user_id: str,
        queries: List[SearchQuery],
        clicked_results: List[SearchResult],
    ):
        """Update user profile based on interaction history."""
        if not self.is_initialized:
            await self.initialize()

        # Extract user preferences from history
        profile = {
            "preferred_content_types": Counter(),
            "preferred_domains": Counter(),
            "query_patterns": [],
            "avg_query_complexity": 0.0,
            "interaction_count": len(clicked_results),
        }

        # Analyze queries
        for query in queries:
            features = self.feature_extractor.extract_query_features(query)
            profile["query_patterns"].append(features)

        # Calculate average complexity
        if profile["query_patterns"]:
            complexities = [f.get("complexity", 0.0) for f in profile["query_patterns"]]
            profile["avg_query_complexity"] = np.mean(complexities)

        # Analyze clicked results
        for result in clicked_results:
            profile["preferred_content_types"][result.content_type.value] += 1
            profile["preferred_domains"][result.domain] += 1

        self.user_profiles[user_id] = profile

    async def recommend_content(
        self, user_id: str, current_query: SearchQuery, results: List[SearchResult]
    ) -> List[ModelPrediction]:
        """Generate content recommendations."""
        if not self.is_initialized:
            await self.initialize()

        if user_id not in self.user_profiles:
            # No profile available, return neutral recommendations
            return [
                ModelPrediction(
                    model_type=ModelType.RECOMMENDATION_ENGINE,
                    prediction=0.5,
                    confidence=0.3,
                    metadata={"reason": "no user profile"},
                )
                for _ in results
            ]

        profile = self.user_profiles[user_id]
        recommendations = []

        for result in results:
            score = 0.5  # Base score

            # Content type preference
            content_type_score = profile["preferred_content_types"].get(
                result.content_type.value, 0
            )
            if content_type_score > 0:
                score += 0.2 * (content_type_score / profile["interaction_count"])

            # Domain preference
            domain_score = profile["preferred_domains"].get(result.domain, 0)
            if domain_score > 0:
                score += 0.1 * (domain_score / profile["interaction_count"])

            # Query similarity
            query_features = self.feature_extractor.extract_query_features(
                current_query
            )
            if profile["query_patterns"]:
                similarities = []
                for pattern in profile["query_patterns"]:
                    similarity = self._calculate_feature_similarity(
                        query_features, pattern
                    )
                    similarities.append(similarity)

                avg_similarity = np.mean(similarities)
                score += 0.2 * avg_similarity

            # Normalize score
            score = max(0.0, min(1.0, score))

            recommendation = ModelPrediction(
                model_type=ModelType.RECOMMENDATION_ENGINE,
                prediction=score,
                confidence=0.6,
                metadata={
                    "content_type_score": content_type_score,
                    "domain_score": domain_score,
                    "user_interaction_count": profile["interaction_count"],
                },
            )

            recommendations.append(recommendation)

        return recommendations

    def _calculate_feature_similarity(
        self, features1: Dict[str, float], features2: Dict[str, float]
    ) -> float:
        """Calculate similarity between feature vectors."""
        # Get common features
        common_features = set(features1.keys()) & set(features2.keys())

        if not common_features:
            return 0.0

        # Calculate cosine similarity
        dot_product = sum(features1[f] * features2[f] for f in common_features)
        norm1 = np.sqrt(sum(features1[f] ** 2 for f in common_features))
        norm2 = np.sqrt(sum(features2[f] ** 2 for f in common_features))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


class MLModelManager:
    """Manages all ML models and provides unified interface."""

    def __init__(self):
        self.query_classifier = QueryClassifier()
        self.ranking_model = RankingModel()
        self.quality_predictor = QualityPredictor()
        self.recommendation_engine = RecommendationEngine()
        self.models = {
            ModelType.QUERY_CLASSIFIER: self.query_classifier,
            ModelType.RANKING_MODEL: self.ranking_model,
            ModelType.QUALITY_PREDICTOR: self.quality_predictor,
            ModelType.RECOMMENDATION_ENGINE: self.recommendation_engine,
        }
        self.training_data = defaultdict(list)

    async def train_all_models(self, training_data: Dict[str, Any]):
        """Train all models with provided data."""
        logger.info("Training all ML models...")

        # Train query classifier
        if "query_classification" in training_data:
            await self.query_classifier.train(training_data["query_classification"])

        # Train ranking model
        if "ranking" in training_data:
            await self.ranking_model.train(training_data["ranking"])

        # Train quality predictor
        if "quality" in training_data:
            await self.quality_predictor.train(training_data["quality"])

        # Initialize recommendation engine
        await self.recommendation_engine.initialize()

        logger.info("ML model training completed")

    async def predict(self, model_type: ModelType, **kwargs) -> ModelPrediction:
        """Get prediction from specific model."""
        model = self.models.get(model_type)
        if not model:
            raise ValueError(f"Unknown model type: {model_type}")

        if model_type == ModelType.QUERY_CLASSIFIER:
            return await model.predict(kwargs.get("query"))
        elif model_type == ModelType.RANKING_MODEL:
            return await model.predict(kwargs.get("query"), kwargs.get("results", []))
        elif model_type == ModelType.QUALITY_PREDICTOR:
            return await model.predict(kwargs.get("result"))
        elif model_type == ModelType.RECOMMENDATION_ENGINE:
            return await model.recommend_content(
                kwargs.get("user_id"), kwargs.get("query"), kwargs.get("results", [])
            )
        else:
            raise ValueError(f"Prediction not implemented for model type: {model_type}")

    def rank_results(
        self, query: SearchQuery, results: List[SearchResult]
    ) -> List[SearchResult]:
        """Rank results using the ranking model."""
        return self.ranking_model.rank_results(query, results)

    async def update_user_profile(
        self,
        user_id: str,
        queries: List[SearchQuery],
        clicked_results: List[SearchResult],
    ):
        """Update user profile for recommendations."""
        await self.recommendation_engine.update_user_profile(
            user_id, queries, clicked_results
        )

    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models."""
        status = {}

        for model_type, model in self.models.items():
            status[model_type.value] = {
                "is_trained": getattr(model, "is_trained", False),
                "is_initialized": getattr(model, "is_initialized", False),
            }

        return status

    def save_models(self, filepath: str):
        """Save trained models to file."""
        model_data = {}

        for model_type, model in self.models.items():
            if hasattr(model, "model") and model.model:
                model_data[model_type.value] = {
                    "model": model.model,
                    "is_trained": getattr(model, "is_trained", False),
                }

        with open(filepath, "wb") as f:
            pickle.dump(model_data, f)

        logger.info(f"Models saved to {filepath}")

    def load_models(self, filepath: str):
        """Load trained models from file."""
        try:
            with open(filepath, "rb") as f:
                model_data = pickle.load(f)

            for model_type_str, data in model_data.items():
                model_type = ModelType(model_type_str)
                model = self.models.get(model_type)

                if model and "model" in data:
                    model.model = data["model"]
                    model.is_trained = data.get("is_trained", False)

            logger.info(f"Models loaded from {filepath}")

        except FileNotFoundError:
            logger.warning(f"Model file not found: {filepath}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")


# Global ML model manager
ml_manager = MLModelManager()
