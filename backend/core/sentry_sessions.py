"""
Comprehensive Sentry Session Management for Raptorflow Backend
=============================================================

Advanced user session tracking with error correlation, session analytics,
and intelligent session management for production debugging.

Features:
- User session tracking and correlation
- Session-based error grouping
- Session health monitoring
- User journey reconstruction
- Session performance analytics
- Cross-session error patterns
- Session lifecycle management
"""

import hashlib
import json
import logging
import os
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

try:
    from sentry_sdk import (
        add_breadcrumb,
        configure_scope,
        continue_trace,
        get_current_span,
        set_context,
        set_tag,
        set_user,
    )

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from sentry_integration import get_sentry_manager


class SessionStatus(str, Enum):
    """Session status types."""

    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    ERROR = "error"


class SessionType(str, Enum):
    """Session types."""

    WEB = "web"
    API = "api"
    MOBILE = "mobile"
    SYSTEM = "system"
    BACKGROUND = "background"


@dataclass
class SessionInfo:
    """Session information structure."""

    session_id: str
    user_id: Optional[str] = None
    session_type: SessionType = SessionType.WEB
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if session is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def is_idle(self, idle_timeout_minutes: int = 30) -> bool:
        """Check if session is idle."""
        idle_cutoff = datetime.now(timezone.utc) - timedelta(
            minutes=idle_timeout_minutes
        )
        return self.last_activity < idle_cutoff


@dataclass
class SessionEvent:
    """Session event structure."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class SessionError:
    """Session error correlation structure."""

    error_id: str
    session_id: str
    timestamp: datetime
    error_type: str
    error_message: str
    severity: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_time: Optional[float] = None
    user_impacted: bool = False


@dataclass
class SessionMetrics:
    """Session performance metrics."""

    session_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_errors: int = 0
    avg_response_time_ms: float = 0.0
    session_duration_minutes: float = 0.0
    error_rate: float = 0.0
    bounce_rate: float = 0.0
    conversion_events: int = 0


class SentrySessionManager:
    """
    Comprehensive session management with intelligent correlation
    and analytics capabilities.
    """

    def __init__(self, default_session_ttl_minutes: int = 60):
        self.sentry_manager = get_sentry_manager()
        self._logger = logging.getLogger(__name__)
        self._default_ttl = default_session_ttl_minutes

        # Session storage
        self._sessions: Dict[str, SessionInfo] = {}
        self._session_events: Dict[str, List[SessionEvent]] = {}
        self._session_errors: Dict[str, List[SessionError]] = {}
        self._user_sessions: Dict[str, List[str]] = {}  # user_id -> session_ids

        # Session analytics
        self._session_metrics: Dict[str, SessionMetrics] = {}
        self._active_sessions: Dict[str, str] = {}  # thread_id -> session_id

        # Thread safety
        self._lock = threading.Lock()

        # Initialize cleanup task
        self._init_cleanup_task()

    def _init_cleanup_task(self) -> None:
        """Initialize session cleanup task."""

        def cleanup_sessions():
            while True:
                try:
                    time.sleep(300)  # 5 minutes
                    self._cleanup_expired_sessions()
                except Exception as e:
                    self._logger.error(f"Error in session cleanup: {e}")

        cleanup_thread = threading.Thread(target=cleanup_sessions, daemon=True)
        cleanup_thread.start()

    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        with self._lock:
            expired_sessions = []

            for session_id, session in self._sessions.items():
                if session.is_expired() or session.is_idle():
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                self._terminate_session(session_id, "expired")

    def create_session(
        self,
        user_id: Optional[str] = None,
        session_type: SessionType = SessionType.WEB,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        ttl_minutes: Optional[int] = None,
    ) -> str:
        """
        Create a new session.

        Args:
            user_id: User ID for the session
            session_type: Type of session
            ip_address: Client IP address
            user_agent: User agent string
            endpoint: Starting endpoint
            metadata: Additional session metadata
            tags: Session tags
            ttl_minutes: Time to live in minutes

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        ttl = ttl_minutes or self._default_ttl
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl)

        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            session_type=session_type,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            metadata=metadata or {},
            tags=tags or {},
            expires_at=expires_at,
        )

        with self._lock:
            self._sessions[session_id] = session
            self._session_events[session_id] = []
            self._session_errors[session_id] = []
            self._session_metrics[session_id] = SessionMetrics(session_id=session_id)

            if user_id:
                if user_id not in self._user_sessions:
                    self._user_sessions[user_id] = []
                self._user_sessions[user_id].append(session_id)

        # Set Sentry user context
        if self.sentry_manager.is_enabled():
            self._set_sentry_user_context(session)

        # Add session creation event
        self._add_session_event(
            session_id,
            "session_created",
            {
                "user_id": user_id,
                "session_type": session_type.value,
                "ip_address": ip_address,
                "endpoint": endpoint,
            },
        )

        # Set as active for current thread
        thread_id = threading.get_ident()
        self._active_sessions[thread_id] = session_id

        self._logger.info(f"Created session {session_id} for user {user_id}")

        return session_id

    def _set_sentry_user_context(self, session: SessionInfo) -> None:
        """Set Sentry user context from session."""
        try:
            user_data = {
                "id": session.user_id,
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
            }

            # Remove None values
            user_data = {k: v for k, v in user_data.items() if v is not None}

            set_user(user_data)

            # Set session tags
            configure_scope(
                lambda scope: scope.set_tag("session_id", session.session_id)
            )
            configure_scope(
                lambda scope: scope.set_tag("session_type", session.session_type.value)
            )

            if session.user_id:
                configure_scope(lambda scope: scope.set_tag("user_id", session.user_id))

            # Set session context
            configure_scope(
                lambda scope: scope.set_context(
                    "session",
                    {
                        "session_id": session.session_id,
                        "user_id": session.user_id,
                        "session_type": session.session_type.value,
                        "status": session.status.value,
                        "created_at": session.created_at.isoformat(),
                        "last_activity": session.last_activity.isoformat(),
                        "ip_address": session.ip_address,
                        "endpoint": session.endpoint,
                        "metadata": session.metadata,
                    },
                )
            )

        except Exception as e:
            self._logger.error(f"Failed to set Sentry user context: {e}")

    def get_current_session(self) -> Optional[SessionInfo]:
        """Get the current session for the calling thread."""
        thread_id = threading.get_ident()
        session_id = self._active_sessions.get(thread_id)

        if session_id:
            with self._lock:
                return self._sessions.get(session_id)

        return None

    def update_session(
        self,
        session_id: str,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Update session information.

        Args:
            session_id: Session ID to update
            endpoint: New endpoint
            metadata: Additional metadata to merge
            tags: Tags to merge

        Returns:
            True if updated successfully
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Update session
            session.last_activity = datetime.now(timezone.utc)
            session.status = SessionStatus.ACTIVE

            if endpoint:
                session.endpoint = endpoint

            if metadata:
                session.metadata.update(metadata)

            if tags:
                session.tags.update(tags)

            # Update Sentry context
            if self.sentry_manager.is_enabled():
                self._set_sentry_user_context(session)

            # Add activity event
            self._add_session_event(
                session_id,
                "session_updated",
                {
                    "endpoint": endpoint,
                    "metadata": metadata,
                    "tags": tags,
                },
            )

            return True

    def track_session_error(
        self,
        error_id: str,
        session_id: Optional[str] = None,
        error_type: str = "unknown",
        error_message: str = "",
        severity: str = "medium",
        context: Optional[Dict[str, Any]] = None,
        recovery_time: Optional[float] = None,
        user_impacted: bool = False,
    ) -> bool:
        """
        Track an error within a session context.

        Args:
            error_id: Error ID from Sentry
            session_id: Session ID (optional, will use current if not provided)
            error_type: Type of error
            error_message: Error message
            severity: Error severity
            context: Additional error context
            recovery_time: Time to recover from error
            user_impacted: Whether user was impacted

        Returns:
            True if tracked successfully
        """
        # Get session ID
        if not session_id:
            current_session = self.get_current_session()
            session_id = current_session.session_id if current_session else None

        if not session_id:
            return False

        session_error = SessionError(
            error_id=error_id,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            context=context or {},
            recovery_time=recovery_time,
            user_impacted=user_impacted,
        )

        with self._lock:
            if session_id in self._session_errors:
                self._session_errors[session_id].append(session_error)

                # Update session metrics
                if session_id in self._session_metrics:
                    self._session_metrics[session_id].total_errors += 1

        # Add error event to session
        self._add_session_event(
            session_id,
            "error_occurred",
            {
                "error_id": error_id,
                "error_type": error_type,
                "severity": severity,
                "user_impacted": user_impacted,
                "recovery_time": recovery_time,
            },
        )

        # Update session status if user impacted
        if user_impacted:
            self.update_session_status(session_id, SessionStatus.ERROR)

        return True

    def track_session_request(
        self,
        session_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: str = "GET",
        status_code: int = 200,
        response_time_ms: float = 0.0,
        success: bool = True,
    ) -> bool:
        """
        Track a request within a session.

        Args:
            session_id: Session ID (optional, will use current if not provided)
            endpoint: Request endpoint
            method: HTTP method
            status_code: Response status code
            response_time_ms: Response time in milliseconds
            success: Whether request was successful

        Returns:
            True if tracked successfully
        """
        # Get session ID
        if not session_id:
            current_session = self.get_current_session()
            session_id = current_session.session_id if current_session else None

        if not session_id:
            return False

        with self._lock:
            if session_id in self._session_metrics:
                metrics = self._session_metrics[session_id]
                metrics.total_requests += 1

                if success:
                    metrics.successful_requests += 1
                else:
                    metrics.failed_requests += 1

                # Update average response time
                if metrics.total_requests == 1:
                    metrics.avg_response_time_ms = response_time_ms
                else:
                    total_time = (
                        metrics.avg_response_time_ms * (metrics.total_requests - 1)
                        + response_time_ms
                    )
                    metrics.avg_response_time_ms = total_time / metrics.total_requests

                # Update error rate
                metrics.error_rate = metrics.failed_requests / metrics.total_requests

        # Add request event to session
        self._add_session_event(
            session_id,
            "request_completed",
            {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "success": success,
            },
        )

        # Update session activity
        self.update_session(session_id, endpoint=endpoint)

        return True

    def track_conversion_event(
        self,
        session_id: Optional[str] = None,
        event_name: str = "conversion",
        event_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track a conversion event within a session.

        Args:
            session_id: Session ID (optional, will use current if not provided)
            event_name: Name of conversion event
            event_data: Additional event data

        Returns:
            True if tracked successfully
        """
        # Get session ID
        if not session_id:
            current_session = self.get_current_session()
            session_id = current_session.session_id if current_session else None

        if not session_id:
            return False

        with self._lock:
            if session_id in self._session_metrics:
                self._session_metrics[session_id].conversion_events += 1

        # Add conversion event to session
        self._add_session_event(
            session_id,
            "conversion_event",
            {
                "event_name": event_name,
                "event_data": event_data or {},
            },
        )

        return True

    def _add_session_event(
        self, session_id: str, event_type: str, data: Dict[str, Any]
    ) -> None:
        """Add an event to the session timeline."""
        event = SessionEvent(session_id=session_id, event_type=event_type, data=data)

        with self._lock:
            if session_id in self._session_events:
                self._session_events[session_id].append(event)

        # Add breadcrumb to Sentry
        if self.sentry_manager.is_enabled():
            add_breadcrumb(
                message=f"Session {event_type}",
                level="info",
                category="session",
                data={"session_id": session_id, "event_type": event_type, **data},
            )

    def update_session_status(self, session_id: str, status: SessionStatus) -> bool:
        """Update session status."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            old_status = session.status
            session.status = status

            # Add status change event
            self._add_session_event(
                session_id,
                "status_changed",
                {
                    "old_status": old_status.value,
                    "new_status": status.value,
                },
            )

            return True

    def terminate_session(self, session_id: str, reason: str = "manual") -> bool:
        """Terminate a session."""
        return self._terminate_session(session_id, reason)

    def _terminate_session(self, session_id: str, reason: str) -> bool:
        """Internal session termination."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Update status
            session.status = SessionStatus.TERMINATED

            # Calculate final metrics
            if session_id in self._session_metrics:
                metrics = self._session_metrics[session_id]
                metrics.session_duration_minutes = (
                    datetime.now(timezone.utc) - session.created_at
                ).total_seconds() / 60

                # Calculate bounce rate (single request sessions)
                if metrics.total_requests == 1:
                    metrics.bounce_rate = 1.0
                else:
                    # Simple bounce rate: sessions with 1-2 requests
                    metrics.bounce_rate = 1.0 if metrics.total_requests <= 2 else 0.0

            # Add termination event
            self._add_session_event(
                session_id,
                "session_terminated",
                {
                    "reason": reason,
                    "duration_minutes": (
                        datetime.now(timezone.utc) - session.created_at
                    ).total_seconds()
                    / 60,
                },
            )

            # Remove from active sessions
            for thread_id, active_session_id in list(self._active_sessions.items()):
                if active_session_id == session_id:
                    del self._active_sessions[thread_id]

            self._logger.info(f"Terminated session {session_id} (reason: {reason})")

            return True

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information."""
        with self._lock:
            return self._sessions.get(session_id)

    def get_session_events(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[SessionEvent]:
        """Get session events."""
        with self._lock:
            events = self._session_events.get(session_id, [])
            if limit:
                return events[-limit:]
            return events

    def get_session_errors(self, session_id: str) -> List[SessionError]:
        """Get session errors."""
        with self._lock:
            return self._session_errors.get(session_id, [])

    def get_session_metrics(self, session_id: str) -> Optional[SessionMetrics]:
        """Get session metrics."""
        with self._lock:
            return self._session_metrics.get(session_id)

    def get_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """Get all sessions for a user."""
        with self._lock:
            session_ids = self._user_sessions.get(user_id, [])
            return [
                self._sessions.get(sid) for sid in session_ids if sid in self._sessions
            ]

    def get_active_sessions(self) -> List[SessionInfo]:
        """Get all active sessions."""
        with self._lock:
            return [
                session
                for session in self._sessions.values()
                if session.status == SessionStatus.ACTIVE and not session.is_expired()
            ]

    def get_session_analytics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Get session analytics for the specified time window.

        Args:
            time_window_hours: Time window in hours

        Returns:
            Session analytics dictionary
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)

        with self._lock:
            # Filter sessions within time window
            recent_sessions = [
                session
                for session in self._sessions.values()
                if session.created_at > cutoff_time
            ]

            # Basic metrics
            total_sessions = len(recent_sessions)
            active_sessions = len(
                [s for s in recent_sessions if s.status == SessionStatus.ACTIVE]
            )
            expired_sessions = len(
                [s for s in recent_sessions if s.status == SessionStatus.EXPIRED]
            )
            terminated_sessions = len(
                [s for s in recent_sessions if s.status == SessionStatus.TERMINATED]
            )
            error_sessions = len(
                [s for s in recent_sessions if s.status == SessionStatus.ERROR]
            )

            # Session type distribution
            type_distribution = {}
            for session in recent_sessions:
                session_type = session.session_type.value
                type_distribution[session_type] = (
                    type_distribution.get(session_type, 0) + 1
                )

            # Calculate average session duration
            durations = []
            for session in recent_sessions:
                if session.status in [SessionStatus.TERMINATED, SessionStatus.EXPIRED]:
                    duration = (
                        session.last_activity - session.created_at
                    ).total_seconds() / 60
                    durations.append(duration)

            avg_duration = sum(durations) / len(durations) if durations else 0

            # Error analysis
            total_errors = sum(len(errors) for errors in self._session_errors.values())
            sessions_with_errors = len(
                [
                    sid
                    for sid, errors in self._session_errors.items()
                    if errors
                    and sid in self._sessions
                    and self._sessions[sid].created_at > cutoff_time
                ]
            )

            # Performance metrics
            performance_metrics = []
            for session_id, metrics in self._session_metrics.items():
                session = self._sessions.get(session_id)
                if session and session.created_at > cutoff_time:
                    performance_metrics.append(metrics)

            if performance_metrics:
                avg_response_time = sum(
                    m.avg_response_time_ms for m in performance_metrics
                ) / len(performance_metrics)
                avg_error_rate = sum(m.error_rate for m in performance_metrics) / len(
                    performance_metrics
                )
                total_conversions = sum(
                    m.conversion_events for m in performance_metrics
                )
            else:
                avg_response_time = 0
                avg_error_rate = 0
                total_conversions = 0

            return {
                "time_window_hours": time_window_hours,
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "expired_sessions": expired_sessions,
                "terminated_sessions": terminated_sessions,
                "error_sessions": error_sessions,
                "session_type_distribution": type_distribution,
                "avg_session_duration_minutes": avg_duration,
                "total_errors": total_errors,
                "sessions_with_errors": sessions_with_errors,
                "error_rate_per_session": (
                    sessions_with_errors / total_sessions if total_sessions > 0 else 0
                ),
                "avg_response_time_ms": avg_response_time,
                "avg_error_rate": avg_error_rate,
                "total_conversions": total_conversions,
                "conversion_rate": (
                    total_conversions / total_sessions if total_sessions > 0 else 0
                ),
            }


# Context manager for session management
@contextmanager
def session_context(
    user_id: Optional[str] = None, session_type: SessionType = SessionType.WEB, **kwargs
):
    """Context manager for automatic session management."""
    session_manager = SentrySessionManager()
    session_id = session_manager.create_session(
        user_id=user_id, session_type=session_type, **kwargs
    )

    try:
        yield session_id
    finally:
        session_manager.terminate_session(session_id, "context_exit")


# Global session manager instance
_session_manager: Optional[SentrySessionManager] = None


def get_session_manager() -> SentrySessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SentrySessionManager()
    return _session_manager
