"""
Claude API service for AI interactions.
"""
from typing import AsyncGenerator, Optional, Dict, Any
from anthropic import AsyncAnthropic

from app.core.config import settings


class ClaudeService:
    """Service for interacting with Claude API."""

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

    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
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
        max_tokens: int = 4096,
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
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add new user message
        messages.append({
            "role": "user",
            "content": new_message
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
            prompt += f"\n\nContext for this conversation:\n{context}"

        return prompt


# Create singleton instance
claude_service = ClaudeService()
