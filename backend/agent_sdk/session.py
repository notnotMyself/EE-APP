"""
Session Management for Claude Agent SDK

Implements long-lived session connections using MessageQueue pattern.
Inspired by the TypeScript simple-chatapp example.

Key patterns:
1. MessageQueue - Async iterator for bidirectional communication
2. AgentSession - Maintains a single query() call with persistent state
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Set
from uuid import uuid4

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    query,
)

from .config import AgentSDKConfig, get_config
from .exceptions import AgentNotFoundError, AgentSDKError

logger = logging.getLogger(__name__)


@dataclass
class UserMessage:
    """User message wrapper"""
    content: str
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)


class MessageQueue:
    """
    Async message queue for bidirectional communication.

    Messages go in via push(), come out via async iteration.
    This enables the SDK's async generator (prompt) to be fed with new messages at any time.
    """

    def __init__(self):
        self._messages: List[UserMessage] = []
        self._waiting: Optional[asyncio.Future] = None
        self._closed: bool = False
        self._lock = asyncio.Lock()

    async def push(self, content: str) -> str:
        """
        Add message to queue (or deliver immediately if consumer waiting).

        Returns:
            message_id for tracking
        """
        msg = UserMessage(content=content)

        async with self._lock:
            if self._closed:
                raise AgentSDKError("MessageQueue is closed")

            if self._waiting is not None and not self._waiting.done():
                # Direct delivery if consumer is waiting
                self._waiting.set_result(msg)
                self._waiting = None
            else:
                # Queue for later consumption
                self._messages.append(msg)

        logger.debug(f"Message pushed to queue: {msg.message_id[:8]}...")
        return msg.message_id

    async def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        """Async iterator for consuming messages"""
        while not self._closed:
            msg = await self._get_next()
            if msg is None:
                break

            # Yield in SDK expected format
            yield {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": msg.content
                }
            }

    async def _get_next(self) -> Optional[UserMessage]:
        """Get next message, waiting if necessary"""
        async with self._lock:
            if self._messages:
                return self._messages.pop(0)

            if self._closed:
                return None

            # Create a new future to wait on
            self._waiting = asyncio.get_event_loop().create_future()

        try:
            # Wait outside the lock
            return await self._waiting
        except asyncio.CancelledError:
            return None

    def close(self):
        """Close the queue, stopping iteration"""
        self._closed = True
        if self._waiting is not None and not self._waiting.done():
            self._waiting.cancel()
        logger.debug("MessageQueue closed")

    @property
    def is_closed(self) -> bool:
        return self._closed


class AgentSession:
    """
    Maintains a long-lived connection to Claude Agent SDK.

    Key benefits:
    - SDK connection stays open, no initialization overhead per message
    - True multi-turn conversation support
    - Streaming output naturally supported
    """

    def __init__(
        self,
        session_id: str,
        agent_role: str,
        config: Optional[AgentSDKConfig] = None,
        system_prompt: Optional[str] = None,
    ):
        self.session_id = session_id
        self.agent_role = agent_role
        self.config = config or get_config()
        self.system_prompt = system_prompt

        self._queue = MessageQueue()
        self._output_iterator: Optional[AsyncIterator] = None
        self._is_listening = False
        self._created_at = time.time()
        self._last_activity = time.time()
        self._message_count = 0
        self._total_cost_usd = 0.0

    async def initialize(self):
        """Initialize the agent session (call once)"""
        if self._output_iterator is not None:
            logger.warning(f"Session {self.session_id} already initialized")
            return

        role_config = self.config.get_agent_role(self.agent_role)
        if not role_config:
            raise AgentNotFoundError(self.agent_role)

        workdir = self.config.get_agent_workdir(self.agent_role)

        # Load system prompt if not provided
        effective_system_prompt = self.system_prompt
        if not effective_system_prompt:
            claude_md_path = workdir / "CLAUDE.md"
            if claude_md_path.exists():
                try:
                    with open(claude_md_path, "r", encoding="utf-8") as f:
                        effective_system_prompt = f.read()
                except Exception as e:
                    logger.error(f"Error loading CLAUDE.md for {self.agent_role}: {e}")
                    effective_system_prompt = f"你是{role_config.name}。"
            else:
                effective_system_prompt = f"""你是{role_config.name}。

职责：{role_config.description}

请根据用户的问题提供专业的回答和建议。"""

        options = ClaudeAgentOptions(
            system_prompt=effective_system_prompt,
            cwd=str(workdir),
            allowed_tools=role_config.allowed_tools,
            model=role_config.model,
            max_turns=role_config.max_turns,
            permission_mode=self.config.permission_mode,
            env=self.config.get_env_dict(),
        )

        # Start the query with the queue as input
        # This is the key pattern: pass an async iterable queue as the prompt
        try:
            self._output_iterator = query(
                prompt=self._queue,  # Pass the async iterable queue
                options=options
            ).__aiter__()

            logger.info(f"AgentSession {self.session_id} initialized for {self.agent_role}")
        except Exception as e:
            logger.error(f"Failed to initialize session {self.session_id}: {e}")
            raise

    async def send_message(self, content: str) -> str:
        """
        Send a message to the agent.

        Returns:
            message_id for tracking
        """
        if self._output_iterator is None:
            await self.initialize()

        self._last_activity = time.time()
        self._message_count += 1

        return await self._queue.push(content)

    async def get_output_stream(self) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream messages from the agent.

        Yields:
            Event dictionaries with type and content
        """
        if self._output_iterator is None:
            raise AgentSDKError("Session not initialized")

        try:
            async for message in self._output_iterator:
                self._last_activity = time.time()

                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            yield {
                                "type": "text_chunk",
                                "content": block.text,
                                "session_id": self.session_id,
                            }
                        elif isinstance(block, ToolUseBlock):
                            yield {
                                "type": "tool_use",
                                "tool_name": block.name,
                                "tool_id": block.id,
                                "input": block.input,
                                "session_id": self.session_id,
                            }
                        elif isinstance(block, ToolResultBlock):
                            yield {
                                "type": "tool_result",
                                "tool_id": block.tool_use_id,
                                "content": block.content,
                                "session_id": self.session_id,
                            }

                elif isinstance(message, ResultMessage):
                    self._total_cost_usd += getattr(message, "total_cost_usd", 0)
                    yield {
                        "type": "result",
                        "total_cost_usd": message.total_cost_usd,
                        "session_id": self.session_id,
                    }

        except asyncio.CancelledError:
            logger.info(f"Output stream cancelled for session {self.session_id}")
            raise
        except Exception as e:
            logger.error(f"Error in output stream for session {self.session_id}: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "session_id": self.session_id,
            }

    def close(self):
        """Close the session"""
        self._queue.close()
        self._output_iterator = None
        logger.info(f"AgentSession {self.session_id} closed")

    @property
    def stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            "session_id": self.session_id,
            "agent_role": self.agent_role,
            "created_at": self._created_at,
            "last_activity": self._last_activity,
            "message_count": self._message_count,
            "total_cost_usd": self._total_cost_usd,
            "is_closed": self._queue.is_closed,
        }


class SessionManager:
    """
    Manages multiple AgentSessions.

    Features:
    - Session creation and lifecycle management
    - Automatic cleanup of idle sessions
    - Session reuse for same user+agent combination
    """

    def __init__(
        self,
        config: Optional[AgentSDKConfig] = None,
        max_sessions: int = 100,
        idle_timeout_seconds: int = 1800,  # 30 minutes
    ):
        self.config = config or get_config()
        self.max_sessions = max_sessions
        self.idle_timeout_seconds = idle_timeout_seconds

        self._sessions: Dict[str, AgentSession] = {}
        self._user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def get_or_create_session(
        self,
        user_id: str,
        agent_role: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> AgentSession:
        """
        Get existing session or create new one.

        Sessions are keyed by conversation_id if provided, otherwise by user_id+agent_role.
        """
        session_key = conversation_id or f"{user_id}:{agent_role}"

        async with self._lock:
            # Return existing session if available
            if session_key in self._sessions:
                session = self._sessions[session_key]
                if not session._queue.is_closed:
                    logger.debug(f"Reusing existing session: {session_key}")
                    return session
                else:
                    # Clean up closed session
                    del self._sessions[session_key]

            # Check if we need to cleanup before creating new session
            if len(self._sessions) >= self.max_sessions:
                await self._cleanup_oldest_sessions()

            # Create new session
            session_id = conversation_id or str(uuid4())
            session = AgentSession(
                session_id=session_id,
                agent_role=agent_role,
                config=self.config,
                system_prompt=system_prompt,
            )

            await session.initialize()

            self._sessions[session_key] = session

            # Track user sessions
            if user_id not in self._user_sessions:
                self._user_sessions[user_id] = set()
            self._user_sessions[user_id].add(session_key)

            logger.info(f"Created new session: {session_key}")
            return session

    async def close_session(self, session_key: str):
        """Close and remove a specific session"""
        async with self._lock:
            if session_key in self._sessions:
                session = self._sessions[session_key]
                session.close()
                del self._sessions[session_key]

                # Clean up user session mapping
                for user_sessions in self._user_sessions.values():
                    user_sessions.discard(session_key)

    async def close_user_sessions(self, user_id: str):
        """Close all sessions for a user"""
        async with self._lock:
            if user_id in self._user_sessions:
                for session_key in list(self._user_sessions[user_id]):
                    if session_key in self._sessions:
                        self._sessions[session_key].close()
                        del self._sessions[session_key]
                del self._user_sessions[user_id]

    async def _cleanup_oldest_sessions(self):
        """Remove oldest idle sessions to make room"""
        sessions_by_activity = sorted(
            self._sessions.items(),
            key=lambda x: x[1]._last_activity
        )

        # Remove 20% of sessions
        to_remove = max(1, len(sessions_by_activity) // 5)
        for session_key, session in sessions_by_activity[:to_remove]:
            session.close()
            del self._sessions[session_key]
            logger.info(f"Cleaned up idle session: {session_key}")

    async def cleanup_idle_sessions(self):
        """Remove sessions that have been idle too long"""
        current_time = time.time()

        async with self._lock:
            to_remove = []
            for session_key, session in self._sessions.items():
                if current_time - session._last_activity > self.idle_timeout_seconds:
                    to_remove.append(session_key)

            for session_key in to_remove:
                self._sessions[session_key].close()
                del self._sessions[session_key]
                logger.info(f"Cleaned up idle session: {session_key}")

    def start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Background loop for periodic cleanup"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self.cleanup_idle_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def shutdown(self):
        """Shutdown manager and close all sessions"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        async with self._lock:
            for session in self._sessions.values():
                session.close()
            self._sessions.clear()
            self._user_sessions.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            "total_sessions": len(self._sessions),
            "sessions_by_agent": self._count_by_agent(),
            "sessions": [s.stats for s in self._sessions.values()],
        }

    def _count_by_agent(self) -> Dict[str, int]:
        """Count sessions by agent role"""
        counts: Dict[str, int] = {}
        for session in self._sessions.values():
            role = session.agent_role
            counts[role] = counts.get(role, 0) + 1
        return counts


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def init_session_manager(config: Optional[AgentSDKConfig] = None) -> SessionManager:
    """Initialize global session manager"""
    global _session_manager
    _session_manager = SessionManager(config=config)
    _session_manager.start_cleanup_task()
    return _session_manager
