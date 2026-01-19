# GCP Production Configuration for SOTA OCR System
# Optimized settings for Google Cloud Platform deployment

import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class GCPConfig:
    """GCP-specific configuration for SOTA OCR System"""
    
    # GCP Project Settings
    project_id: str = os.getenv("GCP_PROJECT_ID", "raptorflow-ocr-prod")
    region: str = os.getenv("GCP_REGION", "us-central1")
    zone: str = os.getenv("GCP_ZONE", "us-central1-a")
    
    # Compute Settings
    machine_type: str = "n1-standard-8"
    gpu_type: str = "nvidia-tesla-a100"
    gpu_count: int = 1
    preemptible: bool = False
    min_cpu_platform: str = "Intel_Cascade_Lake"
    
    # Storage Settings
    storage_bucket: str = os.getenv("STORAGE_BUCKET", "raptorflow-ocr-storage")
    storage_class: str = "STANDARD"
    storage_location: str = "us-central1"
    
    # Network Settings
    network_name: str = "ocr-network"
    subnet_name: str = "ocr-subnet"
    firewall_name: str = "ocr-firewall"
    
    # IAM Settings
    service_account: str = os.getenv("SERVICE_ACCOUNT", "ocr-service-account@raptorflow-ocr-prod.iam.gserviceaccount.com")
    
    # OCR Model Settings
    models_enabled: List[str] = ["chandra_ocr_8b", "dots_ocr", "deepseek_ocr_3b"]
    max_concurrent_models: int = 2
    model_cache_size_gb: int = 50
    model_timeout_seconds: int = 300
    
    # GPU Memory Management
    gpu_memory_limit_gb: int = 35
    gpu_memory_utilization_threshold: float = 0.8
    gpu_auto_scale: bool = True
    
    # Performance Settings
    target_throughput_pages_per_minute: int = 100
    max_latency_seconds: int = 30
    batch_size: int = 32
    
    # Cost Optimization
    enable_preemptible_instances: bool = True
    preemptible_instance_ratio: float = 0.7
    autoscaling_min_instances: int = 1
    autoscaling_max_instances: int = 5
    autoscaling_target_cpu_utilization: float = 70
    
    # Monitoring Settings
    enable_stackdriver: bool = True
    log_level: str = "INFO"
    metrics_collection_interval: int = 60
    alerting_enabled: bool = True
    
    # Security Settings
    enable_vpc_service_controls: bool = True
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    iam_conditions_enabled: bool = True
    
    # Backup Settings
    enable_backups: bool = True
    backup_schedule: str = "daily"
    backup_retention_days: int = 30
    disaster_recovery_enabled: bool = True
    
    # API Settings
    api_rate_limit: int = 1000
    api_timeout_seconds: int = 60
    api_enable_cors: bool = True
    api_cors_origins: List[str] = ["https://raptorflow.ai", "https://app.raptorflow.ai"]
    
    # Database Settings
    database_instance: str = "ocr-monitoring-db"
    database_tier: str = "db-n1-standard-2"
    database_storage_size: str = "100GB"
    
    # Redis Settings
    redis_instance: str = "ocr-cache"
    redis_tier: str = "redis-n1-standard-2"
    redis_memory_size: str = "4GB"
    
    # Load Balancer Settings
    load_balancer_type: str = "HTTP(S)"
    load_balancer_name: str = "ocr-lb"
    ssl_certificate_enabled: bool = True
    
    # Container Settings
    container_registry: str = "us-central1-docker.pkg.dev/raptorflow-ocr-prod/ocr"
    container_image_tag: str = "latest"
    container_cpu_limit: str = "4000m"
    container_memory_limit: str = "16Gi"
    container_gpu_limit: int = 1
    
    # Environment Variables
    node_env: str = "production"
    python_version: str = "3.9"
    cuda_visible_devices: str = "0"
    torch_cuda_arch_list: str = "8.0"
    
    # Cost Tracking
    cost_tracking_enabled: bool = True
    budget_alerts_enabled: bool = True
    monthly_budget_limit: int = 5000

class GCPProductionConfig:
    """Production configuration optimized for GCP deployment"""
    
    def __init__(self):
        self.gcp_config = GCPConfig()
        
    def get_orchestrator_config(self) -> Dict[str, Any]:
        """Get orchestrator configuration for GCP"""
        return {
            "selection_strategy": "auto",
            "cost_budget_per_page": 0.5,
            "max_latency_seconds": self.gcp_config.max_latency_seconds,
            "min_accuracy": 0.85,
            "gcp_project_id": self.gcp_config.project_id,
            "gcp_region": self.gcp_config.region,
            "gpu_memory_limit": self.gcp_config.gpu_memory_limit_gb,
            "models_enabled": self.gcp_config.models_enabled
        }
    
    def get_preprocessor_config(self) -> Dict[str, Any]:
        """Get preprocessor configuration for GCP"""
        return {
            "target_dpi": 200,
            "enable_enhancement": True,
            "pipeline": "auto",
            "gpu_accelerated": True,
            "batch_size": self.gcp_config.batch_size,
            "max_concurrent_jobs": self.gcp_config.autoscaling_max_instances,
            "storage_bucket": self.gcp_config.storage_bucket
        }
    
    def get_quality_assurance_config(self) -> Dict[str, Any]:
        """Get quality assurance configuration for GCP"""
        return {
            "text_coherence": {"enabled": True, "coherence_threshold": 0.7},
            "layout_consistency": {"enabled": True, "consistency_threshold": 0.8},
            "confidence_threshold": {"enabled": True, "min_confidence": 0.85},
            "semantic_validation": {"enabled": True, "semantic_threshold": 0.7},
            "cross_model_verification": {"enabled": True, "agreement_threshold": 0.8},
            "human_review_trigger": {"enabled": True, "review_threshold": 0.7},
            "monitoring_enabled": self.gcp_config.enable_stackdriver
        }
    
    def get_ensemble_config(self) -> Dict[str, Any]:
        """Get ensemble configuration for GCP"""
        return {
            "enabled_models": self.gcp_config.models_enabled,
            "voting_method": "weighted",
            "confidence_threshold": 0.8,
            "consensus_threshold": 0.7,
            "timeout_seconds": self.gcp_config.model_timeout_seconds,
            "max_parallel_models": self.gcp_config.max_concurrent_models,
            "fallback_strategy": "best_confidence",
            "gpu_memory_management": {
                "limit_gb": self.gcp_config.gpu_memory_limit_gb,
                "utilization_threshold": self.gcp_config.gpu_memory_utilization_threshold,
                "auto_scale": self.gcp_config.gpu_auto_scale
            }
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration for GCP"""
        return {
            "metrics": {
                "retention_hours": 24,
                "collection_interval": self.gcp_config.metrics_collection_interval,
                "gcp_project_id": self.gcp_config.project_id,
                "gcp_region": self.gcp_config.region
            },
            "alerts": {
                "accuracy_degradation": {
                    "metric_name": "average_confidence",
                    "threshold": 0.85,
                    "comparison": "lt",
                    "severity": "warning",
                    "enabled": True,
                    "cooldown_minutes": 15
                },
                "high_error_rate": {
                    "metric_name": "error_rate",
                    "threshold": 0.05,
                    "comparison": "gt",
                    "severity": "critical",
                    "enabled": True,
                    "cooldown_minutes": 5
                },
                "gpu_memory_high": {
                    "metric_name": "gpu_utilization",
                    "threshold": 0.9,
                    "comparison": "gt",
                    "severity": "warning",
                    "enabled": True,
                    "cooldown_minutes": 10
                }
            },
            "stackdriver": {
                "enabled": self.gcp_config.enable_stackdriver,
                "log_level": self.gcp_config.log_level,
                "project_id": self.gcp_config.project_id
            }
        }
    
    def get_service_config(self) -> Dict[str, Any]:
        """Get main service configuration for GCP"""
        return {
            "orchestrator": self.get_orchestrator_config(),
            "preprocessor": self.get_preprocessor_config(),
            "quality_assurance": self.get_quality_assurance_config(),
            "ensemble": self.get_ensemble_config(),
            "monitoring": self.get_monitoring_config(),
            "enable_ensemble": True,
            "enable_quality_check": True,
            "enable_monitoring": self.gcp_config.enable_stackdriver,
            "max_file_size_mb": 100,
            "supported_formats": ["pdf", "jpg", "jpeg", "png", "tiff", "bmp"],
            "max_concurrent_jobs": self.gcp_config.autoscaling_max_instances,
            "gcp": {
                "project_id": self.gcp_config.project_id,
                "region": self.gcp_config.region,
                "zone": self.gcp_config.zone,
                "machine_type": self.gcp_config.machine_type,
                "gpu_type": self.gcp_config.gpu_type,
                "gpu_count": self.gcp_config.gpu_count,
                "preemptible": self.gcp_config.preemptible,
                "service_account": self.gcp_config.service_account,
                "storage_bucket": self.gcp_config.storage_bucket,
                "network_name": self.gcp_config.network_name,
                "subnet_name": self.gcp_config.subnet_name
            }
        }
    
    def get_model_configs(self) -> Dict[str, Any]:
        """Get model configurations optimized for GCP"""
        return {
            "chandra_ocr_8b": {
                "model_path": "/app/models/chandra-ocr-8b.pt",
                "api_url": "https://chandra-ocr.raptorflow.ai/api",
                "api_key": os.getenv("CHANDRA_OCR_API_KEY"),
                "gpu_memory_gb": 16,
                "batch_size": 4,
                "timeout_seconds": 60,
                "gcp_optimized": True,
                "use_gpu": True
            },
            "dots_ocr": {
                "model_path": "/app/models/dots-ocr.pt",
                "api_url": "https://dots.ocr.raptorflow.ai/api",
                "api_key": os.getenv("DOTS_OCR_API_KEY"),
                "gpu_memory_gb": 8,
                "batch_size": 8,
                "timeout_seconds": 45,
                "gcp_optimized": True,
                "use_gpu": True
            },
            "deepseek_ocr_3b": {
                "model_path": "/app/models/deepseek-ocr-3b.pt",
                "api_url": "https://deepseek-ocr.raptorflow.ai/api",
                "api_key": os.getenv("DEEPSEEK_OCR_API_KEY"),
                "gpu_memory_gb": 6,
                "batch_size": 16,
                "timeout_seconds": 30,
                "gcp_optimized": True,
                "use_gpu": True
            },
            "olm_ocr_2_7b": {
                "model_path": "/app/models/olm-ocr-2-7b.pt",
                "api_url": "https://olm-ocr.raptorflow.ai/api",
                "api_key": os.getenv("OLM_OCR_API_KEY"),
                "gpu_memory_gb": 12,
                "batch_size": 6,
                "timeout_seconds": 50,
                "gcp_optimized": True,
                "use_gpu": True
            },
            "lighton_ocr": {
                "model_path": "/app/models/lighton-ocr.pt",
                "api_url": "https://lighton-ocr.raptorflow.ai/api",
                "api_key": os.getenv("LIGHTON_OCR_API_KEY"),
                "gpu_memory_gb": 4,
                "batch_size": 20,
                "timeout_seconds": 25,
                "gcp_optimized": True,
                "use_gpu": True
            }
        }
    
    def get_autoscaling_config(self) -> Dict[str, Any]:
        """Get autoscaling configuration for GCP"""
        return {
            "enabled": True,
            "min_instances": self.gcp_config.autoscaling_min_instances,
            "max_instances": self.gcp_config.autoscaling_max_instances,
            "target_cpu_utilization": self.gcp_config.autoscaling_target_cpu_utilization,
            "target_throughput": self.gcp_config.target_throughput_pages_per_minute,
            "scale_up_cooldown": 60,
            "scale_down_cooldown": 300,
            "preemptible_ratio": self.gcp_config.preemptible_instance_ratio,
            "metrics": [
                {
                    "type": "cpu_utilization",
                    "target": 70
                },
                {
                    "type": "custom_metric",
                    "name": "ocr_queue_length",
                    "target": 100
                },
                {
                    "type": "custom_metric", 
                    "name": "gpu_utilization",
                    "target": 80
                }
            ]
        }
    
    def get_cost_optimization_config(self) -> Dict[str, Any]:
        """Get cost optimization configuration for GCP"""
        return {
            "enable_preemptible": self.gcp_config.enable_preemptible_instances,
            "preemptible_ratio": self.gcp_config.preemptible_instance_ratio,
            "committed_use_discounts": {
                "enabled": True,
                "commitment_type": "12-month",
                "resource_type": "compute",
                "accelerator_type": self.gcp_config.gpu_type,
                "accelerator_count": self.gcp_config.gpu_count
            },
            "sustained_use_discounts": {
                "enabled": True,
                "minimum_usage_percent": 25
            },
            "right_sizing": {
                "enabled": True,
                "monitoring_period": 7,  # days
                "adjustment_threshold": 20  # percent
            },
            "budget_alerts": {
                "enabled": self.gcp_config.budget_alerts_enabled,
                "monthly_limit": self.gcp_config.monthly_budget_limit,
                "alert_thresholds": [70, 90, 100]  # percent
            }
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration for GCP"""
        return {
            "vpc_service_controls": {
                "enabled": self.gcp_config.enable_vpc_service_controls,
                "policy_name": "ocr_policy",
                "allowed_projects": [self.gcp_config.project_id]
            },
            "encryption": {
                "at_rest": self.gcp_config.encryption_at_rest,
                "in_transit": self.gcp_config.encryption_in_transit,
                "customer_managed_keys": {
                    "enabled": True,
                    "key_ring": "ocr-keyring",
                    "key_name": "ocr-key"
                }
            },
            "iam": {
                "conditions_enabled": self.gcp_config.iam_conditions_enabled,
                "least_privilege": True,
                "service_account": self.gcp_config.service_account,
                "roles": [
                    "roles/compute.admin",
                    "roles/storage.admin",
                    "roles/logging.admin",
                    "roles/monitoring.admin"
                ]
            },
            "network": {
                "private_google_access": True,
                "cloud_armor": {
                    "enabled": True,
                    "rules": [
                        {
                            "name": "rate_limit",
                            "priority": 1000,
                            "action": "throttle",
                            "rate_limit": {
                                "requests_per_second": 100
                            }
                        }
                    ]
                }
            }
        }
    
    def get_backup_config(self) -> Dict[str, Any]:
        """Get backup configuration for GCP"""
        return {
            "enabled": self.gcp_config.enable_backups,
            "schedule": self.gcp_config.backup_schedule,
            "retention_days": self.gcp_config.backup_retention_days,
            "disaster_recovery": {
                "enabled": self.gcp_config.disaster_recovery_enabled,
                "backup_regions": ["us-east1", "us-west1"],
                "cross_region_replication": True,
                "rpo_hours": 4,  # Recovery Point Objective
                "rto_hours": 2   # Recovery Time Objective
            },
            "storage": {
                "backup_bucket": f"{self.gcp_config.storage_bucket}-backups",
                "storage_class": "NEARLINE",
                "lifecycle_rules": [
                    {
                        "action": "Delete",
                        "condition": {
                            "age": self.gcp_config.backup_retention_days
                        }
                    }
                ]
            }
        }

# Create production configuration instance
production_config = GCPProductionConfig()

# Export configuration functions
def get_production_config() -> Dict[str, Any]:
    """Get complete production configuration for GCP"""
    return {
        "service": production_config.get_service_config(),
        "models": production_config.get_model_configs(),
        "autoscaling": production_config.get_autoscaling_config(),
        "cost_optimization": production_config.get_cost_optimization_config(),
        "security": production_config.get_security_config(),
        "backup": production_config.get_backup_config()
    }

def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration"""
    return {
        "production": get_production_config(),
        "staging": {
            **get_production_config(),
            "autoscaling": {
                **production_config.get_autoscaling_config(),
                "max_instances": 2
            },
            "cost_optimization": {
                **production_config.get_cost_optimization_config(),
                "preemptible_ratio": 0.9
            }
        },
        "development": {
            **get_production_config(),
            "autoscaling": {
                **production_config.get_autoscaling_config(),
                "max_instances": 1
            },
            "models": {
                **production_config.get_model_configs(),
                "chandra_ocr_8b": {
                    **production_config.get_model_configs()["chandra_ocr_8b"],
                    "batch_size": 1
                }
            }
        }
    }
