"""
S.W.A.R.M. Phase 2: Advanced MLOps - Synthetic Data Generation
Production-ready synthetic data generation with privacy and quality controls
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import time
import uuid
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
import yaml
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.metrics import pairwise_distances
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

warnings.filterwarnings("ignore")

logger = logging.getLogger("raptorflow.synthetic_data")


class SyntheticMethod(Enum):
    """Synthetic data generation methods."""

    STATISTICAL = "statistical"
    GAN = "gan"
    VAE = "vae"
    DIFFUSION = "diffusion"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"


class DataPrivacyLevel(Enum):
    """Data privacy protection levels."""

    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


class DataQualityLevel(Enum):
    """Data quality validation levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"


@dataclass
class SyntheticDataConfig:
    """Configuration for synthetic data generation."""

    generation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: SyntheticMethod = SyntheticMethod.STATISTICAL
    target_columns: List[str] = field(default_factory=list)
    sample_size: int = 1000
    privacy_level: DataPrivacyLevel = DataPrivacyLevel.STANDARD
    quality_level: DataQualityLevel = DataQualityLevel.STANDARD
    preserve_correlations: bool = True
    preserve_distributions: bool = True
    noise_level: float = 0.1
    random_seed: int = 42
    output_format: str = "parquet"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "generation_id": self.generation_id,
            "method": self.method.value,
            "target_columns": self.target_columns,
            "sample_size": self.sample_size,
            "privacy_level": self.privacy_level.value,
            "quality_level": self.quality_level.value,
            "preserve_correlations": self.preserve_correlations,
            "preserve_distributions": self.preserve_distributions,
            "noise_level": self.noise_level,
            "random_seed": self.random_seed,
            "output_format": self.output_format,
        }


@dataclass
class DataQualityMetrics:
    """Data quality assessment metrics."""

    feature_name: str = ""
    distribution_similarity: float = 0.0
    correlation_preservation: float = 0.0
    statistical_similarity: float = 0.0
    privacy_score: float = 0.0
    utility_score: float = 0.0
    overall_quality: float = 0.0
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feature_name": self.feature_name,
            "distribution_similarity": self.distribution_similarity,
            "correlation_preservation": self.correlation_preservation,
            "statistical_similarity": self.statistical_similarity,
            "privacy_score": self.privacy_score,
            "utility_score": self.utility_score,
            "overall_quality": self.overall_quality,
            "issues": self.issues,
        }


class StatisticalSynthesizer:
    """Statistical methods for synthetic data generation."""

    def __init__(self):
        self.scalers = {}
        self.distributions = {}
        self.correlations = {}

    def fit(self, data: pd.DataFrame, target_columns: List[str]):
        """Fit statistical models to the data."""
        np.random.seed(42)

        for column in target_columns:
            if column not in data.columns:
                continue

            column_data = data[column].dropna()

            if pd.api.types.is_numeric_dtype(column_data):
                # Fit distribution
                self.distributions[column] = self._fit_distribution(column_data)

                # Fit scaler
                scaler = StandardScaler()
                scaler.fit(column_data.values.reshape(-1, 1))
                self.scalers[column] = scaler
            else:
                # Fit categorical distribution
                value_counts = column_data.value_counts(normalize=True)
                self.distributions[column] = value_counts.to_dict()

        # Calculate correlations
        numeric_columns = [
            col
            for col in target_columns
            if col in data.columns and pd.api.types.is_numeric_dtype(data[col])
        ]

        if len(numeric_columns) > 1:
            self.correlations = data[numeric_columns].corr().to_dict()

    def generate(self, sample_size: int, target_columns: List[str]) -> pd.DataFrame:
        """Generate synthetic data using statistical methods."""
        synthetic_data = pd.DataFrame()

        # Generate numeric features first
        numeric_columns = [
            col
            for col in target_columns
            if col in self.distributions and isinstance(self.distributions[col], tuple)
        ]

        if numeric_columns and self.correlations:
            # Generate correlated data
            synthetic_numeric = self._generate_correlated_data(
                numeric_columns, sample_size
            )
            synthetic_data = pd.concat([synthetic_data, synthetic_numeric], axis=1)

        # Generate categorical features
        for column in target_columns:
            if column not in self.distributions:
                continue

            if isinstance(self.distributions[column], dict):
                # Categorical feature
                categories = list(self.distributions[column].keys())
                probabilities = list(self.distributions[column].values())

                synthetic_values = np.random.choice(
                    categories, size=sample_size, p=probabilities
                )
                synthetic_data[column] = synthetic_values

        return synthetic_data

    def _fit_distribution(self, data: pd.Series) -> Tuple[str, Dict[str, Any]]:
        """Fit the best distribution to the data."""
        distributions = ["norm", "lognorm", "gamma", "beta", "exponential"]
        best_dist = None
        best_params = None
        best_pvalue = 0

        for dist_name in distributions:
            try:
                dist = getattr(stats, dist_name)
                params = dist.fit(data)

                # Kolmogorov-Smirnov test
                _, pvalue = stats.kstest(data, lambda x: dist.cdf(x, *params))

                if pvalue > best_pvalue:
                    best_pvalue = pvalue
                    best_dist = dist_name
                    best_params = params
            except:
                continue

        if best_dist is None:
            # Fallback to normal distribution
            best_dist = "norm"
            best_params = (data.mean(), data.std())

        return (best_dist, best_params)

    def _generate_correlated_data(
        self, columns: List[str], sample_size: int
    ) -> pd.DataFrame:
        """Generate correlated synthetic data."""
        # Extract correlation matrix
        corr_matrix = pd.DataFrame(self.correlations).loc[columns, columns].values

        # Generate correlated normal variables
        mean = np.zeros(len(columns))
        correlated_data = np.random.multivariate_normal(mean, corr_matrix, sample_size)

        # Transform to target distributions
        synthetic_data = pd.DataFrame()

        for i, column in enumerate(columns):
            dist_name, dist_params = self.distributions[column]

            # Convert normal to target distribution
            if dist_name == "norm":
                values = correlated_data[:, i] * dist_params[1] + dist_params[0]
            elif dist_name == "lognorm":
                values = np.exp(correlated_data[:, i] * dist_params[2] + dist_params[1])
            else:
                # Fallback: use normal distribution
                values = correlated_data[:, i] * dist_params[1] + dist_params[0]

            synthetic_data[column] = values

        return synthetic_data


class PrivacyProtection:
    """Privacy protection methods for synthetic data."""

    def __init__(self, privacy_level: DataPrivacyLevel = DataPrivacyLevel.STANDARD):
        self.privacy_level = privacy_level
        self.noise_levels = {
            DataPrivacyLevel.NONE: 0.0,
            DataPrivacyLevel.BASIC: 0.05,
            DataPrivacyLevel.STANDARD: 0.1,
            DataPrivacyLevel.HIGH: 0.2,
            DataPrivacyLevel.MAXIMUM: 0.3,
        }

    def apply_privacy(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply privacy protection to synthetic data."""
        protected_data = data.copy()
        noise_level = self.noise_levels[self.privacy_level]

        for column in protected_data.columns:
            if pd.api.types.is_numeric_dtype(protected_data[column]):
                # Add noise to numeric columns
                noise = np.random.normal(
                    0, noise_level * protected_data[column].std(), len(protected_data)
                )
                protected_data[column] += noise
            else:
                # Perturb categorical columns
                if np.random.random() < noise_level:
                    # Randomly perturb some values
                    mask = np.random.random(len(protected_data)) < noise_level
                    unique_values = protected_data[column].unique()
                    perturbed_values = np.random.choice(unique_values, size=mask.sum())
                    protected_data.loc[mask, column] = perturbed_values

        return protected_data

    def calculate_privacy_score(
        self, original_data: pd.DataFrame, synthetic_data: pd.DataFrame
    ) -> float:
        """Calculate privacy protection score."""
        score = 1.0

        for column in original_data.columns:
            if column not in synthetic_data.columns:
                continue

            if pd.api.types.is_numeric_dtype(original_data[column]):
                # Calculate distance between distributions
                orig_dist = original_data[column].values
                synth_dist = synthetic_data[column].values

                # Wasserstein distance
                distance = stats.wasserstein_distance(orig_dist, synth_dist)
                max_distance = orig_dist.max() - orig_dist.min()

                if max_distance > 0:
                    column_score = min(distance / max_distance, 1.0)
                    score = min(score, column_score)
            else:
                # Calculate categorical similarity
                orig_counts = original_data[column].value_counts(normalize=True)
                synth_counts = synthetic_data[column].value_counts(normalize=True)

                # Jensen-Shannon distance
                all_categories = set(orig_counts.index) | set(synth_counts.index)

                for cat in all_categories:
                    orig_prob = orig_counts.get(cat, 0)
                    synth_prob = synth_counts.get(cat, 0)

                    if orig_prob > 0 and synth_prob > 0:
                        js_dist = np.sqrt(
                            0.5
                            * (
                                orig_prob * np.log(orig_prob / synth_prob)
                                + synth_prob * np.log(synth_prob / orig_prob)
                            )
                        )
                        score = min(score, js_dist)

        return score


class DataQualityValidator:
    """Data quality validation for synthetic data."""

    def __init__(self, quality_level: DataQualityLevel = DataQualityLevel.STANDARD):
        self.quality_level = quality_level

    def validate_quality(
        self, original_data: pd.DataFrame, synthetic_data: pd.DataFrame
    ) -> Dict[str, DataQualityMetrics]:
        """Validate synthetic data quality."""
        quality_metrics = {}

        for column in original_data.columns:
            if column not in synthetic_data.columns:
                continue

            metrics = DataQualityMetrics(feature_name=column)

            # Distribution similarity
            metrics.distribution_similarity = self._calculate_distribution_similarity(
                original_data[column], synthetic_data[column]
            )

            # Statistical similarity
            metrics.statistical_similarity = self._calculate_statistical_similarity(
                original_data[column], synthetic_data[column]
            )

            # Utility score
            metrics.utility_score = self._calculate_utility_score(
                original_data[column], synthetic_data[column]
            )

            # Overall quality
            metrics.overall_quality = np.mean(
                [
                    metrics.distribution_similarity,
                    metrics.statistical_similarity,
                    metrics.utility_score,
                ]
            )

            # Identify issues
            if metrics.distribution_similarity < 0.7:
                metrics.issues.append("Poor distribution similarity")
            if metrics.statistical_similarity < 0.7:
                metrics.issues.append("Poor statistical similarity")
            if metrics.utility_score < 0.7:
                metrics.issues.append("Low utility score")

            quality_metrics[column] = metrics

        # Calculate correlation preservation for numeric columns
        numeric_columns = [
            col
            for col in original_data.columns
            if pd.api.types.is_numeric_dtype(original_data[col])
        ]

        if len(numeric_columns) > 1:
            orig_corr = original_data[numeric_columns].corr()
            synth_corr = synthetic_data[numeric_columns].corr()

            corr_diff = np.abs(orig_corr - synth_corr).mean().mean()
            correlation_score = 1.0 - corr_diff

            for column in numeric_columns:
                if column in quality_metrics:
                    quality_metrics[column].correlation_preservation = correlation_score

        return quality_metrics

    def _calculate_distribution_similarity(
        self, original: pd.Series, synthetic: pd.Series
    ) -> float:
        """Calculate distribution similarity score."""
        try:
            # Remove NaN values
            orig_clean = original.dropna()
            synth_clean = synthetic.dropna()

            if len(orig_clean) == 0 or len(synth_clean) == 0:
                return 0.0

            # Kolmogorov-Smirnov test
            statistic, p_value = stats.ks_2samp(orig_clean, synth_clean)

            # Convert to similarity score (higher is better)
            similarity = 1.0 - statistic

            return max(0.0, min(1.0, similarity))
        except:
            return 0.0

    def _calculate_statistical_similarity(
        self, original: pd.Series, synthetic: pd.Series
    ) -> float:
        """Calculate statistical similarity score."""
        try:
            orig_clean = original.dropna()
            synth_clean = synthetic.dropna()

            if len(orig_clean) == 0 or len(synth_clean) == 0:
                return 0.0

            if pd.api.types.is_numeric_dtype(original):
                # Compare basic statistics
                orig_stats = [
                    orig_clean.mean(),
                    orig_clean.std(),
                    orig_clean.min(),
                    orig_clean.max(),
                ]
                synth_stats = [
                    synth_clean.mean(),
                    synth_clean.std(),
                    synth_clean.min(),
                    synth_clean.max(),
                ]

                # Calculate relative differences
                similarities = []
                for orig_stat, synth_stat in zip(orig_stats, synth_stats):
                    if orig_stat != 0:
                        rel_diff = abs(orig_stat - synth_stat) / abs(orig_stat)
                        similarity = max(0.0, 1.0 - rel_diff)
                        similarities.append(similarity)

                return np.mean(similarities) if similarities else 0.0
            else:
                # Compare categorical distributions
                orig_counts = original.value_counts(normalize=True)
                synth_counts = synthetic.value_counts(normalize=True)

                # Calculate overlap
                all_categories = set(orig_counts.index) | set(synth_counts.index)
                overlap = 0.0

                for cat in all_categories:
                    orig_prob = orig_counts.get(cat, 0)
                    synth_prob = synth_counts.get(cat, 0)
                    overlap += min(orig_prob, synth_prob)

                return overlap
        except:
            return 0.0

    def _calculate_utility_score(
        self, original: pd.Series, synthetic: pd.Series
    ) -> float:
        """Calculate utility score for synthetic data."""
        try:
            # Simple utility score based on data preservation
            orig_clean = original.dropna()
            synth_clean = synthetic.dropna()

            if len(orig_clean) == 0 or len(synth_clean) == 0:
                return 0.0

            if pd.api.types.is_numeric_dtype(original):
                # Utility based on range preservation
                orig_range = orig_clean.max() - orig_clean.min()
                synth_range = synth_clean.max() - synth_clean.min()

                if orig_range > 0:
                    range_similarity = 1.0 - abs(orig_range - synth_range) / orig_range
                    return max(0.0, min(1.0, range_similarity))
                else:
                    return 1.0 if synth_range == 0 else 0.0
            else:
                # Utility based on category preservation
                orig_categories = set(original.unique())
                synth_categories = set(synthetic.unique())

                if len(orig_categories) == 0:
                    return 1.0

                category_overlap = len(orig_categories & synth_categories) / len(
                    orig_categories
                )
                return category_overlap
        except:
            return 0.0


class SyntheticDataGenerator:
    """Main synthetic data generation system."""

    def __init__(self):
        self.statistical_synthesizer = StatisticalSynthesizer()
        self.privacy_protection = PrivacyProtection()
        self.quality_validator = DataQualityValidator()
        self.generation_history: List[Dict[str, Any]] = []

    def generate_synthetic_data(
        self, original_data: pd.DataFrame, config: SyntheticDataConfig
    ) -> Dict[str, Any]:
        """Generate synthetic data with quality and privacy controls."""
        logger.info(f"Starting synthetic data generation: {config.generation_id}")

        start_time = time.time()

        try:
            # Set random seed
            np.random.seed(config.random_seed)

            # Update privacy protection level
            self.privacy_protection = PrivacyProtection(config.privacy_level)

            # Update quality validator level
            self.quality_validator = DataQualityValidator(config.quality_level)

            # Fit synthesizer
            self.statistical_synthesizer.fit(original_data, config.target_columns)

            # Generate synthetic data
            synthetic_data = self.statistical_synthesizer.generate(
                config.sample_size, config.target_columns
            )

            # Apply privacy protection
            if config.privacy_level != DataPrivacyLevel.NONE:
                synthetic_data = self.privacy_protection.apply_privacy(synthetic_data)

            # Validate quality
            quality_metrics = self.quality_validator.validate_quality(
                original_data, synthetic_data
            )

            # Calculate privacy score
            privacy_score = self.privacy_protection.calculate_privacy_score(
                original_data, synthetic_data
            )

            # Update privacy scores in metrics
            for metrics in quality_metrics.values():
                metrics.privacy_score = privacy_score

            # Calculate overall quality
            overall_quality = np.mean(
                [m.overall_quality for m in quality_metrics.values()]
            )

            # Prepare result
            result = {
                "generation_id": config.generation_id,
                "config": config.to_dict(),
                "synthetic_data": synthetic_data,
                "quality_metrics": {k: v.to_dict() for k, v in quality_metrics.items()},
                "overall_quality": overall_quality,
                "privacy_score": privacy_score,
                "generation_time": time.time() - start_time,
                "status": "success",
            }

            # Store in history
            self.generation_history.append(
                {
                    "generation_id": config.generation_id,
                    "timestamp": datetime.now().isoformat(),
                    "config": config.to_dict(),
                    "overall_quality": overall_quality,
                    "privacy_score": privacy_score,
                    "status": "success",
                }
            )

            logger.info(f"Synthetic data generation completed: {config.generation_id}")
            return result

        except Exception as e:
            logger.error(f"Synthetic data generation failed: {str(e)}")

            # Store failure in history
            self.generation_history.append(
                {
                    "generation_id": config.generation_id,
                    "timestamp": datetime.now().isoformat(),
                    "config": config.to_dict(),
                    "error": str(e),
                    "status": "failed",
                }
            )

            return {
                "generation_id": config.generation_id,
                "config": config.to_dict(),
                "error": str(e),
                "generation_time": time.time() - start_time,
                "status": "failed",
            }

    def get_generation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent generation history."""
        return self.generation_history[-limit:]

    def save_synthetic_data(self, result: Dict[str, Any], output_path: str):
        """Save synthetic data to file."""
        if result["status"] != "success":
            raise ValueError("Cannot save failed generation result")

        synthetic_data = result["synthetic_data"]

        if result["config"]["output_format"] == "parquet":
            synthetic_data.to_parquet(output_path, index=False)
        elif result["config"]["output_format"] == "csv":
            synthetic_data.to_csv(output_path, index=False)
        else:
            raise ValueError(
                f"Unsupported output format: {result['config']['output_format']}"
            )

        # Save metadata
        metadata_path = output_path.replace(
            f".{result['config']['output_format']}", "_metadata.json"
        )
        metadata = {
            "generation_id": result["generation_id"],
            "config": result["config"],
            "quality_metrics": result["quality_metrics"],
            "overall_quality": result["overall_quality"],
            "privacy_score": result["privacy_score"],
            "generation_time": result["generation_time"],
            "timestamp": datetime.now().isoformat(),
        }

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"Synthetic data saved to {output_path}")


# Example usage
async def demonstrate_synthetic_data_generation():
    """Demonstrate synthetic data generation system."""
    print(
        "Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Synthetic Data Generation..."
    )

    # Create sample original data
    np.random.seed(42)
    original_data = pd.DataFrame(
        {
            "customer_age": np.random.randint(18, 80, 1000),
            "income": np.random.normal(50000, 15000, 1000),
            "spending_score": np.random.uniform(1, 100, 1000),
            "gender": np.random.choice(["M", "F"], 1000),
            "region": np.random.choice(["North", "South", "East", "West"], 1000),
            "loyalty_years": np.random.exponential(2, 1000),
        }
    )

    print(f"Original data shape: {original_data.shape}")
    print(f"Original data columns: {list(original_data.columns)}")

    # Create synthetic data generator
    generator = SyntheticDataGenerator()

    # Create configuration
    config = SyntheticDataConfig(
        method=SyntheticMethod.STATISTICAL,
        target_columns=list(original_data.columns),
        sample_size=2000,  # Generate more samples than original
        privacy_level=DataPrivacyLevel.STANDARD,
        quality_level=DataQualityLevel.COMPREHENSIVE,
        preserve_correlations=True,
        preserve_distributions=True,
        noise_level=0.1,
        random_seed=42,
    )

    # Generate synthetic data
    print("\nGenerating synthetic data...")
    result = generator.generate_synthetic_data(original_data, config)

    if result["status"] == "success":
        print(f"Generation successful!")
        print(f"Synthetic data shape: {result['synthetic_data'].shape}")
        print(f"Overall quality: {result['overall_quality']:.3f}")
        print(f"Privacy score: {result['privacy_score']:.3f}")
        print(f"Generation time: {result['generation_time']:.2f} seconds")

        # Display quality metrics
        print("\nQuality Metrics by Feature:")
        for feature, metrics in result["quality_metrics"].items():
            print(f"  {feature}:")
            print(
                f"    Distribution similarity: {metrics['distribution_similarity']:.3f}"
            )
            print(
                f"    Statistical similarity: {metrics['statistical_similarity']:.3f}"
            )
            print(f"    Utility score: {metrics['utility_score']:.3f}")
            print(f"    Overall quality: {metrics['overall_quality']:.3f}")
            if metrics["issues"]:
                print(f"    Issues: {', '.join(metrics['issues'])}")

        # Save synthetic data
        output_path = "synthetic_customer_data.parquet"
        generator.save_synthetic_data(result, output_path)
        print(f"\nSynthetic data saved to {output_path}")

    else:
        print(f"Generation failed: {result['error']}")

    # Show generation history
    history = generator.get_generation_history()
    print(f"\nGeneration History: {len(history)} records")
    for record in history:
        print(
            f"  {record['generation_id'][:8]}... - {record['status']} - Quality: {record.get('overall_quality', 'N/A')}"
        )

    print("\nSynthetic Data Generation demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_synthetic_data_generation())
