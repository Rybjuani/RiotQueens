/**
 * Typed client for the canonical FastAPI backend.
 * Contract: POST /v1/chat → ChatResponse { response: { content, validation, ... } }
 *
 * Per Issue #3: the frontend is a client only. Chat must go through the
 * existing FastAPI backend (ModelRouter / Provider abstraction /
 * OutputValidator), not a second Next.js API route. The conversation_id
 * is a per-browser-session identifier (lib/session.ts), NOT a shared
 * constant. The client never sends a system prompt — the server owns
 * the canonical Queen personality.
 */

import { getConversationId } from "@/lib/session";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface OutputValidation {
  is_valid: boolean;
  language_ok: boolean;
  encoding_ok: boolean;
  not_truncated: boolean;
  not_repetitive: boolean;
  no_internal_leak: boolean;
  character_consistent: boolean;
  reasons: string[];
}

export interface ChatResponse {
  response: {
    provider: string;
    model: string;
    content: string;
    usage: { input_tokens: number; output_tokens: number };
    latency_ms: number;
    validation: OutputValidation | null;
    retry_count: number;
  };
}

/**
 * Send a single chat message to the canonical Queen.
 * The backend keeps conversation state server-side; the frontend sends
 * one message at a time per the existing ChatRequest contract.
 */
export async function sendChat(
  message: string,
  opts?: { character_id?: string; signal?: AbortSignal },
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      character_id: opts?.character_id ?? "bardera",
      conversation_id: getConversationId(),
    }),
    signal: opts?.signal,
  });

  if (!res.ok) {
    throw new Error(`Chat API error: ${res.status} ${res.statusText}`);
  }

  return (await res.json()) as ChatResponse;
}

/**
 * Clear the server-side conversation history for the current browser
 * session. This is a prototype diagnostic — it does NOT clear other
 * users' conversations, other characters, or other conversation ids.
 *
 * The server returns `{deleted: bool, conversation_id: string}`.
 * `deleted=false` simply means there was no in-process state for this
 * scope yet (e.g. a fresh browser tab), which is not an error.
 *
 * Note: this is in-process prototype state. Server restart clears all
 * conversations; this is NOT durable persistence.
 */
export async function clearConversation(
  opts?: { character_id?: string; signal?: AbortSignal },
): Promise<{ deleted: boolean; conversation_id: string }> {
  const res = await fetch(
    `${API_URL}/v1/conversations/${encodeURIComponent(getConversationId())}`,
    {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: "demo-user",
        character_id: opts?.character_id ?? "bardera",
      }),
      signal: opts?.signal,
    },
  );
  if (!res.ok) {
    throw new Error(`Clear conversation API error: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as { deleted: boolean; conversation_id: string };
}

/**
 * Inspect the server-side conversation history for the current browser
 * session. Used by the dev diagnostic panel to verify multi-turn
 * continuity. Returns the stored messages (user + assistant only — the
 * canonical Queen system prompt is NEVER stored and NEVER returned).
 */
export interface ConversationMessageView {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ConversationSummary {
  user_id: string;
  character_id: string;
  conversation_id: string;
  messages: ConversationMessageView[];
  created_at: string;
  updated_at: string;
}

export async function getConversation(
  opts?: { character_id?: string; signal?: AbortSignal },
): Promise<ConversationSummary> {
  const res = await fetch(
    `${API_URL}/v1/conversations/${encodeURIComponent(getConversationId())}?user_id=demo-user&character_id=${encodeURIComponent(
      opts?.character_id ?? "bardera",
    )}`,
    { signal: opts?.signal },
  );
  if (!res.ok) {
    throw new Error(`Get conversation API error: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as ConversationSummary;
}
