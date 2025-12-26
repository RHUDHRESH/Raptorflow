"""
Part 18: Real-time Search and Streaming
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements real-time search capabilities, streaming results, and
live data processing for the unified search system.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import websockets
from fastapi import WebSocket, WebSocketDisconnect

from core.unified_search_part1 import SearchQuery, SearchResult, SearchMode, ContentType
from core.unified_search_part2 import SearchProvider
from core.unified_search_part10 import unified_search_engine

logger = logging.getLogger("raptorflow.unified_search.realtime")


class StreamEventType(Enum):
    """Types of streaming events."""
    SEARCH_STARTED = "search_started"
    SEARCH_PROGRESS = "search_progress"
    RESULT_FOUND = "result_found"
    BATCH_COMPLETED = "batch_completed"
    SEARCH_COMPLETED = "search_completed"
    SEARCH_FAILED = "search_failed"
    PROVIDER_STATUS = "provider_status"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class StreamEvent:
    """Streaming event data."""
    event_type: StreamEventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_type': self.event_type.value,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'request_id': self.request_id
        }


@dataclass
class RealtimeSearchSession:
    """Real-time search session."""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    active_searches: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    total_searches: int = 0
    completed_searches: int = 0
    failed_searches: int = 0
    websocket: Optional[WebSocket] = None
    is_active: bool = True
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'active_searches': len(self.active_searches),
            'total_searches': self.total_searches,
            'completed_searches': self.completed_searches,
            'failed_searches': self.failed_searches,
            'is_active': self.is_active
        }


class StreamingSearchExecutor:
    """Executes searches with streaming results."""
    
    def __init__(self):
        self.active_sessions: Dict[str, RealtimeSearchSession] = {}
        self.session_timeout_minutes = 30
        self.max_concurrent_searches = 100
        self.search_queue = asyncio.Queue()
        self.result_buffer_size = 10
        self._cleanup_task: Optional[asyncio.Task] = None
        self._worker_tasks: List[asyncio.Task] = []
        self._num_workers = 5
    
    async def start(self):
        """Start the streaming search executor."""
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Start worker tasks
        for i in range(self._num_workers):
            task = asyncio.create_task(self._search_worker(f"worker-{i}"))
            self._worker_tasks.append(task)
        
        logger.info("Streaming search executor started")
    
    async def stop(self):
        """Stop the streaming search executor."""
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cancel worker tasks
        for task in self._worker_tasks:
            task.cancel()
        
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        
        # Close all websockets
        for session in self.active_sessions.values():
            if session.websocket:
                await session.websocket.close()
        
        logger.info("Streaming search executor stopped")
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new real-time search session."""
        session_id = str(uuid.uuid4())
        
        session = RealtimeSearchSession(
            session_id=session_id,
            user_id=user_id
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Created session: {session_id}")
        return session_id
    
    async def connect_websocket(self, session_id: str, websocket: WebSocket) -> bool:
        """Connect WebSocket to session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        session.websocket = websocket
        session.update_activity()
        
        # Send welcome event
        await self._send_event(session, StreamEvent(
            event_type=StreamEventType.SEARCH_STARTED,
            data={'message': 'Connected to real-time search'},
            session_id=session_id
        ))
        
        return True
    
    async def disconnect_websocket(self, session_id: str):
        """Disconnect WebSocket from session."""
        session = self.active_sessions.get(session_id)
        if session and session.websocket:
            session.websocket = None
            session.is_active = False
    
    async def execute_streaming_search(
        self,
        session_id: str,
        query: SearchQuery,
        providers: Optional[List[SearchProvider]] = None
    ) -> str:
        """Execute search with streaming results."""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Check concurrent search limit
        if len(session.active_searches) >= self.max_concurrent_searches:
            raise ValueError("Too many concurrent searches")
        
        # Create search request
        request_id = str(uuid.uuid4())
        
        search_request = {
            'request_id': request_id,
            'session_id': session_id,
            'query': query,
            'providers': providers or list(SearchProvider),
            'created_at': datetime.now(),
            'status': 'queued'
        }
        
        session.active_searches[request_id] = search_request
        session.total_searches += 1
        session.update_activity()
        
        # Add to queue
        await self.search_queue.put(search_request)
        
        # Send search started event
        await self._send_event(session, StreamEvent(
            event_type=StreamEventType.SEARCH_STARTED,
            data={
                'request_id': request_id,
                'query': query.text,
                'providers': [p.value for p in search_request['providers']]
            },
            session_id=session_id,
            request_id=request_id
        ))
        
        return request_id
    
    async def _search_worker(self, worker_name: str):
        """Worker task for processing search requests."""
        logger.info(f"Search worker {worker_name} started")
        
        while True:
            try:
                # Get search request from queue
                search_request = await self.search_queue.get()
                
                await self._process_search_request(search_request, worker_name)
                
                self.search_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Search worker {worker_name} error: {e}")
        
        logger.info(f"Search worker {worker_name} stopped")
    
    async def _process_search_request(self, search_request: Dict[str, Any], worker_name: str):
        """Process individual search request."""
        session_id = search_request['session_id']
        request_id = search_request['request_id']
        query = search_request['query']
        providers = search_request['providers']
        
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        try:
            # Update status
            search_request['status'] = 'processing'
            search_request['worker'] = worker_name
            search_request['started_at'] = datetime.now()
            
            # Execute search with streaming
            results_stream = self._execute_search_streaming(query, providers)
            
            collected_results = []
            provider_count = len(providers)
            completed_providers = 0
            
            async for event in results_stream:
                if event.event_type == StreamEventType.RESULT_FOUND:
                    collected_results.append(event.data['result'])
                    await self._send_event(session, event, request_id)
                
                elif event.event_type == StreamEventType.PROVIDER_STATUS:
                    completed_providers += 1
                    progress = completed_providers / provider_count
                    await self._send_event(session, StreamEvent(
                        event_type=StreamEventType.SEARCH_PROGRESS,
                        data={
                            'completed_providers': completed_providers,
                            'total_providers': provider_count,
                            'progress_percentage': progress * 100,
                            'provider': event.data['provider'],
                            'status': event.data['status']
                        },
                        session_id=session_id,
                        request_id=request_id
                    ))
            
            # Send completion event
            session.completed_searches += 1
            search_request['status'] = 'completed'
            search_request['completed_at'] = datetime.now()
            search_request['results_count'] = len(collected_results)
            
            await self._send_event(session, StreamEvent(
                event_type=StreamEventType.SEARCH_COMPLETED,
                data={
                    'request_id': request_id,
                    'results_count': len(collected_results),
                    'duration_ms': (search_request['completed_at'] - search_request['started_at']).total_seconds() * 1000
                },
                session_id=session_id,
                request_id=request_id
            ))
            
        except Exception as e:
            # Send error event
            session.failed_searches += 1
            search_request['status'] = 'failed'
            search_request['error'] = str(e)
            search_request['failed_at'] = datetime.now()
            
            await self._send_event(session, StreamEvent(
                event_type=StreamEventType.SEARCH_FAILED,
                data={
                    'request_id': request_id,
                    'error': str(e)
                },
                session_id=session_id,
                request_id=request_id
            ))
        
        finally:
            # Remove from active searches
            session.active_searches.pop(request_id, None)
            session.update_activity()
    
    async def _execute_search_streaming(self, query: SearchQuery, providers: List[SearchProvider]) -> AsyncGenerator[StreamEvent, None]:
        """Execute search with streaming events."""
        # Get available providers
        available_providers = {}
        
        # This would get actual provider instances from the search engine
        # For now, simulate provider execution
        
        for provider in providers:
            try:
                # Send provider status event
                yield StreamEvent(
                    event_type=StreamEventType.PROVIDER_STATUS,
                    data={'provider': provider.value, 'status': 'starting'}
                )
                
                # Simulate search execution
                await asyncio.sleep(0.5)  # Simulate processing time
                
                # Generate mock results
                mock_results = self._generate_mock_results(query, provider, 5)
                
                # Stream results
                for result in mock_results:
                    yield StreamEvent(
                        event_type=StreamEventType.RESULT_FOUND,
                        data={'result': result.to_dict(), 'provider': provider.value}
                    )
                
                # Send completion status
                yield StreamEvent(
                    event_type=StreamEventType.PROVIDER_STATUS,
                    data={'provider': provider.value, 'status': 'completed', 'results_count': len(mock_results)}
                )
                
            except Exception as e:
                yield StreamEvent(
                    event_type=StreamEventType.PROVIDER_STATUS,
                    data={'provider': provider.value, 'status': 'failed', 'error': str(e)}
                )
    
    def _generate_mock_results(self, query: SearchQuery, provider: SearchProvider, count: int) -> List[SearchResult]:
        """Generate mock search results for testing."""
        results = []
        
        for i in range(count):
            result = SearchResult(
                url=f"https://example.com/{provider.value}/result{i+1}",
                title=f"{provider.value.title()} Result {i+1} for: {query.text}",
                content=f"This is mock content from {provider.value} for the query: {query.text}. " * 10,
                snippet=f"Mock snippet from {provider.value} containing: {query.text[:50]}...",
                provider=provider,
                relevance_score=0.9 - (i * 0.1),
                domain_authority=0.8 + (i * 0.05),
                content_type=ContentType.WEB
            )
            results.append(result)
        
        return results
    
    async def _send_event(self, session: RealtimeSearchSession, event: StreamEvent, request_id: Optional[str] = None):
        """Send event to session WebSocket."""
        if not session.websocket:
            return
        
        try:
            event_data = event.to_dict()
            if request_id:
                event_data['request_id'] = request_id
            
            await session.websocket.send_text(json.dumps(event_data))
            
        except Exception as e:
            logger.error(f"Failed to send event to session {session.session_id}: {e}")
            # Mark session as inactive
            session.is_active = False
    
    async def _cleanup_loop(self):
        """Cleanup inactive sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                cutoff_time = datetime.now() - timedelta(minutes=self.session_timeout_minutes)
                inactive_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if session.last_activity < cutoff_time or not session.is_active:
                        inactive_sessions.append(session_id)
                
                # Clean up inactive sessions
                for session_id in inactive_sessions:
                    session = self.active_sessions.pop(session_id, None)
                    if session and session.websocket:
                        await session.websocket.close()
                    
                    logger.info(f"Cleaned up inactive session: {session_id}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_sessions = len(self.active_sessions)
        active_sessions = sum(1 for s in self.active_sessions.values() if s.is_active)
        total_searches = sum(s.total_searches for s in self.active_sessions.values())
        completed_searches = sum(s.completed_searches for s in self.active_sessions.values())
        failed_searches = sum(s.failed_searches for s in self.active_sessions.values())
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_searches': total_searches,
            'completed_searches': completed_searches,
            'failed_searches': failed_searches,
            'success_rate': completed_searches / total_searches if total_searches > 0 else 0,
            'queue_size': self.search_queue.qsize(),
            'active_workers': len(self._worker_tasks)
        }


class RealtimeSearchAPI:
    """Real-time search API endpoints."""
    
    def __init__(self, streaming_executor: StreamingSearchExecutor):
        self.executor = streaming_executor
    
    async def create_session(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create new real-time search session."""
        session_id = await self.executor.create_session(user_id)
        
        return {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'websocket_url': f'/ws/search/{session_id}'
        }
    
    async def connect_websocket(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket connection."""
        await websocket.accept()
        
        success = await self.executor.connect_websocket(session_id, websocket)
        if not success:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        try:
            # Keep connection alive and handle messages
            while True:
                message = await websocket.receive_text()
                await self._handle_websocket_message(websocket, session_id, message)
                
        except WebSocketDisconnect:
            await self.executor.disconnect_websocket(session_id)
        except Exception as e:
            logger.error(f"WebSocket error for session {session_id}: {e}")
            await self.executor.disconnect_websocket(session_id)
    
    async def _handle_websocket_message(self, websocket: WebSocket, session_id: str, message: str):
        """Handle WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'search':
                await self._handle_search_request(websocket, session_id, data)
            elif message_type == 'ping':
                await websocket.send_text(json.dumps({'type': 'pong'}))
            else:
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def _handle_search_request(self, websocket: WebSocket, session_id: str, data: Dict[str, Any]):
        """Handle search request from WebSocket."""
        try:
            # Extract search parameters
            query_text = data.get('query')
            mode = data.get('mode', 'standard')
            max_results = data.get('max_results', 10)
            content_types = data.get('content_types', ['web'])
            providers = data.get('providers', ['native', 'serper'])
            
            if not query_text:
                await websocket.send_text(json.dumps({
                    'type': 'error',
                    'message': 'Query is required'
                }))
                return
            
            # Create SearchQuery
            search_query = SearchQuery(
                text=query_text,
                mode=SearchMode(mode) if mode in [m.value for m in SearchMode] else SearchMode.STANDARD,
                max_results=max_results,
                content_types=[ContentType(ct) for ct in content_types]
            )
            
            # Convert provider strings to enum
            provider_enums = []
            for provider_str in providers:
                try:
                    provider_enums.append(SearchProvider(provider_str))
                except ValueError:
                    continue
            
            # Execute streaming search
            request_id = await self.executor.execute_streaming_search(
                session_id,
                search_query,
                provider_enums
            )
            
            await websocket.send_text(json.dumps({
                'type': 'search_started',
                'request_id': request_id
            }))
            
        except Exception as e:
            await websocket.send_text(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get real-time search statistics."""
        return self.executor.get_session_stats()


class LiveDataManager:
    """Manages live data streams and updates."""
    
    def __init__(self):
        self.data_streams: Dict[str, asyncio.Queue] = {}
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)  # stream_id -> set of session_ids
        self.update_interval = 30  # seconds
        self._update_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start live data manager."""
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Live data manager started")
    
    async def stop(self):
        """Stop live data manager."""
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("Live data manager stopped")
    
    def create_stream(self, stream_id: str, stream_type: str) -> asyncio.Queue:
        """Create a new data stream."""
        if stream_id in self.data_streams:
            return self.data_streams[stream_id]
        
        stream = asyncio.Queue(maxsize=1000)
        self.data_streams[stream_id] = stream
        
        logger.info(f"Created data stream: {stream_id} ({stream_type})")
        return stream
    
    def subscribe_to_stream(self, stream_id: str, session_id: str):
        """Subscribe session to data stream."""
        self.subscribers[stream_id].add(session_id)
        logger.info(f"Session {session_id} subscribed to stream {stream_id}")
    
    def unsubscribe_from_stream(self, stream_id: str, session_id: str):
        """Unsubscribe session from data stream."""
        self.subscribers[stream_id].discard(session_id)
        logger.info(f"Session {session_id} unsubscribed from stream {stream_id}")
    
    async def publish_to_stream(self, stream_id: str, data: Dict[str, Any]):
        """Publish data to stream."""
        if stream_id not in self.data_streams:
            return
        
        stream = self.data_streams[stream_id]
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        data['stream_id'] = stream_id
        
        # Put in queue (non-blocking)
        try:
            stream.put_nowait(data)
        except asyncio.QueueFull:
            # Remove oldest item
            try:
                stream.get_nowait()
                stream.put_nowait(data)
            except asyncio.QueueEmpty:
                pass
    
    async def _update_loop(self):
        """Main update loop for live data."""
        while True:
            try:
                await asyncio.sleep(self.update_interval)
                await self._process_stream_updates()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Live data update error: {e}")
    
    async def _process_stream_updates(self):
        """Process updates from all streams."""
        for stream_id, stream in self.data_streams.items():
            # Process all pending updates
            updates = []
            
            while not stream.empty():
                try:
                    update = stream.get_nowait()
                    updates.append(update)
                except asyncio.QueueEmpty:
                    break
            
            # Send updates to subscribers
            if updates:
                await self._broadcast_updates(stream_id, updates)
    
    async def _broadcast_updates(self, stream_id: str, updates: List[Dict[str, Any]]):
        """Broadcast updates to subscribed sessions."""
        # This would integrate with the streaming executor
        # For now, just log the updates
        logger.debug(f"Broadcasting {len(updates)} updates for stream {stream_id}")


# Global instances
streaming_executor = StreamingSearchExecutor()
realtime_api = RealtimeSearchAPI(streaming_executor)
live_data_manager = LiveDataManager()
