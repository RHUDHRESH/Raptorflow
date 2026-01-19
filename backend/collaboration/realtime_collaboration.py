"""
Real-Time Collaboration System
Advanced real-time collaboration features for Raptorflow
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import asyncio
import uuid
import weakref
from collections import defaultdict, deque
import websockets
from websockets.server import WebSocketServerProtocol
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CollaborationEventType(str, Enum):
    """Collaboration event types"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CURSOR_MOVED = "cursor_moved"
    SELECTION_CHANGED = "selection_changed"
    TEXT_EDITED = "text_edited"
    COMMENT_ADDED = "comment_added"
    COMMENT_RESOLVED = "comment_resolved"
    STEP_COMPLETED = "step_completed"
    WORKFLOW_UPDATED = "workflow_updated"
    PRESENCE_UPDATED = "presence_updated"
    TYPING_STARTED = "typing_started"
    TYPING_STOPPED = "typing_stopped"


class CollaborationPermission(str, Enum):
    """Collaboration permissions"""
    READ = "read"
    WRITE = "write"
    COMMENT = "comment"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class CollaborationUser:
    """Collaboration user"""
    id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    color: str = "#000000"
    permissions: List[CollaborationPermission] = field(default_factory=list)
    cursor_position: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    is_typing: bool = False
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "color": self.color,
            "permissions": [p.value for p in self.permissions],
            "cursor_position": self.cursor_position,
            "selection": self.selection,
            "is_typing": self.is_typing,
            "last_seen": self.last_seen.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class CollaborationEvent:
    """Collaboration event"""
    id: str
    type: CollaborationEventType
    user_id: str
    workspace_id: str
    session_id: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "session_id": self.session_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class CollaborationSession:
    """Collaboration session"""
    id: str
    workspace_id: str
    name: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    users: Dict[str, CollaborationUser] = field(default_factory=dict)
    events: deque = field(default_factory=lambda: deque(maxlen=1000))
    is_active: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_user(self, user: CollaborationUser):
        """Add user to session"""
        self.users[user.id] = user
    
    def remove_user(self, user_id: str):
        """Remove user from session"""
        if user_id in self.users:
            del self.users[user_id]
    
    def get_user(self, user_id: str) -> Optional[CollaborationUser]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[CollaborationUser]:
        """Get all users"""
        return list(self.users.values())
    
    def add_event(self, event: CollaborationEvent):
        """Add event to session"""
        self.events.append(event)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "users": [user.to_dict() for user in self.users.values()],
            "is_active": self.is_active,
            "settings": self.settings,
            "metadata": self.metadata
        }


class RealTimeCollaboration:
    """Real-time collaboration system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Active sessions
        self.sessions: Dict[str, CollaborationSession] = {}
        
        # WebSocket connections
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        # User connection mapping
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        
        # Redis for pub/sub (if available)
        self.redis_client: Optional[redis.Redis] = None
        self._init_redis()
        
        # Event handlers
        self.event_handlers: Dict[CollaborationEventType, List[Callable]] = defaultdict(list)
        
        # Presence tracking
        self.presence: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Typing indicators
        self.typing_users: Dict[str, Set[str]] = defaultdict(set)
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def _init_redis(self):
        """Initialize Redis client"""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            asyncio.create_task(self.redis_client.ping())
            self.logger.info("Redis client initialized for collaboration")
        except Exception as e:
            self.logger.warning(f"Redis not available for collaboration: {e}")
            self.redis_client = None
    
    async def create_session(self, workspace_id: str, name: str, created_by: str, settings: Dict[str, Any] = None) -> CollaborationSession:
        """Create collaboration session"""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        session = CollaborationSession(
            id=session_id,
            workspace_id=workspace_id,
            name=name,
            created_by=created_by,
            settings=settings or {}
        )
        
        self.sessions[session_id] = session
        
        # Publish session creation event
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.USER_JOINED,
            user_id=created_by,
            workspace_id=workspace_id,
            session_id=session_id,
            data={"session_name": name, "session_id": session_id}
        ))
        
        self.logger.info(f"Created collaboration session: {session_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    async def get_sessions_by_workspace(self, workspace_id: str) -> List[CollaborationSession]:
        """Get sessions for workspace"""
        return [session for session in self.sessions.values() if session.workspace_id == workspace_id]
    
    async def join_session(self, session_id: str, user: CollaborationUser) -> bool:
        """Join collaboration session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Add user to session
        session.add_user(user)
        
        # Update presence
        self.presence[user.id] = {
            "session_id": session_id,
            "workspace_id": session.workspace_id,
            "joined_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Publish join event
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.USER_JOINED,
            user_id=user.id,
            workspace_id=session.workspace_id,
            session_id=session_id,
            data={"user": user.to_dict()}
        ))
        
        self.logger.info(f"User {user.id} joined session {session_id}")
        return True
    
    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """Leave collaboration session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Remove user from session
        session.remove_user(user_id)
        
        # Update presence
        if user_id in self.presence:
            del self.presence[user_id]
        
        # Remove typing indicator
        if session_id in self.typing_users and user_id in self.typing_users[session_id]:
            self.typing_users[session_id].remove(user_id)
        
        # Publish leave event
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.USER_LEFT,
            user_id=user_id,
            workspace_id=session.workspace_id,
            session_id=session_id,
            data={"user_id": user_id}
        ))
        
        self.logger.info(f"User {user_id} left session {session_id}")
        return True
    
    async def update_cursor(self, session_id: str, user_id: str, cursor_position: Dict[str, Any]) -> bool:
        """Update user cursor position"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        user = session.get_user(user_id)
        if not user:
            return False
        
        # Update cursor
        user.cursor_position = cursor_position
        user.last_seen = datetime.now()
        
        # Publish cursor event
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.CURSOR_MOVED,
            user_id=user_id,
            workspace_id=session.workspace_id,
            session_id=session_id,
            data={"user_id": user_id, "cursor_position": cursor_position}
        ))
        
        return True
    
    async def update_selection(self, session_id: str, user_id: str, selection: Dict[str, Any]) -> bool:
        """Update user selection"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        user = session.get_user(user_id)
        if not user:
            return False
        
        # Update selection
        user.selection = selection
        user.last_seen = datetime.now()
        
        # Publish selection event
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.SELECTION_CHANGED,
            user_id=user_id,
            workspace_id=session.workspace_id,
            session_id=session_id,
            data={"user_id": user_id, "selection": selection}
        ))
        
        return True
    
    async def add_comment(self, session_id: str, user_id: str, comment: Dict[str, Any]) -> bool:
        """Add comment to session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Generate comment ID
        comment_id = f"comment_{uuid.uuid4().hex[:8]}"
        comment["id"] = comment_id
        comment["user_id"] = user_id
        comment["created_at"] = datetime.now().isoformat()
        
        # Publish comment event
        await self._publish_event(CollaborationEvent(
            id=comment_id,
            type=CollaborationEventType.COMMENT_ADDED,
            user_id=user_id,
            workspace_id=session.workspace_id,
            session_id=session_id,
            data=comment
        ))
        
        self.logger.info(f"Comment added to session {session_id} by user {user_id}")
        return True
    
    async def resolve_comment(self, session_id: str, user_id: str, comment_id: str) -> bool:
        """Resolve comment"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Publish resolution event
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.COMMENT_RESOLVED,
            user_id=user_id,
            workspace_id=session.workspace_id,
            session_id=session_id,
            data={"comment_id": comment_id, "resolved_by": user_id}
        ))
        
        return True
    
    async def start_typing(self, session_id: str, user_id: str) -> bool:
        """Start typing indicator"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Add to typing users
        self.typing_users[session_id].add(user_id)
        
        # Publish typing event
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.TYPING_STARTED,
            user_id=user_id,
            workspace_id=session.workspace_id,
            session_id=session_id,
            data={"user_id": user_id}
        ))
        
        return True
    
    async def stop_typing(self, session_id: str, user_id: str) -> bool:
        """Stop typing indicator"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Remove from typing users
        if session_id in self.typing_users and user_id in self.typing_users[session_id]:
            self.typing_users[session_id].remove(user_id)
        
        # Publish typing event
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.TYPING_STOPPED,
            user_id=user_id,
            workspace_id=session.workspace_id,
            session_id=session_id,
            data={"user_id": user_id}
        ))
        
        return True
    
    async def update_presence(self, user_id: str, presence_data: Dict[str, Any]) -> bool:
        """Update user presence"""
        if user_id not in self.presence:
            return False
        
        # Update presence data
        self.presence[user_id].update(presence_data)
        self.presence[user_id]["last_activity"] = datetime.now().isoformat()
        
        # Publish presence event
        session_id = self.presence[user_id]["session_id"]
        workspace_id = self.presence[user_id]["workspace_id"]
        
        await self._publish_event(CollaborationEvent(
            id=f"event_{uuid.uuid4().hex[:8]}",
            type=CollaborationEventType.PRESENCE_UPDATED,
            user_id=user_id,
            workspace_id=workspace_id,
            session_id=session_id,
            data={"user_id": user_id, "presence": presence_data}
        ))
        
        return True
    
    async def get_session_events(self, session_id: str, since: Optional[datetime] = None, limit: int = 100) -> List[CollaborationEvent]:
        """Get session events"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        events = list(session.events)
        
        # Filter by timestamp
        if since:
            events = [event for event in events if event.timestamp >= since]
        
        # Limit results
        if limit:
            events = events[-limit:]
        
        return events
    
    async def get_typing_users(self, session_id: str) -> Set[str]:
        """Get typing users for session"""
        return self.typing_users.get(session_id, set())
    
    async def get_active_users(self, workspace_id: str) -> List[CollaborationUser]:
        """Get active users for workspace"""
        active_users = []
        
        for session in self.sessions.values():
            if session.workspace_id == workspace_id and session.is_active:
                active_users.extend(session.get_all_users())
        
        return active_users
    
    async def register_websocket(self, websocket: WebSocketServerProtocol, user_id: str, session_id: str):
        """Register WebSocket connection"""
        connection_id = f"conn_{uuid.uuid4().hex[:8]}"
        
        # Store connection
        self.connections[connection_id] = websocket
        self.user_connections[user_id].add(connection_id)
        
        # Join session if not already joined
        session = self.sessions.get(session_id)
        if session:
            user = session.get_user(user_id)
            if user:
                # Send current session state
                await websocket.send(json.dumps({
                    "type": "session_state",
                    "data": session.to_dict()
                }))
                
                # Send recent events
                recent_events = await self.get_session_events(session_id, limit=50)
                for event in recent_events:
                    await websocket.send(json.dumps({
                        "type": "event",
                        "data": event.to_dict()
                    }))
        
        self.logger.info(f"WebSocket registered for user {user_id} in session {session_id}")
        return connection_id
    
    async def unregister_websocket(self, connection_id: str, user_id: str):
        """Unregister WebSocket connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        self.logger.info(f"WebSocket unregistered for user {user_id}")
    
    async def _publish_event(self, event: CollaborationEvent):
        """Publish event to subscribers"""
        # Add to session events
        session = self.sessions.get(event.session_id)
        if session:
            session.add_event(event)
        
        # Publish via Redis pub/sub
        if self.redis_client:
            try:
                channel = f"collaboration:{event.workspace_id}:{event.session_id}"
                await self.redis_client.publish(channel, json.dumps(event.to_dict()))
            except Exception as e:
                self.logger.error(f"Error publishing to Redis: {e}")
        
        # Send to WebSocket connections
        await self._send_to_websockets(event)
    
    async def _send_to_websockets(self, event: CollaborationEvent):
        """Send event to WebSocket connections"""
        message = json.dumps({
            "type": "event",
            "data": event.to_dict()
        })
        
        # Send to all connections in the session
        for user_id, connections in self.user_connections.items():
            if user_id != event.user_id:  # Don't send to sender
                for connection_id in connections:
                    websocket = self.connections.get(connection_id)
                    if websocket:
                        try:
                            await websocket.send(message)
                        except Exception as e:
                            self.logger.error(f"Error sending to WebSocket {connection_id}: {e}")
    
    async def register_event_handler(self, event_type: CollaborationEventType, handler: Callable):
        """Register event handler"""
        self.event_handlers[event_type].append(handler)
    
    async def handle_event(self, event: CollaborationEvent):
        """Handle event with registered handlers"""
        handlers = self.event_handlers.get(event.type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self.logger.error(f"Error in event handler: {e}")
    
    async def cleanup_inactive_sessions(self, timeout_minutes: int = 30):
        """Clean up inactive sessions"""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        
        inactive_sessions = []
        for session_id, session in self.sessions.items():
            if session.users and all(user.last_seen < cutoff_time for user in session.users.values()):
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            session = self.sessions[session_id]
            session.is_active = False
            
            # Notify remaining users
            for user_id in list(session.users.keys()):
                await self.leave_session(session_id, user_id)
            
            self.logger.info(f"Cleaned up inactive session: {session_id}")
        
        return len(inactive_sessions)
    
    async def get_collaboration_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Get collaboration statistics"""
        sessions = await self.get_sessions_by_workspace(workspace_id)
        active_users = await self.get_active_users(workspace_id)
        
        return {
            "workspace_id": workspace_id,
            "active_sessions": len([s for s in sessions if s.is_active]),
            "total_sessions": len(sessions),
            "active_users": len(active_users),
            "typing_users": sum(len(users) for users in self.typing_users.values()),
            "events_per_session": {
                session.id: len(session.events)
                for session in sessions
            },
            "generated_at": datetime.now().isoformat()
        }


# WebSocket handler class
class CollaborationWebSocketHandler(WebSocketServerProtocol):
    """WebSocket handler for collaboration"""
    
    def __init__(self, collaboration_system: RealTimeCollaboration):
        self.collaboration_system = collaboration_system
        self.user_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.connection_id: Optional[str] = None
    
    async def on_connect(self, request):
        """Handle WebSocket connection"""
        # Extract user and session from query parameters
        query = request.query_string.decode()
        params = dict(param.split('=') for param in query.split('&') if param)
        
        self.user_id = params.get('user_id')
        self.session_id = params.get('session_id')
        
        if not self.user_id or not self.session_id:
            await self.close(4001, "Missing user_id or session_id")
            return
        
        # Register connection
        self.connection_id = await self.collaboration_system.register_websocket(
            self, self.user_id, self.session_id
        )
    
    async def on_message(self, message):
        """Handle WebSocket message"""
        try:
            data = json.loads(message)
            event_type = data.get('type')
            event_data = data.get('data', {})
            
            if event_type == 'cursor_move':
                await self.collaboration_system.update_cursor(
                    self.session_id, self.user_id, event_data
                )
            elif event_type == 'selection_change':
                await self.collaboration_system.update_selection(
                    self.session_id, self.user_id, event_data
                )
            elif event_type == 'typing_start':
                await self.collaboration_system.start_typing(
                    self.session_id, self.user_id
                )
            elif event_type == 'typing_stop':
                await self.collaboration_system.stop_typing(
                    self.session_id, self.user_id
                )
            elif event_type == 'add_comment':
                await self.collaboration_system.add_comment(
                    self.session_id, self.user_id, event_data
                )
            elif event_type == 'resolve_comment':
                await self.collaboration_system.resolve_comment(
                    self.session_id, self.user_id, event_data.get('comment_id')
                )
            elif event_type == 'update_presence':
                await self.collaboration_system.update_presence(
                    self.user_id, event_data
                )
            
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {e}")
    
    async def on_close(self, code, reason):
        """Handle WebSocket close"""
        if self.connection_id and self.user_id:
            await self.collaboration_system.unregister_websocket(
                self.connection_id, self.user_id
            )


# Global collaboration system instance
collaboration_system = RealTimeCollaboration()

# Export system
__all__ = ["RealTimeCollaboration", "CollaborationSession", "CollaborationUser", "CollaborationEvent", "CollaborationWebSocketHandler", "collaboration_system"]
