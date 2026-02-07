"""
S.W.A.R.M. Phase 2: Advanced MLOps - Feature Engineering Pipelines
Production-ready feature engineering pipeline implementation
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
import yaml
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

logger = logging.getLogger("raptorflow.feature_engineering")


class FeatureType(Enum):
    """Feature data types."""

    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    GEOGRAPHIC = "geographic"
    IMAGE = "image"
    AUDIO = "audio"


class TransformationType(Enum):
    """Feature transformation types."""

    NORMALIZATION = "normalization"
    STANDARDIZATION = "standardization"
    ENCODING = "encoding"
    BINNING = "binning"
    POLYNOMIAL = "polynomial"
    LOG_TRANSFORM = "log_transform"
    INTERACTION = "interaction"
    AGGREGATION = "aggregation"
    EMBEDDING = "embedding"


class FeatureStatus(Enum):
    """Feature processing status."""

    RAW = "raw"
    CLEANED = "cleaned"
    TRANSFORMED = "transformed"
    SELECTED = "selected"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"


@dataclass
class FeatureMetadata:
    """Feature metadata container."""

    feature_name: str
    feature_type: FeatureType
    data_type: str
    null_count: int = 0
    null_percentage: float = 0.0
    unique_count: int = 0
    unique_percentage: float = 0.0
    cardinality: int = 0
    distribution_stats: Dict[str, float] = field(default_factory=dict)
    correlation_stats: Dict[str, float] = field(default_factory=dict)
    importance_score: float = 0.0
    creation_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    tags: Set[str] = field(default_factory=set)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feature_name": self.feature_name,
            "feature_type": self.feature_type.value,
            "data_type": self.data_type,
            "null_count": self.null_count,
            "null_percentage": self.null_percentage,
            "unique_count": self.unique_count,
            "unique_percentage": self.unique_percentage,
            "cardinality": self.cardinality,
            "distribution_stats": self.distribution_stats,
            "correlation_stats": self.correlation_stats,
            "importance_score": self.importance_score,
            "creation_time": self.creation_time.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "tags": list(self.tags),
            "description": self.description,
        }


@dataclass
class FeatureTransformation:
    """Feature transformation configuration."""

    transformation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    transformation_type: TransformationType = TransformationType.NORMALIZATION
    source_features: List[str] = field(default_factory=list)
    target_feature: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transformation_id": self.transformation_id,
            "transformation_type": self.transformation_type.value,
            "source_features": self.source_features,
            "target_feature": self.target_feature,
            "parameters": self.parameters,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class FeaturePipelineConfig:
    """Feature pipeline configuration."""

    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pipeline_name: str = ""
    description: str = ""
    input_data_source: str = ""
    output_destination: str = ""
    feature_types: Dict[str, FeatureType] = field(default_factory=dict)
    transformations: List[FeatureTransformation] = field(default_factory=list)
    selection_method: str = "importance"
    max_features: int = 100
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    monitoring_enabled: bool = True
    versioning_enabled: bool = True
    auto_retrain: bool = False
    retrain_threshold: float = 0.05

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_name": self.pipeline_name,
            "description": self.description,
            "input_data_source": self.input_data_source,
            "output_destination": self.output_destination,
            "feature_types": {k: v.value for k, v in self.feature_types.items()},
            "transformations": [t.to_dict() for t in self.transformations],
            "selection_method": self.selection_method,
            "max_features": self.max_features,
            "validation_rules": self.validation_rules,
            "monitoring_enabled": self.monitoring_enabled,
            "versioning_enabled": self.versioning_enabled,
            "auto_retrain": self.auto_retrain,
            "retrain_threshold": self.retrain_threshold,
        }


class FeatureAnalyzer:
    """Feature analysis and profiling."""

    def __init__(self):
        self.analysis_cache: Dict[str, FeatureMetadata] = {}

    def analyze_feature(
        self,
        feature_name: str,
        data: pd.Series,
        feature_type: Optional[FeatureType] = None,
    ) -> FeatureMetadata:
        """Analyze a single feature."""
        if feature_name in self.analysis_cache:
            return self.analysis_cache[feature_name]

        # Auto-detect feature type if not provided
        if feature_type is None:
            feature_type = self._detect_feature_type(data)

        # Calculate basic statistics
        null_count = data.isnull().sum()
        null_percentage = null_count / len(data) * 100
        unique_count = data.nunique()
        unique_percentage = unique_count / len(data) * 100
        cardinality = unique_count

        # Distribution statistics
        distribution_stats = self._calculate_distribution_stats(data, feature_type)

        # Create metadata
        metadata = FeatureMetadata(
            feature_name=feature_name,
            feature_type=feature_type,
            data_type=str(data.dtype),
            null_count=null_count,
            null_percentage=null_percentage,
            unique_count=unique_count,
            unique_percentage=unique_percentage,
            cardinality=cardinality,
            distribution_stats=distribution_stats,
        )

        self.analysis_cache[feature_name] = metadata
        return metadata

    def _detect_feature_type(self, data: pd.Series) -> FeatureType:
        """Auto-detect feature type."""
        if pd.api.types.is_numeric_dtype(data):
            if data.nunique() == 2 and set(data.dropna().unique()) <= {0, 1}:
                return FeatureType.BOOLEAN
            return FeatureType.NUMERICAL
        elif pd.api.types.is_datetime64_any_dtype(data):
            return FeatureType.DATETIME
        elif data.dtype == "object":
            if data.str.match(r"^\d{4}-\d{2}-\d{2}").all():
                return FeatureType.DATETIME
            return FeatureType.CATEGORICAL
        else:
            return FeatureType.CATEGORICAL

    def _calculate_distribution_stats(
        self, data: pd.Series, feature_type: FeatureType
    ) -> Dict[str, float]:
        """Calculate distribution statistics."""
        stats = {}

        if feature_type == FeatureType.NUMERICAL:
            clean_data = data.dropna()
            if len(clean_data) > 0:
                stats.update(
                    {
                        "mean": float(clean_data.mean()),
                        "median": float(clean_data.median()),
                        "std": float(clean_data.std()),
                        "min": float(clean_data.min()),
                        "max": float(clean_data.max()),
                        "q25": float(clean_data.quantile(0.25)),
                        "q75": float(clean_data.quantile(0.75)),
                        "skewness": float(clean_data.skew()),
                        "kurtosis": float(clean_data.kurtosis()),
                    }
                )

        elif feature_type == FeatureType.CATEGORICAL:
            value_counts = data.value_counts()
            if len(value_counts) > 0:
                stats.update(
                    {
                        "most_frequent": str(value_counts.index[0]),
                        "most_frequent_count": int(value_counts.iloc[0]),
                        "entropy": float(
                            -(
                                value_counts
                                / len(data)
                                * np.log2(value_counts / len(data) + 1e-10)
                            ).sum()
                        ),
                    }
                )

        return stats

    def analyze_dataset(
        self, df: pd.DataFrame, feature_types: Optional[Dict[str, FeatureType]] = None
    ) -> Dict[str, FeatureMetadata]:
        """Analyze entire dataset."""
        metadata = {}

        for column in df.columns:
            feature_type = feature_types.get(column) if feature_types else None
            metadata[column] = self.analyze_feature(column, df[column], feature_type)

        return metadata


class FeatureTransformer:
    """Feature transformation engine."""

    def __init__(self):
        self.transformers: Dict[str, Any] = {}
        self.transformation_history: List[Dict[str, Any]] = []

    def apply_transformation(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Apply a single transformation."""
        result_data = data.copy()

        try:
            if transformation.transformation_type == TransformationType.NORMALIZATION:
                result_data = self._apply_normalization(result_data, transformation)
            elif (
                transformation.transformation_type == TransformationType.STANDARDIZATION
            ):
                result_data = self._apply_standardization(result_data, transformation)
            elif transformation.transformation_type == TransformationType.ENCODING:
                result_data = self._apply_encoding(result_data, transformation)
            elif transformation.transformation_type == TransformationType.BINNING:
                result_data = self._apply_binning(result_data, transformation)
            elif transformation.transformation_type == TransformationType.POLYNOMIAL:
                result_data = self._apply_polynomial(result_data, transformation)
            elif transformation.transformation_type == TransformationType.LOG_TRANSFORM:
                result_data = self._apply_log_transform(result_data, transformation)
            elif transformation.transformation_type == TransformationType.INTERACTION:
                result_data = self._apply_interaction(result_data, transformation)
            elif transformation.transformation_type == TransformationType.AGGREGATION:
                result_data = self._apply_aggregation(result_data, transformation)

            # Record transformation
            self.transformation_history.append(
                {
                    "transformation_id": transformation.transformation_id,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "source_features": transformation.source_features,
                    "target_feature": transformation.target_feature,
                }
            )

        except Exception as e:
            logger.error(f"Transformation failed: {str(e)}")
            self.transformation_history.append(
                {
                    "transformation_id": transformation.transformation_id,
                    "timestamp": datetime.now().isoformat(),
                    "status": "failed",
                    "error": str(e),
                }
            )

        return result_data

    def _apply_normalization(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Apply min-max normalization."""
        for feature in transformation.source_features:
            if feature in data.columns:
                min_val = data[feature].min()
                max_val = data[feature].max()
                if max_val != min_val:
                    data[f"{feature}_normalized"] = (data[feature] - min_val) / (
                        max_val - min_val
                    )
                else:
                    data[f"{feature}_normalized"] = 0.0
        return data

    def _apply_standardization(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Apply z-score standardization."""
        for feature in transformation.source_features:
            if feature in data.columns:
                mean_val = data[feature].mean()
                std_val = data[feature].std()
                if std_val != 0:
                    data[f"{feature}_standardized"] = (
                        data[feature] - mean_val
                    ) / std_val
                else:
                    data[f"{feature}_standardized"] = 0.0
        return data

    def _apply_encoding(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Apply categorical encoding."""
        encoding_method = transformation.parameters.get("method", "one_hot")

        for feature in transformation.source_features:
            if feature in data.columns:
                if encoding_method == "one_hot":
                    encoder = OneHotEncoder(sparse=False, drop="first")
                    encoded_data = encoder.fit_transform(
                        data[[feature]].fillna("Unknown")
                    )
                    feature_names = [
                        f"{feature}_{cat}" for cat in encoder.categories_[0][1:]
                    ]
                    data[feature_names] = encoded_data
                elif encoding_method == "label":
                    encoder = LabelEncoder()
                    data[f"{feature}_encoded"] = encoder.fit_transform(
                        data[feature].fillna("Unknown")
                    )

        return data

    def _apply_binning(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Apply binning to numerical features."""
        n_bins = transformation.parameters.get("n_bins", 5)
        strategy = transformation.parameters.get("strategy", "uniform")

        for feature in transformation.source_features:
            if feature in data.columns:
                data[f"{feature}_binned"] = pd.cut(
                    data[feature], bins=n_bins, labels=False
                )

        return data

    def _apply_polynomial(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Apply polynomial features."""
        degree = transformation.parameters.get("degree", 2)

        for feature in transformation.source_features:
            if feature in data.columns:
                for d in range(2, degree + 1):
                    data[f"{feature}_poly_{d}"] = data[feature] ** d

        return data

    def _apply_log_transform(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Apply log transformation."""
        for feature in transformation.source_features:
            if feature in data.columns:
                # Handle zeros and negative values
                positive_data = data[feature] - data[feature].min() + 1
                data[f"{feature}_log"] = np.log(positive_data)

        return data

    def _apply_interaction(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Create interaction features."""
        if len(transformation.source_features) >= 2:
            features = transformation.source_features[
                :2
            ]  # Limit to pairwise interactions
            if all(f in data.columns for f in features):
                interaction_name = f"{features[0]}_x_{features[1]}"
                data[interaction_name] = data[features[0]] * data[features[1]]

        return data

    def _apply_aggregation(
        self, data: pd.DataFrame, transformation: FeatureTransformation
    ) -> pd.DataFrame:
        """Apply aggregation features."""
        agg_method = transformation.parameters.get("method", "mean")
        group_by = transformation.parameters.get("group_by", [])

        if group_by and all(col in data.columns for col in group_by):
            for feature in transformation.source_features:
                if feature in data.columns:
                    agg_feature_name = f"{feature}_{agg_method}_by_{'_'.join(group_by)}"
                    data[agg_feature_name] = data.groupby(group_by)[feature].transform(
                        agg_method
                    )

        return data


class FeatureSelector:
    """Feature selection engine."""

    def __init__(self):
        self.selection_history: List[Dict[str, Any]] = []

    def select_features(
        self,
        data: pd.DataFrame,
        target: pd.Series,
        method: str = "importance",
        max_features: int = 100,
    ) -> List[str]:
        """Select features based on specified method."""
        selected_features = []

        try:
            if method == "importance":
                selected_features = self._select_by_importance(
                    data, target, max_features
                )
            elif method == "correlation":
                selected_features = self._select_by_correlation(
                    data, target, max_features
                )
            elif method == "mutual_info":
                selected_features = self._select_by_mutual_info(
                    data, target, max_features
                )
            elif method == "variance":
                selected_features = self._select_by_variance(data, max_features)
            elif method == "univariate":
                selected_features = self._select_by_univariate(
                    data, target, max_features
                )

            # Record selection
            self.selection_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "method": method,
                    "max_features": max_features,
                    "selected_count": len(selected_features),
                    "selected_features": selected_features,
                    "status": "success",
                }
            )

        except Exception as e:
            logger.error(f"Feature selection failed: {str(e)}")
            self.selection_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "method": method,
                    "status": "failed",
                    "error": str(e),
                }
            )

        return selected_features

    def _select_by_importance(
        self, data: pd.DataFrame, target: pd.Series, max_features: int
    ) -> List[str]:
        """Select features using random forest importance."""
        # Handle categorical features
        processed_data = data.copy()
        for col in data.columns:
            if data[col].dtype == "object":
                processed_data[col] = LabelEncoder().fit_transform(
                    data[col].fillna("Unknown")
                )

        # Remove any remaining NaN values
        processed_data = processed_data.fillna(0)

        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(processed_data, target.fillna(0))

        importance_scores = pd.Series(rf.feature_importances_, index=data.columns)
        selected_features = importance_scores.nlargest(max_features).index.tolist()

        return selected_features

    def _select_by_correlation(
        self, data: pd.DataFrame, target: pd.Series, max_features: int
    ) -> List[str]:
        """Select features based on correlation with target."""
        correlations = []

        for feature in data.columns:
            if data[feature].dtype in ["int64", "float64"]:
                corr = abs(data[feature].corr(target))
                correlations.append((feature, corr))

        correlations.sort(key=lambda x: x[1], reverse=True)
        selected_features = [feat for feat, _ in correlations[:max_features]]

        return selected_features

    def _select_by_mutual_info(
        self, data: pd.DataFrame, target: pd.Series, max_features: int
    ) -> List[str]:
        """Select features using mutual information."""
        # Handle categorical features
        processed_data = data.copy()
        for col in data.columns:
            if data[col].dtype == "object":
                processed_data[col] = LabelEncoder().fit_transform(
                    data[col].fillna("Unknown")
                )

        # Remove any remaining NaN values
        processed_data = processed_data.fillna(0)

        mi_scores = mutual_info_classif(processed_data, target.fillna(0))
        feature_scores = pd.Series(mi_scores, index=data.columns)
        selected_features = feature_scores.nlargest(max_features).index.tolist()

        return selected_features

    def _select_by_variance(self, data: pd.DataFrame, max_features: int) -> List[str]:
        """Select features based on variance threshold."""
        variance_threshold = 0.01  # Minimum variance threshold

        # Calculate variance for numerical features
        numerical_features = data.select_dtypes(include=[np.number]).columns
        variances = data[numerical_features].var()

        # Filter by variance threshold
        high_variance_features = variances[
            variances > variance_threshold
        ].index.tolist()

        # Return top features by variance
        selected_features = (
            variances[high_variance_features].nlargest(max_features).index.tolist()
        )

        return selected_features

    def _select_by_univariate(
        self, data: pd.DataFrame, target: pd.Series, max_features: int
    ) -> List[str]:
        """Select features using univariate statistical tests."""
        # Handle categorical features
        processed_data = data.copy()
        for col in data.columns:
            if data[col].dtype == "object":
                processed_data[col] = LabelEncoder().fit_transform(
                    data[col].fillna("Unknown")
                )

        # Remove any remaining NaN values
        processed_data = processed_data.fillna(0)

        selector = SelectKBest(score_func=f_classif, k=max_features)
        selector.fit(processed_data, target.fillna(0))

        selected_features = processed_data.columns[selector.get_support()].tolist()

        return selected_features


class FeatureEngineeringPipeline:
    """Main feature engineering pipeline orchestrator."""

    def __init__(self):
        self.analyzer = FeatureAnalyzer()
        self.transformer = FeatureTransformer()
        self.selector = FeatureSelector()
        self.pipelines: Dict[str, FeaturePipelineConfig] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.feature_store: Dict[str, pd.DataFrame] = {}

    def create_pipeline(self, config: FeaturePipelineConfig) -> str:
        """Create a new feature engineering pipeline."""
        self.pipelines[config.pipeline_id] = config
        logger.info(f"Created pipeline: {config.pipeline_name}")
        return config.pipeline_id

    def execute_pipeline(
        self, pipeline_id: str, data: pd.DataFrame, target: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """Execute feature engineering pipeline."""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        config = self.pipelines[pipeline_id]
        execution_id = str(uuid.uuid4())

        try:
            start_time = datetime.now()

            # Step 1: Analyze features
            logger.info("Analyzing features...")
            feature_metadata = self.analyzer.analyze_dataset(data, config.feature_types)

            # Step 2: Apply transformations
            transformed_data = data.copy()
            for transformation in config.transformations:
                if transformation.is_active:
                    transformed_data = self.transformer.apply_transformation(
                        transformed_data, transformation
                    )

            # Step 3: Feature selection
            selected_features = []
            if target is not None and config.selection_method:
                selected_features = self.selector.select_features(
                    transformed_data,
                    target,
                    config.selection_method,
                    config.max_features,
                )

            # Step 4: Create final dataset
            if selected_features:
                final_data = transformed_data[
                    (
                        selected_features + [target.name]
                        if target is not None
                        else selected_features
                    )
                ]
            else:
                final_data = transformed_data

            # Store in feature store
            self.feature_store[execution_id] = final_data

            # Record execution
            execution_record = {
                "execution_id": execution_id,
                "pipeline_id": pipeline_id,
                "pipeline_name": config.pipeline_name,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": (datetime.now() - start_time).total_seconds(),
                "input_shape": data.shape,
                "output_shape": final_data.shape,
                "features_analyzed": len(feature_metadata),
                "transformations_applied": len(
                    [t for t in config.transformations if t.is_active]
                ),
                "features_selected": len(selected_features),
                "status": "success",
            }

            self.execution_history.append(execution_record)

            logger.info(f"Pipeline {config.pipeline_name} executed successfully")

            return {
                "execution_id": execution_id,
                "status": "success",
                "data": final_data,
                "metadata": feature_metadata,
                "selected_features": selected_features,
                "execution_record": execution_record,
            }

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")

            execution_record = {
                "execution_id": execution_id,
                "pipeline_id": pipeline_id,
                "pipeline_name": config.pipeline_name,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e),
            }

            self.execution_history.append(execution_record)

            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
                "execution_record": execution_record,
            }

    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline status and statistics."""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        config = self.pipelines[pipeline_id]
        executions = [
            e for e in self.execution_history if e["pipeline_id"] == pipeline_id
        ]

        return {
            "pipeline_config": config.to_dict(),
            "total_executions": len(executions),
            "successful_executions": len(
                [e for e in executions if e["status"] == "success"]
            ),
            "failed_executions": len(
                [e for e in executions if e["status"] == "failed"]
            ),
            "average_duration": (
                np.mean([e["duration"] for e in executions if "duration" in e])
                if executions
                else 0
            ),
            "last_execution": executions[-1] if executions else None,
        }

    def get_execution_history(
        self, pipeline_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get execution history."""
        history = self.execution_history

        if pipeline_id:
            history = [e for e in history if e["pipeline_id"] == pipeline_id]

        return history[-limit:]

    def save_pipeline(self, pipeline_id: str, filepath: str):
        """Save pipeline configuration to file."""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        config = self.pipelines[pipeline_id]
        with open(filepath, "w") as f:
            json.dump(config.to_dict(), f, indent=2, default=str)

        logger.info(f"Pipeline {pipeline_id} saved to {filepath}")

    def load_pipeline(self, filepath: str) -> str:
        """Load pipeline configuration from file."""
        with open(filepath, "r") as f:
            config_dict = json.load(f)

        # Reconstruct configuration
        config = FeaturePipelineConfig()
        config.pipeline_id = config_dict.get("pipeline_id", str(uuid.uuid4()))
        config.pipeline_name = config_dict.get("pipeline_name", "")
        config.description = config_dict.get("description", "")
        config.input_data_source = config_dict.get("input_data_source", "")
        config.output_destination = config_dict.get("output_destination", "")
        config.feature_types = {
            k: FeatureType(v) for k, v in config_dict.get("feature_types", {}).items()
        }
        config.selection_method = config_dict.get("selection_method", "importance")
        config.max_features = config_dict.get("max_features", 100)
        config.validation_rules = config_dict.get("validation_rules", {})
        config.monitoring_enabled = config_dict.get("monitoring_enabled", True)
        config.versioning_enabled = config_dict.get("versioning_enabled", True)
        config.auto_retrain = config_dict.get("auto_retrain", False)
        config.retrain_threshold = config_dict.get("retrain_threshold", 0.05)

        # Reconstruct transformations
        transformations = []
        for trans_dict in config_dict.get("transformations", []):
            transformation = FeatureTransformation()
            transformation.transformation_id = trans_dict.get(
                "transformation_id", str(uuid.uuid4())
            )
            transformation.transformation_type = TransformationType(
                trans_dict.get("transformation_type", "normalization")
            )
            transformation.source_features = trans_dict.get("source_features", [])
            transformation.target_feature = trans_dict.get("target_feature", "")
            transformation.parameters = trans_dict.get("parameters", {})
            transformation.is_active = trans_dict.get("is_active", True)
            transformations.append(transformation)

        config.transformations = transformations

        # Register pipeline
        self.pipelines[config.pipeline_id] = config

        logger.info(f"Pipeline loaded from {filepath}")
        return config.pipeline_id


# Example usage and templates
def create_sample_pipeline() -> FeaturePipelineConfig:
    """Create a sample feature engineering pipeline."""
    config = FeaturePipelineConfig(
        pipeline_name="Customer Churn Prediction Pipeline",
        description="Feature engineering pipeline for customer churn prediction",
        selection_method="importance",
        max_features=50,
    )

    # Add transformations
    transformations = [
        FeatureTransformation(
            transformation_type=TransformationType.NORMALIZATION,
            source_features=["age", "income", "spending_score"],
            target_feature="normalized_features",
        ),
        FeatureTransformation(
            transformation_type=TransformationType.ENCODING,
            source_features=["gender", "region", "subscription_type"],
            target_feature="encoded_features",
            parameters={"method": "one_hot"},
        ),
        FeatureTransformation(
            transformation_type=TransformationType.INTERACTION,
            source_features=["age", "income"],
            target_feature="age_income_interaction",
        ),
        FeatureTransformation(
            transformation_type=TransformationType.BINNING,
            source_features=["age"],
            target_feature="age_bins",
            parameters={"n_bins": 5, "strategy": "uniform"},
        ),
    ]

    config.transformations = transformations

    return config


async def demonstrate_feature_engineering():
    """Demonstrate feature engineering pipeline."""
    print("Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Feature Engineering...")

    # Create sample data
    np.random.seed(42)
    n_samples = 1000

    sample_data = pd.DataFrame(
        {
            "age": np.random.randint(18, 80, n_samples),
            "income": np.random.normal(50000, 15000, n_samples),
            "spending_score": np.random.uniform(1, 100, n_samples),
            "gender": np.random.choice(["Male", "Female"], n_samples),
            "region": np.random.choice(["North", "South", "East", "West"], n_samples),
            "subscription_type": np.random.choice(
                ["Basic", "Premium", "Enterprise"], n_samples
            ),
        }
    )

    # Create target variable
    sample_data["churn"] = (
        (sample_data["age"] > 50)
        & (sample_data["income"] < 40000)
        & (sample_data["spending_score"] < 30)
    ).astype(int)

    # Create pipeline
    pipeline = FeatureEngineeringPipeline()
    config = create_sample_pipeline()
    pipeline_id = pipeline.create_pipeline(config)

    print(f"Created pipeline: {config.pipeline_name}")
    print(f"Pipeline ID: {pipeline_id}")

    # Execute pipeline
    target = sample_data["churn"]
    input_data = sample_data.drop("churn", axis=1)

    result = pipeline.execute_pipeline(pipeline_id, input_data, target)

    print(f"\nPipeline Execution Results:")
    print(f"Status: {result['status']}")
    print(f"Input shape: {result['execution_record']['input_shape']}")
    print(f"Output shape: {result['execution_record']['output_shape']}")
    print(f"Features analyzed: {result['execution_record']['features_analyzed']}")
    print(
        f"Transformations applied: {result['execution_record']['transformations_applied']}"
    )
    print(f"Features selected: {result['execution_record']['features_selected']}")

    # Get pipeline status
    status = pipeline.get_pipeline_status(pipeline_id)
    print(f"\nPipeline Status:")
    print(f"Total executions: {status['total_executions']}")
    print(
        f"Success rate: {status['successful_executions']}/{status['total_executions']}"
    )
    print(f"Average duration: {status['average_duration']:.2f}s")

    print("\nFeature Engineering demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_feature_engineering())
