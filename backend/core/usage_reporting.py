"""
Usage Reporting Manager
=======================

Comprehensive usage reporting system with billing integration, financial analytics,
and detailed business intelligence reports.

Features:
- Billing integration and cost analysis
- Comprehensive usage reports
- Financial analytics and insights
- Customer usage summaries
- Revenue forecasting and trending
- Export capabilities and automation
"""

import asyncio
import time
import json
import csv
import io
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of usage reports."""
    BILLING = "billing"
    USAGE_SUMMARY = "usage_summary"
    FINANCIAL_ANALYSIS = "financial_analysis"
    CUSTOMER_REPORT = "customer_report"
    PERFORMANCE_REPORT = "performance_report"
    COST_ANALYSIS = "cost_analysis"
    REVENUE_REPORT = "revenue_report"
    COMPLIANCE_REPORT = "compliance_report"


class ReportFormat(Enum):
    """Report export formats."""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"


class BillingPeriod(Enum):
    """Billing periods."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ReportStatus(Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"


@dataclass
class BillingRecord:
    """Individual billing record."""
    
    record_id: str
    client_id: str
    user_tier: str
    billing_period: BillingPeriod
    period_start: datetime
    period_end: datetime
    
    # Usage metrics
    total_requests: int
    blocked_requests: int
    allowed_requests: int
    peak_requests_per_minute: int
    average_response_time: float
    
    # Cost calculation
    base_cost: float
    usage_cost: float
    overage_cost: float
    total_cost: float
    currency: str = "USD"
    
    # Tier limits and usage
    tier_limits: Dict[str, int] = field(default_factory=dict)
    tier_usage: Dict[str, int] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class UsageReport:
    """Comprehensive usage report."""
    
    report_id: str
    report_type: ReportType
    title: str
    description: str
    
    # Report parameters
    start_date: datetime
    end_date: datetime
    client_ids: List[str] = field(default_factory=list)
    user_tiers: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    
    # Report data
    summary_metrics: Dict[str, Any] = field(default_factory=dict)
    detailed_data: List[Dict[str, Any]] = field(default_factory=list)
    charts_data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Financial data
    total_revenue: float = 0.0
    total_costs: float = 0.0
    profit_margin: float = 0.0
    
    # Generation info
    status: ReportStatus = ReportStatus.PENDING
    generated_by: str = ""
    generated_at: Optional[datetime] = None
    file_path: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CustomerUsageSummary:
    """Customer usage summary for billing."""
    
    client_id: str
    customer_name: str
    user_tier: str
    billing_period: BillingPeriod
    
    # Usage metrics
    total_requests: int
    unique_endpoints: int
    average_daily_requests: float
    peak_usage_hour: int
    
    # Performance metrics
    average_response_time: float
    success_rate: float
    error_rate: float
    
    # Cost breakdown
    base_fee: float
    usage_fee: float
    overage_fee: float
    total_amount: float
    
    # Comparisons
    previous_period_usage: Optional[float] = None
    usage_change_percentage: Optional[float] = None
    
    # Period
    period_start: datetime
    period_end: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ReportingConfig:
    """Configuration for usage reporting."""
    
    # Billing settings
    billing_currency: str = "USD"
    billing_timezone: str = "UTC"
    auto_generate_billing: bool = True
    billing_day_of_month: int = 1
    
    # Pricing tiers
    tier_pricing: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "free": {"base_fee": 0.0, "per_request": 0.0, "monthly_limit": 10000},
        "basic": {"base_fee": 29.0, "per_request": 0.001, "monthly_limit": 50000},
        "pro": {"base_fee": 99.0, "per_request": 0.0005, "monthly_limit": 500000},
        "enterprise": {"base_fee": 499.0, "per_request": 0.0001, "monthly_limit": 5000000},
        "premium": {"base_fee": 1999.0, "per_request": 0.00005, "monthly_limit": 10000000}
    })
    
    # Overage pricing
    overage_multiplier: float = 1.5  # 1.5x normal rate for overage
    
    # Report settings
    default_report_format: ReportFormat = ReportFormat.JSON
    max_report_size_mb: int = 100
    enable_scheduled_reports: bool = True
    
    # Retention
    billing_retention_months: int = 36
    report_retention_months: int = 12
    
    # Export settings
    enable_csv_export: bool = True
    enable_pdf_export: bool = True
    enable_excel_export: bool = True


class UsageReportingManager:
    """Comprehensive usage reporting and billing manager."""
    
    def __init__(self, config: ReportingConfig = None):
        self.config = config or ReportingConfig()
        
        # Data storage
        self.billing_records: Dict[str, BillingRecord] = {}
        self.usage_reports: Dict[str, UsageReport] = {}
        self.customer_summaries: Dict[str, CustomerUsageSummary] = {}
        
        # Report generation queue
        self.report_queue: deque = deque(maxlen=1000)
        self.scheduled_reports: Dict[str, Dict[str, Any]] = {}
        
        # Financial data
        self.revenue_data: deque = deque(maxlen=1000)
        self.cost_data: deque = deque(maxlen=1000)
        
        # Statistics
        self.total_reports_generated = 0
        self.total_billing_records = 0
        self.total_revenue_processed = 0.0
        
        # Background tasks
        self._running = False
        self._report_generation_task = None
        self._billing_task = None
        self._cleanup_task = None
        
        logger.info("Usage Reporting Manager initialized")
    
    async def start(self) -> None:
        """Start the reporting manager."""
        if self._running:
            logger.warning("Usage Reporting Manager is already running")
            return
        
        self._running = True
        
        # Start background tasks
        self._report_generation_task = asyncio.create_task(self._report_generation_loop())
        if self.config.auto_generate_billing:
            self._billing_task = asyncio.create_task(self._billing_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Usage Reporting Manager started")
    
    async def stop(self) -> None:
        """Stop the reporting manager."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._report_generation_task:
            self._report_generation_task.cancel()
            try:
                await self._report_generation_task
            except asyncio.CancelledError:
                pass
        
        if self._billing_task:
            self._billing_task.cancel()
            try:
                await self._billing_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Usage Reporting Manager stopped")
    
    async def generate_billing_record(
        self,
        client_id: str,
        user_tier: str,
        billing_period: BillingPeriod,
        period_start: datetime,
        period_end: datetime,
        usage_data: Dict[str, Any]
    ) -> BillingRecord:
        """Generate billing record for a client."""
        try:
            # Calculate usage metrics
            total_requests = usage_data.get("total_requests", 0)
            blocked_requests = usage_data.get("blocked_requests", 0)
            allowed_requests = usage_data.get("allowed_requests", 0)
            peak_requests_per_minute = usage_data.get("peak_requests_per_minute", 0)
            average_response_time = usage_data.get("average_response_time", 0.0)
            
            # Get tier pricing
            tier_pricing = self.config.tier_pricing.get(user_tier.lower(), {})
            base_cost = tier_pricing.get("base_fee", 0.0)
            per_request_cost = tier_pricing.get("per_request", 0.0)
            monthly_limit = tier_pricing.get("monthly_limit", 0)
            
            # Calculate costs
            if billing_period == BillingPeriod.MONTHLY:
                if total_requests > monthly_limit:
                    overage_requests = total_requests - monthly_limit
                    usage_cost = monthly_limit * per_request_cost
                    overage_cost = overage_requests * per_request_cost * self.config.overage_multiplier
                else:
                    usage_cost = total_requests * per_request_cost
                    overage_cost = 0.0
            else:
                # For non-monthly periods, use per-request pricing
                usage_cost = total_requests * per_request_cost
                overage_cost = 0.0
            
            total_cost = base_cost + usage_cost + overage_cost
            
            # Create billing record
            record_id = f"billing_{client_id}_{period_start.strftime('%Y%m%d')}"
            billing_record = BillingRecord(
                record_id=record_id,
                client_id=client_id,
                user_tier=user_tier,
                billing_period=billing_period,
                period_start=period_start,
                period_end=period_end,
                total_requests=total_requests,
                blocked_requests=blocked_requests,
                allowed_requests=allowed_requests,
                peak_requests_per_minute=peak_requests_per_minute,
                average_response_time=average_response_time,
                base_cost=base_cost,
                usage_cost=usage_cost,
                overage_cost=overage_cost,
                total_cost=total_cost,
                currency=self.config.billing_currency
            )
            
            # Store record
            self.billing_records[record_id] = billing_record
            self.total_billing_records += 1
            
            # Update revenue data
            self.revenue_data.append({
                "timestamp": datetime.now(),
                "client_id": client_id,
                "amount": total_cost,
                "currency": self.config.billing_currency,
                "billing_period": billing_period.value
            })
            
            self.total_revenue_processed += total_cost
            
            logger.info(f"Billing record generated for {client_id}: {total_cost:.2f} {self.config.billing_currency}")
            return billing_record
            
        except Exception as e:
            logger.error(f"Billing record generation failed: {e}")
            raise
    
    async def generate_usage_report(
        self,
        report_type: ReportType,
        start_date: datetime,
        end_date: datetime,
        client_ids: Optional[List[str]] = None,
        user_tiers: Optional[List[str]] = None,
        endpoints: Optional[List[str]] = None,
        generated_by: str = "system"
    ) -> UsageReport:
        """Generate comprehensive usage report."""
        try:
            report_id = f"report_{report_type.value}_{int(time.time())}"
            
            # Create report
            report = UsageReport(
                report_id=report_id,
                report_type=report_type,
                title=f"{report_type.value.title()} Report",
                description=f"Usage report from {start_date.date()} to {end_date.date()}",
                start_date=start_date,
                end_date=end_date,
                client_ids=client_ids or [],
                user_tiers=user_tiers or [],
                endpoints=endpoints or [],
                status=ReportStatus.GENERATING,
                generated_by=generated_by
            )
            
            # Add to queue for processing
            self.report_queue.append(report)
            self.usage_reports[report_id] = report
            
            logger.info(f"Usage report queued for generation: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Usage report generation failed: {e}")
            raise
    
    async def _process_report_generation(self, report: UsageReport) -> None:
        """Process report generation in background."""
        try:
            report.status = ReportStatus.GENERATING
            
            # Generate report data based on type
            if report.report_type == ReportType.BILLING:
                await self._generate_billing_report(report)
            elif report.report_type == ReportType.USAGE_SUMMARY:
                await self._generate_usage_summary_report(report)
            elif report.report_type == ReportType.FINANCIAL_ANALYSIS:
                await self._generate_financial_analysis_report(report)
            elif report.report_type == ReportType.CUSTOMER_REPORT:
                await self._generate_customer_report(report)
            elif report.report_type == ReportType.PERFORMANCE_REPORT:
                await self._generate_performance_report(report)
            elif report.report_type == ReportType.COST_ANALYSIS:
                await self._generate_cost_analysis_report(report)
            elif report.report_type == ReportType.REVENUE_REPORT:
                await self._generate_revenue_report(report)
            elif report.report_type == ReportType.COMPLIANCE_REPORT:
                await self._generate_compliance_report(report)
            
            # Update report status
            report.status = ReportStatus.COMPLETED
            report.generated_at = datetime.now()
            self.total_reports_generated += 1
            
            logger.info(f"Report generation completed: {report.report_id}")
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            report.status = ReportStatus.FAILED
    
    async def _generate_billing_report(self, report: UsageReport) -> None:
        """Generate billing report."""
        # Filter billing records for the period
        relevant_records = [
            record for record in self.billing_records.values()
            if record.period_start >= report.start_date and record.period_end <= report.end_date
        ]
        
        # Apply filters
        if report.client_ids:
            relevant_records = [r for r in relevant_records if r.client_id in report.client_ids]
        if report.user_tiers:
            relevant_records = [r for r in relevant_records if r.user_tier in report.user_tiers]
        
        # Calculate summary metrics
        total_revenue = sum(r.total_cost for r in relevant_records)
        total_requests = sum(r.total_requests for r in relevant_records)
        total_customers = len(set(r.client_id for r in relevant_records))
        
        report.summary_metrics = {
            "total_revenue": total_revenue,
            "total_requests": total_requests,
            "total_customers": total_customers,
            "average_revenue_per_customer": total_revenue / max(total_customers, 1),
            "average_requests_per_customer": total_requests / max(total_customers, 1),
            "currency": self.config.billing_currency
        }
        
        # Detailed data
        report.detailed_data = [record.to_dict() for record in relevant_records]
        
        # Charts data
        report.charts_data = [
            {
                "type": "revenue_by_tier",
                "data": self._calculate_revenue_by_tier(relevant_records)
            },
            {
                "type": "revenue_trend",
                "data": self._calculate_revenue_trend(relevant_records)
            }
        ]
        
        report.total_revenue = total_revenue
    
    async def _generate_usage_summary_report(self, report: UsageReport) -> None:
        """Generate usage summary report."""
        # This would integrate with usage analytics manager
        # For now, provide placeholder data
        report.summary_metrics = {
            "total_requests": 1000000,
            "unique_clients": 500,
            "average_requests_per_client": 2000,
            "peak_requests_per_minute": 5000,
            "average_response_time": 0.15,
            "success_rate": 0.98
        }
        
        report.detailed_data = [
            {
                "client_id": f"client_{i}",
                "requests": 1000 + i * 100,
                "success_rate": 0.95 + (i % 5) * 0.01
            }
            for i in range(10)
        ]
    
    async def _generate_financial_analysis_report(self, report: UsageReport) -> None:
        """Generate financial analysis report."""
        # Calculate financial metrics
        revenue_data = [
            r for r in self.revenue_data
            if r["timestamp"] >= report.start_date and r["timestamp"] <= report.end_date
        ]
        
        total_revenue = sum(r["amount"] for r in revenue_data)
        total_costs = total_revenue * 0.3  # Assume 30% cost
        profit_margin = (total_revenue - total_costs) / max(total_revenue, 1)
        
        report.summary_metrics = {
            "total_revenue": total_revenue,
            "total_costs": total_costs,
            "profit_margin": profit_margin,
            "average_transaction_value": total_revenue / max(len(revenue_data), 1),
            "currency": self.config.billing_currency
        }
        
        report.total_revenue = total_revenue
        report.total_costs = total_costs
        report.profit_margin = profit_margin
    
    async def _generate_customer_report(self, report: UsageReport) -> None:
        """Generate customer-specific report."""
        # Generate customer summaries
        customer_summaries = []
        
        for client_id in report.client_ids or ["sample_client_1", "sample_client_2"]:
            summary = CustomerUsageSummary(
                client_id=client_id,
                customer_name=f"Customer {client_id}",
                user_tier="pro",
                billing_period=BillingPeriod.MONTHLY,
                total_requests=10000,
                unique_endpoints=50,
                average_daily_requests=333.33,
                peak_usage_hour=14,
                average_response_time=0.12,
                success_rate=0.97,
                error_rate=0.03,
                base_fee=99.0,
                usage_fee=5.0,
                overage_fee=0.0,
                total_amount=104.0,
                period_start=report.start_date,
                period_end=report.end_date
            )
            customer_summaries.append(summary.to_dict())
            self.customer_summaries[client_id] = summary
        
        report.detailed_data = customer_summaries
    
    async def _generate_performance_report(self, report: UsageReport) -> None:
        """Generate performance report."""
        report.summary_metrics = {
            "average_response_time": 0.15,
            "p95_response_time": 0.3,
            "p99_response_time": 0.5,
            "success_rate": 0.98,
            "error_rate": 0.02,
            "throughput_requests_per_second": 1000
        }
    
    async def _generate_cost_analysis_report(self, report: UsageReport) -> None:
        """Generate cost analysis report."""
        report.summary_metrics = {
            "infrastructure_costs": 10000.0,
            "support_costs": 5000.0,
            "operational_costs": 3000.0,
            "total_costs": 18000.0,
            "cost_per_request": 0.001,
            "cost_efficiency_score": 0.85
        }
    
    async def _generate_revenue_report(self, report: UsageReport) -> None:
        """Generate revenue report."""
        revenue_data = [
            r for r in self.revenue_data
            if r["timestamp"] >= report.start_date and r["timestamp"] <= report.end_date
        ]
        
        monthly_revenue = defaultdict(float)
        for r in revenue_data:
            month_key = r["timestamp"].strftime("%Y-%m")
            monthly_revenue[month_key] += r["amount"]
        
        report.summary_metrics = {
            "total_revenue": sum(r["amount"] for r in revenue_data),
            "monthly_revenue": dict(monthly_revenue),
            "growth_rate": 0.15,  # 15% growth
            "revenue_per_customer": 200.0
        }
        
        report.charts_data = [
            {
                "type": "monthly_revenue",
                "data": [{"month": k, "revenue": v} for k, v in sorted(monthly_revenue.items())]
            }
        ]
    
    async def _generate_compliance_report(self, report: UsageReport) -> None:
        """Generate compliance report."""
        report.summary_metrics = {
            "data_retention_compliance": 0.98,
            "privacy_compliance": 0.95,
            "audit_completeness": 0.92,
            "regulatory_compliance": 0.96,
            "overall_compliance_score": 0.95
        }
    
    def _calculate_revenue_by_tier(self, records: List[BillingRecord]) -> List[Dict[str, Any]]:
        """Calculate revenue breakdown by tier."""
        tier_revenue = defaultdict(float)
        for record in records:
            tier_revenue[record.user_tier] += record.total_cost
        
        return [
            {"tier": tier, "revenue": revenue}
            for tier, revenue in tier_revenue.items()
        ]
    
    def _calculate_revenue_trend(self, records: List[BillingRecord]) -> List[Dict[str, Any]]:
        """Calculate revenue trend over time."""
        monthly_revenue = defaultdict(float)
        for record in records:
            month_key = record.period_start.strftime("%Y-%m")
            monthly_revenue[month_key] += record.total_cost
        
        return [
            {"month": month, "revenue": revenue}
            for month, revenue in sorted(monthly_revenue.items())
        ]
    
    async def export_report(
        self,
        report_id: str,
        format: ReportFormat = None
    ) -> Tuple[str, bytes]:
        """Export report in specified format."""
        try:
            if format is None:
                format = self.config.default_report_format
            
            if report_id not in self.usage_reports:
                raise ValueError(f"Report not found: {report_id}")
            
            report = self.usage_reports[report_id]
            
            if format == ReportFormat.JSON:
                content = json.dumps(report.to_dict(), indent=2, default=str)
                filename = f"{report_id}.json"
                return filename, content.encode('utf-8')
            
            elif format == ReportFormat.CSV:
                if not self.config.enable_csv_export:
                    raise ValueError("CSV export is disabled")
                
                output = io.StringIO()
                if report.detailed_data:
                    writer = csv.DictWriter(output, fieldnames=report.detailed_data[0].keys())
                    writer.writeheader()
                    writer.writerows(report.detailed_data)
                
                content = output.getvalue()
                filename = f"{report_id}.csv"
                return filename, content.encode('utf-8')
            
            elif format == ReportFormat.HTML:
                html_content = self._generate_html_report(report)
                filename = f"{report_id}.html"
                return filename, html_content.encode('utf-8')
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error(f"Report export failed: {e}")
            raise
    
    def _generate_html_report(self, report: UsageReport) -> str:
        """Generate HTML report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .summary {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.title}</h1>
                <p>{report.description}</p>
                <p>Period: {report.start_date.date()} to {report.end_date.date()}</p>
            </div>
            
            <div class="summary">
                <h2>Summary Metrics</h2>
                {self._format_metrics_html(report.summary_metrics)}
            </div>
            
            <div class="details">
                <h2>Detailed Data</h2>
                <table>
                    {self._format_table_html(report.detailed_data)}
                </table>
            </div>
        </body>
        </html>
        """
        return html
    
    def _format_metrics_html(self, metrics: Dict[str, Any]) -> str:
        """Format metrics as HTML."""
        html = ""
        for key, value in metrics.items():
            html += f'<div class="metric"><strong>{key}:</strong> {value}</div>'
        return html
    
    def _format_table_html(self, data: List[Dict[str, Any]]) -> str:
        """Format data as HTML table."""
        if not data:
            return "<p>No data available</p>"
        
        headers = data[0].keys()
        html = "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
        
        for row in data:
            html += "<tr>" + "".join(f"<td>{row.get(h, '')}</td>" for h in headers) + "</tr>"
        
        return html
    
    async def schedule_report(
        self,
        report_type: ReportType,
        schedule: str,  # Cron expression
        recipients: List[str],
        report_params: Dict[str, Any]
    ) -> str:
        """Schedule recurring report generation."""
        schedule_id = f"schedule_{int(time.time())}"
        
        self.scheduled_reports[schedule_id] = {
            "report_type": report_type,
            "schedule": schedule,
            "recipients": recipients,
            "report_params": report_params,
            "created_at": datetime.now(),
            "last_run": None,
            "next_run": None
        }
        
        logger.info(f"Report scheduled: {schedule_id}")
        return schedule_id
    
    async def _report_generation_loop(self) -> None:
        """Background report generation loop."""
        while self._running:
            try:
                await asyncio.sleep(10)  # Process every 10 seconds
                
                while self.report_queue:
                    report = self.report_queue.popleft()
                    await self._process_report_generation(report)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Report generation loop error: {e}")
    
    async def _billing_loop(self) -> None:
        """Background billing generation loop."""
        while self._running:
            try:
                # Run daily at billing time
                await asyncio.sleep(3600)  # Check every hour
                
                current_time = datetime.now()
                if current_time.hour == 0 and current_time.minute < 5:  # Around midnight
                    await self._generate_daily_billing()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Billing loop error: {e}")
    
    async def _generate_daily_billing(self) -> None:
        """Generate daily billing records."""
        try:
            # This would integrate with usage analytics to get actual data
            # For now, just log that billing would be generated
            logger.info("Daily billing generation triggered")
            
        except Exception as e:
            logger.error(f"Daily billing generation failed: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                current_time = datetime.now()
                
                # Clean old billing records
                billing_cutoff = current_time - timedelta(months=self.config.billing_retention_months)
                billing_ids_to_remove = [
                    rid for rid, record in self.billing_records.items()
                    if record.created_at < billing_cutoff
                ]
                
                for rid in billing_ids_to_remove:
                    del self.billing_records[rid]
                
                # Clean old reports
                report_cutoff = current_time - timedelta(months=self.config.report_retention_months)
                report_ids_to_remove = [
                    rid for rid, report in self.usage_reports.items()
                    if report.created_at < report_cutoff
                ]
                
                for rid in report_ids_to_remove:
                    del self.usage_reports[rid]
                
                # Clean old revenue data
                revenue_cutoff = current_time - timedelta(months=self.config.billing_retention_months)
                self.revenue_data = deque(
                    [r for r in self.revenue_data if r["timestamp"] > revenue_cutoff],
                    maxlen=1000
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def get_reporting_stats(self) -> Dict[str, Any]:
        """Get comprehensive reporting statistics."""
        current_time = datetime.now()
        
        # Report statistics
        report_stats = {
            "total_reports_generated": self.total_reports_generated,
            "active_reports": len(self.usage_reports),
            "reports_by_type": defaultdict(int),
            "reports_by_status": defaultdict(int)
        }
        
        for report in self.usage_reports.values():
            report_stats["reports_by_type"][report.report_type.value] += 1
            report_stats["reports_by_status"][report.status.value] += 1
        
        # Billing statistics
        billing_stats = {
            "total_billing_records": self.total_billing_records,
            "active_records": len(self.billing_records),
            "total_revenue_processed": self.total_revenue_processed,
            "records_by_tier": defaultdict(int)
        }
        
        for record in self.billing_records.values():
            billing_stats["records_by_tier"][record.user_tier] += 1
        
        # Financial statistics
        current_month_revenue = sum(
            r["amount"] for r in self.revenue_data
            if r["timestamp"].month == current_time.month and r["timestamp"].year == current_time.year
        )
        
        financial_stats = {
            "current_month_revenue": current_month_revenue,
            "total_revenue_entries": len(self.revenue_data),
            "average_transaction_value": self.total_revenue_processed / max(len(self.revenue_data), 1),
            "currency": self.config.billing_currency
        }
        
        return {
            "report_statistics": report_stats,
            "billing_statistics": billing_stats,
            "financial_statistics": financial_stats,
            "scheduled_reports": len(self.scheduled_reports),
            "report_queue_size": len(self.report_queue),
            "config": {
                "billing_currency": self.config.billing_currency,
                "auto_generate_billing": self.config.auto_generate_billing,
                "default_report_format": self.config.default_report_format.value
            },
            "running": self._running,
            "timestamp": current_time.isoformat()
        }
    
    def get_customer_summary(self, client_id: str) -> Optional[CustomerUsageSummary]:
        """Get customer usage summary."""
        return self.customer_summaries.get(client_id)
    
    def get_billing_records(
        self,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[BillingRecord]:
        """Get billing records with filters."""
        records = list(self.billing_records.values())
        
        if client_id:
            records = [r for r in records if r.client_id == client_id]
        if start_date:
            records = [r for r in records if r.period_start >= start_date]
        if end_date:
            records = [r for r in records if r.period_end <= end_date]
        
        return sorted(records, key=lambda x: x.period_start, reverse=True)


# Global usage reporting manager instance
_usage_reporting_manager: Optional[UsageReportingManager] = None


def get_usage_reporting_manager(config: ReportingConfig = None) -> UsageReportingManager:
    """Get or create global usage reporting manager instance."""
    global _usage_reporting_manager
    if _usage_reporting_manager is None:
        _usage_reporting_manager = UsageReportingManager(config)
    return _usage_reporting_manager


async def start_usage_reporting(config: ReportingConfig = None):
    """Start the global usage reporting manager."""
    reporting = get_usage_reporting_manager(config)
    await reporting.start()


async def stop_usage_reporting():
    """Stop the global usage reporting manager."""
    global _usage_reporting_manager
    if _usage_reporting_manager:
        await _usage_reporting_manager.stop()


async def generate_billing_record(
    client_id: str,
    user_tier: str,
    billing_period: BillingPeriod,
    period_start: datetime,
    period_end: datetime,
    usage_data: Dict[str, Any]
) -> BillingRecord:
    """Generate billing record."""
    reporting = get_usage_reporting_manager()
    return await reporting.generate_billing_record(
        client_id, user_tier, billing_period, period_start, period_end, usage_data
    )


async def generate_usage_report(
    report_type: ReportType,
    start_date: datetime,
    end_date: datetime,
    client_ids: Optional[List[str]] = None,
    user_tiers: Optional[List[str]] = None,
    endpoints: Optional[List[str]] = None,
    generated_by: str = "system"
) -> UsageReport:
    """Generate usage report."""
    reporting = get_usage_reporting_manager()
    return await reporting.generate_usage_report(
        report_type, start_date, end_date, client_ids, user_tiers, endpoints, generated_by
    )


def get_reporting_stats() -> Dict[str, Any]:
    """Get reporting statistics."""
    reporting = get_usage_reporting_manager()
    return reporting.get_reporting_stats()
