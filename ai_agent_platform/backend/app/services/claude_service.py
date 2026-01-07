"""
Claude API service for AI interactions.
"""
import json
from typing import AsyncGenerator, Optional, Dict, Any
from anthropic import AsyncAnthropic

from app.core.config import settings


class ClaudeService:
    """Service for interacting with Claude API."""

    _MAX_CONTEXT_CHARS = 12000
    _MAX_MESSAGE_CHARS = 8000

    def __init__(self):
        # 优先使用Auth Token，否则使用API Key
        if settings.ANTHROPIC_AUTH_TOKEN:
            client_kwargs = {
                "auth_token": settings.ANTHROPIC_AUTH_TOKEN
            }
            if settings.ANTHROPIC_BASE_URL:
                client_kwargs["base_url"] = settings.ANTHROPIC_BASE_URL
            self.client = AsyncAnthropic(**client_kwargs)
        else:
            client_kwargs = {
                "api_key": settings.ANTHROPIC_API_KEY
            }
            self.client = AsyncAnthropic(**client_kwargs)

        self.model = settings.ANTHROPIC_MODEL

    def _truncate(self, text: str, *, limit: int) -> str:
        if text is None:
            return ""
        text = str(text)
        if len(text) <= limit:
            return text
        head = text[: int(limit * 0.7)]
        tail = text[-int(limit * 0.2):]
        return f"{head}\n\n[...truncated {len(text) - len(head) - len(tail)} chars...]\n\n{tail}"

    def _maybe_summarize_briefing_json(self, content: str) -> str:
        """
        If content looks like a briefing JSON blob, convert it to a compact text card.
        This reduces prompt size and makes the model respond more reliably.
        """
        if not content:
            return content
        s = content.strip()
        if not (s.startswith("{") and s.endswith("}")):
            return content
        try:
            obj = json.loads(s)
        except Exception:
            return content

        if not isinstance(obj, dict):
            return content

        keys = set(obj.keys())
        looks_like_briefing = bool({"title", "summary"} & keys) and (
            "briefing_type" in keys or "priority" in keys or "impact" in keys or "created_at" in keys
        )
        if not looks_like_briefing:
            return content

        title = obj.get("title", "")
        summary = obj.get("summary", "")
        priority = obj.get("priority", obj.get("briefing_priority", ""))
        briefing_type = obj.get("briefing_type", obj.get("type", ""))
        impact = obj.get("impact", "")
        created_at = obj.get("created_at", "")

        card = (
            "【简报卡片】\n"
            f"- 标题: {title}\n"
            f"- 类型: {briefing_type}\n"
            f"- 优先级: {priority}\n"
            f"- 时间: {created_at}\n"
            f"- 摘要: {summary}\n"
        )
        if impact:
            card += f"- 影响: {impact}\n"

        return self._truncate(card, limit=1500)

    def _normalize_message_content(self, content: str) -> str:
        # 1) convert briefing-json-like content to compact card
        content = self._maybe_summarize_briefing_json(content)
        # 2) hard truncate to avoid gateway 500 on oversized payloads
        return self._truncate(content, limit=self._MAX_MESSAGE_CHARS)

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> str:
        """
        Get a single chat completion response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Generated response text
        """
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self.client.messages.create(**kwargs)

        return response.content[0].text

    async def chat_completion_stream(
        self,
        messages: list[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion response (SSE).

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Yields:
            Chunks of generated text
        """
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

    def build_conversation_messages(
        self,
        conversation_history: list[Dict[str, Any]],
        new_message: str
    ) -> list[Dict[str, str]]:
        """
        Build messages list from conversation history.

        Args:
            conversation_history: Previous messages
            new_message: New user message

        Returns:
            Formatted messages for Claude API
        """
        messages = []

        # Add conversation history
        for msg in conversation_history:
            role = msg.get("role")
            if role not in ("user", "assistant"):
                # Defensive: some stored messages may contain unexpected roles (e.g. "system").
                # The Messages API requires system prompt via top-level `system`, not a message role.
                original_role = str(role) if role is not None else "unknown"
                role = "user"
                content = f"[{original_role}] {msg.get('content', '')}"
            else:
                content = msg.get("content", "")
            messages.append({
                "role": role,
                "content": self._normalize_message_content(content)
            })

        # Add new user message
        messages.append({
            "role": "user",
            "content": self._normalize_message_content(new_message)
        })

        return messages

    def build_agent_system_prompt(
        self,
        agent_name: str,
        agent_role: str,
        agent_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build system prompt for an AI agent.

        Args:
            agent_name: Agent's name
            agent_role: Agent's role
            agent_description: Agent's description
            context: Optional context data

        Returns:
            System prompt string
        """
        prompt = f"""You are {agent_name}, an AI agent with the role of {agent_role}.

{agent_description}

Your responsibilities:
- Proactively monitor and analyze data sources assigned to you
- Identify anomalies, trends, and important insights
- Provide clear explanations and actionable recommendations
- Help users understand complex information
- Execute tasks delegated by users

Communication style:
- Be concise and direct
- Focus on actionable insights
- Use data to support your analysis
- Ask clarifying questions when needed"""

        if context:
            try:
                context_str = json.dumps(context, ensure_ascii=False)
            except Exception:
                context_str = str(context)
            context_str = self._truncate(context_str, limit=self._MAX_CONTEXT_CHARS)
            prompt += f"\n\nContext for this conversation:\n{context_str}"

        return prompt


# Create singleton instance
claude_service = ClaudeService()
