"use client";

import { useEffect, useRef, useState } from "react";
import { vane } from "@/lib/companion";
import {
  clearConversation,
  getConversation,
  sendChat,
  type ChatMessage,
  type ConversationSummary,
  type OutputValidation,
} from "@/lib/api";

interface Props {
  answers: Record<string, string>;
  onEdit: () => void;
}

interface RuntimeStatus {
  provider: string;
  model: string;
  configured: boolean;
  mode: string;
}

export function ChatPanel({ answers, onEdit }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: vane.greeting },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [validation, setValidation] = useState<OutputValidation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [runtime, setRuntime] = useState<RuntimeStatus | null>(null);
  const [serverTurnCount, setServerTurnCount] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch runtime/provider status once on mount (safe diagnostics, no secrets).
  useEffect(() => {
    const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${api}/v1/runtime/status`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d) setRuntime(d);
      })
      .catch(() => {
        /* diagnostics are best-effort; ignore failures */
      });
  }, []);

  // Refresh the server-side turn count whenever the local bubble list
  // changes. This is a small dev diagnostic that surfaces whether the
  // backend actually persisted the turn (vs. just rendering it locally).
  useEffect(() => {
    let cancelled = false;
    getConversation()
      .then((summary: ConversationSummary) => {
        if (!cancelled) setServerTurnCount(summary.messages.length);
      })
      .catch(() => {
        /* best-effort diagnostic */
      });
    return () => {
      cancelled = true;
    };
  }, [messages]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || loading) return;
    setError(null);
    setInput("");

    const userMsg: ChatMessage = { role: "user", content };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);

    try {
      const data = await sendChat(content);
      setMessages((m) => [...m, { role: "assistant", content: data.response.content }]);
      setValidation(data.response.validation);
      // Update runtime display from the actual response (provider/model).
      setRuntime((prev) =>
        prev
          ? { ...prev, provider: data.response.provider, model: data.response.model }
          : {
              provider: data.response.provider,
              model: data.response.model,
              configured: false,
              mode: data.response.provider === "mock" ? "mock" : "real",
            },
      );
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error desconocido";
      setError(msg);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "No pude responder ahora. ¿Probamos de nuevo?",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearServerConversation = async () => {
    if (loading) return;
    setError(null);
    try {
      await clearConversation();
      // Reset the local chat to the canonical greeting so the UI does
      // not show stale bubbles after the server state was cleared.
      setMessages([{ role: "assistant", content: vane.greeting }]);
      setValidation(null);
      setServerTurnCount(0);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error desconocido";
      setError(msg);
    }
  };

  const statusLabel = runtime
    ? `provider: ${runtime.provider} · ${runtime.mode}`
    : "provider: ...";

  const turnLabel =
    serverTurnCount !== null ? `turnos server: ${serverTurnCount}` : "turnos server: ...";

  return (
    <section className="section" id="chat">
      <div className="section-inner">
        <div className="chat-grid">
          {/* Side: profile summary */}
          <div className="chat-side glass">
            <div className="progress">Tu punto de partida</div>
            <h3>Así podría sentirse</h3>
            <p>
              Una compañera adulta, creativa y con iniciativa medida. El perfil es editable
              y queda separado de los ajustes temporales.
            </p>
            <dl>
              {Object.entries(answers).map(([k, v]) => (
                <div key={k}>
                  <dt>{k}</dt>
                  <dd>{v}</dd>
                </div>
              ))}
            </dl>
            <button className="secondary" onClick={onEdit}>
              Volver y editar
            </button>
          </div>

          {/* Main: chat */}
          <div className="chat-main glass-strong">
            <div className="chat-header">
              <div className="chat-avatar">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={vane.portrait} alt="" />
              </div>
              <div className="chat-header-info">
                <h4>{vane.name}</h4>
                <span className="status">{statusLabel}</span>
              </div>
            </div>

            <div className="chat-messages" ref={scrollRef}>
              {messages.map((m, i) => (
                <div key={i} className={m.role === "user" ? "bubble user" : "bubble assistant"}>
                  {m.content}
                </div>
              ))}
              {loading && (
                <div className="typing" aria-label="Escribiendo">
                  <span />
                  <span />
                  <span />
                </div>
              )}
            </div>

            {messages.length <= 2 && !loading && (
              <div className="quick-prompts">
                {vane.quickPrompts.map((q) => (
                  <button key={q} className="quick-prompt" onClick={() => send(q)}>
                    {q}
                  </button>
                ))}
              </div>
            )}

            <div className="composer">
              <input
                aria-label="Mensaje"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
                placeholder="Escribile algo a Vane..."
                disabled={loading}
              />
              <button onClick={() => send()} disabled={loading || !input.trim()}>
                Enviar
              </button>
            </div>

            {error && (
              <p className="chat-dev" style={{ color: "var(--magenta)" }}>
                Error: {error}
              </p>
            )}
            {validation && (
              <p className="chat-dev">
                Desarrollo: validación de salida {validation.is_valid ? "OK" : "rechazada"}
                {validation.reasons.length > 0 && ` (${validation.reasons.join(", ")})`}
              </p>
            )}
            <p className="chat-dev">
              {turnLabel}{" "}
              <button
                type="button"
                onClick={clearServerConversation}
                disabled={loading}
                style={{
                  background: "transparent",
                  border: "1px solid var(--violet, #a78bfa)",
                  color: "var(--violet, #a78bfa)",
                  borderRadius: "6px",
                  padding: "2px 8px",
                  marginLeft: "8px",
                  cursor: loading ? "not-allowed" : "pointer",
                  fontSize: "0.85em",
                }}
                aria-label="Limpiar conversación server"
              >
                limpiar conversación
              </button>
            </p>
            <div className="chat-media">▣ Video enviado · placeholder · no generado en vivo</div>
          </div>
        </div>
      </div>
    </section>
  );
}
