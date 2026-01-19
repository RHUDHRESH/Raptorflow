"""
Comprehensive Documentation Analytics with User Feedback and Usage Tracking

Advanced analytics system for RaptorFlow documentation:
- User behavior tracking and analysis
- Documentation usage metrics
- Feedback collection and analysis
- Content performance analytics
- User engagement insights
- A/B testing for documentation
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types for tracking."""
    PAGE_VIEW = "page_view"
    LINK_CLICK = "link_click"
    CODE_COPY = "code_copy"
    SEARCH = "search"
    FEEDBACK_SUBMIT = "feedback_submit"
    TUTORIAL_START = "tutorial_start"
    TUTORIAL_COMPLETE = "tutorial_complete"
    SDK_DOWNLOAD = "sdk_download"
    EXAMPLE_RUN = "example_run"
    BOOKMARK = "bookmark"
    SHARE = "share"


class FeedbackType(Enum):
    """Feedback types."""
    RATING = "rating"
    COMMENT = "comment"
    SUGGESTION = "suggestion"
    BUG_REPORT = "bug_report"
    IMPROVEMENT = "improvement"


@dataclass
class AnalyticsEvent:
    """Analytics event data."""
    event_id: str
    event_type: EventType
    user_id: Optional[str]
    session_id: str
    timestamp: datetime
    page_url: str
    referrer: Optional[str]
    user_agent: str
    ip_address: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserFeedback:
    """User feedback data."""
    feedback_id: str
    user_id: Optional[str]
    page_url: str
    feedback_type: FeedbackType
    rating: Optional[int] = None
    comment: Optional[str] = None
    suggestion: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentationMetrics:
    """Documentation metrics summary."""
    total_page_views: int
    unique_visitors: int
    average_session_duration: float
    bounce_rate: float
    top_pages: List[Dict[str, Any]]
    search_queries: List[Dict[str, Any]]
    feedback_summary: Dict[str, Any]
    engagement_metrics: Dict[str, Any]


class DocumentationAnalyticsConfig(BaseModel):
    """Documentation analytics configuration."""
    database_path: str = "analytics/documentation.db"
    output_dir: str = "analytics_reports"
    tracking_enabled: bool = True
    feedback_enabled: bool = True
    retention_days: int = 90
    report_frequency: str = "daily"  # daily, weekly, monthly
    enable_ab_testing: bool = True
    enable_heatmaps: bool = True


class DocumentationAnalytics:
    """Comprehensive documentation analytics system."""

    def __init__(self, config: DocumentationAnalyticsConfig):
        self.config = config
        self.db_path = Path(config.database_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()

    def _init_database(self) -> None:
        """Initialize analytics database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    page_url TEXT NOT NULL,
                    referrer TEXT,
                    user_agent TEXT,
                    ip_address TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    page_url TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    rating INTEGER,
                    comment TEXT,
                    suggestion TEXT,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    first_seen DATETIME NOT NULL,
                    last_seen DATETIME NOT NULL,
                    total_sessions INTEGER DEFAULT 0,
                    total_page_views INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    page_views INTEGER DEFAULT 0,
                    duration INTEGER,
                    referrer TEXT,
                    user_agent TEXT,
                    ip_address TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # A/B tests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ab_tests (
                    test_id TEXT PRIMARY KEY,
                    test_name TEXT NOT NULL,
                    variant TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    timestamp DATETIME NOT NULL,
                    conversion BOOLEAN DEFAULT FALSE,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)',
                'CREATE INDEX IF NOT EXISTS idx_events_page_url ON events(page_url)',
                'CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id)',
                'CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp)',
                'CREATE INDEX IF NOT EXISTS idx_feedback_page_url ON feedback(page_url)',
                'CREATE INDEX IF NOT EXISTS idx_users_last_seen ON users(last_seen)',
                'CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)'
            ]
            
            for index in indexes:
                cursor.execute(index)
            
            conn.commit()

    def track_event(self, event: AnalyticsEvent) -> None:
        """Track an analytics event."""
        if not self.config.tracking_enabled:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (
                    event_id, event_type, user_id, session_id, timestamp,
                    page_url, referrer, user_agent, ip_address, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.event_type.value,
                event.user_id,
                event.session_id,
                event.timestamp,
                event.page_url,
                event.referrer,
                event.user_agent,
                event.ip_address,
                json.dumps(event.metadata)
            ))
            
            # Update user data
            if event.user_id:
                self._update_user_data(event.user_id, event.timestamp)
            
            # Update session data
            self._update_session_data(event.session_id, event.timestamp, event.page_url)
            
            conn.commit()

    def track_feedback(self, feedback: UserFeedback) -> None:
        """Track user feedback."""
        if not self.config.feedback_enabled:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback (
                    feedback_id, user_id, page_url, feedback_type,
                    rating, comment, suggestion, timestamp, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id,
                feedback.user_id,
                feedback.page_url,
                feedback.feedback_type.value,
                feedback.rating,
                feedback.comment,
                feedback.suggestion,
                feedback.timestamp,
                json.dumps(feedback.metadata)
            ))
            
            conn.commit()

    def _update_user_data(self, user_id: str, timestamp: datetime) -> None:
        """Update user analytics data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing user
                cursor.execute('''
                    UPDATE users SET 
                        last_seen = ?,
                        total_page_views = total_page_views + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (timestamp, user_id))
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO users (
                        user_id, first_seen, last_seen, total_page_views
                    ) VALUES (?, ?, ?, 1)
                ''', (user_id, timestamp, timestamp))

    def _update_session_data(self, session_id: str, timestamp: datetime, page_url: str) -> None:
        """Update session analytics data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if session exists
            cursor.execute('SELECT start_time FROM sessions WHERE session_id = ?', (session_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing session
                cursor.execute('''
                    UPDATE sessions SET 
                        end_time = ?,
                        page_views = page_views + 1,
                        duration = (julianday(?) - julianday(start_time)) * 86400
                    WHERE session_id = ?
                ''', (timestamp, timestamp, session_id))
            else:
                # Create new session
                cursor.execute('''
                    INSERT INTO sessions (
                        session_id, start_time, end_time, page_views
                    ) VALUES (?, ?, ?, 1)
                ''', (session_id, timestamp, timestamp))

    def get_metrics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> DocumentationMetrics:
        """Get documentation metrics."""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            # Total page views
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM events 
                WHERE event_type = ? AND timestamp BETWEEN ? AND ?
            ''', (EventType.PAGE_VIEW.value, start_date, end_date))
            total_page_views = cursor.fetchone()[0]
            
            # Unique visitors
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM events 
                WHERE timestamp BETWEEN ? AND ? AND user_id IS NOT NULL
            ''', (start_date, end_date))
            unique_visitors = cursor.fetchone()[0]
            
            # Average session duration
            cursor.execute('''
                SELECT AVG(duration) FROM sessions 
                WHERE start_time BETWEEN ? AND ? AND duration IS NOT NULL
            ''', (start_date, end_date))
            avg_duration = cursor.fetchone()[0] or 0
            
            # Bounce rate (sessions with only 1 page view)
            cursor.execute('''
                SELECT COUNT(*) FROM sessions 
                WHERE start_time BETWEEN ? AND ? AND page_views = 1
            ''', (start_date, end_date))
            bounce_sessions = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM sessions 
                WHERE start_time BETWEEN ? AND ?
            ''', (start_date, end_date))
            total_sessions = cursor.fetchone()[0]
            
            bounce_rate = (bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # Top pages
            cursor.execute('''
                SELECT page_url, COUNT(*) as views 
                FROM events 
                WHERE event_type = ? AND timestamp BETWEEN ? AND ?
                GROUP BY page_url 
                ORDER BY views DESC 
                LIMIT 10
            ''', (EventType.PAGE_VIEW.value, start_date, end_date))
            top_pages = [{'page': row[0], 'views': row[1]} for row in cursor.fetchall()]
            
            # Search queries
            cursor.execute('''
                SELECT metadata, COUNT(*) as count 
                FROM events 
                WHERE event_type = ? AND timestamp BETWEEN ? AND ?
                GROUP BY metadata 
                ORDER BY count DESC 
                LIMIT 10
            ''', (EventType.SEARCH.value, start_date, end_date))
            
            search_queries = []
            for row in cursor.fetchall():
                try:
                    metadata = json.loads(row[0])
                    query = metadata.get('query', '')
                    search_queries.append({'query': query, 'count': row[1]})
                except:
                    continue
            
            # Feedback summary
            cursor.execute('''
                SELECT AVG(rating), COUNT(*) FROM feedback 
                WHERE timestamp BETWEEN ? AND ? AND rating IS NOT NULL
            ''', (start_date, end_date))
            feedback_row = cursor.fetchone()
            avg_rating = feedback_row[0] or 0
            feedback_count = feedback_row[1] or 0
            
            # Engagement metrics
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) as code_copies,
                    SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) as link_clicks,
                    SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) as tutorial_starts,
                    SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) as tutorial_completes
                FROM events 
                WHERE timestamp BETWEEN ? AND ?
            ''', (
                EventType.CODE_COPY.value,
                EventType.LINK_CLICK.value,
                EventType.TUTORIAL_START.value,
                EventType.TUTORIAL_COMPLETE.value,
                start_date,
                end_date
            ))
            
            engagement_row = cursor.fetchone()
            engagement_metrics = {
                'code_copies': engagement_row[0] or 0,
                'link_clicks': engagement_row[1] or 0,
                'tutorial_starts': engagement_row[2] or 0,
                'tutorial_completes': engagement_row[3] or 0,
                'tutorial_completion_rate': (
                    (engagement_row[3] or 0) / (engagement_row[2] or 1) * 100
                )
            }
            
            return DocumentationMetrics(
                total_page_views=total_page_views,
                unique_visitors=unique_visitors,
                average_session_duration=avg_duration,
                bounce_rate=bounce_rate,
                top_pages=top_pages,
                search_queries=search_queries,
                feedback_summary={
                    'average_rating': avg_rating,
                    'total_feedback': feedback_count
                },
                engagement_metrics=engagement_metrics
            )

    def get_page_analytics(self, page_url: str, days: int = 30) -> Dict[str, Any]:
        """Get detailed analytics for a specific page."""
        start_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Page views over time
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as views
                FROM events 
                WHERE event_type = ? AND page_url = ? AND timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (EventType.PAGE_VIEW.value, page_url, start_date))
            
            views_over_time = [{'date': row[0], 'views': row[1]} for row in cursor.fetchall()]
            
            # User engagement
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) as code_copies,
                    SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) as link_clicks,
                    SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) as feedback_submits
                FROM events 
                WHERE page_url = ? AND timestamp >= ?
            ''', (
                EventType.CODE_COPY.value,
                EventType.LINK_CLICK.value,
                EventType.FEEDBACK_SUBMIT.value,
                page_url,
                start_date
            ))
            
            engagement_row = cursor.fetchone()
            
            # Feedback for this page
            cursor.execute('''
                SELECT rating, comment, suggestion, timestamp
                FROM feedback 
                WHERE page_url = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (page_url, start_date))
            
            feedback_data = []
            for row in cursor.fetchall():
                feedback_data.append({
                    'rating': row[0],
                    'comment': row[1],
                    'suggestion': row[2],
                    'timestamp': row[3]
                })
            
            return {
                'page_url': page_url,
                'views_over_time': views_over_time,
                'engagement': {
                    'code_copies': engagement_row[0] or 0,
                    'link_clicks': engagement_row[1] or 0,
                    'feedback_submits': engagement_row[2] or 0
                },
                'feedback': feedback_data
            }

    def generate_usage_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive usage report."""
        metrics = self.get_metrics()
        
        # Get additional insights
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User retention
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT user_id) as new_users,
                    COUNT(DISTINCT CASE 
                        WHEN first_seen < date('now', '-30 days') THEN user_id 
                    END) as returning_users
                FROM users 
                WHERE last_seen >= date('now', '-{} days')
            '''.format(days))
            
            retention_row = cursor.fetchone()
            
            # Popular content types
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN page_url LIKE '%/api/%' THEN 'API Documentation'
                        WHEN page_url LIKE '%/tutorial%' THEN 'Tutorials'
                        WHEN page_url LIKE '%/guide%' THEN 'Guides'
                        WHEN page_url LIKE '%/example%' THEN 'Examples'
                        ELSE 'Other'
                    END as content_type,
                    COUNT(*) as views
                FROM events 
                WHERE event_type = ? AND timestamp >= date('now', '-{} days')
                GROUP BY content_type
                ORDER BY views DESC
            '''.format(days), (EventType.PAGE_VIEW.value,))
            
            content_types = [{'type': row[0], 'views': row[1]} for row in cursor.fetchall()]
            
            # Device types (simplified)
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN user_agent LIKE '%Mobile%' THEN 'Mobile'
                        WHEN user_agent LIKE '%Tablet%' THEN 'Tablet'
                        ELSE 'Desktop'
                    END as device_type,
                    COUNT(*) as sessions
                FROM sessions 
                WHERE start_time >= date('now', '-{} days')
                GROUP BY device_type
                ORDER BY sessions DESC
            '''.format(days))
            
            devices = [{'device': row[0], 'sessions': row[1]} for row in cursor.fetchall()]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'metrics': metrics,
            'user_retention': {
                'new_users': retention_row[0] or 0,
                'returning_users': retention_row[1] or 0,
                'retention_rate': (
                    (retention_row[1] or 0) / (retention_row[0] or 1) * 100
                )
            },
            'content_types': content_types,
            'devices': devices,
            'insights': self._generate_insights(metrics)
        }

    def _generate_insights(self, metrics: DocumentationMetrics) -> List[str]:
        """Generate insights from metrics."""
        insights = []
        
        if metrics.bounce_rate > 70:
            insights.append(f"High bounce rate ({metrics.bounce_rate:.1f}%) - consider improving content engagement")
        
        if metrics.average_session_duration < 60:
            insights.append(f"Short average session duration ({metrics.average_session_duration:.1f}s) - content may need improvement")
        
        if metrics.feedback_summary['average_rating'] < 3.0:
            insights.append("Low user satisfaction rating - review feedback for improvement areas")
        
        if metrics.engagement_metrics['tutorial_completion_rate'] < 50:
            insights.append("Low tutorial completion rate - consider simplifying tutorials")
        
        if metrics.top_pages:
            top_page = metrics.top_pages[0]
            if top_page['views'] > metrics.total_page_views * 0.3:
                insights.append(f"Page '{top_page['page']}' dominates traffic - ensure it's well maintained")
        
        return insights

    def create_visualizations(self, metrics: DocumentationMetrics) -> Dict[str, str]:
        """Create visualization charts."""
        charts = {}
        
        # Page views chart
        if metrics.top_pages:
            fig = px.bar(
                x=[page['page'] for page in metrics.top_pages],
                y=[page['views'] for page in metrics.top_pages],
                title="Top Pages by Views"
            )
            charts['top_pages'] = fig.to_html(include_plotlyjs='cdn')
        
        # Engagement metrics chart
        engagement_data = [
            {'metric': 'Code Copies', 'value': metrics.engagement_metrics['code_copies']},
            {'metric': 'Link Clicks', 'value': metrics.engagement_metrics['link_clicks']},
            {'metric': 'Tutorial Starts', 'value': metrics.engagement_metrics['tutorial_starts']},
            {'metric': 'Tutorial Completes', 'value': metrics.engagement_metrics['tutorial_completes']}
        ]
        
        fig = px.bar(
            x=[item['metric'] for item in engagement_data],
            y=[item['value'] for item in engagement_data],
            title="User Engagement Metrics"
        )
        charts['engagement'] = fig.to_html(include_plotlyjs='cdn')
        
        return charts

    def export_data(self, format: str = "json", days: int = 30) -> str:
        """Export analytics data."""
        if format.lower() == "json":
            report = self.generate_usage_report(days)
            return json.dumps(report, indent=2, default=str)
        
        elif format.lower() == "csv":
            # Export events to CSV
            start_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query('''
                    SELECT event_type, user_id, session_id, timestamp, page_url, referrer, metadata
                    FROM events 
                    WHERE timestamp >= ?
                    ORDER BY timestamp
                ''', conn, params=(start_date,))
            
            return df.to_csv(index=False)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def cleanup_old_data(self) -> None:
        """Clean up old analytics data."""
        cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clean old events
            cursor.execute('DELETE FROM events WHERE timestamp < ?', (cutoff_date,))
            
            # Clean old feedback
            cursor.execute('DELETE FROM feedback WHERE timestamp < ?', (cutoff_date,))
            
            # Clean old sessions
            cursor.execute('DELETE FROM sessions WHERE start_time < ?', (cutoff_date,))
            
            conn.commit()
        
        logger.info(f"Cleaned up analytics data older than {cutoff_date}")

    def save_report(self, report: Dict[str, Any]) -> None:
        """Save analytics report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON report
        json_file = Path(self.config.output_dir) / f"analytics_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Analytics report saved: {json_file}")
        
        # Save HTML report
        html_file = Path(self.config.output_dir) / f"analytics_report_{timestamp}.html"
        html_content = self._generate_html_report(report)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Analytics HTML report saved: {html_file}")

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML analytics report."""
        metrics = report['metrics']
        
        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Analytics Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body class="bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8">Documentation Analytics Report</h1>
        
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Key Metrics</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600">{metrics.total_page_views:,}</div>
                    <div class="text-sm text-gray-600">Total Page Views</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-green-600">{metrics.unique_visitors:,}</div>
                    <div class="text-sm text-gray-600">Unique Visitors</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600">{metrics.average_session_duration:.1f}s</div>
                    <div class="text-sm text-gray-600">Avg Session Duration</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-orange-600">{metrics.bounce_rate:.1f}%</div>
                    <div class="text-sm text-gray-600">Bounce Rate</div>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">User Engagement</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                    <div class="text-2xl font-bold text-indigo-600">{metrics.engagement_metrics['code_copies']:,}</div>
                    <div class="text-sm text-gray-600">Code Copies</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-teal-600">{metrics.engagement_metrics['link_clicks']:,}</div>
                    <div class="text-sm text-gray-600">Link Clicks</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-pink-600">{metrics.engagement_metrics['tutorial_starts']:,}</div>
                    <div class="text-sm text-gray-600">Tutorial Starts</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-red-600">{metrics.engagement_metrics['tutorial_completion_rate']:.1f}%</div>
                    <div class="text-sm text-gray-600">Tutorial Completion</div>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Top Pages</h2>
            <div class="space-y-2">
                {self._generate_top_pages_html(metrics.top_pages)}
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">User Feedback</h2>
            <div class="grid grid-cols-2 gap-4">
                <div class="text-center">
                    <div class="text-2xl font-bold text-yellow-600">
                        {metrics.feedback_summary['average_rating']:.1f}/5.0
                    </div>
                    <div class="text-sm text-gray-600">Average Rating</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-cyan-600">
                        {metrics.feedback_summary['total_feedback']:,}
                    </div>
                    <div class="text-sm text-gray-600">Total Feedback</div>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">Insights</h2>
            <div class="space-y-2">
                {self._generate_insights_html(report.get('insights', []))}
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        return html

    def _generate_top_pages_html(self, top_pages: List[Dict[str, Any]]) -> str:
        """Generate top pages HTML."""
        if not top_pages:
            return '<p class="text-gray-600">No page data available</p>'
        
        items = []
        for page in top_pages[:10]:
            items.append(f'''
            <div class="flex justify-between items-center py-2 border-b">
                <span class="text-sm font-medium truncate">{page['page']}</span>
                <span class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {page['views']:,} views
                </span>
            </div>
            ''')
        
        return ''.join(items)

    def _generate_insights_html(self, insights: List[str]) -> str:
        """Generate insights HTML."""
        if not insights:
            return '<p class="text-gray-600">No insights available</p>'
        
        items = []
        for insight in insights:
            items.append(f'''
            <div class="flex items-start space-x-2">
                <span class="text-yellow-500 mt-1">💡</span>
                <span class="text-sm text-gray-700">{insight}</span>
            </div>
            ''')
        
        return ''.join(items)


# CLI usage
if __name__ == "__main__":
    import argparse
    import uuid
    
    parser = argparse.ArgumentParser(description="Documentation analytics")
    parser.add_argument("--database", default="analytics/documentation.db", help="Database path")
    parser.add_argument("--output-dir", default="analytics_reports", help="Output directory")
    parser.add_argument("--days", type=int, default=30, help="Report period in days")
    parser.add_argument("--export", choices=["json", "csv"], help="Export format")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old data")
    
    args = parser.parse_args()
    
    # Create configuration
    config = DocumentationAnalyticsConfig(
        database_path=args.database,
        output_dir=args.output_dir
    )
    
    # Initialize analytics
    analytics = DocumentationAnalytics(config)
    
    if args.cleanup:
        analytics.cleanup_old_data()
        print("Old data cleaned up")
    elif args.export:
        data = analytics.export_data(args.export, args.days)
        print(data)
    else:
        # Generate and save report
        report = analytics.generate_usage_report(args.days)
        analytics.save_report(report)
        
        # Print summary
        metrics = report['metrics']
        print(f"\nDocumentation Analytics Summary ({args.days} days):")
        print(f"Page Views: {metrics.total_page_views:,}")
        print(f"Unique Visitors: {metrics.unique_visitors:,}")
        print(f"Avg Session Duration: {metrics.average_session_duration:.1f}s")
        print(f"Bounce Rate: {metrics.bounce_rate:.1f}%")
        print(f"Average Rating: {metrics.feedback_summary['average_rating']:.1f}/5.0")
