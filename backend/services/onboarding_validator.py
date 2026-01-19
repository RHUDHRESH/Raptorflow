"""
Onboarding Input Validator - Comprehensive validation for all onboarding steps
Ensures data integrity and prevents invalid state transitions.
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, ValidationError, validator
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationRule(Enum):
    """Validation rule types"""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    POSITIVE_NUMBER = "positive_number"
    NON_NEGATIVE = "non_negative"
    ENUM = "enum"
    ARRAY_MIN_ITEMS = "array_min_items"
    ARRAY_MAX_ITEMS = "array_max_items"
    FILE_TYPE = "file_type"
    FILE_SIZE = "file_size"


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation failed for {field}: {message}")


class StepValidator:
    """Validator for individual onboarding steps"""
    
    def __init__(self):
        self.step_schemas = self._define_step_schemas()
    
    def validate_step_input(self, step_id: str, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate input data for specific step"""
        try:
            schema = self.step_schemas.get(step_id)
            if not schema:
                return True, []  # No validation required
            
            errors = []
            
            # Validate required fields
            for field, rules in schema.items():
                field_value = data.get(field)
                
                # Check required
                if ValidationRule.REQUIRED in rules and field_value is None:
                    errors.append(f"{field} is required")
                    continue
                
                # Skip validation if field is optional and not provided
                if field_value is None:
                    continue
                
                # Apply validation rules
                for rule in rules:
                    error = self._apply_validation_rule(field, field_value, rule)
                    if error:
                        errors.append(error)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Validation error for step {step_id}: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def _apply_validation_rule(self, field: str, value: Any, rule: ValidationRule) -> Optional[str]:
        """Apply individual validation rule"""
        try:
            if rule == ValidationRule.EMAIL:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(value)):
                    return f"{field} must be a valid email address"
            
            elif rule == ValidationRule.URL:
                if not re.match(r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$', str(value)):
                    return f"{field} must be a valid URL"
            
            elif rule == ValidationRule.PHONE:
                if not re.match(r'^\+?1?-?\.?\s?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$', str(value)):
                    return f"{field} must be a valid phone number"
            
            elif rule == ValidationRule.MIN_LENGTH:
                if isinstance(value, (str, list)) and len(value) < rule.value:
                    return f"{field} must have at least {rule.value} characters/items"
            
            elif rule == ValidationRule.MAX_LENGTH:
                if isinstance(value, (str, list)) and len(value) > rule.value:
                    return f"{field} must have at most {rule.value} characters/items"
            
            elif rule == ValidationRule.POSITIVE_NUMBER:
                if isinstance(value, (int, float)) and value <= 0:
                    return f"{field} must be a positive number"
            
            elif rule == ValidationRule.NON_NEGATIVE:
                if isinstance(value, (int, float)) and value < 0:
                    return f"{field} must be non-negative"
            
            elif rule == ValidationRule.ENUM:
                if value not in rule.value:
                    return f"{field} must be one of: {', '.join(rule.value)}"
            
            elif rule == ValidationRule.ARRAY_MIN_ITEMS:
                if isinstance(value, list) and len(value) < rule.value:
                    return f"{field} must have at least {rule.value} items"
            
            elif rule == ValidationRule.ARRAY_MAX_ITEMS:
                if isinstance(value, list) and len(value) > rule.value:
                    return f"{field} must have at most {rule.value} items"
            
            elif rule == ValidationRule.FILE_TYPE:
                if isinstance(value, str) and value.lower() not in rule.value:
                    return f"{field} must be one of these file types: {', '.join(rule.value)}"
            
            elif rule == ValidationRule.FILE_SIZE:
                if isinstance(value, (int, float)) and value > rule.value:
                    return f"{field} file size must be less than {rule.value / (1024*1024):.1f}MB"
            
            return None
            
        except Exception as e:
            logger.error(f"Error applying validation rule: {e}")
            return f"Validation error for {field}"
    
    def _define_step_schemas(self) -> Dict[str, Dict[str, List[ValidationRule]]]:
        """Define validation schemas for all onboarding steps"""
        return {
            "evidence_upload": {
                "files": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(50)
                ],
                "urls": [
                    ValidationRule.ARRAY_MAX_ITEMS(20)
                ],
                "notes": [
                    ValidationRule.MAX_LENGTH(5000)
                ]
            },
            
            "business_classification": {
                "business_name": [
                    ValidationRule.REQUIRED,
                    ValidationRule.MIN_LENGTH(2),
                    ValidationRule.MAX_LENGTH(200)
                ],
                "business_description": [
                    ValidationRule.REQUIRED,
                    ValidationRule.MIN_LENGTH(50),
                    ValidationRule.MAX_LENGTH(2000)
                ],
                "industry": [
                    ValidationRule.REQUIRED,
                    ValidationRule.ENUM(["technology", "healthcare", "finance", "retail", "manufacturing", "education", "other"])
                ],
                "business_size": [
                    ValidationRule.REQUIRED,
                    ValidationRule.ENUM(["startup", "small", "medium", "large", "enterprise"])
                ],
                "revenue_range": [
                    ValidationRule.REQUIRED,
                    ValidationRule.ENUM(["<100k", "100k-1M", "1M-10M", "10M-50M", "50M-100M", ">100M"])
                ]
            },
            
            "industry_analysis": {
                "target_market_size": [
                    ValidationRule.POSITIVE_NUMBER
                ],
                "growth_rate": [
                    ValidationRule.NON_NEGATIVE
                ],
                "key_trends": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(10)
                ],
                "market_challenges": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(10)
                ]
            },
            
            "competitor_analysis": {
                "competitors": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(20)
                ],
                "analysis_notes": [
                    ValidationRule.MAX_LENGTH(5000)
                ]
            },
            
            "value_proposition": {
                "primary_value": [
                    ValidationRule.REQUIRED,
                    ValidationRule.MIN_LENGTH(10),
                    ValidationRule.MAX_LENGTH(500)
                ],
                "unique_selling_points": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(10)
                ],
                "customer_benefits": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(10)
                ]
            },
            
            "target_audience": {
                "primary_audience": [
                    ValidationRule.REQUIRED,
                    ValidationRule.MIN_LENGTH(50),
                    ValidationRule.MAX_LENGTH(1000)
                ],
                "demographics": [
                    ValidationRule.REQUIRED
                ],
                "psychographics": [
                    ValidationRule.REQUIRED
                ],
                "pain_points": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(20)
                ]
            },
            
            "messaging_framework": {
                "core_message": [
                    ValidationRule.REQUIRED,
                    ValidationRule.MIN_LENGTH(20),
                    ValidationRule.MAX_LENGTH(500)
                ],
                "supporting_points": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(10)
                ],
                "tone_of_voice": [
                    ValidationRule.REQUIRED,
                    ValidationRule.ENUM(["professional", "friendly", "casual", "formal", "technical"])
                ]
            },
            
            "foundation_creation": {
                "business_name": [
                    ValidationRule.REQUIRED,
                    ValidationRule.MIN_LENGTH(2),
                    ValidationRule.MAX_LENGTH(200)
                ],
                "business_description": [
                    ValidationRule.REQUIRED,
                    ValidationRule.MIN_LENGTH(50),
                    ValidationRule.MAX_LENGTH(2000)
                ],
                "industry": [
                    ValidationRule.REQUIRED
                ],
                "classification": [
                    ValidationRule.REQUIRED
                ],
                "industry_analysis": [
                    ValidationRule.REQUIRED
                ],
                "competitor_analysis": [
                    ValidationRule.REQUIRED
                ],
                "value_proposition": [
                    ValidationRule.REQUIRED
                ],
                "target_audience": [
                    ValidationRule.REQUIRED
                ],
                "messaging_framework": [
                    ValidationRule.REQUIRED
                ]
            },
            
            "icp_generation": {
                "foundation_data": [
                    ValidationRule.REQUIRED
                ],
                "target_count": [
                    ValidationRule.REQUIRED,
                    ValidationRule.ENUM([1, 2, 3])
                ]
            },
            
            "move_planning": {
                "foundation_data": [
                    ValidationRule.REQUIRED
                ],
                "icps": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(3)
                ],
                "strategic_moves": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(10)
                ]
            },
            
            "campaign_setup": {
                "moves": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(10)
                ],
                "icps": [
                    ValidationRule.ARRAY_MIN_ITEMS(1),
                    ValidationRule.ARRAY_MAX_ITEMS(3)
                ],
                "campaign_name": [
                    ValidationRule.REQUIRED,
                    ValidationRule.MIN_LENGTH(5),
                    ValidationRule.MAX_LENGTH(100)
                ],
                "campaign_description": [
                    ValidationRule.MIN_LENGTH(20),
                    ValidationRule.MAX_LENGTH(1000)
                ],
                "budget": [
                    ValidationRule.POSITIVE_NUMBER
                ],
                "duration_days": [
                    ValidationRule.POSITIVE_NUMBER
                ]
            },
            
            "onboarding_complete": {
                # No input validation required for completion step
            }
        }


class FileValidator:
    """Validator for file uploads"""
    
    ALLOWED_FILE_TYPES = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "txt": "text/plain",
        "csv": "text/csv",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif"
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def validate_file(cls, file_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate uploaded file"""
        errors = []
        
        filename = file_data.get("filename", "")
        file_type = file_data.get("file_type", "")
        file_size = file_data.get("file_size", 0)
        
        # Check filename
        if not filename:
            errors.append("Filename is required")
        elif len(filename) > 255:
            errors.append("Filename too long (max 255 characters)")
        
        # Check file type
        if file_type not in cls.ALLOWED_FILE_TYPES.values():
            errors.append(f"File type not allowed: {file_type}")
        
        # Check file size
        if file_size > cls.MAX_FILE_SIZE:
            errors.append(f"File size too large (max {cls.MAX_FILE_SIZE / (1024*1024):.1f}MB)")
        
        if file_size <= 0:
            errors.append("File size must be positive")
        
        return len(errors) == 0, errors


class OnboardingValidator:
    """Main validator orchestrator"""
    
    def __init__(self):
        self.step_validator = StepValidator()
        self.file_validator = FileValidator()
    
    def validate_step_input(self, step_id: str, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate step input with comprehensive checks"""
        try:
            # Basic structure validation
            if not isinstance(data, dict):
                return False, ["Input data must be a dictionary"]
            
            # Step-specific validation
            is_valid, errors = self.step_validator.validate_step_input(step_id, data)
            
            # File validation for evidence upload
            if step_id == "evidence_upload" and "files" in data:
                for file_data in data["files"]:
                    file_valid, file_errors = self.file_validator.validate_file(file_data)
                    if not file_valid:
                        errors.extend([f"File {file_data.get('filename', 'unknown')}: {err}" for err in file_errors])
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def validate_step_transition(self, from_step: Optional[str], to_step: str, step_dependencies: Dict[str, List[str]]) -> tuple[bool, str]:
        """Validate step transition based on dependencies"""
        try:
            dependencies = step_dependencies.get(to_step, [])
            
            for dep_step in dependencies:
                if from_step != dep_step and not self._is_step_completed(dep_step):
                    return False, f"Cannot transition to {to_step} without completing {dep_step}"
            
            return True, "Transition valid"
            
        except Exception as e:
            logger.error(f"Transition validation error: {e}")
            return False, f"Transition validation error: {str(e)}"
    
    def _is_step_completed(self, step_id: str) -> bool:
        """Check if step is completed (placeholder for actual implementation)"""
        # This would integrate with the state service
        return False
