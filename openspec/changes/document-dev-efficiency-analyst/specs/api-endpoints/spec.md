## ADDED Requirements

### Requirement: FastAPI Service Configuration

The system SHALL provide a FastAPI web service as the Agent Orchestrator that exposes HTTP and WebSocket APIs.

#### Scenario: Service metadata

- **WHEN** the FastAPI application starts
- **THEN** it SHALL be titled "AI Agent Orchestrator"
- **AND** version SHALL be "2.0.0"
- **AND** OpenAPI documentation SHALL be available at /docs

#### Scenario: CORS configuration

- **WHEN** handling HTTP requests
- **THEN** the service SHALL allow all origins (allow_origins=["*"])
- **AND** allow all methods and headers
- **AND** enable credentials
- **AND** this SHALL support local Flutter web development

### Requirement: Health Check Endpoint

The system SHALL provide a health check endpoint for monitoring service status.

#### Scenario: Health check request

- **WHEN** a GET request is sent to /health or /api/v1/health
- **THEN** the service SHALL return 200 OK
- **AND** response SHALL include status, agent count, and available tools

### Requirement: Agent List Endpoint

The system SHALL provide an endpoint to list all registered AI agents.

#### Scenario: List agents request

- **WHEN** a GET request is sent to /api/v1/agents
- **THEN** the service SHALL return a list of all registered agents
- **AND** each agent SHALL include role, name (Chinese), description, and workspace path

### Requirement: WebSocket Streaming Chat

The system SHALL provide a WebSocket endpoint for real-time streaming conversations with AI agents.

#### Scenario: WebSocket connection

- **WHEN** a client connects to /ws/chat
- **THEN** the service SHALL accept the WebSocket connection
- **AND** await messages from the client

#### Scenario: WebSocket message format

- **WHEN** client sends a WebSocket message
- **THEN** the message SHALL be JSON with fields:
  - agent_role: str (e.g., "dev_efficiency_analyst")
  - message: str (user's message)
  - conversation_history: optional list of previous messages
- **AND** the service SHALL validate the agent_role exists

#### Scenario: Stream conversation response

- **WHEN** processing a WebSocket chat message
- **THEN** the service SHALL:
  1. Load agent configuration and CLAUDE.md instructions
  2. Call Claude API with streaming enabled
  3. Stream each content delta to the client as JSON
  4. Include tool_use and tool_result events when tools are called
  5. Send final response when conversation completes

#### Scenario: WebSocket error handling

- **WHEN** an error occurs during WebSocket conversation
- **THEN** the service SHALL send an error message to the client
- **AND** log the error details
- **AND** close the connection gracefully if necessary

### Requirement: HTTP SSE Streaming Chat

The system SHALL provide an HTTP endpoint with Server-Sent Events (SSE) for streaming conversations.

#### Scenario: SSE chat request

- **WHEN** a POST request is sent to /api/v1/chat/stream
- **THEN** the service SHALL accept a JSON body with agent_role, message, and conversation_history
- **AND** return a streaming response with Content-Type: text/event-stream

#### Scenario: SSE event format

- **WHEN** streaming a conversation via SSE
- **THEN** each event SHALL be formatted as:
  ```
  data: {"type": "content_delta", "content": "..."}

  ```
- **AND** events MAY include types: content_delta, tool_use, tool_result, done
- **AND** the stream SHALL end with a done event

#### Scenario: SSE tool execution visibility

- **WHEN** Claude calls a tool during SSE streaming
- **THEN** the service SHALL send a tool_use event showing tool name and input
- **AND** send a tool_result event showing the tool's output
- **AND** continue streaming Claude's response after tool execution

### Requirement: Conversation History Support

Both WebSocket and HTTP endpoints SHALL accept conversation history to enable multi-turn dialogues.

#### Scenario: Continue conversation with history

- **WHEN** a request includes conversation_history
- **THEN** the service SHALL prepend the history to the messages sent to Claude API
- **AND** Claude SHALL have context from previous turns
- **AND** the agent SHALL maintain continuity in the conversation

#### Scenario: History message format

- **WHEN** providing conversation history
- **THEN** each history item SHALL include role ("user" or "assistant") and content (str)
- **AND** the history SHALL be ordered chronologically

### Requirement: Agent Manager Integration

The API endpoints SHALL integrate with AgentManager to execute conversations with proper workspace isolation.

#### Scenario: Route to agent workspace

- **WHEN** processing a chat request for a specific agent_role
- **THEN** the service SHALL retrieve the agent's AgentConfig from AgentManager
- **AND** load the agent's CLAUDE.md as system instructions
- **AND** execute all tools within the agent's workspace directory

#### Scenario: Invalid agent role handling

- **WHEN** a request specifies an unknown agent_role
- **THEN** the service SHALL return 404 Not Found (HTTP) or error message (WebSocket)
- **AND** inform the client which agent roles are valid

### Requirement: Claude API Integration

The service SHALL integrate with Anthropic Claude API using custom authentication and base URL.

#### Scenario: Claude API configuration

- **WHEN** the service initializes
- **THEN** it SHALL read ANTHROPIC_AUTH_TOKEN and ANTHROPIC_BASE_URL from environment
- **AND** configure AsyncAnthropic client with base_url="https://llm-gateway.oppoer.me"
- **AND** use model "saas/claude-sonnet-4.5" by default

#### Scenario: Streaming conversation with Claude

- **WHEN** handling a chat request
- **THEN** the service SHALL call Claude API with:
  - model: configured model name
  - system: CLAUDE.md content
  - messages: user message + conversation history
  - tools: tool definitions (bash, read_file, write_file, web_fetch)
  - max_tokens: reasonable limit (e.g., 4096)
  - stream: true
- **AND** process the streaming response

#### Scenario: Tool execution during conversation

- **WHEN** Claude API returns a tool_use block
- **THEN** the service SHALL execute the tool using AgentManager's tool handlers
- **AND** send the tool result back to Claude API
- **AND** continue the conversation until Claude returns a text response or completes
