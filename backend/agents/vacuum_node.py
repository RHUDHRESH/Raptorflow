from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class VacuumValidReport(BaseModel):
    is_valid: bool = Field(description="Whether the data record meets mandatory schema requirements")
    missing_fields: List[str] = Field(description="List of required fields that are missing")
    type_errors: List[str] = Field(description="List of fields with incorrect data types")

class VacuumAccurateReport(BaseModel):
    is_accurate: bool = Field(description="Whether the data points are logically consistent and cross-referenced")
    discrepancies: List[str] = Field(description="Specific logical errors or inaccuracies found")

class VacuumUniformReport(BaseModel):
    is_uniform: bool = Field(description="Whether the data follows the standard formatting (ISO dates, etc)")
    fixed_record: dict = Field(description="The record after applying standardization")

class VacuumNode:
    """
    Implements Osipov's 'VACUUM' protocol for SOTA data quality.
    V: Valid (Data types, constraints)
    A: Accurate (Fact-checking, cross-ref)
    C: Consistent (No internal contradictions)
    U: Uniform (Formatting, units)
    U: Unified (Single source of truth)
    M: Model-ready (Ready for LLM/ML consumption)
    """
    
    @staticmethod
    def validate_record(record: dict, required_fields: List[str], schema: dict) -> VacuumValidReport:
        missing = [f for f in required_fields if f not in record or record[f] is None]
        type_errs = []
        
        for field, expected_type in schema.items():
            if field in record and record[field] is not None:
                if not isinstance(record[field], expected_type):
                    type_errs.append(f"Field '{field}' expected {expected_type}, got {type(record[field])}")
                    
        return VacuumValidReport(
            is_valid=len(missing) == 0 and len(type_errs) == 0,
            missing_fields=missing,
            type_errors=type_errs
        )

    @staticmethod
    def evaluate_accuracy(record: dict) -> VacuumAccurateReport:
        discrepancies = []
        
        # Example Cross-Reference: Start Date vs End Date
        if 'start_date' in record and 'end_date' in record:
            if record['start_date'] > record['end_date']:
                discrepancies.append(f"Start date ({record['start_date']}) is after end date ({record['end_date']})")
        
        # Example Cross-Reference: Metric Targets
        if 'target_value' in record:
            if record['target_value'] < 0:
                discrepancies.append(f"Target value ({record['target_value']}) cannot be negative")

        return VacuumAccurateReport(
            is_accurate=len(discrepancies) == 0,
            discrepancies=discrepancies
        )

    @staticmethod
    def standardize(record: dict) -> VacuumUniformReport:
        fixed = record.copy()
        is_uniform = True
        
        # Standardize Dates to ISO
        for key in ['created_at', 'start_date', 'end_date', 'scheduled_at']:
            if key in fixed and isinstance(fixed[key], str):
                try:
                    # Simple check for ISO-like string
                    datetime.fromisoformat(fixed[key].replace('Z', '+00:00'))
                except ValueError:
                    is_uniform = False
                    # We could add more complex parsing here if needed
        
        # Standardize Coordinates
        for key in ['lat', 'lng', 'latitude', 'longitude']:
            if key in fixed and isinstance(fixed[key], (int, float)):
                fixed[key] = round(float(fixed[key]), 6)

        return VacuumUniformReport(
            is_uniform=is_uniform,
            fixed_record=fixed
        )
