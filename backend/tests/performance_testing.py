"""
Performance Test Suite with Load Testing and Benchmarking

Provides comprehensive performance testing for RaptorFlow backend API:
- Load testing with concurrent users
- Stress testing with peak load scenarios
- Benchmarking with performance metrics
- VertexAI-specific performance validation
- Real-time monitoring and alerting
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import matplotlib.pyplot as plt
import numpy as np
import psutil
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Performance test types."""
    LOAD = "load"
    STRESS = "stress"
    SPIKE = "spike"
    ENDURANCE = "endurance"
    BENCHMARK = "benchmark"


class PerformanceMetric(Enum):
    """Performance metrics to track."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    CONCURRENT_USERS = "concurrent_users"


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    metric: PerformanceMetric
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    target_value: Optional[float] = None
    variance_threshold: float = 5.0  # Percentage variance allowed


@dataclass
class TestScenario:
    """Performance test scenario configuration."""
    name: str
    test_type: TestType
    endpoint: str
    method: str = "GET"
    concurrent_users: int = 10
    duration: int = 60  # seconds
    ramp_up_time: int = 10  # seconds
    requests_per_second: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    thresholds: List[PerformanceThreshold] = field(default_factory=list)


@dataclass
class PerformanceResult:
    """Individual performance test result."""
    timestamp: datetime
    response_time: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class PerformanceReport:
    """Performance test report."""
    scenario_name: str
    test_type: TestType
    start_time: datetime
    end_time: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float] = field(default_factory=list)
    throughput: float = 0.0
    error_rate: float = 0.0
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    thresholds_met: Dict[str, bool] = field(default_factory=dict)
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def p95_response_time(self) -> float:
        """Calculate 95th percentile response time."""
        return np.percentile(self.response_times, 95) if self.response_times else 0.0
    
    @property
    def p99_response_time(self) -> float:
        """Calculate 99th percentile response time."""
        return np.percentile(self.response_times, 99) if self.response_times else 0.0


class PerformanceTestConfig(BaseModel):
    """Performance test configuration."""
    base_url: str = "http://localhost:8000"
    output_dir: str = "performance_results"
    auth_token: Optional[str] = None
    monitoring_interval: float = 1.0  # seconds
    generate_charts: bool = True
    save_raw_data: bool = True
    alert_thresholds: Dict[str, float] = Field(default_factory=lambda: {
        "response_time": 2.0,
        "error_rate": 5.0,
        "cpu_usage": 80.0,
        "memory_usage": 85.0
    })


class PerformanceTestSuite:
    """Comprehensive performance test suite."""

    def __init__(self, config: PerformanceTestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.monitoring_active = False
        self.monitoring_data: Dict[str, List[float]] = {
            'cpu': [],
            'memory': [],
            'timestamps': []
        }
        
        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        self.monitoring_active = False

    async def _setup_session(self) -> None:
        """Setup HTTP session."""
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=1000, limit_per_host=1000)
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'RaptorFlow-Performance-Test/1.0'
        }
        
        if self.config.auth_token:
            headers['Authorization'] = f'Bearer {self.config.auth_token}'
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers
        )

    async def _make_request(
        self,
        scenario: TestScenario,
        user_id: str
    ) -> PerformanceResult:
        """Make single performance test request."""
        start_time = time.time()
        
        try:
            url = f"{self.config.base_url}{scenario.endpoint}"
            
            async with self.session.request(
                method=scenario.method,
                url=url,
                json=scenario.data,
                headers=scenario.headers
            ) as response:
                response_time = time.time() - start_time
                
                return PerformanceResult(
                    timestamp=datetime.now(),
                    response_time=response_time,
                    status_code=response.status,
                    success=response.status < 400,
                    user_id=user_id
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            
            return PerformanceResult(
                timestamp=datetime.now(),
                response_time=response_time,
                status_code=0,
                success=False,
                error_message=str(e),
                user_id=user_id
            )

    async def _user_simulation(
        self,
        scenario: TestScenario,
        user_id: str,
        duration: int,
        requests_per_second: Optional[int] = None
    ) -> List[PerformanceResult]:
        """Simulate single user behavior."""
        results = []
        end_time = time.time() + duration
        
        if requests_per_second:
            # Fixed rate testing
            interval = 1.0 / requests_per_second
            while time.time() < end_time:
                result = await self._make_request(scenario, user_id)
                results.append(result)
                await asyncio.sleep(interval)
        else:
            # Continuous testing
            while time.time() < end_time:
                result = await self._make_request(scenario, user_id)
                results.append(result)
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
        
        return results

    async def _start_monitoring(self) -> None:
        """Start system resource monitoring."""
        self.monitoring_active = True
        
        async def monitor():
            while self.monitoring_active:
                cpu_percent = psutil.cpu_percent(interval=None)
                memory_percent = psutil.virtual_memory().percent
                
                self.monitoring_data['cpu'].append(cpu_percent)
                self.monitoring_data['memory'].append(memory_percent)
                self.monitoring_data['timestamps'].append(datetime.now())
                
                await asyncio.sleep(self.config.monitoring_interval)
        
        # Start monitoring task
        asyncio.create_task(monitor())

    def _stop_monitoring(self) -> None:
        """Stop system resource monitoring."""
        self.monitoring_active = False

    async def _run_load_test(self, scenario: TestScenario) -> PerformanceReport:
        """Run load test scenario."""
        logger.info(f"Starting load test: {scenario.name}")
        
        start_time = datetime.now()
        await self._start_monitoring()
        
        # Create user tasks
        user_tasks = []
        for i in range(scenario.concurrent_users):
            user_id = f"user_{i}"
            
            # Ramp up delay
            if scenario.ramp_up_time > 0:
                delay = (scenario.ramp_up_time / scenario.concurrent_users) * i
                await asyncio.sleep(delay)
            
            # Start user simulation
            task = self._user_simulation(
                scenario,
                user_id,
                scenario.duration,
                scenario.requests_per_second
            )
            user_tasks.append(task)
        
        # Wait for all users to complete
        user_results = await asyncio.gather(*user_tasks)
        
        # Stop monitoring
        self._stop_monitoring()
        end_time = datetime.now()
        
        # Aggregate results
        all_results = []
        for results in user_results:
            all_results.extend(results)
        
        # Create report
        report = PerformanceReport(
            scenario_name=scenario.name,
            test_type=scenario.test_type,
            start_time=start_time,
            end_time=end_time,
            total_requests=len(all_results),
            successful_requests=sum(1 for r in all_results if r.success),
            failed_requests=sum(1 for r in all_results if not r.success),
            response_times=[r.response_time for r in all_results],
            throughput=len(all_results) / scenario.duration,
            error_rate=(sum(1 for r in all_results if not r.success) / len(all_results)) * 100,
            cpu_usage=self.monitoring_data['cpu'],
            memory_usage=self.monitoring_data['memory']
        )
        
        # Check thresholds
        report.thresholds_met = self._check_thresholds(report, scenario.thresholds)
        
        logger.info(f"Load test completed: {scenario.name} - {report.successful_requests}/{report.total_requests} successful")
        return report

    async def _run_stress_test(self, scenario: TestScenario) -> PerformanceReport:
        """Run stress test scenario."""
        logger.info(f"Starting stress test: {scenario.name}")
        
        # Progressive load increase
        max_users = scenario.concurrent_users * 2
        step_users = scenario.concurrent_users // 4
        step_duration = scenario.duration // 4
        
        all_results = []
        start_time = datetime.now()
        await self._start_monitoring()
        
        for current_users in range(step_users, max_users + 1, step_users):
            logger.info(f"Stress test step: {current_users} concurrent users")
            
            # Run with current user count
            step_results = await self._run_load_test(
                TestScenario(
                    name=f"{scenario.name}_step_{current_users}",
                    test_type=scenario.test_type,
                    endpoint=scenario.endpoint,
                    method=scenario.method,
                    concurrent_users=current_users,
                    duration=step_duration,
                    data=scenario.data,
                    headers=scenario.headers,
                    thresholds=scenario.thresholds
                )
            )
            
            all_results.extend(step_results.response_times)
            
            # Check if system is failing
            if step_results.error_rate > 50:
                logger.warning(f"System failure detected at {current_users} users")
                break
        
        self._stop_monitoring()
        end_time = datetime.now()
        
        # Create final report
        report = PerformanceReport(
            scenario_name=scenario.name,
            test_type=scenario.test_type,
            start_time=start_time,
            end_time=end_time,
            total_requests=len(all_results),
            successful_requests=len(all_results),  # Simplified for stress test
            failed_requests=0,
            response_times=all_results,
            throughput=len(all_results) / (end_time - start_time).total_seconds(),
            error_rate=0.0,
            cpu_usage=self.monitoring_data['cpu'],
            memory_usage=self.monitoring_data['memory']
        )
        
        return report

    async def _run_spike_test(self, scenario: TestScenario) -> PerformanceReport:
        """Run spike test scenario."""
        logger.info(f"Starting spike test: {scenario.name}")
        
        # Baseline load
        baseline_duration = scenario.duration // 3
        spike_duration = scenario.duration // 3
        cooldown_duration = scenario.duration - baseline_duration - spike_duration
        
        all_results = []
        start_time = datetime.now()
        await self._start_monitoring()
        
        # Baseline phase
        baseline_scenario = TestScenario(
            name=f"{scenario.name}_baseline",
            test_type=scenario.test_type,
            endpoint=scenario.endpoint,
            method=scenario.method,
            concurrent_users=scenario.concurrent_users // 2,
            duration=baseline_duration,
            data=scenario.data,
            headers=scenario.headers
        )
        
        baseline_report = await self._run_load_test(baseline_scenario)
        all_results.extend(baseline_report.response_times)
        
        # Spike phase
        spike_scenario = TestScenario(
            name=f"{scenario.name}_spike",
            test_type=scenario.test_type,
            endpoint=scenario.endpoint,
            method=scenario.method,
            concurrent_users=scenario.concurrent_users * 3,
            duration=spike_duration,
            data=scenario.data,
            headers=scenario.headers
        )
        
        spike_report = await self._run_load_test(spike_scenario)
        all_results.extend(spike_report.response_times)
        
        # Cooldown phase
        cooldown_scenario = TestScenario(
            name=f"{scenario.name}_cooldown",
            test_type=scenario.test_type,
            endpoint=scenario.endpoint,
            method=scenario.method,
            concurrent_users=scenario.concurrent_users // 2,
            duration=cooldown_duration,
            data=scenario.data,
            headers=scenario.headers
        )
        
        cooldown_report = await self._run_load_test(cooldown_scenario)
        all_results.extend(cooldown_report.response_times)
        
        self._stop_monitoring()
        end_time = datetime.now()
        
        # Create combined report
        report = PerformanceReport(
            scenario_name=scenario.name,
            test_type=scenario.test_type,
            start_time=start_time,
            end_time=end_time,
            total_requests=len(all_results),
            successful_requests=len(all_results),
            failed_requests=0,
            response_times=all_results,
            throughput=len(all_results) / (end_time - start_time).total_seconds(),
            error_rate=0.0,
            cpu_usage=self.monitoring_data['cpu'],
            memory_usage=self.monitoring_data['memory']
        )
        
        return report

    def _check_thresholds(
        self,
        report: PerformanceReport,
        thresholds: List[PerformanceThreshold]
    ) -> Dict[str, bool]:
        """Check if performance thresholds are met."""
        results = {}
        
        for threshold in thresholds:
            if threshold.metric == PerformanceMetric.RESPONSE_TIME:
                avg_time = report.avg_response_time
                if threshold.max_value and avg_time > threshold.max_value:
                    results[f"response_time_max"] = False
                elif threshold.target_value and abs(avg_time - threshold.target_value) > threshold.variance_threshold:
                    results[f"response_time_target"] = False
                else:
                    results[f"response_time"] = True
            
            elif threshold.metric == PerformanceMetric.ERROR_RATE:
                if threshold.max_value and report.error_rate > threshold.max_value:
                    results["error_rate"] = False
                else:
                    results["error_rate"] = True
            
            elif threshold.metric == PerformanceMetric.THROUGHPUT:
                if threshold.min_value and report.throughput < threshold.min_value:
                    results["throughput"] = False
                else:
                    results["throughput"] = True
            
            elif threshold.metric == PerformanceMetric.CPU_USAGE:
                avg_cpu = statistics.mean(report.cpu_usage) if report.cpu_usage else 0
                if threshold.max_value and avg_cpu > threshold.max_value:
                    results["cpu_usage"] = False
                else:
                    results["cpu_usage"] = True
            
            elif threshold.metric == PerformanceMetric.MEMORY_USAGE:
                avg_memory = statistics.mean(report.memory_usage) if report.memory_usage else 0
                if threshold.max_value and avg_memory > threshold.max_value:
                    results["memory_usage"] = False
                else:
                    results["memory_usage"] = True
        
        return results

    def generate_scenarios(self) -> List[TestScenario]:
        """Generate default performance test scenarios."""
        scenarios = [
            # Load test scenarios
            TestScenario(
                name="Health Check Load Test",
                test_type=TestType.LOAD,
                endpoint="/health",
                concurrent_users=50,
                duration=60,
                thresholds=[
                    PerformanceThreshold(
                        metric=PerformanceMetric.RESPONSE_TIME,
                        max_value=1.0,
                        target_value=0.5
                    ),
                    PerformanceThreshold(
                        metric=PerformanceMetric.ERROR_RATE,
                        max_value=1.0
                    )
                ]
            ),
            
            TestScenario(
                name="User Profile Load Test",
                test_type=TestType.LOAD,
                endpoint="/users/me",
                concurrent_users=100,
                duration=60,
                thresholds=[
                    PerformanceThreshold(
                        metric=PerformanceMetric.RESPONSE_TIME,
                        max_value=2.0,
                        target_value=1.0
                    ),
                    PerformanceThreshold(
                        metric=PerformanceMetric.ERROR_RATE,
                        max_value=2.0
                    )
                ]
            ),
            
            TestScenario(
                name="Workspace List Load Test",
                test_type=TestType.LOAD,
                endpoint="/workspaces",
                concurrent_users=75,
                duration=60,
                thresholds=[
                    PerformanceThreshold(
                        metric=PerformanceMetric.RESPONSE_TIME,
                        max_value=1.5,
                        target_value=0.8
                    ),
                    PerformanceThreshold(
                        metric=PerformanceMetric.ERROR_RATE,
                        max_value=1.5
                    )
                ]
            ),
            
            # VertexAI-specific scenarios
            TestScenario(
                name="VertexAI Inference Load Test",
                test_type=TestType.LOAD,
                endpoint="/api/v1/ai/inference",
                method="POST",
                concurrent_users=20,
                duration=120,
                data={
                    "prompt": "Test prompt for performance testing",
                    "model": "gemini-pro",
                    "max_tokens": 100
                },
                thresholds=[
                    PerformanceThreshold(
                        metric=PerformanceMetric.RESPONSE_TIME,
                        max_value=5.0,
                        target_value=3.0
                    ),
                    PerformanceThreshold(
                        metric=PerformanceMetric.ERROR_RATE,
                        max_value=5.0
                    )
                ]
            ),
            
            # Stress test scenarios
            TestScenario(
                name="Health Check Stress Test",
                test_type=TestType.STRESS,
                endpoint="/health",
                concurrent_users=200,
                duration=120,
                thresholds=[
                    PerformanceThreshold(
                        metric=PerformanceMetric.RESPONSE_TIME,
                        max_value=3.0
                    ),
                    PerformanceThreshold(
                        metric=PerformanceMetric.ERROR_RATE,
                        max_value=10.0
                    )
                ]
            ),
            
            # Spike test scenarios
            TestScenario(
                name="Spike Test - Authentication",
                test_type=TestType.SPIKE,
                endpoint="/auth/login",
                method="POST",
                concurrent_users=50,
                duration=90,
                data={
                    "email": "test@example.com",
                    "password": "testpassword123"
                },
                thresholds=[
                    PerformanceThreshold(
                        metric=PerformanceMetric.RESPONSE_TIME,
                        max_value=2.0
                    ),
                    PerformanceThreshold(
                        metric=PerformanceMetric.ERROR_RATE,
                        max_value=5.0
                    )
                ]
            )
        ]
        
        return scenarios

    def generate_performance_charts(self, reports: List[PerformanceReport]) -> None:
        """Generate performance visualization charts."""
        if not self.config.generate_charts:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Response time chart
        plt.figure(figsize=(12, 8))
        
        for i, report in enumerate(reports):
            plt.subplot(2, 2, 1)
            plt.hist(report.response_times, bins=50, alpha=0.7, label=report.scenario_name)
            plt.xlabel('Response Time (s)')
            plt.ylabel('Frequency')
            plt.title('Response Time Distribution')
            plt.legend()
            
            # Throughput chart
            plt.subplot(2, 2, 2)
            plt.bar(report.scenario_name, report.throughput)
            plt.ylabel('Throughput (requests/sec)')
            plt.title('Throughput Comparison')
            plt.xticks(rotation=45)
            
            # Error rate chart
            plt.subplot(2, 2, 3)
            plt.bar(report.scenario_name, report.error_rate)
            plt.ylabel('Error Rate (%)')
            plt.title('Error Rate Comparison')
            plt.xticks(rotation=45)
            
            # Resource usage chart
            plt.subplot(2, 2, 4)
            if report.cpu_usage:
                plt.plot(report.cpu_usage, label='CPU Usage')
            if report.memory_usage:
                plt.plot(report.memory_usage, label='Memory Usage')
            plt.ylabel('Usage (%)')
            plt.xlabel('Time')
            plt.title('Resource Usage')
            plt.legend()
        
        plt.tight_layout()
        chart_file = Path(self.config.output_dir) / f"performance_charts_{timestamp}.png"
        plt.savefig(chart_file)
        plt.close()
        
        logger.info(f"Performance charts saved: {chart_file}")

    def generate_report(self, reports: List[PerformanceReport]) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_scenarios': len(reports),
                'total_requests': sum(r.total_requests for r in reports),
                'total_successful': sum(r.successful_requests for r in reports),
                'total_failed': sum(r.failed_requests for r in reports),
                'overall_success_rate': (
                    sum(r.successful_requests for r in reports) /
                    sum(r.total_requests for r in reports) * 100
                ) if reports else 0,
                'avg_response_time': (
                    sum(r.avg_response_time for r in reports) / len(reports)
                ) if reports else 0
            },
            'scenarios': [
                {
                    'name': report.scenario_name,
                    'test_type': report.test_type.value,
                    'start_time': report.start_time.isoformat(),
                    'end_time': report.end_time.isoformat(),
                    'total_requests': report.total_requests,
                    'successful_requests': report.successful_requests,
                    'failed_requests': report.failed_requests,
                    'throughput': report.throughput,
                    'error_rate': report.error_rate,
                    'avg_response_time': report.avg_response_time,
                    'p95_response_time': report.p95_response_time,
                    'p99_response_time': report.p99_response_time,
                    'thresholds_met': report.thresholds_met,
                    'cpu_usage': {
                        'avg': statistics.mean(report.cpu_usage) if report.cpu_usage else 0,
                        'max': max(report.cpu_usage) if report.cpu_usage else 0,
                        'min': min(report.cpu_usage) if report.cpu_usage else 0
                    },
                    'memory_usage': {
                        'avg': statistics.mean(report.memory_usage) if report.memory_usage else 0,
                        'max': max(report.memory_usage) if report.memory_usage else 0,
                        'min': min(report.memory_usage) if report.memory_usage else 0
                    }
                }
                for report in reports
            ]
        }

    def save_reports(self, reports: List[PerformanceReport]) -> None:
        """Save performance test reports."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON report
        report_data = self.generate_report(reports)
        json_file = Path(self.config.output_dir) / f"performance_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        logger.info(f"Performance report saved: {json_file}")
        
        # Save raw data if enabled
        if self.config.save_raw_data:
            raw_data = {
                'monitoring_data': self.monitoring_data,
                'reports': [
                    {
                        'scenario_name': report.scenario_name,
                        'response_times': report.response_times,
                        'cpu_usage': report.cpu_usage,
                        'memory_usage': report.memory_usage
                    }
                    for report in reports
                ]
            }
            raw_file = Path(self.config.output_dir) / f"raw_data_{timestamp}.json"
            with open(raw_file, 'w') as f:
                json.dump(raw_data, f, indent=2)
            logger.info(f"Raw data saved: {raw_file}")
        
        # Generate charts
        self.generate_performance_charts(reports)

    async def run_performance_tests(self, scenarios: Optional[List[TestScenario]] = None) -> List[PerformanceReport]:
        """Run performance tests."""
        if scenarios is None:
            scenarios = self.generate_scenarios()
        
        logger.info(f"Starting {len(scenarios)} performance test scenarios")
        
        reports = []
        for scenario in scenarios:
            try:
                if scenario.test_type == TestType.LOAD:
                    report = await self._run_load_test(scenario)
                elif scenario.test_type == TestType.STRESS:
                    report = await self._run_stress_test(scenario)
                elif scenario.test_type == TestType.SPIKE:
                    report = await self._run_spike_test(scenario)
                else:
                    logger.warning(f"Unsupported test type: {scenario.test_type}")
                    continue
                
                reports.append(report)
                
                # Check alert thresholds
                self._check_alerts(report)
                
            except Exception as e:
                logger.error(f"Performance test failed for {scenario.name}: {e}")
        
        # Save reports
        self.save_reports(reports)
        
        logger.info(f"Performance testing completed: {len(reports)} scenarios executed")
        return reports

    def _check_alerts(self, report: PerformanceReport) -> None:
        """Check for performance alerts."""
        alerts = []
        
        # Response time alert
        if report.avg_response_time > self.config.alert_thresholds.get('response_time', 2.0):
            alerts.append({
                'type': 'response_time',
                'severity': 'warning',
                'message': f"Average response time {report.avg_response_time:.3f}s exceeds threshold",
                'scenario': report.scenario_name
            })
        
        # Error rate alert
        if report.error_rate > self.config.alert_thresholds.get('error_rate', 5.0):
            alerts.append({
                'type': 'error_rate',
                'severity': 'critical',
                'message': f"Error rate {report.error_rate:.1f}% exceeds threshold",
                'scenario': report.scenario_name
            })
        
        # CPU usage alert
        if report.cpu_usage:
            avg_cpu = statistics.mean(report.cpu_usage)
            if avg_cpu > self.config.alert_thresholds.get('cpu_usage', 80.0):
                alerts.append({
                    'type': 'cpu_usage',
                    'severity': 'warning',
                    'message': f"Average CPU usage {avg_cpu:.1f}% exceeds threshold",
                    'scenario': report.scenario_name
                })
        
        # Memory usage alert
        if report.memory_usage:
            avg_memory = statistics.mean(report.memory_usage)
            if avg_memory > self.config.alert_thresholds.get('memory_usage', 85.0):
                alerts.append({
                    'type': 'memory_usage',
                    'severity': 'warning',
                    'message': f"Average memory usage {avg_memory:.1f}% exceeds threshold",
                    'scenario': report.scenario_name
                })
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Performance Alert [{alert['severity'].upper()}]: {alert['message']} (Scenario: {alert['scenario']})")


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run performance tests")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base API URL")
    parser.add_argument("--auth-token", help="Authentication token")
    parser.add_argument("--output-dir", default="performance_results", help="Output directory")
    parser.add_argument("--scenarios", help="JSON file with test scenarios")
    parser.add_argument("--no-charts", action="store_true", help="Disable chart generation")
    parser.add_argument("--no-raw-data", action="store_true", help="Disable raw data saving")
    
    args = parser.parse_args()
    
    # Create configuration
    config = PerformanceTestConfig(
        base_url=args.base_url,
        auth_token=args.auth_token,
        output_dir=args.output_dir,
        generate_charts=not args.no_charts,
        save_raw_data=not args.no_raw_data
    )
    
    # Load custom scenarios if provided
    scenarios = None
    if args.scenarios:
        with open(args.scenarios, 'r') as f:
            scenarios_data = json.load(f)
        # Convert to TestScenario objects (simplified)
        scenarios = []
        for data in scenarios_data:
            scenarios.append(TestScenario(**data))
    
    # Run performance tests
    async def main():
        async with PerformanceTestSuite(config) as suite:
            reports = await suite.run_performance_tests(scenarios)
            
            # Print summary
            print(f"\nPerformance Testing Summary:")
            print(f"Total Scenarios: {len(reports)}")
            print(f"Total Requests: {sum(r.total_requests for r in reports)}")
            print(f"Success Rate: {sum(r.successful_requests for r in reports) / sum(r.total_requests for r in reports) * 100:.1f}%")
            print(f"Average Response Time: {sum(r.avg_response_time for r in reports) / len(reports):.3f}s")
    
    asyncio.run(main())
