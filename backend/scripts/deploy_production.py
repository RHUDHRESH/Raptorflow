#!/usr/bin/env python3
"""
Production deployment script for Raptorflow.

Handles complete production deployment with validation.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validate_production import ProductionValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionDeployer:
    """Handles production deployment."""

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.region = os.getenv("GCP_REGION", "us-central1")

        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID must be set")

    def run_command(
        self, command: List[str], check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a shell command."""
        logger.info(f"Running: {' '.join(command)}")

        try:
            result = subprocess.run(
                command, check=check, capture_output=True, text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            raise

    def validate_environment(self) -> bool:
        """Validate deployment environment."""
        logger.info("Validating deployment environment...")

        # Check gcloud authentication
        try:
            result = self.run_command(["gcloud", "auth", "list"])
            if "No credentialed accounts" in result.stdout:
                logger.error("No gcloud authentication found")
                return False
            logger.info("✅ gcloud authentication found")
        except Exception as e:
            logger.error(f"gcloud authentication check failed: {e}")
            return False

        # Check Docker
        try:
            result = self.run_command(["docker", "--version"])
            logger.info(f"✅ Docker available: {result.stdout.strip()}")
        except Exception as e:
            logger.error(f"Docker not available: {e}")
            return False

        return True

    def build_docker_image(self, tag: str) -> bool:
        """Build Docker image."""
        logger.info(f"Building Docker image: {tag}")

        try:
            self.run_command(
                ["docker", "build", "-t", tag, "-f", "backend/Dockerfile", "backend/"]
            )
            logger.info(f"✅ Docker image built: {tag}")
            return True
        except Exception as e:
            logger.error(f"Docker build failed: {e}")
            return False

    def push_docker_image(self, tag: str) -> bool:
        """Push Docker image to Artifact Registry."""
        logger.info(f"Pushing Docker image: {tag}")

        try:
            # Configure Docker for Artifact Registry
            self.run_command(
                [
                    "gcloud",
                    "auth",
                    "configure-docker",
                    f"{self.region}-docker.pkg.dev",
                    "--quiet",
                ]
            )

            # Tag for Artifact Registry
            artifact_tag = f"{self.region}-docker.pkg.dev/{self.project_id}/raptorflow-backend/raptorflow-backend:latest"
            self.run_command(["docker", "tag", tag, artifact_tag])

            # Push to Artifact Registry
            self.run_command(["docker", "push", artifact_tag])
            logger.info(f"✅ Docker image pushed: {artifact_tag}")
            return True
        except Exception as e:
            logger.error(f"Docker push failed: {e}")
            return False

    def deploy_cloud_run(self, image_tag: str) -> bool:
        """Deploy to Cloud Run."""
        logger.info(f"Deploying to Cloud Run: {image_tag}")

        try:
            # Get environment variables
            env_vars = [
                f"UPSTASH_REDIS_URL={os.getenv('UPSTASH_REDIS_URL')}",
                f"UPSTASH_REDIS_TOKEN={os.getenv('UPSTASH_REDIS_TOKEN')}",
                f"SUPABASE_URL={os.getenv('SUPABASE_URL')}",
                f"SUPABASE_SERVICE_ROLE_KEY={os.getenv('SUPABASE_SERVICE_ROLE_KEY')}",
                f"GCP_PROJECT_ID={self.project_id}",
                f"GCP_REGION={self.region}",
                "ENVIRONMENT=production",
            ]

            # Deploy to Cloud Run
            cmd = [
                "gcloud",
                "run",
                "deploy",
                "raptorflow-backend",
                "--image",
                image_tag,
                "--region",
                self.region,
                "--platform",
                "managed",
                "--allow-unauthenticated",
                "--memory",
                "2Gi",
                "--cpu",
                "1",
                "--max-instances",
                "10",
                "--timeout",
                "300",
                "--quiet",
            ]

            for env_var in env_vars:
                cmd.extend(["--set-env-vars", env_var])

            self.run_command(cmd)
            logger.info("✅ Cloud Run deployment successful")
            return True
        except Exception as e:
            logger.error(f"Cloud Run deployment failed: {e}")
            return False

    def get_service_url(self) -> str:
        """Get deployed service URL."""
        try:
            result = self.run_command(
                [
                    "gcloud",
                    "run",
                    "services",
                    "describe",
                    "raptorflow-backend",
                    "--region",
                    self.region,
                    "--format",
                    "value(status.url)",
                ]
            )
            url = result.stdout.strip()
            logger.info(f"Service URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to get service URL: {e}")
            return ""

    def run_post_deployment_tests(self, service_url: str) -> bool:
        """Run post-deployment tests."""
        logger.info("Running post-deployment tests...")

        try:
            import httpx

            # Test health endpoint
            health_url = f"{service_url}/api/v1/health"
            response = httpx.get(health_url, timeout=30)

            if response.status_code != 200:
                logger.error(f"Health check failed: {response.status_code}")
                return False

            health_data = response.json()
            if health_data.get("status") != "healthy":
                logger.error(f"Service not healthy: {health_data}")
                return False

            logger.info("✅ Post-deployment tests passed")
            return True
        except Exception as e:
            logger.error(f"Post-deployment tests failed: {e}")
            return False

    async def deploy(self) -> Dict[str, Any]:
        """Execute full production deployment."""
        logger.info("Starting production deployment...")

        deployment_results = {
            "validation": False,
            "environment": False,
            "build": False,
            "push": False,
            "deploy": False,
            "tests": False,
            "service_url": "",
        }

        # Step 1: Validate production configuration
        logger.info("Step 1: Validating production configuration...")
        validator = ProductionValidator()
        validation_results = await validator.run_all_validations()

        if validation_results["summary"]["failed"] > 0:
            logger.error("Production validation failed - aborting deployment")
            return deployment_results

        deployment_results["validation"] = True
        logger.info("✅ Production validation passed")

        # Step 2: Validate deployment environment
        logger.info("Step 2: Validating deployment environment...")
        if not self.validate_environment():
            logger.error("Environment validation failed - aborting deployment")
            return deployment_results

        deployment_results["environment"] = True
        logger.info("✅ Environment validation passed")

        # Step 3: Build Docker image
        logger.info("Step 3: Building Docker image...")
        image_tag = f"gcr.io/{self.project_id}/raptorflow-backend:latest"
        if not self.build_docker_image(image_tag):
            logger.error("Docker build failed - aborting deployment")
            return deployment_results

        deployment_results["build"] = True
        logger.info("✅ Docker build successful")

        # Step 4: Push Docker image
        logger.info("Step 4: Pushing Docker image...")
        artifact_tag = f"{self.region}-docker.pkg.dev/{self.project_id}/raptorflow-backend/raptorflow-backend:latest"
        if not self.push_docker_image(image_tag):
            logger.error("Docker push failed - aborting deployment")
            return deployment_results

        deployment_results["push"] = True
        logger.info("✅ Docker push successful")

        # Step 5: Deploy to Cloud Run
        logger.info("Step 5: Deploying to Cloud Run...")
        if not self.deploy_cloud_run(artifact_tag):
            logger.error("Cloud Run deployment failed")
            return deployment_results

        deployment_results["deploy"] = True
        logger.info("✅ Cloud Run deployment successful")

        # Step 6: Get service URL
        service_url = self.get_service_url()
        deployment_results["service_url"] = service_url

        # Step 7: Run post-deployment tests
        logger.info("Step 6: Running post-deployment tests...")
        if not self.run_post_deployment_tests(service_url):
            logger.error("Post-deployment tests failed")
            return deployment_results

        deployment_results["tests"] = True
        logger.info("✅ Post-deployment tests passed")

        return deployment_results

    def print_deployment_summary(self, results: Dict[str, Any]):
        """Print deployment summary."""
        print("\n" + "=" * 60)
        print("PRODUCTION DEPLOYMENT SUMMARY")
        print("=" * 60)

        steps = [
            ("Validation", results["validation"]),
            ("Environment", results["environment"]),
            ("Docker Build", results["build"]),
            ("Docker Push", results["push"]),
            ("Cloud Run Deploy", results["deploy"]),
            ("Post-Deploy Tests", results["tests"]),
        ]

        print("\nDeployment Steps:")
        all_passed = True
        for step_name, passed in steps:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {step_name:20} {status}")
            if not passed:
                all_passed = False

        if results["service_url"]:
            print(f"\n🌐 Service URL: {results['service_url']}")

        print("\n" + "=" * 60)

        if all_passed:
            print("🎉 PRODUCTION DEPLOYMENT SUCCESSFUL")
            print("\nNext steps:")
            print("1. Test the service at the URL above")
            print("2. Update DNS if needed")
            print("3. Configure monitoring alerts")
            print("4. Run smoke tests")
        else:
            print("🚨 PRODUCTION DEPLOYMENT FAILED")
            print("Check the logs above for details")
            sys.exit(1)


async def main():
    """Main deployment function."""
    try:
        deployer = ProductionDeployer()
        results = await deployer.deploy()
        deployer.print_deployment_summary(results)
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
