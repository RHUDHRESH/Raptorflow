import asyncio
import logging
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import pytest
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import random
import uuid

# Import the rate limiting components
from .advanced_rate_limiter import AdvancedRateLimiter, get_advanced_rate_limiter
from .distributed_rate_limiting import DistributedRateLimiter, get_distributed_rate_limiter
from .ml_rate_optimizer import MLRateOptimizer, get_ml_rate_optimizer
from .usage_analytics import UsageAnalyticsManager, get_usage_analytics_manager
from .rate_limit_alerting import RateLimitAlertingManager, get_rate_limit_alerting_manager
from .usage_patterns_analyzer import UsagePatternsAnalyzer, get_usage_patterns_analyzer
from .dynamic_rate_limiter import DynamicRateLimiter, get_dynamic_rate_limiter
from .usage_forecasting import UsageForecastingManager, get_usage_forecasting_manager
from .rate_limit_bypass import RateLimitBypassManager, get_rate_limit_bypass_manager
from .usage_reporting import UsageReportingManager, get_usage_reporting_manager
from .rate_limit_dashboard import RateLimitDashboard, get_rate_limit_dashboard
from .usage_optimizer import UsageOptimizer, get_usage_optimizer

logger = logging.getLogger(__name__)

class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    LOAD = "load"
    STRESS = "stress"
    PERFORMANCE = "performance"
    REGRESSION = "regression"

class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TestResult:
    test_name: str
    test_type: TestType
    status: TestStatus
    execution_time: float
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None

@dataclass
class LoadTestConfig:
    concurrent_users: int = 100
    requests_per_second: int = 1000
    test_duration: int = 60  # seconds
    ramp_up_time: int = 10  # seconds
    endpoints: List[str] = field(default_factory=lambda: ["/api/v1/test"])
    user_tiers: List[str] = field(default_factory=lambda: ["free", "basic", "pro", "enterprise"])

@dataclass
class PerformanceMetrics:
    avg_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    throughput: float
    cpu_usage: float
    memory_usage: float

class RateLimitingTestFramework:
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.load_test_config = LoadTestConfig()
        self.is_running = False
        self.test_sessions: Dict[str, Any] = {}
        
        # Initialize all components for testing
        self.components = {
            "advanced_rate_limiter": get_advanced_rate_limiter(),
            "distributed_rate_limiter": get_distributed_rate_limiter(),
            "ml_rate_optimizer": get_ml_rate_optimizer(),
            "usage_analytics": get_usage_analytics_manager(),
            "rate_limit_alerting": get_rate_limit_alerting_manager(),
            "usage_patterns_analyzer": get_usage_patterns_analyzer(),
            "dynamic_rate_limiter": get_dynamic_rate_limiter(),
            "usage_forecasting": get_usage_forecasting_manager(),
            "rate_limit_bypass": get_rate_limit_bypass_manager(),
            "usage_reporting": get_usage_reporting_manager(),
            "rate_limit_dashboard": get_rate_limit_dashboard(),
            "usage_optimizer": get_usage_optimizer()
        }
        
        logger.info("RateLimitingTestFramework initialized")

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        logger.info("Starting comprehensive test suite")
        
        test_summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "execution_time": 0,
            "test_results": []
        }
        
        start_time = time.time()
        
        # Start all components
        await self._start_components()
        
        try:
            # Run unit tests
            await self._run_unit_tests()
            
            # Run integration tests
            await self._run_integration_tests()
            
            # Run performance tests
            await self._run_performance_tests()
            
            # Run load tests
            await self._run_load_tests()
            
            # Run stress tests
            await self._run_stress_tests()
            
        finally:
            # Stop all components
            await self._stop_components()
        
        # Calculate summary
        test_summary["execution_time"] = time.time() - start_time
        test_summary["total_tests"] = len(self.test_results)
        test_summary["passed_tests"] = len([r for r in self.test_results if r.status == TestStatus.PASSED])
        test_summary["failed_tests"] = len([r for r in self.test_results if r.status == TestStatus.FAILED])
        test_summary["skipped_tests"] = len([r for r in self.test_results if r.status == TestStatus.SKIPPED])
        test_summary["test_results"] = [
            {
                "name": r.test_name,
                "type": r.test_type.value,
                "status": r.status.value,
                "execution_time": r.execution_time,
                "error": r.error_message
            }
            for r in self.test_results
        ]
        
        logger.info(f"Test suite completed: {test_summary['passed_tests']}/{test_summary['total_tests']} passed")
        return test_summary

    async def run_load_test(self, config: LoadTestConfig = None) -> Dict[str, Any]:
        """Run load test with specified configuration"""
        if config:
            self.load_test_config = config
        
        logger.info(f"Starting load test: {self.load_test_config.concurrent_users} users, "
                   f"{self.load_test_config.requests_per_second} RPS")
        
        results = {
            "test_config": {
                "concurrent_users": self.load_test_config.concurrent_users,
                "requests_per_second": self.load_test_config.requests_per_second,
                "test_duration": self.load_test_config.test_duration,
                "ramp_up_time": self.load_test_config.ramp_up_time
            },
            "performance_metrics": None,
            "errors": [],
            "requests_completed": 0,
            "requests_failed": 0
        }
        
        try:
            # Start all components
            await self._start_components()
            
            # Execute load test
            metrics = await self._execute_load_test()
            results["performance_metrics"] = metrics
            
        except Exception as e:
            logger.error(f"Load test failed: {e}")
            results["errors"].append(str(e))
        
        finally:
            # Stop all components
            await self._stop_components()
        
        return results

    async def _run_unit_tests(self):
        """Run unit tests for individual components"""
        logger.info("Running unit tests")
        
        unit_tests = [
            self._test_advanced_rate_limiter_unit,
            self._test_distributed_rate_limiter_unit,
            self._test_ml_rate_optimizer_unit,
            self._test_usage_analytics_unit,
            self._test_rate_limit_alerting_unit,
            self._test_usage_patterns_analyzer_unit,
            self._test_dynamic_rate_limiter_unit,
            self._test_usage_forecasting_unit,
            self._test_rate_limit_bypass_unit,
            self._test_usage_reporting_unit,
            self._test_rate_limit_dashboard_unit,
            self._test_usage_optimizer_unit
        ]
        
        for test_func in unit_tests:
            await self._run_single_test(test_func, TestType.UNIT)

    async def _run_integration_tests(self):
        """Run integration tests between components"""
        logger.info("Running integration tests")
        
        integration_tests = [
            self._test_rate_limiter_integration,
            self._test_analytics_integration,
            self._test_alerting_integration,
            self._test_forecasting_integration,
            self._test_dashboard_integration
        ]
        
        for test_func in integration_tests:
            await self._run_single_test(test_func, TestType.INTEGRATION)

    async def _run_performance_tests(self):
        """Run performance tests"""
        logger.info("Running performance tests")
        
        performance_tests = [
            self._test_rate_limiter_performance,
            self._test_analytics_performance,
            self._test_ml_optimizer_performance
        ]
        
        for test_func in performance_tests:
            await self._run_single_test(test_func, TestType.PERFORMANCE)

    async def _run_load_tests(self):
        """Run load tests"""
        logger.info("Running load tests")
        
        await self._run_single_test(self._test_basic_load, TestType.LOAD)

    async def _run_stress_tests(self):
        """Run stress tests"""
        logger.info("Running stress tests")
        
        stress_tests = [
            self._test_high_concurrency_stress,
            self._test_memory_stress,
            self._test_rate_limit_stress
        ]
        
        for test_func in stress_tests:
            await self._run_single_test(test_func, TestType.STRESS)

    async def _run_single_test(self, test_func, test_type: TestType):
        """Run a single test function"""
        test_name = test_func.__name__
        start_time = time.time()
        
        result = TestResult(
            test_name=test_name,
            test_type=test_type,
            status=TestStatus.RUNNING,
            execution_time=0,
            details={}
        )
        
        try:
            logger.info(f"Running test: {test_name}")
            await test_func()
            result.status = TestStatus.PASSED
            result.details["message"] = "Test passed successfully"
            
        except Exception as e:
            logger.error(f"Test {test_name} failed: {e}")
            result.status = TestStatus.FAILED
            result.error_message = str(e)
            result.details["error"] = str(e)
        
        result.execution_time = time.time() - start_time
        self.test_results.append(result)

    async def _test_advanced_rate_limiter_unit(self):
        """Unit test for AdvancedRateLimiter"""
        rate_limiter = self.components["advanced_rate_limiter"]
        
        # Test basic rate limiting
        user_id = "test_user_1"
        endpoint = "/api/v1/test"
        
        # Should allow requests within limit
        for i in range(5):
            result = await rate_limiter.check_rate_limit(user_id, endpoint)
            assert result.allowed, f"Request {i} should be allowed"
        
        # Test rate limit exceeded
        result = await rate_limiter.check_rate_limit(user_id, endpoint)
        assert not result.allowed, "Request should be rate limited"

    async def _test_distributed_rate_limiter_unit(self):
        """Unit test for DistributedRateLimiter"""
        rate_limiter = self.components["distributed_rate_limiter"]
        
        # Test distributed rate limiting
        user_id = "test_user_2"
        endpoint = "/api/v1/test"
        
        # Should allow requests within limit
        for i in range(10):
            result = await rate_limiter.check_rate_limit(user_id, endpoint)
            assert result.allowed, f"Request {i} should be allowed"
        
        # Test rate limit exceeded
        result = await rate_limiter.check_rate_limit(user_id, endpoint)
        assert not result.allowed, "Request should be rate limited"

    async def _test_ml_rate_optimizer_unit(self):
        """Unit test for MLRateOptimizer"""
        optimizer = self.components["ml_rate_optimizer"]
        
        # Test optimization
        user_id = "test_user_3"
        optimization = await optimizer.optimize_rate_limits(user_id)
        
        assert optimization is not None, "Optimization should return a result"
        assert hasattr(optimization, 'recommended_limits'), "Should have recommended limits"

    async def _test_usage_analytics_unit(self):
        """Unit test for UsageAnalyticsManager"""
        analytics = self.components["usage_analytics"]
        
        # Test analytics recording
        user_id = "test_user_4"
        await analytics.record_request(user_id, "/api/v1/test", 200, 150)
        
        # Test analytics retrieval
        metrics = await analytics.get_user_metrics(user_id)
        assert metrics is not None, "Should return user metrics"

    async def _test_rate_limit_alerting_unit(self):
        """Unit test for RateLimitAlertingManager"""
        alerting = self.components["rate_limit_alerting"]
        
        # Test alert creation
        user_id = "test_user_5"
        await alerting.check_abuse_patterns(user_id)
        
        # Should not trigger alerts for normal usage
        alerts = await alerting.get_active_alerts()
        # Note: This might be empty for normal usage

    async def _test_usage_patterns_analyzer_unit(self):
        """Unit test for UsagePatternsAnalyzer"""
        analyzer = self.components["usage_patterns_analyzer"]
        
        # Test pattern analysis
        user_id = "test_user_6"
        usage_data = {
            "endpoint": "/api/v1/test",
            "hourly_usage": [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65,
                           70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125]
        }
        
        pattern = await analyzer.analyze_usage_pattern(user_id, usage_data)
        assert pattern is not None, "Should return usage pattern"

    async def _test_dynamic_rate_limiter_unit(self):
        """Unit test for DynamicRateLimiter"""
        rate_limiter = self.components["dynamic_rate_limiter"]
        
        # Test dynamic rate limiting
        user_id = "test_user_7"
        user_tier = "pro"
        endpoint = "/api/v1/test"
        
        result = await rate_limiter.check_rate_limit(user_id, endpoint, user_tier)
        assert result is not None, "Should return rate limit result"

    async def _test_usage_forecasting_unit(self):
        """Unit test for UsageForecastingManager"""
        forecaster = self.components["usage_forecasting"]
        
        # Test forecasting
        user_id = "test_user_8"
        forecast = await forecaster.forecast_usage(user_id, days=7)
        
        assert forecast is not None, "Should return usage forecast"
        assert hasattr(forecast, 'predicted_usage'), "Should have predicted usage"

    async def _test_rate_limit_bypass_unit(self):
        """Unit test for RateLimitBypassManager"""
        bypass = self.components["rate_limit_bypass"]
        
        # Test bypass check
        user_id = "test_user_9"
        endpoint = "/api/v1/test"
        
        result = await bypass.check_bypass(user_id, endpoint)
        assert result is not None, "Should return bypass result"

    async def _test_usage_reporting_unit(self):
        """Unit test for UsageReportingManager"""
        reporting = self.components["usage_reporting"]
        
        # Test report generation
        user_id = "test_user_10"
        report = await reporting.generate_usage_report(user_id, "billing")
        
        assert report is not None, "Should generate usage report"

    async def _test_rate_limit_dashboard_unit(self):
        """Unit test for RateLimitDashboard"""
        dashboard = self.components["rate_limit_dashboard"]
        
        # Test dashboard data
        metrics = await dashboard.get_dashboard_metrics()
        assert metrics is not None, "Should return dashboard metrics"

    async def _test_usage_optimizer_unit(self):
        """Unit test for UsageOptimizer"""
        optimizer = self.components["usage_optimizer"]
        
        # Test optimization plan generation
        user_id = "test_user_11"
        plan = await optimizer.generate_optimization_plan(user_id)
        
        assert plan is not None, "Should generate optimization plan"

    async def _test_rate_limiter_integration(self):
        """Integration test for rate limiters"""
        advanced = self.components["advanced_rate_limiter"]
        distributed = self.components["distributed_rate_limiter"]
        
        user_id = "integration_test_user"
        endpoint = "/api/v1/integration"
        
        # Test both rate limiters work together
        adv_result = await advanced.check_rate_limit(user_id, endpoint)
        dist_result = await distributed.check_rate_limit(user_id, endpoint)
        
        assert adv_result is not None, "Advanced rate limiter should return result"
        assert dist_result is not None, "Distributed rate limiter should return result"

    async def _test_analytics_integration(self):
        """Integration test for analytics components"""
        analytics = self.components["usage_analytics"]
        patterns = self.components["usage_patterns_analyzer"]
        
        user_id = "analytics_integration_user"
        
        # Record some usage
        await analytics.record_request(user_id, "/api/v1/test", 200, 150)
        
        # Analyze patterns
        usage_data = {"endpoint": "/api/v1/test", "hourly_usage": [10] * 24}
        pattern = await patterns.analyze_usage_pattern(user_id, usage_data)
        
        assert pattern is not None, "Should analyze usage patterns"

    async def _test_alerting_integration(self):
        """Integration test for alerting"""
        alerting = self.components["rate_limit_alerting"]
        analytics = self.components["usage_analytics"]
        
        user_id = "alerting_integration_user"
        
        # Record usage that might trigger alerts
        for i in range(100):
            await analytics.record_request(user_id, "/api/v1/test", 200, 50)
        
        # Check for alerts
        await alerting.check_abuse_patterns(user_id)

    async def _test_forecasting_integration(self):
        """Integration test for forecasting"""
        forecaster = self.components["usage_forecasting"]
        analytics = self.components["usage_analytics"]
        
        user_id = "forecasting_integration_user"
        
        # Record historical usage
        for i in range(30):
            await analytics.record_request(user_id, "/api/v1/test", 200, 150)
        
        # Generate forecast
        forecast = await forecaster.forecast_usage(user_id, days=7)
        assert forecast is not None, "Should generate forecast"

    async def _test_dashboard_integration(self):
        """Integration test for dashboard"""
        dashboard = self.components["rate_limit_dashboard"]
        analytics = self.components["usage_analytics"]
        
        user_id = "dashboard_integration_user"
        
        # Record some usage
        await analytics.record_request(user_id, "/api/v1/test", 200, 150)
        
        # Get dashboard metrics
        metrics = await dashboard.get_dashboard_metrics()
        assert metrics is not None, "Should return dashboard metrics"

    async def _test_rate_limiter_performance(self):
        """Performance test for rate limiters"""
        rate_limiter = self.components["advanced_rate_limiter"]
        
        # Test performance with many requests
        start_time = time.time()
        
        for i in range(1000):
            user_id = f"perf_user_{i % 100}"
            await rate_limiter.check_rate_limit(user_id, "/api/v1/perf")
        
        execution_time = time.time() - start_time
        requests_per_second = 1000 / execution_time
        
        # Should handle at least 1000 requests per second
        assert requests_per_second >= 1000, f"Performance too slow: {requests_per_second} RPS"

    async def _test_analytics_performance(self):
        """Performance test for analytics"""
        analytics = self.components["usage_analytics"]
        
        # Test performance with many analytics records
        start_time = time.time()
        
        for i in range(1000):
            user_id = f"analytics_user_{i % 100}"
            await analytics.record_request(user_id, "/api/v1/analytics", 200, 150)
        
        execution_time = time.time() - start_time
        requests_per_second = 1000 / execution_time
        
        # Should handle at least 500 analytics records per second
        assert requests_per_second >= 500, f"Analytics performance too slow: {requests_per_second} RPS"

    async def _test_ml_optimizer_performance(self):
        """Performance test for ML optimizer"""
        optimizer = self.components["ml_rate_optimizer"]
        
        # Test performance with many optimizations
        start_time = time.time()
        
        for i in range(100):
            user_id = f"ml_user_{i}"
            await optimizer.optimize_rate_limits(user_id)
        
        execution_time = time.time() - start_time
        optimizations_per_second = 100 / execution_time
        
        # Should handle at least 10 optimizations per second
        assert optimizations_per_second >= 10, f"ML optimizer performance too slow: {optimizations_per_second} RPS"

    async def _test_basic_load(self):
        """Basic load test"""
        config = self.load_test_config
        response_times = []
        errors = []
        
        # Create concurrent users
        tasks = []
        for user_id in range(config.concurrent_users):
            task = self._simulate_user_load(user_id, config.requests_per_second // config.concurrent_users)
            tasks.append(task)
        
        # Execute load test
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = time.time() - start_time
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                response_times.extend(result)
        
        # Calculate metrics
        if response_times:
            metrics = PerformanceMetrics(
                avg_response_time=statistics.mean(response_times),
                p50_response_time=np.percentile(response_times, 50),
                p95_response_time=np.percentile(response_times, 95),
                p99_response_time=np.percentile(response_times, 99),
                requests_per_second=len(response_times) / execution_time,
                error_rate=len(errors) / (len(response_times) + len(errors)),
                throughput=len(response_times) / execution_time,
                cpu_usage=0.0,  # Would need system monitoring
                memory_usage=0.0  # Would need system monitoring
            )
            
            # Assert performance requirements
            assert metrics.avg_response_time < 100, f"Average response time too high: {metrics.avg_response_time}ms"
            assert metrics.p95_response_time < 200, f"P95 response time too high: {metrics.p95_response_time}ms"
            assert metrics.error_rate < 0.01, f"Error rate too high: {metrics.error_rate}"

    async def _test_high_concurrency_stress(self):
        """High concurrency stress test"""
        # Test with very high concurrency
        high_concurrency_config = LoadTestConfig(
            concurrent_users=1000,
            requests_per_second=10000,
            test_duration=30,
            ramp_up_time=5
        )
        
        # Run stress test
        await self._execute_load_test_with_config(high_concurrency_config)

    async def _test_memory_stress(self):
        """Memory stress test"""
        # Test memory usage under stress
        rate_limiter = self.components["advanced_rate_limiter"]
        
        # Create many unique users to stress memory
        for i in range(10000):
            user_id = f"memory_stress_user_{i}"
            await rate_limiter.check_rate_limit(user_id, "/api/v1/memory_stress")

    async def _test_rate_limit_stress(self):
        """Rate limit stress test"""
        rate_limiter = self.components["advanced_rate_limiter"]
        
        # Test rate limiting under extreme load
        user_id = "rate_limit_stress_user"
        
        # Send many requests quickly
        for i in range(10000):
            await rate_limiter.check_rate_limit(user_id, "/api/v1/rate_limit_stress")

    async def _simulate_user_load(self, user_id: int, requests_per_second: int) -> List[float]:
        """Simulate load for a single user"""
        response_times = []
        rate_limiter = self.components["advanced_rate_limiter"]
        
        for i in range(requests_per_second * self.load_test_config.test_duration):
            start_time = time.time()
            
            # Make request
            await rate_limiter.check_rate_limit(f"user_{user_id}", "/api/v1/load_test")
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            response_times.append(response_time)
            
            # Rate limiting
            await asyncio.sleep(1.0 / requests_per_second)
        
        return response_times

    async def _execute_load_test(self) -> PerformanceMetrics:
        """Execute load test and return metrics"""
        return await self._execute_load_test_with_config(self.load_test_config)

    async def _execute_load_test_with_config(self, config: LoadTestConfig) -> PerformanceMetrics:
        """Execute load test with specific configuration"""
        response_times = []
        errors = []
        
        # Create concurrent users
        tasks = []
        for user_id in range(config.concurrent_users):
            task = self._simulate_user_load(user_id, config.requests_per_second // config.concurrent_users)
            tasks.append(task)
        
        # Execute load test
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = time.time() - start_time
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                response_times.extend(result)
        
        # Calculate and return metrics
        if response_times:
            return PerformanceMetrics(
                avg_response_time=statistics.mean(response_times),
                p50_response_time=np.percentile(response_times, 50),
                p95_response_time=np.percentile(response_times, 95),
                p99_response_time=np.percentile(response_times, 99),
                requests_per_second=len(response_times) / execution_time,
                error_rate=len(errors) / (len(response_times) + len(errors)),
                throughput=len(response_times) / execution_time,
                cpu_usage=0.0,  # Would need system monitoring
                memory_usage=0.0  # Would need system monitoring
            )
        else:
            return PerformanceMetrics(0, 0, 0, 0, 0, 1.0, 0, 0, 0)

    async def _start_components(self):
        """Start all components for testing"""
        for name, component in self.components.items():
            if hasattr(component, 'start'):
                try:
                    await component.start()
                    logger.info(f"Started {name}")
                except Exception as e:
                    logger.error(f"Failed to start {name}: {e}")

    async def _stop_components(self):
        """Stop all components after testing"""
        for name, component in self.components.items():
            if hasattr(component, 'stop'):
                try:
                    await component.stop()
                    logger.info(f"Stopped {name}")
                except Exception as e:
                    logger.error(f"Failed to stop {name}: {e}")

# Global test framework instance
_test_framework_instance: Optional[RateLimitingTestFramework] = None

def get_test_framework() -> RateLimitingTestFramework:
    """Get the global test framework instance"""
    global _test_framework_instance
    if _test_framework_instance is None:
        _test_framework_instance = RateLimitingTestFramework()
    return _test_framework_instance

# Utility functions for running tests
async def run_comprehensive_tests() -> Dict[str, Any]:
    """Run comprehensive test suite"""
    framework = get_test_framework()
    return await framework.run_all_tests()

async def run_load_test(config: LoadTestConfig = None) -> Dict[str, Any]:
    """Run load test with specified configuration"""
    framework = get_test_framework()
    return await framework.run_load_test(config)

async def run_unit_tests() -> List[TestResult]:
    """Run only unit tests"""
    framework = get_test_framework()
    await framework._run_unit_tests()
    return framework.test_results

async def run_integration_tests() -> List[TestResult]:
    """Run only integration tests"""
    framework = get_test_framework()
    await framework._run_integration_tests()
    return framework.test_results

# Pytest fixtures
@pytest.fixture
async def test_framework():
    """Pytest fixture for test framework"""
    framework = RateLimitingTestFramework()
    await framework._start_components()
    yield framework
    await framework._stop_components()

@pytest.fixture
async def rate_limiter():
    """Pytest fixture for rate limiter"""
    limiter = get_advanced_rate_limiter()
    await limiter.start()
    yield limiter
    await limiter.stop()

# Test cases for pytest
@pytest.mark.asyncio
async def test_advanced_rate_limiter(rate_limiter):
    """Pytest test for advanced rate limiter"""
    user_id = "pytest_user"
    endpoint = "/api/v1/test"
    
    # Test basic functionality
    result = await rate_limiter.check_rate_limit(user_id, endpoint)
    assert result.allowed
    
    # Test rate limiting
    for i in range(10):
        result = await rate_limiter.check_rate_limit(user_id, endpoint)
    
    # Should eventually be rate limited
    result = await rate_limiter.check_rate_limit(user_id, endpoint)
    assert not result.allowed

@pytest.mark.asyncio
async def test_ml_optimizer():
    """Pytest test for ML optimizer"""
    optimizer = get_ml_rate_optimizer()
    await optimizer.start()
    
    try:
        user_id = "pytest_ml_user"
        optimization = await optimizer.optimize_rate_limits(user_id)
        assert optimization is not None
    finally:
        await optimizer.stop()

if __name__ == "__main__":
    # Run tests when executed directly
    async def main():
        framework = get_test_framework()
        results = await framework.run_all_tests()
        print(json.dumps(results, indent=2, default=str))
    
    asyncio.run(main())
