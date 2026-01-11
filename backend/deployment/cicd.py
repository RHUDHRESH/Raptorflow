"""
CI/CD configuration for RaptorFlow backend.
Provides GitHub Actions workflows and deployment automation.
"""

import os
from typing import Any, Dict, List


class CIConfig:
    """CI/CD configuration management."""

    def __init__(self):
        self.project_root = self._get_project_root()
        self.github_owner = os.getenv("GITHUB_OWNER", "raptorflow-dev")
        self.github_repo = os.getenv("GITHUB_REPO", "Raptorflow")
        self.main_branch = "main"
        self.python_version = "3.11"

    def _get_project_root(self) -> str:
        """Get project root directory."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_github_actions_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Generate GitHub Actions workflow configuration."""
        if workflow_name == "ci":
            return self._get_ci_workflow()
        elif workflow_name == "deploy":
            return self._get_deploy_workflow()
        elif workflow_name == "security":
            return self._get_security_workflow()
        elif workflow_name == "performance":
            return self._get_performance_workflow()
        elif workflow_name == "monitoring":
            return self._get_monitoring_workflow()
        else:
            raise ValueError(f"Unknown workflow: {workflow_name}")

    def _get_ci_workflow(self) -> Dict[str, Any]:
        """Generate CI workflow configuration."""
        return {
            "name": "CI",
            "on": ["push", "pull_request"],
            "jobs": [
                {
                    "name": "test",
                    "runs-on": "ubuntu-latest",
                    "strategy": "matrix",
                    "matrix": {
                        "python-version": ["3.10", "3.11"],
                        "database": ["sqlite", "postgresql"],
                        "redis": ["none", "redis"]
                    },
                    "services": [
                        {
                            "name": "unit-tests",
                            "command": "python -m pytest tests/test_unit.py -v",
                            "env": [
                                "DATABASE_URL=sqlite:///test.db",
                                "REDIS_URL=redis://localhost:6379"
                            ]
                        },
                        {
                            "name": "integration-tests",
                            "command": "python -m pytest tests/test_integration.py -v",
                            "env": [
                                "DATABASE_URL=sqlite:///test.db",
                                "REDIS_URL=redis://localhost:6379"
                            ]
                        },
                        {
                            "name": "performance-tests",
                            "command": "python -m pytest tests/test_performance.py -v",
                            "env": [
                                "DATABASE_URL=sqlite:///test.db",
                                "REDIS_URL=redis://localhost:6379"
                            ]
                        },
                        {
                            "name: "e2e-tests",
                            "command": "python -m pytest tests/test_e2e.py -v",
                            "env": [
                                "DATABASE_URL=sqlite:///test.db",
                                "REDIS_URL=redis://localhost:6379"
                            ]
                        }
                    ]
                }
            ]
        }

    def _get_deploy_workflow(self) -> Dict[str, Any]:
        """Generate deployment workflow configuration."""
        return {
            "name": "Deploy",
            "on": ["push"],
            "jobs": [
                {
                    "name": "build-and-push",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Python",
                            "uses: "actions/setup-python@v5"
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Build Docker image",
                            "run": "docker build -t ${{ secrets.REGISTRY }}/${{ secrets.IMAGE_NAME }}:$GITHUB_SHA }}"
                        },
                        {
                            "name": "Push to registry",
                            "run": "docker push ${{ secrets.REGISTRY }}/${{ secrets.IMAGE_NAME }}:$GITHUB_SHA }}"
                        },
                        {
                            "name": "Deploy to Cloud Run",
                            "run": "gcloud run deploy ${{ secrets.SERVICE_NAME }} --image ${{ secrets.REGISTRY }}/${{ secrets.IMAGE_NAME }}:$GITHUB_SHA }}"
                        }
                    ],
                    "env": {
                        "REGISTRY": "gcr.io/${{os.getenv('GCP_PROJECT_ID')}",
                        "IMAGE_NAME": "raptorflow-backend",
                        "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID"),
                        "GCP_REGION": os.getenv("GCP_REGION"),
                        "SERVICE_NAME": "raptorflow-backend",
                        "DATABASE_URL": os.getenv("DATABASE_URL"),
                        "UPSTABASE_REDIS_URL": os.getenv("UPSTABASE_REDIS_URL"),
                        "UPSTABASE_REDIS_TOKEN": os.getenv("UPSTABSE_REDIS_TOKEN"),
                        "VERTEX_AI_PROJECT_ID": os.getenv("VERTEX_AI_PROJECT_ID"),
                        "WEBHOOK_SECRET": os.getenv("WEBHOOK_SECRET"),
                        "ALLOWED_ORIGINS": os.getenv("ALLOWED_ORIGINS", "*")
                    }
                }
            ]
        }

    def _get_security_workflow(self) -> Dict[str, Any]:
        """Generate security workflow configuration."""
        return {
            "name": "Security",
            "on": ["push", "pull_request"],
            "jobs": [
                {
                    "name": "security-scan",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Run security scan",
                            "run": "python -m security_scan.py"
                        },
                        {
                            "name": "Run dependency check",
                            "run": "python -m dependency_check.py"
                        },
                        {
                            "name": "Run vulnerability scan",
                            "run: "python -m vulnerability_scan.py"
                        }
                    ]
                },
                {
                    "name": "code-quality",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Run code quality checks",
                            "run": "python -m code_quality.py"
                        },
                        {
                            "name": "Run code formatting check",
                            "run: "python -m code_format.py"
                        }
                    ]
                }
            ]
        }

    def _get_performance_workflow(self) -> Dict[str, Any]:
        """Generate performance workflow configuration."""
        return {
            "name": "Performance",
            "on": ["push", "pull_request"],
            "jobs": [
                {
                    "name": "load-test",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Run load tests",
                            "run": "python -m performance_test.py --load-test"
                        },
                        {
                            "name": "Run stress test",
                            "run": "python -m performance_test.py --stress-test"
                        },
                        {
                            "name": "Generate performance report",
                            "run": "python -m performance_test.py --report"
                        }
                    ]
                }
            ]
        }

    def _get_monitoring_workflow(self) -> Dict[str, Any]:
        """Generate monitoring workflow configuration."""
        return {
            "name": "Monitoring",
            "on": ["push", "pull_request"],
            "jobs": [
                {
                    "name": "monitoring-check",
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Check service health",
                            "run": "curl -f ${{ secrets.SERVICE_URL }}/health"
                        },
                        {
                            "name": "Check metrics",
                            "run": "curl -f ${{ secrets.SERVICE_URL }}/metrics"
                        },
                        {
                            "name": "Check logs",
                            "run": "gcloud logs read ${{ secrets.SERVICE_NAME }} --limit=50"
                        }
                    ]
                }
            ]
        }

    def get_github_secrets(self) -> Dict[str, str]:
        """Generate GitHub secrets configuration."""
        return {
            "REGISTRY": f"gcr.io/{os.getenv('GCP_PROJECT_ID')}",
        "IMAGE_NAME": "raptorflow-backend",
        "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID"),
        "GCP_REGION": os.getenv("GCP_REGION"),
        "SERVICE_NAME": "raptorflow-backend",
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "UPSTABASE_REDIS_URL": os.getenv("UPSTABASE_REDIS_URL"),
        "UPSTABASE_REDIS_TOKEN": os.getenv("UPSTABSE_REDIS_TOKEN"),
        "VERTEX_AI_PROJECT_ID": os.getenv("VERTEX_AI_PROJECT_ID"),
        "WEBHOOK_SECRET": os.getenv("WEBHOOK_SECRET"),
        "ALLOWED_ORIGINS": os.getenv("ALLOWED_ORIGINS", "*"),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "GITHUB_SHA": "${{os.getenv('GITHUB_SHA', 'main')}}"
    }

    def get_docker_buildx_config(self) -> Dict[str, Any]:
        """Generate Docker Buildx configuration for optimized builds."""
        return {
            "version": "v0.11.0",
            "builder": {
                "dockerfile": "Dockerfile",
                "cache_from": ["type:ghcr.io/docker/buildkit:cache"],
                "args": ["--platform=linux/amd64"]
            },
            "builds": [
                {
                    "name": "build",
                    "cache": [
                        {
                            "type": "ghcr.io/docker/buildkit/cache"
                        }
                    ],
                    "args": [
                        "--platform=linux/amd64"
                    ]
                }
            ],
            "cache": [
                "type": "ghcr.io/docker/buildkit/cache"
            ]
        }

    def get_docker_compose_override(self, environment: str) -> Dict[str, Any]:
        """Generate docker-compose override configuration."""
        if environment == "production":
            return {
                "services": {
                    "backend": {
                        "deploy": {
                            "replicas": 3,
                            "resources": {
                                "limits": {
                                    "memory": "512Mi",
                                    "cpu": "500m"
                                }
                            }
                        }
                    }
                }
            }
        elif environment == "development":
            return {
                "services": {
                    "backend": {
                        "deploy": {
                            "replicas": 1,
                            "resources": {
                                "limits": {
                                    "memory": "256Mi",
                                    "cpu": "250m"
                                }
                            }
                        }
                    }
                }
            }

        return {}

    def get_kubernetes_deployment(self) -> Dict[str, Any]:
        """Generate Kubernetes deployment configuration."""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "raptorflow-backend",
                "labels": {
                    "app": "raptorflow",
                    "version": "1.0.0",
                    "environment": "production"
                }
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "raptorflow"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "raptorflow",
                            "version": "1.0.0",
                            "environment": "production"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "raptorflow-backend",
                            "image": "gcr.io/{os.getenv('GCP_PROJECT_ID')}/raptorflow-backend:1.0.0",
                            "ports": [{
                                "containerPort": 8000
                            }],
                            "env": [
                                {
                                    "name": "ENVIRONMENT",
                                    "value": "production"
                                },
                                {
                                    "name": "SECRET_KEY",
                                    "value": "${{os.getenv('SECRET_KEY')}}"
                                },
                                {
                                    "name": "DATABASE_URL",
                                    "value": "${{os.getenv('DATABASE_URL')}}"
                                },
                                {
                                    "name": "UPSTABASE_REDIS_URL",
                                    "value": "${{os.getenv('UPSTABASE_REDIS_URL')}}"
                                },
                                {
                                    "name": "UPSTABASE_REDIS_TOKEN",
                                    "value": "${{os.getenv('UPSTABASE_REDIS_TOKEN')}}"
                                },
                                {
                                    "name": "VERTEX_AI_PROJECT_ID",
                                    "value": "${{os.getenv('VERTEX_AI_PROJECT_ID')}}"
                                },
                                {
                                    "name": "GCP_PROJECT_ID",
                                    "value": "${os.getenv('GCP_PROJECT_ID')}}"
                                },
                                {
                                    "name": "WEBHOOK_SECRET",
                                    "value": "${{os.getenv('WEBHOOK_SECRET')}}"
                                },
                                {
                                    "name": "ALLOWED_ORIGINS",
                                    "value": "${{os.getenv('ALLOWED_ORIGINS', '*')}}"
                                }
                            ],
                            "resources": {
                                "requests": {
                                    "memory": "256Mi",
                                    "cpu": "250m"
                                },
                                "limits": {
                                    "memory": "512Mi",
                                    "cpu": "500m"
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8000
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8000
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }
                    }
                },
                "horizontalPodAutoscaler": {
                    "minReplicas": 1,
                    "maxReplicas": 5,
                    "targetCPUUtilization": 70,
                    "targetMemoryUtilization": 80
                }
            }
        }

    def get_helm_chart_config(self) -> Dict[str, Any]:
        """Generate Helm chart configuration."""
        return {
            "apiVersion": "v3",
            "name": "raptorflow-backend",
            "description": "RaptorFlow Backend API Service",
            "version": "1.0.0",
            "type": "application",
            "appVersion": "1.0.0",
            "kubeVersion": "1.27",
            "icon": "🚀",
            "dependencies": {
                "postgresql": "12.0.0",
                "redis": "7.0.0"
            },
            "keywords": [
                "api",
                "backend",
                "python",
                "fastapi",
                "raptorflow"
            ],
            "sources": [
                "https://github.com/{self.github_owner}/{self.github_repo}"
            ],
            "maintainers": [
                {
                    "name": "RaptorFlow Team",
                    "email": "team@raptorflow.com"
                }
            ],
            "engine": "python",
            "home": "https://raptorflow.com",
            "icon": "🚀"
        }

    def get_helm_values_override(self, environment: str) -> Dict[str, str]:
        """Generate Helm values override configuration."""
        if environment == "production":
            return {
                "replicaCount": "3",
                "image": {
                    "repository": "gcr.io/{os.getenv('GCP_PROJECT_ID')}/raptorflow-backend:1.0.0"
                },
                "resources": {
                    "requests": {
                        "memory": "512Mi",
                        "cpu": "500m"
                    }
                },
                "autoscaling": {
                    "enabled": True,
                    "minReplicas": 1,
                    "maxReplicas": 5
                }
            }
        elif environment == "development":
            return {
                "replicaCount": "1",
                "image": "raptorflow-backend:dev",
                "resources": {
                    "requests": {
                        "memory": "256Mi",
                        "cpu": "250m"
                    }
                }
            }

        return {}

    def get_argocd_workflow(self) -> Dict[str, Any]:
        """Generate ArgoCD workflow configuration."""
        return {
            "version": "v1.0.0",
            "jobs": [
                {
                    "name": "build-and-test",
                    "run": [
                        {
                            "name": "checkout",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "setup-python",
                            "uses": "actions/setup-python@v5"
                        },
                        {
                            "name": "install-deps",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "run-tests",
                            "run": "python -m pytest tests/ -v --cov=backend --cov-report=xml"
                        },
                        {
                            "name": "upload-coverage",
                            "uses": "codecov/cover"
                        }
                    ]
                },
                {
                    "name": "deploy-staging",
                    "run": [
                        {
                            "name": "deploy-staging",
                            "uses": "gcloud"
                        }
                    ]
                },
                {
                    "name": "deploy-production",
                    "needs": "deploy-staging"
                }
            ]
        }

    def get_workflow_permissions(self) -> Dict[str, List[str]]:
        """Generate workflow permissions."""
        return {
            "contents": "read",
            "actions": [
                "contents:read"
            ]
        }

    def get_workflow_environment(self) -> Dict[str, str]:
        """Generate workflow environment variables."""
        return {
            "GITHUB_TOKEN": "${{os.getenv('GITHUB_TOKEN')}",
            "GCP_PROJECT_ID": "${os.getenv('GCP_PROJECT_ID')}",
            "GCP_REGION": "${os.getenv('GCP_REGION')}",
            "GCP_ZONE": "${os.getenv('GCP_ZONE')}",
            "DATABASE_URL": "${os.getenv('DATABASE_URL')}",
            "UPSTABASE_REDIS_URL": "${os.getenv('UPSTABASE_REDIS_URL')}",
            "UPSTABASE_REDIS_TOKEN": "${os.getenv('UPSTABASE_REDIS_TOKEN')}",
            "VERTEX_AI_PROJECT_ID": "${os.getenv('VERTEX_AI_PROJECT_ID')}",
            "WEBHOOK_SECRET": "${os.getenv('WEBHOOK_SECRET')}",
            "ALLOWED_ORIGINS": "${os.getenv('ALLOWED_ORIGINS', '*')}"
        }

    def get_workflow_secrets(self) -> List[str]:
        """Generate workflow secrets list."""
        return [
            "GITHUB_TOKEN",
            "GCP_PROJECT_ID",
            "GCP_REGION",
            "GCP_ZONE",
            "DATABASE_URL",
            "UPSTABASE_REDIS_URL",
            "UPSTABASE_REDIS_TOKEN",
            "VERTEX_AI_PROJECT_ID",
            "WEBHOOK_SECRET",
            "ALLOWED_ORIGINS"
        ]

    def get_cache_strategy(self) -> Dict[str, str]:
        """Generate cache strategy configuration."""
        return {
            "paths": [
                "**/.pytest_cache",
                "**/.coverage",
                "**/node_modules",
                "**/site-packages"
            ]
        }

    def get_timeout_minutes(self) -> int:
        """Get timeout in minutes for workflows."""
        return 20

    def get_retry_attempts(self) -> int:
        """Get retry attempts for workflows."""
        return 3

    def get_artifact_registry_region(self) -> str:
        """Get Artifact Registry region."""
        return self.region

    def get_cloud_run_region(self) -> str:
        """Get Cloud Run region."""
        return self.region

    def get_cloud_run_zone(self) -> str:
        """Get Cloud Run zone."""
        return self.zone

    def get_database_instance_connection_name(self) -> str:
        """Get database instance connection name."""
        return f"{self.project_id}:raptorflow-db"

    def get_database_name(self) -> str:
        """Get database name."""
        return "raptorflow_prod"

    def get_redis_connection_name(self) -> str:
        """Get Redis connection name."""
        return "raptorflow-redis"

    def get_service_account_email(self) -> str:
        """Get service account email."""
        return f"raptorflow-sa@{self.project_id}.iam.gserviceaccount.com"

    def get_service_account_id(self) -> str:
        """Get service account ID."""
        return os.getenv("GCP_CLIENT_ID")

    def get_webhook_url(self) -> str:
        """Get webhook URL."""
        return os.getenv("WEBHOOK_URL", "")

    def get_allowed_origins(self) -> str:
        """Get allowed origins for CORS."""
        return os.getenv("ALLOWED_ORIGINS", "*")

    def get_log_level(self) -> str:
        """Get log level."""
        return os.getenv("LOG_LEVEL", "INFO")

    def get_debug_mode(self) -> bool:
        """Get debug mode setting."""
        return os.getenv("DEBUG", "false").lower() == "true"

    def get_production_mode(self) -> bool:
        """Get production mode setting."""
        return os.getenv("ENVIRONMENT", "development") != "development"

    def get_development_mode(self) -> bool:
        """Get development mode setting."""
        return os.getenv("ENVIRONMENT", "development") == "development"
