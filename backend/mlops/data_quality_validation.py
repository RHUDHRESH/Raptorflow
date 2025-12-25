"""
S.W.A.R.M. Phase 2: Advanced MLOps - Data Quality Validation System
Production-ready data quality validation and monitoring
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
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

logger = logging.getLogger("raptorflow.data_quality")


class ValidationLevel(Enum):
    """Data quality validation levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"


class ValidationStatus(Enum):
    """Validation status levels."""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


class QualityDimension(Enum):
    """Data quality dimensions."""

    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    INTEGRITY = "integrity"


@dataclass
class ValidationRule:
    """Data quality validation rule."""

    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    dimension: QualityDimension = QualityDimension.COMPLETENESS
    column: str = ""
    rule_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    threshold: float = 0.0
    severity: str = "medium"
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "dimension": self.dimension.value,
            "column": self.column,
            "rule_type": self.rule_type,
            "parameters": self.parameters,
            "threshold": self.threshold,
            "severity": self.severity,
            "enabled": self.enabled,
        }


@dataclass
class ValidationResult:
    """Data quality validation result."""

    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    status: ValidationStatus = ValidationStatus.PASSED
    score: float = 0.0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "validation_id": self.validation_id,
            "rule_id": self.rule_id,
            "status": self.status.value,
            "score": self.score,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class QualityReport:
    """Data quality report."""

    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_name: str = ""
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    overall_score: float = 0.0
    total_rules: int = 0
    passed_rules: int = 0
    warning_rules: int = 0
    failed_rules: int = 0
    skipped_rules: int = 0
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    results: List[ValidationResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "dataset_name": self.dataset_name,
            "validation_level": self.validation_level.value,
            "overall_score": self.overall_score,
            "total_rules": self.total_rules,
            "passed_rules": self.passed_rules,
            "warning_rules": self.warning_rules,
            "failed_rules": self.failed_rules,
            "skipped_rules": self.skipped_rules,
            "dimension_scores": self.dimension_scores,
            "results": [r.to_dict() for r in self.results],
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
        }


class ValidationRuleEngine:
    """Engine for executing data quality validation rules."""

    def __init__(self):
        self.rule_handlers = {
            "completeness": self._validate_completeness,
            "uniqueness": self._validate_uniqueness,
            "validity": self._validate_validity,
            "accuracy": self._validate_accuracy,
            "consistency": self._validate_consistency,
            "timeliness": self._validate_timeliness,
            "integrity": self._validate_integrity,
        }

    def validate_rule(
        self, data: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Execute a single validation rule."""
        if not rule.enabled:
            return ValidationResult(
                rule_id=rule.rule_id,
                status=ValidationStatus.SKIPPED,
                message="Rule is disabled",
            )

        if rule.column not in data.columns:
            return ValidationResult(
                rule_id=rule.rule_id,
                status=ValidationStatus.SKIPPED,
                message=f"Column '{rule.column}' not found in dataset",
            )

        try:
            handler = self.rule_handlers.get(rule.rule_type)
            if handler is None:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    status=ValidationStatus.FAILED,
                    message=f"Unknown rule type: {rule.rule_type}",
                )

            return handler(data, rule)

        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                status=ValidationStatus.FAILED,
                message=f"Validation error: {str(e)}",
            )

    def _validate_completeness(
        self, data: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Validate data completeness (null values)."""
        column_data = data[rule.column]
        total_count = len(column_data)
        null_count = column_data.isnull().sum()
        completeness_score = 1.0 - (null_count / total_count)

        status = ValidationStatus.PASSED
        if completeness_score < rule.threshold:
            if completeness_score < rule.threshold * 0.5:
                status = ValidationStatus.FAILED
            else:
                status = ValidationStatus.WARNING

        message = f"Completeness: {completeness_score:.3f} ({null_count} null values out of {total_count})"

        return ValidationResult(
            rule_id=rule.rule_id,
            status=status,
            score=completeness_score,
            message=message,
            details={
                "null_count": null_count,
                "total_count": total_count,
                "completeness_percentage": completeness_score * 100,
            },
        )

    def _validate_uniqueness(
        self, data: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Validate data uniqueness (duplicate values)."""
        column_data = data[rule.column]
        total_count = len(column_data)
        unique_count = column_data.nunique()
        duplicate_count = total_count - unique_count
        uniqueness_score = unique_count / total_count

        status = ValidationStatus.PASSED
        if uniqueness_score < rule.threshold:
            if uniqueness_score < rule.threshold * 0.5:
                status = ValidationStatus.FAILED
            else:
                status = ValidationStatus.WARNING

        message = f"Uniqueness: {uniqueness_score:.3f} ({duplicate_count} duplicates out of {total_count})"

        return ValidationResult(
            rule_id=rule.rule_id,
            status=status,
            score=uniqueness_score,
            message=message,
            details={
                "unique_count": unique_count,
                "duplicate_count": duplicate_count,
                "total_count": total_count,
                "uniqueness_percentage": uniqueness_score * 100,
            },
        )

    def _validate_validity(
        self, data: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Validate data validity (format, range, patterns)."""
        column_data = data[rule.column]
        valid_count = 0
        total_count = len(column_data.dropna())

        validation_type = rule.parameters.get("type", "range")

        if validation_type == "range":
            min_val = rule.parameters.get("min")
            max_val = rule.parameters.get("max")

            if min_val is not None and max_val is not None:
                valid_mask = (column_data >= min_val) & (column_data <= max_val)
                valid_count = valid_mask.sum()

        elif validation_type == "pattern":
            pattern = rule.parameters.get("pattern", "")
            if pattern:
                import re

                valid_mask = column_data.str.match(pattern, na=False)
                valid_count = valid_mask.sum()

        elif validation_type == "values":
            allowed_values = set(rule.parameters.get("values", []))
            if allowed_values:
                valid_mask = column_data.isin(allowed_values)
                valid_count = valid_mask.sum()

        validity_score = valid_count / total_count if total_count > 0 else 1.0

        status = ValidationStatus.PASSED
        if validity_score < rule.threshold:
            if validity_score < rule.threshold * 0.5:
                status = ValidationStatus.FAILED
            else:
                status = ValidationStatus.WARNING

        message = (
            f"Validity: {validity_score:.3f} ({valid_count} valid out of {total_count})"
        )

        return ValidationResult(
            rule_id=rule.rule_id,
            status=status,
            score=validity_score,
            message=message,
            details={
                "valid_count": valid_count,
                "invalid_count": total_count - valid_count,
                "total_count": total_count,
                "validity_percentage": validity_score * 100,
                "validation_type": validation_type,
            },
        )

    def _validate_accuracy(
        self, data: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Validate data accuracy (statistical outliers, anomalies)."""
        column_data = data[rule.column].dropna()

        if len(column_data) < 10:
            return ValidationResult(
                rule_id=rule.rule_id,
                status=ValidationStatus.SKIPPED,
                message="Insufficient data for accuracy validation",
            )

        # Use Isolation Forest for outlier detection
        try:
            isolation_forest = IsolationForest(contamination=0.1, random_state=42)
            outlier_labels = isolation_forest.fit_predict(
                column_data.values.reshape(-1, 1)
            )
            outlier_count = (outlier_labels == -1).sum()
            accuracy_score = 1.0 - (outlier_count / len(column_data))

            status = ValidationStatus.PASSED
            if accuracy_score < rule.threshold:
                if accuracy_score < rule.threshold * 0.5:
                    status = ValidationStatus.FAILED
                else:
                    status = ValidationStatus.WARNING

            message = f"Accuracy: {accuracy_score:.3f} ({outlier_count} outliers out of {len(column_data)})"

            return ValidationResult(
                rule_id=rule.rule_id,
                status=status,
                score=accuracy_score,
                message=message,
                details={
                    "outlier_count": outlier_count,
                    "inlier_count": len(column_data) - outlier_count,
                    "total_count": len(column_data),
                    "accuracy_percentage": accuracy_score * 100,
                },
            )
        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                status=ValidationStatus.FAILED,
                message=f"Accuracy validation error: {str(e)}",
            )

    def _validate_consistency(
        self, data: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Validate data consistency across related columns."""
        related_columns = rule.parameters.get("related_columns", [])

        if not related_columns:
            return ValidationResult(
                rule_id=rule.rule_id,
                status=ValidationStatus.SKIPPED,
                message="No related columns specified for consistency validation",
            )

        consistency_type = rule.parameters.get("consistency_type", "correlation")

        if consistency_type == "correlation":
            # Check correlation consistency
            correlations = []
            for related_col in related_columns:
                if related_col in data.columns:
                    corr = data[rule.column].corr(data[related_col])
                    correlations.append(abs(corr))

            if correlations:
                avg_correlation = np.mean(correlations)
                consistency_score = avg_correlation
            else:
                consistency_score = 0.0

        elif consistency_type == "logical":
            # Check logical consistency (e.g., start_date <= end_date)
            consistency_score = 1.0  # Placeholder for logical checks

        status = ValidationStatus.PASSED
        if consistency_score < rule.threshold:
            if consistency_score < rule.threshold * 0.5:
                status = ValidationStatus.FAILED
            else:
                status = ValidationStatus.WARNING

        message = f"Consistency: {consistency_score:.3f}"

        return ValidationResult(
            rule_id=rule.rule_id,
            status=status,
            score=consistency_score,
            message=message,
            details={
                "consistency_type": consistency_type,
                "related_columns": related_columns,
                "consistency_score": consistency_score,
            },
        )

    def _validate_timeliness(
        self, data: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Validate data timeliness (recency, staleness)."""
        if not pd.api.types.is_datetime64_any_dtype(data[rule.column]):
            return ValidationResult(
                rule_id=rule.rule_id,
                status=ValidationStatus.SKIPPED,
                message="Column is not a datetime type",
            )

        column_data = data[rule.column].dropna()

        if len(column_data) == 0:
            return ValidationResult(
                rule_id=rule.rule_id,
                status=ValidationStatus.SKIPPED,
                message="No valid datetime values",
            )

        # Check data recency
        max_date = column_data.max()
        current_date = datetime.now()
        days_old = (current_date - max_date).days

        max_days_old = rule.parameters.get("max_days_old", 30)
        timeliness_score = max(0.0, 1.0 - (days_old / max_days_old))

        status = ValidationStatus.PASSED
        if timeliness_score < rule.threshold:
            if timeliness_score < rule.threshold * 0.5:
                status = ValidationStatus.FAILED
            else:
                status = ValidationStatus.WARNING

        message = f"Timeliness: {timeliness_score:.3f} (data is {days_old} days old)"

        return ValidationResult(
            rule_id=rule.rule_id,
            status=status,
            score=timeliness_score,
            message=message,
            details={
                "max_date": max_date.isoformat(),
                "days_old": days_old,
                "max_days_old": max_days_old,
                "timeliness_percentage": timeliness_score * 100,
            },
        )

    def _validate_integrity(
        self, data: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Validate data integrity (referential integrity, constraints)."""
        integrity_type = rule.parameters.get("integrity_type", "referential")

        if integrity_type == "referential":
            # Check referential integrity
            reference_table = rule.parameters.get("reference_table")
            reference_column = rule.parameters.get("reference_column")

            if not reference_table or not reference_column:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    status=ValidationStatus.SKIPPED,
                    message="No reference table/column specified",
                )

            # Placeholder for referential integrity check
            integrity_score = 1.0

        elif integrity_type == "constraint":
            # Check constraint integrity
            constraint_type = rule.parameters.get("constraint_type", "unique")

            if constraint_type == "unique":
                unique_count = data[rule.column].nunique()
                total_count = len(data[rule.column])
                integrity_score = unique_count / total_count
            else:
                integrity_score = 1.0

        status = ValidationStatus.PASSED
        if integrity_score < rule.threshold:
            if integrity_score < rule.threshold * 0.5:
                status = ValidationStatus.FAILED
            else:
                status = ValidationStatus.WARNING

        message = f"Integrity: {integrity_score:.3f}"

        return ValidationResult(
            rule_id=rule.rule_id,
            status=status,
            score=integrity_score,
            message=message,
            details={
                "integrity_type": integrity_type,
                "integrity_score": integrity_score,
            },
        )


class DataQualityValidator:
    """Main data quality validation system."""

    def __init__(self):
        self.rule_engine = ValidationRuleEngine()
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[QualityReport] = []

    def add_rule(self, rule: ValidationRule) -> str:
        """Add a validation rule."""
        self.validation_rules[rule.rule_id] = rule
        logger.info(f"Added validation rule: {rule.name}")
        return rule.rule_id

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a validation rule."""
        if rule_id in self.validation_rules:
            del self.validation_rules[rule_id]
            logger.info(f"Removed validation rule: {rule_id}")
            return True
        return False

    def get_rules(
        self, dimension: Optional[QualityDimension] = None
    ) -> List[ValidationRule]:
        """Get validation rules, optionally filtered by dimension."""
        rules = list(self.validation_rules.values())

        if dimension:
            rules = [rule for rule in rules if rule.dimension == dimension]

        return rules

    def validate_dataset(
        self,
        data: pd.DataFrame,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        dataset_name: str = "",
    ) -> QualityReport:
        """Validate entire dataset against applicable rules."""
        logger.info(f"Starting data quality validation for: {dataset_name}")

        start_time = time.time()

        # Filter rules based on validation level
        applicable_rules = self._get_applicable_rules(validation_level)

        # Execute validations
        results = []
        for rule in applicable_rules:
            result = self.rule_engine.validate_rule(data, rule)
            results.append(result)

        # Calculate dimension scores
        dimension_scores = {}
        for dimension in QualityDimension:
            dimension_results = [
                r
                for r in results
                if self.validation_rules.get(r.rule_id, ValidationRule()).dimension
                == dimension
            ]

            if dimension_results:
                dimension_scores[dimension.value] = np.mean(
                    [r.score for r in dimension_results]
                )
            else:
                dimension_scores[dimension.value] = 1.0

        # Calculate overall score
        overall_score = np.mean([r.score for r in results]) if results else 1.0

        # Count results by status
        passed_count = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        warning_count = sum(1 for r in results if r.status == ValidationStatus.WARNING)
        failed_count = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        skipped_count = sum(1 for r in results if r.status == ValidationStatus.SKIPPED)

        # Generate recommendations
        recommendations = self._generate_recommendations(results)

        # Create report
        report = QualityReport(
            dataset_name=dataset_name,
            validation_level=validation_level,
            overall_score=overall_score,
            total_rules=len(applicable_rules),
            passed_rules=passed_count,
            warning_rules=warning_count,
            failed_rules=failed_count,
            skipped_rules=skipped_count,
            dimension_scores=dimension_scores,
            results=results,
            recommendations=recommendations,
        )

        # Store in history
        self.validation_history.append(report)

        logger.info(
            f"Data quality validation completed: {dataset_name} - Score: {overall_score:.3f}"
        )
        return report

    def _get_applicable_rules(
        self, validation_level: ValidationLevel
    ) -> List[ValidationRule]:
        """Get rules applicable to the validation level."""
        all_rules = list(self.validation_rules.values())

        # Filter by validation level (simplified - in practice, rules would have level attributes)
        if validation_level == ValidationLevel.BASIC:
            return [
                rule
                for rule in all_rules
                if rule.dimension
                in [QualityDimension.COMPLETENESS, QualityDimension.UNIQUENESS]
            ]
        elif validation_level == ValidationLevel.STANDARD:
            return [
                rule
                for rule in all_rules
                if rule.dimension
                in [
                    QualityDimension.COMPLETENESS,
                    QualityDimension.UNIQUENESS,
                    QualityDimension.VALIDITY,
                ]
            ]
        elif validation_level == ValidationLevel.COMPREHENSIVE:
            return [
                rule
                for rule in all_rules
                if rule.dimension
                in [
                    QualityDimension.COMPLETENESS,
                    QualityDimension.UNIQUENESS,
                    QualityDimension.VALIDITY,
                    QualityDimension.ACCURACY,
                ]
            ]
        else:  # PRODUCTION
            return all_rules

    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        failed_rules = [r for r in results if r.status == ValidationStatus.FAILED]
        warning_rules = [r for r in results if r.status == ValidationStatus.WARNING]

        if failed_rules:
            recommendations.append(
                f"Address {len(failed_rules)} critical quality issues immediately"
            )

            # Specific recommendations by dimension
            for result in failed_rules:
                rule = self.validation_rules.get(result.rule_id)
                if rule:
                    if rule.dimension == QualityDimension.COMPLETENESS:
                        recommendations.append(
                            f"Improve data completeness for {rule.column}"
                        )
                    elif rule.dimension == QualityDimension.UNIQUENESS:
                        recommendations.append(f"Remove duplicates in {rule.column}")
                    elif rule.dimension == QualityDimension.VALIDITY:
                        recommendations.append(
                            f"Fix data format issues in {rule.column}"
                        )

        if warning_rules:
            recommendations.append(
                f"Monitor {len(warning_rules)} quality issues that may need attention"
            )

        if not failed_rules and not warning_rules:
            recommendations.append(
                "Data quality is excellent - continue current practices"
            )

        return recommendations

    def get_validation_history(self, limit: int = 10) -> List[QualityReport]:
        """Get recent validation history."""
        return self.validation_history[-limit:]

    def save_report(self, report: QualityReport, output_path: str):
        """Save quality report to file."""
        report_data = report.to_dict()

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        logger.info(f"Quality report saved to {output_path}")


# Example usage
async def demonstrate_data_quality_validation():
    """Demonstrate data quality validation system."""
    print(
        "Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Data Quality Validation..."
    )

    # Create sample data with quality issues
    np.random.seed(42)
    sample_data = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1],  # Duplicate
            "age": [25, 30, None, 45, 22, 35, 28, 33, 40, 27, 25],  # Missing value
            "income": [
                50000,
                60000,
                70000,
                80000,
                45000,
                65000,
                55000,
                75000,
                85000,
                48000,
                50000,
            ],
            "email": [
                "a@b.com",
                "invalid-email",
                "c@d.com",
                "e@f.com",
                "g@h.com",
                "i@j.com",
                "k@l.com",
                "m@n.com",
                "o@p.com",
                "q@r.com",
                "a@b.com",
            ],
            "registration_date": pd.date_range("2020-01-01", periods=10).tolist()
            + [pd.Timestamp("2020-01-01")],  # Old data
            "category": [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G",
                "H",
                "I",
                "J",
                "A",
            ],  # Duplicate
        }
    )

    print(f"Sample data shape: {sample_data.shape}")
    print(f"Sample data columns: {list(sample_data.columns)}")

    # Create validator
    validator = DataQualityValidator()

    # Add validation rules
    rules = [
        ValidationRule(
            name="Customer ID Uniqueness",
            description="Customer IDs should be unique",
            dimension=QualityDimension.UNIQUENESS,
            column="customer_id",
            rule_type="uniqueness",
            threshold=0.95,
        ),
        ValidationRule(
            name="Age Completeness",
            description="Age should not have missing values",
            dimension=QualityDimension.COMPLETENESS,
            column="age",
            rule_type="completeness",
            threshold=0.90,
        ),
        ValidationRule(
            name="Email Validity",
            description="Email should have valid format",
            dimension=QualityDimension.VALIDITY,
            column="email",
            rule_type="validity",
            parameters={
                "type": "pattern",
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            },
            threshold=0.90,
        ),
        ValidationRule(
            name="Income Accuracy",
            description="Income should not have outliers",
            dimension=QualityDimension.ACCURACY,
            column="income",
            rule_type="accuracy",
            threshold=0.90,
        ),
        ValidationRule(
            name="Registration Timeliness",
            description="Registration data should be recent",
            dimension=QualityDimension.TIMELINESS,
            column="registration_date",
            rule_type="timeliness",
            parameters={"max_days_old": 365},
            threshold=0.80,
        ),
    ]

    for rule in rules:
        validator.add_rule(rule)

    print(f"\nAdded {len(rules)} validation rules")

    # Validate dataset
    print("\nValidating dataset...")
    report = validator.validate_dataset(
        sample_data, ValidationLevel.COMPREHENSIVE, "sample_customer_data"
    )

    # Display results
    print(f"\nQuality Report Summary:")
    print(f"  Overall Score: {report.overall_score:.3f}")
    print(f"  Total Rules: {report.total_rules}")
    print(f"  Passed: {report.passed_rules}")
    print(f"  Warnings: {report.warning_rules}")
    print(f"  Failed: {report.failed_rules}")
    print(f"  Skipped: {report.skipped_rules}")

    print(f"\nDimension Scores:")
    for dimension, score in report.dimension_scores.items():
        print(f"  {dimension}: {score:.3f}")

    print(f"\nValidation Results:")
    for result in report.results:
        rule = validator.validation_rules.get(result.rule_id)
        rule_name = rule.name if rule else result.rule_id
        print(f"  {rule_name}: {result.status.value.upper()} - {result.message}")

    print(f"\nRecommendations:")
    for recommendation in report.recommendations:
        print(f"  • {recommendation}")

    # Save report
    report_path = "data_quality_report.json"
    validator.save_report(report, report_path)
    print(f"\nQuality report saved to {report_path}")

    # Show validation history
    history = validator.get_validation_history()
    print(f"\nValidation History: {len(history)} reports")
    for hist_report in history:
        print(
            f"  {hist_report.dataset_name} - Score: {hist_report.overall_score:.3f} - {hist_report.timestamp.strftime('%Y-%m-%d %H:%M')}"
        )

    print("\nData Quality Validation demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_data_quality_validation())
