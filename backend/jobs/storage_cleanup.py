"""
Storage cleanup job for GCS
Automatically cleans up expired files and manages storage costs
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any

from infrastructure.storage import get_cloud_storage
from .services.storage import storage_service

logger = logging.getLogger(__name__)


class StorageCleanupJob:
    """Automated storage cleanup and maintenance"""

    def __init__(self):
        self.storage = get_cloud_storage()
        self.logger = logging.getLogger("storage_cleanup")

    async def run_cleanup(self) -> Dict[str, Any]:
        """Run comprehensive storage cleanup"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "cleanup_results": {},
            "cost_analysis": {},
            "recommendations": [],
        }

        try:
            # 1. Clean up expired files
            expired_count = await self.cleanup_expired_files()
            results["cleanup_results"]["expired_files"] = expired_count

            # 2. Clean up old temp files
            temp_count = await self.cleanup_temp_files()
            results["cleanup_results"]["temp_files"] = temp_count

            # 3. Analyze storage costs
            cost_analysis = await self.analyze_storage_costs()
            results["cost_analysis"] = cost_analysis

            # 4. Generate recommendations
            recommendations = self.generate_recommendations(cost_analysis)
            results["recommendations"] = recommendations

            self.logger.info(f"Storage cleanup completed: {results}")
            return results

        except Exception as e:
            self.logger.error(f"Storage cleanup failed: {e}")
            results["error"] = str(e)
            return results

    async def cleanup_expired_files(self) -> int:
        """Clean up files past their retention period"""
        try:
            cleaned_count = await self.storage.cleanup_expired_files()
            self.logger.info(f"Cleaned up {cleaned_count} expired files")
            return cleaned_count
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired files: {e}")
            return 0

    async def cleanup_temp_files(self) -> int:
        """Clean up temporary files older than 24 hours"""
        try:
            from infrastructure.storage import FileCategory

            # Get all temp files
            temp_files = await self.storage.list_files(
                workspace_id="*",  # All workspaces
                category=FileCategory.TEMP,
                limit=1000,
            )

            cleaned_count = 0
            cutoff_time = datetime.now() - timedelta(hours=24)

            for file in temp_files:
                if file.created_at < cutoff_time:
                    success = await self.storage.delete_file(
                        file_id=file.file_id, workspace_id=file.workspace_id
                    )
                    if success:
                        cleaned_count += 1

            self.logger.info(f"Cleaned up {cleaned_count} temp files")
            return cleaned_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup temp files: {e}")
            return 0

    async def analyze_storage_costs(self) -> Dict[str, Any]:
        """Analyze storage costs by category and age"""
        try:
            # Get bucket info
            bucket_info = self.storage.get_bucket_info()

            # Analyze by storage class
            storage_costs = {
                "STANDARD": {"cost_per_gb": 0.020, "size_gb": 0},
                "NEARLINE": {"cost_per_gb": 0.010, "size_gb": 0},
                "COLDLINE": {"cost_per_gb": 0.004, "size_gb": 0},
                "ARCHIVE": {"cost_per_gb": 0.001, "size_gb": 0},
            }

            # Calculate total monthly cost
            total_monthly_cost = 0

            # This would require actual bucket usage analysis
            # For now, return placeholder data
            return {
                "total_size_gb": 0,
                "total_monthly_cost": total_monthly_cost,
                "storage_class_costs": storage_costs,
                "bucket_info": bucket_info,
            }

        except Exception as e:
            self.logger.error(f"Failed to analyze storage costs: {e}")
            return {}

    def generate_recommendations(self, cost_analysis: Dict[str, Any]) -> list:
        """Generate cost optimization recommendations"""
        recommendations = []

        try:
            total_cost = cost_analysis.get("total_monthly_cost", 0)

            if total_cost > 100:  # $100/month threshold
                recommendations.append(
                    {
                        "type": "cost_optimization",
                        "priority": "high",
                        "message": f"Monthly storage cost ${total_cost:.2f} exceeds threshold. Consider lifecycle policies.",
                        "action": "Implement automatic storage class transitions",
                    }
                )

            # Check for old files that could be archived
            recommendations.append(
                {
                    "type": "lifecycle_optimization",
                    "priority": "medium",
                    "message": "Consider implementing stricter lifecycle rules for old files",
                    "action": "Set files older than 90 days to COLDLINE storage class",
                }
            )

            # Check for large files
            recommendations.append(
                {
                    "type": "file_optimization",
                    "priority": "low",
                    "message": "Review large files for compression opportunities",
                    "action": "Implement file compression for uploads > 10MB",
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")

        return recommendations


# Scheduled job runner
async def run_storage_cleanup():
    """Run storage cleanup job (can be called by scheduler)"""
    job = StorageCleanupJob()
    results = await job.run_cleanup()

    # Log results
    logger.info(f"Storage cleanup job completed: {results}")

    # Send alerts if needed
    if results.get("cost_analysis", {}).get("total_monthly_cost", 0) > 100:
        logger.warning("Storage costs exceed threshold - review needed")

    return results


if __name__ == "__main__":
    import asyncio

    # Run cleanup job
    asyncio.run(run_storage_cleanup())
