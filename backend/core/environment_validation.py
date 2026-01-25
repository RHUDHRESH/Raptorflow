import os
from typing import List, Dict, Any
from pydantic import BaseModel, validator
import logging

logger = logging.getLogger(__name__)


class EnvironmentConfig(BaseModel):
    """Validate required environment variables"""
    
    supabase_url: str
    supabase_service_key: str
    supabase_storage_bucket: str
    vertex_ai_project_id: str
    
    @validator('supabase_url')
    def validate_supabase_url(cls, v):
        if not v.startswith('https://') and not v.startswith('http://'):
            raise ValueError('SUPABASE_URL must be a valid URL')
        return v
    
    @validator('supabase_storage_bucket')
    def validate_bucket_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('SUPABASE_STORAGE_BUCKET must be at least 3 characters')
        return v
    
    @validator('vertex_ai_project_id')
    def validate_project_id(cls, v):
        if not v or len(v) < 6:
            raise ValueError('VERTEX_AI_PROJECT_ID must be at least 6 characters')
        return v


def validate_environment() -> Dict[str, Any]:
    """Validate all required environment variables"""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY', 
        'SUPABASE_STORAGE_BUCKET',
        'VERTEX_AI_PROJECT_ID'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    try:
        return EnvironmentConfig(
            supabase_url=os.getenv('SUPABASE_URL'),
            supabase_service_key=os.getenv('SUPABASE_SERVICE_KEY'),
            supabase_storage_bucket=os.getenv('SUPABASE_STORAGE_BUCKET'),
            vertex_ai_project_id=os.getenv('VERTEX_AI_PROJECT_ID')
        )
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        raise ValueError(f"Environment validation failed: {e}")


def validate_optional_environment() -> Dict[str, Any]:
    """Validate optional environment variables with defaults"""
    config = {
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', '50')),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'gcp_region': os.getenv('GCP_REGION', 'us-central1'),
        'vertex_ai_location': os.getenv('VERTEX_AI_LOCATION', 'us-central1'),
        'vertex_ai_model': os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-flash'),
        'ocr_provider': os.getenv('OCR_PROVIDER', 'tesseract'),
        'mock_redis': os.getenv('MOCK_REDIS', 'true').lower() == 'true',
        'enable_rate_limiting': os.getenv('ENABLE_RATE_LIMITING', 'false').lower() == 'true',
        'enable_usage_tracking': os.getenv('ENABLE_USAGE_TRACKING', 'true').lower() == 'true',
        'enable_background_jobs': os.getenv('ENABLE_BACKGROUND_JOBS', 'false').lower() == 'true',
    }
    
    # Validate numeric values
    if config['max_file_size_mb'] <= 0 or config['max_file_size_mb'] > 1000:
        logger.warning(f"Invalid MAX_FILE_SIZE_MB: {config['max_file_size_mb']}, using default 50")
        config['max_file_size_mb'] = 50
    
    return config


def check_service_credentials() -> Dict[str, bool]:
    """Check if service credentials are properly configured"""
    checks = {
        'google_credentials': bool(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')),
        'gemini_api_key': bool(os.getenv('GEMINI_API_KEY')),
        'brave_search_key': bool(os.getenv('BRAVE_SEARCH_API_KEY')),
        'sentry_dsn': bool(os.getenv('SENTRY_DSN')),
    }
    
    # Log warnings for missing credentials
    for service, configured in checks.items():
        if not configured:
            logger.warning(f"Missing credentials for service: {service}")
    
    return checks


def validate_all_environment() -> Dict[str, Any]:
    """Perform complete environment validation"""
    try:
        # Validate required variables
        required_config = validate_environment()
        
        # Validate optional variables
        optional_config = validate_optional_environment()
        
        # Check service credentials
        service_checks = check_service_credentials()
        
        logger.info("Environment validation completed successfully")
        
        return {
            'required': required_config.dict(),
            'optional': optional_config,
            'service_checks': service_checks,
            'valid': True
        }
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return {
            'error': str(e),
            'valid': False
        }
