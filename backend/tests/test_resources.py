"""
Comprehensive test suite for resource management system.
Tests resource cleanup, leak detection, and quota enforcement.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from .core.resources import (
    ResourceManager,
    ResourceType,
    ResourceStatus,
    ResourceInfo,
    ResourceQuota,
    ResourceCleanupStrategy,
    MemoryCleanupStrategy,
    FileHandleCleanupStrategy,
    AsyncTaskCleanupStrategy,
    get_resource_manager,
)


class TestResourceManager:
    """Test cases for ResourceManager."""

    @pytest.fixture
    async def resource_manager(self):
        """Create a resource manager for testing."""
        manager = ResourceManager(leak_check_interval=1, cleanup_interval=2)
        await manager.start()
        yield manager
        await manager.stop()

    @pytest.mark.asyncio
    async def test_register_resource(self, resource_manager):
        """Test resource registration."""
        resource_id = "test_resource_1"

        # Register a resource
        success = resource_manager.register_resource(
            resource_id=resource_id,
            resource_type=ResourceType.MEMORY,
            owner="test_user",
            workspace_id="test_workspace",
            size_bytes=1024,
        )

        assert success is True
        assert resource_id in resource_manager.resources
        assert (
            resource_manager.resources[resource_id].resource_type == ResourceType.MEMORY
        )
        assert resource_manager.resources[resource_id].owner == "test_user"
        assert resource_manager.resources[resource_id].workspace_id == "test_workspace"

    @pytest.mark.asyncio
    async def test_unregister_resource(self, resource_manager):
        """Test resource unregistration."""
        resource_id = "test_resource_2"

        # Register and then unregister
        resource_manager.register_resource(
            resource_id=resource_id,
            resource_type=ResourceType.FILE_HANDLE,
            owner="test_user",
        )

        success = resource_manager.unregister_resource(resource_id)

        assert success is True
        assert resource_id not in resource_manager.resources
        assert (
            resource_manager.resources[resource_id].status == ResourceStatus.CLEANED_UP
        )

    @pytest.mark.asyncio
    async def test_access_resource(self, resource_manager):
        """Test resource access tracking."""
        resource_id = "test_resource_3"

        # Register resource
        resource_manager.register_resource(
            resource_id=resource_id,
            resource_type=ResourceType.ASYNC_TASK,
            owner="test_user",
        )

        # Access resource multiple times
        resource_manager.access_resource(resource_id)
        resource_manager.access_resource(resource_id)

        resource_info = resource_manager.resources[resource_id]
        assert resource_info.access_count == 2
        assert resource_info.status == ResourceStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_quota_enforcement(self, resource_manager):
        """Test quota enforcement."""
        # Set a quota
        quota = ResourceQuota(
            resource_type=ResourceType.MEMORY,
            max_count=2,
            workspace_id="test_workspace",
        )
        resource_manager.set_quota(quota)

        # Register resources within quota
        assert (
            resource_manager.register_resource(
                "quota_test_1", ResourceType.MEMORY, workspace_id="test_workspace"
            )
            is True
        )

        assert (
            resource_manager.register_resource(
                "quota_test_2", ResourceType.MEMORY, workspace_id="test_workspace"
            )
            is True
        )

        # Try to exceed quota
        assert (
            resource_manager.register_resource(
                "quota_test_3", ResourceType.MEMORY, workspace_id="test_workspace"
            )
            is False
        )

    @pytest.mark.asyncio
    async def test_leak_detection(self, resource_manager):
        """Test resource leak detection."""
        resource_id = "leak_test_resource"

        # Register an old resource
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now() - timedelta(hours=2)

            resource_manager.register_resource(
                resource_id=resource_id,
                resource_type=ResourceType.MEMORY,
                owner="test_user",
            )

        # Restore current time and trigger leak detection
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()

            await resource_manager._detect_leaks()

        # Check if leak was detected
        leaks = resource_manager.get_leaked_resources()
        assert len(leaks) > 0
        leak = next((l for l in leaks if l.resource_id == resource_id), None)
        assert leak is not None
        assert leak.severity in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_cleanup_by_type(self, resource_manager):
        """Test cleanup by resource type."""
        # Register multiple resources of different types
        resource_manager.register_resource(
            "cleanup_test_1", ResourceType.MEMORY, owner="test_user"
        )
        resource_manager.register_resource(
            "cleanup_test_2", ResourceType.FILE_HANDLE, owner="test_user"
        )
        resource_manager.register_resource(
            "cleanup_test_3", ResourceType.MEMORY, owner="test_user"
        )

        # Clean up memory resources
        cleanup_count = await resource_manager.cleanup_resources_by_type(
            ResourceType.MEMORY
        )

        assert cleanup_count == 2
        assert "cleanup_test_1" not in resource_manager.resources
        assert "cleanup_test_3" not in resource_manager.resources
        # File handle should still exist
        assert "cleanup_test_2" in resource_manager.resources

    @pytest.mark.asyncio
    async def test_cleanup_by_owner(self, resource_manager):
        """Test cleanup by resource owner."""
        # Register resources for different owners
        resource_manager.register_resource(
            "owner_test_1", ResourceType.MEMORY, owner="user1"
        )
        resource_manager.register_resource(
            "owner_test_2", ResourceType.FILE_HANDLE, owner="user1"
        )
        resource_manager.register_resource(
            "owner_test_3", ResourceType.MEMORY, owner="user2"
        )

        # Clean up resources for user1
        cleanup_count = await resource_manager.cleanup_resources_by_owner("user1")

        assert cleanup_count == 2
        assert "owner_test_1" not in resource_manager.resources
        assert "owner_test_2" not in resource_manager.resources
        # user2's resource should still exist
        assert "owner_test_3" in resource_manager.resources

    @pytest.mark.asyncio
    async def test_memory_cleanup_strategy(self):
        """Test memory cleanup strategy."""
        strategy = MemoryCleanupStrategy()

        # Create a mock resource with memory reference
        mock_memory = {"data": "test"}
        resource_info = ResourceInfo(
            resource_id="memory_test",
            resource_type=ResourceType.MEMORY,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            status=ResourceStatus.ACTIVE,
            metadata={"memory_ref": Mock(return_value=None)},  # Mock weakref
        )

        # Test cleanup
        success = await strategy.cleanup(resource_info)
        assert success is True

    @pytest.mark.asyncio
    async def test_file_handle_cleanup_strategy(self):
        """Test file handle cleanup strategy."""
        strategy = FileHandleCleanupStrategy()

        # Create a mock file handle
        mock_file = Mock()
        mock_file.close = Mock()

        resource_info = ResourceInfo(
            resource_id="file_test",
            resource_type=ResourceType.FILE_HANDLE,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            status=ResourceStatus.ACTIVE,
            metadata={"file_handle": mock_file},
        )

        # Test cleanup
        success = await strategy.cleanup(resource_info)
        assert success is True
        mock_file.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_task_cleanup_strategy(self):
        """Test async task cleanup strategy."""
        strategy = AsyncTaskCleanupStrategy()

        # Create a mock async task
        mock_task = Mock()
        mock_task.done = Mock(return_value=False)
        mock_task.cancel = Mock()

        resource_info = ResourceInfo(
            resource_id="task_test",
            resource_type=ResourceType.ASYNC_TASK,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            status=ResourceStatus.ACTIVE,
            metadata={"task": mock_task},
        )

        # Test cleanup
        success = await strategy.cleanup(resource_info)
        assert success is True
        mock_task.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_resource_summary(self, resource_manager):
        """Test resource summary generation."""
        # Register various resources
        resource_manager.register_resource(
            "summary_test_1", ResourceType.MEMORY, owner="user1"
        )
        resource_manager.register_resource(
            "summary_test_2", ResourceType.FILE_HANDLE, owner="user1"
        )
        resource_manager.register_resource(
            "summary_test_3",
            ResourceType.MEMORY,
            owner="user2",
            status=ResourceStatus.LEAKED,
        )

        # Get summary
        summary = resource_manager.get_resource_summary()

        assert summary["total_resources"] == 3
        assert summary["resources_by_type"][ResourceType.MEMORY.value] == 2
        assert summary["resources_by_type"][ResourceType.FILE_HANDLE.value] == 1
        assert summary["resources_by_status"][ResourceStatus.ACTIVE.value] == 2
        assert summary["resources_by_status"][ResourceStatus.LEAKED.value] == 1

    @pytest.mark.asyncio
    async def test_concurrent_cleanup(self, resource_manager):
        """Test concurrent cleanup operations."""
        # Register many resources
        for i in range(10):
            resource_manager.register_resource(
                f"concurrent_test_{i}", ResourceType.MEMORY, owner="test_user"
            )

        # Run cleanup concurrently
        start_time = time.time()
        cleanup_count = await resource_manager.cleanup_all_resources()
        end_time = time.time()

        # Should clean up all resources
        assert cleanup_count == 10
        assert len(resource_manager.resources) == 0

        # Should complete in reasonable time (parallel processing)
        assert (end_time - start_time) < 5.0  # 5 seconds max

    @pytest.mark.asyncio
    async def test_custom_cleanup_strategy(self, resource_manager):
        """Test custom cleanup strategy."""

        class CustomStrategy(ResourceCleanupStrategy):
            async def cleanup(self, resource_info):
                return True

            def can_handle(self, resource_type):
                return resource_type == ResourceType.CACHE

        # Add custom strategy
        resource_manager.add_cleanup_strategy(CustomStrategy())

        # Test with cache resource
        resource_info = ResourceInfo(
            resource_id="custom_test",
            resource_type=ResourceType.CACHE,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            status=ResourceStatus.ACTIVE,
        )

        success = await resource_manager.cleanup_resource("custom_test")
        assert success is True


class TestResourceQuotas:
    """Test cases for resource quotas."""

    @pytest.mark.asyncio
    async def test_quota_creation(self):
        """Test quota creation and validation."""
        quota = ResourceQuota(
            resource_type=ResourceType.MEMORY,
            max_count=100,
            max_size_bytes=1024 * 1024 * 1024,  # 1GB
            max_age_seconds=3600,  # 1 hour
            workspace_id="test_workspace",
        )

        assert quota.resource_type == ResourceType.MEMORY
        assert quota.max_count == 100
        assert quota.max_size_bytes == 1024 * 1024 * 1024
        assert quota.max_age_seconds == 3600
        assert quota.workspace_id == "test_workspace"

    @pytest.mark.asyncio
    async def test_quota_serialization(self):
        """Test quota serialization to dictionary."""
        quota = ResourceQuota(
            resource_type=ResourceType.DATABASE_CONNECTION,
            max_count=50,
            workspace_id="test_workspace",
        )

        quota_dict = quota.to_dict()

        assert quota_dict["resource_type"] == "database_connection"
        assert quota_dict["max_count"] == 50
        assert quota_dict["workspace_id"] == "test_workspace"
        assert "created_at" in quota_dict  # Should have timestamp


class TestResourceLeaks:
    """Test cases for resource leak detection."""

    @pytest.mark.asyncio
    async def test_leak_creation(self):
        """Test leak creation and properties."""
        from core.resources import ResourceLeak

        resource_info = ResourceInfo(
            resource_id="leak_test",
            resource_type=ResourceType.MEMORY,
            created_at=datetime.now() - timedelta(hours=2),
            last_accessed=datetime.now() - timedelta(hours=2),
            status=ResourceStatus.LEAKED,
        )

        leak = ResourceLeak(
            resource_id="leak_test",
            resource_type=ResourceType.MEMORY,
            leak_detected_at=datetime.now(),
            leak_duration_seconds=7200,  # 2 hours
            severity="high",
            description="Test leak",
            suggested_action="Clean up resource",
            resource_info=resource_info,
        )

        assert leak.resource_id == "leak_test"
        assert leak.resource_type == ResourceType.MEMORY
        assert leak.leak_duration_seconds == 7200
        assert leak.severity == "high"
        assert leak.description == "Test leak"
        assert leak.suggested_action == "Clean up resource"

    @pytest.mark.asyncio
    async def test_leak_severity_calculation(self, resource_manager):
        """Test leak severity calculation."""
        # Test different age ratios
        test_cases = [
            (1800, 3600, "low"),  # 0.5 ratio
            (7200, 3600, "high"),  # 2.0 ratio
            (18000, 3600, "critical"),  # 5.0 ratio
        ]

        for age_seconds, threshold, expected_severity in test_cases:
            severity = resource_manager._calculate_leak_severity(age_seconds, threshold)
            assert severity == expected_severity


class TestGlobalResourceManager:
    """Test cases for global resource manager."""

    @pytest.mark.asyncio
    async def test_global_manager_singleton(self):
        """Test that global resource manager is a singleton."""
        manager1 = get_resource_manager()
        manager2 = get_resource_manager()

        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_global_manager_lifecycle(self):
        """Test global manager start/stop lifecycle."""
        manager = get_resource_manager()

        # Start should be idempotent
        await manager.start()
        await manager.start()
        assert manager._running is True

        # Stop should work
        await manager.stop()
        assert manager._running is False


# Integration Tests


class TestResourceIntegration:
    """Integration tests for resource management system."""

    @pytest.mark.asyncio
    async def test_end_to_end_resource_lifecycle(self):
        """Test complete resource lifecycle."""
        manager = ResourceManager()
        await manager.start()

        try:
            # 1. Register resource
            resource_id = "lifecycle_test"
            success = manager.register_resource(
                resource_id=resource_id,
                resource_type=ResourceType.MEMORY,
                owner="integration_user",
                workspace_id="integration_workspace",
            )
            assert success is True

            # 2. Access resource
            manager.access_resource(resource_id)
            resource_info = manager.resources[resource_id]
            assert resource_info.access_count == 1

            # 3. Wait for leak detection (simulate old resource)
            resource_info.created_at = datetime.now() - timedelta(hours=2)
            await manager._detect_leaks()

            # 4. Clean up resource
            cleanup_success = await manager.cleanup_resource(resource_id)
            assert cleanup_success is True

            # 5. Verify cleanup
            assert resource_id not in manager.resources

        finally:
            await manager.stop()

    @pytest.mark.asyncio
    async def test_quota_enforcement_integration(self):
        """Test quota enforcement in realistic scenario."""
        manager = ResourceManager()
        await manager.start()

        try:
            # Set quota
            quota = ResourceQuota(
                resource_type=ResourceType.ASYNC_TASK,
                max_count=3,
                workspace_id="quota_test_workspace",
            )
            manager.set_quota(quota)

            # Register resources up to quota
            for i in range(3):
                success = manager.register_resource(
                    f"quota_resource_{i}",
                    ResourceType.ASYNC_TASK,
                    workspace_id="quota_test_workspace",
                )
                assert success is True

            # Try to exceed quota
            excess_success = manager.register_resource(
                "quota_resource_excess",
                ResourceType.ASYNC_TASK,
                workspace_id="quota_test_workspace",
            )
            assert excess_success is False

            # Check quota violations
            assert len(manager.quota_violations) > 0
            violation = manager.quota_violations[-1]
            assert violation.workspace_id == "quota_test_workspace"
            assert violation.violation_type == "quota_exceeded"

        finally:
            await manager.stop()


# Performance Tests


class TestResourcePerformance:
    """Performance tests for resource management."""

    @pytest.mark.asyncio
    async def test_high_volume_resource_tracking(self):
        """Test performance with high volume of resources."""
        manager = ResourceManager()
        await manager.start()

        try:
            # Register many resources
            start_time = time.time()
            resource_count = 1000

            for i in range(resource_count):
                manager.register_resource(
                    f"perf_test_{i}", ResourceType.MEMORY, owner="perf_user"
                )

            registration_time = time.time() - start_time

            # Should complete quickly
            assert registration_time < 5.0  # 5 seconds for 1000 resources
            assert len(manager.resources) == resource_count

            # Test cleanup performance
            cleanup_start = time.time()
            cleanup_count = await manager.cleanup_all_resources()
            cleanup_time = time.time() - cleanup_start

            # Should also complete quickly due to parallel processing
            assert cleanup_time < 10.0  # 10 seconds for cleanup
            assert cleanup_count == resource_count

        finally:
            await manager.stop()

    @pytest.mark.asyncio
    async def test_memory_usage_tracking(self):
        """Test memory usage tracking doesn't leak."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        manager = ResourceManager()
        await manager.start()

        try:
            # Create and cleanup many resources
            for cycle in range(5):
                # Register resources
                for i in range(100):
                    manager.register_resource(
                        f"memory_test_{cycle}_{i}",
                        ResourceType.MEMORY,
                        owner="memory_test_user",
                    )

                # Clean up
                await manager.cleanup_all_resources()

                # Check memory hasn't grown significantly
                current_memory = process.memory_info().rss
                memory_growth = current_memory - initial_memory

                # Allow some growth but should be reasonable
                assert memory_growth < 50 * 1024 * 1024  # 50MB max growth

        finally:
            await manager.stop()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
