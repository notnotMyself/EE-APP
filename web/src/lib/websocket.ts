/**
 * WebSocket client for real-time conversation streaming.
 *
 * Protocol (server -> client):
 *   { type: "connected", conversation_id, ts }
 *   { type: "text_chunk", content, ts }
 *   { type: "tool_use", tool_name, tool_id, tool_input }
 *   { type: "tool_result", tool_id, result, is_error }
 *   { type: "done", message_id }
 *   { type: "ping", ts }
 *   { type: "error", content }
 *
 * Protocol (client -> server):
 *   { type: "message", content }
 *   { type: "pong" }
 */

const WS_BASE =
  process.env.NEXT_PUBLIC_WS_BASE ?? "wss://super-niuma-cn.allawntech.com";

export type WSMessageType =
  | "connected"
  | "text_chunk"
  | "tool_use"
  | "tool_result"
  | "done"
  | "ping"
  | "error";

export interface WSMessage {
  type: WSMessageType;
  content?: string;
  conversation_id?: string;
  message_id?: string;
  tool_name?: string;
  tool_id?: string;
  tool_input?: Record<string, unknown>;
  result?: string;
  is_error?: boolean;
  ts?: number;
}

export interface WSCallbacks {
  onConnected?: () => void;
  onTextChunk?: (content: string) => void;
  onToolUse?: (toolName: string, toolId: string) => void;
  onToolResult?: (toolId: string, result: string, isError: boolean) => void;
  onDone?: (messageId?: string) => void;
  onError?: (content: string) => void;
  onClose?: () => void;
  /** 所有重连尝试耗尽后触发，表示连接彻底失败 */
  onPermanentClose?: () => void;
}

export class ConversationWebSocket {
  private ws: WebSocket | null = null;
  private conversationId: string;
  private token: string;
  private callbacks: WSCallbacks;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private instanceId: string; // 区分 StrictMode 的两次实例

  constructor(
    conversationId: string,
    token: string,
    callbacks: WSCallbacks
  ) {
    this.conversationId = conversationId;
    this.token = token;
    this.callbacks = callbacks;
    this.instanceId = Math.random().toString(36).slice(2, 6);
    this.log("constructor");
  }

  private log(event: string, extra?: Record<string, unknown>) {
    const ts = new Date().toISOString().slice(11, 23); // HH:mm:ss.mmm
    console.log(
      `[WS:${this.instanceId}] ${ts} ${event}`,
      extra ?? "",
    );
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.log("connect:skip (already open)");
      return;
    }

    const url = `${WS_BASE}/api/v1/conversations/${this.conversationId}/ws?token=${encodeURIComponent(this.token)}`;
    this.log("connect:start", { url: url.replace(/token=.+/, "token=***") });
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.log("onopen", { reconnectAttempts: this.reconnectAttempts });
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);
        if (msg.type !== "ping" && msg.type !== "text_chunk") {
          // text_chunk 太频繁不记录，ping 也不记录
          this.log("onmessage", { type: msg.type });
        }
        this.handleMessage(msg);
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = (ev) => {
      this.log("onclose", { code: ev.code, reason: ev.reason, wasClean: ev.wasClean });
      this.clearPingTimer();
      this.callbacks.onClose?.();
      this.maybeReconnect();
    };

    this.ws.onerror = (ev) => {
      this.log("onerror", { type: ev.type });
      // onclose will fire after onerror
    };
  }

  disconnect(): void {
    this.log("disconnect", { maxReconnectAttempts: this.maxReconnectAttempts });
    this.maxReconnectAttempts = 0; // prevent reconnect
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.clearPingTimer();
    if (this.ws) {
      // 主动断开：先摘掉回调，避免 onclose/onerror 延迟触发时误走 onPermanentClose
      this.ws.onopen = null;
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.onmessage = null;
      this.ws.close();
      this.ws = null;
    }
  }

  sendMessage(content: string, attachments?: unknown[]): void {
    if (this.ws?.readyState !== WebSocket.OPEN) return;
    const payload: Record<string, unknown> = { type: "message", content };
    if (attachments?.length) payload.attachments = attachments;
    this.ws.send(JSON.stringify(payload));
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // ─── Internal ───────────────────────────────────────────────────────────

  private handleMessage(msg: WSMessage): void {
    switch (msg.type) {
      case "connected":
        this.callbacks.onConnected?.();
        break;
      case "text_chunk":
        if (msg.content) this.callbacks.onTextChunk?.(msg.content);
        break;
      case "tool_use":
        if (msg.tool_name && msg.tool_id)
          this.callbacks.onToolUse?.(msg.tool_name, msg.tool_id);
        break;
      case "tool_result":
        if (msg.tool_id)
          this.callbacks.onToolResult?.(
            msg.tool_id,
            msg.result ?? "",
            msg.is_error ?? false
          );
        break;
      case "done":
        this.callbacks.onDone?.(msg.message_id);
        break;
      case "ping":
        this.sendPong();
        break;
      case "error":
        this.callbacks.onError?.(msg.content ?? "Unknown error");
        break;
    }
  }

  private sendPong(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "pong" }));
    }
  }

  private clearPingTimer(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  private maybeReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.log("maybeReconnect:exhausted", { attempts: this.reconnectAttempts });
      this.callbacks.onPermanentClose?.();
      return;
    }
    this.reconnectAttempts++;
    const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 10000);
    this.log("maybeReconnect:schedule", { attempt: this.reconnectAttempts, delayMs: delay });
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }
}
