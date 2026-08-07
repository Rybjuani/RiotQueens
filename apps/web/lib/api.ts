/**
 * Typed client for the canonical FastAPI backend.
 * Contract: POST /v1/chat → ChatResponse { response: { content, validation, ... } }
 *
 * Per Issue #1: the frontend is a client only. Chat must go through the
 * existing FastAPI backend (ModelRouter / Provider abstraction /
 * OutputValidator), not a second Next.js API route.
 */

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
 * Send a single chat message to the canonical companion (Vane).
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
      character_id: opts?.character_id ?? "vane",
      conversation_id: "web-session",
    }),
    signal: opts?.signal,
  });

  if (!res.ok) {
    throw new Error(`Chat API error: ${res.status} ${res.statusText}`);
  }

  return (await res.json()) as ChatResponse;
}
