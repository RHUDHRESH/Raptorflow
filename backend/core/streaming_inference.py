"""
AI Inference Streaming System
=============================

Real-time streaming inference for long-running AI tasks with progress updates,
chunked responses, and client-side synchronization.

Features:
- Real-time response streaming
- Progress tracking and updates
- Chunked response delivery
- Client synchronization
- Connection management
- Error handling and recovery
- Performance monitoring
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Set, Union
import weakref

import structlog
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class StreamStatus(str, Enum):
    """Stream status types."""
    
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class ChunkType(str, Enum):
    """Stream chunk types."""
    
    PROGRESS = "progress"
    DATA = "data"
    ERROR = "error"
    METADATA = "metadata"
    CONTROL = "control"
    HEARTBEAT = "heartbeat"


@dataclass
class StreamChunk:
    """Individual stream chunk."""
    
    id: str
    type: ChunkType
    data: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sequence: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "sequence": self.sequence,
            "metadata": self.metadata,
        }


@dataclass
class StreamSession:
    """Active streaming session."""
    
    id: str
    request_id: str
    websocket: WebSocket
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    status: StreamStatus = StreamStatus.CONNECTING
    
    # Stream configuration
    heartbeat_interval: int = 30  # seconds
    chunk_size: int = 1024  # bytes
    compression: bool = True
    
    # Stream state
    sequence_counter: int = 0
    total_chunks: int = 0
    bytes_sent: int = 0
    
    # Progress tracking
    progress_current: float = 0.0
    progress_total: float = 100.0
    progress_message: str = ""
    
    # Error handling
    error_count: int = 0
    max_errors: int = 5
    
    def __post_init__(self):
        """Initialize session after creation."""
        self.last_activity = self.created_at
    
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status in [StreamStatus.CONNECTED, StreamStatus.STREAMING]
    
    def is_stale(self, timeout_seconds: int = 300) -> bool:
        """Check if session is stale."""
        return datetime.utcnow() > self.last_activity + timedelta(seconds=timeout_seconds)
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage."""
        if self.progress_total <= 0:
            return 0.0
        return min(100.0, (self.progress_current / self.progress_total) * 100.0)
    
    def increment_sequence(self) -> int:
        """Increment sequence counter."""
        self.sequence_counter += 1
        return self.sequence_counter
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status.value,
            "heartbeat_interval": self.heartbeat_interval,
            "chunk_size": self.chunk_size,
            "compression": self.compression,
            "sequence_counter": self.sequence_counter,
            "total_chunks": self.total_chunks,
            "bytes_sent": self.bytes_sent,
            "progress_current": self.progress_current,
            "progress_total": self.progress_total,
            "progress_message": self.progress_message,
            "progress_percentage": self.get_progress_percentage(),
            "error_count": self.error_count,
            "max_errors": self.max_errors,
        }


class StreamingInferenceManager:
    """Manages streaming inference sessions and connections."""
    
    def __init__(
        self,
        max_sessions: int = 1000,
        session_timeout: int = 300,  # 5 minutes
        heartbeat_interval: int = 30,
    ):
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.heartbeat_interval = heartbeat_interval
        
        # Session management
        self.active_sessions: Dict[str, StreamSession] = {}
        self.request_sessions: Dict[str, Set[str]] = {}  # request_id -> session_ids
        
        # WebSocket connection tracking
        self.websocket_sessions: Dict[WebSocket, Set[str]] = {}  # websocket -> session_ids
        
        # Background tasks
        self._cleanup_task = None
        self._heartbeat_task = None
        self._running = False
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "completed_sessions": 0,
            "error_sessions": 0,
            "total_chunks_sent": 0,
            "total_bytes_sent": 0,
            "average_session_duration": 0.0,
        }
        
        # Event callbacks
        self._session_callbacks: Dict[str, List[callable]] = {
            "connected": [],
            "disconnected": [],
            "error": [],
            "completed": [],
        }
    
    async def start(self):
        """Start streaming manager."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_sessions())
        self._heartbeat_task = asyncio.create_task(self._send_heartbeats())
        logger.info("Streaming inference manager started")
    
    async def stop(self):
        """Stop streaming manager."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all active sessions
        await self.close_all_sessions()
        logger.info("Streaming inference manager stopped")
    
    async def create_session(
        self,
        request_id: str,
        websocket: WebSocket,
        **config
    ) -> Optional[StreamSession]:
        """Create new streaming session."""
        async with self._lock:
            # Check session limit
            if len(self.active_sessions) >= self.max_sessions:
                logger.warning(f"Session limit reached: {self.max_sessions}")
                return None
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create session
            session = StreamSession(
                id=session_id,
                request_id=request_id,
                websocket=websocket,
                **config
            )
            
            # Add to tracking
            self.active_sessions[session_id] = session
            
            if request_id not in self.request_sessions:
                self.request_sessions[request_id] = set()
            self.request_sessions[request_id].add(session_id)
            
            if websocket not in self.websocket_sessions:
                self.websocket_sessions[websocket] = set()
            self.websocket_sessions[websocket].add(session_id)
            
            # Update statistics
            self.stats["total_sessions"] += 1
            self.stats["active_sessions"] += 1
            
            logger.info(f"Created streaming session {session_id} for request {request_id}")
            
            # Trigger callbacks
            await self._trigger_callbacks("connected", session)
            
            return session
    
    async def get_session(self, session_id: str) -> Optional[StreamSession]:
        """Get session by ID."""
        async with self._lock:
            return self.active_sessions.get(session_id)
    
    async def get_request_sessions(self, request_id: str) -> List[StreamSession]:
        """Get all sessions for a request."""
        async with self._lock:
            session_ids = self.request_sessions.get(request_id, set())
            return [self.active_sessions[sid] for sid in session_ids if sid in self.active_sessions]
    
    async def send_chunk(self, session_id: str, chunk: StreamChunk) -> bool:
        """Send chunk to session."""
        async with self._lock:
            session = self.active_sessions.get(session_id)
            if not session or not session.is_active():
                return False
            
            try:
                # Update chunk sequence
                chunk.sequence = session.increment_sequence()
                
                # Serialize chunk
                chunk_data = json.dumps(chunk.to_dict())
                
                # Send via WebSocket
                await session.websocket.send_text(chunk_data)
                
                # Update session stats
                session.total_chunks += 1
                session.bytes_sent += len(chunk_data.encode())
                session.update_activity()
                
                # Update global stats
                self.stats["total_chunks_sent"] += 1
                self.stats["total_bytes_sent"] += len(chunk_data.encode())
                
                logger.debug(f"Sent chunk {chunk.sequence} to session {session_id}")
                return True
                
            except Exception as e:
                logger.error(f"Error sending chunk to session {session_id}: {e}")
                await self._handle_session_error(session, str(e))
                return False
    
    async def send_progress(
        self,
        session_id: str,
        current: float,
        total: float,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send progress update."""
        async with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            # Update session progress
            session.progress_current = current
            session.progress_total = total
            session.progress_message = message
            
            # Create progress chunk
            chunk = StreamChunk(
                id=str(uuid.uuid4()),
                type=ChunkType.PROGRESS,
                data={
                    "current": current,
                    "total": total,
                    "percentage": session.get_progress_percentage(),
                    "message": message,
                },
                metadata=metadata or {},
            )
            
            return await self.send_chunk(session_id, chunk)
    
    async def send_data(self, session_id: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send data chunk."""
        chunk = StreamChunk(
            id=str(uuid.uuid4()),
            type=ChunkType.DATA,
            data=data,
            metadata=metadata or {},
        )
        return await self.send_chunk(session_id, chunk)
    
    async def send_error(self, session_id: str, error: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send error chunk."""
        async with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.error_count += 1
            
            chunk = StreamChunk(
                id=str(uuid.uuid4()),
                type=ChunkType.ERROR,
                data={"error": error, "error_count": session.error_count},
                metadata=metadata or {},
            )
            
            # Mark session as error if too many errors
            if session.error_count >= session.max_errors:
                session.status = StreamStatus.ERROR
                await self._trigger_callbacks("error", session)
            
            return await self.send_chunk(session_id, chunk)
    
    async def complete_session(self, session_id: str, final_data: Optional[Any] = None) -> bool:
        """Complete streaming session."""
        async with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.status = StreamStatus.COMPLETED
            
            # Send final data if provided
            if final_data is not None:
                await self.send_data(session_id, final_data, {"final": True})
            
            # Send completion chunk
            chunk = StreamChunk(
                id=str(uuid.uuid4()),
                type=ChunkType.CONTROL,
                data={"action": "complete", "final": True},
            )
            await self.send_chunk(session_id, chunk)
            
            # Update statistics
            self.stats["completed_sessions"] += 1
            
            # Trigger callbacks
            await self._trigger_callbacks("completed", session)
            
            # Remove from active sessions
            await self._remove_session(session_id)
            
            logger.info(f"Completed streaming session {session_id}")
            return True
    
    async def close_session(self, session_id: str, reason: str = "client_disconnect") -> bool:
        """Close streaming session."""
        async with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.status = StreamStatus.DISCONNECTED
            
            # Send close chunk
            chunk = StreamChunk(
                id=str(uuid.uuid4()),
                type=ChunkType.CONTROL,
                data={"action": "close", "reason": reason},
            )
            
            try:
                await session.websocket.send_text(json.dumps(chunk.to_dict()))
                await session.websocket.close()
            except Exception:
                pass  # WebSocket might already be closed
            
            # Trigger callbacks
            await self._trigger_callbacks("disconnected", session)
            
            # Remove from active sessions
            await self._remove_session(session_id)
            
            logger.info(f"Closed streaming session {session_id}: {reason}")
            return True
    
    async def _remove_session(self, session_id: str):
        """Remove session from tracking."""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        # Remove from request sessions
        if session.request_id in self.request_sessions:
            self.request_sessions[session.request_id].discard(session_id)
            if not self.request_sessions[session.request_id]:
                del self.request_sessions[session.request_id]
        
        # Remove from websocket sessions
        if session.websocket in self.websocket_sessions:
            self.websocket_sessions[session.websocket].discard(session_id)
            if not self.websocket_sessions[session.websocket]:
                del self.websocket_sessions[session.websocket]
        
        # Update statistics
        self.stats["active_sessions"] -= 1
    
    async def _handle_session_error(self, session: StreamSession, error: str):
        """Handle session error."""
        session.error_count += 1
        await self.send_error(session.id, error)
        
        if session.error_count >= session.max_errors:
            session.status = StreamStatus.ERROR
            await self._trigger_callbacks("error", session)
            await self.close_session(session.id, "too_many_errors")
    
    async def _cleanup_sessions(self):
        """Background task to cleanup stale sessions."""
        while self._running:
            try:
                async with self._lock:
                    stale_sessions = []
                    
                    for session_id, session in self.active_sessions.items():
                        if session.is_stale(self.session_timeout):
                            stale_sessions.append(session_id)
                
                for session_id in stale_sessions:
                    await self.close_session(session_id, "timeout")
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)
    
    async def _send_heartbeats(self):
        """Background task to send heartbeats."""
        while self._running:
            try:
                async with self._lock:
                    sessions_to_heartbeat = list(self.active_sessions.values())
                
                for session in sessions_to_heartbeat:
                    if session.is_active():
                        chunk = StreamChunk(
                            id=str(uuid.uuid4()),
                            type=ChunkType.HEARTBEAT,
                            data={"timestamp": datetime.utcnow().isoformat()},
                        )
                        await self.send_chunk(session.id, chunk)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error sending heartbeats: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def close_all_sessions(self):
        """Close all active sessions."""
        async with self._lock:
            session_ids = list(self.active_sessions.keys())
        
        for session_id in session_ids:
            await self.close_session(session_id, "shutdown")
    
    def add_callback(self, event: str, callback: callable):
        """Add event callback."""
        if event in self._session_callbacks:
            self._session_callbacks[event].append(callback)
    
    def remove_callback(self, event: str, callback: callable):
        """Remove event callback."""
        if event in self._session_callbacks:
            try:
                self._session_callbacks[event].remove(callback)
            except ValueError:
                pass
    
    async def _trigger_callbacks(self, event: str, session: StreamSession):
        """Trigger event callbacks."""
        for callback in self._session_callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(session)
                else:
                    callback(session)
            except Exception as e:
                logger.error(f"Error in callback for event {event}: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get streaming statistics."""
        async with self._lock:
            # Calculate average session duration
            total_duration = 0
            session_count = 0
            
            for session in self.active_sessions.values():
                duration = (datetime.utcnow() - session.created_at).total_seconds()
                total_duration += duration
                session_count += 1
            
            avg_duration = total_duration / session_count if session_count > 0 else 0
            
            return {
                **self.stats,
                "active_sessions": len(self.active_sessions),
                "request_sessions": len(self.request_sessions),
                "websocket_connections": len(self.websocket_sessions),
                "average_session_duration": round(avg_duration, 2),
                "sessions_by_status": {
                    status.value: len([s for s in self.active_sessions.values() if s.status == status])
                    for status in StreamStatus
                },
            }


class StreamingInferenceService:
    """High-level streaming inference service."""
    
    def __init__(self, manager: StreamingInferenceManager):
        self.manager = manager
    
    async def stream_inference(
        self,
        request_id: str,
        websocket: WebSocket,
        inference_generator: AsyncGenerator[Dict[str, Any], None],
        **config
    ) -> bool:
        """Stream inference results to client."""
        # Create session
        session = await self.manager.create_session(request_id, websocket, **config)
        if not session:
            return False
        
        try:
            # Accept WebSocket connection
            await websocket.accept()
            session.status = StreamStatus.CONNECTED
            
            # Stream inference results
            async for result in inference_generator:
                if not session.is_active():
                    break
                
                # Handle different result types
                if isinstance(result, dict):
                    if "progress" in result:
                        await self.manager.send_progress(
                            session.id,
                            result["progress"].get("current", 0),
                            result["progress"].get("total", 100),
                            result["progress"].get("message", ""),
                            result.get("metadata")
                        )
                    elif "data" in result:
                        await self.manager.send_data(session.id, result["data"], result.get("metadata"))
                    elif "error" in result:
                        await self.manager.send_error(session.id, result["error"], result.get("metadata"))
                    else:
                        await self.manager.send_data(session.id, result)
                else:
                    await self.manager.send_data(session.id, result)
            
            # Complete session
            await self.manager.complete_session(session.id)
            return True
            
        except WebSocketDisconnect:
            await self.manager.close_session(session.id, "client_disconnect")
            return False
        except Exception as e:
            logger.error(f"Error in streaming inference: {e}")
            await self.manager.send_error(session.id, str(e))
            await self.manager.close_session(session.id, "error")
            return False


# Global streaming manager
_streaming_manager: Optional[StreamingInferenceManager] = None


async def get_streaming_manager() -> StreamingInferenceManager:
    """Get or create global streaming manager."""
    global _streaming_manager
    if _streaming_manager is None:
        _streaming_manager = StreamingInferenceManager()
        await _streaming_manager.start()
    return _streaming_manager


async def shutdown_streaming_manager():
    """Shutdown streaming manager."""
    global _streaming_manager
    if _streaming_manager:
        await _streaming_manager.stop()
        _streaming_manager = None
