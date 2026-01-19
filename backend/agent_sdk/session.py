"""
Session Management for Claude Agent SDK

Implements long-lived session connections using ClaudeSDKClient.
Based on the official Python SDK examples (streaming_mode.py).

Key patterns:
1. ClaudeSDKClient - Official bidirectional streaming client
2. AgentSession - Wraps ClaudeSDKClient with session management
3. SessionManager - Manages multiple sessions with lifecycle control

Reference: claude-agent-sdk-python/examples/streaming_mode.py
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional, Set
from uuid import uuid4

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage as SDKUserMessage,
)

from .config import AgentSDKConfig, get_config
from .exceptions import AgentNotFoundError, AgentSDKError

logger = logging.getLogger(__name__)


@dataclass
class MessageRecord:
    """Record of a message in the session"""
    content: str
    role: str  # 'user' or 'assistant'
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)


class AgentSession:
    """
    Maintains a long-lived connection to Claude using ClaudeSDKClient.

    Based on the official SDK pattern from streaming_mode.py:
    - Uses ClaudeSDKClient for bidirectional streaming
    - Supports multi-turn conversation with client.query()
    - Properly handles receive_response() for message consumption

    Key benefits:
    - True multi-turn conversation support
    - Connection stays open between messages
    - Streaming output naturally supported
    - Support for interrupts
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

        self._client: Optional[ClaudeSDKClient] = None
        self._is_connected: bool = False
        self._created_at = time.time()
        self._last_activity = time.time()
        self._message_count = 0
        self._total_cost_usd = 0.0
        self._lock = asyncio.Lock()

    async def initialize(self):
        """
        Initialize the agent session by connecting ClaudeSDKClient.

        Based on the official pattern:
        async with ClaudeSDKClient(options) as client:
            ...

        We manage connect/disconnect manually for long-lived sessions.
        """
        if self._is_connected:
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

        try:
            self._client = ClaudeSDKClient(options=options)
            await self._client.connect()  # Connect for long-lived session
            self._is_connected = True
            logger.info(f"AgentSession {self.session_id} initialized for {self.agent_role}")
        except Exception as e:
            logger.error(f"Failed to initialize session {self.session_id}: {e}")
            raise

    async def send_message_stream(self, content: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Send a message and stream the response.

        This follows the official pattern from streaming_mode.py:
        1. client.query(prompt) - Send the message
        2. client.receive_response() - Receive messages until ResultMessage

        Yields:
            Event dictionaries with type and content
        """
        async with self._lock:
            if not self._is_connected or self._client is None:
                await self.initialize()

            self._last_activity = time.time()
            self._message_count += 1

            try:
                # Send message using the official client.query() pattern
                await self._client.query(content)

                # Receive response using receive_response() which terminates at ResultMessage
                async for message in self._client.receive_response():
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

                    elif isinstance(message, SDKUserMessage):
                        # User messages can contain tool results
                        for block in message.content if isinstance(message.content, list) else []:
                            if isinstance(block, ToolResultBlock):
                                yield {
                                    "type": "tool_result",
                                    "tool_id": block.tool_use_id,
                                    "content": block.content,
                                    "session_id": self.session_id,
                                }

                    elif isinstance(message, SystemMessage):
                        # System messages (usually ignored)
                        pass

                    elif isinstance(message, ResultMessage):
                        # Result message indicates response is complete
                        if message.total_cost_usd:
                            self._total_cost_usd += message.total_cost_usd
                        yield {
                            "type": "result",
                            "total_cost_usd": message.total_cost_usd,
                            "duration_ms": message.duration_ms,
                            "num_turns": message.num_turns,
                            "session_id": self.session_id,
                        }
                        # receive_response() automatically terminates after ResultMessage

            except asyncio.CancelledError:
                logger.info(f"Message stream cancelled for session {self.session_id}")
                raise
            except Exception as e:
                logger.error(f"Error in message stream for session {self.session_id}: {e}")
                yield {
                    "type": "error",
                    "error": str(e),
                    "session_id": self.session_id,
                }

    async def interrupt(self):
        """
        Send interrupt signal to stop current response.

        Based on the official pattern from streaming_mode.py example_with_interrupt().
        """
        if self._client and self._is_connected:
            try:
                await self._client.interrupt()
                logger.info(f"Interrupt sent to session {self.session_id}")
            except Exception as e:
                logger.error(f"Error sending interrupt to session {self.session_id}: {e}")

    async def close(self):
        """Close the session and disconnect the client"""
        if self._client:
            try:
                await self._client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting session {self.session_id}: {e}")
            finally:
                self._client = None
                self._is_connected = False
        logger.info(f"AgentSession {self.session_id} closed")

    @property
    def is_connected(self) -> bool:
        return self._is_connected

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
            "is_connected": self._is_connected,
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
            # Return existing session if available and connected
            if session_key in self._sessions:
                session = self._sessions[session_key]
                if session.is_connected:
                    logger.debug(f"Reusing existing session: {session_key}")
                    return session
                else:
                    # Clean up disconnected session
                    await session.close()
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
                await session.close()
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
                        await self._sessions[session_key].close()
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
            await session.close()
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
                await self._sessions[session_key].close()
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
                await session.close()
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
