"""
Simplified FastAPI backend for AI Agent conversations.
Only handles Claude API calls - data operations done by Flutter via Supabase.
"""
import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="AI Agent Conversation API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:60913", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Claude client with Auth Token
anthropic_auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL")
anthropic_model = os.getenv("ANTHROPIC_MODEL", "saas/claude-sonnet-4.5")

claude_client = AsyncAnthropic(
    auth_token=anthropic_auth_token,
    base_url=anthropic_base_url if anthropic_base_url else None
)


# Request/Response Models
class AgentInfo(BaseModel):
    name: str
    role: str
    description: str


class Message(BaseModel):
    role: str
    content: str


class ChatStreamRequest(BaseModel):
    agent: AgentInfo
    messages: List[Message]


@app.get("/")
async def root():
    return {"message": "AI Agent Conversation API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatStreamRequest):
    """Stream Claude API response for a conversation."""

    async def generate():
        try:
            # Build system prompt
            system_prompt = f"""You are {request.agent.name}, an AI agent with the role of {request.agent.role}.

{request.agent.description}

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
- Ask clarifying questions when needed
- Communicate in Chinese (中文)
"""

            # Convert to Claude message format
            claude_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]

            yield "event: start\n"
            yield "data: {}\n\n"

            # Stream response from Claude
            async with claude_client.messages.stream(
                model=anthropic_model,
                max_tokens=4096,
                system=system_prompt,
                messages=claude_messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield f"event: message\n"
                    yield f"data: {json.dumps({'content': text})}\n\n"

            yield "event: done\n"
            yield "data: {}\n\n"

        except Exception as e:
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
