"""
Docker configuration for RaptorFlow backend.
Provides Dockerfile, docker-compose, and container orchestration.
"""

import os
from typing import Any, Dict, List


class DockerConfig:
    """Docker configuration management."""

    def __init__(self):
        self.project_root = self._get_project_root()
        self.app_name = "raptorflow-backend"
        self.version = "1.0.0"
        self.python_version = "3.11"

    def _get_project_root(self) -> str:
        """Get project root directory."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_dockerfile_content(self) -> str:
        """Generate Dockerfile content."""
        return f"""# RaptorFlow Backend Dockerfile
FROM python:{self.python_version}-slim

# Set environment variables
ENV PYTHONDONTWRITEPAGE=1 \\
    PYTHONUNBUFFERED=1 \\
    DEBIAN_FRONTEND=noninteractive \\
    NODE_PATH=/usr/local/lib/python{self.python_version}/site-packages

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser \\
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    def get_docker_compose_content(self, environment: str = "development") -> Dict[str, Any]:
        """Generate docker-compose configuration."""
        if environment == "development":
            return self._get_dev_docker_compose()
        elif environment == "production":
            return self._get_prod_docker_compose()
        else:
            raise ValueError(f"Unknown environment: {environment}")

    def _get_dev_docker_compose(self) -> Dict[str, Any]:
        """Development docker-compose configuration."""
        return {
            "version": "3.8",
            "services": {
                "backend": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile"
                    },
                    "ports": ["8000:8000"],
                    "environment": [
                        "ENVIRONMENT=development",
                        "DEBUG=true",
                        "SECRET_KEY=dev-secret-key-change-in-production",
                        "DATABASE_URL=postgresql://postgres:5432/raptorflow_dev",
                        "UPSTABASE_REDIS_URL=redis://redis:6379/raptorflow_dev",
                        "UPSTABASE_REDIS_TOKEN=dev-redis-token",
                        "VERTEX_AI_PROJECT_ID=dev-project-id",
                        "GCP_PROJECT_ID=dev-project-id",
                        "WEBHOOK_SECRET=dev-webhook-secret"
                    ],
                    "volumes": [
                        ".:/app",
                        "./logs:/app/logs"
                    ],
                    "depends_on": ["postgres", "redis"],
                    "restart": "unless-stopped"
                },
                "postgres": {
                    "image": "postgres:15",
                    "environment": [
                        "POSTGRES_DB=raptorflow_dev",
                        "POSTGRES_USER=postgres",
                        "POSTGRES_PASSWORD=postgres",
                        "POSTGRES_HOST_AUTH_METHOD=trust"
                    ],
                    "ports": ["5432:5432"],
                    "volumes": [
                        "postgres_data:/var/lib/postgresql/data"
                    ],
                    "restart": "unless-stopped"
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": ["6379:6379"],
                    "volumes": [
                        "redis_data:/data"
                    ],
                    "restart": "unless-stopped"
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80"],
                    "volumes": [
                        "./nginx/nginx.conf:/etc/nginx/nginx.conf",
                        "./nginx/ssl:/etc/nginx/ssl"
                    ],
                    "depends_on": ["backend"],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "postgres_data": {},
                "redis_data": {}
            }
        }

    def _get_prod_docker_compose(self) -> Dict[str, Any]:
        """Production docker-compose configuration."""
        return {
            "version": "3.8",
            "services": {
                "backend": {
                    "image": f"gcr.io/{os.getenv('GCP_PROJECT_ID', 'raptorflow-prod')}/{self.app_name}:{self.version}",
                    "ports": ["8000:8000"],
                    "environment": [
                        "ENVIRONMENT=production",
                        "DEBUG=false",
                        "SECRET_KEY=${{os.getenv('SECRET_KEY')}",
                        "DATABASE_URL=${{os.getenv('DATABASE_URL')}",
                        "UPSTASE_REDIS_URL=${{os.getenv('UPSTASE_REDIS_URL')}",
                        "UPSTASESE_REDIS_TOKEN=${{os.getenv('UPSTASESE_REDIS_TOKEN')}",
                        "VERTEX_AI_PROJECT_ID=${{os.getenv('VERTEX_AI_PROJECT_ID')}",
                        "GCP_PROJECT_ID=${{.getenv('GCP_PROJECT_ID')}",
                        "WEBHOOK_SECRET=${{os.getenv('WEBHOOK_SECRET')}",
                        "ALLOWED_ORIGINS=${{os.getenv('ALLOWED_ORIGINS', '*')}"
                    ],
                    "deploy": {
                        "replicas": 2,
                        "resources": {
                            "limits": {
                                "memory": "512M",
                                "cpu": "500m"
                            },
                            "requests": {
                                "memory": "256M",
                                "cpu": "250m"
                            }
                        }
                    },
                    "restart_policy": {
                        "condition": "on-failure",
                        "delay": "5s",
                        "max_attempts": 3
                    }
                },
                "postgres": {
                    "image": "postgres:15",
                    "environment": [
                        "POSTGRES_DB=${{os.getenv('POSTGRES_DB', 'raptorflow_prod')}",
                        "POSTGRES_USER=${{.getenv('POSTGRES_USER', 'postgres')}",
                        "POSTGRES_PASSWORD=${{os.getenv('POSTGRES_PASSWORD')}",
                        "POSTGRES_HOST_AUTH_METHOD=trust"
                    ],
                    "volumes": [
                        "postgres_data:/var/lib/postgresql/data"
                    ],
                    "restart_policy": {
                        "condition": "on-failure",
                        "delay": "5s",
                        "max_attempts": 3
                    }
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": ["6379:6379"],
                    "volumes": [
                        "redis_data:/data"
                    ],
                    "restart_policy": {
                        "condition": "on-failure",
                        "delay": "5s",
                        "max_attempts": 3
                    }
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx/nginx.conf:/etc/nginx/nginx.conf",
                        "./nginx/ssl:/etc/nginx/ssl"
                    ],
                    "restart_policy": {
                        "condition": "on-failure",
                        "delay": "5s",
                        "max_attempts": 3
                    }
                }
            },
            "volumes": {
                "postgres_data": {},
                "redis_data": {}
            }
        }

    def get_dockerignore_content(self) -> str:
        """Generate .dockerignore content."""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*$py.o
*.so

# Virtual environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Coverage
.coverage
htmlcov/
.pytest_cache/

# Documentation
docs/_build/
site/

# Environment
.env
.env.local
.env.*.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# Temporary files
*.tmp
*.bak
*.swp
*~
"""

    def get_multi_stage_dockerfile(self) -> str:
        """Generate multi-stage Dockerfile for production optimization."""
        return f"""# Multi-stage Dockerfile for RaptorFlow Backend
# Stage 1: Build stage
FROM python:{self.python_version}-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user --upgrade pip \\
    && pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:{self.python_version}-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/* \\
    && useradd --create-home --shell /bin/bash appuser

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python{self.python_version}/site-packages /usr/local/lib/python{self.python_version}/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set work directory
WORKDIR /app

# Copy application code
COPY . .

# Create non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    def get_kubernetes_deployment(self, namespace: str = "default") -> Dict[str, Any]:
        """Generate Kubernetes deployment configuration."""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self.app_name,
                "namespace": namespace,
                "labels": {
                    "app": self.app_name,
                    "version": self.version
                }
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": self.app_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": self.app_name,
                            "version": self.version
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": self.app_name,
                            "image": f"gcr.io/{os.getenv('GCP_PROJECT_ID', 'raptorflow-prod')}/{self.app_name}:{self.version}",
                            "ports": [{
                                "containerPort": 8000,
                                "protocol": "TCP"
                            }],
                            "env": [
                                {
                                    "name": "ENVIRONMENT",
                                    "value": "production"
                                },
                                {
                                    "name": "SECRET_KEY",
                                    "value": "${{os.getenv('SECRET_KEY')}"
                                },
                                {
                                    "name": "DATABASE_URL",
                                    "value": "${{os.getenv('DATABASE_URL')}"
                                },
                                {
                                    "name": "UPSTABASE_REDIS_URL",
                                    "value": "${{os.getenv('UPSTABASE_REDIS_URL')}"
                                },
                                {
                                    "name": "UPSTABASE_REDIS_TOKEN",
                                    "value": "${{os.getenv('UPSTABASE_REDIS_TOKEN')}"
                                },
                                {
                                    "name": "VERTEX_AI_PROJECT_ID",
                                    "value": "${{os.getenv('VERTEX_AI_PROJECT_ID')}"
                                },
                                {
                                    "name": "GCP_PROJECT_ID",
                                    "value": "${{.getenv('GCP_PROJECT_ID')}"
                                },
                                {
                                    "name": "WEBHOOK_SECRET",
                                    "value": "${{.getenv('WEBHOOK_SECRET')}"
                                },
                                {
                                    "name": "ALLOWED_ORIGINS",
                                    "value": "${{os.getenv('ALLOWED_ORIGINS', '*')}"
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
                        }]
                    }
                }
            }
        }

    def get_kubernetes_service(self, namespace: str = "default") -> Dict[str, Any]:
        """Generate Kubernetes service configuration."""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self.app_name,
                "namespace": namespace,
                "labels": {
                    "app": self.app_name,
                    "version": self.version
                }
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": self.app_name
                    }
                },
                "ports": [{
                    "port": 8000,
                    "targetPort": 8000,
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        }

    def get_kubernetes_configmap(self, namespace: str = "default") -> Dict[str, Any]:
        """Generate Kubernetes ConfigMap for environment variables."""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.app_name}-config",
                "namespace": namespace
            },
            "data": {
                "ENVIRONMENT": "production",
                "DEBUG": "false",
                "ALLOWED_ORIGINS": "*"
            }
        }

    def get_kubernetes_secret(self, namespace: str = "default") -> Dict[str, Any]:
        """Generate Kubernetes Secret for sensitive data."""
        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{self.app_name}-secrets",
                "namespace": namespace
            },
            "type": "Opaque",
            "data": {
                "SECRET_KEY": os.getenv("SECRET_KEY", "").encode(),
                "DATABASE_URL": os.getenv("DATABASE_URL", "").encode(),
                "UPSTABASE_REDIS_TOKEN": os.getenv("UPSTABASE_REDIS_TOKEN", "").encode(),
                "VERTEX_AI_PROJECT_ID": os.getenv("VERTEX_AI_PROJECT_ID", "").encode(),
                "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID", "").encode(),
                "WEBHOOK_SECRET": os.getenv("WEBHOOK_SECRET", "").encode()
            }
        }

    def get_health_check_dockerfile(self) -> str:
        """Generate health check Dockerfile."""
        return """# Health check service
FROM alpine:latest

RUN apk add --no-cache curl

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://backend:8000/health || exit 1
"""

    def get_nginx_config(self) -> str:
        """Generate nginx configuration."""
        return """events {
    worker_connections 1024;
}

http {{
    upstream backend {{
        server backend:8000;
    }}

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=10m rate=10r/s;

    server {{
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options "nosniff";
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

        # CORS headers
        add_header Access-Control-Allow-Origin $http_origin;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range";
        add_header Access-Control-Expose-Headers "Content-Length,Content-Range";

        # Proxy to backend
        location / {{
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        # Health check endpoint
        location /health {{
            proxy_pass http://backend:8000/health;
            access_log off;
        }}

        # Static files (if any)
        location /static/ {{
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}

        # Error pages
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {{
            root /usr/share/nginx/html;
        }}
    }}
}}"""

    def get_build_script(self) -> str:
        """Generate build script for Docker images."""
        return f"""#!/bin/bash
# RaptorFlow Backend Build Script

set -e

# Configuration
PROJECT_NAME="{self.app_name}"
VERSION="{self.version}"
GCP_PROJECT_ID="{os.getenv('GCP_PROJECT_ID', 'raptorflow-prod')}"
REGISTRY="gcr.io/$GCP_PROJECT_NAME/$PROJECT_NAME"

echo "Building $PROJECT_NAME version $VERSION..."

# Build and tag Docker image
docker build -t $REGISTRY:$VERSION .

# Push to registry
echo "Pushing to registry..."
docker push $REGISTRY:$VERSION

# Tag as latest
docker tag $REGISTRY:$VERSION $REGISTRY:latest

echo "Pushing latest tag..."
docker push $REGISTRY:latest

echo "Build completed successfully!"
"""

    def get_deploy_script(self) -> str:
        """Generate deployment script for production."""
        return f"""#!/bin/bash
# RaptorFlow Backend Deployment Script

set -e

# Configuration
PROJECT_NAME="{self.app_name}"
VERSION="{self.version}"
GCP_PROJECT_ID="{os.getenv('GCP_PROJECT_ID', 'raptorflow-prod')}"
REGION="{os.getenv('GCP_REGION', 'us-central1')}"
REGISTRY="gcr.io/$GCP_PROJECT_ID/$PROJECT_NAME"

echo "Deploying $PROJECT_NAME version $VERSION to GCP..."

# Configure gcloud if not already configured
if ! gcloud auth list | grep -q "$GCP_PROJECT_ID"; then
    echo "Configuring gcloud..."
    gcloud config set project $GCP_PROJECT_ID
    gcloud auth configure-docker $REGION
fi

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $REGISTRY:$VERSION \\
    --image $REGISTRY:$VERSION \\
    --region $REGION \\
    --platform managed \\
    --allow-unauthenticated \\
    --port 8000 \\
    --memory 512Mi \\
    --cpu 1 \\
    --min-instances 1 \\
    --max-instances 3 \\
    --set-env-vars \\
        ENVIRONMENT=production \\
        SECRET_KEY="${{os.getenv('SECRET_KEY')}" \\
        DATABASE_URL="${{os.getenv('DATABASE_URL')}" \\
        UPSTABASE_REDIS_URL="${{os.getenv('UPSTABASE_REDIS_URL')}" \\
        UPSTABASE_REDIS_TOKEN="${{os.getenv('UPSTABASE_REDIS_TOKEN')}" \\
        VERTEX_AI_PROJECT_ID="${{os.getenv('VERTEX_AI_PROJECT_ID')}" \\
        GCP_PROJECT_ID="$GCP_PROJECT_ID" \\
        WEBHOOK_SECRET="${{os.getenv('WEBHOOK_SECRET')}" \\
        ALLOWED_ORIGINS="${{os.getenv('ALLOWED_ORIGINS', '*')}" \\
    --set-cloudsql-instances raptorflow-prod:us-central1:raptorflow-db \\
    --set-cloudsql-databases raptorflow_prod \\
    --set-secrets raptorflow-prod-secrets

# Set up traffic routing
echo "Configuring traffic routing..."
gcloud run services update-traffic $PROJECT_NAME \\
    --to-revisions $VERSION \\
    --to-min-revisions 1

echo "Deployment completed successfully!"
echo "Service URL: https://$PROJECT_NAME-$RANDOM_HASH.a.run.app"
"""
