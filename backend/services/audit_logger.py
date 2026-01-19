"""
Secure Audit Logging System for PhonePe Integration
Implements comprehensive logging with sensitive data masking and compliance
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import gzip
from pathlib import Path
import uuid
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class EventType(Enum):
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_STATUS_CHECK = "payment_status_check"
    WEBHOOK_RECEIVED = "webhook_received"
    WEBHOOK_PROCESSED = "webhook_processed"
    AUTH_TOKEN_REQUESTED = "auth_token_requested"
    AUTH_TOKEN_REFRESHED = "auth_token_refreshed"
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    API_CALL_MADE = "api_call_made"
    CONFIGURATION_CHANGED = "configuration_changed"
    SYSTEM_ERROR = "system_error"

@dataclass
class AuditEvent:
    """Audit event structure"""
    event_id: str
    timestamp: datetime
    event_type: EventType
    level: LogLevel
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    transaction_id: Optional[str] = None
    merchant_order_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    security_context: Optional[Dict[str, Any]] = None
    compliance_flags: Optional[List[str]] = None

class DataMasker:
    """Sensitive data masking for audit logs"""
    
    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        # Credit card numbers
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', lambda m: f"****-****-****-{m.group()[-4:]}"),
        # Phone numbers (Indian format)
        (r'\b(?:\+91[-\s]?|0)?[6-9]\d{9}\b', lambda m: f"******{m.group()[-4:]}"),
        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', lambda m: f"{m.group()[:3]}***@{m.group().split('@')[1]}"),
        # API keys and tokens
        (r'\b[A-Za-z0-9]{32,}\b', lambda m: f"{m.group()[:8]}{'*' * (len(m.group()) - 12)}{m.group()[-4:]}"),
        # PAN numbers (Indian)
        (r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', lambda m: f"*****{m.group()[-4:]}"),
        # Aadhaar numbers (Indian)
        (r'\b\d{4}\s?\d{4}\s?\d{4}\b', lambda m: f"****-****-{m.group()[-4:]}"),
        # Bank account numbers
        (r'\b\d{10,18}\b', lambda m: f"****{m.group()[-4:]}"),
    ]

    # Fields to completely mask
    COMPLETELY_MASKED_FIELDS = {
        'password', 'secret', 'key', 'token', 'authorization', 'signature',
        'client_secret', 'access_token', 'refresh_token', 'api_key',
        'credit_card', 'card_number', 'cvv', 'pin', 'ssn', 'pan', 'aadhaar'
    }

    @classmethod
    def mask_data(cls, data: Any, field_path: str = "") -> Any:
        """Recursively mask sensitive data"""
        if isinstance(data, dict):
            masked_dict = {}
            for key, value in data.items():
                current_path = f"{field_path}.{key}" if field_path else key
                masked_dict[key] = cls.mask_data(value, current_path)
            return masked_dict
        elif isinstance(data, list):
            return [cls.mask_data(item, f"{field_path}[]") for item in data]
        elif isinstance(data, str):
            # Check if field name suggests complete masking
            if any(field in field_path.lower() for field in cls.COMPLETELY_MASKED_FIELDS):
                return "*" * min(len(data), 12)
            
            # Apply pattern-based masking
            masked_data = data
            for pattern, mask_func in cls.SENSITIVE_PATTERNS:
                masked_data = re.sub(pattern, mask_func, masked_data)
            
            return masked_data
        else:
            return data

class AuditLogger:
    """Enhanced audit logger with security and compliance features"""
    
    def __init__(self, log_dir: str = "audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Encryption for log files
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Log rotation settings
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_files = 30  # Keep 30 days of logs
        
        # Compliance settings
        self.retention_days = 2555  # 7 years for financial records
        self.compliance_regions = ["IN", "US", "EU"]  # Supported compliance regions
        
        # Async logging queue
        self.log_queue = asyncio.Queue()
        self._logging_task = None

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for log files"""
        key_file = self.log_dir / "audit_key.enc"
        
        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()
        
        # Generate new key
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        
        # Set secure permissions
        key_file.chmod(0o600)
        return key

    async def start_logging(self):
        """Start background logging task"""
        if self._logging_task is None:
            self._logging_task = asyncio.create_task(self._process_log_queue())

    async def stop_logging(self):
        """Stop background logging task"""
        if self._logging_task:
            self._logging_task.cancel()
            try:
                await self._logging_task
            except asyncio.CancelledError:
                pass
            self._logging_task = None

    async def _process_log_queue(self):
        """Process log entries in background"""
        while True:
            try:
                event = await self.log_queue.get()
                await self._write_log_entry(event)
                self.log_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Failed to process audit log entry: {e}")

    async def _write_log_entry(self, event: AuditEvent):
        """Write audit event to log file"""
        try:
            # Mask sensitive data
            masked_event = self._mask_event(event)
            
            # Convert to JSON
            log_data = json.dumps(asdict(masked_event), default=str, ensure_ascii=False)
            
            # Compress and encrypt
            compressed_data = gzip.compress(log_data.encode('utf-8'))
            encrypted_data = self.cipher.encrypt(compressed_data)
            
            # Write to daily log file
            date_str = event.timestamp.strftime("%Y-%m-%d")
            log_file = self.log_dir / f"audit_{date_str}.log.enc"
            
            with open(log_file, "ab") as f:
                f.write(encrypted_data + b"\n")
            
            # Check file size and rotate if necessary
            if log_file.stat().st_size > self.max_file_size:
                await self._rotate_log_file(log_file)
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def _mask_event(self, event: AuditEvent) -> AuditEvent:
        """Mask sensitive data in audit event"""
        # Mask request and response data
        if event.request_data:
            event.request_data = DataMasker.mask_data(event.request_data, "request")
        
        if event.response_data:
            event.response_data = DataMasker.mask_data(event.response_data, "response")
        
        # Mask user agent partially
        if event.user_agent:
            # Keep first 50 characters, mask the rest
            if len(event.user_agent) > 50:
                event.user_agent = event.user_agent[:50] + "*" * (len(event.user_agent) - 50)
        
        # Mask IP address partially
        if event.ip_address:
            try:
                parts = event.ip_address.split(".")
                if len(parts) == 4:
                    event.ip_address = f"{parts[0]}.{parts[1]}.***.{parts[3]}"
            except:
                event.ip_address = "***.***.***.***"
        
        return event

    async def _rotate_log_file(self, log_file: Path):
        """Rotate log file when it gets too large"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_file = log_file.with_name(f"{log_file.stem}_{timestamp}{log_file.suffix}")
        
        # Move current file
        log_file.rename(rotated_file)
        
        # Clean up old files
        await self._cleanup_old_logs()

    async def _cleanup_old_logs(self):
        """Clean up old log files based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for log_file in self.log_dir.glob("audit_*.log.enc"):
            try:
                # Extract date from filename
                date_str = log_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    logger.info(f"Deleted old audit log: {log_file}")
            except Exception as e:
                logger.warning(f"Failed to process log file {log_file}: {e}")

    async def log_event(
        self,
        event_type: EventType,
        level: LogLevel = LogLevel.INFO,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        merchant_order_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        security_context: Optional[Dict[str, Any]] = None,
        compliance_flags: Optional[List[str]] = None
    ):
        """Log an audit event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type=event_type,
            level=level,
            user_id=user_id,
            session_id=session_id,
            transaction_id=transaction_id,
            merchant_order_id=merchant_order_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_data=request_data,
            response_data=response_data,
            error_message=error_message,
            duration_ms=duration_ms,
            security_context=security_context,
            compliance_flags=compliance_flags or []
        )
        
        # Add to queue for background processing
        await self.log_queue.put(event)

    async def log_payment_initiated(
        self,
        user_id: str,
        transaction_id: str,
        amount: int,
        request_data: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log payment initiation"""
        await self.log_event(
            event_type=EventType.PAYMENT_INITIATED,
            level=LogLevel.INFO,
            user_id=user_id,
            transaction_id=transaction_id,
            ip_address=ip_address,
            request_data=request_data,
            compliance_flags=["PCI_DSS", "GDPR", "PCI_COMPLIANT"]
        )

    async def log_payment_success(
        self,
        user_id: str,
        transaction_id: str,
        amount: int,
        response_data: Dict[str, Any]
    ):
        """Log successful payment"""
        await self.log_event(
            event_type=EventType.PAYMENT_SUCCESS,
            level=LogLevel.INFO,
            user_id=user_id,
            transaction_id=transaction_id,
            response_data=response_data,
            compliance_flags=["PCI_DSS", "GDPR", "AUDIT_REQUIRED"]
        )

    async def log_security_violation(
        self,
        violation_type: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None
    ):
        """Log security violation"""
        await self.log_event(
            event_type=EventType.SECURITY_VIOLATION,
            level=LogLevel.WARNING,
            ip_address=ip_address,
            user_agent=user_agent,
            request_data=request_data,
            security_context={"violation_type": violation_type},
            compliance_flags=["SECURITY_INCIDENT", "IMMEDIATE_REVIEW"]
        )

    async def search_logs(
        self,
        event_type: Optional[EventType] = None,
        user_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Search audit logs (for authorized personnel only)"""
        results = []
        
        # Determine date range
        if not start_date:
            start_date = datetime.now() - timedelta(days=1)
        if not end_date:
            end_date = datetime.now()
        
        # Search through log files
        current_date = start_date.date()
        while current_date <= end_date.date():
            log_file = self.log_dir / f"audit_{current_date.strftime('%Y-%m-%d')}.log.enc"
            
            if log_file.exists():
                try:
                    results.extend(await self._search_log_file(
                        log_file, event_type, user_id, transaction_id, start_date, end_date, limit
                    ))
                except Exception as e:
                    logger.error(f"Failed to search log file {log_file}: {e}")
            
            current_date += timedelta(days=1)
        
        return results[:limit]

    async def _search_log_file(
        self,
        log_file: Path,
        event_type: Optional[EventType],
        user_id: Optional[str],
        transaction_id: Optional[str],
        start_date: datetime,
        end_date: datetime,
        limit: int
    ) -> List[AuditEvent]:
        """Search individual log file"""
        results = []
        
        try:
            with open(log_file, "rb") as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    try:
                        # Decrypt and decompress
                        decrypted_data = self.cipher.decrypt(line.strip())
                        log_data = gzip.decompress(decrypted_data).decode('utf-8')
                        event_dict = json.loads(log_data)
                        
                        # Convert to AuditEvent
                        event = AuditEvent(
                            event_id=event_dict["event_id"],
                            timestamp=datetime.fromisoformat(event_dict["timestamp"]),
                            event_type=EventType(event_dict["event_type"]),
                            level=LogLevel(event_dict["level"]),
                            user_id=event_dict.get("user_id"),
                            session_id=event_dict.get("session_id"),
                            transaction_id=event_dict.get("transaction_id"),
                            merchant_order_id=event_dict.get("merchant_order_id"),
                            ip_address=event_dict.get("ip_address"),
                            user_agent=event_dict.get("user_agent"),
                            request_data=event_dict.get("request_data"),
                            response_data=event_dict.get("response_data"),
                            error_message=event_dict.get("error_message"),
                            duration_ms=event_dict.get("duration_ms"),
                            security_context=event_dict.get("security_context"),
                            compliance_flags=event_dict.get("compliance_flags", [])
                        )
                        
                        # Apply filters
                        if event_type and event.event_type != event_type:
                            continue
                        if user_id and event.user_id != user_id:
                            continue
                        if transaction_id and event.transaction_id != transaction_id:
                            continue
                        if event.timestamp < start_date or event.timestamp > end_date:
                            continue
                        
                        results.append(event)
                        
                        if len(results) >= limit:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Failed to process log entry: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Failed to read log file {log_file}: {e}")
        
        return results

    async def get_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        region: str = "IN"
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        events = await self.search_logs(start_date=start_date, end_date=end_date, limit=10000)
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "region": region
            },
            "summary": {
                "total_events": len(events),
                "payment_events": len([e for e in events if e.event_type in [
                    EventType.PAYMENT_INITIATED, EventType.PAYMENT_SUCCESS, EventType.PAYMENT_FAILED
                ]]),
                "security_events": len([e for e in events if e.event_type == EventType.SECURITY_VIOLATION]),
                "error_events": len([e for e in events if e.level in [LogLevel.ERROR, LogLevel.CRITICAL]])
            },
            "compliance_flags": {
                "PCI_DSS": len([e for e in events if "PCI_DSS" in (e.compliance_flags or [])]),
                "GDPR": len([e for e in events if "GDPR" in (e.compliance_flags or [])]),
                "AUDIT_REQUIRED": len([e for e in events if "AUDIT_REQUIRED" in (e.compliance_flags or [])])
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return report

# Global audit logger instance
audit_logger = AuditLogger()
