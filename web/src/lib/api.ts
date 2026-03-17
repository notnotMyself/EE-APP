/**
 * Backend API client for conversation management.
 *
 * REST endpoints (all require Bearer token):
 *   GET    /api/v1/conversations           — list user conversations
 *   POST   /api/v1/conversations           — create conversation
 *   GET    /api/v1/conversations/:id/messages — list messages
 *   PUT    /api/v1/conversations/:id/title  — update title
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "https://super-niuma-cn.allawntech.com";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Conversation {
  id: string;
  user_id: string;
  agent_id: string;
  agent_name?: string;
  agent_role?: string;
  title?: string;
  status: string;
  started_at: string;
  last_message_at?: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content_type: string;
  content: string;
  briefing_id?: string;
  created_at: string;
}

// ─── Helper ─────────────────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  token: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options?.headers ?? {}),
    },
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body}`);
  }

  return res.json();
}

// ─── Conversation API ───────────────────────────────────────────────────────

/** List all conversations for the current user. */
export function listConversations(token: string): Promise<Conversation[]> {
  return apiFetch<Conversation[]>("/api/v1/conversations", token);
}

/** Create a new conversation with an agent. */
export function createConversation(
  token: string,
  agentId: string,
  title?: string
): Promise<Conversation> {
  return apiFetch<Conversation>("/api/v1/conversations", token, {
    method: "POST",
    body: JSON.stringify({ agent_id: agentId, title }),
  });
}

/** Get or create a conversation for a specific agent (single-conv mode). */
export function getConversationWithAgent(
  token: string,
  agentId: string
): Promise<Conversation> {
  return apiFetch<Conversation>(`/api/v1/conversations/${agentId}`, token);
}

/** List messages for a conversation. */
export function listMessages(
  token: string,
  conversationId: string,
  limit = 50,
  offset = 0
): Promise<{ messages: Message[]; total: number; conversation_id: string }> {
  return apiFetch(
    `/api/v1/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`,
    token
  );
}

/** Delete a conversation. */
export async function deleteConversation(
  token: string,
  conversationId: string
): Promise<void> {
  await apiFetch<void>(`/api/v1/conversations/${conversationId}`, token, {
    method: "DELETE",
  });
}

/** Update conversation title. */
export function updateConversationTitle(
  token: string,
  conversationId: string,
  title: string
): Promise<Conversation> {
  return apiFetch<Conversation>(
    `/api/v1/conversations/${conversationId}/title`,
    token,
    { method: "PUT", body: JSON.stringify({ title }) }
  );
}
